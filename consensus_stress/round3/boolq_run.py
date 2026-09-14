"""Balanced BoolQ cross-dataset: run 5-agent panel (100 q x 5 agents x 4 conditions = 2000 calls)."""
from __future__ import annotations
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase2"))
import round3_lib as pl3
import pilot_lib as pl2

ROOT = Path(__file__).resolve().parent
DATASET = ROOT.parents[1] / "data" / "benchmarks" / "boolq" / "train.parquet"
SALT = b"cs-paper-boolq-20260913\n"
CONDITIONS = ("original", "paraphrase", "reverse", "remove")
N_WORKERS = 16


def main() -> int:
    pl2.SALT = SALT
    pl2.PROTOCOL_VERSION = "cs-paper-boolq-20260913"
    pl2.configure_v10()
    comps = pl2.load_composites(DATASET)
    print("comps:", len(comps))
    para_raw = json.loads((ROOT / "boolq_paraphrase_manifest.json").read_text(encoding="utf-8"))
    para = {}
    for qid, row in para_raw.items():
        if not row.get("usable"):
            raise ValueError(f"unusable paraphrase: {qid}")
        para[qid] = {"paraphrase_sentence": row["para1"]}
    client = pl3.CachedChatClient(ROOT / "cache")
    tasks = [(comp, agent_index, condition)
             for comp in comps for agent_index in range(pl3.N_AGENTS) for condition in CONDITIONS]
    expected = len(tasks)
    print("expected calls:", expected)
    records = []
    start = time.monotonic()
    done = 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as pool:
        futures = {
            pool.submit(pl2.run_one_agent_call, client, comp,
                        pl2.build_evidence_view(comp, agent_index, condition,
                                                substitute_manifest={}, paraphrase_manifest=para),
                        agent_index=agent_index): None
            for comp, agent_index, condition in tasks
        }
        for fut in as_completed(futures):
            records.append(fut.result())
            done += 1
            if done % 500 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                print(f"[boolq] {done}/{expected} success={ok} elapsed={time.monotonic()-start:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    summary = {"protocol": "cs-paper-boolq-20260913", "expected_calls": expected,
               "records": len(records), "success": sum(1 for r in records if r["success"]),
               "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4)}
    pl3.write_jsonl(ROOT / "boolq_records.jsonl", records)
    pl3.write_json(ROOT / "run_summary_boolq.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
