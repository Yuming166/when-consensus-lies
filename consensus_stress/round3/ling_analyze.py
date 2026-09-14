"""Phase 6 cross-model analysis: Ling within-model validity, per-model comparison on the shared
100-pair cohort, cross-model transfer (frozen RS_q + Qwen logistic), mechanism profile."""
from __future__ import annotations
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analysis_lib as al
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
ANALYSIS_DIR = ROOT / "analysis"


def load_merged(prefix) -> list[dict]:
    feats = [json.loads(l) for l in (ROOT / f"{prefix}_preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((ROOT / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        g = gold[f["item_id"]]
        f["gold_label"] = g
        f["gold_yes"] = g == "SUPPORTS"
        f["consensus_wrong"] = int((f["consensus"] == "yes") != f["gold_yes"])
        f["risk_bf_q"] = -f["bf_q"] if f.get("bf_q") is not None else None
        f["disagreement"] = 1.0 - f["agreement"]
    return feats


def gates_for(prefix):
    feats = load_merged(prefix)
    hc = [f for f in feats if f["agreement"] >= al.HC_THRESHOLD]
    recs = [json.loads(l) for l in (ROOT / f"{prefix}_records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    primary = al.group_bootstrap(hc, "risk_bf_q", seed=20260913 + 50)
    per_label = {k: al.label_subgroup_bootstrap(hc, "risk_bf_q", k, seed=20260913 + 51) for k in ("SUPPORTS", "REFUTES")}
    macro = al.macro_ci(hc, "risk_bf_q", seed=20260913 + 52)
    worst_point = min(per_label["SUPPORTS"]["auroc"], per_label["REFUTES"]["auroc"])
    worst_label = "SUPPORTS" if per_label["SUPPORTS"]["auroc"] <= per_label["REFUTES"]["auroc"] else "REFUTES"
    worst_ci = per_label[worst_label]["ci"]
    para_agent_flip = sum(1 for f in feats for i in range(5)
                          if f["_agent_bf"][str(i)]["paraphrase"] == 0) / (5 * len(feats))
    c2 = al.permutation_risk(hc, seed=20260913 + 53)
    red = {
        "spearman_risk_agreement": round(al.spearman([f["risk_bf_q"] for f in hc], [f["agreement"] for f in hc]), 4),
        "spearman_risk_conf": round(al.spearman([f["risk_bf_q"] for f in hc], [f["mean_confidence"] for f in hc]), 4),
    }
    gates = {
        "g1_pipeline_ge_0.95": len(recs) > 0 and sum(1 for r in recs if r["success"]) / len(recs) >= 0.95,
        "g2_primary_ci_lb_gt_0.5": bool(primary and primary["ci"][0] > 0.5),
        "g2_primary_point_ge_0.60": bool(primary and primary["auroc"] >= 0.60),
        "g3_macro_ci_lb_gt_0.5": bool(macro and macro["ci"][0] > 0.5),
        "g4_worst_ci_lb_gt_0.5": worst_ci[0] > 0.5,
        "g5_placebo_clean": para_agent_flip <= 0.30,
        "g6_perm_pass": bool(c2 and c2["obs_auroc"] > c2["perm_95pct"]),
        "g7_reducibility": bool(red["spearman_risk_agreement"] < 0.9 and red["spearman_risk_conf"] < 0.9),
    }
    gates["pass"] = all(gates[k] for k in ["g1_pipeline_ge_0.95", "g2_primary_ci_lb_gt_0.5",
                                            "g2_primary_point_ge_0.60", "g3_macro_ci_lb_gt_0.5",
                                            "g4_worst_ci_lb_gt_0.5", "g5_placebo_clean",
                                            "g6_perm_pass", "g7_reducibility"])
    return {"prefix": prefix, "n_total": len(feats), "hc": len(hc),
            "wrong_hc": sum(1 for f in hc if f["consensus_wrong"]),
            "hc_by_label": dict(Counter(f["gold_label"] for f in hc)),
            "wrong_by_label": dict(Counter(f["gold_label"] for f in hc if f["consensus_wrong"])),
            "primary": primary, "per_label": per_label, "macro": macro,
            "worst_label": worst_label, "worst_ci": worst_ci, "c2": c2, "reducibility": red,
            "para_agent_flip": round(para_agent_flip, 4), "gates": gates,
            "risk80": al.risk_at_80_bootstrap(hc, "risk_bf_q", seed=20260913 + 54)}


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    qwen = load_merged("")   # main cohort features (all 300 pairs)
    ling = load_merged("ling")
    qwen_by_item = {f["item_id"]: f for f in qwen}
    shared = [f for f in ling if f["item_id"] in qwen_by_item]
    for f in shared:
        f["qwen_risk"] = qwen_by_item[f["item_id"]]["risk_bf_q"]
        f["qwen_wrong"] = qwen_by_item[f["item_id"]]["consensus_wrong"]
        f["qwen_bf_reverse"] = qwen_by_item[f["item_id"]]["bf_reverse"]
        f["qwen_bf_paraphrase"] = qwen_by_item[f["item_id"]]["bf_paraphrase"]
    print("shared items:", len(shared))

    g_ling = gates_for("ling")
    # Qwen per-model stats on the SAME shared cohort (items of first 100 pairs)
    shared_qwen = [qwen_by_item[f["item_id"]] for f in ling]
    qwen_shared_hc = [f for f in shared_qwen if f["agreement"] >= al.HC_THRESHOLD]
    ling_shared_hc = [f for f in shared if f["agreement"] >= al.HC_THRESHOLD]
    qwen_shared_primary = al.group_bootstrap(qwen_shared_hc, "risk_bf_q", seed=20260913 + 60)
    ling_shared_primary = al.group_bootstrap(ling_shared_hc, "risk_bf_q", seed=20260913 + 61)
    qwen_shared_risk80 = al.risk_at_80_bootstrap(qwen_shared_hc, "risk_bf_q", seed=20260913 + 62)
    ling_shared_risk80 = al.risk_at_80_bootstrap(ling_shared_hc, "risk_bf_q", seed=20260913 + 63)

    # cross-model item-level correlation (secondary)
    both = [f for f in shared if f.get("risk_bf_q") is not None and f.get("qwen_risk") is not None]
    corr = {"spearman_rsq": al.spearman([f["qwen_risk"] for f in both], [f["risk_bf_q"] for f in both]),
            "n": len(both)} if len(both) > 2 else None

    # Qwen logistic transfer: fit on Qwen shared-cohort OOF, apply to Ling
    from sklearn.linear_model import LogisticRegression
    rng = random.Random(20260913 + 70)
    rows_q = [f for f in qwen_shared_hc if f["bf_paraphrase"] is not None and f["bf_reverse"] is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows_q:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    rng.shuffle(pairs)
    folds = [pairs[i::5] for i in range(5)]
    oof = {}
    for fi in range(5):
        tr = [p for j in range(5) if j != fi for p in folds[j]]
        Xtr = np.array([[f["bf_paraphrase"], f["bf_reverse"]] for p in tr for f in by_pair[p]])
        ytr = np.array([f["consensus_wrong"] for p in tr for f in by_pair[p]])
        clf = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
        for p in folds[fi]:
            for f in by_pair[p]:
                oof[f["cqid"]] = float(clf.predict_proba(np.array([[f["bf_paraphrase"], f["bf_reverse"]]]))[:, 1][0])
    for f in rows_q:
        f["logistic_oof"] = oof.get(f["cqid"])
    # fit on ALL Qwen shared data, apply to Ling
    Xall = np.array([[f["bf_paraphrase"], f["bf_reverse"]] for f in rows_q])
    yall = np.array([f["consensus_wrong"] for f in rows_q])
    clf_all = LogisticRegression(max_iter=2000).fit(Xall, yall)
    ling_rows = [f for f in ling_shared_hc if f.get("bf_paraphrase") is not None and f.get("bf_reverse") is not None]
    for f in ling_rows:
        f["ling_logistic_transfer"] = float(clf_all.predict_proba(
            np.array([[f["bf_paraphrase"], f["bf_reverse"]]]))[:, 1][0])
    transfer_auroc = al.group_bootstrap(ling_rows, "ling_logistic_transfer", seed=20260913 + 71)

    # mechanism profile: reverse faithfulness by correctness per model (shared HC)
    mech = {}
    for prefix, tag in (("", "qwen"), ("ling", "ling")):
        ff = qwen_shared_hc if prefix == "" else ling_shared_hc
        mech[tag] = {
            "bf_reverse_correct": round(float(np.mean([f["bf_reverse"] for f in ff if not f["consensus_wrong"] and f["bf_reverse"] is not None])), 4),
            "bf_reverse_wrong": round(float(np.mean([f["bf_reverse"] for f in ff if f["consensus_wrong"] and f["bf_reverse"] is not None])), 4),
            "bf_paraphrase_correct": round(float(np.mean([f["bf_paraphrase"] for f in ff if not f["consensus_wrong"] and f["bf_paraphrase"] is not None])), 4),
            "bf_paraphrase_wrong": round(float(np.mean([f["bf_paraphrase"] for f in ff if f["consensus_wrong"] and f["bf_paraphrase"] is not None])), 4),
            "n_correct": sum(1 for f in ff if not f["consensus_wrong"]),
            "n_wrong": sum(1 for f in ff if f["consensus_wrong"]),
        }

    result = {
        "protocol": pl.PROTOCOL_VERSION,
        "ling_within_model": g_ling,
        "per_model_shared": {
            "qwen": {"primary": qwen_shared_primary, "risk80": qwen_shared_risk80,
                     "n_hc": len(qwen_shared_hc), "n_wrong": sum(1 for f in qwen_shared_hc if f["consensus_wrong"])},
            "ling": {"primary": ling_shared_primary, "risk80": ling_shared_risk80,
                     "n_hc": len(ling_shared_hc), "n_wrong": sum(1 for f in ling_shared_hc if f["consensus_wrong"])},
        },
        "cross_model_item_corr": corr,
        "cross_model_transfer": {"ling_logistic_transfer_auroc": transfer_auroc},
        "mechanism_profile": mech,
    }
    (ANALYSIS_DIR / "ling_analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
