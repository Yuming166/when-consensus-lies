# Gate 2 Decision (Confirmation cohort) — PASS

Protocol: cs-pilot-vitaminc-conf-2026-09-13. Date: 2026-09-13.

## Verdict: PASS (all 7 frozen corrected gates)

| criterion | frozen | observed | pass |
|---|---|---|---|
| pipeline | >= 0.95 | 1.00 | YES |
| primary AUROC(RS_q=-BF_q, wrong\|HC) | CI lb > 0.5, point >= 0.60 | 0.912 [0.848, 0.973] | YES |
| macro-label | CI lb > 0.5 | macro 0.912; CI [0.759, 0.972] | YES |
| worst-label | point > 0.5 | SUPP 0.788 / REF 0.968 (worst 0.788) | YES |
| C1 placebo | paraphrase flip <= 0.30 | 0.050 | YES |
| C2 permutation | obs > 95th pct | 0.912 > 0.699 | YES |
| reducibility | not a copy of agreement/confidence | Spearman -0.39 / -0.21; agr==0.8 AUROC 0.70 | YES |

## Gate 2 (round 2) final: PASS

- Pilot cohort (cs-pilot-vitaminc-2026-09-13): substantive direction confirmed
  AUROC(-BF_q, wrong) = 0.901 [0.847, 0.946] (as-written numeric gate FAIL due to a
  preregistration sign defect — documented, not repaired).
- Confirmation cohort (cs-pilot-vitaminc-conf-2026-09-13): ALL corrected gates PASS.
- Two independent, pre-registered, disjoint cohorts show the same direction-consistent,
  label-symmetric, placebo-clean, permutation-validated effect; the expected-response
  faithfulness profile (unresponsive/unstable consensus => risky) distinguishes correct from
  false high-consensus answers beyond confidence/agreement and beyond frozen R_PI/R_sym.

## Caveats (honest boundaries)

- The pilot's as-written gate failed; the corrected gate was frozen before the confirmation
  cohort's agent calls (not re-gated post-hoc on the pilot).
- SUPPORTS-subgroup wrong items in the confirmation cohort are few (2), so its worst-label
  CI is wide ([0.565, 0.957]); the point-level worst gate passes but a full-scale cohort would
  use a CI-level worst gate (V3.16.1 style).
- Effect sizes are cohort-level on Qwen3.5-4B only; cross-model replication (Phase 6) is not
  yet done.
