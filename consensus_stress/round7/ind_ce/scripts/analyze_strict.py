#!/usr/bin/env python3
"""Round-7 W2 analysis (label merged AFTER feature freeze).

Flip rates + Delta_CE [CI]; AUROC/Risk@80 of S_natural/S_ind/S_combined/S_placebo/S_pair
on HC; OOF logistic increment of S_ind over S_natural; rho(S_natural, S_ind).
"""
from __future__ import annotations
import json, math, random, sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
R6 = HERE.parent.parent / "round6" / "large_model"
sys.path.insert(0, str(R3))
import analysis_lib as al  # noqa: E402

BOOTSTRAP_N = 2000
BOOT_SEED = 20260914
HC_THRESHOLD = 0.8
CONDITIONS = ("natural", "ind", "placebo")


def load_round6(cond="original") -> dict:
    out = {}
    for line in (R6 / "records.jsonl").read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        r = json.loads(line)
        if r["condition"] == cond and r.get("decision"):
            out[(r["item_id"], r["agent_index"])] = r["decision"]["answer"]
    return out


def load_ours(prefix: str = "") -> dict:
    out = {}
    for fn in (("strict_records.jsonl",) if prefix else ("records_smoke.jsonl", "records.jsonl")):
        for line in (HERE / fn).read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            r = json.loads(line)
            if r.get("decision"):
                out[(r["item_id"], r["agent_index"], r["condition"])] = r["decision"]["answer"]
    return out


def load_gold() -> dict:
    ledger = json.loads((R3 / "labels_ledger.json").read_text(encoding="utf-8"))
    return {it["item_id"]: it["gold_label"] for it in ledger["items"]}


def item_pair(item_id: str) -> str:
    return ":".join(item_id.split(":")[:2])


def flip_rate_and_ci(ours, orig, pairs, cond, *, seed, n=BOOTSTRAP_N):
    rng = random.Random(seed)
    rows = []
    for it in sorted({k[0] for k in ours}):
        for i in range(5):
            y0 = orig.get((it, i))
            y1 = ours.get((it, i, cond))
            if y0 is not None and y1 is not None:
                rows.append((item_pair(it), int(y0 != y1)))
    obs = sum(v for _, v in rows) / max(1, len(rows))
    by_pair = {}
    for pid, v in rows:
        by_pair.setdefault(pid, []).append(v)
    groups = sorted(by_pair)

    def stat():
        s = []
        for _ in range(len(groups)):
            s.extend(by_pair[rng.choice(groups)])
        return sum(s) / max(1, len(s))

    vals = sorted(stat() for _ in range(n))
    return {"rate": round(obs, 4), "n": len(rows), "n_pairs": len(groups),
            "ci": [round(vals[int(0.025 * n)], 4), round(vals[int(0.975 * n) - 1], 4)]}


def diff_ci(ours, orig, pairs, key_a, key_b, *, seed, n=BOOTSTRAP_N):
    rng = random.Random(seed)
    rows_a, rows_b = [], []
    for it in sorted({k[0] for k in ours}):
        for i in range(5):
            y0 = orig.get((it, i))
            ya = ours.get((it, i, key_a))
            yb = ours.get((it, i, key_b))
            if y0 is not None and ya is not None:
                rows_a.append((item_pair(it), int(y0 != ya)))
            if y0 is not None and yb is not None:
                rows_b.append((item_pair(it), int(y0 != yb)))
    obs_a = sum(v for _, v in rows_a) / max(1, len(rows_a))
    obs_b = sum(v for _, v in rows_b) / max(1, len(rows_b))
    obs = obs_a - obs_b
    by_a, by_b = {}, {}
    for pid, v in rows_a:
        by_a.setdefault(pid, []).append(v)
    for pid, v in rows_b:
        by_b.setdefault(pid, []).append(v)
    groups = sorted(set(by_a) | set(by_b))

    def stat():
        sa, sb = [], []
        for _ in range(len(groups)):
            pid = rng.choice(groups)
            sa.extend(by_a.get(pid, []))
            sb.extend(by_b.get(pid, []))
        return (sum(sa) / max(1, len(sa))) - (sum(sb) / max(1, len(sb)))

    vals = sorted(stat() for _ in range(n))
    return {"diff": round(obs, 4), "n_a": len(rows_a), "n_b": len(rows_b),
            "ci": [round(vals[int(0.025 * n)], 4), round(vals[int(0.975 * n) - 1], 4)]}


def main() -> int:
    import sys as _sys
    prefix = _sys.argv[1] if len(_sys.argv) > 1 else ""
    if prefix:
        globals()["HERE"] = HERE
    ours = load_ours(prefix=prefix)
    orig = load_round6("original")
    gold = load_gold()
    fp = (HERE / f"{prefix}preoutcome_features.jsonl") if prefix else (HERE / "preoutcome_features.jsonl")
    feats = [json.loads(l) for l in fp.read_text(encoding="utf-8").splitlines() if l]
    for f in feats:
        g = gold[f["item_id"]]
        f["gold_label"] = g
        f["gold_yes"] = g == "SUPPORTS"
        f["consensus_wrong"] = int((f["consensus"] == "yes") != f["gold_yes"])
    hc = [f for f in feats if f["agreement"] >= HC_THRESHOLD]
    wrong = [f for f in hc if f["consensus_wrong"]]

    # ---- three-condition flip rates ----
    flip = {}
    for cond in CONDITIONS:
        flip[cond] = flip_rate_and_ci(ours, orig, None, cond, seed=BOOT_SEED + 0)
    dce = diff_ci(ours, orig, None, "ind", "placebo", seed=BOOT_SEED + 0)
    dni = diff_ci(ours, orig, None, "ind", "natural", seed=BOOT_SEED + 0)
    dnp = diff_ci(ours, orig, None, "natural", "placebo", seed=BOOT_SEED + 0)
    # round6 replication: rev_flip_rate from round6 reverse records on same items
    r6_rev = load_round6("reverse")
    repl_rows = 0
    repl_flips = 0
    for it in sorted({k[0] for k in ours}):
        for i in range(5):
            y0 = orig.get((it, i))
            y1 = r6_rev.get((it, i))
            if y0 is not None and y1 is not None:
                repl_rows += 1
                repl_flips += int(y0 != y1)
    r6_rev_rate = repl_flips / max(1, repl_rows)

    # ---- AUROC / Risk@80 (risk direction: higher = riskier, W1/round6 convention) ----
    hc2 = []
    for f in hc:
        row = dict(f)
        for src in ("S_natural", "S_ind", "S_combined", "S_placebo",
                    "S_pair_flip_gpt", "S_pair_same_gpt", "S_pair_flip_qwen", "S_pair_same_qwen"):
            v = f.get(src)
            row[f"R_{src}"] = (-v) if v is not None else None
        row["S_pair_panel_gpt"] = f.get("S_pair_panel_gpt")
        row["S_pair_panel_qwen"] = f.get("S_pair_panel_qwen")
        hc2.append(row)
    hc2 = [f for f in hc2]

    def rows_with(feats, key):
        return [f for f in feats if f.get(key) is not None]

    score_keys = ["R_S_natural", "R_S_ind", "R_S_combined", "R_S_placebo",
                  "S_pair_panel_gpt", "R_S_pair_flip_gpt", "R_S_pair_same_gpt",
                  "S_pair_panel_qwen"]
    display = {"R_S_natural": "S_natural", "R_S_ind": "S_ind", "R_S_combined": "S_combined",
               "R_S_placebo": "S_placebo", "S_pair_panel_gpt": "S_pair_panel_gpt",
               "R_S_pair_flip_gpt": "S_pair_flip_gpt", "R_S_pair_same_gpt": "S_pair_same_gpt",
               "S_pair_panel_qwen": "S_pair_panel_qwen"}
    auroc = {}
    risk = {}
    for key in score_keys:
        rows = rows_with(hc2, key)
        auroc[display[key]] = al.group_bootstrap(rows, key, seed=BOOT_SEED + 1) if rows else None
        risk[display[key]] = al.risk_at_80_bootstrap(rows, key, seed=BOOT_SEED + 2) if rows else None
        if key.startswith("R_"):
            if auroc[display[key]]:
                auroc[display[key]]["risk_direction_negated"] = True
            if risk[display[key]]:
                risk[display[key]]["risk_direction_negated"] = True
    paired = {
        "S_ind_minus_S_natural": al.paired_bootstrap_diff(hc2, "R_S_ind", "R_S_natural", seed=BOOT_SEED + 3),
        "S_combined_minus_S_natural": al.paired_bootstrap_diff(hc2, "R_S_combined", "R_S_natural", seed=BOOT_SEED + 3),
        "S_ind_minus_S_placebo": al.paired_bootstrap_diff(hc2, "R_S_ind", "R_S_placebo", seed=BOOT_SEED + 3),
        "S_pair_panel_minus_S_ind": al.paired_bootstrap_diff(hc2, "R_S_ind", "S_pair_panel_gpt", seed=BOOT_SEED + 3),
        "S_pair_panel_minus_S_natural": al.paired_bootstrap_diff(hc2, "R_S_natural", "S_pair_panel_gpt", seed=BOOT_SEED + 3),
    }
    risk_at_80_key = "R_S_combined"
    combined_risk_at_80 = al.risk_at_80_bootstrap(hc2, risk_at_80_key, seed=BOOT_SEED + 2)

    # ---- rho(S_natural, S_ind) with pair-grouped CI ----
    rho_rows = [f for f in feats if f["S_natural"] is not None and f["S_ind"] is not None]
    rng = random.Random(BOOT_SEED + 5)
    by_pair = {}
    for f in rho_rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    groups = sorted(by_pair)
    obs_rho = al.spearman([f["S_natural"] for f in rho_rows], [f["S_ind"] for f in rho_rows])
    vals = []
    for _ in range(BOOTSTRAP_N):
        sample = []
        for _ in range(len(groups)):
            sample.extend(by_pair[rng.choice(groups)])
        v = al.spearman([f["S_natural"] for f in sample], [f["S_ind"] for f in sample])
        if v is not None:
            vals.append(v)
    vals = sorted(vals)
    rho = {"spearman": round(obs_rho, 4), "n": len(rho_rows),
           "ci": [round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4)]}

    # ---- OOF logistic increment (leave-one-pair-out, HC) ----
    oof = oof_logistic_increment(hc, seed=BOOT_SEED + 4)

    result = {
        "protocol": "cs-paper-ind-ce-20260914-round7-w2",
        "cohort": {"n_items_total": len(feats), "n_pairs": len({f["pair_id"] for f in feats}),
                   "hc": {"n": len(hc), "n_wrong": len(wrong),
                          "wrong_rate": round(len(wrong) / max(1, len(hc)), 4)}},
        "flip_rates": flip,
        "delta_CE": dce,
        "delta_NI": dni,
        "delta_NP": dnp,
        "round6_reverse_replication": {"our_natural_rate": flip["natural"]["rate"],
                                       "round6_rev_rate": round(r6_rev_rate, 4),
                                       "abs_diff": round(abs(flip["natural"]["rate"] - r6_rev_rate), 4),
                                       "gate_le_0.15": abs(flip["natural"]["rate"] - r6_rev_rate) <= 0.15,
                                       "n_rows": repl_rows},
        "gates": {
            "G3_delta_CE_gt_0": {"point": dce["diff"], "ci_lb": dce["ci"][0],
                                 "pass": dce["diff"] > 0 and dce["ci"][0] > 0},
            "G4_placebo_le_0.30": {"rate": flip["placebo"]["rate"], "pass": flip["placebo"]["rate"] <= 0.30},
        },
        "auroc": auroc,
        "risk_at_80": risk,
        "paired_auroc_diff": paired,
        "rho": rho,
        "oof_increment": oof,
    }
    (HERE / "analysis" / f"ind_ce_{prefix}results.json" if prefix else HERE / "analysis" / "ind_ce_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def oof_logistic_increment(feats, *, seed, n=BOOTSTRAP_N):
    """Leave-one-pair-out OOF logistic: P(wrong|HC) ~ [S_natural] vs [S_natural, S_ind].
    Returns OOF AUROC for each model + bootstrap CI on the difference (fixed OOF preds)."""
    try:
        from sklearn.linear_model import LogisticRegression
    except Exception:
        return {"error": "sklearn unavailable"}
    rows = [f for f in feats if f["S_natural"] is not None and f["S_ind"] is not None]
    by_pair = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    X1 = np.asarray([[f["S_natural"]] for f in rows], float)
    X2 = np.asarray([[f["S_natural"], f["S_ind"]] for f in rows], float)
    y = np.asarray([f["consensus_wrong"] for f in rows], int)
    oof1 = np.zeros(len(rows))
    oof2 = np.zeros(len(rows))
    for test_pid in pairs:
        test_idx = [i for i, f in enumerate(rows) if f["pair_id"] == test_pid]
        tr_idx = [i for i in range(len(rows)) if i not in test_idx]
        if len(set(y[tr_idx])) < 2 or len(test_idx) == 0:
            fallback = float(np.mean(y[tr_idx])) if len(tr_idx) else 0.5
            oof1[test_idx] = fallback
            oof2[test_idx] = fallback
            continue
        for X, oof in ((X1, oof1), (X2, oof2)):
            try:
                clf = LogisticRegression(C=1.0, max_iter=1000)
                clf.fit(X[tr_idx], y[tr_idx])
                oof[test_idx] = clf.predict_proba(X[test_idx])[:, 1]
            except Exception:
                oof[test_idx] = float(np.mean(y[tr_idx]))
    a1 = al.auROC([float(v) for v in oof1], list(y))
    a2 = al.auROC([float(v) for v in oof2], list(y))
    obs = (a2 - a1) if (a1 is not None and a2 is not None) else None
    rng = random.Random(seed)

    def stat():
        sample = []
        for _ in range(len(pairs)):
            pid = rng.choice(pairs)
            for f in by_pair[pid]:
                i = rows.index(f)
                sample.append(i)
        s1 = al.auROC([float(oof1[i]) for i in sample], [int(y[i]) for i in sample])
        s2 = al.auROC([float(oof2[i]) for i in sample], [int(y[i]) for i in sample])
        return (s2 - s1) if (s1 is not None and s2 is not None) else None

    vals = sorted(v for v in (stat() for _ in range(n)) if v is not None)
    return {
        "model_A": "S_natural", "model_B": "[S_natural, S_ind]",
        "n_hc": len(rows), "n_pairs": len(pairs),
        "n_wrong": int(y.sum()),
        "oof_auroc_A": round(a1, 4) if a1 is not None else None,
        "oof_auroc_B": round(a2, 4) if a2 is not None else None,
        "oof_auroc_diff_B_minus_A": round(obs, 4) if obs is not None else None,
        "ci": [round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4)]
        if vals else None,
        "note": "leave-one-pair-out OOF; CI = pair-grouped bootstrap over fixed OOF predictions",
    }


if __name__ == "__main__":
    raise SystemExit(main())
