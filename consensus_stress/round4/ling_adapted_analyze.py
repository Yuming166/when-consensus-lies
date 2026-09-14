"""Analyze the round-4 adapted Ling run after preoutcome features are frozen."""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R3 = HERE.parent / "round3"
sys.path.insert(0, str(R3))
import analysis_lib as al  # noqa: E402
import round3_lib as pl  # noqa: E402

ANALYSIS = HERE / "analysis"
HC_THRESHOLD = al.HC_THRESHOLD
SEED = 20_260_913 + 400


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def merge_labels(feats: list[dict]) -> list[dict]:
    ledger = json.loads((R3 / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {row["item_id"]: row["gold_label"] for row in ledger["items"]}
    for row in feats:
        label = gold[row["item_id"]]
        row["gold_label"] = label
        row["gold_yes"] = label == "SUPPORTS"
        row["consensus_wrong"] = int((row["consensus"] == "yes") != row["gold_yes"])
        row["risk_bf_q"] = -row["bf_q"] if row.get("bf_q") is not None else None
        row["disagreement"] = 1.0 - row["agreement"]
    return feats


def pair_group_mean_diff(rows: list[dict], key: str, n: int = 2000, seed: int = SEED) -> dict:
    rng = random.Random(seed)
    by_pair: dict[str, list[dict]] = {}
    for row in rows:
        if row.get(key) is not None:
            by_pair.setdefault(row["pair_id"], []).append(row)
    pairs = sorted(by_pair)

    def statistic(sample: list[dict]) -> float | None:
        correct = [row[key] for row in sample if not row["consensus_wrong"]]
        wrong = [row[key] for row in sample if row["consensus_wrong"]]
        if not correct or not wrong:
            return None
        return float(np.mean(correct) - np.mean(wrong))

    all_rows = [row for p in pairs for row in by_pair[p]]
    obs = statistic(all_rows)
    vals = []
    for _ in range(n):
        sample = [row for _ in pairs for row in by_pair[rng.choice(pairs)]]
        value = statistic(sample)
        if value is not None:
            vals.append(value)
    vals.sort()
    return {
        "correct_mean": float(np.mean([row[key] for row in all_rows if not row["consensus_wrong"]])),
        "wrong_mean": float(np.mean([row[key] for row in all_rows if row["consensus_wrong"]])),
        "diff_correct_minus_wrong": obs,
        "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
        "n": len(all_rows), "n_pairs": len(pairs),
    }


def main() -> None:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    records = load_jsonl(HERE / "ling_records.jsonl")
    ling_all = merge_labels(load_jsonl(HERE / "ling_preoutcome_features.jsonl"))
    qwen_all = merge_labels(load_jsonl(R3 / "preoutcome_features.jsonl"))
    qwen_by_item = {row["item_id"]: row for row in qwen_all}
    for row in ling_all:
        q = qwen_by_item.get(row["item_id"])
        if q:
            row["qwen_risk"] = q["risk_bf_q"]
            row["qwen_bf_reverse"] = q["bf_reverse"]
            row["qwen_bf_paraphrase"] = q["bf_paraphrase"]
    ling_hc = [row for row in ling_all if row["agreement"] >= HC_THRESHOLD]

    primary = al.group_bootstrap(ling_hc, "risk_bf_q", seed=SEED + 1)
    per_label = {
        label: al.label_subgroup_bootstrap(ling_hc, "risk_bf_q", label, seed=SEED + 2)
        for label in ("SUPPORTS", "REFUTES")
    }
    macro = al.macro_ci(ling_hc, "risk_bf_q", seed=SEED + 3)
    worst_label = min(per_label, key=lambda k: per_label[k]["auroc"])
    para_agent_flip = sum(
        1 for row in ling_all for i in range(5)
        if row["_agent_bf"][str(i)]["paraphrase"] == 0
    ) / (5 * len(ling_all))
    permutation = al.permutation_risk(ling_hc, seed=SEED + 4)
    reducibility = {
        "spearman_risk_agreement": al.spearman(
            [row["risk_bf_q"] for row in ling_hc],
            [row["agreement"] for row in ling_hc]),
        "spearman_risk_confidence": al.spearman(
            [row["risk_bf_q"] for row in ling_hc],
            [row["mean_confidence"] for row in ling_hc]),
    }
    risk80 = al.risk_at_80_bootstrap(ling_hc, "risk_bf_q", seed=SEED + 5)
    pipeline_rate = sum(1 for row in records if row["success"]) / len(records)
    gates = {
        "pipeline_ge_0.95": pipeline_rate >= 0.95,
        "primary_ci_lb_gt_0.5": bool(primary and primary["ci"][0] > 0.5),
        "primary_point_ge_0.60": bool(primary and primary["auroc"] >= 0.60),
        "macro_ci_lb_gt_0.5": bool(macro and macro["ci"][0] > 0.5),
        "worst_label_ci_lb_gt_0.5": bool(per_label[worst_label]["ci"][0] > 0.5),
        "paraphrase_placebo_le_0.30": para_agent_flip <= 0.30,
        "permutation_obs_gt_95pct": bool(permutation and permutation["obs_auroc"] > permutation["perm_95pct"]),
        "reducibility_abs_spearman_lt_0.9": bool(
            abs(reducibility["spearman_risk_agreement"]) < 0.9 and
            abs(reducibility["spearman_risk_confidence"]) < 0.9),
    }
    gates["all_pass"] = all(gates.values())

    qwen_transfer = al.group_bootstrap(ling_hc, "qwen_risk", seed=SEED + 10)
    qwen_transfer_risk80 = al.risk_at_80_bootstrap(ling_hc, "qwen_risk", seed=SEED + 11)
    paired_auroc = al.paired_bootstrap_diff(
        ling_hc, "qwen_risk", "risk_bf_q", seed=SEED + 12)
    paired_risk80 = al.risk_at_80_paired_diff(
        ling_hc, "qwen_risk", "risk_bf_q", seed=SEED + 13)
    mechanism = pair_group_mean_diff(ling_hc, "bf_reverse", seed=SEED + 14)
    mechanism_gate = bool(mechanism["diff_correct_minus_wrong"] > 0 and mechanism["ci"][0] > 0)
    both_transfer_scores = {
        "qwen_transfer_primary_ci_lb_gt_0.5": bool(qwen_transfer and qwen_transfer["ci"][0] > 0.5),
        "ling_own_primary_ci_lb_gt_0.5": bool(primary and primary["ci"][0] > 0.5),
    }

    shared_scores = [row for row in ling_hc
                     if row.get("risk_bf_q") is not None and row.get("qwen_risk") is not None]
    item_corr = {
        "spearman_qwen_risk_ling_risk": al.spearman(
            [row["qwen_risk"] for row in shared_scores],
            [row["risk_bf_q"] for row in shared_scores]),
        "n": len(shared_scores), "n_pairs": len({row["pair_id"] for row in shared_scores}),
    }

    qwen_hc = [row for row in qwen_all if row["agreement"] >= HC_THRESHOLD]
    qwen_context = {
        "primary_auroc": al.group_bootstrap(qwen_hc, "risk_bf_q", seed=SEED + 20),
        "risk_at_80": al.risk_at_80_bootstrap(qwen_hc, "risk_bf_q", seed=SEED + 21),
        "n_hc": len(qwen_hc),
        "wrong_hc": sum(row["consensus_wrong"] for row in qwen_hc),
    }
    overlap_rows = []
    for row in ling_all:
        q = qwen_by_item.get(row["item_id"])
        if not q:
            continue
        overlap_rows.append({
            "pair_id": row["pair_id"], "ling_hc": row["agreement"] >= HC_THRESHOLD,
            "qwen_hc": q["agreement"] >= HC_THRESHOLD,
            "same_consensus": row["consensus"] == q["consensus"],
            "qwen_wrong": q["consensus_wrong"], "ling_wrong": row["consensus_wrong"],
        })
    both_hc = [row for row in overlap_rows if row["ling_hc"] and row["qwen_hc"]]
    model_overlap = {
        "all_items": {
            "n": len(overlap_rows),
            "same_consensus": sum(row["same_consensus"] for row in overlap_rows),
            "both_wrong": sum(row["qwen_wrong"] and row["ling_wrong"] for row in overlap_rows),
            "qwen_only_wrong": sum(row["qwen_wrong"] and not row["ling_wrong"] for row in overlap_rows),
            "ling_only_wrong": sum(not row["qwen_wrong"] and row["ling_wrong"] for row in overlap_rows),
            "both_correct": sum(not row["qwen_wrong"] and not row["ling_wrong"] for row in overlap_rows),
        },
        "both_hc": {
            "n": len(both_hc),
            "same_consensus": sum(row["same_consensus"] for row in both_hc),
            "both_wrong": sum(row["qwen_wrong"] and row["ling_wrong"] for row in both_hc),
            "qwen_only_wrong": sum(row["qwen_wrong"] and not row["ling_wrong"] for row in both_hc),
            "ling_only_wrong": sum(not row["qwen_wrong"] and row["ling_wrong"] for row in both_hc),
            "both_correct": sum(not row["qwen_wrong"] and not row["ling_wrong"] for row in both_hc),
        },
    }

    result = {
        "protocol": "cs-paper-ling-adapted-20260913-round4",
        "cohort": {"n_pairs": len({row["pair_id"] for row in ling_all}),
                   "n_items": len(ling_all), "n_hc": len(ling_hc),
                   "wrong_hc": sum(row["consensus_wrong"] for row in ling_hc),
                   "hc_by_label": dict(Counter(row["gold_label"] for row in ling_hc)),
                   "wrong_by_label": dict(Counter(row["gold_label"] for row in ling_hc if row["consensus_wrong"]))},
        "pipeline": {"records": len(records), "success": sum(row["success"] for row in records),
                     "valid_rate": pipeline_rate,
                     "first_pass_rate": sum(row["first_pass_valid"] for row in records) / len(records),
                     "per_condition": {
                         cond: {"n": sum(row["condition"] == cond for row in records),
                                "success": sum(row["condition"] == cond and row["success"] for row in records)}
                         for cond in pl.CONDITIONS}},
        "ling_within_model": {
            "primary_auroc": primary, "per_label": per_label, "macro": macro,
            "worst_label": worst_label, "risk_at_80": risk80,
            "paraphrase_agent_infidelity": para_agent_flip,
            "permutation": permutation, "reducibility": reducibility,
            "gates": gates},
        "cross_model": {
            "qwen_score_transfer_auroc": qwen_transfer,
            "qwen_score_transfer_risk_at_80": qwen_transfer_risk80,
            "ling_own_score_auroc": primary,
            "ling_own_score_risk_at_80": risk80,
            "paired_diff_qwen_transfer_minus_ling_own": {
                "auroc": paired_auroc, "risk_at_80": paired_risk80},
            "transfer_both_primary_ci_lb_gt_0.5": all(both_transfer_scores.values()),
            "transfer_component_gates": both_transfer_scores,
            "item_level_spearman_secondary": item_corr},
        "mechanism_transfer": {
            "reverse_fidelity": mechanism,
            "gate_correct_minus_wrong_ci_lb_gt_0": mechanism_gate},
        "model_comparison_context": {
            "qwen_round3_same_full_cohort": qwen_context,
            "consensus_and_error_overlap": model_overlap},
    }
    (ANALYSIS / "ling_adapted_analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
