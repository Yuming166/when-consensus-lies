#!/usr/bin/env python3
"""Diagnostic figures for round-7 W3 stress-profile analysis (post-hoc).

fig1: 2-panel scatter of reversal rigidity (1 - rev_flip_rate) vs removal instability
      (rem_flip_rate) on the HC subset; correct vs wrong consensus; rigid regions marked.
fig2: Qwen phase-3 lambda subset - removal flip curve by rigid/correctness group.
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import stress_common as sc

FIG = sc.HERE / "figures"


def fig1() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True, sharey=True)
    for ax, model_key in zip(axes, ("qwen", "ling")):
        feats = sc.load_model(model_key, hc_only=True)
        rev = np.array([f["risk_rev"] for f in feats])
        rem = np.array([f["risk_rem"] for f in feats])
        lab = np.array([f["consensus_wrong"] for f in feats])
        for lv, color, mark, name in ((0, "#2a7db8", "o", "correct consensus"),
                                      (1, "#d64933", "x", "wrong consensus")):
            m = lab == lv
            ax.scatter(rev[m], rem[m], c=color, marker=mark, s=34 if lv == 0 else 55,
                       alpha=0.75, linewidths=0.5, label=name)
        ax.axvspan(0.6, 1.0, color="gray", alpha=0.08)
        ax.axhline(0.6, color="gray", lw=0.6, ls="--", alpha=0.5)
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 1.05)
        ax.set_title(sc.MODEL_FILES[model_key]["display"])
        ax.set_xlabel("reversal rigidity (1 - rev_flip_rate)")
        ax.set_ylabel("removal instability (rem_flip_rate)")
        ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    fig.suptitle("Multi-axis pressure profile (HC subset; post-hoc diagnostic)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = FIG / "axis_profile_scatter.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print("wrote", out)


def fig2() -> None:
    d = json.loads((sc.HERE / "stress_profile_results.json").read_text(encoding="utf-8"))
    la = d["task3_false_positive"]["lambda_axis"]["consensus-rigid"]
    lam = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, key, title in ((axes[0], "removal", "removal axis (evidence deletion)"),
                           (axes[1], "reversal", "reversal axis (counter-evidence)")):
        ax.plot(lam, la[f"curve_{key}_correct"], "o-", c="#2a7db8",
                label=f"correct-rigid (n={la['n_correct_rigid']})")
        ax.plot(lam, la[f"curve_{key}_wrong"], "x--", c="#d64933",
                label=f"wrong-rigid (n={la['n_wrong_rigid']})")
        ax.set_xlabel("lambda (fraction of units stressed)")
        ax.set_ylabel("mean agent flip probability")
        ax.set_title(title)
        ax.legend(fontsize=8)
    fig.suptitle("Qwen phase-3 lambda subset: rigid panels by correctness (post-hoc diagnostic)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = FIG / "lambda_separation.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig1()
    fig2()
