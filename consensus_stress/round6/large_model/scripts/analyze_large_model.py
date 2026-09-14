"""Round-6 Agent D: within-model + transfer analysis (labels merged AFTER feature freeze).

Reads: large_model/preoutcome_features.jsonl (frozen, label-free), round3/labels_ledger.json,
round3/preoutcome_features.jsonl (Qwen frozen RS_q), round4/ling_preoutcome_features.jsonl
(Ling frozen RS_q), round3/analysis_lib.py (pair-grouped bootstrap).
Outputs: analysis/large_model_within_model.json + analysis/large_model_transfer.json +
analysis/large_model_*.md.
"""
from __future__ import annotations
import json, random, sys
from collections import Counter
from pathlib import Path

import numpy as np

ROUND3 = Path(__file__).resolve().parent.parent.parent.parent / "round3"
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROUND3))
import analysis_lib as al  # noqa: E402

HC_THRESHOLD = al.HC_THRESHOLD
PERM_N = 1000


def load_gpt_merged() -> list[dict]:
    feats = [json.loads(l) for l in (HERE / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((ROUND3 / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        g = gold[f["item_id"]]
        f["gold_label"] = g
        f["gold_yes"] = g == "SUPPORTS"
        f["consensus_wrong"] = int((f["consensus"] == "yes") != f["gold_yes"])
        f["risk_bf_q"] = -f["bf_q"] if f.get("bf_q") is not None else None
    return feats


def load_transfer_scores(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        out[row["cqid"]] = row
    return out


def permutation_auroc(feats, score_key, label_key="consensus_wrong", n=PERM_N, seed=al.BOOTSTRAP_SEED + 13):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None]
    obs = al.auROC([f[score_key] for f in rows], [f[label_key] for f in rows])
    if obs is None:
        return None
    # per-item preserve/flip-swap permutation (round-3 style)
    labels = [f[label_key] for f in rows]
    vals = []
    for _ in range(n):
        swapped = []
        for i in range(0, len(labels) - 1, 2):
            if rng.random() < 0.5:
                swapped.extend([labels[i + 1], labels[i]])
            else:
                swapped.extend([labels[i], labels[i + 1]])
        if len(swapped) != len(labels):
            swapped.extend(labels[len(swapped):])
        a = al.auROC([f[score_key] for f in rows], swapped)
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    pct95 = vals[int(0.95 * len(vals)) - 1] if vals else None
    return {"observed": obs, "perm_p95": pct95, "pass_obs_gt_p95": obs > pct95, "n_perm": len(vals)}


def mechanism_fidelity_bootstrap(feats, score_key, label_key="consensus_wrong",
                                 n=2000, seed=al.BOOTSTRAP_SEED + 17):
    """Pair-grouped bootstrap of mean(correct bf_reverse) - mean(wrong bf_reverse)."""
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None]
    by_pair = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def stat(rows_):
        c = [f[score_key] for f in rows_ if f[label_key] == 0]
        w = [f[score_key] for f in rows_ if f[label_key] == 1]
        if not c or not w:
            return None
        return float(np.mean(c) - np.mean(w))

    obs = stat(rows)
    if obs is None:
        return None
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        v = stat(sample)
        if v is not None:
            vals.append(v)
    vals = sorted(vals)
    return {"mean_correct_minus_wrong": obs,
            "ci": [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]],
            "n_correct": sum(1 for f in rows if f[label_key] == 0),
            "n_wrong": sum(1 for f in rows if f[label_key] == 1)}


def main() -> int:
    out_dir = HERE / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    feats = load_gpt_merged()
    hc = [f for f in feats if f["agreement"] >= HC_THRESHOLD]
    wrong = [f for f in hc if f["consensus_wrong"]]
    print(f"gpt features total={len(feats)} hc={len(hc)} wrong_hc={len(wrong)} "
          f"rate={len(wrong)/max(1,len(hc)):.4f}")
    print("hc_by_label:", dict(Counter(f["gold_label"] for f in hc)))
    print("wrong_hc_by_label:", dict(Counter(f["gold_label"] for f in wrong)))

    risk_key = "risk_bf_q"
    within = {
        "hc_threshold": HC_THRESHOLD,
        "n_total": len(feats), "n_hc": len(hc), "n_wrong_hc": len(wrong),
        "wrong_rate_hc": round(len(wrong) / max(1, len(hc)), 4),
        "hc_by_label": dict(Counter(f["gold_label"] for f in hc)),
        "wrong_hc_by_label": dict(Counter(f["gold_label"] for f in wrong)),
        "primary_auroc": al.group_bootstrap(hc, risk_key),
        "risk_at_80": al.risk_at_80_bootstrap(hc, risk_key),
        "per_label_auroc": {k: al.label_subgroup_bootstrap(hc, risk_key, k) for k in ("SUPPORTS", "REFUTES")},
        "macro_auroc": al.macro_ci(hc, risk_key),
    }
    # placebo (agent-level paraphrase flip rate)
    para_flips = 0
    para_n = 0
    for f in feats:
        for i in range(5):
            v = f["_agent_bf"].get(str(i), {}).get("paraphrase")
            if v is not None:
                para_n += 1
                para_flips += int(v == 0)
    within["placebo"] = {"agent_paraphrase_flip_rate": round(para_flips / max(1, para_n), 4),
                         "n": para_n, "gate_le_0.30": (para_flips / max(1, para_n)) <= 0.30}
    within["permutation"] = permutation_auroc(hc, risk_key)
    within["mechanism_fidelity"] = mechanism_fidelity_bootstrap(
        hc, "bf_reverse", label_key="consensus_wrong")
    # reducibility (reported, not a gate here)
    within["reducibility"] = {
        "spearman_risk_agreement": round(al.spearman([f[risk_key] for f in hc], [f["agreement"] for f in hc]), 4),
        "spearman_risk_conf": round(al.spearman([f[risk_key] for f in hc], [f["mean_confidence"] for f in hc]), 4),
    }

    # transfer (Qwen / Ling frozen RS_q -> gpt wrong|HC)
    qwen = load_transfer_scores(ROUND3 / "preoutcome_features.jsonl")
    ling = load_transfer_scores(Path(__file__).resolve().parent.parent.parent.parent / "round4" / "ling_preoutcome_features.jsonl")
    transfer = {"source": {"qwen": "round3/preoutcome_features.jsonl",
                           "ling": "round4/ling_preoutcome_features.jsonl"}}
    for name, src in (("qwen", qwen), ("ling", ling)):
        rows = []
        for f in hc:
            s = src.get(f["cqid"])
            if s is not None and s.get("bf_q") is not None:
                rows.append({**f, "src_risk": -s["bf_q"]})
        transfer[name] = {"n_hc_with_src": len(rows),
                          "auroc": al.group_bootstrap(rows, "src_risk", label_key="consensus_wrong") if rows else None,
                          "risk_at_80": al.risk_at_80_bootstrap(rows, "src_risk") if rows else None}
        if rows:
            transfer[name]["spearman_src_gpt_risk"] = round(
                al.spearman([r["src_risk"] for r in rows], [r[risk_key] for r in rows]), 4)

    (out_dir / "large_model_within_model.json").write_text(
        json.dumps(within, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "large_model_transfer.json").write_text(
        json.dumps(transfer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("WITHIN:", json.dumps({k: within[k] for k in ("primary_auroc", "risk_at_80", "placebo", "permutation", "mechanism_fidelity")}, ensure_ascii=False, indent=2))
    print("TRANSFER:", json.dumps({k: v for k, v in transfer.items() if k != "source"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
