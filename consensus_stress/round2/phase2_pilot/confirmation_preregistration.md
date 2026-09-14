# Confirmation Cohort Preregistration — Corrected Direction-Consistent Gate (VitaminC, Qwen3.5-4B)

Status: FROZEN before any confirmation-cohort model call. Protocol id: `cs-pilot-vitaminc-conf-2026-09-13`.

This cohort is a FRESH, DISJOINT replication of `cs-pilot-vitaminc-2026-09-13` (pilot). It is
run because the pilot's as-written numeric gate contained a preregistration sign defect: the
literal gate (AUROC(BF_q, wrong) CI lb > 0.5) encodes "higher BF_q => wrong consensus", which
contradicts the protocol's own frozen substantive direction ("higher BF_q => lower risk").
The pilot result was strongly in the frozen substantive direction (AUROC(-BF_q, wrong) = 0.901
[0.847, 0.946]), but the as-written gate cannot formally pass. This confirmation cohort tests
the SAME substantive hypothesis on NEW data with a CORRECTED, direction-consistent gate frozen
BEFORE any confirmation agent call. No confirmation outcome will be used to alter this gate.

## 1. Design identity with the pilot (unchanged, frozen)

- Same cohort type: VitaminC natural SUPPORTS/REFUTES pairs, one pair per page, page-disjoint,
  disjoint from frozen V3.16/V3.16.1 target+distractor pages, contrast gates
  (character_ratio >= 0.93, token_jaccard >= 0.85), filters (no U+FFFD; claim 5-40 tokens;
  evidence 10-120 tokens).
- SAME oracle: decision-relevance-aware expected-response; conditions
  original / paraphrase / reverse (natural swap) / synthetic_reverse / remove; BF_q =
  mean over agents of faithfulness across {paraphrase, reverse}; synthetic_reverse secondary
  only; remove = NO-FORCED-RESPONSE (descriptive).
- SAME personas and 2-of-3 partition table (frozen V10), same prompt contract
  (yes/no + confidence + cited ids), same endpoint/model/no reasoning_effort, same
  temperature/seed/max_tokens/retry-2 rules.
- SAME frozen R_PI (0.1/0.3/0.6 over {remove,reverse,synthetic_reverse} flips) and R_sym
  (0.3*reverse_inertia + 0.7*intervention_disagreement) definitions.

## 2. Selection (frozen)

- From the same deterministic hash-ordered eligible pool used by the pilot, take the NEXT 50
  pairs (pilot used indices 0-99; confirmation uses indices 100-149). The confirmation pairs
  are disjoint from the pilot's 100 pairs and from all excluded pages.
- 50 pairs = 100 items, exactly 50 SUPPORTS + 50 REFUTES. Distractors assigned
  deterministically (page outside used+excluded; jaccard(claim, D) <= 0.05).
- Offline decision-relevance audit: 30 sampled items; >= 24/30 relevant, else exclude audited
  non-relevant items and their pairs before agent calls (same rule as pilot).
- Paraphrase artifacts: 100 evidence units x 2 variants + 50 distractor paraphrases = 250 calls;
  audit 20 items meaning-preserving (>= 16/20, else paraphrase downgraded to
  NO-FORCED-RESPONSE and BF_q recomputed from reverse only).

## 3. Corrected direction-consistent gate (frozen; no post-hoc changes)

Risk score RS_q = -BF_q (higher = riskier), matching the frozen substantive direction
"higher BF_q => lower risk" (unresponsive/unstable consensus => risky).

PASS if and only if ALL of:
1. pipeline valid rate >= 0.95, no unrepairable parser failures;
2. primary: AUROC(RS_q, consensus_wrong | HC) CI lower bound > 0.5 AND point >= 0.60
   (equivalently AUROC(BF_q, wrong) CI upper bound < 0.5 AND point <= 0.40);
3. macro-label (unweighted mean of SUPPORTS/REFUTES subgroup AUROCs) CI lower bound > 0.5;
4. worst-label point estimate > 0.5 (CI reported);
5. C1 placebo: agent-level paraphrase flip rate <= 0.30;
6. C2 permutation: observed AUROC(RS_q) > 95th percentile of the permutation distribution
   (per-question swap of preserve/flip roles, risk orientation);
7. not reducible to agreement/confidence: Spearman(RS_q, agreement) < 0.9 and
   Spearman(RS_q, mean_confidence) < 0.9; AUROC(RS_q) at agreement==0.8 reported (point > 0.5;
   CI may be wide at pilot n).

FAIL if any criterion fails; record FAIL and diagnose (model behavior / evidence construction
/ oracle / sample size / genuine absence of transfer). No metric or cohort change after
outcomes; no sign flip; no silent repair.

## 4. Gate 2 final rule (both cohorts)

Gate 2 (round 2) PASS iff:
- pilot cohort: substantive direction confirmed (AUROC(-BF_q, wrong) > 0.5 with CI upper bound
  < 0.5 on BF_q orientation, or equivalently CI lower bound > 0.5 on risk orientation) — ALREADY
  satisfied on the pilot (0.901 [0.847, 0.946]) — AND
- confirmation cohort passes all 7 corrected gates above.
Otherwise FAIL (recorded honestly).

## 5. Secondary analyses (unchanged from pilot)

Per-condition faithfulness AUROCs, R_PI/R_sym/confidence/agreement AUROCs, paired bootstrap
diffs vs RS_q, correct-vs-wrong mean differences, descriptive flip rates, worst-label and
macro reporting in both orientations, stage/batch notes.

## 6. Artifacts

- confirmation_selection_manifest.json, confirmation_selection_audit.json,
  confirmation_labels_ledger.json (sealed), confirmation_relevance_audit.json,
  confirmation_paraphrase_manifest.json + audit, confirmation_records.jsonl (no labels),
  confirmation_preoutcome_features.jsonl (no labels), analysis/confirmation_analysis.json
  + confirmation_analysis.md, analysis/gate2_decision_confirmation.md.
- Registry entries appended for every experiment (old entries unchanged).
