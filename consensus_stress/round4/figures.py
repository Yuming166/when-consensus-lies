"""Round-4 figures for Ling cross-model transfer and active probe pilot."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
R3 = HERE.parent / "round3"
sys.path.insert(0, str(R3))
import analysis_lib as al  # noqa: E402

FIG = HERE / "figures"
CONDITIONS = ("paraphrase", "reverse", "synthetic_reverse", "remove")


def roc_curve(labels, scores):
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    pos = sum(labels); neg = len(labels) - pos
    fpr, tpr = [0.0], [0.0]; tp = fp = 0
    i = 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        for k in range(i, j):
            if pairs[k][1] == 1: tp += 1
            else: fp += 1
        fpr.append(fp / neg); tpr.append(tp / pos)
        i = j
    return fpr, tpr


def merged_ling_hc():
    rows = [json.loads(line) for line in (HERE / "ling_preoutcome_features.jsonl").read_text().splitlines() if line]
    qwen = {r["item_id"]: r for r in [json.loads(line) for line in (R3 / "preoutcome_features.jsonl").read_text().splitlines() if line]}
    ledger = json.loads((R3 / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {r["item_id"]: r["gold_label"] for r in ledger["items"]}
    out = []
    for row in rows:
        row["gold_label"] = gold[row["item_id"]]
        row["consensus_wrong"] = int((row["consensus"] == "yes") != (row["gold_label"] == "SUPPORTS"))
        row["risk_bf_q"] = -row["bf_q"]
        row["qwen_risk"] = qwen[row["item_id"]]["risk_bf_q"] if "risk_bf_q" in qwen[row["item_id"]] else -qwen[row["item_id"]]["bf_q"]
        row["mean_confidence_risk"] = -row["mean_confidence"]
        row["disagreement"] = 1.0 - row["agreement"]
        if row["agreement"] >= al.HC_THRESHOLD: out.append(row)
    return out


def coverage_curve(rows, key):
    ordered = sorted(rows, key=lambda r: r[key])
    overall = sum(r["consensus_wrong"] for r in rows) / len(rows)
    xs, ys = [], []
    for coverage in [i / 20 for i in range(2, 21)]:
        keep = ordered[:int(coverage * len(ordered))]
        error = sum(r["consensus_wrong"] for r in keep) / len(keep) if keep else 0
        xs.append(coverage); ys.append(error / overall)
    return xs, ys


def active_rows():
    rows = merged_ling_hc()  # not used directly
    qrows = [json.loads(line) for line in (R3 / "preoutcome_features.jsonl").read_text().splitlines() if line]
    ledger = json.loads((R3 / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {r["item_id"]: r["gold_label"] for r in ledger["items"]}
    out = []
    for row in qrows:
        row["gold_label"] = gold[row["item_id"]]
        row["consensus_wrong"] = int((row["consensus"] == "yes") != (row["gold_label"] == "SUPPORTS"))
        if row["agreement"] < al.HC_THRESHOLD: continue
        row["risk_active"] = 1.0 - row["bf_reverse"]
        cond = CONDITIONS[hashlib.sha256(("round4-fixed-rotation:" + row["item_id"]).encode()).digest()[0] % 4]
        vals = {"paraphrase": 1-row["bf_paraphrase"], "reverse": 1-row["bf_reverse"],
                "synthetic_reverse": 1-row["bf_synthetic_reverse"], "remove": 1-row["rem_flip_rate"]}
        row["risk_fixed"] = vals[cond]
        out.append(row)
    return out


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    rows = merged_ling_hc(); labels = [r["consensus_wrong"] for r in rows]
    plt.figure(figsize=(6.2, 5.4))
    for name, key in {"Ling RS_q": "risk_bf_q", "Qwen RS_q transfer": "qwen_risk",
                       "confidence (inverted)": "mean_confidence_risk", "disagreement": "disagreement"}.items():
        fpr, tpr = roc_curve(labels, [r[key] for r in rows])
        auc = al.auROC([r[key] for r in rows], labels)
        plt.plot(fpr, tpr, label=f"{name} ({auc:.3f})")
    plt.plot([0, 1], [0, 1], "k--", alpha=.4)
    plt.xlabel("FPR"); plt.ylabel("TPR")
    plt.title("Cross-model error ranking on Ling HC items")
    plt.legend(loc="lower right", fontsize=8); plt.tight_layout()
    plt.savefig(FIG / "roc_ling_crossmodel.png", dpi=180); plt.close()

    plt.figure(figsize=(6.2, 5.0))
    for name, key in {"Ling RS_q": "risk_bf_q", "Qwen RS_q transfer": "qwen_risk"}.items():
        xs, ys = coverage_curve(rows, key); plt.plot(xs, ys, marker="o", label=name)
    plt.axhline(1, color="k", ls="--", alpha=.4)
    plt.xlabel("Coverage retained (lowest risk first)"); plt.ylabel("Relative error rate")
    plt.title("Risk-coverage on Ling HC items"); plt.legend(); plt.tight_layout()
    plt.savefig(FIG / "risk_coverage_ling_crossmodel.png", dpi=180); plt.close()

    m = json.loads((HERE / "analysis" / "ling_adapted_analysis.json").read_text())["mechanism_transfer"]["reverse_fidelity"]
    plt.figure(figsize=(5.4, 4.2))
    plt.bar(["Correct", "Wrong"], [m["correct_mean"], m["wrong_mean"]], color=["#4C78A8", "#E45756"])
    plt.ylim(0, 1); plt.ylabel("Natural-evidence reverse fidelity")
    plt.title("Ling mechanism transfer")
    plt.tight_layout(); plt.savefig(FIG / "ling_mechanism_reverse.png", dpi=180); plt.close()

    arows = active_rows(); alabels = [r["consensus_wrong"] for r in arows]
    plt.figure(figsize=(6.2, 5.2))
    for name, key in {"Active reversal probe": "risk_active", "Fixed condition rotation": "risk_fixed"}.items():
        fpr, tpr = roc_curve(alabels, [r[key] for r in arows])
        auc = al.auROC([r[key] for r in arows], alabels)
        plt.plot(fpr, tpr, label=f"{name} ({auc:.3f})")
    plt.plot([0, 1], [0, 1], "k--", alpha=.4)
    plt.xlabel("FPR"); plt.ylabel("TPR"); plt.title("Matched-budget probe selection (Qwen HC)")
    plt.legend(loc="lower right", fontsize=8); plt.tight_layout()
    plt.savefig(FIG / "active_probe_roc.png", dpi=180); plt.close()
    print("figures:", sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    main()
