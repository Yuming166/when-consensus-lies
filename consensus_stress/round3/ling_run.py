"""Phase 6 cross-model: run the IDENTICAL frozen protocol on Ling-3.0-tiny.

Cohort: first 100 pairs (200 items) of the main 300-pair cohort; same selection manifest,
same paraphrase artifacts, same oracle, same conditions, same BF_q. Only the endpoint/model
changes. Records contain no labels. Cache separate (round3/cache_ling).
"""
from __future__ import annotations
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
LING_ENDPOINT = "http://127.0.0.1:31520/v1/chat/completions"
LING_MODEL = "Ling-3.0-tiny"
N_PAIRS = 100
N_WORKERS = 16
VALIDITY_MIN = 0.90  # frozen: Ling validity gate (lower only for pipeline; primary gates unchanged)


def load_artifacts() -> tuple[dict, dict]:
    sel = json.loads((ROOT / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((ROOT / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    return sel, artifacts


def build_composites_first_n(sel: dict, artifacts: dict, n: int):
    pairs = sel["pairs"][:n]
    distractors = {r["pair_id"]: pl.Distractor(
        distractor_id=r["distractor_id"], distractor_page=r["distractor_page"],
        evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["distractor_id"]),
    ) for r in pairs}
    npairs = [pl.NaturalPair(
        pair_id=r["pair_id"], case_id=r["case_id"], page=r["page"], claim=r["claim"],
        supports_id=r["supports_id"], refutes_id=r["refutes_id"],
        supports_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["supports_id"]),
        refutes_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["refutes_id"]),
        character_ratio=float(r["character_ratio"]), token_jaccard=float(r["token_jaccard"]),
    ) for r in pairs]
    return pl.build_composites(npairs, distractors, artifacts, stage_override=1)


def main() -> int:
    sel, artifacts = load_artifacts()
    comps = build_composites_first_n(sel, artifacts, N_PAIRS)
    print(f"ling items: {len(comps)} (expect {N_PAIRS * 2})")
    pl.ENDPOINT = LING_ENDPOINT
    pl.MODEL = LING_MODEL
    client = pl.CachedChatClient(ROOT / "cache_ling")
    tasks = [(comp, agent_index, condition)
             for comp in comps for agent_index in range(pl.N_AGENTS) for condition in pl.CONDITIONS]
    expected = len(tasks)
    records: list[dict] = []
    start = time.monotonic()
    done = 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as pool:
        futures = {
            pool.submit(pl.run_one_agent_call, client, comp,
                        pl.build_view(comp, agent_index, condition), agent_index=agent_index): None
            for comp, agent_index, condition in tasks
        }
        for fut in as_completed(futures):
            records.append(fut.result())
            done += 1
            if done % 500 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                print(f"[ling] {done}/{expected} success={ok} elapsed={time.monotonic()-start:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    summary = {
        "protocol": pl.PROTOCOL_VERSION, "model": LING_MODEL, "endpoint": LING_ENDPOINT,
        "n_pairs": N_PAIRS, "expected_calls": expected, "records": len(records),
        "success": sum(1 for r in records if r["success"]),
        "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4),
        "first_pass_rate": round(sum(1 for r in records if r["first_pass_valid"]) / max(1, len(records)), 4),
        "per_condition": {cond: {"n": sum(1 for r in records if r["condition"] == cond),
                                 "success": sum(1 for r in records if r["condition"] == cond and r["success"])}
                          for cond in pl.CONDITIONS},
    }
    pl.write_jsonl(ROOT / "ling_records.jsonl", records)
    pl.write_json(ROOT / "run_summary_ling.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
