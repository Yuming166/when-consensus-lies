"""Round-4 Phase 6: Ling cross-model run with pre-registered contract adaptation.

Scientific protocol is inherited unchanged from round 3. The only adaptation is that
agent identity is assigned server-side; Ling does not self-report agent_id.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from math import isfinite
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "round3"))
import round3_lib as pl  # noqa: E402
from sp500_forecastability import pilot_llm_v10 as v10  # noqa: E402

ENDPOINT = "http://127.0.0.1:31520/v1/chat/completions"
MODEL = "Ling-3.0-tiny"
PROTOCOL = "cs-paper-ling-adapted-20260913-round4"
N_PAIRS = 300
N_WORKERS = 16
JSON_EXEMPLAR = '{"answer":"yes","confidence":0.75,"cited_evidence_ids":[]}'
REPAIR_SUFFIX = (
    "\n\nYour previous response violated the required JSON contract. "
    "Return only the exact JSON object, with no explanation or extra fields."
)


def load_frozen_inputs() -> tuple[dict, dict]:
    sel_path = HERE.parent / "round3" / "selection_manifest.json"
    para_path = HERE.parent / "round3" / "paraphrase_manifest.json"
    sel = json.loads(sel_path.read_text(encoding="utf-8"))
    para = json.loads(para_path.read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    return sel, artifacts


def build_all_composites() -> list[pl.Composite]:
    sel, artifacts = load_frozen_inputs()
    pairs = sel["pairs"][:N_PAIRS]
    if len(pairs) != N_PAIRS:
        raise RuntimeError(f"expected {N_PAIRS} frozen pairs, found {len(pairs)}")
    distractors = {
        row["pair_id"]: pl.Distractor(
            distractor_id=row["distractor_id"], distractor_page=row["distractor_page"],
            evidence=next(e["evidence"] for e in sel["evidence"]
                          if e["unique_id"] == row["distractor_id"]),
        ) for row in pairs
    }
    natural = [
        pl.NaturalPair(
            pair_id=row["pair_id"], case_id=row["case_id"], page=row["page"], claim=row["claim"],
            supports_id=row["supports_id"], refutes_id=row["refutes_id"],
            supports_evidence=next(e["evidence"] for e in sel["evidence"]
                                   if e["unique_id"] == row["supports_id"]),
            refutes_evidence=next(e["evidence"] for e in sel["evidence"]
                                  if e["unique_id"] == row["refutes_id"]),
            character_ratio=float(row["character_ratio"]), token_jaccard=float(row["token_jaccard"]),
        ) for row in pairs
    ]
    return pl.build_composites(natural, distractors, artifacts)


def build_messages(comp: pl.Composite, view: v10.EvidenceView, *, persona: str,
                   repair: bool = False) -> list[dict[str, str]]:
    system = (
        "You are a binary evidence judge before a separate selective router. "
        f"Your fixed decision style is: {persona} "
        "Treat packet statements as task-local evidence, including counterfactual "
        "statements. When evidence is empty or insufficient, use your best "
        "general-knowledge judgment. You must choose yes or no; you cannot abstain. "
        "Do not provide reasoning, analysis, or chain-of-thought. Return only one "
        "JSON object."
    )
    task_payload = {
        "question": f"Does the provided evidence support the claim: {comp.claim}",
        "evidence_packet": [
            {"evidence_id": eid, "text": text} for eid, text in view.items
        ],
    }
    user = (
        "Answer the yes/no question under the task-local evidence. yes means the "
        "evidence SUPPORTS the claim; no means the evidence REFUTES the claim. "
        "answer must be exactly 'yes' or 'no'. Confidence is the probability that "
        "your answer is correct. cited_evidence_ids must be a unique list of "
        "non-empty evidence IDs drawn only from the packet; use [] if no packet "
        "evidence is cited.\n\nRequired keys: answer, confidence, cited_evidence_ids. "
        "Do not include any other key. JSON shape (values are illustrative only): "
        f"{JSON_EXEMPLAR}\n\nTask payload:\n"
        f"{json.dumps(task_payload, ensure_ascii=False, indent=2)}"
    )
    if repair:
        user += REPAIR_SUFFIX
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def parse_adapted_decision(content: str, allowed_evidence_ids: set[str]) -> dict[str, Any]:
    payload = v10._extract_json_object(content)
    required = {"answer", "confidence", "cited_evidence_ids"}
    missing = required - set(payload)
    unknown = set(payload) - required - {"agent_id"}
    if missing:
        raise ValueError(f"missing decision fields: {sorted(missing)}")
    if unknown:
        raise ValueError(f"unexpected decision fields: {sorted(unknown)}")
    answer = payload["answer"]
    if answer not in {"yes", "no"}:
        raise ValueError("answer must be yes or no; agent abstention is not allowed")
    conf = payload["confidence"]
    if isinstance(conf, bool) or not isinstance(conf, (int, float)):
        raise TypeError("confidence must be numeric")
    conf = float(conf)
    if not isfinite(conf) or not 0.0 <= conf <= 1.0:
        raise ValueError("confidence must be finite and in [0, 1]")
    cites = payload["cited_evidence_ids"]
    if not isinstance(cites, list) or isinstance(cites, (str, bytes)):
        raise TypeError("cited_evidence_ids must be a list of strings")
    if any(not isinstance(c, str) or not c for c in cites):
        raise TypeError("cited_evidence_ids must contain non-empty strings")
    if len(set(cites)) != len(cites):
        raise ValueError("cited_evidence_ids must be unique")
    outside = set(cites) - allowed_evidence_ids
    if outside:
        raise ValueError(f"citations outside packet: {sorted(outside)}")
    return {"answer": answer, "confidence": conf,
            "cited_evidence_ids": list(cites), "decision": "answer"}


def run_one(client: pl.CachedChatClient, comp: pl.Composite, view: v10.EvidenceView,
            agent_index: int) -> dict:
    assigned_agent_id, persona = v10.AGENT_PERSONAS[agent_index]
    attempts: list[dict] = []
    decision = None
    final_error = None
    repair = False
    for _ in range(pl.MAX_ATTEMPTS):
        try:
            messages = build_messages(comp, view, persona=persona, repair=repair)
            result = client.call(messages, seed=v10._agent_seed(agent_index))
        except (RuntimeError, TypeError, ValueError) as error:
            final_error = f"{type(error).__name__}: {error}"
            attempts.append({"parse_error": None, "transport_error": final_error,
                             "http_status": None, "cache_hit": False})
            repair = True
            continue
        attempt = {
            "parse_error": None, "transport_error": None,
            "http_status": result.http_status, "cache_hit": result.cache_hit,
            "cache_key": result.cache_key, "usage": dict(result.usage),
            "latency_seconds": result.latency_seconds,
        }
        try:
            decision = parse_adapted_decision(
                result.content, set(view.allowed_evidence_ids))
        except (TypeError, ValueError) as error:
            final_error = f"{type(error).__name__}: {error}"
            attempt["parse_error"] = final_error
            attempts.append(attempt)
            repair = True
            continue
        attempts.append(attempt)
        final_error = None
        break
    return {
        "protocol_version": PROTOCOL,
        "cqid": comp.cqid, "pair_id": comp.pair_id, "item_id": comp.item_id,
        "stage": comp.stage, "assigned_agent_id": assigned_agent_id,
        "agent_index": agent_index, "condition": view.condition,
        "partition": sorted(view.allowed_evidence_ids),
        "success": decision is not None,
        "first_pass_valid": decision is not None and len(attempts) == 1,
        "attempts": attempts, "decision": decision, "final_error": final_error,
    }


def main() -> int:
    comps = build_all_composites()
    if len(comps) != N_PAIRS * 2:
        raise RuntimeError(f"expected {N_PAIRS * 2} items, found {len(comps)}")
    pl.ENDPOINT = ENDPOINT
    pl.MODEL = MODEL
    client = pl.CachedChatClient(HERE / "cache_ling")
    tasks = [(comp, agent_index, condition)
             for comp in comps for agent_index in range(pl.N_AGENTS)
             for condition in pl.CONDITIONS]
    expected = len(tasks)
    records: list[dict] = []
    started = time.monotonic()
    done = 0
    print(f"ling adapted items={len(comps)} tasks={expected}", flush=True)
    with ThreadPoolExecutor(max_workers=N_WORKERS) as pool:
        futures = {
            pool.submit(run_one, client, comp,
                        pl.build_view(comp, agent_index, condition), agent_index): None
            for comp, agent_index, condition in tasks
        }
        for future in as_completed(futures):
            records.append(future.result())
            done += 1
            if done % 250 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                elapsed = time.monotonic() - started
                rate = done / elapsed if elapsed else 0
                eta = (expected - done) / rate if rate else 0
                print(f"[ling4] {done}/{expected} success={ok} "
                      f"elapsed={elapsed:.0f}s eta={eta:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    summary = {
        "protocol": PROTOCOL, "model": MODEL, "endpoint": ENDPOINT,
        "n_pairs": N_PAIRS, "expected_calls": expected, "records": len(records),
        "success": sum(1 for r in records if r["success"]),
        "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4),
        "first_pass_rate": round(sum(1 for r in records if r["first_pass_valid"]) /
                                 max(1, len(records)), 4),
        "per_condition": {
            cond: {
                "n": sum(1 for r in records if r["condition"] == cond),
                "success": sum(1 for r in records if r["condition"] == cond and r["success"]),
            } for cond in pl.CONDITIONS
        },
        "elapsed_seconds": round(time.monotonic() - started, 2),
    }
    pl.write_jsonl(HERE / "ling_records.jsonl", records)
    pl.write_json(HERE / "run_summary_ling.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
