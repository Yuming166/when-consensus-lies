"""Agent E -- label balance & error quality (SUPPORTS vs REFUTES), round6.

Read-only: frozen round3/round4 preoutcome features + labels_ledger.
Zero new model calls. Diagnostic/matched-rate analyses are explicitly post-hoc.

Seed rules:
  - Reproduction of frozen per-label AUROC uses the historical seeds:
      Qwen  per-label : analysis_lib default seed 20260913 (round3 analyze.py)
      Ling  per-label : 20260913 + 402              (round4 SEED+2)
  - All NEW round6 statistics use base seed 20260913 + 600 (Agent E block),
    with a documented per-statistic offset.
"""
from __future__ import annotations
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R6 = HERE.parent
ROOT = R6.parents[1]                     # consensus_stress
R3 = ROOT / "round3"
R4 = ROOT / "round4"
FROZEN = ROOT / "benchmark" / "frozen" / "vitaminc"

sys.path.insert(0, str(R3))
import analysis_lib as al  # noqa: E402

HC_THRESHOLD = 0.8
BOOTSTRAP_N = 2000
R6_SEED = 20_260_913 + 600               # Agent E block base
RISK_KEY = "risk_bf_q"

SOURCES = {
    "qwen": FROZEN / "preoutcome_features.jsonl",
    "ling": FROZEN / "ling_preoutcome_features.jsonl",
}
LEDGER = FROZEN / "labels_ledger.json"


def load_merged(prefix: str) -> list[dict]:
    path = SOURCES[prefix]
    feats = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        g = gold[f["item_id"]]
        f["gold_label"] = g
        f["gold_yes"] = g == "SUPPORTS"
        f["consensus_wrong"] = int((f["consensus"] == "yes") != f["gold_yes"])
        f[RISK_KEY] = -f["bf_q"] if f.get("bf_q") is not None else None
    return feats


# ---------------------------------------------------------------- utilities
def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float] | None:
    if n == 0:
        return None
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (center - half, center + half)


def auROC_concordance(scores, labels, wrong_labels):
    """Additive concordant-pair decomposition of the pooled AUROC by wrong-item label.

    pooled AUROC = sum_over_wrong_items( n_correct_below + 0.5*n_correct_tied ) / (pos*neg).
    The numerator is additive across wrong-item labels, so the share of concordant mass
    carried by SUPPORTS-wrong vs REFUTES-wrong items is exact given the frozen scores.
    """
    n = len(scores)
    concord = {"SUPPORTS": 0.0, "REFUTES": 0.0}
    pos = {"SUPPORTS": 0, "REFUTES": 0}
    neg = sum(1 for l in labels if l == 0)
    for i in range(n):
        if labels[i] == 1:
            wl = wrong_labels[i]
            pos[wl] += 1
            below = tied = 0
            for j in range(n):
                if labels[j] == 0:
                    if scores[j] < scores[i]:
                        below += 1
                    elif scores[j] == scores[i]:
                        tied += 1
            concord[wl] += below + 0.5 * tied
    total = sum(concord.values())
    total_pos = sum(pos.values())
    return {"concord_by_label": concord,
            "concord_share_by_label": {k: v / total for k, v in concord.items()},
            "pos_by_label": pos, "neg": neg, "total_concord": total,
            "implied_pooled_auroc": total / (total_pos * neg) if total_pos and neg else None}


def label_risk_at_80_bootstrap(feats, key, label, coverage=0.8, n=BOOTSTRAP_N, seed=R6_SEED + 10):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key) is not None and f["gold_label"] == label]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def reduction(rows_):
        overall = np.mean([f["consensus_wrong"] for f in rows_])
        if overall == 0:
            return None
        xs = sorted(rows_, key=lambda f: f[key])
        keep = xs[:int(coverage * len(xs))]
        ret = np.mean([f["consensus_wrong"] for f in keep]) if keep else 0.0
        return 1.0 - ret / overall

    obs = reduction(rows)
    if obs is None:
        return None
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        sample = [f for f in sample if f["gold_label"] == label]
        r = reduction(sample)
        if r is not None:
            vals.append(r)
    vals = sorted(vals)
    return {"reduction": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "overall_error": float(np.mean([f["consensus_wrong"] for f in rows])),
            "n": len(rows), "n_pairs": len(pairs)}


def label_auroc_diff_ci(feats, key, n=BOOTSTRAP_N, seed=R6_SEED + 20):
    """Same-pair bootstrap CI for AUROC(SUPPORTS) - AUROC(REFUTES)."""
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def diff(rows_):
        vals = []
        for lbl in ("SUPPORTS", "REFUTES"):
            sub = [f for f in rows_ if f["gold_label"] == lbl]
            a = al.auROC([f[key] for f in sub], [f["consensus_wrong"] for f in sub])
            if a is None:
                return None
            vals.append(a)
        return vals[0] - vals[1]

    obs = diff(rows)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        d = diff(sample)
        if d is not None:
            vals.append(d)
    vals = sorted(vals)
    return {"diff": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows)}


# ------------------------------------------------- matched-rate diagnostics
def draw_label_pairs_until(feats, label, min_errors, max_draws, rng, key, cap=50):
    """Pair-grouped resampling within one label until >= min_errors wrong items collected.

    Returns (sample, draws_done, errors_collected). Diagnostic only.
    Running error count maintained incrementally (O(draws) per call).
    """
    rows = [f for f in feats if f.get(key) is not None and f["gold_label"] == label]
    by_pair: dict[str, list[dict]] = {}
    err_by_pair: dict[str, int] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
        err_by_pair[f["pair_id"]] = err_by_pair.get(f["pair_id"], 0) + int(f["consensus_wrong"])
    pairs = sorted(by_pair)
    sample: list[dict] = []
    err = 0
    draws = 0
    while err < min_errors and draws < max_draws * cap:
        pid = rng.choice(pairs)
        sample.extend(by_pair[pid])
        err += err_by_pair[pid]
        draws += 1
    return sample, draws, err


def error_count_matched_auroc(feats, up_to_refutes=True, n=BOOTSTRAP_N, seed=R6_SEED + 30):
    """Diagnostic pooled AUROC with matched per-label error counts.

    up_to_refutes=True : SUPPORTS is resampled until it contributes as many errors
                         as REFUTES (raise rare label up to the frequent label).
    up_to_refutes=False: both labels are resampled until they contribute the same
                         small error count (the SUPPORTS count, 7 for Qwen) -- i.e.
                         REFUTES is matched down to the rare label.
    Both scenarios are post-hoc sensitivity analyses, NOT gates.
    """
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(RISK_KEY) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    err_by_label = Counter(f["gold_label"] for f in rows if f["consensus_wrong"])
    e_sup, e_ref = err_by_label["SUPPORTS"], err_by_label["REFUTES"]
    target = e_ref if up_to_refutes else e_sup

    def statistic():
        # label A (to match up/down) sampled until >= target errors
        if up_to_refutes:
            a_label, a_err = "SUPPORTS", e_sup
            b_label, b_err = "REFUTES", e_ref
        else:
            a_label, a_err = "REFUTES", e_ref
            b_label, b_err = "SUPPORTS", e_sup
        a_sample, _, _ = draw_label_pairs_until(rows, a_label, target, len(by_pair), rng, RISK_KEY)
        # b_label: ordinary pair-grouped resample of its own pairs
        b_rows = [f for f in rows if f["gold_label"] == b_label]
        b_by_pair: dict[str, list[dict]] = {}
        for f in b_rows:
            b_by_pair.setdefault(f["pair_id"], []).append(f)
        b_pairs = sorted(b_by_pair)
        b_sample = []
        for _ in range(len(b_pairs)):
            b_sample.extend(b_by_pair[rng.choice(b_pairs)])
        pooled = a_sample + b_sample
        a = al.auROC([f[RISK_KEY] for f in pooled], [f["consensus_wrong"] for f in pooled])
        return a

    obs = None
    vals = []
    for _ in range(n):
        a = statistic()
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    # observed on a single fixed draw for a point estimate (median of replicates is
    # a stable diagnostic point; report the replicate median as the diagnostic value)
    return {
        "diagnostic_auroc_median": float(np.median(vals)),
        "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
        "target_errors_per_label": int(target),
        "e_sup": int(e_sup), "e_ref": int(e_ref),
        "n_replicates": len(vals),
    }


# ------------------------------------------------------- LOO jackknife
def jackknife_label_auroc(feats, key, label):
    rows = [f for f in feats if f.get(key) is not None and f["gold_label"] == label]
    full = al.auROC([f[key] for f in rows], [f["consensus_wrong"] for f in rows])
    loo = []
    for i in range(len(rows)):
        sub = rows[:i] + rows[i + 1:]
        a = al.auROC([f[key] for f in sub], [f["consensus_wrong"] for f in sub])
        if a is not None:
            loo.append(a)
    loo = sorted(loo)
    return {
        "full": full, "n": len(rows),
        "loo_min": loo[0], "loo_max": loo[-1],
        "loo_mean": float(np.mean(loo)),
        "loo_all_gt_05": all(x > 0.5 for x in loo),
        "loo_all_gt_08": all(x > 0.8 for x in loo),
    }


def error_rank_percentiles(feats, key, label):
    rows = [f for f in feats if f.get(key) is not None and f["gold_label"] == label]
    ordered = sorted(rows, key=lambda f: f[key])          # low risk -> high risk
    n = len(ordered)
    pcts = []
    for idx, f in enumerate(ordered):
        if f["consensus_wrong"]:
            pcts.append((idx + 1) / n * 100.0)
    return {"n": n, "n_errors": len(pcts), "pctiles": [round(x, 2) for x in pcts],
            "mean_pctile": float(np.mean(pcts)) if pcts else None,
            "min_pctile": min(pcts) if pcts else None,
            "max_pctile": max(pcts) if pcts else None}


# -------------------------------------------------------------------- main
def analyze(prefix: str) -> dict:
    feats = load_merged(prefix)
    hc = [f for f in feats if f["agreement"] >= HC_THRESHOLD]
    wrong = [f for f in hc if f["consensus_wrong"]]
    n_by_label = Counter(f["gold_label"] for f in hc)
    e_by_label = Counter(f["gold_label"] for f in wrong)
    out: dict = {"prefix": prefix, "n_total": len(feats), "n_hc": len(hc),
                 "n_wrong_hc": len(wrong),
                 "hc_by_label": dict(n_by_label), "wrong_by_label": dict(e_by_label),
                 "error_rate_by_label": {lbl: round(e_by_label[lbl] / n_by_label[lbl], 4)
                                         for lbl in ("SUPPORTS", "REFUTES")},
                 "wilson_ci_by_label": {lbl: [round(x, 4) for x in wilson_ci(e_by_label[lbl], n_by_label[lbl])]
                                        for lbl in ("SUPPORTS", "REFUTES")}}

    # ---- pooled reference (reproduction) ----
    pool_seed = 20260913 if prefix == "qwen" else 20_260_913 + 400 + 1
    out["pooled"] = {
        "auroc": al.group_bootstrap(hc, RISK_KEY, seed=pool_seed),
        "risk80": al.risk_at_80_bootstrap(hc, RISK_KEY, seed=pool_seed + 4),
    }

    # ---- task 1: per-label AUROC / Risk@80 with pair-grouped CI ----
    hist_seed = 20260913 if prefix == "qwen" else 20_260_913 + 400 + 2
    per_label_auroc = {lbl: al.label_subgroup_bootstrap(hc, RISK_KEY, lbl, seed=hist_seed)
                       for lbl in ("SUPPORTS", "REFUTES")}
    per_label_risk80 = {lbl: label_risk_at_80_bootstrap(hc, RISK_KEY, lbl, seed=R6_SEED + 10)
                        for lbl in ("SUPPORTS", "REFUTES")}
    auroc_diff = label_auroc_diff_ci(hc, RISK_KEY, seed=R6_SEED + 20)
    out["per_label_auroc"] = per_label_auroc
    out["per_label_risk80"] = per_label_risk80
    out["label_auroc_diff_sup_minus_ref"] = auroc_diff

    # ---- task 2: diagnostics (post-hoc) ----
    conc = auROC_concordance([f[RISK_KEY] for f in hc],
                             [f["consensus_wrong"] for f in hc],
                             [f["gold_label"] for f in hc])
    out["concordance_attribution"] = conc
    out["matched_up_to_refutes"] = error_count_matched_auroc(hc, up_to_refutes=True, seed=R6_SEED + 30)
    out["matched_down_to_supports"] = error_count_matched_auroc(hc, up_to_refutes=False, seed=R6_SEED + 31)

    # ---- task 3: SUPPORTS 7-error robustness (Qwen primary, Ling secondary) ----
    out["jackknife_supports"] = jackknife_label_auroc(hc, RISK_KEY, "SUPPORTS")
    out["jackknife_refutes"] = jackknife_label_auroc(hc, RISK_KEY, "REFUTES")
    out["error_rank_pctiles_supports"] = error_rank_percentiles(hc, RISK_KEY, "SUPPORTS")
    out["error_rank_pctiles_refutes"] = error_rank_percentiles(hc, RISK_KEY, "REFUTES")
    return out


def main() -> None:
    results = {"qwen": analyze("qwen"), "ling": analyze("ling")}
    out_path = R6 / "label_balance_analysis_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", out_path)

    # console summary
    for prefix, r in results.items():
        print(f"\n=== {prefix} ===")
        print("HC:", r["n_hc"], "wrong:", r["n_wrong_hc"], "per-label:", r["hc_by_label"], r["wrong_by_label"])
        print("pooled AUROC:", r["pooled"]["auroc"])
        print("per-label AUROC:", {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                                       for kk, vv in v.items() if kk != 'n_pairs'}
                                   for k, v in r["per_label_auroc"].items()})
        print("per-label Risk@80:", {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                                          for kk, vv in v.items() if kk != 'n_pairs'}
                                      for k, v in r["per_label_risk80"].items()})
        print("AUROC diff sup-ref:", r["label_auroc_diff_sup_minus_ref"])
        print("concord share:", r["concordance_attribution"]["concord_share_by_label"])
        print("matched up:", r["matched_up_to_refutes"])
        print("matched down:", r["matched_down_to_supports"])
        print("jackknife SUPPORTS:", {k: (round(v, 4) if isinstance(v, float) else v)
                                      for k, v in r["jackknife_supports"].items()})
        print("supports error pctiles:", r["error_rank_pctiles_supports"])


if __name__ == "__main__":
    main()
