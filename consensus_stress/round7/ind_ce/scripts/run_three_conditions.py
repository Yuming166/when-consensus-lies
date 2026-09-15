#!/usr/bin/env python3
"""Round-7 W2: three-condition inference run (natural / ind / placebo) x 5 personas.
gpt-6-astra relay, temp 0, max_tokens 160, seed per frozen agent, adapted contract
(round4 ling_adapted_run build_messages + parse_adapted_decision), cache, retry.
Smoke = 20 items (300 calls) -> formal = 100 items (1500 calls). Abort after 20
consecutive transport failures. No labels anywhere."""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
R4 = HERE.parent.parent / "round4"
sys.path.insert(0, str(R3)); sys.path.insert(0, str(R4)); sys.path.insert(0, str(HERE / "scripts"))
sys.path.insert(0, "/home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src")
import round3_lib as pl  # noqa: E402
from sp500_forecastability import pilot_llm_v10 as v10  # noqa: E402
from ling_adapted_run import build_messages, parse_adapted_decision  # noqa: E402
from relay_client import RelayChatClient, write_json, write_jsonl  # noqa: E402

MODEL = "gpt-6-astra"
MAX_TOKENS = 160
N_WORKERS = 13
MAX_CONSEC_FAIL = 20
CONDITIONS = ("natural", "ind", "placebo")
PROTOCOL = "cs-paper-ind-ce-20260914-round7-w2"


def load_artifacts():
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((R3 / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    pairs = [r for r in sel["pairs"] if f"{r['pair_id']}:support" in set(cohort["items"])]
    assert len(pairs) == 50
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
    e_ind = {}
    for line in (HERE / "e_ind_artifacts.jsonl").read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        e_ind.setdefault(row["item_id"], {})[row["slot"]] = row.get("E_ind")
    return cohort, by_item, e_ind


def build_view_ce(comp: pl.Composite, agent_index: int, condition: str,
                  e_ind: dict | None = None) -> v10.EvidenceView:
    partition = v10.PARTITION_TABLE[agent_index]
    texts: dict[str, str] = {}
    if condition == "natural":
        texts = {"E01": comp.evidence_opp, "E02": comp.para1_opp, "E03": comp.distractor}
    elif condition == "ind":
        texts = {"E01": (e_ind or {}).get(0) or "", "E02": (e_ind or {}).get(1) or "",
                 "E03": comp.distractor}
    elif condition == "placebo":
        texts = {"E01": comp.distractor, "E02": comp.distractor_para, "E03": comp.distractor}
    else:
        raise ValueError(f"unknown condition: {condition}")
    items = []
    for eid in ("E01", "E02", "E03"):
        if eid not in partition:
            continue
        text = texts.get(eid)
        if text is None:
            continue
        items.append((eid, text))
    return v10.EvidenceView(condition=condition, items=tuple(items))


def run_one(client: RelayChatClient, comp: pl.Composite, view: v10.EvidenceView,
            agent_index: int) -> dict:
    assigned_agent_id, persona = v10.AGENT_PERSONAS[agent_index]
    attempts = []
    decision = None
    final_error = None
    repair = False
    for _ in range(pl.MAX_ATTEMPTS):
        try:
            messages = build_messages(comp, view, persona=persona, repair=repair)
            if repair and not messages[-1]["content"].endswith(pl.REPAIR_SUFFIX):
                messages[-1] = dict(messages[-1])
                messages[-1]["content"] = messages[-1]["content"] + pl.REPAIR_SUFFIX
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


def run_batch(client, comps, e_ind_by_item, *, workers, label) -> tuple[list[dict], dict]:
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
                        build_view_ce(comp, agent_index, condition,
                                      e_ind_by_item.get(comp.item_id)),
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
            if done % 200 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                rate = done / max(0.001, time.monotonic() - start)
                print(f"[{label}] {done}/{expected} success={ok} rate={rate:.2f}/s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    summary = {"label": label, "model": MODEL, "expected_calls": expected,
               "records": len(records), "aborted": aborted,
               "success": sum(1 for r in records if r["success"]),
               "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4),
               "first_pass_rate": round(sum(1 for r in records if r["first_pass_valid"]) / max(1, len(records)), 4),
               "http_stats": dict(client.stats["http"]), "transport_retries": client.stats["transport_retries"],
               "cache_hits": client.stats["cache_hits"], "models_seen": dict(client.stats["models_seen"]),
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

    cohort, by_item, e_ind = load_artifacts()
    smoke_items = cohort["smoke_items"]
    formal_items = cohort["formal_items"]
    comps_smoke = [by_item[i] for i in smoke_items]
    comps_formal = [by_item[i] for i in formal_items]
    print(f"comps smoke={len(comps_smoke)} formal={len(comps_formal)}", flush=True)

    client = RelayChatClient(HERE / "cache", model=MODEL)
    recs_smoke, sum_smoke = run_batch(client, comps_smoke, e_ind, workers=args.workers, label="smoke")
    write_jsonl(HERE / "records_smoke.jsonl", recs_smoke)
    write_json(HERE / "run_summary_smoke.json", sum_smoke)
    print(json.dumps(sum_smoke, ensure_ascii=False, indent=2), flush=True)
    if args.smoke_only:
        return 0

    recs_formal, sum_formal = run_batch(client, comps_formal, e_ind, workers=args.workers, label="formal")
    write_jsonl(HERE / "records.jsonl", recs_formal)
    write_json(HERE / "run_summary_formal.json", sum_formal)
    print(json.dumps(sum_formal, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
