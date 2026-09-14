"""Round-3 figures: ROC, risk-coverage, phase-3 stress curves (matplotlib)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analysis_lib as al

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"


def load_hc():
    feats = [json.loads(l) for l in (ROOT / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((ROOT / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        f["gold_label"] = gold[f["item_id"]]
        f["consensus_wrong"] = int((f["consensus"] == "yes") != (f["gold_label"] == "SUPPORTS"))
        f["risk_bf_q"] = -f["bf_q"] if f.get("bf_q") is not None else None
        f["disagreement"] = 1.0 - f["agreement"]
    return [f for f in feats if f["agreement"] >= al.HC_THRESHOLD]


def roc_curve(labels, scores):
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    tpr, fpr = [0.0], [0.0]
    tp = fp = 0
    i = 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        for k in range(i, j):
            if pairs[k][1] == 1:
                tp += 1
            else:
                fp += 1
        tpr.append(tp / n_pos if n_pos else 0)
        fpr.append(fp / n_neg if n_neg else 0)
        i = j
    return fpr, tpr


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    hc = load_hc()
    labels = [f["consensus_wrong"] for f in hc]
    scores = {
        "RS_q (-BF_q)": "risk_bf_q",
        "R_sym": "R_sym",
        "R_PI": "R_PI",
        "disagreement": "disagreement",
        "confidence": "mean_confidence",
    }
    plt.figure(figsize=(6, 6))
    for name, key in scores.items():
        fpr, tpr = roc_curve(labels, [f[key] for f in hc])
        a = al.auROC([f[key] for f in hc], labels)
        plt.plot(fpr, tpr, label=f"{name} (AUROC={a:.3f})")
    plt.plot([0, 1], [0, 1], "k--", alpha=0.4)
    plt.xlabel("FPR"); plt.ylabel("TPR"); plt.title("Round-3 paper-scale: consensus-error ranking (Qwen3.5-4B)")
    plt.legend(loc="lower right", fontsize=8)
    plt.tight_layout(); plt.savefig(FIG / "roc_paper_scale.png", dpi=150)

    # risk-coverage
    plt.figure(figsize=(6, 6))
    for name, key in scores.items():
        rows = sorted([f for f in hc if f.get(key) is not None], key=lambda f: f[key])
        cov, err = [], []
        overall = np.mean([f["consensus_wrong"] for f in rows])
        for c in np.linspace(0.1, 1.0, 10):
            keep = rows[:int(c * len(rows))]
            err.append(np.mean([f["consensus_wrong"] for f in keep]) / overall if overall else 1.0)
            cov.append(c)
        plt.plot(cov, err, label=name)
    plt.axhline(1.0, color="k", linestyle="--", alpha=0.4)
    plt.xlabel("coverage (fraction retained, lowest risk first)")
    plt.ylabel("relative error rate")
    plt.title("Risk-coverage (relative error) — Qwen3.5-4B")
    plt.legend(loc="upper right", fontsize=8)
    plt.tight_layout(); plt.savefig(FIG / "risk_coverage_paper_scale.png", dpi=150)

    # phase-3 curve
    if (ROOT / "analysis" / "phase3_results.json").exists():
        p3 = json.loads((ROOT / "analysis" / "phase3_results.json").read_text(encoding="utf-8"))
        curve = p3["consensus_profile"]["reversal_flip_curve"]
        plt.figure(figsize=(6, 5))
        plt.plot(curve["lambda"], curve["correct"], "o-", label="correct consensus")
        plt.plot(curve["lambda"], curve["wrong"], "s-", label="wrong consensus")
        plt.xlabel("lambda (fraction of decision-relevant units reversed)")
        plt.ylabel("mean agent flip probability")
        plt.title("Phase 3: expected-response stress curve by correctness")
        plt.legend()
        plt.tight_layout(); plt.savefig(FIG / "phase3_stress_curve.png", dpi=150)

    print("figures written:", sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    main()
