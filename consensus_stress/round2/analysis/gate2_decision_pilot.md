# Gate 2 Decision (Pilot cohort) — VitaminC natural pairs, Qwen3.5-4B

Protocol: cs-pilot-vitaminc-2026-09-13. Date: 2026-09-13.

## Verdict: FAIL under the literal frozen numeric gate (preregistration sign defect)

The frozen numeric gate ("AUROC(BF_q, consensus_wrong) CI lower bound > 0.5 AND point >= 0.60",
copied from the round-1 BoolQ protocol) encodes the direction "higher BF_q => wrong consensus".
The protocol's own section 8 froze the substantive direction as "higher BF_q => lower risk
(unfaithful -> risky)". These two statements contradict each other: under "higher BF_q =>
correct", AUROC(BF_q, wrong) is expected BELOW 0.5.

## Results on the pilot cohort (195 high-consensus items, 34 wrong)

| criterion | frozen form | observed | pass |
|---|---|---|---|
| pipeline validity | >= 0.95 | 1.00 (5000/5000) | YES |
| E3 primary | AUROC(BF_q, wrong) CI lb > 0.5, point >= 0.60 | 0.099 [0.054, 0.153] | NO (literal) |
| macro/worst-label | macro CI lb > 0.5; worst point > 0.5 | SUPP 0.114 / REF 0.074 (BF_q orientation) | NO (literal) |
| C1 placebo | paraphrase flip <= 0.30 | 0.028 agent / 0.010 consensus | YES |
| C2 permutation | obs > 95th pct | obs 0.099 < center 0.503 | NO (literal orientation) |
| reducibility | not a copy of agreement/confidence | Spearman 0.25/0.20; not reducible | YES |

## Substantive finding (frozen direction, not post-hoc)

In the protocol's own frozen substantive direction (higher BF_q => lower risk), the pilot
result is strong and consistent:

- AUROC(-BF_q, wrong) = 0.901 [0.847, 0.946] (wrong consensus ranks far below correct on
  expected-response faithfulness).
- Macro-label CI [0.851, 0.953]; worst-label point 0.886 (SUPPORTS) / 0.926 (REFUTES) — both
  labels in the SAME direction (no label confound, unlike BoolQ).
- Mechanism: wrong consensus is unresponsive to a genuine natural evidence reversal
  (BF_reverse 0.088 vs 0.775 correct), i.e., evidence-insensitive consensus is risky; placebo
  clean so this is not general instability.
- Permutation control passes in the risk orientation (obs 0.901 > 95th pct 0.620).
- Superior to frozen baselines: -BF_q vs R_sym +0.055 [+0.016, +0.096], vs R_PI +0.221
  [+0.165, +0.283], vs mean-confidence +0.568, vs agreement +0.456 (all paired CIs exclude 0).
- Stage consistency: 0.909 [0.859, 0.950] vs 0.886 [0.793, 0.967].

## Decision

1. The pilot cohort alone does NOT formally pass the as-written gate; the failure is a
   preregistration sign defect (the numeric gate's orientation contradicts the protocol's own
   stated direction), not an absence of signal.
2. No post-hoc sign flip is performed; the substantive direction remains as frozen.
3. To obtain a formally passable, pre-registered positive result, a FRESH confirmation cohort
   (new disjoint selection) is run under a CORRECTED direction-consistent gate frozen BEFORE
   any confirmation agent call (confirmation_preregistration.md). Both cohorts (pilot +
   confirmation) must show the direction-consistent effect.
4. If the confirmation cohort passes all corrected gates, Gate 2 is declared PASS with two
   independent pre-registered cohorts. Otherwise, FAIL is recorded honestly with diagnosis.
