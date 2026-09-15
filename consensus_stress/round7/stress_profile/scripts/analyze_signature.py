#!/usr/bin/env python3
"""Task 1 (Agent W3): removal-axis reversal signature on the FULL 600-item cohort.

Verifies, on the whole frozen cohort (Qwen3.5-4B and Ling-3.0-tiny), that wrong
consensus is (a) MORE unstable under evidence removal (higher rem_flip_rate) and
(b) MORE rigid under natural reversal (lower rev_flip_rate). phase3 verified this on
a 120-pair / 225-HC subset of Qwen only; here we use all 600 items per model plus the
HC subset as a sensitivity, with pair-grouped bootstrap 95% CIs on the flip-rate gap.

All statistics here are exploratory / post-hoc robustness analysis (plan §16): the
flip-rate means, gaps, and axis AUROCs were not part of the frozen gate protocol.
"""
from __future__ import annotations
import json
from pathlib import Path

import stress_common as sc

OUT = sc.HERE / "stress_profile_results.json"


def axis_signature(model_key: str, population: str) -> dict:
    hc_only = population == "hc"
    feats = sc.load_model(model_key, hc_only=hc_only)
    rec = {"model": sc.MODEL_FILES[model_key]["display"], "population": population,
           "n_items": len(feats), "n_pairs": len({f["pair_id"] for f in feats}),
           "n_correct": sum(1 for f in feats if not f["consensus_wrong"]),
           "n_wrong": sum(1 for f in feats if f["consensus_wrong"])}
    for axis, key, risk_key in (
            ("reversal_rigidity", "rev_flip_rate", "risk_rev"),
            ("removal_instability", "rem_flip_rate", "risk_rem"),
            ("paraphrase_instability", "para_flip_rate", "risk_para"),
            ("synthetic_reverse_flip", "synth_flip_rate", "risk_synth")):
        c = [f[key] for f in feats if not f["consensus_wrong"]]
        w = [f[key] for f in feats if f["consensus_wrong"]]
        gap = sc.group_mean_bootstrap(feats, key, seed=sc.POSTHOC_BASE + 1)
        a = sc.auroc_ci(feats, risk_key, seed=sc.POSTHOC_BASE + 2)
        rec[axis] = {
            "mean_correct": round(float(np_mean(c)), 4),
            "mean_wrong": round(float(np_mean(w)), 4),
            "gap_correct_minus_wrong": gap["diff_correct_minus_wrong"],
            "gap_ci": gap["ci"],
            "auroc_risk_axis": a,
        }
    return rec


def np_mean(x) -> float:
    import numpy as np
    return float(np.mean(x))


def main() -> None:
    results = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    section = {"protocol": "round7-w3-stress-profile-task1-signature",
               "seed_base": sc.SEED_FROZEN, "posthoc_seed_base": sc.POSTHOC_BASE,
               "bootstrap_n": sc.BOOTSTRAP_N,
               "status": "exploratory / post-hoc robustness analysis (plan §16)",
               "models": []}
    for model_key in ("qwen", "ling"):
        for population in ("all", "hc"):
            section["models"].append(axis_signature(model_key, population))
    results["task1_signature"] = section
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(section, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
