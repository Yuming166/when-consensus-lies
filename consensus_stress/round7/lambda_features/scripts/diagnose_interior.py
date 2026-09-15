#!/usr/bin/env python3
"""W4 (round7): interior-shape diagnostic for the reversal lambda curve.

The lambda=1 anchor of reversal stress-area IS rev_flip_rate (same frozen reverse
records). To test whether the curve's interior (lambda in [0.2, 0.8]) carries any
predictive signal beyond that endpoint, this script computes:
  - flip probability at lambda=0.8 alone  (plain AUROC)
  - interior area (trapezoid over [0.2,0.8], excluding the 0.8->1.0 segment that
    contains rev_flip_rate)                (plain AUROC + incremental over rev_flip_rate)
Both are post-hoc/exploratory, 225-item HC subset scope. No new model calls.
Outputs: interior_diagnostic.json
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

import numpy as np

CS = Path(__file__).resolve().parents[3]
R3 = CS / "round3"
HERE = Path(__file__).resolve().parent.parent
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))
import analysis_lib as al

SEED_BASE = 20_260_913
OFFSET_START = 600
HC_THRESHOLD = 0.8
BOOTSTRAP_N = 2000


def main():
    rows = [json.loads(l) for l in (HERE / "features_phase3_lambda.jsonl").read_text(encoding="utf-8").splitlines() if l]
    hc = [r for r in rows if r["agreement"] >= HC_THRESHOLD]

    # interior area over lambdas [0.2,0.4,0.6,0.8] (trapezoid; excludes the 0.8->1.0
    # segment that carries rev_flip_rate / the lambda=1 anchor)
    for r in hc:
        c = r.get("reversal_curve") or {}
        vals = [c.get(f"flip_{int(lam*10)}") for lam in (0.2, 0.4, 0.6, 0.8)]
        if any(v is None for v in vals):
            r["reversal_interior_area"] = None
            r["reversal_flip_08"] = None
            continue
        # trapezoid from 0 -> 0.2 -> 0.4 -> 0.6 -> 0.8 (flip at 0 is 0 by construction)
        area = 0.5 * (0.0 + vals[0]) * 0.2 + 0.5 * (vals[0] + vals[1]) * 0.2 \
            + 0.5 * (vals[1] + vals[2]) * 0.2 + 0.5 * (vals[2] + vals[3]) * 0.2
        r["reversal_interior_area"] = float(area)
        r["reversal_flip_08"] = float(vals[3])
        r["risk_rev_interior_area"] = -float(area)
        r["risk_rev_flip_08"] = -float(vals[3])

    offset = OFFSET_START
    res = {
        "protocol": "round7-W4-interior-shape-diagnostic",
        "status": "exploratory / post-hoc; 225-item HC subset (119 pairs, 22 wrong); Qwen",
        "note": "lambda=1 anchor of reversal stress-area == rev_flip_rate (same reverse records). "
                "Interior area excludes that endpoint and tests only curve-shape signal.",
        "plain_auroc": {
            "reversal_flip_at_0.8": al.group_bootstrap(hc, "risk_rev_flip_08", seed=SEED_BASE + offset),
            "reversal_interior_area_[0.2,0.8]": al.group_bootstrap(hc, "risk_rev_interior_area", seed=SEED_BASE + offset + 1),
        },
        "incremental_over_rev_flip_rate": {},
    }
    offset += 2
    rng = random.Random(SEED_BASE + offset)
    for key, name in (("risk_rev_interior_area", "reversal interior area [0.2,0.8]"),
                      ("risk_rev_flip_08", "reversal flip at lambda=0.8")):
        rows_ = [r for r in hc if r.get(key) is not None and r.get("rev_flip_rate") is not None]
        by_pair = {}
        for r in rows_:
            by_pair.setdefault(r["pair_id"], []).append(r)
        pairs = sorted(by_pair)

        def auroc_resid(sample):
            x = np.array([r[key] for r in sample], dtype=float)
            b = np.array([r["rev_flip_rate"] for r in sample], dtype=float)
            y = np.array([r["consensus_wrong"] for r in sample], dtype=float)
            if np.std(b) == 0.0 or np.std(x) == 0.0:
                return None
            slope, intercept = np.polyfit(b, x, 1)
            return al.auROC((x - (slope * b + intercept)).tolist(), y.tolist())

        obs = auroc_resid(rows_)
        vals = []
        for _ in range(BOOTSTRAP_N):
            sample = []
            for _ in range(len(pairs)):
                sample.extend(by_pair[rng.choice(pairs)])
            a = auroc_resid(sample)
            if a is not None:
                vals.append(a)
        vals = sorted(vals)
        res["incremental_over_rev_flip_rate"][key] = {
            "name": name,
            "auroc": obs,
            "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n": len(rows_), "n_pairs": len(pairs),
        }
    out = HERE / "interior_diagnostic.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
