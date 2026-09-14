# CS Pilot — BoolQ Expected-Response Faithfulness: Results

Protocol: `cs-pilot-boolq-2026-09-12` (see pilot_preregistration.md + Amendments A/B/C/C2).
Date: 2026-09-13. Model: Qwen3.5-4B @ 127.0.0.1:31518 (no reasoning_effort).
Machine-readable: analysis.json. Raw records: records.jsonl. Frozen features: preoutcome_features.jsonl.

## 1. Pipeline integrity

- 100 BoolQ questions (train, 50 yes / 50 no, fresh cohort; no overlap with any frozen validation selection).
- 5 agents x 5 conditions x 100 questions = 2,500 records; success 2,500/2,500 (100%); first-pass valid 100%.
- Offline artifacts: 300/300 paraphrases usable (audit 20/20 meaning-preserving, 0 polarity reversals);
  300/300 substitutes usable under the relaxed length contract, but semantic audit judged only 23/40 (57.5%)
  as clearly opposite-supporting -> Amendment B rule triggered: substitute is NO-FORCED-RESPONSE for
  expected-response scoring and is reported descriptively only.
- Outcome firewall: records/features contain no label fields; labels merged only after
  preoutcome_features.jsonl was written.

## 2. Population

- High-consensus (agreement >= 0.8): 81/100 questions.
- Wrong high-consensus: 9/81 = 11.1% (V12.1 validation cohort had 22.0%; train subset is easier).

## 3. E1 — agent-level expected-response accuracy (all 100 questions)

| Condition | Oracle | Accuracy |
|---|---|---|
| paraphrase (semantic-preserving) | Y* = Y0 | 0.936 |
| reverse (polarity reversal) | Y* = flip(Y0) | 0.300 |
| overall (scored) | | 0.618 |

Interpretation: agents are strongly stable under meaning-preserving paraphrase (93.6% faithful) but
only 30% respond to explicit polarity reversal. The 30% reverse flip rate reproduces the frozen
V3.15.2 Qwen reverse flip rate (0.327) on a different cohort.

## 4. Placebo control (C1)

- Paraphrase agent flip rate: 6.4% (threshold for violation was 30%) -> control NOT violated.
- Paraphrase consensus flip rate: 6.0%.

## 5. E2 — consensus-level faithfulness (high-consensus subset)

| Quantity | Correct consensus | Wrong consensus |
|---|---|---|
| BF_q (paraphrase+reverse) mean | 0.621 | 0.578 |
| BF_paraphrase mean | 0.948 | — |
| BF_reverse mean | 0.284 | — |
| remove flip rate | 0.373 | — |
| substitute flip rate (descriptive) | 0.523 | — |

## 6. E3 — primary gate: AUROC(BF_q, consensus_wrong | high-consensus)

- AUROC = 0.363; 95% CI [0.102, 0.611]; n = 81.
- Pre-registered pass rule: CI lower bound > 0.5 AND point >= 0.60. **GATE FAILS.**

Note on direction: the point estimate is BELOW 0.5, i.e., wrong consensus has slightly LOWER
expected-response faithfulness (mean diff wrong-correct = -0.043, CI [-0.198, +0.135]). The
registered hypothesis (higher BF_q => wrong) is not supported; flipping the sign after seeing the
result is forbidden by Rule 1, so the gate verdict stands as FAIL.

## 7. Secondary score AUROCs (high-consensus, 1000-question bootstrap, seed 20260913)

| Score | AUROC [95% CI] |
|---|---|
| BF_q | 0.363 [0.102, 0.611] |
| BF_paraphrase | 0.294 [0.116, 0.471] |
| BF_reverse | 0.485 [0.259, 0.698] |
| R_PI (frozen, pilot cohort) | 0.651 [0.430, 0.869] |
| mean confidence | 0.244 [0.090, 0.391] |
| agreement | 0.528 [0.390, 0.616] |
| remove flip rate | 0.420 [0.225, 0.607] |
| substitute flip rate | 0.313 [0.140, 0.491] |

Paired diffs vs BF_q: BF_q - R_PI = -0.288 [-0.753, +0.229]; BF_q - confidence = +0.120 [-0.230, +0.464];
BF_q - agreement = -0.164 [-0.482, +0.164].

## 8. Label subgroups (validity audit; known BoolQ answer-prior issue)

| Native label | n (HC) | AUROC(BF_q) [95% CI] |
|---|---|---|
| yes | 40 | 0.042 [0.000, 0.114] |
| no | 41 | 0.965 [0.875, 1.000] |

The relationship between BF_q and consensus error is OPPOSITE across native labels and extreme in
both directions. The aggregate 0.363 is therefore dominated by the known BoolQ answer-prior
confound; the aggregate endpoint is not interpretable as a stable phenomenon without a
label-symmetric design. This mirrors (with reversed sign) the frozen R_PI label asymmetry
(yes 0.834 / no 0.213 on V12.1).

## 9. Null / placebo controls

- C2 permutation (swap preserve/flip semantics per question): observed AUROC 0.363 vs permutation
  mean 0.490 (95th pct 0.641). Observed lies BELOW the permutation distribution center: the
  pre-registered preserve/flip semantics carry an inverted (not positive) signal.
- C3 agent-level randomization: observed 0.363 vs perm mean 0.364. (Note: this control is weak by
  construction — shuffling agents within a question preserves per-condition answer sets, so BF_q
  changes little; it is reported but not used for the verdict.)
- Reducibility: Spearman(BF_q, agreement) = -0.32; Spearman(BF_q, mean_confidence) = -0.02;
  AUROC(BF_q) at agreement==0.8 exactly = 0.500 [0.227, 0.773] (n=13). BF_q is not a copy of
  confidence/agreement, but it is also not predictive.

## 10. Gate 2 verdict: FAIL (pre-registered criteria)

- E3 primary gate failed (CI includes 0.5; point estimate inverted).
- The behavioral phenomenon (invariance != reliability; agents stable under preservation, weakly
  responsive to reversal) EXISTS and is measurable, matching frozen flip-rate findings.
- The expected-response faithfulness score does NOT predict consensus error on this cohort; the
  aggregate signal is label-confounded, and the reverse oracle (Y* = flip) is only 30% satisfied,
  which may reflect either genuine evidence insensitivity or oracle misspecification on
  non-decision-relevant evidence units.

Decision per plan decision tree: retain C1/C2 as BEHAVIORAL ANALYSIS ONLY on this cohort;
do NOT advance to Phase 3/4 with the current formulation. Recorded as FAIL, not repaired.
