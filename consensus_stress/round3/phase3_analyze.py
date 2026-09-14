"""Phase 3 analysis: stress curve, stress area, breakpoint, robustness radius; consensus profile."""
from __future__ import annotations
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analysis_lib as al
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
ANALYSIS_DIR = ROOT / "analysis"
LAMBDAS = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
GRID = LAMBDAS


def load_base() -> list[dict]:
    feats = [json.loads(l) for l in (ROOT / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((ROOT / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        f["gold_label"] = gold[f["item_id"]]
        f["consensus_wrong"] = int((f["consensus"] == "yes") != (f["gold_label"] == "SUPPORTS"))
    return feats


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    feats = load_base()
    by_cqid = {f["cqid"]: f for f in feats}

    recs = [json.loads(l) for l in (ROOT / "records_phase3_lambda.jsonl").read_text(encoding="utf-8").splitlines() if l]
    main_recs = [json.loads(l) for l in (ROOT / "records.jsonl").read_text(encoding="utf-8").splitlines() if l]

    # original answers per agent + anchors from main records
    orig = defaultdict(dict)
    for r in main_recs:
        if r["condition"] == "original" and r["decision"]:
            orig[r["cqid"]][r["agent_index"]] = r["decision"]["answer"]
    anchor_flip = defaultdict(dict)  # (cqid, axis) -> mean flip prob at lambda=1
    for r in main_recs:
        if r["condition"] in ("reverse", "remove") and r["decision"]:
            axis = "reversal" if r["condition"] == "reverse" else "removal"
            y0 = orig.get(r["cqid"], {}).get(r["agent_index"])
            if y0 is not None:
                anchor_flip[(r["cqid"], axis)][r["agent_index"]] = int(r["decision"]["answer"] != y0)

    # gather per-item per-axis flip probabilities over grid
    grid_flip = defaultdict(dict)  # (cqid, axis) -> {lambda: flip_prob}
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

    # consensus per item per lambda
    def consensus_at(cqid, lam):
        votes = []
        for r in recs:
            if r["cqid"] == cqid and r["lambda"] == lam and r.get("decision"):
                votes.append(r["decision"]["answer"])
        # votes by (agent, axis) may duplicate; dedupe per agent per axis
        return votes

    items = []
    for f in feats:
        cqid = f["cqid"]
        row = {"cqid": cqid, "item_id": f["item_id"], "pair_id": f["pair_id"],
               "gold_label": f["gold_label"], "consensus_wrong": f["consensus_wrong"],
               "agreement": f["agreement"]}
        for axis in ("reversal", "removal"):
            d = grid_flip.get((cqid, axis), {})
            def _mean(v):
                return v if isinstance(v, (int, float)) else (float(np.mean(v)) if v else None)
            pts = sorted((lam, _mean(d.get(lam))) for lam in GRID if _mean(d.get(lam)) is not None)
            if len(pts) < 4:
                row[f"{axis}_stress_area"] = None
                row[f"{axis}_breakpoint"] = None
                row[f"{axis}_robustness_radius"] = None
                continue
            # trapezoid integral
            area = 0.0
            for (l1, v1), (l2, v2) in zip(pts, pts[1:]):
                area += 0.5 * (v1 + v2) * (l2 - l1)
            row[f"{axis}_stress_area"] = float(area)
            # consensus flip: majority at lambda vs majority at 0 (original consensus)
            votes0 = orig_majority(orig, cqid)
            votes_by_lam = defaultdict(list)
            for r in recs:
                if r["cqid"] == cqid and r["axis"] == axis and r.get("decision"):
                    votes_by_lam[r["lambda"]].append(r["decision"]["answer"])
            bp = None
            for lam in GRID:
                if lam == 0.0:
                    continue
                votes = votes_by_lam.get(lam)
                if not votes:
                    continue
                maj = max(set(votes), key=votes.count)
                if votes0 is not None and maj != votes0:
                    bp = lam
                    break
            row[f"{axis}_breakpoint"] = bp  # None = never flips
            rr = 1.0
            for lam in GRID:
                if lam == 0.0:
                    continue
                votes = votes_by_lam.get(lam)
                if not votes:
                    continue
                maj = max(set(votes), key=votes.count)
                if votes0 is not None and maj != votes0:
                    rr = lam
                    break
            row[f"{axis}_robustness_radius"] = float(rr)
        items.append(row)

    hc = [x for x in items if x["agreement"] >= al.HC_THRESHOLD]
    out = {
        "protocol": pl.PROTOCOL_VERSION,
        "phase3_subset_items": sum(1 for x in items if x.get("reversal_stress_area") is not None),
        "phase3_hc": len(hc),
        "stress_area": {},
        "breakpoint": {},
        "robustness": {},
        "consensus_profile": {},
    }
    for axis in ("reversal", "removal"):
        key_area = f"{axis}_stress_area"
        sub = [x for x in hc if x.get(key_area) is not None]
        risk = [-(x[key_area]) for x in sub]
        lab = [x["consensus_wrong"] for x in sub]
        a = al.group_bootstrap(sub, key_area, seed=20260913 + 40)
        a_risk = al.group_bootstrap([{**x, "risk_stress": -(x[key_area])} for x in sub], "risk_stress", seed=20260913 + 41)
        correct = [x[key_area] for x in sub if not x["consensus_wrong"]]
        wrong = [x[key_area] for x in sub if x["consensus_wrong"]]
        bp = [x[f"{axis}_breakpoint"] for x in sub]
        bp_num = [b for b in bp if b is not None]
        bp_none = sum(1 for b in bp if b is None)
        rr = [x[f"{axis}_robustness_radius"] for x in sub]
        out["stress_area"][axis] = {
            "auroc_risk_stress": a_risk,
            "mean_correct": round(float(np.mean(correct)), 4) if correct else None,
            "mean_wrong": round(float(np.mean(wrong)), 4) if wrong else None,
            "n_correct": len(correct), "n_wrong": len(wrong),
        }
        out["breakpoint"][axis] = {
            "mean_breakpoint_correct": round(float(np.mean([b for b in bp if b is not None])), 4),
            "n_breakpoint_none_correct": sum(1 for x in sub if not x["consensus_wrong"] and x[f"{axis}_breakpoint"] is None),
            "n_breakpoint_none_wrong": sum(1 for x in sub if x["consensus_wrong"] and x[f"{axis}_breakpoint"] is None),
            "n_correct": sum(1 for x in sub if not x["consensus_wrong"]),
            "n_wrong": sum(1 for x in sub if x["consensus_wrong"]),
        }
        out["robustness"][axis] = {
            "mean_rr_correct": round(float(np.mean([x[f"{axis}_robustness_radius"] for x in sub if not x["consensus_wrong"]])), 4),
            "mean_rr_wrong": round(float(np.mean([x[f"{axis}_robustness_radius"] for x in sub if x["consensus_wrong"]])), 4),
        }
    # consensus profile: flip prob curve by correctness (reversal)
    curve = {"lambda": list(GRID), "correct": [], "wrong": []}
    for lam in GRID:
        cv, wv = [], []
        for x in items:
            d = grid_flip.get((x["cqid"], "reversal"), {})
            v = d.get(lam)
            v = v if isinstance(v, (int, float)) else (float(np.mean(v)) if v else None)
            if v is None:
                continue
            if x["consensus_wrong"]:
                wv.append(v)
            else:
                cv.append(v)
        curve["correct"].append(round(float(np.mean(cv)), 4) if cv else None)
        curve["wrong"].append(round(float(np.mean(wv)), 4) if wv else None)
    out["consensus_profile"]["reversal_flip_curve"] = curve
    (ANALYSIS_DIR / "phase3_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


def orig_majority(orig, cqid):
    votes = [v for v in orig.get(cqid, {}).values() if v]
    if not votes:
        return None
    return max(set(votes), key=votes.count)


if __name__ == "__main__":
    main()
