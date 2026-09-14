"""Confirmation cohort analysis under the corrected direction-consistent gate."""
from __future__ import annotations
import json
import random
import sys
from collections import Counter
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round2_lib as pl
from analyze import (auROC, pair_grouped_bootstrap, label_subgroup_bootstrap,
                     paired_bootstrap_diff, spearman, HC_THRESHOLD, BOOTSTRAP_N,
                     BOOTSTRAP_SEED, PERM_N)

ROOT = Path(__file__).resolve().parent
PREFIX = "confirmation"
ANALYSIS_DIR = ROOT.parent / "analysis"
SCORES = ["bf_q", "bf_paraphrase", "bf_reverse", "bf_synthetic_reverse", "R_PI", "R_sym",
          "mean_confidence", "agreement", "conf_dispersion", "D_inert", "flip_inertia",
          "frac_shared", "rev_flip_rate", "rem_flip_rate"]


def load_merged() -> list[dict]:
    feats = [json.loads(l) for l in (ROOT / f"{PREFIX}_preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((ROOT / f"{PREFIX}_labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        g = gold[f["item_id"]]
        f["gold_label"] = g
        f["gold_yes"] = g == "SUPPORTS"
        f["consensus_wrong"] = int((f["consensus"] == "yes") != f["gold_yes"])
        f["risk_bf_q"] = -f["bf_q"] if f.get("bf_q") is not None else None
    return feats


def compute_macro_ci(feats, key, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 7):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key) is not None]
    by_pair = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        a_s = auROC([f[key] for f in sample if f["gold_label"] == "SUPPORTS"],
                    [f["consensus_wrong"] for f in sample if f["gold_label"] == "SUPPORTS"])
        a_r = auROC([f[key] for f in sample if f["gold_label"] == "REFUTES"],
                    [f["consensus_wrong"] for f in sample if f["gold_label"] == "REFUTES"])
        if a_s is not None and a_r is not None:
            vals.append(0.5 * (a_s + a_r))
    vals = sorted(vals)
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]


def permutation_risk(feats, n=PERM_N, seed=BOOTSTRAP_SEED + 8):
    rng = random.Random(seed)
    rows = [f for f in feats if f["bf_paraphrase"] is not None and f["bf_reverse"] is not None]
    labels = [f["consensus_wrong"] for f in rows]
    obs = auROC([-f["bf_q"] for f in rows], labels)
    perms = []
    for _ in range(n):
        pseudo = []
        for f in rows:
            if rng.random() < 0.5:
                pseudo.append(-(0.5 * f["bf_paraphrase"] + 0.5 * (1.0 - f["bf_reverse"])))
            else:
                pseudo.append(-(0.5 * (1.0 - f["bf_paraphrase"]) + 0.5 * f["bf_reverse"]))
        a = auROC(pseudo, labels)
        if a is not None:
            perms.append(a)
    perms = sorted(perms)
    return {"obs_auroc": obs, "perm_mean": float(np.mean(perms)),
            "perm_95pct": perms[int(0.95 * len(perms))], "n": len(rows)}


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    feats = load_merged()
    hc = [f for f in feats if f["agreement"] >= HC_THRESHOLD]
    wrong = [f for f in hc if f["consensus_wrong"]]
    print(f"total={len(feats)} hc={len(hc)} wrong_hc={len(wrong)} rate={len(wrong)/max(1,len(hc)):.3f}")

    recs = [json.loads(l) for l in (ROOT / f"{PREFIX}_records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    e1 = {}
    for cond in pl.SCORED_ALL:
        n = ok = 0
        for r in recs:
            if r["condition"] != cond or not r.get("decision"):
                continue
            y0 = None
            for r0 in recs:
                if r0["cqid"] == r["cqid"] and r0["agent_index"] == r["agent_index"] and r0["condition"] == "original":
                    y0 = r0["decision"]["answer"]; break
            if y0 is None: continue
            exp = y0 if cond == "paraphrase" else ("no" if y0 == "yes" else "yes")
            n += 1; ok += int(r["decision"]["answer"] == exp)
        e1[cond] = {"n": n, "accuracy": round(ok / n, 4) if n else None}

    primary = pair_grouped_bootstrap(hc, "risk_bf_q")
    per_label = {k: label_subgroup_bootstrap(hc, "risk_bf_q", k) for k in ("SUPPORTS", "REFUTES")}
    macro_ci = compute_macro_ci(hc, "risk_bf_q")
    worst_point = min(per_label["SUPPORTS"]["auroc"], per_label["REFUTES"]["auroc"])
    worst_label = "SUPPORTS" if per_label["SUPPORTS"]["auroc"] <= per_label["REFUTES"]["auroc"] else "REFUTES"

    s1 = {k: pair_grouped_bootstrap(hc, k) for k in SCORES}
    s2 = {k: paired_bootstrap_diff(hc, "risk_bf_q", k) for k in ["R_PI", "R_sym", "mean_confidence", "agreement"]}

    para_agent_flip = sum(1 for f in feats for i in range(5)
                          if f["_agent_bf"][str(i)]["paraphrase"] == 0) / (5 * len(feats))
    c1 = {"agent_paraphrase_flip_rate": round(para_agent_flip, 4),
          "violation": para_agent_flip > 0.30}
    c2 = permutation_risk(hc)
    red = {
        "spearman_risk_agreement": round(spearman([f["risk_bf_q"] for f in hc], [f["agreement"] for f in hc]), 4),
        "spearman_risk_conf": round(spearman([f["risk_bf_q"] for f in hc], [f["mean_confidence"] for f in hc]), 4),
    }
    hc13 = [f for f in hc if abs(f["agreement"] - 0.8) < 1e-9]
    red["auroc_at_agr_0.8"] = {"n": len(hc13), "auroc": auROC([f["risk_bf_q"] for f in hc13], [f["consensus_wrong"] for f in hc13])}

    gates = {
        "g1_pipeline_ge_0.95": len(recs) > 0 and sum(1 for r in recs if r["success"]) / len(recs) >= 0.95,
        "g2_primary_ci_lb_gt_0.5": bool(primary and primary["ci"][0] > 0.5),
        "g2_primary_point_ge_0.60": bool(primary and primary["auroc"] >= 0.60),
        "g3_macro_ci_lb_gt_0.5": bool(macro_ci and macro_ci[0] > 0.5),
        "g4_worst_point_gt_0.5": worst_point > 0.5,
        "g5_placebo_clean": not c1["violation"],
        "g6_perm_pass": bool(c2 and c2["obs_auroc"] > c2["perm_95pct"]),
        "g7_reducibility": bool(red["spearman_risk_agreement"] is not None
                                and red["spearman_risk_agreement"] < 0.9
                                and red["spearman_risk_conf"] < 0.9
                                and (red["auroc_at_agr_0.8"]["auroc"] or 0) > 0.5),
    }
    gates["gate2_confirmation_pass"] = all(gates[k] for k in [
        "g1_pipeline_ge_0.95", "g2_primary_ci_lb_gt_0.5", "g2_primary_point_ge_0.60",
        "g3_macro_ci_lb_gt_0.5", "g4_worst_point_gt_0.5", "g5_placebo_clean",
        "g6_perm_pass", "g7_reducibility"])

    result = {
        "protocol": "cs-pilot-vitaminc-conf-2026-09-13",
        "population": {"total_items": len(feats), "high_consensus": len(hc),
                       "wrong_hc": len(wrong), "wrong_rate": round(len(wrong)/max(1, len(hc)), 4),
                       "hc_by_label": dict(Counter(f["gold_label"] for f in hc)),
                       "wrong_hc_by_label": dict(Counter(f["gold_label"] for f in wrong))},
        "e1": e1,
        "primary_risk_bf_q": primary,
        "per_label_risk_bf_q": per_label,
        "macro_ci": macro_ci,
        "worst_label": worst_label,
        "s1": s1, "s2": s2, "c1": c1, "c2": c2, "reducibility": red, "gates": gates,
    }
    (ANALYSIS_DIR / "confirmation_analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "s1"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
