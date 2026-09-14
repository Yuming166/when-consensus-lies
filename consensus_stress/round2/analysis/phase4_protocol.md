# Phase 4 — Reliability Modeling Protocol (frozen before analysis)

Protocol id: `cs-phase4-reliability-20260913`. Status: frozen before any Phase-4 analysis.
Uses ONLY already-frozen preoutcome features (pilot + confirmation); zero new model calls.

## Population
- Combined high-consensus items (agreement >= 0.8) from cs-pilot-vitaminc-20260913 (195)
  and cs-pilot-vitaminc-conf-20260913 (94): 295 items, 47 consensus_wrong (15.9%).
- Target: consensus_wrong (label merged only after features were frozen).

## Representations compared (all from preoutcome features)
1. BF_q (frozen composite, mean over agents of {paraphrase, reverse} faithfulness);
   risk form RS_q = -BF_q (higher = riskier).
2. Logistic regression on {bf_paraphrase, bf_reverse} -> P(wrong); fit inside pair-grouped
   5-fold CV (fold on pairs), OOF predictions; report AUROC of OOF P(wrong).
3. Isotonic regression on RS_q (OOF-calibrated); report ECE (raw vs calibrated) and note that
   isotonic is monotone so AUROC equals RS_q.
4. Baselines (frozen): R_PI, R_sym, mean_confidence, disagreement = 1 - agreement,
   conf_dispersion.

## Endpoints
- AUROC with pair-grouped bootstrap 95% CI (2000 replicates, seed 20260913).
- Paired bootstrap diffs: RS_q - each baseline.
- Risk@80: retain bottom 80% by risk score; error reduction = 1 - retained_error / overall_error;
  pair-grouped bootstrap CI for reduction (pass if CI lower bound > 0).
- Logistic: 5-fold pair-grouped CV, folds by pair hash, deterministic seed.

## Frozen decision rule (Phase 4 gate, informative only)
Report all comparisons with CIs; no single pass/fail gate (Gate 4 formal thresholds belong to
the paper-scale protocol). The Phase-4 result is descriptive/exploratory on the pilot-scale
cohort.
