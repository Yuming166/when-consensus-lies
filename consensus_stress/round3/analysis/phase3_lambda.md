# Phase 3 — Continuous Lambda Stress (full version)

Protocol: `cs-paper-vitaminc-2026-09-13` section 7 (frozen before calls). 120-pair
deterministic subset (240 items) of the 300-pair main cohort; lambda grid
{0.2, 0.4, 0.6, 0.8} with anchors at 0 (original) and 1 (reverse/remove) from main records.
Reversal axis: each decision-relevant unit in the agent view is replaced by its natural
counter-evidence with probability lambda (seeded). Removal axis: each decision-relevant
unit is removed with probability lambda (seeded). 9,600 fresh calls; valid rate 0.9982.

## Reversal axis (primary) — strong, direction-consistent

- Mean agent flip probability vs lambda: correct consensus 0 → 0.18 → 0.35 → 0.49 →
  0.70 → 0.85; wrong consensus 0 → 0.02 → 0.05 → 0.05 → 0.08 → 0.12.
- **Stress area AUROC(RS_stress = -stress_area, wrong | HC) = 0.948 [0.925, 0.968]**
  (pair-grouped, CI lb > 0.5; gate PASS).
- Mean stress area: correct 0.436 vs wrong 0.032 (correct consensus is ~14x more
  responsive to gradual natural reversal).
- Breakpoint (smallest lambda where the consensus flips): correct mean 0.555;
  **22/22 wrong consensus NEVER flip at any lambda in [0,1]** (rigid);
  31/203 correct never flip.
- Robustness radius: correct 0.623 vs wrong 1.000 (wrong consensus keeps the original
  answer at every stress level).

## Removal axis (secondary, descriptive)

- Mean flip probability under removal: correct 0.245 vs wrong 0.383 — wrong consensus is
  MORE unstable under removal (prior-driven answers wobble when decisive evidence is
  removed), the opposite signature of the reversal axis.
- Robustness radius under removal: correct 0.793 vs wrong 0.618.
- Reported descriptively only (per preregistration, reversal is the primary axis).

## Reading

The continuous curve adds per-question granularity to the round-2 discrete finding:
correct consensus responds proportionally to natural evidence reversal (flip probability
rises smoothly with lambda), while false consensus is rigid at every lambda (robustness
radius 1.0, no breakpoint). Stress area is a strong, frozen, outcome-free consensus-risk
feature (AUROC 0.948), consistent with the main cohort's BF_q result (0.943).
