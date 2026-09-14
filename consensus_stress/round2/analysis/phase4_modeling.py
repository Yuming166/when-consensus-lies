"""Phase 4: reliability modeling on combined pilot+confirmation features (no new calls)."""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase2_pilot"))
import round2_lib as pl
from analyze import auROC, pair_grouped_bootstrap, paired_bootstrap_diff

ROOT = Path(__file__).resolve().parent
BOOTSTRAP_N = 2000
SEED = 20260913
HC = 0.8


def load_combined() -> list[dict]:
    out = []
    for prefix, ledger in (("", "labels_ledger.json"), ("confirmation", "confirmation_labels_ledger.json")):
        fn = "preoutcome_features.jsonl" if prefix == "" else f"{prefix}_preoutcome_features.jsonl"
        feats = [json.loads(l) for l in open(ROOT.parent / "phase2_pilot" / fn)]
        gold = {it["item_id"]: it["gold_label"]
                for it in json.load(open(ROOT.parent / "phase2_pilot" / ledger))["items"]}
        for f in feats:
            f["gold"] = gold[f["item_id"]]
            f["wrong"] = int((f["consensus"] == "yes") != (f["gold"] == "SUPPORTS"))
            f["risk"] = -f["bf_q"] if f.get("bf_q") is not None else None
            f["consensus_wrong"] = f["wrong"]
            f["disagreement"] = 1.0 - f["agreement"]
        out.extend(feats)
    return [f for f in out if f["agreement"] >= HC]


def risk_at_80_bootstrap(feats, key, n=BOOTSTRAP_N, seed=SEED + 9):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key) is not None]
    overall = np.mean([f["wrong"] for f in rows])
    def reduction(rows_):
        xs = sorted(rows_, key=lambda f: f[key])
        keep = xs[:int(0.8 * len(xs))]
        ret = np.mean([f["wrong"] for f in keep]) if keep else 0.0
        return 1.0 - ret / overall if overall > 0 else 0.0
    obs = reduction(rows)
    by_pair = {}
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


def ece(y_true, y_prob, bins=10):
    y_true = np.asarray(y_true, float); y_prob = np.asarray(y_prob, float)
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0; n = 0
    for i in range(bins):
        m = (y_prob >= edges[i]) & (y_prob < edges[i + 1]) if i < bins - 1 else (y_prob >= edges[i]) & (y_prob <= edges[i + 1])
        if m.sum() == 0:
            continue
        conf = y_prob[m].mean(); acc = y_true[m].mean()
        total += m.sum() * abs(acc - conf); n += m.sum()
    return total / n if n else None


def main() -> None:
    feats = load_combined()
    wrong = sum(1 for f in feats if f["wrong"])
    print(f"combined HC: {len(feats)} items, {wrong} wrong ({wrong/len(feats):.3f})")

    # 5-fold pair-grouped CV for logistic on {bf_paraphrase, bf_reverse}
    rng = random.Random(SEED + 10)
    pairs = sorted({f["pair_id"] for f in feats})
    rng.shuffle(pairs)
    folds = [pairs[i::5] for i in range(5)]
    oof = {}
    for fi, test_pairs in enumerate(folds):
        train = [f for f in feats if f["pair_id"] not in set(test_pairs)]
        test = [f for f in feats if f["pair_id"] in set(test_pairs)]
        Xt = np.array([[f["bf_paraphrase"], f["bf_reverse"]] for f in train], float)
        yt = np.array([f["wrong"] for f in train], float)
        Xe = np.array([[f["bf_paraphrase"], f["bf_reverse"]] for f in test], float)
        w = np.linalg.solve(Xt.T @ Xt + 1e-6 * np.eye(2), Xt.T @ yt)
        for f, x in zip(test, Xe):
            oof[f["item_id"]] = float(1.0 / (1.0 + np.exp(-(x @ w))))
    for f in feats:
        f["logistic_oof"] = oof[f["item_id"]]

    results = {}
    for key in ["risk", "R_PI", "R_sym", "mean_confidence", "disagreement", "conf_dispersion"]:
        results[key] = pair_grouped_bootstrap(feats, key)
    results["logistic_oof"] = pair_grouped_bootstrap(feats, "logistic_oof")

    paired = {k: paired_bootstrap_diff(feats, "risk", k)
              for k in ["R_PI", "R_sym", "mean_confidence", "disagreement", "conf_dispersion", "logistic_oof"]}
    risk80 = {k: risk_at_80_bootstrap(feats, k) for k in
              ["risk", "R_PI", "R_sym", "mean_confidence", "disagreement", "logistic_oof"]}

    # isotonic calibration on OOF split (fit on even pairs, apply to odd) - simple monotone
    pairs_sorted = sorted(pairs)
    even = set(pairs_sorted[::2]); odd = set(pairs_sorted[1::2])
    fit = [f for f in feats if f["pair_id"] in even]
    cal = [f for f in feats if f["pair_id"] in odd]
    from sklearn.isotonic import IsotonicRegression
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(np.array([f["risk"] for f in fit]), np.array([f["wrong"] for f in fit], float))
    for f in cal:
        f["iso_oof"] = float(iso.predict([f["risk"]])[0])
    iso_ece = ece([f["wrong"] for f in cal], [f["iso_oof"] for f in cal])
    # raw ECE is not defined for the raw risk score (negative, not a probability);
    # report ECE only for the calibrated (probability) mapping. A min-max normalized risk
    # ECE is reported for reference.
    rmin, rmax = min(f["risk"] for f in cal), max(f["risk"] for f in cal)
    raw_norm = [(f["risk"] - rmin) / (rmax - rmin) if rmax > rmin else 0.5 for f in cal]
    raw_ece = ece([f["wrong"] for f in cal], raw_norm)
    iso_auroc = auROC([f["iso_oof"] for f in cal], [f["wrong"] for f in cal])

    out = {
        "protocol": "cs-phase4-reliability-20260913",
        "population": {"n": len(feats), "wrong": wrong,
                       "wrong_rate": round(wrong / len(feats), 4)},
        "auroc": results,
        "paired_diff_vs_risk": paired,
        "risk80": risk80,
        "isotonic": {"oof_n": len(cal), "ece_raw_minmax_norm": raw_ece, "ece_iso": iso_ece,
                     "auroc_iso_oof": iso_auroc,
                     "note": "isotonic is monotone in risk; AUROC unchanged by design; ECE reported for calibration"},
        "logistic": {"note": "5-fold pair-grouped CV on {bf_paraphrase, bf_reverse}; OOF AUROC",
                     "auroc": results["logistic_oof"]},
    }
    (ROOT / "phase4_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"auroc": results, "paired": paired, "risk80": risk80,
                      "isotonic": out["isotonic"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
