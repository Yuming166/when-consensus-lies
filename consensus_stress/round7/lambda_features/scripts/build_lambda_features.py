#!/usr/bin/env python3
"""W4 (round7, fusion point B): per-item phase-3 lambda stress features.

Zero new model calls. Replicates the frozen stress-feature construction from
consensus_stress/round3/phase3_analyze.py exactly (stress-area, breakpoint,
robustness-radius for reversal AND removal axes), joins each phase-3 subset item
(240 items / 120 pairs) with preoutcome features + gold labels, and writes
features_phase3_lambda.jsonl.

The phase-3 stress protocol itself is preregistered (round3/preregistration.md
section 7, frozen 2026-09-13). The W4 *reducibility* analysis built on top of
these features is exploratory/post-hoc (plan section 16) and is documented as such.

Outputs (all under round7/lambda_features/):
  features_phase3_lambda.jsonl   per-item stress features + baselines + labels
  build_features_verify.json     sanity checks vs round3/analysis/phase3_results.json
"""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

CS = Path(__file__).resolve().parents[3]          # .../consensus_stress
R3 = CS / "round3"
HERE = Path(__file__).resolve().parent.parent     # .../round7/lambda_features

LAMBDAS = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
GRID = LAMBDAS
HC_THRESHOLD = 0.8


def load_base():
    feats = [json.loads(l) for l in (R3 / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((R3 / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        f["gold_label"] = gold[f["item_id"]]
        f["consensus_wrong"] = int((f["consensus"] == "yes") != (f["gold_label"] == "SUPPORTS"))
    return feats


def orig_majority(orig, cqid):
    votes = [v for v in orig.get(cqid, {}).values() if v]
    if not votes:
        return None
    return max(set(votes), key=votes.count)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    feats = load_base()

    recs = [json.loads(l) for l in (R3 / "records_phase3_lambda.jsonl").read_text(encoding="utf-8").splitlines() if l]
    main_recs = [json.loads(l) for l in (R3 / "records.jsonl").read_text(encoding="utf-8").splitlines() if l]

    # original answers per agent + lambda=1 anchors from main records
    orig = defaultdict(dict)
    for r in main_recs:
        if r["condition"] == "original" and r["decision"]:
            orig[r["cqid"]][r["agent_index"]] = r["decision"]["answer"]
    anchor_flip = defaultdict(dict)   # (cqid, axis) -> {agent: 0/1}
    for r in main_recs:
        if r["condition"] in ("reverse", "remove") and r["decision"]:
            axis = "reversal" if r["condition"] == "reverse" else "removal"
            y0 = orig.get(r["cqid"], {}).get(r["agent_index"])
            if y0 is not None:
                anchor_flip[(r["cqid"], axis)][r["agent_index"]] = int(r["decision"]["answer"] != y0)

    # per-item per-axis flip probability over the grid
    grid_flip = defaultdict(dict)     # (cqid, axis) -> {lambda: [flip per agent]}
    for r in recs:
        if not r.get("decision"):
            continue
        cqid, axis, lam = r["cqid"], r["axis"], r["lambda"]
        y0 = orig.get(cqid, {}).get(r["agent_index"])
        if y0 is None:
            continue
        grid_flip[(cqid, axis)].setdefault(lam, []).append(int(r["decision"]["answer"] != y0))
    for (cqid, axis), d in grid_flip.items():
        d[0.0] = 0.0
        d[1.0] = np.mean(list(anchor_flip.get((cqid, axis), {}).values())) if anchor_flip.get((cqid, axis)) else None

    subset_cqids = set(r["cqid"] for r in recs)

    rows = []
    for f in feats:
        cqid = f["cqid"]
        if cqid not in subset_cqids:
            continue
        row = {"cqid": cqid, "item_id": f["item_id"], "pair_id": f["pair_id"],
               "gold_label": f["gold_label"], "consensus_wrong": f["consensus_wrong"],
               "consensus": f["consensus"], "agreement": f["agreement"],
               "rev_flip_rate": f["rev_flip_rate"], "rem_flip_rate": f["rem_flip_rate"],
               "bf_q": f["bf_q"], "bf_reverse": f["bf_reverse"], "bf_paraphrase": f["bf_paraphrase"],
               "R_sym": f["R_sym"], "R_PI": f["R_PI"],
               "intervention_disagreement": f["intervention_disagreement"],
               "mean_confidence": f["mean_confidence"]}
        row["risk_bf_q"] = -f["bf_q"] if f["bf_q"] is not None else None       # RS_q
        row["risk_rev_axis"] = -f["rev_flip_rate"]                              # binary reverse axis risk
        votes0 = orig_majority(orig, cqid)
        for axis in ("reversal", "removal"):
            d = grid_flip.get((cqid, axis), {})

            def _mean(v):
                return v if isinstance(v, (int, float)) else (float(np.mean(v)) if v else None)

            pts = sorted((lam, _mean(d.get(lam))) for lam in GRID if _mean(d.get(lam)) is not None)
            curve = {f"flip_{int(lam*10)}": _mean(d.get(lam)) for lam in GRID}
            if len(pts) < 4:
                row[f"{axis}_stress_area"] = None
                row[f"{axis}_breakpoint"] = None
                row[f"{axis}_robustness_radius"] = None
                row[f"{axis}_curve"] = curve
                continue
            area = 0.0
            for (l1, v1), (l2, v2) in zip(pts, pts[1:]):
                area += 0.5 * (v1 + v2) * (l2 - l1)
            row[f"{axis}_stress_area"] = float(area)
            votes_by_lam = defaultdict(list)
            for r in recs:
                if r["cqid"] == cqid and r["axis"] == axis and r.get("decision"):
                    votes_by_lam[r["lambda"]].append(r["decision"]["answer"])
            bp = None
            rr = 1.0
            for lam in GRID:
                if lam == 0.0:
                    continue
                votes = votes_by_lam.get(lam)
                if not votes:
                    continue
                maj = max(set(votes), key=votes.count)
                if votes0 is not None and maj != votes0:
                    if bp is None:
                        bp = lam
                    rr = lam
                    break
            row[f"{axis}_breakpoint"] = bp
            row[f"{axis}_robustness_radius"] = float(rr)
            row[f"{axis}_curve"] = curve
        # risk encodings for reducibility (short names: rev = reversal, rem = removal)
        for axis, short in (("reversal", "rev"), ("removal", "rem")):
            sa = row[f"{axis}_stress_area"]
            bp = row[f"{axis}_breakpoint"]
            rr = row[f"{axis}_robustness_radius"]
            row[f"risk_{short}_stress_area"] = -sa if sa is not None else None
            row[f"risk_{short}_breakpoint_none1"] = 1.0 if bp is None else bp
            row[f"risk_{short}_robustness_radius"] = rr  # rr already 1.0 if never flips
        rows.append(row)

    # keep deterministic order
    rows.sort(key=lambda r: r["cqid"])
    out = HERE / "features_phase3_lambda.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    # --- verification vs round3/analysis/phase3_results.json ---
    sys.path.insert(0, str(R3))
    import analysis_lib as al
    hc = [r for r in rows if r["agreement"] >= HC_THRESHOLD]
    rev = [r for r in hc if r.get("reversal_stress_area") is not None]
    a_risk = al.group_bootstrap([{**r, "risk_stress": r["risk_rev_stress_area"]} for r in rev],
                                "risk_stress", seed=20260913 + 41)
    verify = {
        "subset_items": len(rows),
        "subset_pairs": len({r["pair_id"] for r in rows}),
        "hc_subset_items": len(hc),
        "hc_subset_pairs": len({r["pair_id"] for r in hc}),
        "reversal_stress_area": {
            "n": len(rev),
            "n_groups": len({r["pair_id"] for r in rev}),
            "n_correct": sum(1 for r in rev if not r["consensus_wrong"]),
            "n_wrong": sum(1 for r in rev if r["consensus_wrong"]),
            "auroc_risk_stress": a_risk,
        },
        "missing_orig_or_anchor_items": sum(1 for r in rows if r["reversal_stress_area"] is None),
    }
    (HERE / "build_features_verify.json").write_text(
        json.dumps(verify, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verify, ensure_ascii=False, indent=2, sort_keys=True))
    print("wrote", out)


if __name__ == "__main__":
    main()
