"""CS pilot: run 5-agent panel on all conditions (100 q x 5 agents x 5 cond).

Records contain NO label/gold fields (outcome firewall). Cache reused from
artifact generation. Writes records.jsonl + progress; all-or-nothing validity
check at the end.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_lib as pl

ROOT = Path(__file__).resolve().parent
DATASET = ROOT.parents[1] / "data" / "benchmarks" / "boolq" / "train.parquet"
N_WORKERS = 16


def load_artifacts():
    sel = json.loads((ROOT / "selection_manifest.json").read_text(encoding="utf-8"))
    sub = json.loads((ROOT / "substitute_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((ROOT / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    for qid, row in sub.items():
        if not row.get("usable"):
            raise ValueError(f"unusable substitute: {qid}")
    for qid, row in para.items():
        if not row.get("usable"):
            raise ValueError(f"unusable paraphrase: {qid}")
    return sel, sub, para


def build_tasks():
    sel, sub, para = load_artifacts()
    comps = pl.load_composites(DATASET)
    expected_qids = {c.cqid for c in comps}
    tasks = []
    for comp in comps:
        for agent_index in range(pl.N_AGENTS):
            for condition in pl.CONDITIONS:
                view = pl.build_evidence_view(
                    comp, agent_index, condition,
                    substitute_manifest=sub, paraphrase_manifest=para,
                )
                tasks.append((comp, agent_index, condition, view))
    return tasks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    ap.add_argument("--smoke", action="store_true", help="run 2 questions x 1 agent x 5 conditions")
    args = ap.parse_args()

    tasks = build_tasks()
    if args.smoke:
        tasks = [t for t in tasks if t[0].cqid in {tasks[0][0].cqid, tasks[1][0].cqid}]
        tasks = [t for t in tasks if t[1] == 0][:5]
    expected = len(tasks)
    print(f"tasks: {expected} (unique cqids={len({t[0].cqid for t in tasks})})")

    client = pl.CachedChatClient(ROOT / "cache")
    records = []
    start = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(pl.run_one_agent_call, client, comp, view,
                        agent_index=agent_index): (comp.cqid, agent_index, condition)
            for comp, agent_index, condition, view in tasks
        }
        for fut in as_completed(futures):
            rec = fut.result()
            records.append(rec)
            done += 1
            if done % 250 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                print(f"[run] {done}/{expected} success={ok} "
                      f"elapsed={time.time()-start:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    pl.write_jsonl(ROOT / "records.jsonl", records)

    total = len(records)
    success = sum(1 for r in records if r["success"])
    first_pass = sum(1 for r in records if r["first_pass_valid"])
    per_cond = {}
    for cond in pl.CONDITIONS:
        recs = [r for r in records if r["condition"] == cond]
        per_cond[cond] = {
            "n": len(recs),
            "success": sum(1 for r in recs if r["success"]),
            "first_pass": sum(1 for r in recs if r["first_pass_valid"]),
        }
    summary = {
        "protocol": pl.PROTOCOL_VERSION,
        "expected_calls": expected,
        "records": total,
        "success": success,
        "first_pass_valid": first_pass,
        "valid_rate": success / max(1, total),
        "first_pass_rate": first_pass / max(1, total),
        "per_condition": per_cond,
        "smoke": args.smoke,
    }
    pl.write_json(ROOT / "run_summary.json", summary)
    print(json.dumps(summary, indent=2))
    ok = (success == total) and (total == expected)
    print("RUN_COMPLETE:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
