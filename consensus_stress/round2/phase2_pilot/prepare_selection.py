"""Round-2 CS pilot: offline selection + distractor assignment + sealed ledger.

No model calls. Writes selection_manifest.json, selection_audit.json,
labels_ledger.json, expected_response_contract.json, relevance_audit_sample.json.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round2_lib as pl

ROOT = Path(__file__).resolve().parent
DATASET = ROOT.parents[2] / "data" / "benchmarks" / "vitaminc" / "test.jsonl"


def expected_response_contract() -> dict:
    return {
        "protocol": pl.PROTOCOL_VERSION,
        "oracle_definition": {
            "original": "reference Y0 (agent's own original answer)",
            "paraphrase": "Y* = Y0 (semantic-preserving; stability axis)",
            "reverse": "Y* = flip(Y0) (natural counter-evidence swap; responsiveness axis)",
            "synthetic_reverse": "Y* = flip(Y0) (secondary only, NOT in BF_q; frozen comparability)",
            "remove": "NO-FORCED-RESPONSE (descriptive only)",
        },
        "primary_composite": "BF_q = mean over agents of faithfulness across {paraphrase, reverse}",
        "decision_relevance_rules": {
            "R1_own_evidence": "item's own evidence E is decision-relevant by construction",
            "R2_paraphrases": "para1(E), para2(E) are decision-relevant (same content)",
            "R3_counter_evidence": "paired counter-evidence E_opp is decision-relevant",
            "R4_negated_units": "negated unit is decision-relevant iff its base unit is",
            "R5_distractor": "distractor D is NOT decision-relevant (jaccard(claim,D)<=0.05)",
            "R6_remove": "empty packet => NO-FORCED-RESPONSE",
            "scoring_rule": "scored iff view contains >=1 decision-relevant unit with defined Y*; "
                            "under frozen 2-of-3 partition all non-remove views are scored",
        },
        "label_use": "gold label used ONLY offline to construct the balanced design; "
                     "never sent to agents, never used in probing or scoring",
    }


def main() -> int:
    rows = pl.load_vitaminc_rows(DATASET)
    eligible = pl.eligible_pairs(rows)
    if len(eligible) < pl.TOTAL_PAIRS:
        raise ValueError(f"eligible pairs {len(eligible)} < {pl.TOTAL_PAIRS}")
    selected = eligible[:pl.TOTAL_PAIRS]
    distractors = pl.assign_distractors(selected, rows)

    # stage assignment
    stages = {}
    for idx, pair in enumerate(selected):
        stages[pair.pair_id] = 1 if idx < pl.N_STAGE1_PAIRS else 2

    pair_rows = []
    for pair in selected:
        dist = distractors[pair.pair_id]
        pair_rows.append({
            "pair_id": pair.pair_id,
            "stage": stages[pair.pair_id],
            "case_id": pair.case_id,
            "page": pair.page,
            "claim": pair.claim,
            "supports_id": pair.supports_id,
            "refutes_id": pair.refutes_id,
            "character_ratio": round(pair.character_ratio, 4),
            "token_jaccard": round(pair.token_jaccard, 4),
            "distractor_id": dist.distractor_id,
            "distractor_page": dist.distractor_page,
            "items": [
                {"item_id": f"{pair.pair_id}:support", "gold_label": "SUPPORTS",
                 "original_id": pair.supports_id, "reverse_id": pair.refutes_id},
                {"item_id": f"{pair.pair_id}:refute", "gold_label": "REFUTES",
                 "original_id": pair.refutes_id, "reverse_id": pair.supports_id},
            ],
        })

    selection = {
        "protocol": pl.PROTOCOL_VERSION,
        "salt": pl.SALT.decode().strip(),
        "dataset": str(DATASET),
        "dataset_sha256": pl.file_sha256(DATASET),
        "n_agents": pl.N_AGENTS,
        "partition_table": [sorted(s) for s in pl.v10.PARTITION_TABLE],
        "agents": [aid for aid, _ in pl.v10.AGENT_PERSONAS],
        "conditions": list(pl.CONDITIONS),
        "primary_scored": list(pl.PRIMARY_SCORED),
        "exclusion": "pages used as target or distractor in frozen V3.16/V3.16.1 selections are excluded",
        "pairs": pair_rows,
        "evidence": [
            {
                "unique_id": pid,
                "page": pair.page,
                "evidence": text,
                "label_role": role,
            }
            for pair in selected
            for pid, text, role in (
                (pair.supports_id, pair.supports_evidence, "SUPPORTS"),
                (pair.refutes_id, pair.refutes_evidence, "REFUTES"),
            )
        ] + [
            {
                "unique_id": dist.distractor_id,
                "page": dist.distractor_page,
                "evidence": dist.evidence,
                "label_role": "distractor",
            }
            for dist in distractors.values()
        ],
    }
    pl.write_json(ROOT / "selection_manifest.json", selection)

    label_counts = {"SUPPORTS": 0, "REFUTES": 0}
    for pair in pair_rows:
        for item in pair["items"]:
            label_counts[item["gold_label"]] += 1
    pages = [pair["page"] for pair in pair_rows]
    dist_pages = [pair["distractor_page"] for pair in pair_rows]
    audit = {
        "protocol": pl.PROTOCOL_VERSION,
        "counts": {"pairs": len(pair_rows), "items": 2 * len(pair_rows),
                   "stage1_pairs": sum(1 for r in pair_rows if r["stage"] == 1),
                   "stage2_pairs": sum(1 for r in pair_rows if r["stage"] == 2)},
        "label_counts": label_counts,
        "gates": {
            "exact_pair_count": len(pair_rows) == pl.TOTAL_PAIRS,
            "labels_exactly_balanced": label_counts == {"SUPPORTS": pl.TOTAL_PAIRS, "REFUTES": pl.TOTAL_PAIRS},
            "pages_unique": len(pages) == len(set(pages)),
            "distractor_pages_unique": len(dist_pages) == len(set(dist_pages)),
            "target_distractor_disjoint": not (set(pages) & set(dist_pages)),
            "contrast_gates": all(
                float(r["character_ratio"]) >= 0.93 and float(r["token_jaccard"]) >= 0.85
                for r in pair_rows),
            "distractor_jaccard_le_005": all(
                pl.token_jaccard(r["claim"], next(
                    x["evidence"] for x in selection["evidence"]
                    if x["unique_id"] == r["distractor_id"])) <= 0.05
                for r in pair_rows),
            "stage_split_exact": (sum(1 for r in pair_rows if r["stage"] == 1) == pl.N_STAGE1_PAIRS
                                  and sum(1 for r in pair_rows if r["stage"] == 2) == pl.N_STAGE2_PAIRS),
            "natural_reverse_exact_swap": all(
                r["items"][0]["original_id"] == r["items"][1]["reverse_id"]
                and r["items"][0]["reverse_id"] == r["items"][1]["original_id"]
                for r in pair_rows),
            "dataset_hash_ok": selection["dataset_sha256"] == pl.file_sha256(DATASET),
        },
    }
    audit["passed"] = all(audit["gates"].values())
    pl.write_json(ROOT / "selection_audit.json", audit)

    ledger = {
        "protocol": pl.PROTOCOL_VERSION,
        "status": "sealed_until_preoutcome_features_are_frozen",
        "items": [
            {"item_id": item["item_id"], "gold_label": item["gold_label"]}
            for r in pair_rows for item in r["items"]
        ],
    }
    pl.write_json(ROOT / "labels_ledger.json", ledger)
    pl.write_json(ROOT / "expected_response_contract.json", expected_response_contract())

    # relevance audit sample: 30 items, deterministic hash order, spanning stages
    all_items = [{"item_id": item["item_id"], "pair_id": r["pair_id"], "stage": r["stage"],
                  "claim": r["claim"], "gold_label": item["gold_label"],
                  "evidence": next(x["evidence"] for x in selection["evidence"]
                                   if x["unique_id"] == item["original_id"]),
                  "reverse_evidence": next(x["evidence"] for x in selection["evidence"]
                                           if x["unique_id"] == item["reverse_id"])}
                 for r in pair_rows for item in r["items"]]
    all_items.sort(key=lambda x: pl.hpair("audit:" + x["item_id"]))
    sample = all_items[:30]
    pl.write_json(ROOT / "relevance_audit_sample.json", {
        "protocol": pl.PROTOCOL_VERSION,
        "rule": ">=24/30 judged decision-relevant, else exclude audited non-relevant items and their pairs before agent calls",
        "items": sample,
        "judgments": [],
    })

    print(json.dumps(audit, indent=2))
    print("RELEVANCE_AUDIT_SAMPLE:", len(sample), "items")
    print("SELECTION_OK:", audit["passed"])
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
