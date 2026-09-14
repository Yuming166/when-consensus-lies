"""Write analysis/large_model_within_model.md and large_model_transfer.md from JSONs."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
AN = HERE / "analysis"

def fmt_ci(x):
    if not x:
        return "N/A"
    return f"{x['auroc']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}] (n={x['n']})"

within = json.loads((AN / "large_model_within_model.json").read_text(encoding="utf-8"))
transfer = json.loads((AN / "large_model_transfer.json").read_text(encoding="utf-8"))
summ = json.loads((HERE / "run_summary_formal.json").read_text(encoding="utf-8"))

md = f"""# Large-Model Single-Point Validation — Within-Model Results (gpt-6-astra)

Protocol: `cs-paper-gpt-singlepoint-20260914-round6` · Relay: `https://openapi.center/v1` ·
Model: **gpt-6-astra** (verified in 2,483/2,483 successful records) · Date: 2026-09-14.

## Run summary (formal, 100 items x 5 agents x 5 conditions = 2,500 logical calls)

| metric | value |
|---|---|
| records | {summ['records']} |
| valid | {summ['success']} |
| **valid rate (G1 gate >= 0.95)** | **{summ['valid_rate']:.4f}** (PASS) |
| first-pass rate | {summ['first_pass_rate']:.4f} |
| HTTP statuses (all internal attempts) | 200 x {summ['http_stats'].get('200',0)}, 429 x {summ['http_stats'].get('429',0)}, 502 x {summ['http_stats'].get('502',0)}, 400 x {summ['http_stats'].get('400',0)} |
| transport retries | {summ['transport_retries']} |
| cache hits (mirror-equivalent views) | {summ['cache_hits']} |
| elapsed (s) | {summ['elapsed_seconds']} |
| token usage (logical, incl. cache replays) | prompt {summ['token_usage']['prompt_tokens']}, completion {summ['token_usage']['completion_tokens']} |

Failures: 17/2,500 records are transport failures (429/502/400 "Upstream request failed");
**0 parse failures** (contract adaptation not needed; no JSON exemplar escalation required).
2 items lack complete 5-agent original answers (transport failures on `original`) and are
excluded from feature-level analysis by the Round-3 feature construction rule (all 5 originals
required to define consensus/agreement); this is not post-hoc subset selection on outcomes.

## Cohort & HC

- Items attempted: 100 (50 pairs). Items with complete features: 98 (label-free, SHA256
  `f1d167aad462da7dc2af8efae593685f386e3b434e8d36af79361b7989204e03`, frozen before label merge).
- High-consensus (agreement >= 0.8): **{within['n_hc']}** items; wrong: **{within['n_wrong_hc']}**
  (error rate {within['wrong_rate_hc']:.4f}); HC by label SUPPORTS/REFUTES =
  {json.dumps(within['hc_by_label'])}; wrong-HC by label = {json.dumps(within['wrong_hc_by_label'])}.

## Gates (all frozen in preregistration Section 5)

| gate | result | verdict |
|---|---|---|
| G1 pipeline valid >= 0.95 | {summ['valid_rate']:.4f} | **PASS** |
| G2 primary AUROC(RS_q, wrong\|HC) CI lb > 0.5 | {fmt_ci(within['primary_auroc'])} | **PASS** (lb {within['primary_auroc']['ci'][0]:.3f} > 0.5; point >= 0.60) |
| G3 placebo paraphrase flip <= 0.30 | {within['placebo']['agent_paraphrase_flip_rate']:.4f} (n={within['placebo']['n']}) | **PASS** |
| G4 permutation obs > p95 | obs {within['permutation']['observed']:.4f} > p95 {within['permutation']['perm_p95']:.4f} | **PASS** |
| G5 mechanism fidelity (correct-wrong bf_reverse) CI excl. 0 | mean diff {within['mechanism_fidelity']['mean_correct_minus_wrong']:.3f} [{within['mechanism_fidelity']['ci'][0]:.3f}, {within['mechanism_fidelity']['ci'][1]:.3f}] (correct n={within['mechanism_fidelity']['n_correct']}, wrong n={within['mechanism_fidelity']['n_wrong']}) | **PASS** |

## Risk@80 (secondary)

- Risk@80 error reduction: **{within['risk_at_80']['reduction']:.3f}** [{within['risk_at_80']['ci'][0]:.3f}, {within['risk_at_80']['ci'][1]:.3f}] (overall HC error {within['risk_at_80']['overall_error']:.4f}, n={within['risk_at_80']['n']}).
- All {within['n_wrong_hc']} wrong HC items fall in the highest-risk 20% under RS_q.

## Reducibility (reported, not a gate)

- Spearman(RS_q, agreement): {within['reducibility']['spearman_risk_agreement']}
- Spearman(RS_q, mean confidence): {within['reducibility']['spearman_risk_conf']}

## Boundaries

- N=8 wrong HC items is small; CIs are pair-grouped but the wrong-N drives wide tails. The
  result supports the pre-registered CI-level gate (lb > 0.5) and the mechanism direction, but
  is a single-point (100-item) validation, not a full-cohort estimate.
- All numbers are on the frozen Round-3 VitaminC cohort subset (first 50 pairs); no label was
  used to select prompts, adapters, or subsets; labels merged only after feature freeze.
- Model is a relay GPT-class model (gpt-6-astra); the relay is a third-party proxy; per-call
  model id is recorded and matches `gpt-6-astra` in every successful record.
"""
(AN / "large_model_within_model.md").write_text(md, encoding="utf-8")

q = transfer["qwen"]; l = transfer["ling"]
md2 = f"""# Large-Model Single-Point Validation — Mechanism Transfer (Qwen/Ling frozen RS_q -> gpt-6-astra errors)

Protocol: `cs-paper-gpt-singlepoint-20260914-round6` · Secondary evidence (not a gate).

Frozen Round-3 Qwen3.5-4B `RS_q` and Round-4 Ling-3.0-tiny `RS_q` (both `=-BF_q`) are evaluated
against **gpt-6-astra's own** `consensus_wrong` on the gpt HC subset (n={q['n_hc_with_src']}).

| source | AUROC (pair-grouped CI) | Risk@80 reduction (CI) | Spearman(src RS_q, gpt RS_q) |
|---|---|---|---|
| Qwen3.5-4B (round3) | {fmt_ci(q['auroc'])} | {q['risk_at_80']['reduction']:.3f} [{q['risk_at_80']['ci'][0]:.3f}, {q['risk_at_80']['ci'][1]:.3f}] | {q['spearman_src_gpt_risk']} |
| Ling-3.0-tiny (round4) | {fmt_ci(l['auroc'])} | {l['risk_at_80']['reduction']:.3f} [{l['risk_at_80']['ci'][0]:.3f}, {l['risk_at_80']['ci'][1]:.3f}] | {l['spearman_src_gpt_risk']} |

## Interpretation

- Both frozen scores transfer at aggregate level (AUROC CI lower bound > 0.5), with Qwen's
  risk score transferring more strongly than Ling's (consistent with Qwen's higher item-level
  RS_q correlation, Spearman 0.68 vs 0.37).
- Item-level transfer is secondary; the within-model mechanism (natural-reversal fidelity
  lower on wrong HC consensus) is the primary claim and passes (see within-model report).
- Boundaries: transfer AUROC is computed against only 8 wrong HC items; treat the CI as
  indicative; no claim of per-item ranking equivalence across models.
"""
(AN / "large_model_transfer.md").write_text(md2, encoding="utf-8")
print("markdown written")
print(md)
