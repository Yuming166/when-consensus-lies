#!/usr/bin/env python3
"""Task 3 (Agent W3): false-positive decomposition - correct-but-rigid panels.

Reviewer concern: "correct consensus also stays unchanged under reversal." We isolate
the panels that are CORRECT yet rigid under natural reversal (mirror-wrong) and test
whether removal / lambda axes separate them from TRULY wrong panels:
  - removal axis: rem_flip_rate (full cohort, both models)
  - lambda axis: per-item phase-3 continuous stress features (Qwen 120-pair subset)

Rigid definitions (both reported):
  - consensus-rigid: rev_flip_rate <= 0.4 (majority unchanged under reversal)
  - fully-rigid   : rev_flip_rate == 0.0 (no agent flips)
All statistics are exploratory / post-hoc robustness analysis (plan §16).
"""
from __future__ import annotations
import json
import random
from pathlib import Path

import numpy as np

import stress_common as sc
import lambda_features as lf

OUT = sc.HERE / "stress_profile_results.json"


def rigid_mask(feats: list[dict], thr: float) -> dict[str, bool]:
    return {f["cqid"]: (f["rev_flip_rate"] <= thr) for f in feats}


def separation_bootstrap(feats: list[dict], key: str, rigid: dict[str, bool],
                         seed: int) -> dict:
    """AUROC separating correct-rigid (0) from wrong-rigid (1) on `key`.

    Pair-grouped bootstrap over the union of pairs present in either rigid group.
    """
    rng = random.Random(seed)
    pos = [f for f in feats if rigid.get(f["cqid"]) and f["consensus_wrong"]]
    neg = [f for f in feats if rigid.get(f["cqid"]) and not f["consensus_wrong"]]
    rows = [f for f in pos + neg if f.get(key) is not None]
    if not rows or not pos or not neg:
        return None
    for f in rows:
        f["_sep"] = int(f["consensus_wrong"])
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def auroc(rows_: list[dict]) -> float | None:
        p = sum(1 for f in rows_ if f["_sep"] == 1)
        n = sum(1 for f in rows_ if f["_sep"] == 0)
        if p == 0 or n == 0:
            return None
        return sc.al.auROC([f[key] for f in rows_], [f["_sep"] for f in rows_])

    obs = auroc(rows)
    vals = []
    for _ in range(sc.BOOTSTRAP_N):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        v = auroc(sample)
        if v is not None:
            vals.append(v)
    vals = sorted(vals)
    return {"auroc": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n_correct_rigid": len(neg), "n_wrong_rigid": len(pos), "n_pairs": len(pairs)}


def group_stats(feats: list[dict], rigid: dict[str, bool]) -> dict:
    groups = {
        "correct_rigid": [f for f in feats if rigid.get(f["cqid"]) and not f["consensus_wrong"]],
        "wrong_rigid": [f for f in feats if rigid.get(f["cqid"]) and f["consensus_wrong"]],
        "correct_responsive": [f for f in feats if not rigid.get(f["cqid"]) and not f["consensus_wrong"]],
        "wrong_responsive": [f for f in feats if not rigid.get(f["cqid"]) and f["consensus_wrong"]],
    }
    out = {}
    for gname, g in groups.items():
        out[gname] = {"n": len(g)}
        for k in ("rem_flip_rate", "para_flip_rate", "rev_flip_rate"):
            vals = [f[k] for f in g if f.get(k) is not None]
            out[gname][k] = round(float(np.mean(vals)), 4) if vals else None
    return out


def false_positive_model(model_key: str, population: str, thr: float, thr_name: str) -> dict:
    hc_only = population == "hc"
    feats = sc.load_model(model_key, hc_only=hc_only)
    rigid = rigid_mask(feats, thr)
    rec = {"model": sc.MODEL_FILES[model_key]["display"], "population": population,
           "rigid_definition": thr_name, "rigid_threshold": thr,
           "n_items": len(feats),
           "n_rigid": sum(rigid.values()),
           "groups": group_stats(feats, rigid)}
    rec["separation_rem"] = separation_bootstrap(feats, "rem_flip_rate", rigid,
                                                 seed=sc.POSTHOC_BASE + 500)
    rec["separation_para"] = separation_bootstrap(feats, "para_flip_rate", rigid,
                                                  seed=sc.POSTHOC_BASE + 501)
    # combined non-reversal profile: rem + para
    for f in feats:
        f["_rem_para_sep"] = f["rem_flip_rate"] + f["para_flip_rate"]
    rec["separation_rem_para"] = separation_bootstrap(feats, "_rem_para_sep", rigid,
                                                      seed=sc.POSTHOC_BASE + 502)
    return rec


def lambda_subset_analysis() -> dict:
    """Qwen phase-3 120-pair subset: separation of rigid groups on lambda stress features."""
    feats = sc.load_model("qwen", hc_only=True)
    by_cqid = {f["cqid"]: f for f in feats}
    per_item = lf.build_per_item()
    rigid_cons = rigid_mask(feats, 0.4)
    rigid_full = rigid_mask(feats, 0.0)
    out = {"model": sc.MODEL_FILES["qwen"]["display"],
           "subset_items": len(per_item),
           "hc_subset_items": sum(1 for cqid in per_item if cqid in by_cqid)}
    for thr_name, thr, mask in (("consensus-rigid", 0.4, rigid_cons), ("fully-rigid", 0.0, rigid_full)):
        rows = []
        for cqid, row in per_item.items():
            f = by_cqid.get(cqid)
            if f is None or not mask.get(cqid):
                continue
            r = {"cqid": cqid, "pair_id": f["pair_id"], "wrong": f["consensus_wrong"],
                 "rem_flip": f["rem_flip_rate"], "para_flip": f["para_flip_rate"],
                 "rem_para_sep": f["rem_flip_rate"] + f["para_flip_rate"],
                 "rev_area": row["reversal_stress_area"],
                 "rem_area": row["removal_stress_area"],
                 "rev_rr": row["reversal_robustness_radius"],
                 "rem_rr": row["removal_robustness_radius"],
                 "curve_rev": row["curve_reversal"], "curve_rem": row["curve_removal"]}
            rows.append(r)
        entry = {"rigid_definition": thr_name, "n_correct_rigid": sum(1 for r in rows if not r["wrong"]),
                 "n_wrong_rigid": sum(1 for r in rows if r["wrong"])}
        for k in ("rev_area", "rem_area", "rev_rr", "rem_rr", "rem_flip", "para_flip"):
            c = [r[k] for r in rows if not r["wrong"] and r[k] is not None]
            w = [r[k] for r in rows if r["wrong"] and r[k] is not None]
            entry[f"mean_{k}_correct"] = round(float(np.mean(c)), 4) if c else None
            entry[f"mean_{k}_wrong"] = round(float(np.mean(w)), 4) if w else None
        # separation AUROC on removal flip rate (full HC, same mask)
        sep = separation_bootstrap(feats, "rem_flip_rate", mask, seed=sc.POSTHOC_BASE + 600)
        entry["separation_rem_flip_rate"] = sep
        # separation on lambda removal stress area over the subset (pair-grouped CI)
        entry["separation_rem_area"] = separation_bootstrap_on_rows(
            rows, "rem_area", seed=sc.POSTHOC_BASE + 601)
        entry["separation_rev_area"] = separation_bootstrap_on_rows(
            rows, "rev_area", seed=sc.POSTHOC_BASE + 602)
        entry["separation_rem_para"] = separation_bootstrap_on_rows(
            rows, "rem_para_sep", seed=sc.POSTHOC_BASE + 603)
        # curves by group
        def curve_mean(group_rows, key, i):
            vals = [r[key][i] for r in group_rows if r[key][i] is not None]
            return round(float(np.mean(vals)), 4) if vals else None
        c_rows = [r for r in rows if not r["wrong"]]
        w_rows = [r for r in rows if r["wrong"]]
        entry["curve_reversal_correct"] = [curve_mean(c_rows, "curve_rev", i) for i in range(6)]
        entry["curve_reversal_wrong"] = [curve_mean(w_rows, "curve_rev", i) for i in range(6)]
        entry["curve_removal_correct"] = [curve_mean(c_rows, "curve_rem", i) for i in range(6)]
        entry["curve_removal_wrong"] = [curve_mean(w_rows, "curve_rem", i) for i in range(6)]
        out[thr_name] = entry
    return out



def separation_bootstrap_on_rows(rows: list[dict], key: str, seed: int) -> dict | None:
    """Pair-grouped bootstrap AUROC separating correct-rigid (0) from wrong-rigid (1)
    on `key`, restricted to the given rows (e.g., the phase-3 lambda subset)."""
    rng = random.Random(seed)
    rows = [r for r in rows if r.get(key) is not None]
    if not any(r["wrong"] for r in rows) or not any(not r["wrong"] for r in rows):
        return None
    by_pair: dict[str, list[dict]] = {}
    for r in rows:
        by_pair.setdefault(r["pair_id"], []).append(r)
    pairs = sorted(by_pair)

    def auroc(rows_: list[dict]) -> float | None:
        p = sum(1 for r in rows_ if r["wrong"])
        n = sum(1 for r in rows_ if not r["wrong"])
        if p == 0 or n == 0:
            return None
        return sc.al.auROC([r[key] for r in rows_], [1 if r["wrong"] else 0 for r in rows_])

    obs = auroc(rows)
    vals = []
    for _ in range(sc.BOOTSTRAP_N):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        v = auroc(sample)
        if v is not None:
            vals.append(v)
    vals = sorted(vals)
    return {"auroc": obs, "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n_correct_rigid": sum(1 for r in rows if not r["wrong"]),
            "n_wrong_rigid": sum(1 for r in rows if r["wrong"]), "n_pairs": len(pairs)}


def main() -> None:
    results = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    section = {"protocol": "round7-w3-stress-profile-task3-false-positive-decomposition",
               "seed_base": sc.SEED_FROZEN, "posthoc_seed_base": sc.POSTHOC_BASE,
               "bootstrap_n": sc.BOOTSTRAP_N,
               "status": "exploratory / post-hoc robustness analysis (plan §16)",
               "models": [], "lambda_axis": None}
    for model_key in ("qwen", "ling"):
        for population in ("hc", "all"):
            for thr, name in ((0.4, "consensus-rigid rev<=0.4"), (0.0, "fully-rigid rev==0")):
                section["models"].append(false_positive_model(model_key, population, thr, name))
    section["lambda_axis"] = lambda_subset_analysis()
    results["task3_false_positive"] = section
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(section, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
