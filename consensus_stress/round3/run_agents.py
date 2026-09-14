"""Round-3 paper-scale: run 5-agent panel on 300 VitaminC pairs (no labels).

Stage 1 = first 150 pairs (300 items x 5 agents x 5 conditions = 7500 calls).
Stage 2 runs only if stage-1 integrity passes (>=0.95 valid + audits). NO outcomes used.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
N_WORKERS = 16
VALIDITY_MIN = 0.95


def load_artifacts() -> tuple[dict, dict]:
    sel = json.loads((ROOT / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((ROOT / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {}
    for uid, row in para.items():
        if not row.get("usable"):
            raise ValueError(f"unusable paraphrase: {uid}")
        artifacts[uid] = {"para1": row["para1"], "para2": row["para2"]}
    return sel, artifacts


def build_composites_for_stage(sel: dict, artifacts: dict, stage: int):
    pairs = [r for r in sel["pairs"] if r["stage"] == stage]
    distractors = {r["pair_id"]: pl.Distractor(
        distractor_id=r["distractor_id"], distractor_page=r["distractor_page"],
        evidence=next(e["evidence"] for e in sel["evidence"]
                      if e["unique_id"] == r["distractor_id"]),
    ) for r in pairs}
    npairs = [pl.NaturalPair(
        pair_id=r["pair_id"], case_id=r["case_id"], page=r["page"], claim=r["claim"],
        supports_id=r["supports_id"], refutes_id=r["refutes_id"],
        supports_evidence=next(e["evidence"] for e in sel["evidence"]
                               if e["unique_id"] == r["supports_id"]),
        refutes_evidence=next(e["evidence"] for e in sel["evidence"]
                              if e["unique_id"] == r["refutes_id"]),
        character_ratio=float(r["character_ratio"]), token_jaccard=float(r["token_jaccard"]),
    ) for r in pairs]
    return pl.build_composites(npairs, distractors, artifacts, stage_override=stage)


def run_stage(client, comps, *, stage: int, workers: int) -> tuple[list[dict], dict]:
    tasks = [(comp, agent_index, condition)
             for comp in comps for agent_index in range(pl.N_AGENTS)
             for condition in pl.CONDITIONS]
    expected = len(tasks)
    records: list[dict] = []
    start = time.monotonic()
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(pl.run_one_agent_call, client, comp,
                        pl.build_view(comp, agent_index, condition),
                        agent_index=agent_index): (comp.cqid, agent_index, condition)
            for comp, agent_index, condition in tasks
        }
        for fut in as_completed(futures):
            rec = fut.result()
            records.append(rec)
            done += 1
            if done % 1000 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                print(f"[run-stage{stage}] {done}/{expected} success={ok} "
                      f"elapsed={time.monotonic()-start:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    total = len(records)
    success = sum(1 for r in records if r["success"])
    first_pass = sum(1 for r in records if r["first_pass_valid"])
    summary = {
        "stage": stage,
        "expected_calls": expected,
        "records": total,
        "success": success,
        "first_pass_valid": first_pass,
        "valid_rate": round(success / max(1, total), 4),
        "first_pass_rate": round(first_pass / max(1, total), 4),
        "per_condition": {
            cond: {"n": sum(1 for r in records if r["condition"] == cond),
                   "success": sum(1 for r in records if r["condition"] == cond and r["success"])}
            for cond in pl.CONDITIONS
        },
    }
    return records, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    ap.add_argument("--stage1-only", action="store_true")
    args = ap.parse_args()

    sel, artifacts = load_artifacts()
    client = pl.CachedChatClient(ROOT / "cache")

    comps1 = build_composites_for_stage(sel, artifacts, stage=1)
    print(f"stage1 items: {len(comps1)} (expect {pl.N_STAGE1_PAIRS * 2})")
    records1, sum1 = run_stage(client, comps1, stage=1, workers=args.workers)
    pl.write_jsonl(ROOT / "records_stage1.jsonl", records1)
    pl.write_json(ROOT / "run_summary_stage1.json", sum1)
    print(json.dumps(sum1, indent=2))

    integrity_ok = (sum1["valid_rate"] >= VALIDITY_MIN and sum1["records"] == sum1["expected_calls"])
    rel = json.loads((ROOT / "relevance_audit.json").read_text(encoding="utf-8"))
    pa = json.loads((ROOT / "paraphrase_audit.json").read_text(encoding="utf-8")) if (ROOT/"paraphrase_audit.json").exists() else {"threshold_ge_80pct": True}
    audits_ok = bool(rel["threshold_ge_80pct"] and pa.get("threshold_ge_80pct", True))
    print(f"STAGE1_INTEGRITY: valid_rate={sum1['valid_rate']} integrity_ok={integrity_ok} audits_ok={audits_ok}")

    if args.stage1_only or not integrity_ok or not audits_ok:
        print("STAGE2_SKIPPED (outcome-free expansion decision)")
        merged = records1
    else:
        comps2 = build_composites_for_stage(sel, artifacts, stage=2)
        print(f"stage2 items: {len(comps2)} (expect {pl.N_STAGE2_PAIRS * 2})")
        records2, sum2 = run_stage(client, comps2, stage=2, workers=args.workers)
        pl.write_jsonl(ROOT / "records_stage2.jsonl", records2)
        pl.write_json(ROOT / "run_summary_stage2.json", sum2)
        print(json.dumps(sum2, indent=2))
        merged = records1 + records2

    pl.write_jsonl(ROOT / "records.jsonl", merged)
    total_ok = sum(1 for r in merged if r["success"])
    print(f"TOTAL_RECORDS: {len(merged)} success={total_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
