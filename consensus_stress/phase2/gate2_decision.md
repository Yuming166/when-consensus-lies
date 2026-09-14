# Gate 2 Decision — Consensus Stress Testing pilot (BoolQ, Qwen3.5-4B)

Date: 2026-09-13. Protocol: cs-pilot-boolq-2026-09-12.

## Verdict: FAIL (pre-registered Gate 2 criteria)

| Criterion (frozen) | Result | Pass? |
|---|---|---|
| Pipeline >= 0.95 valid | 100% valid, 100% first-pass | YES |
| E3 AUROC(BF_q, wrong\|HC): CI lb > 0.5, point >= 0.60 | 0.363 [0.102, 0.611] | NO |
| C2 permutation: observed > 95th pct | 0.363 vs 95th pct 0.641 | NO (below center) |
| C1 placebo: paraphrase flip <= 0.30 | 0.064 agent / 0.060 consensus | YES (clean) |
| Not reducible to agreement/confidence | Spearman -0.32 / -0.02; cond-0.8 AUROC 0.50 | NOT predictive (fails utility, not reducibility) |

## What was established (positive, honest)

1. The expected-response faithfulness MEASUREMENT is well-defined and reproducible: 93.6% agent
   stability under semantic-preserving paraphrase vs 30.0% responsiveness to explicit polarity
   reversal, consistent with the frozen V3.15.2 Qwen reverse flip rate (0.327) on a different cohort.
2. The placebo control is clean: paraphrase barely moves answers (6%), so the low reverse
   responsiveness is not caused by general instability.
3. The phenomenon "agreement != evidence-responsiveness" is behaviorally real: high-consensus
   answers are produced despite weak responsiveness to reversal.
4. Frozen R_PI reproduces a positive-direction (though not significant, n=9 errors) AUROC of 0.651
   on the fresh train cohort, and the frozen label asymmetry replicates with reversed sign
   (yes 0.042 / no 0.965).

## What failed

- BF_q does not predict consensus error in the pre-registered direction; the aggregate point
  estimate is inverted (wrong consensus has slightly LOWER faithfulness, diff -0.043 [-0.198, +0.135]).
- The aggregate endpoint is dominated by the BoolQ answer-prior confound (opposite within-label
  directions). This is a known, frozen-project boundary, not a new discovery.
- The reverse oracle Y* = flip(Y0) is satisfied only 30% of the time; on items where the transformed
  evidence unit is not decision-relevant, the expected response is not well-defined, so the oracle
  may be misspecified. A relevance-aware or no-forced-response oracle is required.

## Decision

- C1/C2 on BoolQ with this oracle: **retain as behavioral analysis only** (do not claim error
  prediction). Not killed as a concept, not promoted.
- Phase 3 (stress benchmark axes) and Phase 4 (reliability modeling vs RPI/Rsym): **NOT executed** —
  gated on Gate 2.
- Phase 5 (active probing) and Phase 6 (cross-model): **NOT executed** — gated.
- No post-hoc sign flip, no test-set re-tuning, no silent cohort repair (Rules 1, 5, 8).

## Reformulation proposal for a future cohort (not executed this run)

1. **Label-symmetric cohort** (VitaminC natural pairs or a balanced BoolQ construction): the pilot
   shows the aggregate BoolQ endpoint is uninterpretable due to answer priors; any future gate must
   be label-symmetric with macro/worst-label gates (frozen V3.16.1 style).
2. **Decision-relevance-aware expected response**: declare NO-FORCED-RESPONSE for intervention items
   whose evidence unit is not decision-relevant for the question (relevance determined offline,
   before agent calls, without test-time labels), avoiding the 70% "unresponsive" majority that
   makes the current oracle statistically weak.
3. **Explicit direction pre-registration**: choose and freeze the risk direction (faithful = safe vs
   unfaithful = risky) before seeing results; the pilot's mean difference points to
   "unfaithful -> risky" but must not be claimed post-hoc.
4. If a future cohort passes Gate 2 with a fixed oracle, then build the stress curve (Phase 3) and
   reliability models (Phase 4).
