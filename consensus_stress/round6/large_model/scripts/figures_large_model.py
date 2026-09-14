"""Round-6 Agent D figures: ROC (within/transfer), risk-coverage, mechanism."""
from __future__ import annotations
import json, sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROUND3 = Path(__file__).resolve().parent.parent.parent.parent / "round3"
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROUND3))
import analysis_lib as al  # noqa: E402

FIG = HERE / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def roc_points(scores, labels):
    """Deterministic ROC curve points (tpr/fpr) without sklearn."""
    pairs = sorted(zip(scores, labels), key=lambda x: x[0], reverse=True)
    pos = sum(labels); neg = len(labels) - pos
    if pos == 0 or neg == 0:
        return None
    tpr = [0.0]; fpr = [0.0]
    tp = fp = 0
    for i, (s, l) in enumerate(pairs):
        if l == 1:
            tp += 1
        else:
            fp += 1
        # step at score boundaries
        if i == len(pairs) - 1 or pairs[i + 1][0] != s:
            tpr.append(tp / pos)
            fpr.append(fp / neg)
    return fpr, tpr


def load_merged():
    feats = [json.loads(l) for l in (HERE / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((ROUND3 / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        f["gold_label"] = gold[f["item_id"]]
        f["gold_yes"] = f["gold_label"] == "SUPPORTS"
        f["consensus_wrong"] = int((f["consensus"] == "yes") != f["gold_yes"])
        f["risk_bf_q"] = -f["bf_q"] if f.get("bf_q") is not None else None
    return feats


def main():
    feats = load_merged()
    hc = [f for f in feats if f["agreement"] >= al.HC_THRESHOLD]
    # 1) ROC within-model
    plt.figure(figsize=(5.5, 5))
    pt = roc_points([f["risk_bf_q"] for f in hc], [f["consensus_wrong"] for f in hc])
    if pt:
        fpr, tpr = pt
        a = al.auROC([f["risk_bf_q"] for f in hc], [f["consensus_wrong"] for f in hc])
        plt.plot(fpr, tpr, lw=2, label=f"RS_q within-model (AUROC={a:.3f})")
    plt.plot([0, 1], [0, 1], "k--", alpha=0.4)
    plt.xlabel("FPR"); plt.ylabel("TPR"); plt.title("gpt-6-astra within-model (HC, N=%d)" % len(hc))
    plt.legend(loc="lower right"); plt.tight_layout()
    plt.savefig(FIG / "roc_within_model.png", dpi=150); plt.close()

    # 2) ROC transfer
    plt.figure(figsize=(5.5, 5))
    for name, path in (("Qwen", ROUND3 / "preoutcome_features.jsonl"),
                       ("Ling", Path(__file__).resolve().parent.parent.parent.parent / "round4" / "ling_preoutcome_features.jsonl")):
        src = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                src[row["cqid"]] = row
        rows = [f for f in hc if f["cqid"] in src and src[f["cqid"]].get("bf_q") is not None]
        scores = [-src[f["cqid"]]["bf_q"] for f in rows]
        labels = [f["consensus_wrong"] for f in rows]
        pt = roc_points(scores, labels)
        if pt:
            a = al.auROC(scores, labels)
            plt.plot(pt[0], pt[1], lw=2, label=f"{name} RS_q transfer (AUROC={a:.3f})")
    plt.plot([0, 1], [0, 1], "k--", alpha=0.4)
    plt.xlabel("FPR"); plt.ylabel("TPR"); plt.title("Frozen Qwen/Ling RS_q -> gpt-6-astra errors (HC)")
    plt.legend(loc="lower right"); plt.tight_layout()
    plt.savefig(FIG / "roc_transfer.png", dpi=150); plt.close()

    # 3) Risk-coverage curve
    rows = sorted(hc, key=lambda f: f["risk_bf_q"])
    overall = np.mean([f["consensus_wrong"] for f in rows])
    covs = np.linspace(0.1, 1.0, 19)
    errs = []
    for c in covs:
        keep = rows[:int(c * len(rows))]
        errs.append(np.mean([f["consensus_wrong"] for f in keep]) / overall if overall else 0)
    plt.figure(figsize=(5.5, 4.2))
    plt.plot(covs, errs, "o-", lw=2)
    plt.axhline(1.0, color="k", ls="--", alpha=0.5)
    plt.xlabel("Retained fraction (lowest risk)"); plt.ylabel("Relative error rate")
    plt.title("Risk-coverage: gpt-6-astra HC (N=%d, wrong=%d)" % (len(rows), sum(1 for f in rows if f["consensus_wrong"])))
    plt.tight_layout(); plt.savefig(FIG / "risk_coverage.png", dpi=150); plt.close()

    # 4) Mechanism: mean bf_reverse correct vs wrong with pair-grouped CI of difference
    c = [f["bf_reverse"] for f in hc if f["consensus_wrong"] == 0 and f.get("bf_reverse") is not None]
    w = [f["bf_reverse"] for f in hc if f["consensus_wrong"] == 1 and f.get("bf_reverse") is not None]
    plt.figure(figsize=(4.8, 4.2))
    plt.bar(["correct\n(N=%d)" % len(c), "wrong\n(N=%d)" % len(w)],
            [np.mean(c), np.mean(w)], color=["#4c72b0", "#c44e52"])
    plt.ylabel("mean bf_reverse (fidelity)"); plt.ylim(0, 1.05)
    plt.title("Mechanism: natural-reversal fidelity by correctness")
    plt.tight_layout(); plt.savefig(FIG / "mechanism_fidelity.png", dpi=150); plt.close()
    print("figures written:", sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    raise SystemExit(main())
