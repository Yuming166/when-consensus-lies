# Outcome Firewall (Phase 0 audit)

Audit date: 2026-09-12. This file defines the mandatory separation between
pre-outcome (probe/score construction) and post-outcome (evaluation) stages for
the consensus-stress-testing program. It codifies what the frozen project already
does (sealed outcome ledger, outcome-free public manifest, forbidden score inputs).

## 1. Outcome variables that are firewalled

- ground-truth labels (`gold_binary`, `label`, `answer` gold value, SUPPORTS/REFUTES)
- correctness / error indicators (`correct`, `consensus_wrong`, `harmful_fc`, `any_wrong`)
- any derived outcome statistic computed from labels (e.g., label-group AUROC used
  during score selection)

## 2. Allowed inputs to probes / risk scores (pre-outcome only)

- agent answers, confidence, cited evidence IDs (observable responses)
- evidence packet contents and identities (environment-held)
- intervention definitions (transformation semantics), frozen before model calls
- provenance graph (source root -> evidence item -> agent view -> cited evidence -> decision)
- aggregate observable statistics: agreement, disagreement, flip/inertia rates,
  intervention response vectors, expected-response faithfulness

## 3. Forbidden inputs (never allowed in score/probe construction)

- any label field or correctness field (mirrors frozen R_PI forbidden set:
  label, gold_binary, correct, any_wrong, harmful_fc)
- any value read from the outcome ledger before pre-outcome routes are frozen

## 4. Frozen project mechanisms this program inherits

1. Dataset labels may be used ONLY to construct and audit a balanced/contrastive
   selection and to generate frozen intervention artifacts (e.g., V10 substitute
   generation which uses the gold answer to write opposite-supporting evidence).
   This is offline dataset construction, performed before any agent model call,
   and the artifacts are frozen. It is NOT test-time probe selection.
2. Outcome-free public manifest + sealed outcome ledger are built and hashed before
   agent model calls (V3.16.1 pattern).
3. Pre-outcome routes (high-consensus IDs, risk scores, retained/abstained IDs) are
   frozen before the outcome ledger is opened.
4. Only after all pre-outcome routes are frozen are labels evaluated.

## 5. Consensus-stress program additional firewall rules (hard)

- F1. Expected-response definitions are declared in the preregistration from the
  transformation semantics alone (same-answer for semantic-preserving; flip for
  polarity reversal; no-forced-response for removal/weak perturbation). They are
  frozen before agent responses are read. Rule 7 of the plan (no redefining
  expected response post-hoc) applies.
- F2. No label/correctness value may select which probe to run at test time
  (plan Rule 6).
- F3. No score weight or threshold is tuned on test-set labels or test-set
  correctness (plan Rule 5).
- F4. Permutation / placebo controls are pre-registered with the same endpoint as
  the primary analysis and reported regardless of outcome.
- F5. If a new method uses more inference calls than the baseline, it is compared
  at matched inference budget (plan Rule 9).
- F6. The gold label may be used only for the FINAL evaluation of frozen routes,
  never for construction. Every artifact that touches a label before freeze is
  listed in the experiment registry.

## 6. Gate discipline

- Any preregistered gate that fails is recorded as FAIL/INVALIDATED/INCONCLUSIVE in
  the registry and retained. A new cohort may be designed, but the original cohort
  is never silently repaired (plan Rule 8).
- Positive results require an independent reproduction or falsification attempt
  (plan Rule 10).
