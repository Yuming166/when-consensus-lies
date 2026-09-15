#!/usr/bin/env python3
"""Task 2 (Agent W3): multi-axis risk representations vs RS_q / BF_q on the HC subset.

Constructs label-free, fixed-weight multi-axis risk scores from frozen features:
  - risk_rev_rem      = (1 - rev_flip_rate) + rem_flip_rate
  - risk_rev_rem_para = (1 - rev_flip_rate) + rem_flip_rate + para_flip_rate
  - risk_rsq_rem      = -BF_q + rem_flip_rate            (frozen RS_q + removal axis)
  - risk_z3           = z(1-rev) + z(rem) + z(para)      (z-scored on HC, label-free)
  - risk_rem_para     = rem_flip_rate + para_flip_rate   (non-reversal axes reference)
  - logistic_oof3     = pair-grouped 5-fold OOF logistic on {risk_rev, risk_rem,
                        risk_para} (post-hoc fitted ceiling; labels used only for
                        out-of-fold evaluation)

Metrics on HC (agreement >= 0.8): AUROC, Risk@80, paired AUROC diff vs RS_q,
paired Risk@80 diff vs RS_q, Spearman vs RS_q. Pair-grouped bootstrap 95% CIs.
All statistics are exploratory / post-hoc robustness analysis (plan §16).
"""
from __future__ import annotations
import json
import random
from pathlib import Path

import numpy as np

import stress_common as sc

OUT = sc.HERE / "stress_profile_results.json"
COMBO_SPECS = [
    ("risk_rev_rem", "reversal rigidity + removal instability (fixed 1:1)"),
    ("risk_rev_rem_para", "reversal + removal + paraphrase instability (fixed 1:1:1)"),
    ("risk_rsq_rem", "RS_q + removal instability (fixed 1:1)"),
    ("risk_z3", "z-scored reversal + removal + paraphrase (equal weights)"),
    ("risk_rem_para", "removal + paraphrase instability only (reference)"),
]


def add_risk_keys(feats: list[dict]) -> None:
    # fixed-weight label-free combos on frozen features
    for f in feats:
        f["risk_rev_rem"] = f["risk_rev"] + f["risk_rem"]
        f["risk_rev_rem_para"] = f["risk_rev"] + f["risk_rem"] + f["risk_para"]
        f["risk_rsq_rem"] = f["risk_bf_q"] + f["risk_rem"]
        f["risk_rem_para"] = f["risk_rem"] + f["risk_para"]
    # z-scored equal-weight combo (z computed on the HC cohort; label-free transform)
    def z(a): return (a - a.mean()) / (a.std() + 1e-12)
    zrev = z(np.array([f["risk_rev"] for f in feats], dtype=float))
    zrem = z(np.array([f["risk_rem"] for f in feats], dtype=float))
    zpara = z(np.array([f["risk_para"] for f in feats], dtype=float))
    for f, a, b, c in zip(feats, zrev, zrem, zpara):
        f["risk_z3"] = float(a + b + c)


def logistic_oof3(feats: list[dict], seed: int) -> None:
    """Pair-grouped 5-fold OOF logistic on {risk_rev, risk_rem, risk_para}."""
    from sklearn.linear_model import LogisticRegression
    rng = random.Random(seed)
    rows = [f for f in feats
            if f.get("risk_rev") is not None and f.get("risk_rem") is not None
            and f.get("risk_para") is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    rng.shuffle(pairs)
    folds = [pairs[i::5] for i in range(5)]
    oof: dict[str, float] = {}
    for fi in range(5):
        tr = [p for j in range(5) if j != fi for p in folds[j]]
        te = folds[fi]
        Xtr = np.array([[f["risk_rev"], f["risk_rem"], f["risk_para"]]
                        for p in tr for f in by_pair[p]])
        ytr = np.array([f["consensus_wrong"] for p in tr for f in by_pair[p]])
        clf = LogisticRegression(max_iter=2000)
        clf.fit(Xtr, ytr)
        for p in te:
            for f in by_pair[p]:
                oof[f["cqid"]] = float(clf.predict_proba(
                    np.array([[f["risk_rev"], f["risk_rem"], f["risk_para"]]]))[:, 1][0])
    for f in rows:
        f["logistic_oof3"] = oof.get(f["cqid"])


def combo_metrics(feats: list[dict], key: str, rsq_key: str, seed: int) -> dict:
    return {
        "auroc": sc.auroc_ci(feats, key, seed=seed + 10),
        "risk80": sc.risk80_ci(feats, key, seed=seed + 11),
        "paired_auroc_diff_vs_rsq": sc.paired_auroc_diff(feats, key, rsq_key, seed=seed + 12),
        "paired_risk80_diff_vs_rsq": sc.paired_risk80_diff(feats, key, rsq_key, seed=seed + 13),
        "spearman_vs_rsq": sc.spearman_ci(feats, key, rsq_key, seed=seed + 14),
    }


def main() -> None:
    results = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    section = {"protocol": "round7-w3-stress-profile-task2-multiaxis-vs-rsq",
               "seed_base": sc.SEED_FROZEN, "posthoc_seed_base": sc.POSTHOC_BASE,
               "bootstrap_n": sc.BOOTSTRAP_N, "hc_threshold": sc.HC_THRESHOLD,
               "status": "exploratory / post-hoc robustness analysis (plan §16)",
               "combos": []}
    for model_key in ("qwen", "ling"):
        feats = sc.load_model(model_key, hc_only=True)
        add_risk_keys(feats)
        logistic_oof3(feats, seed=sc.POSTHOC_BASE + 200)
        model_rec = {
            "model": sc.MODEL_FILES[model_key]["display"],
            "hc": {"n_items": len(feats),
                   "n_pairs": len({f["pair_id"] for f in feats}),
                   "wrong": sum(f["consensus_wrong"] for f in feats)},
            "rs_q": {
                "auroc": sc.auroc_ci(feats, "risk_bf_q", seed=sc.SEED_FROZEN),
                "risk80": sc.risk80_ci(feats, "risk_bf_q", seed=sc.SEED_FROZEN + 9),
            },
            "axes": {},
            "combos": {},
        }
        for key, name in COMBO_SPECS:
            model_rec["combos"][key] = {
                "name": name,
                **combo_metrics(feats, key, "risk_bf_q", sc.POSTHOC_BASE + 300),
            }
        # logistic OOF ceiling
        model_rec["combos"]["logistic_oof3"] = {
            "name": "OOF logistic on {rev, rem, para} (post-hoc fitted ceiling)",
            **combo_metrics(feats, "logistic_oof3", "risk_bf_q", sc.POSTHOC_BASE + 400),
        }
        section["combos"].append(model_rec)
    results["task2_multiaxis"] = section
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(section, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
