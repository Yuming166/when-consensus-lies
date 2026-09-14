"""Balanced BoolQ cross-dataset analysis: same 7 gates (worst-label point-level + CI), Risk@80,
paired diffs vs R_PI/R_sym/confidence/disagreement. Honest replication-attempt framing."""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analysis_lib as al
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
ANALYSIS_DIR = ROOT / "analysis"


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    feats = [json.loads(l) for l in (ROOT / "boolq_preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((ROOT / "boolq_labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["cqid"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        g = gold[f["cqid"]]
        f["gold_label"] = g
        f["consensus_wrong"] = int((f["consensus"] == "yes") != (g == "yes"))
        f["risk_bf_q"] = -f["bf_q"] if f.get("bf_q") is not None else None
        f["disagreement"] = 1.0 - f["agreement"]
    hc = [f for f in feats if f["agreement"] >= al.HC_THRESHOLD]
    recs = [json.loads(l) for l in (ROOT / "boolq_records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    print(f"boolq total={len(feats)} hc={len(hc)} wrong_hc={sum(1 for f in hc if f['consensus_wrong'])}")
    print("hc_by_label:", dict(Counter(f["gold_label"] for f in hc)))
    print("wrong_by_label:", dict(Counter(f["gold_label"] for f in hc if f["consensus_wrong"])))

    primary = al.group_bootstrap(hc, "risk_bf_q", seed=20260913 + 100)
    per_label = {k: al.label_subgroup_bootstrap(hc, "risk_bf_q", k, seed=20260913 + 101)
                 for k in ("yes", "no")}
    macro = al.macro_ci(hc, "risk_bf_q", seed=20260913 + 102)
    worst_point = min(per_label["yes"]["auroc"], per_label["no"]["auroc"])
    worst_label = "yes" if per_label["yes"]["auroc"] <= per_label["no"]["auroc"] else "no"
    worst_ci = per_label[worst_label]["ci"]
    s2 = {k: al.paired_bootstrap_diff(hc, "risk_bf_q", k, seed=20260913 + 103)
          for k in ["R_PI", "R_sym", "mean_confidence", "disagreement"]}
    risk80 = {k: al.risk_at_80_bootstrap(hc, k, seed=20260913 + 104)
              for k in ["risk_bf_q", "R_sym", "R_PI", "mean_confidence", "disagreement"]}
    orig = {(r["cqid"], r["agent_index"]): r["decision"]["answer"]
            for r in recs if r["condition"] == "original" and r["decision"]}
    para_agent_flip = sum(
        1 for r in recs if r["condition"] == "paraphrase" and r.get("decision")
        and orig.get((r["cqid"], r["agent_index"])) is not None
        and r["decision"]["answer"] != orig[(r["cqid"], r["agent_index"])]
    ) / (5 * len(feats))
    c2 = al.permutation_risk(hc, seed=20260913 + 105)
    red = {"spearman_risk_agreement": al.spearman([f["risk_bf_q"] for f in hc], [f["agreement"] for f in hc]),
           "spearman_risk_conf": al.spearman([f["risk_bf_q"] for f in hc], [f["mean_confidence"] for f in hc])}
    gates = {
        "g1_pipeline_ge_0.95": len(recs) > 0 and sum(1 for r in recs if r["success"]) / len(recs) >= 0.95,
        "g2_primary_ci_lb_gt_0.5": bool(primary and primary["ci"][0] > 0.5),
        "g2_primary_point_ge_0.60": bool(primary and primary["auroc"] >= 0.60),
        "g3_macro_ci_lb_gt_0.5": bool(macro and macro["ci"][0] > 0.5),
        "g4_worst_point_gt_0.5": worst_point > 0.5,
        "g5_placebo_clean": para_agent_flip <= 0.30,
        "g6_perm_pass": bool(c2 and c2["obs_auroc"] > c2["perm_95pct"]),
        "g7_reducibility": bool(red["spearman_risk_agreement"] is not None and red["spearman_risk_agreement"] < 0.9
                                and red["spearman_risk_conf"] < 0.9),
    }
    gates["pass"] = all(gates[k] for k in ["g1_pipeline_ge_0.95", "g2_primary_ci_lb_gt_0.5",
                                            "g2_primary_point_ge_0.60", "g3_macro_ci_lb_gt_0.5",
                                            "g4_worst_point_gt_0.5", "g5_placebo_clean",
                                            "g6_perm_pass", "g7_reducibility"])
    result = {"protocol": "cs-paper-boolq-20260913",
              "reverse_definition": "negation prefix (BoolQ lacks natural counter-evidence)",
              "population": {"total": len(feats), "hc": len(hc),
                             "wrong_hc": sum(1 for f in hc if f["consensus_wrong"]),
                             "hc_by_label": dict(Counter(f["gold_label"] for f in hc)),
                             "wrong_by_label": dict(Counter(f["gold_label"] for f in hc if f["consensus_wrong"]))},
              "primary": primary, "per_label": per_label, "macro": macro,
              "worst_label": worst_label, "worst_ci": worst_ci,
              "paired_diff_vs_risk": s2, "risk80": risk80,
              "para_agent_flip": round(para_agent_flip, 4), "c2": c2, "reducibility": red,
              "gates": gates}
    (ANALYSIS_DIR / "boolq_analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
