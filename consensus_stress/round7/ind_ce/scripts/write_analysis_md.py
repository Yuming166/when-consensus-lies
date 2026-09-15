#!/usr/bin/env python3
"""Write analysis/ind_ce_results.md from analysis/ind_ce_results.json."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

def main() -> int:
    import sys as _sys
    prefix = _sys.argv[1] if len(_sys.argv) > 1 else ""
    res_path = HERE / "analysis" / f"ind_ce_{prefix}results.json" if prefix else HERE / "analysis" / "ind_ce_results.json"
    out_path = HERE / "analysis" / f"ind_ce_{prefix}results.md" if prefix else HERE / "analysis" / "ind_ce_results.md"
    res = json.loads(res_path.read_text(encoding="utf-8"))
    L = []
    L.append("# Round-7 W2 — Independent Counter-Evidence vs Natural vs Placebo (results)")
    L.append("")
    L.append(f"Protocol: `{res['protocol']}` (preregistered; cohort = first 100 items / 50 pairs of round3 selection_manifest).")
    L.append("")
    L.append(f"Cohort analyzed: n={res['cohort']['n_items_total']} items, {res['cohort']['n_pairs']} pairs; "
             f"HC (agreement>=0.8): n={res['cohort']['hc']['n']}, wrong={res['cohort']['hc']['n_wrong']} "
             f"({res['cohort']['hc']['wrong_rate']:.1%}).")
    L.append("")
    L.append("## 1. Three-condition flip rates (label-blind)")
    L.append("")
    L.append("| condition | P(flip) | 95% CI | n (item x agent) |")
    L.append("|---|---|---|---|")
    for c in ("natural", "ind", "placebo"):
        f = res["flip_rates"][c]
        L.append(f"| {c} | {f['rate']:.4f} | [{f['ci'][0]:.4f}, {f['ci'][1]:.4f}] | {f['n']} |")
    d = res["delta_CE"]
    L.append("")
    L.append(f"**Delta_CE = P(flip|ind) - P(flip|placebo) = {d['diff']:+.4f} "
             f"[{d['ci'][0]:+.4f}, {d['ci'][1]:+.4f}]** (pair-grouped bootstrap 2000, seed 20260914).")
    dni = res["delta_NI"]
    L.append(f"Delta_NI = P(flip|ind) - P(flip|natural) = {dni['diff']:+.4f} [{dni['ci'][0]:+.4f}, {dni['ci'][1]:+.4f}].")
    dnp = res["delta_NP"]
    L.append(f"Delta_NP = P(flip|natural) - P(flip|placebo) = {dnp['diff']:+.4f} [{dnp['ci'][0]:+.4f}, {dnp['ci'][1]:+.4f}].")
    L.append("")
    r6 = res["round6_reverse_replication"]
    L.append(f"Round-6 replication: our P(flip|natural)={r6['our_natural_rate']:.4f} vs round-6 rev_flip_rate="
             f"{r6['round6_rev_rate']:.4f} (abs diff {r6['abs_diff']:.4f}, gate<=0.15: {r6['gate_le_0.15']}).")
    L.append("")
    L.append("## 2. Gates")
    L.append("")
    for g, v in res["gates"].items():
        L.append(f"- **{g}**: {json.dumps(v, ensure_ascii=False)}")
    L.append("")
    L.append("## 3. AUROC / Risk@80 on HC (risk direction: higher = riskier; pair-grouped 2000, seed 20260914+1/2)")
    L.append("")
    L.append("| score | AUROC [CI] | Risk@80 reduction [CI] |")
    L.append("|---|---|---|")
    for s in ("S_natural", "S_ind", "S_combined", "S_placebo", "S_pair_panel_gpt", "S_pair_flip_gpt", "S_pair_same_gpt", "S_pair_panel_qwen"):
        a = res["auroc"].get(s)
        r = res["risk_at_80"].get(s)
        a_str = f"{a['auroc']:.4f} [{a['ci'][0]:.4f}, {a['ci'][1]:.4f}]" if a else "n/a"
        r_str = f"{r['reduction']:.4f} [{r['ci'][0]:.4f}, {r['ci'][1]:.4f}]" if r else "n/a"
        L.append(f"| {s} | {a_str} | {r_str} |")
    L.append("")
    L.append("### Paired AUROC differences")
    L.append("")
    for k, v in res["paired_auroc_diff"].items():
        L.append(f"- {k}: {v['diff']:+.4f} [{v['ci'][0]:+.4f}, {v['ci'][1]:+.4f}] (n={v['n']})" if v else f"- {k}: n/a")
    L.append("")
    L.append(f"## 4. rho(S_natural, S_ind) = {res['rho']['spearman']:.4f} "
             f"[{res['rho']['ci'][0]:.4f}, {res['rho']['ci'][1]:.4f}] (n={res['rho']['n']})")
    L.append("")
    L.append("## 5. OOF logistic increment (S_ind over S_natural)")
    o = res["oof_increment"]
    if "error" in o:
        L.append(f"- {o['error']}")
    else:
        L.append(f"- model A={o['model_A']}: OOF AUROC {o['oof_auroc_A']}; "
                 f"model B={o['model_B']}: OOF AUROC {o['oof_auroc_B']}; "
                 f"diff {o['oof_auroc_diff_B_minus_A']:+.4f} [{o['ci'][0]:+.4f}, {o['ci'][1]:+.4f}] "
                 f"(HC n={o['n_hc']}, wrong={o['n_wrong']}, pairs={o['n_pairs']}).")
    L.append("")
    L.append("## 6. Interpretation")
    L.append("")
    gates_pass = all(v.get("pass") for v in res["gates"].values())
    L.append(f"- E_ind construction: see `run_summary_audit.json` and `audit_sample.jsonl` "
             f"(decision-relevance + independence gates).")
    L.append(f"- Delta_CE > 0 with CI excluding 0: {res['gates']['G3_delta_CE_gt_0']['pass']}.")
    L.append(f"- Placebo clean (P(flip|placebo)<=0.30): {res['gates']['G4_placebo_le_0.30']['pass']}.")
    L.append(f"- S_ind increment over S_natural: see OOF logistic above (small-HC caveat).")
    L.append("")
    out_path.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"analysis/{out_path.name} written")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
