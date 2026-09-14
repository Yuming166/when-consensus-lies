"""Round-2 CS confirmation: offline selection of pairs 100-149 (disjoint from pilot)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round2_lib as pl

ROOT = Path(__file__).resolve().parent
DATASET = ROOT.parents[2] / "data" / "benchmarks" / "vitaminc" / "test.jsonl"
OFFSET = 100
N_PAIRS = 50
PREFIX = "confirmation"


def main() -> int:
    rows = pl.load_vitaminc_rows(DATASET)
    eligible = pl.eligible_pairs(rows)
    if len(eligible) < OFFSET + N_PAIRS:
        raise ValueError(f"eligible {len(eligible)} < {OFFSET + N_PAIRS}")
    selected = eligible[OFFSET:OFFSET + N_PAIRS]
    distractors = pl.assign_distractors(selected, rows)

    pair_rows = []
    for pair in selected:
        dist = distractors[pair.pair_id]
        pair_rows.append({
            "pair_id": pair.pair_id, "stage": 1, "case_id": pair.case_id, "page": pair.page,
            "claim": pair.claim, "supports_id": pair.supports_id, "refutes_id": pair.refutes_id,
            "character_ratio": round(pair.character_ratio, 4), "token_jaccard": round(pair.token_jaccard, 4),
            "distractor_id": dist.distractor_id, "distractor_page": dist.distractor_page,
            "items": [
                {"item_id": f"{pair.pair_id}:support", "gold_label": "SUPPORTS",
                 "original_id": pair.supports_id, "reverse_id": pair.refutes_id},
                {"item_id": f"{pair.pair_id}:refute", "gold_label": "REFUTES",
                 "original_id": pair.refutes_id, "reverse_id": pair.supports_id},
            ],
        })
    selection = {
        "protocol": "cs-pilot-vitaminc-conf-2026-09-13",
        "offset": OFFSET,
        "salt": pl.SALT.decode().strip(),
        "dataset": str(DATASET),
        "dataset_sha256": pl.file_sha256(DATASET),
        "n_agents": pl.N_AGENTS,
        "partition_table": [sorted(s) for s in pl.v10.PARTITION_TABLE],
        "agents": [aid for aid, _ in pl.v10.AGENT_PERSONAS],
        "conditions": list(pl.CONDITIONS),
        "primary_scored": list(pl.PRIMARY_SCORED),
        "exclusion": "disjoint from pilot pairs (indices 0-99) and from frozen V3.16/V3.16.1 pages",
        "pairs": pair_rows,
        "evidence": [
            {"unique_id": pid, "page": pair.page, "evidence": text, "label_role": role}
            for pair in selected for pid, text, role in (
                (pair.supports_id, pair.supports_evidence, "SUPPORTS"),
                (pair.refutes_id, pair.refutes_evidence, "REFUTES"),
            )
        ] + [
            {"unique_id": dist.distractor_id, "page": dist.distractor_page,
             "evidence": dist.evidence, "label_role": "distractor"}
            for dist in distractors.values()
        ],
    }
    pl.write_json(ROOT / f"{PREFIX}_selection_manifest.json", selection)

    label_counts = {"SUPPORTS": 0, "REFUTES": 0}
    for r in pair_rows:
        for it in r["items"]:
            label_counts[it["gold_label"]] += 1
    pages = [r["page"] for r in pair_rows]
    audit = {
        "protocol": selection["protocol"],
        "counts": {"pairs": len(pair_rows), "items": 2 * len(pair_rows)},
        "label_counts": label_counts,
        "gates": {
            "exact_pair_count": len(pair_rows) == N_PAIRS,
            "labels_balanced": label_counts == {"SUPPORTS": N_PAIRS, "REFUTES": N_PAIRS},
            "pages_unique": len(pages) == len(set(pages)),
            "contrast_gates": all(float(r["character_ratio"]) >= 0.93 and float(r["token_jaccard"]) >= 0.85 for r in pair_rows),
            "distractor_jaccard_le_005": all(
                pl.token_jaccard(r["claim"], next(e["evidence"] for e in selection["evidence"]
                                                  if e["unique_id"] == r["distractor_id"])) <= 0.05
                for r in pair_rows),
            "disjoint_from_pilot": all(r["pair_id"] not in pilot_pair_ids() for r in pair_rows),
            "natural_reverse_exact_swap": all(
                r["items"][0]["original_id"] == r["items"][1]["reverse_id"]
                and r["items"][0]["reverse_id"] == r["items"][1]["original_id"]
                for r in pair_rows),
        },
    }
    audit["passed"] = all(audit["gates"].values())
    pl.write_json(ROOT / f"{PREFIX}_selection_audit.json", audit)

    ledger = {
        "protocol": selection["protocol"],
        "status": "sealed_until_preoutcome_features_are_frozen",
        "items": [{"item_id": it["item_id"], "gold_label": it["gold_label"]}
                  for r in pair_rows for it in r["items"]],
    }
    pl.write_json(ROOT / f"{PREFIX}_labels_ledger.json", ledger)

    all_items = [{"item_id": it["item_id"], "pair_id": r["pair_id"], "stage": 1,
                  "claim": r["claim"], "gold_label": it["gold_label"],
                  "evidence": next(e["evidence"] for e in selection["evidence"]
                                   if e["unique_id"] == it["original_id"]),
                  "reverse_evidence": next(e["evidence"] for e in selection["evidence"]
                                           if e["unique_id"] == it["reverse_id"])}
                 for r in pair_rows for it in r["items"]]
    all_items.sort(key=lambda x: pl.hpair("audit:" + x["item_id"]))
    sample = all_items[:30]
    pl.write_json(ROOT / f"{PREFIX}_relevance_audit_sample.json", {
        "protocol": selection["protocol"],
        "rule": ">=24/30 judged decision-relevant, else exclude audited non-relevant items and their pairs before agent calls",
        "items": sample, "judgments": [],
    })
    print(json.dumps(audit, indent=2))
    print("CONFIRMATION_SELECTION_OK:", audit["passed"])
    return 0 if audit["passed"] else 1


def pilot_pair_ids() -> set:
    sel = json.loads((ROOT / "selection_manifest.json").read_text(encoding="utf-8"))
    return {r["pair_id"] for r in sel["pairs"]}


if __name__ == "__main__":
    raise SystemExit(main())
