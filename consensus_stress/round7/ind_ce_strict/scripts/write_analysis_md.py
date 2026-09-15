#!/usr/bin/env python3
"""Round-7 W2b: render analysis/strict_results.md from strict_results.json."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def fmt_ci(x):
    if x is None:
        return "n/a"
    if isinstance(x, dict):
        return f"{x.get('auroc', x.get('rate', x.get('diff', x.get('reduction', '?'))))} [{x['ci'][0]}, {x['ci'][1]}]"
    return str(x)


def main() -> int:
    r = json.loads((HERE / "analysis" / "strict_results.json").read_text(encoding="utf-8"))
    L = []
    A = L.append
    A("# Round-7 W2b STRICT — Independent Counter-Evidence (claim-only) vs Matched Placebo (results)")
    A("")
    A("Protocol: `cs-paper-ind-ce-strict-20260915-round7-w2b` (preregistered; cohort = first 50 items / 25 pairs).")
    A("")
    c = r["cohort"]
    A(f"Cohort analyzed: n={c['n_items_total']} items, {c['n_pairs']} pairs; HC (agreement>=0.8): "
      f"n={c['hc']['n']}, wrong={c['hc']['n_wrong']} ({c['hc']['wrong_rate']*100:.1f}%).")
    A("")
    A("## 1. Flip rates (label-blind; item x agent pairs, pair-grouped bootstrap 2000)")
    A("")
    A("| condition | P(flip) | 95% CI | n |")
    A("|---|---|---|---|")
    for cond in ("ind_strict", "natural", "pm"):
        f = r["flip_rates"][cond]
        A(f"| {cond} | {f['rate']} | [{f['ci'][0]}, {f['ci'][1]}] | {f['n']} |")
    A("")
    d = r["delta_CE"]
    A(f"**Delta_CE = P(flip|ind_strict) - P(flip|pm) = +{d['diff']} [{d['ci'][0]}, {d['ci'][1]}]**")
    dn = r["delta_ind_natural"]
    A(f"Delta_ind-natural = {dn['diff']} [{dn['ci'][0]}, {dn['ci'][1]}]")
    dnp = r["delta_natural_pm"]
    A(f"Delta_natural-pm = {dnp['diff']} [{dnp['ci'][0]}, {dnp['ci'][1]}]")
    A("")
    A("## 2. Gates")
    A("")
    for gk, gv in r["gates"].items():
        A(f"- **{gk}**: {json.dumps(gv, ensure_ascii=False)}")
    A("")
    A("## 3. AUROC / Risk@80 on HC (risk direction: higher = riskier; pair-grouped 2000)")
    A("")
    A("| score | AUROC [CI] | Risk@80 reduction [CI] |")
    A("|---|---|---|")
    for key in ("R_S_ind_strict", "R_S_natural", "R_S_pm", "RS_q", "R_S_combined_natural_ind"):
        au = r["auroc"].get(key)
        rk = r["risk_at_80"].get(key)
        aus = "n/a" if not au else f"{au['auroc']:.4f} [{au['ci'][0]:.4f}, {au['ci'][1]:.4f}]"
        rks = "n/a" if not rk else f"{rk['reduction']:.4f} [{rk['ci'][0]:.4f}, {rk['ci'][1]:.4f}]"
        A(f"| {key} | {aus} | {rks} |")
    A("")
    A("### Paired AUROC differences")
    A("")
    for pk, pv in r["paired"].items():
        if pv is None:
            A(f"- {pk}: n/a")
            continue
        A(f"- {pk}: {pv['diff']:.4f} [{pv['ci'][0]:.4f}, {pv['ci'][1]:.4f}] (n={pv['n']})")
    A("")
    rho = r["rho"]
    A(f"## 4. rho(S_natural, S_ind_strict) = {rho['rho']} [{rho['ci'][0]}, {rho['ci'][1]}] (n={rho['n']})")
    A("")
    A("## 5. OOF logistic increment (diagnostic)")
    A("")
    for k, v in r["oof"].items():
        A(f"- {k}: model_a AUROC {v['oof_auroc_a']}, model_b AUROC {v['oof_auroc_b']}, "
          f"diff {v['diff']} [{v['ci'][0]}, {v['ci'][1]}] (n={v['n']})")
    A("")
    leak = r["leakage_audit"]
    A(f"## 6. Leakage audit (inference prompts, {leak['n_checks']} rebuilt checks)")
    A("")
    A(f"- pass: {leak['pass']}; sha-match rate: {leak['sha_match_rate']}")
    if leak["failures"]:
        A(f"- failures: {leak['failures'][:10]}")
    A("")
    A("## 7. Interpretation")
    A("")
    A("- E_ind_strict construction: claim-only dual-direction generation + offline gold assignment "
      "(see run_summary_audit.json / audit_sample.jsonl and run_summary_parser_correction.json).")
    A("- Delta_CE and gates: see section 2; placebo cleanliness is the key gate.")
    A("- S_ind_strict predictive value: AUROC/Risk@80 on HC and paired increments vs S_natural/RS_q.")
    A("- Parser correction transparency: run_summary_parser_correction.json.")
    A("")
    (HERE / "analysis" / "strict_results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("written analysis/strict_results.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
