"""FEVER cross-dataset: run 5-agent panel on FEVER natural claim pairs (no labels)."""
from __future__ import annotations
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
N_WORKERS = 16


def main() -> int:
    sel = json.loads((ROOT / "fever_selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((ROOT / "fever_paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    pairs = sel["pairs"]
    distractors = {r["pair_id"]: pl.Distractor(
        distractor_id=r["distractor_id"], distractor_page=r["distractor_page"],
        evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["distractor_id"]),
    ) for r in pairs}
    npairs = [pl.NaturalPair(
        pair_id=r["pair_id"], case_id=r["case_id"], page=r["page"], claim=r["claim"],
        supports_id=r["supports_id"], refutes_id=r["refutes_id"],
        supports_evidence=r["supports_evidence"], refutes_evidence=r["refutes_evidence"],
        character_ratio=float(r["character_ratio"]), token_jaccard=float(r["token_jaccard"]),
    ) for r in pairs]
    comps = pl.build_composites(npairs, distractors, artifacts, stage_override=1)
    print(f"fever items: {len(comps)} (expect {len(pairs) * 2})")
    client = pl.CachedChatClient(ROOT / "cache")
    tasks = [(comp, agent_index, condition)
             for comp in comps for agent_index in range(pl.N_AGENTS) for condition in pl.CONDITIONS]
    expected = len(tasks)
    records = []
    start = time.monotonic()
    done = 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as pool:
        futures = {pool.submit(pl.run_one_agent_call, client, comp,
                               pl.build_view(comp, agent_index, condition), agent_index=agent_index): None
                   for comp, agent_index, condition in tasks}
        for fut in as_completed(futures):
            records.append(fut.result())
            done += 1
            if done % 500 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                print(f"[fever] {done}/{expected} success={ok} elapsed={time.monotonic()-start:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    summary = {"protocol": pl.PROTOCOL_VERSION + "-fever", "expected_calls": expected,
               "records": len(records), "success": sum(1 for r in records if r["success"]),
               "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4)}
    pl.write_jsonl(ROOT / "fever_records.jsonl", records)
    pl.write_json(ROOT / "run_summary_fever.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
