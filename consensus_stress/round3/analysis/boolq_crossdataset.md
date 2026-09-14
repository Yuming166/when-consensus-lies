# Phase 6 — Cross-Dataset Balanced BoolQ: HONEST FAIL (specificity boundary)

Protocol: `cs-paper-boolq-20260913` (frozen before calls). Fresh 50-yes/50-no cohort
from boolq/train.parquet (100 items), frozen V10 3-unit evidence extraction, same
personas/partition/oracle, conditions original/paraphrase/reverse/remove. BoolQ has no
natural counter-evidence; reverse = negation prefix (frozen V10), documented in the
protocol. 600 paraphrase + 2,000 agent calls; pipeline valid 100%.

## Result

- HC 85/100 (85%), wrong 23 (27%): yes 16/40 (40%), no 7/45 (16%).
- **Primary AUROC(RS_q = -BF_q, wrong | HC) = 0.449 [0.308, 0.579] — direction REVERSED
  (below 0.5). Gate 2 cross-dataset FAILS (G2/G3/G4/G6).**
- Label subgroups diverge: no 0.073 [0.005, 0.169] vs yes 0.745 [0.579, 0.889] — the
  round-1 BoolQ answer-prior confound reproduces in risk orientation.
- Risk@80(RS_q) = 0.239 [-0.467, 0.348] (n.s.); paired diff vs R_PI = -0.097
  [-0.182, -0.009] (RS_q WORSE than R_PI on BoolQ); permutation fails (0.449 < 0.612).
- Placebo clean (0.052); pipeline valid 100%.

## Diagnosis (honest)

- The mechanism does not transfer to BoolQ because the frozen oracle's reverse axis is
  synthetic (negation prefix), not natural counter-evidence. Round 2 already showed the
  synthetic-reversal axis is weak/non-separating on VitaminC; BoolQ has no natural
  counter-evidence at all, and its strong answer-prior confound re-emerges.
- This is a SPECIFICITY result, not a contradiction of the main finding: it supports the
  causal claim that the risk signature is specifically "unresponsive to genuine natural
  evidence reversal", not "unresponsive to any perturbation". No parser/oracle/gate was
  changed; the negative is retained.
