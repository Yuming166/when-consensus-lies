from __future__ import annotations
import csv
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ("qwen35", "deepseek_v41")
METHOD_KEYS = ("raw", "curve", "raw_plus_arithmetic44",
               "drop_worldwise_alignment", "drop_cross_world_consistency",
               "drop_question_operation_cues")

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_npz(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k].copy() for k in z.files}

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def views(f):
    G, raw17, curve, A = (f[k] for k in ("G96", "raw17", "Curve33", "Arithmetic44"))
    raw = np.concatenate([G, curve[:, :16], curve[:, [18, 17]]], axis=1)
    ci = [i for i in range(33) if i not in (16, 24, 25, 30)]
    curve_view = np.concatenate([G, curve[:, ci]], axis=1)
    mats = {
        "raw": raw.copy(),
        "curve": curve_view.copy(),
        "raw_plus_arithmetic44": np.concatenate([raw, A], axis=1),
        "drop_worldwise_alignment": np.concatenate([raw, A[:, 24:44]], axis=1),
        "drop_cross_world_consistency": np.concatenate([raw, A[:, :24], A[:, 40:44]], axis=1),
        "drop_question_operation_cues": np.concatenate([raw, A[:, :40]], axis=1),
    }
    return mats

report = {"status": "PASS", "checks": {}, "tracks": {}}
schemas = json.loads((ROOT / "schemas/feature_schema.json").read_text())
for block, dim in (("G96", 96), ("raw17", 17), ("Curve33", 33), ("Arithmetic44", 44)):
    require(len(schemas[block]["feature_names"]) == dim, f"schema dimension mismatch: {block}")
report["checks"]["schema_dimensions_and_order"] = True

track_ids = {}
for track in TRACKS:
    f = load_npz(ROOT / f"data/{track}_features_label_blind.npz")
    labels = read_csv(ROOT / f"labels/{track}_labels.csv")
    coverage = read_csv(ROOT / f"coverage/{track}_attempted_coverage.csv")
    folds = read_csv(ROOT / f"data/{track}_folds.csv")
    ref = load_npz(ROOT / f"reference/oof/{track}_oof_scores_label_blind.npz")

    ids = f["item_ids"].astype(str)
    groups = f["groups"].astype(str)
    fold = f["outer_fold"].astype(int)
    n = len(ids)
    require(len(set(ids)) == n, f"{track}: duplicate strict ID")
    require(f["G96"].shape == (n, 96), f"{track}: G96 shape")
    require(f["raw17"].shape == (n, 17), f"{track}: Raw17 shape")
    require(f["Curve33"].shape == (n, 33), f"{track}: Curve33 shape")
    require(f["Arithmetic44"].shape == (n, 44), f"{track}: Arithmetic44 shape")
    require(np.array_equal(f["raw17"], f["Curve33"][:, :17]), f"{track}: Raw17/Curve33 prefix")
    for key in ("G96", "raw17", "Curve33", "Arithmetic44"):
        require(np.isfinite(f[key]).all(), f"{track}: nonfinite {key}")
    require(set(np.unique(fold)) == set(range(5)), f"{track}: missing fold")
    for g in set(groups):
        require(len(set(fold[groups == g])) == 1, f"{track}: group crosses folds")
    mats = views(f)
    expected_dims = {
        "raw": 114, "curve": 125, "raw_plus_arithmetic44": 158,
        "drop_worldwise_alignment": 134, "drop_cross_world_consistency": 142,
        "drop_question_operation_cues": 154,
    }
    require({k: v.shape[1] for k, v in mats.items()} == expected_dims, f"{track}: view dimensions")
    require(all(np.isfinite(x).all() for x in mats.values()), f"{track}: nonfinite constructed view")
    mv = list(mats.values())
    require(all(not np.shares_memory(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))),
            f"{track}: constructed views share writable memory")
    require(all(not np.shares_memory(f[a], f[b]) for i, a in enumerate(("G96","raw17","Curve33","Arithmetic44"))
                for b in ("G96","raw17","Curve33","Arithmetic44")[i + 1:]),
            f"{track}: component arrays share memory")

    label_map = {x["item_id"]: x for x in labels}
    require(len(label_map) == len(labels), f"{track}: duplicate label ID")
    y = []
    for iid in ids:
        r = label_map.get(iid)
        require(r is not None and r["label_status"] == "KNOWN" and r["error"] in ("0","1"),
                f"{track}: missing strict label {iid}")
        require(r["source_group"] == groups[np.where(ids == iid)[0][0]], f"{track}: label group mismatch")
        require(int(r["outer_fold"]) == int(fold[np.where(ids == iid)[0][0]]), f"{track}: label fold mismatch")
        y.append(int(r["error"]))
    y = np.asarray(y, dtype=np.int64)
    require(set(np.unique(y)) == {0,1}, f"{track}: missing class")

    fold_map = {r["item_id"]: (r["source_group"], int(r["outer_fold"])) for r in folds}
    require(len(fold_map) == n and set(fold_map) == set(ids), f"{track}: fold manifest coverage")
    require(all(fold_map[i] == (str(groups[j]), int(fold[j])) for j,i in enumerate(ids)),
            f"{track}: fold manifest order/content mismatch")

    coverage_map = {r["item_id"]: r for r in coverage}
    require(len(coverage_map) == len(coverage), f"{track}: duplicate coverage ID")
    require(set(ids).issubset(coverage_map), f"{track}: strict IDs absent from attempted coverage")
    require(all(coverage_map[i]["strict_eligible"].lower() == "true" for i in ids), f"{track}: strict flag")
    require(all(coverage_map[i]["label_status"] == "KNOWN" for i in ids), f"{track}: strict label coverage")
    require(all(coverage_map[i]["original_response_record_sha256"] == label_map[i]["original_response_record_sha256"]
                for i in ids), f"{track}: label/original response hash mismatch")
    for r in coverage:
        for w in ("original", "positive", "negative"):
            state = r[f"{w}_state"]
            require(state != "" or state == "", f"{track}: state field malformed")
            if not state:
                require(state == "", f"{track}: malformed missing status")

    require(np.array_equal(ref["item_ids"].astype(str), ids), f"{track}: OOF ID order")
    require(np.array_equal(ref["source_group"].astype(str), groups), f"{track}: OOF group order")
    require(np.array_equal(ref["outer_fold"].astype(int), fold), f"{track}: OOF fold order")
    for key in METHOD_KEYS:
        require(ref[key].shape == (n,) and np.isfinite(ref[key]).all(), f"{track}: OOF {key}")
    track_ids[track] = {iid: (groups[i], int(fold[i]), int(y[i])) for i,iid in enumerate(ids)}
    report["tracks"][track] = {
        "attempted": len(coverage), "strict": n, "groups": len(set(groups)),
        "errors": int(y.sum()), "correct": int((1-y).sum()),
        "attempted_label_known": sum(r["label_status"] == "KNOWN" for r in labels),
        "attempted_label_unknown": sum(r["label_status"] != "KNOWN" for r in labels),
        "fold_support": {str(k): {"items": int((fold == k).sum()), "errors": int(y[fold == k].sum()),
                                  "correct": int((1-y[fold == k]).sum())} for k in range(5)},
    }

common = set(track_ids["qwen35"]) & set(track_ids["deepseek_v41"])
require(set(track_ids["deepseek_v41"]).issubset(track_ids["qwen35"]), "DeepSeek strict cohort is not Qwen subset")
require(all(track_ids["qwen35"][i][:2] == track_ids["deepseek_v41"][i][:2] for i in common),
        "shared cross-track group/fold mismatch")
report["checks"]["unique_ids_groups_folds_features_memory"] = True
report["checks"]["strict_label_response_generation_binding"] = True
report["checks"]["label_free_oof_alignment"] = True
report["checks"]["cross_track_subset_and_folds"] = True
report["checks"]["no_status_backfilled"] = True
report["cross_track_common_strict_ids"] = len(common)
report["qwen_strict_minus_deepseek"] = len(track_ids["qwen35"]) - len(common)
report["deepseek_strict_minus_qwen"] = len(track_ids["deepseek_v41"]) - len(common)
(ROOT / "audit/VALIDATION.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
print(json.dumps(report, ensure_ascii=False, indent=2))
