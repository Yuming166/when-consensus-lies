# When Consensus Lies — Curated Data & Documents

A curated companion repository for the **"When Consensus Lies"** research line:
*as-of provenance faithfulness for reliable multi-agent LLM decisions under
distribution shift*, with S&P 500 as a sequential, as-of-constrained testbed.

This repository intentionally contains **experiment data and documents only**
(no code, no runtime logs, no model caches). It is the clean showcase of the
project; the full working tree lives in
[`Yuming166/SP500_ML`](https://github.com/Yuming166/SP500_ML).

## In one paragraph

When several LLM agents agree, the agreement can be false consensus caused by
shared evidence, stale evidence, or behaviorally irrelevant citations. We make
the evaluation environment responsible for evidence identity and provenance:
five fixed personas receive controlled evidence views, and the environment
applies paired `remove` / `reverse` / `substitute` interventions without
inspecting hidden chain-of-thought. From observable answer changes and citation
overlap we freeze an outcome-independent risk score (`R_PI`, later the
label-symmetric `R_sym`) before any label is revealed, and test whether it can
rank wrong high-consensus decisions *before the outcome is known*. S&P 500 is
used as a demanding sequential testbed with as-of provenance constraints — not
as a financial-alpha claim.

## Key results (with explicit claim boundaries)

| # | Experiment | Verdict | Core numbers | Boundary |
|---|---|---|---|---|
| 1 | Synthetic V3 (fixed conditional-provenance score, leave-one-mechanism-out) | **PASS** | AUROC 0.977 [0.971, 0.982]; AURC 0.233 | Holds on held-out corruption mechanisms; matched-coverage analysis is explicitly post-hoc |
| 2 | Synthetic V4 (learned monotonic provenance router) | **FAIL (primary)** | ECE 0.074 (best); AURC 0.316; Risk@80 0.447 | Better calibration than baselines, but behind fixed V3 (0.235 / 0.440); drifts when evidence-inertia is fully held out |
| 3 | BoolQ real-LLM replication, Qwen3.5-4B (V12.1, 358 q / 7,160 calls, frozen `R_PI`) | **PASS** | AUROC 0.705 [0.620, 0.781]; Risk@80 error 0.220 → 0.133 (−0.087) | Label subgroups reverse (yes 0.834 / no 0.213); citation sharing alone at chance |
| 4 | Ling-3.0-tiny replication of the frozen Qwen protocol (V3.15.2) | **PASS aggregate-only** | AUROC 0.640 [0.558, 0.717]; Risk@80 0.194 → 0.145 | Worst-label gate fails (0.120); aggregate cross-family replication only, not label-invariant |
| 5 | VitaminC fresh natural-pair replication, Qwen + Ling (V3.16.1, 23,120 calls, frozen `R_sym`) | **PASS** | Qwen AUROC 0.839 [0.802, 0.873]; Ling 0.727 [0.689, 0.764]; Risk@80 gains +0.057 / +0.042 | Item-level risk Spearman only 0.294 → aggregate behavioral-signal transfer, not universal transfer |
| 6 | S&P 500 LLM replay V1→V2 (Hy-MT2-7B, 500 decision dates, 10,000 calls) | **FAIL (routing endpoint, twice)** | V1 AURC diff −0.0874 [−0.199, +0.074]; V2 +0.032 [−0.089, +0.181] | V1 risk ECE 0.055 (best calibrated); prompt-only repair lifted paired validity 68.2% → 75.6% (sign test p ≈ 7×10⁻⁹). No alpha / predictability / routing-superiority claim |

**Non-claims.** No result in this repository establishes universal factuality,
citation sufficiency, live-retrieval robustness, S&P 500 alpha, or prospective
trading performance. Every unfavorable result above is preserved in the formal
records.

## Repository layout

```
data/
  market/        S&P 500 / ETF daily prices, VIX, macro, sentiment,
                 put/call ratio, mutual-fund flows (snapshot ~2026-05)
  benchmarks/    BoolQ (parquet), VitaminC (test.jsonl), FEVER validation subset
docs/
  paper/         ACL draft v2 (markdown + compiled PDF) and figures
  protocols/     Preregistrations for the formal experiments
  results/       Formal result reports (failures preserved)
  research_brief.md                    One-page brief for faculty meetings
  asof_provenance_faithfulness.md      Core methodology
  data_contract.md                     Data / leakage-prevention contract
```

## Data provenance

- Market data: public daily price/volume and fund-flow snapshots (SPY, IVV,
  VOO, VIX, CBOE, ICI), as-of aligned; see `data/market/READ_ME数据说明.rtf`.
- BoolQ / VitaminC / FEVER: standard public research datasets, redistributed for
  research use under their original licenses (see
  `data/benchmarks/vitaminc/LICENSE`).

## Disclaimer

Research and education only. Not investment advice.
