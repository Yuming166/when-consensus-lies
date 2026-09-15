#!/usr/bin/env python3
"""Round 7 Agent W3 - fusion point A: shared loaders + bootstrap helpers.

Read-only frozen inputs (benchmark/frozen/vitaminc) + labels ledger. No new model calls.
Reuses round3/analysis_lib.py pair-grouped bootstrap conventions (2000 replicates).
Frozen RS_q reproduction uses the original seed base 20260913; ALL new statistics use a
distinct POSTHOC seed base (20260913 + 1000) and are labeled exploratory/post-hoc.
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent          # round7/stress_profile
R7 = HERE.parent                                       # round7
CS = R7.parent                                         # consensus_stress
R3 = CS / "round3"
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))
import analysis_lib as al                              # noqa: E402

FROZEN = CS / "benchmark" / "frozen" / "vitaminc"
LEDGER = FROZEN / "labels_ledger.json"
BOOTSTRAP_N = 2000
HC_THRESHOLD = al.HC_THRESHOLD          # 0.8
SEED_FROZEN = al.BOOTSTRAP_SEED          # 20260913 (frozen reproduction)
POSTHOC_BASE = al.BOOTSTRAP_SEED + 1000  # 20260913+1000, distinct for all new stats

MODEL_FILES = {
    "qwen": {"features": FROZEN / "preoutcome_features.jsonl", "display": "Qwen3.5-4B"},
    "ling": {"features": FROZEN / "ling_preoutcome_features.jsonl", "display": "Ling-3.0-tiny"},
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def load_model(model_key: str, hc_only: bool = False) -> list[dict]:
    """Load frozen features + gold; attach labels and risk-oriented keys."""
    rows = load_jsonl(MODEL_FILES[model_key]["features"])
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    gold = {r["item_id"]: r["gold_label"] for r in ledger["items"]}
    for row in rows:
        label = gold[row["item_id"]]
        row["gold_label"] = label
        row["gold_yes"] = label == "SUPPORTS"
        row["consensus_wrong"] = int((row["consensus"] == "yes") != row["gold_yes"])
        row["risk_bf_q"] = -row["bf_q"]
        row["risk_rev"] = 1.0 - row["rev_flip_rate"]      # reversal rigidity (higher = riskier)
        row["risk_rem"] = row["rem_flip_rate"]            # removal instability (higher = riskier)
        row["risk_para"] = row["para_flip_rate"]          # paraphrase instability
        row["risk_synth"] = row["synth_flip_rate"]
    if hc_only:
        return [row for row in rows if row["agreement"] >= HC_THRESHOLD]
    return rows


def group_mean_bootstrap(feats: list[dict], key: str, seed: int, n: int = BOOTSTRAP_N) -> dict:
    """Pair-grouped bootstrap 95% CI of (mean(key | correct) - mean(key | wrong))."""
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def stat(rows_: list[dict]) -> float | None:
        c = [f[key] for f in rows_ if not f["consensus_wrong"]]
        w = [f[key] for f in rows_ if f["consensus_wrong"]]
        if not c or not w:
            return None
        return float(np.mean(c) - np.mean(w))

    obs = stat(rows)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        v = stat(sample)
        if v is not None:
            vals.append(v)
    vals = sorted(vals)
    return {"diff_correct_minus_wrong": obs,
            "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n_correct": sum(1 for f in rows if not f["consensus_wrong"]),
            "n_wrong": sum(1 for f in rows if f["consensus_wrong"]),
            "n_pairs": len(pairs)}


def auroc_ci(feats: list[dict], key: str, seed: int) -> dict:
    return al.group_bootstrap(feats, key, seed=seed)


def risk80_ci(feats: list[dict], key: str, seed: int) -> dict:
    return al.risk_at_80_bootstrap(feats, key, seed=seed)


def paired_auroc_diff(feats: list[dict], key_a: str, key_b: str, seed: int) -> dict:
    return al.paired_bootstrap_diff(feats, key_a, key_b, seed=seed)


def paired_risk80_diff(feats: list[dict], key_a: str, key_b: str, seed: int) -> dict:
    return al.risk_at_80_paired_diff(feats, key_a, key_b, seed=seed)


def spearman_ci(feats: list[dict], key_a: str, key_b: str, seed: int,
                n: int = BOOTSTRAP_N) -> dict:
    from scipy.stats import spearmanr
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key_a) is not None and f.get(key_b) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    x0 = np.array([f[key_a] for f in rows], dtype=float)
    y0 = np.array([f[key_b] for f in rows], dtype=float)
    point = float(spearmanr(x0, y0).statistic)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        xs = np.array([f[key_a] for f in sample], dtype=float)
        ys = np.array([f[key_b] for f in sample], dtype=float)
        if np.all(xs == xs[0]) or np.all(ys == ys[0]):
            continue
        s = float(spearmanr(xs, ys).statistic)
        if np.isfinite(s):
            vals.append(s)
    vals = sorted(vals)
    return {"rho": point,
            "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_pairs": len(pairs)}
