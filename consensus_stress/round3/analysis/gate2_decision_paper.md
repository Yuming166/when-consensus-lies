# Gate 2 (paper scale) Decision — PASS

Protocol: `cs-paper-vitaminc-2026-09-13` (frozen before any model call). 300 fresh
VitaminC natural pairs (600 items), label-symmetric, page+pairs disjoint from round 2 and
V3.16/V3.16.1. Risk form RS_q = -BF_q (higher = riskier), frozen before calls.

## Verdict: PASS (all 8 frozen gates)

| gate | frozen | observed | pass |
|---|---|---|---|
| G1 pipeline | valid >= 0.95 | 0.9999 (14,999/15,000) | YES |
| G2 primary AUROC(RS_q, wrong\|HC) | CI lb > 0.5, point >= 0.60 | 0.943 [0.924, 0.960] | YES |
| G3 macro-label | CI lb > 0.5 | 0.952 [0.904, 0.995] | YES |
| G4 worst-label (SUPPORTS) | CI lb > 0.5 (CI-level) | 0.917 [0.819, 0.999] | YES |
| G5 placebo | paraphrase flip <= 0.30 | 0.038 | YES |
| G6 permutation | obs > 95th pct | 0.943 > 0.596 | YES |
| G7 reducibility | Spearman < 0.9; agr==0.8 AUROC > 0.5 | -0.004 / -0.161; 0.844 | YES |

## Phase 4 (formal) — PASS

- P1 Risk@80 CI lb > 0: 0.846 [0.638, 0.981] -> PASS.
- P2/P3 AUROC paired diffs vs R_sym +0.051 [+0.029, +0.075], R_PI +0.315 [+0.271, +0.360] -> PASS.
- P4/P5 Risk@80 paired diffs vs R_sym +0.347 [+0.152, +0.502], R_PI +0.847 [+0.677, +0.984] -> PASS.
- P6 isotonic ECE 0.057 -> 0.013 (reported).

## Phase 3 (continuous lambda) — PASS (reversal axis)

- Stress-area AUROC(RS_stress, wrong|HC) = 0.948 [0.925, 0.968]; wrong consensus rigid
  at every lambda (robustness radius 1.0, no breakpoint for 22/22).

## Reading

The paper-scale cohort confirms and exceeds the round-2 baseline: the expected-response
faithfulness representation (frozen composite BF_q / RS_q) ranks consensus errors with
AUROC 0.943 (round 2: 0.906), cuts errors at 80% coverage by 85% (round 2: 65%), and is
significantly better than frozen R_sym and R_PI on both AUROC and Risk@80 with
CI-confirmed paired differences, label-symmetric, placebo-clean, permutation-validated,
CI-level worst-label-gated, and reducibility-safe. Phase 3 gives the continuous stress
curve with per-question breakpoint/robustness-radius support.

## Boundaries (honest)

- SUPPORTS worst-label CI is wide (7 wrong items) but passes at CI level.
- REFUTES items carry 89% of the error mass (58/65); the effect holds in both labels.
- Qwen3.5-4B/VitaminC only; cross-model (Ling) and cross-dataset (BoolQ/FEVER) reported
  separately in Phase 6 (both honest negatives / blocked this round).
