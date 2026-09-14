"""Confirmation cohort: 5-agent panel, no labels. 50 pairs / 100 items x 5 agents x 5 cond."""
from __future__ import annotations
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import round2_lib as pl

ROOT = Path(__file__).resolve().parent
PREFIX = "confirmation"
N_WORKERS = 16


def build_composites():
    sel = json.loads((ROOT / f"{PREFIX}_selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((ROOT / f"{PREFIX}_paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {}
    for uid, row in para.items():
        if not row.get("usable"):
            raise ValueError(f"unusable paraphrase: {uid}")
        artifacts[uid] = {"para1": row["para1"], "para2": row["para2"]}
    pairs = sel["pairs"]
    distractors = {r["pair_id"]: pl.Distractor(
        distractor_id=r["distractor_id"], distractor_page=r["distractor_page"],
        evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["distractor_id"]))
        for r in pairs}
    npairs = [pl.NaturalPair(
        pair_id=r["pair_id"], case_id=r["case_id"], page=r["page"], claim=r["claim"],
        supports_id=r["supports_id"], refutes_id=r["refutes_id"],
        supports_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["supports_id"]),
        refutes_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["refutes_id"]),
        character_ratio=float(r["character_ratio"]), token_jaccard=float(r["token_jaccard"]))
        for r in pairs]
    return pl.build_composites(npairs, distractors, artifacts, stage_override=1)


def main() -> int:
    comps = build_composites()
    print(f"confirmation items: {len(comps)} (expect {50*2})")
    tasks = [(comp, ai, cond) for comp in comps for ai in range(pl.N_AGENTS) for cond in pl.CONDITIONS]
    expected = len(tasks)
    client = pl.CachedChatClient(ROOT / "cache")
    records = []
    start = time.monotonic()
    done = 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as pool:
        futs = {pool.submit(pl.run_one_agent_call, client, comp,
                            pl.build_view(comp, ai, cond), agent_index=ai): (comp.cqid, ai, cond)
                for comp, ai, cond in tasks}
        for fut in as_completed(futs):
            records.append(fut.result())
            done += 1
            if done % 500 == 0 or done == expected:
                print(f"[conf] {done}/{expected} ok={sum(1 for r in records if r['success'])} "
                      f"elapsed={time.monotonic()-start:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    pl.write_jsonl(ROOT / f"{PREFIX}_records.jsonl", records)
    total = len(records); success = sum(1 for r in records if r["success"])
    first = sum(1 for r in records if r["first_pass_valid"])
    summary = {"expected_calls": expected, "records": total, "success": success,
               "first_pass_valid": first, "valid_rate": round(success / max(1, total), 4),
               "first_pass_rate": round(first / max(1, total), 4)}
    pl.write_json(ROOT / f"{PREFIX}_run_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if (success == total == expected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
