"""Round-3 paper-scale analysis: Gate 2 (E1-E7) + Phase 4 (P1-P6) on main cohort.

Labels merged ONLY here, after preoutcome_features.jsonl is frozen.
"""
from __future__ import annotations
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analysis_lib as al

ROOT = Path(__file__).resolve().parent
ANALYSIS_DIR = ROOT / "analysis"
FIGURES_DIR = ROOT / "figures"

SCORES = [
    "bf_q", "bf_paraphrase", "bf_reverse", "bf_synthetic_reverse",
    "R_PI", "R_sym", "mean_confidence", "agreement", "conf_dispersion",
    "D_inert", "flip_inertia", "frac_shared", "rev_flip_rate", "rem_flip_rate",
]
RISK_KEY = "risk_bf_q"


def load_merged() -> list[dict]:
    feats = [json.loads(l) for l in (ROOT / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
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


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    feats = load_merged()
    hc = [f for f in feats if f["agreement"] >= al.HC_THRESHOLD]
    wrong = [f for f in hc if f["consensus_wrong"]]
    print(f"total={len(feats)} hc={len(hc)} wrong_hc={len(wrong)} rate={len(wrong)/max(1,len(hc)):.4f}")
    print("hc_by_label:", dict(Counter(f['gold_label'] for f in hc)))
    print("wrong_hc_by_label:", dict(Counter(f['gold_label'] for f in wrong)))

    # --- Gate 2 (paper scale) ---
    recs = [json.loads(l) for l in (ROOT / "records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    e1_agent = {}
    for cond in ("paraphrase", "reverse", "synthetic_reverse"):
        n = ok = 0
        orig = {(r["cqid"], r["agent_index"]): r["decision"]["answer"]
                for r in recs if r["condition"] == "original" and r["decision"]}
        for r in recs:
            if r["condition"] != cond or not r.get("decision"):
                continue
            y0 = orig.get((r["cqid"], r["agent_index"]))
            if y0 is None:
                continue
            exp = y0 if cond == "paraphrase" else ("no" if y0 == "yes" else "yes")
            n += 1
            ok += int(r["decision"]["answer"] == exp)
        e1_agent[cond] = {"n": n, "accuracy": round(ok / n, 4) if n else None}

    primary = al.group_bootstrap(hc, RISK_KEY)
    per_label = {k: al.label_subgroup_bootstrap(hc, RISK_KEY, k) for k in ("SUPPORTS", "REFUTES")}
    macro = al.macro_ci(hc, RISK_KEY)
    worst_point = min(per_label["SUPPORTS"]["auroc"], per_label["REFUTES"]["auroc"])
    worst_label = "SUPPORTS" if per_label["SUPPORTS"]["auroc"] <= per_label["REFUTES"]["auroc"] else "REFUTES"
    worst_ci = per_label[worst_label]["ci"]

    s1 = {k: al.group_bootstrap(hc, k) for k in SCORES}
    s2 = {k: al.paired_bootstrap_diff(hc, RISK_KEY, k)
          for k in ["R_PI", "R_sym", "mean_confidence", "disagreement", "agreement"]}

    para_agent_flip = sum(1 for f in feats for i in range(5)
                          if f["_agent_bf"][str(i)]["paraphrase"] == 0) / (5 * len(feats))
    c1 = {"agent_paraphrase_flip_rate": round(para_agent_flip, 4),
          "violation": para_agent_flip > 0.30}
    c2 = al.permutation_risk(hc)
    red = {
        "spearman_risk_agreement": round(al.spearman([f[RISK_KEY] for f in hc], [f["agreement"] for f in hc]), 4),
        "spearman_risk_conf": round(al.spearman([f[RISK_KEY] for f in hc], [f["mean_confidence"] for f in hc]), 4),
    }
    hc13 = [f for f in hc if abs(f["agreement"] - 0.8) < 1e-9]
    red["auroc_at_agr_0.8"] = {"n": len(hc13),
                               "auroc": al.auROC([f[RISK_KEY] for f in hc13], [f["consensus_wrong"] for f in hc13])}

    gates = {
        "g1_pipeline_ge_0.95": len(recs) > 0 and sum(1 for r in recs if r["success"]) / len(recs) >= 0.95,
        "g2_primary_ci_lb_gt_0.5": bool(primary and primary["ci"][0] > 0.5),
        "g2_primary_point_ge_0.60": bool(primary and primary["auroc"] >= 0.60),
        "g3_macro_ci_lb_gt_0.5": bool(macro and macro["ci"][0] > 0.5),
        "g4_worst_ci_lb_gt_0.5": worst_ci[0] > 0.5,
        "g5_placebo_clean": not c1["violation"],
        "g6_perm_pass": bool(c2 and c2["obs_auroc"] > c2["perm_95pct"]),
        "g7_reducibility": bool(red["spearman_risk_agreement"] is not None
                                and red["spearman_risk_agreement"] < 0.9
                                and red["spearman_risk_conf"] < 0.9
                                and (red["auroc_at_agr_0.8"]["auroc"] or 0) > 0.5),
    }
    gates["gate2_paper_pass"] = all(gates[k] for k in [
        "g1_pipeline_ge_0.95", "g2_primary_ci_lb_gt_0.5", "g2_primary_point_ge_0.60",
        "g3_macro_ci_lb_gt_0.5", "g4_worst_ci_lb_gt_0.5", "g5_placebo_clean",
        "g6_perm_pass", "g7_reducibility"])

    # --- Phase 4: Risk@80 + paired diffs + logistic/isotonic ---
    risk80 = {k: al.risk_at_80_bootstrap(hc, k) for k in [RISK_KEY, "R_sym", "R_PI",
                                                          "mean_confidence", "disagreement", "agreement"]}
    risk80_diff = {
        "vs_R_sym": al.risk_at_80_paired_diff(hc, RISK_KEY, "R_sym"),
        "vs_R_PI": al.risk_at_80_paired_diff(hc, RISK_KEY, "R_PI"),
        "vs_confidence": al.risk_at_80_paired_diff(hc, RISK_KEY, "mean_confidence"),
        "vs_disagreement": al.risk_at_80_paired_diff(hc, RISK_KEY, "disagreement"),
    }

    # logistic 5-fold pair-grouped OOF on {bf_paraphrase, bf_reverse}
    from sklearn.linear_model import LogisticRegression
    from sklearn.isotonic import IsotonicRegression
    rng = random.Random(20260913 + 10)
    rows = [f for f in hc if f["bf_paraphrase"] is not None and f["bf_reverse"] is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    rng.shuffle(pairs)
    folds = [pairs[i::5] for i in range(5)]
    oof = {}
    for fi in range(5):
        tr = [p for j in range(5) if j != fi for p in folds[j]]
        te = folds[fi]
        Xtr = np.array([[f["bf_paraphrase"], f["bf_reverse"]] for p in tr for f in by_pair[p]])
        ytr = np.array([f["consensus_wrong"] for p in tr for f in by_pair[p]])
        clf = LogisticRegression(max_iter=2000)
        clf.fit(Xtr, ytr)
        for p in te:
            for f in by_pair[p]:
                oof[f["cqid"]] = float(clf.predict_proba(np.array([[f["bf_paraphrase"], f["bf_reverse"]]]))[:, 1][0])
    for f in rows:
        f["logistic_oof"] = oof.get(f["cqid"])
    log_auroc = al.group_bootstrap(rows, "logistic_oof", seed=20260913 + 14)
    log_diff = al.paired_bootstrap_diff(rows, RISK_KEY, "logistic_oof", seed=20260913 + 15)
    log_risk80 = al.risk_at_80_bootstrap(rows, "logistic_oof", seed=20260913 + 16)

    # isotonic calibration of RS_q on OOF split
    rng2 = random.Random(20260913 + 17)
    pairs2 = sorted(by_pair)
    rng2.shuffle(pairs2)
    cut = max(1, int(0.5 * len(pairs2)))
    tr_pairs, te_pairs = set(pairs2[:cut]), pairs2[cut:]
    Xtr = np.array([f[RISK_KEY] for p in tr_pairs for f in by_pair[p]])
    ytr = np.array([f["consensus_wrong"] for p in tr_pairs for f in by_pair[p]])
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(Xtr, ytr)
    te_rows = [f for p in te_pairs for f in by_pair[p]]
    cal = iso.predict(np.array([f[RISK_KEY] for f in te_rows]))
    raw_min, raw_max = Xtr.min(), Xtr.max()
    raw_norm = [(f[RISK_KEY] - raw_min) / max(1e-9, raw_max - raw_min) for f in te_rows]
    ece_raw = al.ece([f["consensus_wrong"] for f in te_rows], raw_norm) if hasattr(al, "ece") else None
    ece_cal = al.ece([f["consensus_wrong"] for f in te_rows], cal) if hasattr(al, "ece") else None
    # fallback ece implementation
    if ece_raw is None:
        ece_raw = ece_impl([f["consensus_wrong"] for f in te_rows], raw_norm)
        ece_cal = ece_impl([f["consensus_wrong"] for f in te_rows], cal)

    result = {
        "protocol": "cs-paper-vitaminc-2026-09-13",
        "population": {"total_items": len(feats), "high_consensus": len(hc),
                       "wrong_hc": len(wrong), "wrong_rate": round(len(wrong) / max(1, len(hc)), 4),
                       "hc_by_label": dict(Counter(f["gold_label"] for f in hc)),
                       "wrong_hc_by_label": dict(Counter(f["gold_label"] for f in wrong)),
                       "stage1_hc": len([f for f in hc if f["stage"] == 1]),
                       "stage2_hc": len([f for f in hc if f["stage"] == 2])},
        "e1_agent_faithfulness": e1_agent,
        "primary_risk_bf_q": primary,
        "per_label_risk_bf_q": per_label,
        "macro": macro,
        "worst_label": worst_label,
        "worst_ci": worst_ci,
        "s1_auroc": {k: v for k, v in s1.items()},
        "s2_paired_diff_vs_risk": s2,
        "c1_placebo": c1,
        "c2_permutation": c2,
        "reducibility": red,
        "gates": gates,
        "phase4_risk80": risk80,
        "phase4_risk80_diff": risk80_diff,
        "phase4_logistic": {"auroc": log_auroc, "paired_diff_vs_risk": log_diff, "risk80": log_risk80},
        "phase4_isotonic": {"ece_raw": ece_raw, "ece_cal": ece_cal},
    }
    (ANALYSIS_DIR / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("s1_auroc",)}, indent=2, ensure_ascii=False))


def ece_impl(y_true, y_prob, bins=10):
    y_true = np.asarray(y_true, float); y_prob = np.asarray(y_prob, float)
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0; n = 0
    for i in range(bins):
        m = (y_prob >= edges[i]) & (y_prob < edges[i + 1]) if i < bins - 1 else (y_prob >= edges[i]) & (y_prob <= edges[i + 1])
        if m.sum() == 0:
            continue
        total += m.sum() * abs(y_prob[m].mean() - y_true[m].mean()); n += m.sum()
    return total / n if n else None


if __name__ == "__main__":
    main()
