# Round 3 Paper-Scale Preregistration — Expected-Response Faithfulness / Consensus Stress Testing (VitaminC, Qwen3.5-4B)

Status: FROZEN before ANY round-3 model call (artifact, agent, or analysis model).
Protocol id: `cs-paper-vitaminc-2026-09-13`. Orchestrator: DeepSeek v4 flash Max (server default).
Research model: local Qwen3.5-4B @ http://127.0.0.1:31518 (NO reasoning_effort field).
Cross-model: Ling-3.0-tiny (started later, same frozen protocol; separate preregistered entry).

This protocol scales Gate 2 / Phase 3 / Phase 4 of round 2 to a paper-scale cohort
(300 fresh VitaminC natural pairs), keeping the round-2 corrected, direction-consistent
gate (RS_q = -BF_q, higher = riskier) and the decision-relevance-aware expected-response
oracle, and adding a CI-level worst-label gate and a strict Risk@80 CI gate.

## 1. Research question (frozen)

When 5 Qwen3.5-4B agents form a high-consensus answer on a paper-scale, label-symmetric
VitaminC natural-pair cohort, does the outcome-blind expected-response faithfulness profile
(RS_q = -BF_q) distinguish correct consensus from false consensus beyond confidence /
vote agreement / frozen R_PI / frozen R_sym, with pair-grouped bootstrap CIs, a CI-level
worst-label gate, placebo and permutation controls, and a strict Risk@80 gate at the
preregistered operating point?

## 2. Population and selection (frozen; offline)

- Dataset: `data/benchmarks/vitaminc/test.jsonl` (official VitaminC test, SHA256 recorded).
- Natural pairs: same `case_id` + same `claim`, exactly one SUPPORTS and one REFUTES row
  (same page/revision; minimal natural contrast).
- Exclusions (all recorded):
  1. Any page used as target OR distractor in frozen V3.16 / V3.16.1 selections.
  2. All 150 pair_ids used in round 2 (`cs-pilot-vitaminc-2026-09-13` indices 0-99 and
     `cs-pilot-vitaminc-conf-2026-09-13` indices 100-149), loaded from the sealed round-2
     selection manifests. Round 3 is page-disjoint AND pair-disjoint from round 2.
- Eligibility gates (frozen; broadened from round 2's 0.93/0.85 to reach paper scale while
  preserving "minimal natural contrast"):
  - one pair per page (highest character_ratio, then token_jaccard, then case_id);
  - character_ratio(S,R) >= 0.85 AND token_jaccard(S,R) >= 0.70;
  - no U+FFFD in claim/evidence; claim tokens in [5,40]; each evidence tokens in [10,120].
- Ordering: sha256(SALT + page), SALT = b"cs-paper-vitaminc-2026-09-13\n"; round-2 pair_ids
  are skipped, then the FIRST 300 pairs are selected = 600 items, exactly
  300 SUPPORTS + 300 REFUTES (label-symmetric by construction).
- Each pair yields two composite items sharing the claim:
  S-item (gold SUPPORTS, evidence = supports evidence, reverse = refutes evidence);
  R-item (gold REFUTES, evidence = refutes evidence, reverse = supports evidence).
- Distractor D: one sentence from a page outside {used} U {excluded}, deterministic,
  token_jaccard(claim, D) <= 0.05, shared by both items of a pair.
- Stage split (integrity management, NO outcome used): stage 1 = first 150 pairs,
  stage 2 = next 150 pairs. Stage 2 runs only if stage-1 integrity passes (>=0.95 valid
  records and artifact audits pass); the decision uses NO labels/outcomes.

## 3. Decision-relevance-aware expected-response oracle (frozen; offline; label-free)

Identical to round 2 (see round2 preregistration sections 3-4):
- R1 own evidence E decision-relevant; R2 paraphrases para1(E)/para2(E) relevant;
  R3 paired counter-evidence E_opp relevant (natural opposite by construction);
  R4 negated unit relevant iff base relevant; R5 distractor NOT relevant;
  R6 empty packet (remove) => NO-FORCED-RESPONSE (descriptive only).
- Scoring: an agent call is scored iff its view contains >= 1 decision-relevant unit with a
  defined expected response; under the frozen 2-of-3 partition all non-remove views are scored.
- Conditions: original / paraphrase / reverse (natural swap) / synthetic_reverse (secondary) /
  remove. BF_q = mean over agents of faithfulness across {paraphrase, reverse};
  synthetic_reverse is secondary only (round-2 finding: weak, non-separating).
- Paraphrase artifacts: 2 variants per evidence unit + 1 per distractor (offline, cached).
  Audit >= 80% meaning-preserving on a 30-item sample; else paraphrase downgraded to
  NO-FORCED-RESPONSE and BF_q recomputed from reverse only.
- Offline decision-relevance audit: 30 items, deterministic hash sample, >= 24/30 judged
  decision-relevant, else exclude audited non-relevant items and their pairs before calls.

## 4. Model calls (frozen)

- Endpoint http://127.0.0.1:31518/v1/chat/completions, model `Qwen3.5-4B`, temperature 0.0,
  fixed seeds (frozen V10 `_agent_seed`), max_tokens 160 (agent) / 256 (artifact),
  prompt-only JSON (no response_format), NO reasoning_effort, retry-2 with frozen repair
  suffix, content-addressed cache under round3/cache.
- Budget: 900 units x 2 = 1,800 paraphrase calls; 600 items x 5 agents x 5 conditions =
  15,000 agent calls. Total ~16,800.

## 5. Primary endpoints (frozen)

On the high-consensus subset (original agreement >= 0.8):
- E1 pipeline: valid rate >= 0.95, no unrepairable parser failures.
- E2 primary gate: AUROC(RS_q = -BF_q, consensus_wrong | HC) pair-grouped bootstrap CI
  lower bound > 0.5 AND point >= 0.60. Direction: higher RS_q => riskier.
- E3 macro-label AUROC (unweighted mean of SUPPORTS/REFUTES subgroup AUROCs) CI lb > 0.5.
- E4 worst-label AUROC (min of SUPPORTS/REFUTES) CI lower bound > 0.5 (CI-level, V3.16.1 style).
- E5 placebo: agent-level paraphrase flip rate <= 0.30.
- E6 permutation: observed AUROC(RS_q) > 95th percentile of 1000 per-question
  preserve/flip-swap permutations.
- E7 reducibility: Spearman(RS_q, agreement) < 0.9, Spearman(RS_q, mean_confidence) < 0.9,
  AUROC(RS_q | agreement==0.8) point > 0.5.

## 6. Gate 2 (paper scale) decision rule (frozen)

PASS iff ALL of E1..E7. FAIL if any criterion fails; record FAIL and diagnose (model
behavior / evidence construction / oracle definition / sample size / genuine absence).
No post-hoc sign flip, no silent cohort/metric repair, no test-set changes after outcomes.

## 7. Phase 3 (continuous lambda stress; frozen protocol, fresh calls)

- Subset: 120 pairs (240 items) chosen deterministically from the 300-pair main cohort by
  hash order on SALT + "lambda:" + pair_id (outcome-free).
- Reversal axis: at lambda in {0.2, 0.4, 0.6, 0.8}, for each agent view, each decision-relevant
  unit is independently reversed (E -> E_opp) with probability lambda via a seeded RNG
  (seed = hash(item_id, agent_index, lambda)); non-reversed relevant units stay E; distractor
  unchanged. Lambda = 0 anchor = original records; lambda = 1 anchor = reverse records
  (no new calls for anchors).
- Removal axis: same grid; each decision-relevant unit is independently REMOVED with
  probability lambda (seeded); remaining units stay E; distractor unchanged. Anchors:
  lambda 0 = original, lambda 1 = remove records.
- No forced expected response at intermediate lambda (partial-reversal oracle undefined);
  we record answer flip probability vs the agent's own original answer.
- Per-question stress metrics (reversal axis primary): stress_area (trapezoidal integral of
  flip probability over lambda in [0,1]); breakpoint (smallest lambda where the consensus
  answer flips, else "none"); robustness_radius (largest lambda where consensus keeps the
  original answer; = 1.0 if never flips).
- Consensus-level profile: AUROC(RS_stress = -stress_area, wrong | HC) with pair-grouped CI
  (gate: CI lb > 0.5, same direction), mean breakpoint by correctness, and robustness-radius
  distributions; removal axis reported descriptively.
- Calls: 240 items x 5 agents x 4 lambdas x 2 axes = 9,600 (anchors free).

## 8. Phase 4 (reliability modeling; frozen protocol, no new agent calls)

- Scores compared on HC items (pair-grouped bootstrap, 2000 replicates): RS_q = -BF_q
  (frozen composite), logistic on {bf_paraphrase, bf_reverse} (pair-grouped 5-fold OOF),
  isotonic-calibrated RS_q, R_PI (frozen 0.1/0.3/0.6), R_sym (frozen 0.3/0.7),
  mean_confidence, disagreement (1-agreement), conf_dispersion.
- Primary metrics: AUROC with CI; Risk@80 (retain lowest-risk 80%) error reduction with CI;
  paired bootstrap diffs AUROC and Risk@80 vs R_sym / R_PI / confidence / disagreement.
- Gate 4 (formal, frozen) — PASS iff ALL of:
  P1 Risk@80(RS_q) CI lower bound > 0 (strict CI gate at preregistered coverage 0.80);
  P2 paired diff AUROC(RS_q) - AUROC(R_sym): CI lb > 0;
  P3 paired diff AUROC(RS_q) - AUROC(R_PI): CI lb > 0;
  P4 paired diff Risk@80(RS_q) - Risk@80(R_sym): CI lb > 0;
  P5 paired diff Risk@80(RS_q) - Risk@80(R_PI): CI lb > 0;
  P6 ECE improvement from isotonic calibration reported (descriptive, no gate).
- Logistic is evaluated via pair-grouped 5-fold CV (OOF); isotonic on OOF split; neither
  uses held-out labels for selection. The frozen composite BF_q is the primary representation.

## 9. Phase 6 cross-model (frozen; separate entry before Ling calls)

- Cohort: the first 100 pairs (200 items) of the 300-pair main cohort, run on
  Ling-3.0-tiny with the IDENTICAL frozen protocol (same selection, same artifacts, same
  oracle, same conditions, same BF_q formula, same gates). No per-model retuning, no
  post-hoc gate changes.
- Reported separately: (a) within-model validity = Ling's own 7 gates on its 200 items;
  (b) per-model AUROC / Risk@80 on the shared 100-pair cohort (Qwen vs Ling);
  (c) cross-model transfer = the frozen RS_q formula applied to Ling without retuning,
  plus (secondary) the Qwen-fitted Phase-4 logistic applied to Ling features;
  (d) mechanism transfer = correct/wrong flip profiles per model (descriptive);
  (e) item-level Spearman(RS_q_Qwen, RS_q_Ling) reported ONLY as secondary evidence.
- If the Ling server cannot be started safely, cross-model is reported BLOCKED honestly.

## 10. Phase 6 cross-dataset (frozen; separate entry before FEVER calls)

- Dataset: `data/benchmarks/fever-validation.jsonl`. FEVER cannot provide same-claim
  SUPPORTS/REFUTES natural pairs (verified: 0 same-claim pairs with both verdicts), so we
  construct label-symmetric "natural claim-pair" cohorts:
  - Match REFUTES claims to near-duplicate SUPPORTS claims (character_ratio >= 0.85,
    token_jaccard >= 0.65, single-evidence rows), one pair per evidence page.
  - Pair uses the SUPPORTS claim C_S for both items:
    S-item: (C_S, E_S) gold SUPPORTS; R-item: (C_S, E_R) gold REFUTES, where E_S = SUPPORTS
    evidence sentence, E_R = REFUTES evidence sentence. Reverse swaps E_S/E_R (natural
    counter-evidence: E_R must refute C_S and E_S must support C_S — audited offline,
    Qwen judge + orchestrator verification; >= 80% audit pass required, else pair excluded).
  - Target 50-60 pairs (100-120 items), label-symmetric by construction, page-disjoint
    (one pair per page), deterministic hash order, fresh (no overlap with any prior cohort).
- Same oracle/conditions/partitions/personas/BF_q and the same 7 gates (with the caveat
  that n is smaller; worst-label gate at point level with CI reported).
- Budget: ~180 units x 2 paraphrase calls + 120 items x 5 agents x 5 conditions = ~3,360 calls.

## 11. Phase 5 (active probing)

Only executed if budget and gates allow after Phases 3/4/6; otherwise written as a
next-step plan. No active-probing calls otherwise.

## 12. Outcome firewall

Labels are merged ONLY in analysis after preoutcome features are frozen. Forbidden score
inputs: label, gold_binary, correct, consensus_wrong (mirror frozen R_PI set). Dataset
labels used only offline to construct the balanced design and artifacts, never at test time,
never in probing or scoring.

## 13. Artifacts (all under consensus_stress/round3/)

preregistration.md, selection_manifest.json + selection_audit.json + labels_ledger.json
(sealed), relevance_audit.json, paraphrase_manifest.json + generation stats + audit,
expected_response_contract.json, records.jsonl (no labels), preoutcome_features.jsonl
(no labels), analysis/*.json + *.md, figures/*.png, registry.yaml entries appended
(old entries unchanged). No git commit/push; docs/ and frozen code untouched.
