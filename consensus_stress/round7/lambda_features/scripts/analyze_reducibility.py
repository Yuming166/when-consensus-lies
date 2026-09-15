#!/usr/bin/env python3
"""W4 (round7, fusion point B): reducibility of phase-3 lambda stress features.

Zero new model calls. On the frozen 240-item / 120-pair phase-3 subset (HC subset:
agreement >= 0.8 -> 225 items / 119 pairs), tests whether continuous lambda-curve
features (stress-area, breakpoint, robustness-radius; reversal primary, removal
descriptive) carry incremental signal beyond:
  (a) the binary reverse axis (rev_flip_rate), and
  (b) RS_q / BF_q (= -RS_q; residualization is sign-invariant to BF_q).
R_sym is included as a reference baseline (same method as round6).

Method (reused verbatim from round6/reducibility/analyze_reducibility.py):
label-free OLS residualization of the stress risk on the baseline, refit inside
each pair-grouped bootstrap replicate; AUROC of residuals vs consensus_wrong.
All CI are pair-grouped bootstrap 95% (2000 resamples, seed base 20260913 +
distinct offsets). This whole W4 analysis is exploratory/post-hoc (plan section 16).

Outputs: reducibility_results.json (all stats).
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

CS = Path(__file__).resolve().parents[3]
R3 = CS / "round3"
HERE = Path(__file__).resolve().parent.parent
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))
import analysis_lib as al

SEED_BASE = 20_260_913
OFFSET_START = 200           # clearly outside round3 (+40/41) and round6 (+0..~56) ranges
HC_THRESHOLD = 0.8
BOOTSTRAP_N = 2000

# stress risk features (direction: higher = riskier / more consensus-wrong)
STRESS_FEATURES = [
    ("risk_rev_stress_area", "reversal stress-area (RS_stress=-area)"),
    ("risk_rev_breakpoint_none1", "reversal breakpoint lambda (never-flip=1.0)"),
    ("risk_rev_robustness_radius", "reversal robustness radius (=1.0 never flips)"),
    ("risk_rem_stress_area", "removal stress-area (descriptive)"),
    ("risk_rem_breakpoint_none1", "removal breakpoint lambda (descriptive)"),
    ("risk_rem_robustness_radius", "removal robustness radius (descriptive)"),
]

# baselines: raw feature key + risk-key alias + human name
BASELINES = [
    ("rev_flip_rate", "risk_rev_axis", "binary reverse axis (rev_flip_rate)"),
    ("bf_q", "risk_bf_q", "RS_q/BF_q (= -bf_q)"),
    ("R_sym", "R_sym", "R_sym (reference)"),
]


def load_subset_hc():
    rows = [json.loads(l) for l in (HERE / "features_phase3_lambda.jsonl").read_text(encoding="utf-8").splitlines() if l]
    return [r for r in rows if r["agreement"] >= HC_THRESHOLD]


def plain_auroc(hc, key, seed):
    return al.group_bootstrap(hc, key, seed=seed)


def residualize_auroc(hc, key_new, key_b, seed):
    """Incremental AUROC: AUROC of label-free OLS residuals of key_new on key_b.
    Pair-grouped bootstrap; OLS refit inside each replicate (round6 method)."""
    rng = random.Random(seed)
    rows = [r for r in hc if r.get(key_new) is not None and r.get(key_b) is not None]
    by_pair = {}
    for r in rows:
        by_pair.setdefault(r["pair_id"], []).append(r)
    pairs = sorted(by_pair)

    def auroc_resid(sample):
        x = np.array([r[key_new] for r in sample], dtype=float)
        b = np.array([r[key_b] for r in sample], dtype=float)
        y = np.array([r["consensus_wrong"] for r in sample], dtype=float)
        if np.std(b) == 0.0 or np.std(x) == 0.0:
            return None
        slope, intercept = np.polyfit(b, x, 1)
        resid = x - (slope * b + intercept)
        return al.auROC(resid.tolist(), y.tolist())

    obs = auroc_resid(rows)
    vals = []
    for _ in range(BOOTSTRAP_N):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        a = auroc_resid(sample)
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    return {"auroc": obs,
            "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_pairs": len(pairs)}


def spearman_ci(hc, key_a, key_b, seed):
    rng = random.Random(seed)
    rows = [r for r in hc if r.get(key_a) is not None and r.get(key_b) is not None]
    by_pair = {}
    for r in rows:
        by_pair.setdefault(r["pair_id"], []).append(r)
    pairs = sorted(by_pair)
    x0 = np.array([r[key_a] for r in rows], dtype=float)
    y0 = np.array([r[key_b] for r in rows], dtype=float)
    point = float(spearmanr(x0, y0).statistic)
    vals = []
    for _ in range(BOOTSTRAP_N):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        xs = np.array([r[key_a] for r in sample], dtype=float)
        ys = np.array([r[key_b] for r in sample], dtype=float)
        if np.all(xs == xs[0]) or np.all(ys == ys[0]):
            continue
        s = float(spearmanr(xs, ys).statistic)
        if np.isfinite(s):
            vals.append(s)
    vals = sorted(vals)
    return {"rho": point,
            "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_pairs": len(pairs)}


def main():
    hc = load_subset_hc()
    offset = OFFSET_START
    results = {
        "protocol": "round7-W4-lambda-feature-reducibility",
        "scope": "frozen phase-3 subset (240 items / 120 pairs); HC agreement>=0.8 "
                 "-> 225 items / 119 pairs; Qwen3.5-4B only for lambda curves",
        "status": "exploratory / post-hoc robustness analysis (plan section 16); "
                  "zero new model calls; no frozen-number edits",
        "seed_base": SEED_BASE, "bootstrap_n": BOOTSTRAP_N, "hc_threshold": HC_THRESHOLD,
        "method": "plain AUROC + incremental AUROC of label-free OLS residuals of each "
                  "stress feature on each baseline (refit in replicate) + paired AUROC "
                  "diff + Spearman; pair-grouped bootstrap 95% CI (round6 convention)",
        "hc": {"n_items": len(hc), "n_pairs": len({r["pair_id"] for r in hc}),
               "wrong": sum(r["consensus_wrong"] for r in hc)},
    }

    # baseline plain AUROCs on this subset (direction-aware risk encodings)
    results["baselines_auroc"] = {}
    for key, risk_key, name in BASELINES:
        results["baselines_auroc"][key] = {
            "name": name,
            "auroc": plain_auroc(hc, risk_key, seed=SEED_BASE + offset),
        }
        offset += 1

    results["stress_features"] = {}
    for feat_key, feat_name in STRESS_FEATURES:
        rec = {"name": feat_name, "plain_auroc": plain_auroc(hc, feat_key, seed=SEED_BASE + offset)}
        offset += 1
        rec["baselines"] = {}
        for key, risk_key, name in BASELINES:
            rec["baselines"][key] = {
                "name": name,
                "incremental_auroc_resid_on_baseline": residualize_auroc(
                    hc, feat_key, key, seed=SEED_BASE + offset),
                "paired_auroc_diff_stress_minus_baseline": al.paired_bootstrap_diff(
                    hc, feat_key, risk_key, seed=SEED_BASE + offset + 1),
                "spearman_stress_vs_baseline": spearman_ci(
                    hc, feat_key, risk_key, seed=SEED_BASE + offset + 2),
            }
            offset += 3
        results["stress_features"][feat_key] = rec

    out = HERE / "reducibility_results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
