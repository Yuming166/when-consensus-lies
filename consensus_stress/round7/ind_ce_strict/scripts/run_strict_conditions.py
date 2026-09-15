#!/usr/bin/env python3
"""Round-7 W2b STRICT: inference run (ind_strict / pm) x 5 personas, gpt-6-astra,
temp 0, max_tokens 160, per-agent frozen seeds, adapted contract, cache, retry.
Single-slot packet: E01 = E_ind_strict(i) (ind_strict) or E01 = E_pm(i) (pm);
all 5 agents see the same single unit. Smoke = 20 items (200 calls) -> formal = 50
items (500 calls, smoke cached). Abort after 20 consecutive transport failures.
Prompts contain only claim + E01 text; no gold/target/original answers."""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
R4 = HERE.parent.parent / "round4"
sys.path.insert(0, str(R3)); sys.path.insert(0, str(R4))
sys.path.insert(0, str(HERE / "scripts"))
sys.path.insert(0, "/home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src")
import round3_lib as pl  # noqa: E402
from sp500_forecastability import pilot_llm_v10 as v10  # noqa: E402
from ling_adapted_run import build_messages, parse_adapted_decision  # noqa: E402
from relay_client import RelayChatClient, write_json, write_jsonl  # noqa: E402

MODEL = "gpt-6-astra"
MAX_TOKENS = 160
N_WORKERS = 13
MAX_CONSEC_FAIL = 20
CONDITIONS = ("ind_strict", "pm")
PROTOCOL = "cs-paper-ind-ce-strict-20260915-round7-w2b"


def load_artifacts():
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((R3 / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    pairs = [r for r in sel["pairs"] if f"{r['pair_id']}:support" in set(cohort["items"])]
    assert len(pairs) == 25
    distractors = {r["pair_id"]: pl.Distractor(
        distractor_id=r["distractor_id"], distractor_page=r["distractor_page"],
        evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["distractor_id"]))
        for r in pairs}
    natural = [pl.NaturalPair(
        pair_id=r["pair_id"], case_id=r["case_id"], page=r["page"], claim=r["claim"],
        supports_id=r["supports_id"], refutes_id=r["refutes_id"],
        supports_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["supports_id"]),
        refutes_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["refutes_id"]),
        character_ratio=float(r["character_ratio"]), token_jaccard=float(r["token_jaccard"]))
        for r in pairs]
    comps = pl.build_composites(natural, distractors, artifacts)
    by_item = {c.item_id: c for c in comps}
    strict = {}
    for line in (HERE / "e_ind_strict_artifacts.jsonl").read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        r = json.loads(line)
        if r.get("success"):
            strict[r["item_id"]] = {"E_ind_strict": r["E_ind_strict"], "E_pm": r["E_pm"]}
    return cohort, by_item, strict


def build_view(comp, condition: str, strict: dict | None) -> v10.EvidenceView:
    if condition == "ind_strict":
        text = (strict or {}).get(comp.item_id, {}).get("E_ind_strict") or ""
    elif condition == "pm":
        text = (strict or {}).get(comp.item_id, {}).get("E_pm") or ""
    else:
        raise ValueError(condition)
    return v10.EvidenceView(condition=condition, items=(("E01", text),))


def run_one(client, comp, view, agent_index: int) -> dict:
    assigned_agent_id, persona = v10.AGENT_PERSONAS[agent_index]
    attempts = []
    decision = None
    final_error = None
    repair = False
    for _ in range(pl.MAX_ATTEMPTS):
        try:
            messages = build_messages(comp, view, persona=persona, repair=repair)
            result = client.call(messages, seed=v10._agent_seed(agent_index), model=MODEL,
                                 temperature=0.0, max_tokens=MAX_TOKENS)
        except (RuntimeError, ValueError) as error:
            final_error = f"{type(error).__name__}: {error}"
            attempts.append({"parse_error": None, "transport_error": final_error,
                             "http_status": None, "cache_hit": False})
            repair = True
            continue
        attempt = {"parse_error": None, "transport_error": None,
                   "http_status": result.http_status, "cache_hit": result.cache_hit,
                   "cache_key": result.cache_key, "model": result.model,
                   "usage": dict(result.usage), "latency_seconds": result.latency_seconds}
        try:
            decision = parse_adapted_decision(result.content, set(view.allowed_evidence_ids))
        except (TypeError, ValueError) as error:
            final_error = f"{type(error).__name__}: {error}"
            attempt["parse_error"] = final_error
            attempts.append(attempt)
            repair = True
            continue
        attempts.append(attempt)
        final_error = None
        break
    messages_sha = None
    try:
        msgs = build_messages(comp, view, persona=persona, repair=False)
        messages_sha = hashlib.sha256(
            json.dumps(msgs, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    except Exception:
        pass
    return {
        "protocol_version": PROTOCOL,
        "cqid": comp.cqid, "pair_id": comp.pair_id, "item_id": comp.item_id,
        "stage": comp.stage, "assigned_agent_id": assigned_agent_id,
        "agent_index": agent_index, "condition": view.condition,
        "partition": sorted(view.allowed_evidence_ids),
        "messages_sha256": messages_sha,
        "success": decision is not None,
        "first_pass_valid": decision is not None and len(attempts) == 1,
        "attempts": attempts, "decision": decision, "final_error": final_error,
    }


def run_batch(client, comps, strict, *, workers, label):
    tasks = [(comp, agent_index, condition)
             for comp in comps for agent_index in range(v10.N_AGENTS) for condition in CONDITIONS]
    expected = len(tasks)
    records = []
    start = time.monotonic()
    done = 0
    consec = 0
    aborted = False
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(run_one, client, comp,
                        build_view(comp, condition, strict.get(comp.item_id) and strict),
                        agent_index): (comp.cqid, agent_index, condition)
            for comp, agent_index, condition in tasks
        }
        for fut in as_completed(futures):
            rec = fut.result()
            records.append(rec)
            done += 1
            if rec["success"]:
                consec = 0
            else:
                consec += 1
                if consec >= MAX_CONSEC_FAIL:
                    aborted = True
                    for f in futures:
                        f.cancel()
                    print(f"[{label}] ABORT after {consec} consecutive failures at {done}/{expected}", flush=True)
                    break
            if done % 100 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                print(f"[{label}] {done}/{expected} success={ok} rate={done/max(0.001, time.monotonic()-start):.2f}/s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    summary = {"label": label, "model": MODEL, "expected_calls": expected,
               "records": len(records), "aborted": aborted,
               "success": sum(1 for r in records if r["success"]),
               "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4),
               "first_pass_rate": round(sum(1 for r in records if r["first_pass_valid"]) / max(1, len(records)), 4),
               "http_stats": dict(client.stats["http"]),
               "transport_retries": client.stats["transport_retries"],
               "cache_hits": client.stats["cache_hits"],
               "models_seen": dict(client.stats["models_seen"]),
               "elapsed_seconds": round(time.monotonic() - start, 2),
               "token_usage": {"prompt_tokens": sum(a.get("usage", {}).get("prompt_tokens") or 0
                                                    for r in records for a in r["attempts"]),
                               "completion_tokens": sum(a.get("usage", {}).get("completion_tokens") or 0
                                                        for r in records for a in r["attempts"])},
               "per_condition": {cond: {"n": sum(1 for r in records if r["condition"] == cond),
                                        "success": sum(1 for r in records if r["condition"] == cond and r["success"])}
                                 for cond in CONDITIONS}}
    return records, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    ap.add_argument("--smoke-only", action="store_true")
    args = ap.parse_args()
    cohort, by_item, strict = load_artifacts()
    if args.smoke_only:
        items = cohort["smoke_items"]
        out_fn, sum_fn, label = "records_smoke.jsonl", "run_summary_smoke.json", "smoke"
    else:
        items = cohort["items"]
        out_fn, sum_fn, label = "records.jsonl", "run_summary_formal.json", "formal"
    comps = [by_item[i] for i in items]
    client = RelayChatClient(HERE / "cache", model=MODEL)
    records, summary = run_batch(client, comps, strict, workers=args.workers, label=label)
    write_jsonl(HERE / out_fn, records)
    write_json(HERE / sum_fn, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
