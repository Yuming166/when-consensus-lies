"""Round-2 CS pilot analysis (label merge AFTER preoutcome features frozen)."""
from __future__ import annotations
import json
import random
import statistics
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
ANALYSIS_DIR = ROOT.parent / "analysis"
FIGURES_DIR = ROOT.parent / "figures"
HC_THRESHOLD = 0.8
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 20260913
PERM_N = 1000

SCORES = [
    "bf_q", "bf_paraphrase", "bf_reverse", "bf_synthetic_reverse",
    "R_PI", "R_sym", "mean_confidence", "agreement", "conf_dispersion",
    "D_inert", "flip_inertia", "frac_shared", "rev_flip_rate", "rem_flip_rate",
]


def load_merged() -> list[dict]:
    feats = [json.loads(l) for l in (ROOT / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((ROOT / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        g = gold[f["item_id"]]
        f["gold_label"] = g
        f["gold_yes"] = g == "SUPPORTS"
        f["consensus_wrong"] = int((f["consensus"] == "yes") != f["gold_yes"])
    return feats


def auROC(scores, labels):
    pos = sum(1 for l in labels if l == 1)
    neg = sum(1 for l in labels if l == 0)
    if pos == 0 or neg == 0:
        return None
    return float(roc_auc(labels, scores))


def roc_auc(labels, scores):
    # simple rank-based AUROC without sklearn dependency risk
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    pos = sum(1 for _, l in pairs if l == 1)
    neg = len(pairs) - pos
    if pos == 0 or neg == 0:
        return None
    rank_sum = 0.0
    i = 0
    n = len(pairs)
    while i < n:
        j = i
        while j < n and pairs[j][0] == pairs[i][0]:
            j += 1
        # average rank for ties
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            if pairs[k][1] == 1:
                rank_sum += avg
        i = j
    return (rank_sum - pos * (pos + 1) / 2.0) / (pos * neg)


def pair_grouped_bootstrap(feats, score_key, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    obs = auROC([f[score_key] for f in rows], [f["consensus_wrong"] for f in rows])
    if obs is None:
        return None
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            pid = rng.choice(pairs)
            sample.extend(by_pair[pid])
        a = auROC([f[score_key] for f in sample], [f["consensus_wrong"] for f in sample])
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    return {"auroc": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_pairs": len(pairs)}


def label_subgroup_bootstrap(feats, score_key, label, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None and f["gold_label"] == label]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    obs = auROC([f[score_key] for f in rows], [f["consensus_wrong"] for f in rows])
    if obs is None:
        return None
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            pid = rng.choice(pairs)
            sample.extend(by_pair[pid])
        # keep only this label's items (pair may contribute both items in resample)
        sample = [f for f in sample if f["gold_label"] == label]
        a = auROC([f[score_key] for f in sample], [f["consensus_wrong"] for f in sample])
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    return {"auroc": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_pairs": len(pairs)}


def macro_worst(feats, score_key):
    res = {}
    res["SUPPORTS"] = label_subgroup_bootstrap(feats, score_key, "SUPPORTS")
    res["REFUTES"] = label_subgroup_bootstrap(feats, score_key, "REFUTES")
    if res["SUPPORTS"] and res["REFUTES"]:
        # macro from the same resamples would need paired resampling; use point macro + per-label CIs
        macro_point = (res["SUPPORTS"]["auroc"] + res["REFUTES"]["auroc"]) / 2.0
        worst_point = min(res["SUPPORTS"]["auroc"], res["REFUTES"]["auroc"])
        res["macro_point"] = macro_point
        res["worst_point"] = worst_point
        res["worst_label"] = ("SUPPORTS" if res["SUPPORTS"]["auroc"] <= res["REFUTES"]["auroc"] else "REFUTES")
    return res


def paired_bootstrap_diff(feats, key_a, key_b, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 1):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key_a) is not None and f.get(key_b) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    labels_all = [f["consensus_wrong"] for f in rows]
    obs = auROC([f[key_a] for f in rows], labels_all) - auROC([f[key_b] for f in rows], labels_all)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            pid = rng.choice(pairs)
            sample.extend(by_pair[pid])
        a = auROC([f[key_a] for f in sample], [f["consensus_wrong"] for f in sample])
        b = auROC([f[key_b] for f in sample], [f["consensus_wrong"] for f in sample])
        if a is not None and b is not None:
            vals.append(a - b)
    vals = sorted(vals)
    return {"diff": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]], "n": len(rows)}


def permutation_control(feats, n=PERM_N, seed=BOOTSTRAP_SEED + 2):
    rng = random.Random(seed)
    rows = [f for f in feats if f["bf_paraphrase"] is not None and f["bf_reverse"] is not None]
    labels = [f["consensus_wrong"] for f in rows]
    obs = auROC([f["bf_q"] for f in rows], labels)
    perms = []
    for _ in range(n):
        pseudo = []
        for f in rows:
            if rng.random() < 0.5:
                pseudo.append(0.5 * f["bf_paraphrase"] + 0.5 * (1.0 - f["bf_reverse"]))
            else:
                pseudo.append(0.5 * (1.0 - f["bf_paraphrase"]) + 0.5 * f["bf_reverse"])
        a = auROC(pseudo, labels)
        if a is not None:
            perms.append(a)
    perms = sorted(perms)
    return {"obs_auroc": obs, "perm_mean": float(np.mean(perms)),
            "perm_95pct": perms[int(0.95 * len(perms))],
            "perm_ci": [perms[int(0.025 * len(perms))], perms[int(0.975 * len(perms)) - 1]],
            "n": len(rows)}


def agent_randomization_control(feats, n=PERM_N, seed=BOOTSTRAP_SEED + 3):
    rng = random.Random(seed)
    rows = [f for f in feats if f["bf_q"] is not None]
    labels = [f["consensus_wrong"] for f in rows]
    obs = auROC([f["bf_q"] for f in rows], labels)
    perms = []
    for _ in range(n):
        pseudo = []
        for f in rows:
            bp = [f["_agent_bf"][str(i)]["paraphrase"] for i in range(5)]
            br = [f["_agent_bf"][str(i)]["reverse"] for i in range(5)]
            rng.shuffle(bp)
            rng.shuffle(br)
            pseudo.append(0.5 * np.nanmean([x for x in bp if x is not None]) +
                          0.5 * np.nanmean([x for x in br if x is not None]))
        a = auROC(pseudo, labels)
        if a is not None:
            perms.append(a)
    perms = sorted(perms)
    return {"obs_auroc": obs, "perm_mean": float(np.mean(perms)),
            "perm_95pct": perms[int(0.95 * len(perms))], "n": len(rows)}


def spearman(xs, ys):
    rx = rankdata(xs)
    ry = rankdata(ys)
    n = len(rx)
    if n < 2:
        return None
    mx, my = np.mean(rx), np.mean(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        return None
    return cov / (vx * vy) ** 0.5


def rankdata(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j < len(order) and xs[order[j]] == xs[order[i]]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg
        i = j
    return ranks


def mean_ci(values):
    vals = sorted(values)
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]


def bootstrap_mean_diff(feats, key, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 4):
    rng = random.Random(seed)
    wrong = [f for f in feats if f["consensus_wrong"] == 1 and f.get(key) is not None]
    correct = [f for f in feats if f["consensus_wrong"] == 0 and f.get(key) is not None]
    if not wrong or not correct:
        return None
    obs = np.mean([f[key] for f in wrong]) - np.mean([f[key] for f in correct])
    vals = []
    for _ in range(n):
        w = np.mean([rng.choice([f[key] for f in wrong]) for _ in range(len(wrong))])
        c = np.mean([rng.choice([f[key] for f in correct]) for _ in range(len(correct))])
        vals.append(w - c)
    return {"diff": obs, "ci": mean_ci(vals), "n_wrong": len(wrong), "n_correct": len(correct)}


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    feats = load_merged()
    hc = [f for f in feats if f["agreement"] >= HC_THRESHOLD]
    wrong = [f for f in hc if f["consensus_wrong"]]
    print(f"total={len(feats)} high_consensus={len(hc)} wrong_hc={len(wrong)} rate={len(wrong)/max(1,len(hc)):.3f}")

    # E1 agent-level expected-response accuracy per scored condition (all items)
    recs = [json.loads(l) for l in (ROOT / "records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    e1 = {}
    for cond in pl.SCORED_ALL:
        n = 0
        ok = 0
        for r in recs:
            if r["condition"] != cond or not r.get("decision"):
                continue
            y0 = None
            for r0 in recs:
                if r0["cqid"] == r["cqid"] and r0["agent_index"] == r["agent_index"] and r0["condition"] == "original":
                    y0 = r0["decision"]["answer"]
                    break
            if y0 is None:
                continue
            exp = y0 if cond == "paraphrase" else ("no" if y0 == "yes" else "yes")
            n += 1
            ok += int(r["decision"]["answer"] == exp)
        e1[cond] = {"n": n, "accuracy": round(ok / n, 4) if n else None}

    # E2 consensus-level descriptive
    e2 = {
        "bf_q_wrong": round(float(np.mean([f["bf_q"] for f in wrong if f["bf_q"] is not None])), 4) if wrong else None,
        "bf_q_correct": round(float(np.mean([f["bf_q"] for f in hc if not f["consensus_wrong"] and f["bf_q"] is not None])), 4),
        "bf_q_all": round(float(np.mean([f["bf_q"] for f in hc if f["bf_q"] is not None])), 4),
    }

    # E3 primary
    e3 = pair_grouped_bootstrap(hc, "bf_q")
    # E4 macro/worst
    e4 = macro_worst(hc, "bf_q")

    # S1 all score AUROCs
    s1 = {}
    for key in SCORES:
        s1[key] = pair_grouped_bootstrap(hc, key)

    # S2 paired diffs vs BF_q
    s2 = {}
    for key in ["R_PI", "R_sym", "mean_confidence", "agreement"]:
        s2[key] = paired_bootstrap_diff(hc, "bf_q", key)

    # S3 stage consistency
    s3 = {}
    for st in (1, 2):
        sub = [f for f in hc if f["stage"] == st]
        s3[f"stage{st}"] = pair_grouped_bootstrap(sub, "bf_q")

    # S4 mean diff
    s4 = bootstrap_mean_diff(hc, "bf_q")

    # S5 descriptive flip rates (consensus-level)
    s5 = {}
    for key in ["para_flip_rate", "rev_flip_rate", "synth_flip_rate", "rem_flip_rate"]:
        vals = [f[key] for f in hc if f.get(key) is not None]
        s5[key] = round(float(np.mean(vals)), 4) if vals else None

    # C1 placebo
    para_agent_flip = sum(1 for f in feats for i in range(5)
                          if f["_agent_bf"][str(i)]["paraphrase"] == 0) / (
        5 * len(feats)) if feats else None
    cons_flip = sum(1 for f in hc if f["para_flip_rate"] > 0.5) / len(hc) if hc else None
    c1 = {"agent_paraphrase_flip_rate": round(para_agent_flip, 4),
          "consensus_paraphrase_flip_rate": round(cons_flip, 4) if cons_flip is not None else None,
          "violation": para_agent_flip is not None and para_agent_flip > 0.30}

    # C2 permutation
    c2 = permutation_control(hc)

    # C3 agent randomization
    c3 = agent_randomization_control(hc)

    # Reducibility
    hc13 = [f for f in hc if abs(f["agreement"] - 0.8) < 1e-9]
    red = {
        "spearman_bf_agreement": round(spearman([f["bf_q"] for f in hc], [f["agreement"] for f in hc]), 4),
        "spearman_bf_conf": round(spearman([f["bf_q"] for f in hc], [f["mean_confidence"] for f in hc]), 4),
        "auroc_bf_at_agreement_0.8": pair_grouped_bootstrap(hc13, "bf_q"),
    }

    gates = {
        "pipeline_valid_rate": round(sum(1 for r in recs if r["success"]) / len(recs), 4) if recs else 0,
        "g1_pipeline_ge_0.95": bool(recs) and sum(1 for r in recs if r["success"]) / len(recs) >= 0.95,
        "g2_e3_ci_lb_gt_0.5": bool(e3 and e3["ci"][0] > 0.5),
        "g2_e3_point_ge_0.60": bool(e3 and e3["auroc"] >= 0.60),
        "g2_e3_direction_consistent": bool(e3 and e3["auroc"] > 0.5),
        "g3_macro_ci_lb_gt_0.5": False,  # computed below
        "g4_worst_point_gt_0.5": False,
        "g5_c1_placebo_clean": bool(c1 and not c1["violation"]),
        "g6_c2_perm_pass": bool(c2 and c2["obs_auroc"] > c2["perm_95pct"]),
        "g7_reducibility": None,
    }

    # macro CI via paired label resamples: recompute macro distribution
    macro_ci = compute_macro_ci(hc, "bf_q")
    gates["g3_macro_ci_lb_gt_0.5"] = bool(macro_ci and macro_ci[0] > 0.5)
    gates["g4_worst_point_gt_0.5"] = bool(e4 and e4["worst_point"] > 0.5)
    red13 = red["auroc_bf_at_agreement_0.8"]
    gates["g7_reducibility"] = bool(
        red["spearman_bf_agreement"] is not None and red["spearman_bf_agreement"] < 0.9
        and red["spearman_bf_conf"] is not None and red["spearman_bf_conf"] < 0.9
        and red13 and red13["ci"][0] > 0.5)
    gates["gate2_pass"] = all(gates[k] for k in
                              ["g1_pipeline_ge_0.95", "g2_e3_ci_lb_gt_0.5", "g2_e3_point_ge_0.60",
                               "g2_e3_direction_consistent", "g3_macro_ci_lb_gt_0.5",
                               "g4_worst_point_gt_0.5", "g5_c1_placebo_clean", "g6_c2_perm_pass",
                               "g7_reducibility"])

    # direction-consistent orientation: risk score = -BF_q (higher = riskier)
    for f in feats:
        f["risk_bf_q"] = -f["bf_q"] if f.get("bf_q") is not None else None
    for f in hc:
        f["risk_bf_q"] = -f["bf_q"] if f.get("bf_q") is not None else None
    risk = {
        "auroc_minus_bf_q": pair_grouped_bootstrap(hc, "risk_bf_q"),
        "macro_ci_minus_bf_q": compute_macro_ci(hc, "risk_bf_q"),
        "per_label_minus_bf_q": {
            "SUPPORTS": label_subgroup_bootstrap(hc, "risk_bf_q", "SUPPORTS"),
            "REFUTES": label_subgroup_bootstrap(hc, "risk_bf_q", "REFUTES"),
        },
        "paired_diff_vs": {k: paired_bootstrap_diff(hc, "risk_bf_q", k)
                           for k in ["R_PI", "R_sym", "mean_confidence", "agreement"]},
        "stage_consistency": {f"stage{st}": pair_grouped_bootstrap(
            [f for f in hc if f["stage"] == st], "risk_bf_q") for st in (1, 2)},
        "permutation_risk_orientation": None,
        "note": "risk_bf_q = -BF_q so that higher score = riskier; the frozen substantive "
                "direction (higher BF_q => lower risk) corresponds to AUROC(risk_bf_q, wrong) > 0.5. "
                "The literal frozen numeric gate used AUROC(BF_q, wrong) > 0.5, which encodes the "
                "opposite orientation (a preregistration sign defect documented in gate2_decision.md).",
    }
    # permutation in risk orientation
    rng_perm = random.Random(BOOTSTRAP_SEED + 2)
    rows_perm = [f for f in hc if f["bf_paraphrase"] is not None and f["bf_reverse"] is not None]
    labels_perm = [f["consensus_wrong"] for f in rows_perm]
    obs_perm = auROC([-f["bf_q"] for f in rows_perm], labels_perm)
    perms_risk = []
    for _ in range(PERM_N):
        pseudo = []
        for f in rows_perm:
            if rng_perm.random() < 0.5:
                pseudo.append(-(0.5 * f["bf_paraphrase"] + 0.5 * (1.0 - f["bf_reverse"])))
            else:
                pseudo.append(-(0.5 * (1.0 - f["bf_paraphrase"]) + 0.5 * f["bf_reverse"]))
        a = auROC(pseudo, labels_perm)
        if a is not None:
            perms_risk.append(a)
    perms_risk = sorted(perms_risk)
    risk["permutation_risk_orientation"] = {
        "obs_auroc": obs_perm,
        "perm_mean": float(np.mean(perms_risk)),
        "perm_95pct": perms_risk[int(0.95 * len(perms_risk))],
    }

    result = {
        "protocol": "cs-pilot-vitaminc-2026-09-13",
        "risk_orientation": risk,
        "population": {"total_items": len(feats), "high_consensus": len(hc),
                       "wrong_hc": len(wrong), "wrong_rate": round(len(wrong) / max(1, len(hc)), 4),
                       "hc_by_label": dict(Counter(f["gold_label"] for f in hc)),
                       "wrong_hc_by_label": dict(Counter(f["gold_label"] for f in wrong))},
        "e1": e1, "e2": e2, "e3": e3, "e4": {k: v for k, v in e4.items() if v is not None},
        "macro_ci": macro_ci,
        "s1": s1, "s2": s2, "s3": s3, "s4": s4, "s5": s5,
        "c1": c1, "c2": c2, "c3": c3, "reducibility": red,
        "gates": gates,
    }
    (ANALYSIS_DIR / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"population": result["population"], "e1": e1, "e3": e3,
                      "e4": {k: v for k, v in e4.items() if v is not None}, "macro_ci": macro_ci,
                      "s1": s1, "c1": c1, "c2": c2, "red": red, "gates": gates}, indent=2, ensure_ascii=False))


def compute_macro_ci(feats, score_key, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 5):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    macro_vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            pid = rng.choice(pairs)
            sample.extend(by_pair[pid])
        a_s = auROC([f[score_key] for f in sample if f["gold_label"] == "SUPPORTS"],
                    [f["consensus_wrong"] for f in sample if f["gold_label"] == "SUPPORTS"])
        a_r = auROC([f[score_key] for f in sample if f["gold_label"] == "REFUTES"],
                    [f["consensus_wrong"] for f in sample if f["gold_label"] == "REFUTES"])
        if a_s is not None and a_r is not None:
            macro_vals.append(0.5 * (a_s + a_r))
    macro_vals = sorted(macro_vals)
    return [macro_vals[int(0.025 * len(macro_vals))], macro_vals[int(0.975 * len(macro_vals)) - 1]]


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import round2_lib as pl
    main()
