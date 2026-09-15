#!/usr/bin/env python3
"""Per-item phase-3 continuous-lambda features (Qwen, 120-pair subset).

Recomputes, from the frozen records (records.jsonl + records_phase3_lambda.jsonl), the
per-item reversal/removal stress curves used by round3/phase3_analyze.py and exposes
per-item stress area + consensus robustness radius. NO new model calls; deterministic.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path

import numpy as np

import stress_common as sc

GRID = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)


def load_records() -> tuple[list[dict], list[dict]]:
    main = sc.load_jsonl(sc.R3 / "records.jsonl")
    grid_recs = sc.load_jsonl(sc.R3 / "records_phase3_lambda.jsonl")
    return main, grid_recs


def _val(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) if np.isfinite(float(v)) else None
    vals = [x for x in v if x is not None]
    return float(np.mean(vals)) if vals else None


def build_per_item() -> dict[str, dict]:
    main, grid_recs = load_records()
    orig: dict[str, dict[int, str]] = defaultdict(dict)
    for r in main:
        if r["condition"] == "original" and r.get("decision"):
            orig[r["cqid"]][r["agent_index"]] = r["decision"]["answer"]
    anchor: dict[tuple[str, str], dict[int, int]] = defaultdict(dict)
    for r in main:
        if r["condition"] in ("reverse", "remove") and r.get("decision"):
            axis = "reversal" if r["condition"] == "reverse" else "removal"
            y0 = orig.get(r["cqid"], {}).get(r["agent_index"])
            if y0 is not None:
                anchor[(r["cqid"], axis)][r["agent_index"]] = int(r["decision"]["answer"] != y0)
    grid: dict[tuple[str, str], dict[float, list[int]]] = defaultdict(dict)
    for r in grid_recs:
        if not r.get("decision"):
            continue
        cqid, axis, lam = r["cqid"], r["axis"], r["lambda"]
        y0 = orig.get(cqid, {}).get(r["agent_index"])
        if y0 is None:
            continue
        grid[(cqid, axis)].setdefault(lam, []).append(int(r["decision"]["answer"] != y0))
    for (cqid, axis), d in grid.items():
        d[0.0] = [0]
        a = anchor.get((cqid, axis), {})
        d[1.0] = [float(np.mean(list(a.values()))) if a else None]

    # consensus majority under original (from main records)
    votes0: dict[str, str] = {}
    for cqid, agents in orig.items():
        vs = [v for v in agents.values() if v]
        if vs:
            votes0[cqid] = max(set(vs), key=vs.count)

    subset_cqids = {r["cqid"] for r in grid_recs}
    per_item: dict[str, dict] = {}
    for cqid, agents in orig.items():
        if cqid not in subset_cqids:
            continue  # only the phase-3 120-pair subset has lambda-grid data
        row = {"cqid": cqid}
        for axis in ("reversal", "removal"):
            d = grid.get((cqid, axis), {})
            pts = [(lam, _val(d.get(lam))) for lam in GRID]
            pts = [(l, v) for l, v in pts if v is not None]
            area = None
            if len(pts) >= 4:
                area = 0.0
                for (l1, v1), (l2, v2) in zip(pts, pts[1:]):
                    area += 0.5 * (v1 + v2) * (l2 - l1)
            # consensus robustness radius: smallest lambda where majority flips
            rr = None
            v0 = votes0.get(cqid)
            if v0 is not None:
                rr = 1.0
                for lam in GRID:
                    if lam == 0.0:
                        continue
                    votes = []
                    for r in grid_recs:
                        if r["cqid"] == cqid and r["axis"] == axis and r["lambda"] == lam \
                                and r.get("decision"):
                            votes.append(r["decision"]["answer"])
                    if not votes:
                        continue
                    maj = max(set(votes), key=votes.count)
                    if maj != v0:
                        rr = lam
                        break
            row[f"{axis}_stress_area"] = area
            row[f"{axis}_robustness_radius"] = rr
        row["curve_reversal"] = [_val(grid.get((cqid, "reversal"), {}).get(lam)) for lam in GRID]
        row["curve_removal"] = [_val(grid.get((cqid, "removal"), {}).get(lam)) for lam in GRID]
        per_item[cqid] = row
    return per_item
