#!/usr/bin/env python3
"""Agent C (R3): reducibility of RS_q to R_sym / R_PI / flip-rate / disagreement / confidence.

Read-only frozen records (benchmark/frozen/vitaminc + labels ledger). No new model calls.
Reuses round3/analysis_lib.py pair-grouped bootstrap conventions and seeds.
Outputs round6/reducibility/reducibility_results.json
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
CS = HERE.parent.parent
BENCH = CS / "benchmark"
FROZEN = BENCH / "frozen" / "vitaminc"
R3 = CS / "round3"
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))
import analysis_lib as al

SEED = 20_260_913          # same base as leaderboard
HC_THRESHOLD = 0.8
BOOTSTRAP_N = 2000
TIES_EPS = 1e-9

MODEL_FILES = {
    "qwen": {"features": FROZEN / "preoutcome_features.jsonl", "display": "Qwen3.5-4B"},
    "ling": {"features": FROZEN / "ling_preoutcome_features.jsonl", "display": "Ling-3.0-tiny"},
}

# Baseline score keys -> human names. AUROC is direction-agnostic; raw feature values used.
BASELINES = [
    ("R_sym", "R_sym"),
    ("R_PI", "R_PI"),
    ("rev_flip_rate", "flip-rate (natural reverse)"),
    ("intervention_disagreement", "disagreement (intervention)"),
    ("agreement", "agreement (vote)"),
    ("mean_confidence", "confidence (mean)"),
    ("bf_paraphrase", "paraphrase faithfulness (axis)"),
]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def load_hc(model_key: str) -> list[dict]:
    rows = load_jsonl(MODEL_FILES[model_key]["features"])
    ledger = json.loads((FROZEN / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {r["item_id"]: r["gold_label"] for r in ledger["items"]}
    for row in rows:
        label = gold[row["item_id"]]
        row["gold_label"] = label
        row["gold_yes"] = label == "SUPPORTS"
        row["consensus_wrong"] = int((row["consensus"] == "yes") != row["gold_yes"])
        row["risk_bf_q"] = -row["bf_q"]
        row["risk_rev_axis"] = -row["rev_flip_rate"]
        row["risk_para_axis"] = -row["bf_paraphrase"]
    return [row for row in rows if row["agreement"] >= HC_THRESHOLD]


def spearman_ci(hc: list[dict], key_a: str, key_b: str, seed: int) -> dict:
    rng = random.Random(seed)
    rows = [r for r in hc if r.get(key_a) is not None and r.get(key_b) is not None]
    by_pair: dict[str, list[dict]] = {}
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


def residualize_auroc(hc: list[dict], key_new: str, key_b: str, label_key: str,
                      seed: int) -> dict:
    """Incremental AUROC: AUROC of OLS residuals of RS_q on baseline B (label-free fit).

    Pair-grouped bootstrap; the OLS residualization is refit inside each replicate.
    """
    rng = random.Random(seed)
    rows = [r for r in hc if r.get(key_new) is not None and r.get(key_b) is not None]
    by_pair: dict[str, list[dict]] = {}
    for r in rows:
        by_pair.setdefault(r["pair_id"], []).append(r)
    pairs = sorted(by_pair)

    def auroc_resid(sample: list[dict]) -> float | None:
        x = np.array([r[key_new] for r in sample], dtype=float)
        b = np.array([r[key_b] for r in sample], dtype=float)
        y = np.array([r[label_key] for r in sample], dtype=float)
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


def plain_auroc(hc: list[dict], key: str, seed: int) -> dict:
    return al.group_bootstrap(hc, key, seed=seed)


def main() -> int:
    results = {"protocol": "round6-reducibility-vs-R_sym-R_PI-flip-disagreement-confidence",
               "seed_base": SEED, "bootstrap_n": BOOTSTRAP_N,
               "hc_threshold": HC_THRESHOLD,
               "method": "Spearman (tie-aware) + incremental AUROC of label-free OLS "
                         "residuals of RS_q on each baseline; pair-grouped bootstrap 95% CI",
               "models": []}
    offset = 0
    for model_key in ("qwen", "ling"):
        hc = load_hc(model_key)
        rs_auroc = plain_auroc(hc, "risk_bf_q", seed=SEED + offset); offset += 1
        model_rec = {
            "model": MODEL_FILES[model_key]["display"],
            "hc": {"n_items": len(hc),
                   "n_pairs": len({r["pair_id"] for r in hc}),
                   "wrong": sum(r["consensus_wrong"] for r in hc)},
            "rs_q_auroc": rs_auroc,
            "axes": {
                "risk_reverse_axis_minus_rev_flip_rate": plain_auroc(hc, "risk_rev_axis", seed=SEED + offset),
                "risk_paraphrase_axis_minus_bf_paraphrase": plain_auroc(hc, "risk_para_axis", seed=SEED + offset + 1),
                "incremental_rs_q_over_reverse_axis": residualize_auroc(hc, "risk_bf_q", "rev_flip_rate", "consensus_wrong", seed=SEED + offset + 2),
                "incremental_rs_q_over_paraphrase_axis": residualize_auroc(hc, "risk_bf_q", "bf_paraphrase", "consensus_wrong", seed=SEED + offset + 3),
                "paired_auroc_diff_rs_q_minus_reverse_axis": al.paired_bootstrap_diff(hc, "risk_bf_q", "risk_rev_axis", seed=SEED + offset + 4),
                "paired_auroc_diff_rs_q_minus_paraphrase_axis": al.paired_bootstrap_diff(hc, "risk_bf_q", "risk_para_axis", seed=SEED + offset + 5),
            },
            "baselines": {},
        }
        offset += 6
        for key, name in BASELINES:
            s = spearman_ci(hc, "risk_bf_q", key, seed=SEED + offset); offset += 1
            inc = residualize_auroc(hc, "risk_bf_q", key, "consensus_wrong",
                                    seed=SEED + offset); offset += 1
            b_auroc = plain_auroc(hc, key, seed=SEED + offset); offset += 1
            paired = al.paired_bootstrap_diff(hc, "risk_bf_q", key,
                                              seed=SEED + offset); offset += 1
            model_rec["baselines"][key] = {
                "name": name,
                "spearman_rs_q": s,
                "incremental_auroc_resid_rs_q_on_b": inc,
                "baseline_auroc": b_auroc,
                "paired_auroc_diff_rs_q_minus_b": paired,
            }
        results["models"].append(model_rec)

    out = HERE / "reducibility_results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
