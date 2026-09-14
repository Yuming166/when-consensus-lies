"""Phase 3: continuous lambda stress (fresh calls; no labels; no expected-response oracle at intermediate lambda).

Reversal axis: each decision-relevant unit in the agent view is replaced by its natural
counter-evidence with probability lambda (seeded). Removal axis: each decision-relevant unit
is removed with probability lambda (seeded). Distractor unchanged. lambda in {0.2,0.4,0.6,0.8}.
Anchors lambda=0 (original) and lambda=1 (reverse/remove) come from the main-cohort records.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
LAMBDAS = (0.2, 0.4, 0.6, 0.8)
AXES = ("reversal", "removal")
N_SUBSET_PAIRS = 120
N_WORKERS = 16


def lambda_subset_pairs(sel: dict) -> list[dict]:
    pairs = sorted(sel["pairs"], key=lambda p: pl.hpair("lambda:" + p["pair_id"]))
    return pairs[:N_SUBSET_PAIRS]


def seed_for(item_id: str, agent_index: int, axis: str, lam: float) -> int:
    raw = f"{item_id}:{agent_index}:{axis}:{lam}".encode()
    return int(hashlib.sha256(pl.SALT + raw).hexdigest()[:16], 16)


def build_lambda_view(comp, agent_index, axis, lam, rng):
    partition = pl.v10.PARTITION_TABLE[agent_index]
    base = {"E01": comp.evidence, "E02": comp.para1, "E03": comp.distractor}
    opp = {"E01": comp.evidence_opp, "E02": comp.para1_opp}
    items = []
    for eid in ("E01", "E02", "E03"):
        if eid not in partition:
            continue
        if eid == "E03":
            items.append((eid, comp.distractor))
            continue
        if axis == "reversal":
            text = opp[eid] if rng.random() < lam else base[eid]
            items.append((eid, text))
        else:  # removal
            if rng.random() < lam:
                continue
            items.append((eid, base[eid]))
    return pl.v10.EvidenceView(condition=f"lambda_{axis}_{lam}", items=tuple(items))


def run_subset(client, comps_by_cqid, pairs_subset, workers: int) -> tuple[list[dict], dict]:
    tasks = [(comp, agent_index, axis, lam)
             for comp in comps_by_cqid.values()
             for agent_index in range(pl.N_AGENTS)
             for axis in AXES for lam in LAMBDAS]
    expected = len(tasks)
    records: list[dict] = []
    start = time.monotonic()
    done = 0

    def make(comp, agent_index, axis, lam):
        rng = __import__("random").Random(seed_for(comp.item_id, agent_index, axis, lam))
        view = build_lambda_view(comp, agent_index, axis, lam, rng)
        rec = pl.run_one_agent_call(client, comp, view, agent_index=agent_index)
        rec["axis"] = axis
        rec["lambda"] = lam
        rec["condition"] = view.condition
        return rec

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(make, comp, agent_index, axis, lam): None
                   for comp, agent_index, axis, lam in tasks}
        for fut in as_completed(futures):
            rec = fut.result()
            records.append(rec)
            done += 1
            if done % 1000 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                print(f"[phase3] {done}/{expected} success={ok} elapsed={time.monotonic()-start:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["axis"], r["lambda"]))
    summary = {
        "expected_calls": expected, "records": len(records),
        "success": sum(1 for r in records if r["success"]),
        "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4),
    }
    return records, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    args = ap.parse_args()

    sel = json.loads((ROOT / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((ROOT / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    pairs_subset = lambda_subset_pairs(sel)
    subset_ids = {p["pair_id"] for p in pairs_subset}
    distractors = {r["pair_id"]: pl.Distractor(
        distractor_id=r["distractor_id"], distractor_page=r["distractor_page"],
        evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["distractor_id"]),
    ) for r in sel["pairs"] if r["pair_id"] in subset_ids}
    npairs = [pl.NaturalPair(
        pair_id=r["pair_id"], case_id=r["case_id"], page=r["page"], claim=r["claim"],
        supports_id=r["supports_id"], refutes_id=r["refutes_id"],
        supports_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["supports_id"]),
        refutes_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["refutes_id"]),
        character_ratio=float(r["character_ratio"]), token_jaccard=float(r["token_jaccard"]),
    ) for r in pairs_subset]
    comps = pl.build_composites(npairs, distractors, artifacts, stage_override=1)
    print(f"phase3 items: {len(comps)} (expect {N_SUBSET_PAIRS * 2})")
    client = pl.CachedChatClient(ROOT / "cache")
    records, summary = run_subset(client, {c.cqid: c for c in comps}, pairs_subset, args.workers)
    pl.write_jsonl(ROOT / "records_phase3_lambda.jsonl", records)
    pl.write_json(ROOT / "run_summary_phase3.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
