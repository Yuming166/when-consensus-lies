# Phase 3 — Consensus Stress Benchmark (discrete axes, sketch from frozen records)

Protocol note: Phase 3 was planned as a continuous stress knob. Within this round's budget, a
DISCRETE evidence-semantics axis is evaluated from the already-frozen records (zero new calls):
original -> paraphrase (semantic-preserving) -> synthetic_reverse (weak change)
-> reverse (natural counter-evidence swap, strong decision-relevant change)
-> remove (evidence removal). Registry: appended (phase3-sketch).

## Combined cohort (pilot + confirmation), high-consensus, by correctness

| condition | mean agreement (correct n=242 / wrong n=47) | expected-response fidelity (correct / wrong) |
|---|---|---|
| original | 0.991 / 0.962 | — (reference) |
| paraphrase | 0.994 / 0.953 | 0.987 / 0.915 |
| synthetic_reverse | 0.894 / 0.898 | 0.429 / 0.540 |
| reverse | 0.967 / 0.987 | **0.794 / 0.119** |
| remove | 0.993 / 0.987 | — (no-forced-response) |

## Reading

1. Agreement under strong reversal separates only weakly (0.967 vs 0.987): correct consensus
   flips appropriately as a group; wrong consensus stays rigid. The expected-response
   fidelity lens is the strong separator (0.794 vs 0.119) — "the model changed appropriately"
   matters, not merely "the model changed".
2. Placebo (paraphrase) is clean in both groups; wrong consensus is slightly less stable
   (0.915 vs 0.987) but the dominant signature is unresponsiveness to the decision-relevant
   reversal, not general instability.
3. The synthetic negation prefix is a weak stress (fidelity ~0.43-0.54) and does not separate
   (wrong slightly HIGHER), confirming that a decision-relevance-aware natural reversal is the
   informative axis (round-1 lesson).

## Boundary

This is a discrete 5-point profile on Qwen3.5-4B. A continuous lambda grid (fraction of units
reversed/removed) and breakpoint/robustness-radius summaries remain for a future budget
(Phase 3 full), with a pre-registered protocol and fresh calls.
