from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
import platform
import time
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ("qwen35", "deepseek_v41")
METHODS = ("raw", "curve", "raw_plus_arithmetic44",
           "drop_worldwise_alignment", "drop_cross_world_consistency",
           "drop_question_operation_cues")

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_npz(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k].copy() for k in z.files}

def make_views(f):
    G, raw17, curve, A = (f[k] for k in ("G96", "raw17", "Curve33", "Arithmetic44"))
    raw = np.concatenate([G, curve[:, :16], curve[:, [18, 17]]], axis=1)
    ci = [i for i in range(33) if i not in (16, 24, 25, 30)]
    curve_view = np.concatenate([G, curve[:, ci]], axis=1)
    return {
        "raw": raw.copy(),
        "curve": curve_view.copy(),
        "raw_plus_arithmetic44": np.concatenate([raw, A], axis=1),
        "drop_worldwise_alignment": np.concatenate([raw, A[:, 24:44]], axis=1),
        "drop_cross_world_consistency": np.concatenate([raw, A[:, :24], A[:, 40:44]], axis=1),
        "drop_question_operation_cues": np.concatenate([raw, A[:, :40]], axis=1),
    }

def main():
    ap = argparse.ArgumentParser(description="Fixed, offline source-group OOF refit for the two PECR tracks.")
    ap.add_argument("--outdir", required=True, help="New output directory; existing paths are refused.")
    ap.add_argument("--verify-exact", action="store_true", help="Require exact prediction equality to released reference OOF.")
    args = ap.parse_args()
    out = Path(args.outdir)
    if not out.is_absolute():
        out = (ROOT / out).resolve()
    if out.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {out}")
    out.mkdir(parents=True)
    params = json.loads((ROOT / "protocol/HGB_PARAMS.json").read_text())["parameters"]
    started = time.time()
    all_results = {}
    track_reports = {}

    for track in TRACKS:
        f = load_npz(ROOT / f"data/{track}_features_label_blind.npz")
        ids = f["item_ids"].astype(str)
        groups = f["groups"].astype(str)
        folds = f["outer_fold"].astype(int)
        labels = read_csv(ROOT / f"labels/{track}_labels.csv")
        label_map = {r["item_id"]: r for r in labels}
        y = np.asarray([int(label_map[i]["error"]) for i in ids], dtype=np.int64)
        Xs = make_views(f)
        ref = load_npz(ROOT / f"reference/oof/{track}_oof_scores_label_blind.npz")
        pred = {name: np.full(len(ids), np.nan, dtype=np.float64) for name in METHODS}
        fit_count = 0
        for fold in range(5):
            train = np.flatnonzero(folds != fold)
            test = np.flatnonzero(folds == fold)
            assert not set(groups[train]) & set(groups[test])
            assert set(y[train]) == set(y[test]) == {0, 1}
            for name in METHODS:
                model = HistGradientBoostingClassifier(**params)
                with threadpool_limits(limits=1):
                    model.fit(Xs[name][train], y[train])
                    score = model.predict_proba(Xs[name][test])[:, 1]
                if model.n_iter_ != 250:
                    raise RuntimeError(f"{track}/{name}/fold={fold}: expected 250 iterations, got {model.n_iter_}")
                pred[name][test] = score
                fit_count += 1
        if any(not np.isfinite(p).all() for p in pred.values()):
            raise RuntimeError(f"{track}: incomplete or nonfinite OOF predictions")
        exact = {}
        max_abs_error = {}
        for name in METHODS:
            exact[name] = bool(np.array_equal(pred[name], ref[name]))
            max_abs_error[name] = float(np.max(np.abs(pred[name] - ref[name])))
        if args.verify_exact and not all(exact.values()):
            raise RuntimeError(f"{track}: reference mismatch; see exact comparison in run report")

        metrics = {}
        for name, score in pred.items():
            metrics[name] = {
                "auroc": float(roc_auc_score(y, score)),
                "auprc": float(average_precision_score(y, score)),
            }
        all_results[track] = {"item_ids": ids, "source_group": groups, "outer_fold": folds, **pred}
        track_reports[track] = {
            "items": len(ids), "groups": len(set(groups)), "errors": int(y.sum()),
            "correct": int((1-y).sum()), "fits": fit_count,
            "reference_exact_by_view": exact, "reference_max_abs_error_by_view": max_abs_error,
            "metrics_from_refit_oof": metrics,
        }

    oof_path = out / "OOF_RETRAINED_LABEL_FREE.npz"
    np.savez_compressed(oof_path, **{f"{track}_{key}": value for track, data in all_results.items() for key, value in data.items()})
    report = {
        "status": "PASS" if all(all(v["reference_exact_by_view"].values()) for v in track_reports.values()) else "COMPLETED_WITH_REFERENCE_DIFFERENCES",
        "protocol": "fixed HGB, saved five source-group folds, no tuning",
        "python": platform.python_version(),
        "runtime": {p: __import__("importlib.metadata", fromlist=["version"]).version(p)
                    for p in ("numpy", "scipy", "scikit-learn", "threadpoolctl")},
        "parameters": params, "tracks": track_reports,
        "total_fits": sum(x["fits"] for x in track_reports.values()),
        "elapsed_seconds": time.time() - started,
        "oof_sha256": __import__("hashlib").sha256(oof_path.read_bytes()).hexdigest(),
        "no_model_api_calls": True,
    }
    (out / "REFIT_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
