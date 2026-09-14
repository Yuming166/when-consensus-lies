"""Phase 3 sketch: discrete consensus stress profile from frozen records (no new calls).

Axis: original -> paraphrase (semantic-preserving) -> synthetic_reverse (weak change)
-> reverse (strong natural change) -> remove (evidence removal). Metrics per condition:
(a) consensus agreement among the 5 agents; (b) expected-response fidelity (mean over agents).
Separated by consensus correctness on the original condition.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
HC = 0.8
AXIS = ["original", "paraphrase", "synthetic_reverse", "reverse", "remove"]


def load_combined() -> tuple[list[dict], dict]:
    feats = []
    for prefix, ledger in (("", "labels_ledger.json"), ("confirmation", "confirmation_labels_ledger.json")):
        fn = "preoutcome_features.jsonl" if prefix == "" else f"{prefix}_preoutcome_features.jsonl"
        feats += [json.loads(l) for l in open(ROOT.parent / "phase2_pilot" / fn)]
        gold = {it["item_id"]: it["gold_label"]
                for it in json.load(open(ROOT.parent / "phase2_pilot" / ledger))["items"]}
        for f in feats:
            if f["item_id"] in gold:
                f["gold"] = gold[f["item_id"]]
                f["wrong"] = int((f["consensus"] == "yes") != (f["gold"] == "SUPPORTS"))
    recs = {}
    for prefix in ("", "confirmation"):
        fn = "records.jsonl" if prefix == "" else f"{prefix}_records.jsonl"
        for line in open(ROOT.parent / "phase2_pilot" / fn):
            r = json.loads(line)
            recs[(r["cqid"], r["agent_index"], r["condition"])] = r["decision"]
    return feats, recs


def main() -> None:
    feats, recs = load_combined()
    hc = [f for f in feats if f["agreement"] >= HC and f.get("wrong") is not None]
    groups = {"correct": [f for f in hc if not f["wrong"]], "wrong": [f for f in hc if f["wrong"]]}
    out = {}
    for gname, items in groups.items():
        out[gname] = {"n": len(items)}
        for cond in AXIS:
            agreements = []
            fidelity = []
            for f in items:
                answers = []
                ok = 0
                n_scored = 0
                for i in range(5):
                    d = recs.get((f["cqid"], i, cond))
                    if not d:
                        continue
                    answers.append(d["answer"])
                    if cond != "original":
                        y0 = recs.get((f["cqid"], i, "original"), {}).get("answer")
                        if y0 is None:
                            continue
                        exp = y0 if cond == "paraphrase" else ("no" if y0 == "yes" else "yes")
                        if cond != "remove":
                            ok += int(d["answer"] == exp)
                            n_scored += 1
                if len(answers) >= 2:
                    cnt = Counter(answers)
                    agreements.append(cnt.most_common(1)[0][1] / len(answers))
                if n_scored:
                    fidelity.append(ok / n_scored)
            out[gname][cond] = {
                "mean_agreement": round(float(np.mean(agreements)), 4) if agreements else None,
                "mean_fidelity": round(float(np.mean(fidelity)), 4) if fidelity else None,
            }
    (ROOT / "phase3_stress_profile.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))

    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, metric in ((axes[0], "mean_agreement"), (axes[1], "mean_fidelity")):
        x = np.arange(len(AXIS))
        for gname, color, ls in (("correct", "tab:green", "-"), ("wrong", "tab:red", "--")):
            vals = [out[gname][c][metric] for c in AXIS]
            ax.plot(x, vals, color=color, ls=ls, marker="o", label=f"{gname} consensus (n={out[gname]['n']})")
        ax.set_xticks(x); ax.set_xticklabels(AXIS, rotation=25, fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_title(metric)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ROOT.parent / "figures" / "phase3_stress_profile.png", dpi=160)
    print("saved figures/phase3_stress_profile.png")


if __name__ == "__main__":
    main()
