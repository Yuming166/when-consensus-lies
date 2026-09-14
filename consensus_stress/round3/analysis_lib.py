"""Round-3 analysis helpers (pair-grouped bootstrap, AUROC, Risk@80, paired diffs)."""
from __future__ import annotations
import json
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
HC_THRESHOLD = 0.8
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 20260913
PERM_N = 1000


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


def group_bootstrap(feats, score_key, group_key="pair_id", label_key="consensus_wrong",
                    n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None]
    by_g: dict[str, list[dict]] = {}
    for f in rows:
        by_g.setdefault(f[group_key], []).append(f)
    groups = sorted(by_g)
    obs = auROC([f[score_key] for f in rows], [f[label_key] for f in rows])
    if obs is None:
        return None
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(groups)):
            gid = rng.choice(groups)
            sample.extend(by_g[gid])
        a = auROC([f[score_key] for f in sample], [f[label_key] for f in sample])
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    return {"auroc": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_groups": len(groups)}


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
        sample = [f for f in sample if f["gold_label"] == label]
        a = auROC([f[score_key] for f in sample], [f["consensus_wrong"] for f in sample])
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    return {"auroc": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows), "n_pairs": len(pairs)}


def macro_ci(feats, score_key, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 3):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def macro(rows_):
        vals = []
        for lbl in ("SUPPORTS", "REFUTES"):
            sub = [f for f in rows_ if f["gold_label"] == lbl]
            a = auROC([f[score_key] for f in sub], [f["consensus_wrong"] for f in sub])
            if a is not None:
                vals.append(a)
        return float(np.mean(vals)) if vals else None

    obs = macro(rows)
    if obs is None:
        return None
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        m = macro(sample)
        if m is not None:
            vals.append(m)
    vals = sorted(vals)
    return {"macro": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]}


def paired_bootstrap_diff(feats, key_a, key_b, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 5,
                          label_key="consensus_wrong"):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key_a) is not None and f.get(key_b) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def diff(rows_):
        a = auROC([f[key_a] for f in rows_], [f[label_key] for f in rows_])
        b = auROC([f[key_b] for f in rows_], [f[label_key] for f in rows_])
        return (a - b) if (a is not None and b is not None) else None

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


def risk_at_80(feats, key, coverage=0.8):
    """Error reduction when retaining the lowest-risk `coverage` fraction. Higher=better."""
    rows = [f for f in feats if f.get(key) is not None]
    overall = np.mean([f["consensus_wrong"] for f in rows])
    xs = sorted(rows, key=lambda f: f[key])
    keep = xs[:int(coverage * len(xs))]
    ret = np.mean([f["consensus_wrong"] for f in keep]) if keep else 0.0
    return {"reduction": float(1.0 - ret / overall) if overall > 0 else 0.0,
            "overall_error": float(overall), "retained_error": float(ret), "n": len(rows)}


def risk_at_80_bootstrap(feats, key, coverage=0.8, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 9):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key) is not None]
    overall = np.mean([f["consensus_wrong"] for f in rows])
    if overall == 0:
        return None

    def reduction(rows_):
        xs = sorted(rows_, key=lambda f: f[key])
        keep = xs[:int(coverage * len(xs))]
        ret = np.mean([f["consensus_wrong"] for f in keep]) if keep else 0.0
        return 1.0 - ret / overall

    obs = reduction(rows)
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        vals.append(reduction(sample))
    vals = sorted(vals)
    return {"reduction": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "overall_error": float(overall), "n": len(rows)}


def risk_at_80_paired_diff(feats, key_a, key_b, coverage=0.8, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 11):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key_a) is not None and f.get(key_b) is not None]
    overall = np.mean([f["consensus_wrong"] for f in rows])
    if overall == 0:
        return None
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def reduction(rows_, key):
        xs = sorted(rows_, key=lambda f: f[key])
        keep = xs[:int(coverage * len(xs))]
        ret = np.mean([f["consensus_wrong"] for f in keep]) if keep else 0.0
        return 1.0 - ret / overall

    obs = reduction(rows, key_a) - reduction(rows, key_b)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        vals.append(reduction(sample, key_a) - reduction(sample, key_b))
    vals = sorted(vals)
    return {"diff": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows)}


def permutation_risk(feats, risk_key="risk_bf_q", n=PERM_N, seed=BOOTSTRAP_SEED + 13):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(risk_key) is not None]
    labels = [f["consensus_wrong"] for f in rows]
    obs = auROC([f[risk_key] for f in rows], labels)
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


def spearman(a, b):
    import numpy as np
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / denom) if denom > 0 else None
