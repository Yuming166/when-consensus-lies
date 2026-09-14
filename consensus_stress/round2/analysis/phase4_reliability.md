# Phase 4 — Reliability Modeling (combined pilot+confirmation, no new calls)

Protocol: cs-phase4-reliability-20260913 (frozen before analysis). Combined high-consensus:
289 items, 47 wrong (16.3%). Target: consensus_wrong. Risk form RS_q = -BF_q (higher=riskier).

## AUROC (pair-grouped bootstrap, 2000 replicates)

| representation | AUROC [95% CI] | paired diff vs RS_q [CI] |
|---|---|---|
| RS_q = -BF_q (expected-response faithfulness) | 0.906 [0.865, 0.944] | — |
| logistic (5-fold pair-grouped OOF on {para,rev}) | 0.837 [0.752, 0.906] | +0.069 [+0.019, +0.135] |
| R_sym (frozen) | 0.845 [0.798, 0.890] | +0.060 [+0.026, +0.100] |
| R_PI (frozen) | 0.659 [0.600, 0.720] | +0.246 [+0.196, +0.301] |
| disagreement (1-agreement) | 0.573 [0.516, 0.633] | +0.333 [+0.275, +0.394] |
| conf_dispersion | 0.468 [0.379, 0.558] | +0.438 [+0.349, +0.529] |
| mean confidence | 0.324 [0.255, 0.394] | +0.582 [+0.506, +0.662] |

## Risk@80 (retain bottom 80% by risk; error reduction vs overall 16.3%)

| representation | reduction [95% CI] |
|---|---|
| RS_q | 0.654 [0.299, 0.892] |
| logistic OOF | 0.494 [0.191, 0.762] |
| R_sym | 0.281 [0.012, 0.592] |
| R_PI | 0.148 [-0.120, 0.407] |
| disagreement | 0.148 [-0.128, 0.390] |
| mean confidence | -0.171 [-0.470, 0.125] |

## Calibration

Isotonic regression on RS_q (OOF split): ECE 0.053 (min-max-normalized raw) -> 0.013 (calibrated);
AUROC unchanged by design (monotone transform). Logistic OOF AUROC (0.837) is LOWER than the
simple frozen composite BF_q (0.906): no fitted-model benefit at pilot scale; the simple
interpretable representation suffices.

## Reading

The expected-response faithfulness representation (BF_q / RS_q) dominates every baseline on
AUROC (all paired-diff CIs exclude 0) and is the only representation with a strong Risk@80
error reduction (65%, CI lower bound 29.9%). It also beats a fitted logistic on the same two
interventions, supporting the framework's claim that the CONCEPT (expected-response
faithfulness with a decision-relevance-aware oracle), not extra fitting, carries the signal.

## Boundaries

- Logistic evaluated via pair-grouped 5-fold CV (no held-out test beyond the folds; OOF).
- Pilot-scale cohort (289 HC); Gate-4 formal thresholds (Risk@80 at the preregistered
  operating point with strict CI gates) belong to a paper-scale protocol on a larger cohort.
