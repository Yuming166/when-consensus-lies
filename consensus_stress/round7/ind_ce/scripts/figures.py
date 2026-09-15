#!/usr/bin/env python3
"""Round-7 W2 figures: flip-rate CI bars, AUROC comparison, rho scatter."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))

def main() -> int:
    res = json.loads((HERE / "analysis" / "ind_ce_results.json").read_text(encoding="utf-8"))
    fig_dir = HERE / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Fig 1: flip rates with CI
    conds = ["natural", "ind", "placebo"]
    rates = [res["flip_rates"][c]["rate"] for c in conds]
    lo = [res["flip_rates"][c]["ci"][0] for c in conds]
    hi = [res["flip_rates"][c]["ci"][1] for c in conds]
    err_lo = np.asarray(rates) - np.asarray(lo)
    err_hi = np.asarray(hi) - np.asarray(rates)
    fig, ax = plt.subplots(figsize=(6, 4.2))
    xs = np.arange(len(conds))
    ax.bar(xs, rates, yerr=[err_lo, err_hi], capsize=5, color=["#4c72b0", "#dd8452", "#8c8c8c"])
    ax.set_xticks(xs); ax.set_xticklabels([f"{c}\nP(flip|{c})" for c in conds])
    ax.set_ylabel("Flip rate (vs frozen original answer)")
    ax.set_title("Three-condition counter-evidence response (gpt-6-astra, n=100 items)")
    for x, r in zip(xs, rates):
        ax.text(x, r + 0.02, f"{r:.3f}", ha="center")
    dce = res["delta_CE"]
    ax.text(0.02, 0.98, f"$\\Delta_{{CE}}$ = {dce['diff']:+.3f}  [{dce['ci'][0]:+.3f}, {dce['ci'][1]:+.3f}]",
            transform=ax.transAxes, va="top", fontsize=10,
            bbox=dict(boxstyle="round", fc="white", alpha=0.85))
    fig.tight_layout()
    fig.savefig(fig_dir / "flip_rates_ce.png", dpi=150)
    plt.close(fig)

    # Fig 2: AUROC comparison
    scores = ["S_natural", "S_ind", "S_combined", "S_placebo", "S_pair_panel_gpt"]
    labels = ["S_natural", "S_ind", "S_combined", "S_placebo", "S_pair_panel"]
    auroc = [res["auroc"][s]["auroc"] if res["auroc"].get(s) else None for s in scores]
    ci_lo = [res["auroc"][s]["ci"][0] if res["auroc"].get(s) else None for s in scores]
    ci_hi = [res["auroc"][s]["ci"][1] if res["auroc"].get(s) else None for s in scores]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    valid = [(i, a, l, h) for i, (a, l, h) in enumerate(zip(auroc, ci_lo, ci_hi)) if a is not None]
    xs = np.arange(len(valid))
    ax.errorbar(xs, [v[1] for v in valid],
                yerr=[[v[1] - v[2] for v in valid], [v[3] - v[1] for v in valid]],
                fmt="o", capsize=5, color="#c44e52")
    ax.axhline(0.5, ls="--", color="gray")
    ax.set_xticks(xs); ax.set_xticklabels([labels[v[0]] for v in valid])
    ax.set_ylabel("AUROC (consensus_wrong | HC)")
    ax.set_title("Score AUROC on gpt-6-astra HC (pair-grouped 95% CI)")
    for v in valid:
        ax.text(v[0], v[1] + 0.02, f"{v[1]:.3f}", ha="center")
    fig.tight_layout()
    fig.savefig(fig_dir / "auroc_scores.png", dpi=150)
    plt.close(fig)

    # Fig 3: rho scatter
    feats = [json.loads(l) for l in (HERE / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    x = [f["S_natural"] for f in feats if f["S_natural"] is not None and f["S_ind"] is not None]
    y = [f["S_ind"] for f in feats if f["S_natural"] is not None and f["S_ind"] is not None]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(x, y, s=18, alpha=0.7)
    ax.set_xlabel("S_natural (mirror counter-evidence flip rate)")
    ax.set_ylabel("S_ind (independent counter-evidence flip rate)")
    rho = res["rho"]["spearman"]
    ax.set_title(f"$\\rho$(S_natural, S_ind) = {rho:.3f}")
    ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
    fig.tight_layout()
    fig.savefig(fig_dir / "rho_scatter.png", dpi=150)
    plt.close(fig)
    print("figures written:", sorted(p.name for p in fig_dir.glob("*.png")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
