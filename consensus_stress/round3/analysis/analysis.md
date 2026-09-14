# Round 3 Paper-Scale — Gate 2 + Phase 4 Report (VitaminC, Qwen3.5-4B)

Protocol: `cs-paper-vitaminc-2026-09-13` (frozen before any model call). 300 fresh natural
pairs (600 items), label-symmetric (300 SUPPORTS + 300 REFUTES), page- and pair-disjoint
from round 2 (150 pairs) and from frozen V3.16/V3.16.1 pages. Eligibility broadened to
character_ratio >= 0.85 AND token_jaccard >= 0.70 (one pair per page) to reach paper scale;
contrast median 0.95 / 0.84. Risk form RS_q = -BF_q (higher = riskier).

## Pipeline

- Paraphrase artifacts: 900/900 units usable (1 citation-heavy distractor swapped
  deterministically before any call; documented in artifacts_repair_note.md).
- Agent calls: 15,000/15,000 records, 14,999 valid (99.99%; one reverse call failed after
  retry — single missing agent feature for that item). Stage1 99.99%, Stage2 100%.
- Paraphrase audit: 30/30 meaning-preserving (100%); relevance audit: 30/30 decision-relevant.
- Preoutcome features frozen (600 items, no label fields) before label merge.

## Population (high-consensus, agreement >= 0.8)

- 567 HC items (94.5% of 600); 65 wrong (11.5%): SUPPORTS 7/283 (2.5%), REFUTES 58/284 (20.4%).
- REFUTES items are the hard cases; the label-symmetric design exposes this asymmetry.

## Gate 2 (paper scale) — ALL 8 GATES PASS

| gate | frozen | observed | pass |
|---|---|---|---|
| G1 pipeline valid | >= 0.95 | 0.9999 | YES |
| G2 primary AUROC(RS_q, wrong\|HC) | CI lb>0.5, point>=0.60 | 0.943 [0.924, 0.960] | YES |
| G3 macro-label | CI lb>0.5 | 0.952 [0.904, 0.995] | YES |
| G4 worst-label (SUPPORTS) | **CI lb>0.5** (CI-level) | 0.917 [0.819, 0.999] | YES |
| G5 placebo | para flip <= 0.30 | 0.038 | YES |
| G6 permutation | obs > 95th pct | 0.943 > 0.596 | YES |
| G7 reducibility | Spearman<0.9; agr==0.8 AUROC>0.5 | -0.004 / -0.161; 0.844 | YES |

## Phase 4 — AUROC (pair-grouped bootstrap, 2000 replicates)

| representation | AUROC [95% CI] | paired diff vs RS_q [CI] |
|---|---|---|
| **RS_q = -BF_q** | **0.943 [0.924, 0.960]** | — |
| logistic OOF {para,rev} | 0.941 [0.922, 0.959] | +0.002 [-0.002, +0.007] (tie) |
| R_sym (frozen) | 0.892 [0.861, 0.921] | +0.051 [+0.029, +0.075] |
| R_PI (frozen) | 0.628 [0.586, 0.670] | +0.315 [+0.271, +0.360] |
| disagreement | 0.583 [0.536, 0.630] | +0.360 [+0.306, +0.413] |
| confidence | 0.272 [0.226, 0.321] | +0.671 [+0.620, +0.723] |

## Phase 4 — Risk@80 (retain lowest-risk 80%; strict CI gate)

| representation | reduction [95% CI] |
|---|---|
| **RS_q** | **0.846 [0.638, 0.981]** — CI lb > 0 (strict gate PASS) |
| R_sym | 0.499 [0.273, 0.770] |
| R_PI | -0.001 [-0.235, 0.271] (n.s.) |
| disagreement | 0.095 [-0.076, 0.388] (n.s.) |
| confidence | -0.232 [-0.511, 0.039] (n.s.) |

Risk@80 paired diffs (RS_q minus baseline): vs R_sym **+0.347 [+0.152, +0.502]**,
vs R_PI **+0.847 [+0.677, +0.984]**, vs confidence +1.078, vs disagreement +0.751.

## Gate 4 — ALL GATES PASS

- P1 Risk@80 CI lb > 0: 0.638 -> PASS.
- P2 AUROC diff vs R_sym CI lb > 0: 0.029 -> PASS.
- P3 AUROC diff vs R_PI CI lb > 0: 0.271 -> PASS.
- P4 Risk@80 diff vs R_sym CI lb > 0: 0.152 -> PASS.
- P5 Risk@80 diff vs R_PI CI lb > 0: 0.677 -> PASS.
- P6 isotonic ECE 0.057 -> 0.013 (reported).

## Calibration / modeling

- Isotonic calibration of RS_q (OOF): ECE 0.057 -> 0.013; AUROC unchanged by design.
- Frozen composite BF_q (0.943) ties the fitted logistic OOF (0.941, paired diff CI
  includes 0): the concept (expected-response faithfulness with decision-relevance-aware
  oracle), not extra fitting, carries the signal.

## vs round-2 baseline (must maintain/exceed)

| metric | round2 combined (289 HC) | round3 paper-scale (567 HC) |
|---|---|---|
| AUROC(RS_q, wrong\|HC) | 0.906 [0.865, 0.944] | 0.943 [0.924, 0.960] |
| Risk@80 reduction | 0.654 [0.299, 0.892] | 0.846 [0.638, 0.981] |
| paired diff vs R_sym | +0.060 [+0.026, +0.100] | +0.051 [+0.029, +0.075] |
| paired diff vs R_PI | +0.246 [+0.196, +0.301] | +0.315 [+0.271, +0.360] |

The paper-scale result maintains/exceeds the round-2 baseline on AUROC and Risk@80 and
shows significant, CI-confirmed gains over frozen R_sym and R_PI (Phase 4 P2-P5).

## Boundaries

- SUPPORTS worst-label CI is wide (7 wrong items) but passes at CI level.
- REFUTES items dominate the error mass (20.4%); the effect holds in both labels.
- Qwen3.5-4B / VitaminC only; cross-model and cross-dataset in round-3 Phase 6.
