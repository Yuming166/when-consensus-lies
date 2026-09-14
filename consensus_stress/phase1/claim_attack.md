# Phase 1 — Claim Attack (adversarial novelty/correctness review)

Audit date: 2026-09-12. Purpose: attempt to destroy each candidate claim before Phase 2.

## Attack 1: "Expected-response faithfulness is new"
- Attack: it is a re-labeling of intervention flip rate / inertia (already in R_PI and R_sym).
  Concretely, faithfulness_reverse = 1 - reverse_flip_rate; faithfulness_substitute =
  1 - substitute_flip_rate. A weighted sum of these would reproduce R_sym's ingredients.
- Response: accepted as partially true. The measurement's defensible novelty is (a) the
  pre-registered transformation-derived oracle (Y* = Y0 / flip(Y0) / no-forced-response) applied
  to BOTH semantic-preserving and semantic-changing axes jointly, and (b) the consensus-level
  aggregation into a faithfulness profile. The empirical claim (error prediction beyond RPI/Rsym)
  must be established in Phase 4, not asserted.
- Kill condition: if BF features add no error-prediction signal beyond RPI/Rsym/confidence/
  disagreement under the frozen protocol -> retain as behavioral analysis only.

## Attack 2: "Consensus stress testing is just metamorphic testing / CheckList on agents"
- Attack: METAL/CheckList already apply transformations and check expected properties.
- Response: partially true for the technique. The differentiator is the OBJECT (already-formed
  multi-agent consensus) and the USE (outcome-blind ranking of consensus error, i.e., selective
  prediction), not the transformation technique. CheckList does not rank future errors before
  labels; it tests capabilities.
- Kill condition: if the stress profile does not predict consensus error at all -> the "stress
  testing" framing collapses to descriptive behavioral analysis.

## Attack 3: "Stress curve is an ROC curve / AURC relabeled"
- Attack: area under curve and breakpoints are standard summary statistics; the risk-coverage
  curve already exists in this project.
- Response: risk-coverage varies the routing threshold at fixed evidence; a stress curve varies
  the evidence stress level at fixed routing. Distinct axis, but both produce AURC-style
  summaries. The stress-curve claim must show the trajectory itself (shape) adds signal beyond
  the scalar summary, or the claim should be downgraded to "stress profile scalar".
- Kill condition: if scalar summaries of the trajectory do not add anything over single-point
  features -> keep only the scalar, drop the curve claim.

## Attack 4: "Robustness-responsiveness map is a 2D feature vector"
- Attack: any 2D scatter (stability, flip) is trivially constructible from raw answers.
- Response: accepted; the map is an interpretability layer. Primary novelty stays with C1/C2.
- Kill condition: none (kept as analysis), but it cannot be sold as a standalone contribution.

## Attack 5: "Active probing is new"
- Attack: active testing/evaluation and active learning already select informative actions;
  adaptive sequential testing exists.
- Response: the setting (evidence interventions on a formed consensus, label-blind acquisition)
  is a specific instance; novelty is contingent on the reliability-per-budget comparison beating
  fixed probing. Rule 9 (matched budget) applies.
- Kill condition: if fixed probing at equal budget is not beaten -> drop active-probing claim.

## Attack 6 (label leakage / outcome firewall)
- Attack: expected response Y* = flip(Y0) uses the model's own original answer Y0, which is
  pre-outcome and allowed. But if the substitute artifact were generated using the gold label
  (V10 does this), is that leakage?
- Response: substitute generation uses dataset labels OFFLINE to construct the frozen artifact
  (opposite-supporting evidence). This is dataset construction, frozen before model calls, and
  identical to the frozen project's V10/V12 practice. The agent responses and all scores use only
  observable outputs + frozen artifacts. The label is never an input to probing or scoring.
  Still, the risk that "substitute expected flip" is label-coupled is real; the placebo and
  permutation controls plus a label-free paraphrase axis mitigate it. We also report the
  no-label asymmetry known from BoolQ.

## Attack 7 (placebo validity)
- Attack: if the LLM paraphrase accidentally changes meaning, the "semantic-preserving" axis is
  invalid, and flip-under-paraphrase would be mis-scored as unfaithful.
- Response: paraphrase artifacts are frozen before agent calls; we record the paraphrase flip
  rate as a control diagnostic. If paraphrase flip rate is high (> some threshold), we report it
  as a control violation and restrict claims accordingly (plan Attack 10 / Gate 2 null control).

## Attack 8 (power / sample adequacy)
- Attack: 50-100 BoolQ questions yield ~10-20 high-consensus errors; AUROC CIs will be wide.
- Response: the pilot is a pipeline + phenomenon check (Gate 2), not the final Phase 4 comparison.
  Sample size, expected error counts, and the decision rule (advance only if effect direction is
  consistent AND controls pass) are pre-registered before model calls.

## Falsification experiment (what would make the claim false)
- Null: BF_q has AUROC CI that includes 0.5 on the high-consensus subset, or permutation control
  shows the same signal as random, or the placebo control shows instability that drives the
  signal. Any of these kills C1/C2 as an error-prediction claim.

## Gate 1 decision
- C2 (Consensus Stress Testing) and C1 (expected-response faithfulness at consensus level) survive
  the attack with differentiated, empirically-testable claims.
- C3/C4 survive as secondary representations; C5 survives only as contingent future work.
- Proceed to Phase 2 pilot with these claims and the falsification plan above.
