"""Shared read-only helpers for round-7 W1 P0 audit (mirror equivalence + S_pair).

All data is frozen. No model calls. Bootstrap follows round3/analysis_lib.py:
pair-grouped resampling, 2000 replicates, seed base 20260913 + fixed offsets
(round5 seed rule). AUROC is the tie-aware Mann-Whitney U / average-rank AUC.
"""
from __future__ import annotations
import json
import random
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

CS = Path(__file__).resolve().parents[3]      # consensus_stress/
R3 = CS / "round3"
R4 = CS / "round4"
FROZEN = CS / "benchmark" / "frozen" / "vitaminc"

SEED_BASE = 20_260_913
BOOTSTRAP_N = 2000
HC_THRESHOLD = 0.8

MODEL_FILES = {
    "qwen": {"features": FROZEN / "preoutcome_features.jsonl",
             "records": FROZEN / "records.jsonl",
             "display": "Qwen3.5-4B"},
    "ling": {"features": FROZEN / "ling_preoutcome_features.jsonl",
             "records": FROZEN / "ling_records.jsonl",
             "display": "Ling-3.0-tiny"},
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def load_ledger() -> dict:
    return json.loads((R3 / "labels_ledger.json").read_text(encoding="utf-8"))


def load_full(model_key: str) -> list[dict]:
    """Frozen preoutcome features + labels merged ONLY here (post-freeze), all items."""
    rows = load_jsonl(MODEL_FILES[model_key]["features"])
    ledger = load_ledger()
    gold = {r["item_id"]: r["gold_label"] for r in ledger["items"]}
    for row in rows:
        label = gold[row["item_id"]]
        row["gold_label"] = label
        row["gold_yes"] = label == "SUPPORTS"
        row["consensus_wrong"] = int((row["consensus"] == "yes") != row["gold_yes"])
        row["risk_bf_q"] = -row["bf_q"] if row.get("bf_q") is not None else None
    return rows


def load_hc(model_key: str) -> list[dict]:
    """HC subset of load_full (agreement >= 0.8)."""
    return [row for row in load_full(model_key) if row["agreement"] >= HC_THRESHOLD]


def flip(y: str) -> str:
    return "no" if y == "yes" else "yes"


def mirror_item_id(item_id: str) -> str:
    return (item_id.replace(":support", ":refute") if item_id.endswith(":support")
            else item_id.replace(":refute", ":support"))


def auROC(scores, labels):
    pos = sum(1 for l in labels if l == 1)
    neg = sum(1 for l in labels if l == 0)
    if pos == 0 or neg == 0:
        return None
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    rank_sum = 0.0
    i = 0
    n = len(pairs)
    while i < n:
        j = i
        while j < n and pairs[j][0] == pairs[i][0]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            if pairs[k][1] == 1:
                rank_sum += avg
        i = j
    return (rank_sum - pos * (pos + 1) / 2.0) / (pos * neg)


def group_bootstrap_auroc(rows, score_key, label_key="consensus_wrong", seed=SEED_BASE):
    """Pair-grouped bootstrap AUROC + 95% CI (round3/analysis_lib convention)."""
    rng = random.Random(seed)
    rows = [r for r in rows if r.get(score_key) is not None]
    by_g: dict[str, list[dict]] = {}
    for r in rows:
        by_g.setdefault(r["pair_id"], []).append(r)
    groups = sorted(by_g)
    obs = auROC([r[score_key] for r in rows], [r[label_key] for r in rows])
    vals = []
    for _ in range(BOOTSTRAP_N):
        sample = []
        for _ in range(len(groups)):
            sample.extend(by_g[rng.choice(groups)])
        a = auROC([r[score_key] for r in sample], [r[label_key] for r in sample])
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    return {"auroc": obs,
            "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_pairs": len(groups)}


def paired_bootstrap_diff(rows, key_a, key_b, label_key="consensus_wrong", seed=SEED_BASE):
    rng = random.Random(seed)
    rows = [r for r in rows if r.get(key_a) is not None and r.get(key_b) is not None]
    by_pair: dict[str, list[dict]] = {}
    for r in rows:
        by_pair.setdefault(r["pair_id"], []).append(r)
    pairs = sorted(by_pair)

    def diff(rows_):
        a = auROC([r[key_a] for r in rows_], [r[label_key] for r in rows_])
        b = auROC([r[key_b] for r in rows_], [r[label_key] for r in rows_])
        return (a - b) if (a is not None and b is not None) else None

    obs = diff(rows)
    vals = []
    for _ in range(BOOTSTRAP_N):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        d = diff(sample)
        if d is not None:
            vals.append(d)
    vals = sorted(vals)
    return {"diff": obs,
            "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_pairs": len(pairs)}


def spearman_ci(rows, key_a, key_b, seed=SEED_BASE):
    rng = random.Random(seed)
    rows = [r for r in rows if r.get(key_a) is not None and r.get(key_b) is not None]
    by_pair: dict[str, list[dict]] = {}
    for r in rows:
        by_pair.setdefault(r["pair_id"], []).append(r)
    pairs = sorted(by_pair)
    x0 = np.array([r[key_a] for r in rows], dtype=float)
    y0 = np.array([r[key_b] for r in rows], dtype=float)
    if np.all(x0 == x0[0]) or np.all(y0 == y0[0]):
        return None
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


def pearson(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return float(np.corrcoef(x, y)[0, 1])


def add_mirror_refs(rows, full=None):
    """Attach mirror-item fields (same pair, other item) from `full` (default: same list).

    Using the full 600-item set keeps every HC row's mirror fields well-defined even
    when the mirror item is not itself in the HC subset.
    """
    full = full if full is not None else rows
    by_item = {r["item_id"]: r for r in full}
    for r in rows:
        j = by_item.get(mirror_item_id(r["item_id"]))
        r["mirror_item_id"] = j["item_id"] if j else None
        for key in ("bf_q", "bf_reverse", "bf_paraphrase", "rev_flip_rate",
                    "risk_bf_q", "agreement", "mean_confidence", "R_sym", "R_PI",
                    "consensus_wrong", "consensus"):
            r[f"mirror_{key}"] = j.get(key) if j else None
    return rows
