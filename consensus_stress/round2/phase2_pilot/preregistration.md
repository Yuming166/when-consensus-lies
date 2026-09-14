# Round 2 Phase-2 Pilot Preregistration — Expected-Response Faithfulness on VitaminC Natural Pairs (Qwen3.5-4B)

Status: FROZEN before any round-2 model call. Protocol id: `cs-pilot-vitaminc-2026-09-13`.
All selection, relevance audit, artifact generation, and all agent decision calls happen
only after this file is written and the registry entry is PROPOSED/RUNNING.

This protocol redoes Gate 2 of the previous run (`cs-pilot-boolq-2026-09-12`, FAIL) following
`consensus_stress/phase2/gate2_decision.md` recommendations 1-4:
1. label-symmetric cohort (VitaminC natural SUPPORTS/REFUTES pairs) with macro/worst-label gates;
2. decision-relevance-aware expected-response oracle (offline relevance; non-relevant = NO-FORCED-RESPONSE);
3. pre-registered risk direction, no post-hoc sign flip;
4. reuse of the frozen 5-agent infrastructure (personas, 2-of-3 evidence views, R_PI/R_sym frozen definitions).

## 1. Research question (Gate 2 redo)

When 5 Qwen3.5-4B agents form a high-consensus answer to the question
"Does the evidence support the claim?" on a label-symmetric VitaminC natural-pair cohort,
does an outcome-blind expected-response faithfulness profile (measured by controlled evidence
stress) distinguish correct consensus from false consensus, beyond ordinary confidence /
vote agreement, and does the distinction survive null/placebo controls and hold in BOTH
native labels (SUPPORTS and REFUTES)?

## 2. Population and selection (frozen)

- Dataset: `data/benchmarks/vitaminc/test.jsonl` (official VitaminC real contrastive test,
  frozen SHA256 recorded in selection manifest).
- Natural pairs: same `case_id` + same `claim`, exactly two rows whose labels are
  {SUPPORTS, REFUTES}; the pair is a natural minimal contrast (same page/revision, evidence
  differs only in the decisive detail).
- Exclusion: any page used as target OR distractor page in the frozen V3.16 (284 pairs)
  and V3.16.1 (289 pairs) selections is excluded (target+distractor pages = 1076 pages,
  disjoint from our pool; recorded in selection audit).
- Deterministic filters (all frozen before any model call):
  - one pair per page; when a page has several pairs, keep the highest-contrast pair
    (max character_ratio, then max token_jaccard, then lexicographic case_id);
  - contrast gates: character_ratio(S,R) >= 0.93 AND token_jaccard(S,R) >= 0.85;
  - no U+FFFD replacement character in claim or either evidence;
  - claim tokens in [5, 40]; each evidence tokens in [10, 120].
- Order: pairs sorted by sha256(SALT + page) with SALT = b"cs-pilot-vitaminc-2026-09-13\n".
  Stage 1 = first 50 pairs (100 items); Stage 2 = next 50 pairs (100 items). Total 100 pairs,
  200 items, exactly 100 SUPPORTS + 100 REFUTES (label-symmetric by construction).
- Each pair yields two composite items with the SAME claim:
  - S-item (gold = SUPPORTS): evidence = supports evidence; reverse evidence = refutes evidence.
  - R-item (gold = REFUTES): evidence = refutes evidence; reverse evidence = supports evidence.
- Distractor D (third packet unit): one sentence from a page outside {used pages} U {excluded
  pages}, deterministic (hash order), with token_jaccard(claim, D) <= 0.05; one distractor per
  pair (shared by the two items of the pair).
- Labels are used ONLY offline to construct the balanced design and to write artifact texts;
  never sent to agents, never used in probing or scoring (outcome firewall; same as frozen
  project practice).

## 3. Decision-relevance-aware expected-response oracle (frozen; offline; label-free)

Relevance is decided OFFLINE before any agent call, by the following frozen rules plus a
human audit (section 4):

- R1: the item's own evidence E is DECISION-RELEVANT (VitaminC gold defines the verdict;
  contrast gates guarantee E vs E_opp are minimal natural edits).
- R2: paraphrase variants para1(E), para2(E) are DECISION-RELEVANT (same content as E).
- R3: the paired counter-evidence E_opp is DECISION-RELEVANT (it genuinely supports the
  opposite verdict by construction).
- R4: a negated unit "Task-local counterfactual: it is false that: X" is DECISION-RELEVANT
  iff X is (negation of a decisive unit stays decisive).
- R5: the distractor D is NOT DECISION-RELEVANT (token_jaccard(claim, D) <= 0.05).
- R6: empty packet (remove) => NO-FORCED-RESPONSE for all agents (descriptive only).
- Scoring rule: an agent call is scored for expected-response faithfulness iff its view
  contains >= 1 decision-relevant unit whose expected response is defined. Under the frozen
  2-of-3 partition table, every view of every non-remove condition contains >= 1
  decision-relevant unit, so all non-remove calls are scored; NO-FORCED-RESPONSE applies to
  the remove condition and to distractor units (which never define an expected response
  by themselves).

## 4. Human audit (offline, before any agent call)

- Relevance audit: 30 items sampled deterministically (hash order, spanning both stages);
  the orchestrator judges whether the item's own evidence E is decision-relevant for the
  claim (i.e., determines SUPPORTS vs REFUTES). Rule: if >= 24/30 (80%) judged relevant,
  selection stands. If < 80%, the audited non-relevant items AND their paired items are
  EXCLUDED from the selection before any agent call (and the exclusion is recorded); the
  protocol and oracle are unchanged.
- Artifact audit: 20 paraphrases (10 per variant type) judged meaning-preserving. If < 80%,
  the paraphrase condition is downgraded to NO-FORCED-RESPONSE (Amendment-style trigger,
  frozen before agent calls) and BF_q is recomputed from the remaining scored conditions;
  the audit result is recorded regardless.

## 5. Conditions, expected responses, and scored status (frozen; label-free)

| condition | packet construction | expected Y*(T) | scored |
|---|---|---|---|
| original | [E, para1(E), D] | reference Y0 (agent's own original answer) | reference |
| paraphrase | [para1(E), para2(E), para(D)] | Y* = Y0 (semantic-preserving) | scored (stability) |
| reverse | [E_opp, para1(E_opp), D] | Y* = flip(Y0) (natural counter-evidence swap) | scored (responsiveness) |
| synthetic_reverse | ["it is false that: E", "it is false that: para1(E)", "it is false that: D"] | Y* = flip(Y0) | scored (secondary only; NOT in BF_q) |
| remove | [] | NO-FORCED-RESPONSE | descriptive only |

- PRIMARY composite BF_q = mean over agents and scored conditions {paraphrase, reverse} of
  per-agent faithfulness 1[observed == Y*(condition)].
- synthetic_reverse is kept for frozen-V10/V3.16 comparability; because its oracle
  satisfaction rate was the round-1 failure mode, it is reported per-condition only and is
  NOT part of BF_q (frozen before any agent call).
- Per-agent Y0 is the agent's own original-condition answer. Expected responses are defined
  from transformation semantics alone (no label, no correctness), frozen before any agent call.

## 6. Model calls

- Endpoint: http://127.0.0.1:31518/v1/chat/completions, model `Qwen3.5-4B`, temperature 0.0,
  seed fixed per (agent, condition), agent-call max_tokens 160, artifact-call max_tokens 256,
  prompt-only JSON (no server-side response_format), NO `reasoning_effort` field.
- Personas and 2-of-3 partition table: frozen from
  /home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src/sp500_forecastability/pilot_llm_v10.py
  (read-only; AGENT_PERSONAS and PARTITION_TABLE unchanged).
- Question format (new, round-2): "Does the provided evidence support the claim: <claim>?",
  answer exactly "yes" (SUPPORTS) or "no" (REFUTES) via the frozen V10 JSON contract
  {agent_id, answer, confidence, cited_evidence_ids}; yes/no mapped to SUPPORTS/REFUTES.
- Artifact calls: 200 evidence units x 2 paraphrase variants = 400 + 100 distractor
  paraphrases = 500 (offline, cached).
- Agent calls: 200 items x 5 agents x 5 conditions = 5000 (Stage 1: 2500, Stage 2: 2500),
  all cached by content hash; retries capped at 2 with the frozen repair suffix.
- Stage 2 expansion rule (frozen BEFORE outcome merge): run Stage 2 iff (a) Stage 1 record
  validity >= 0.95, (b) both audits passed or triggered fallbacks as written, (c) budget
  remains. The expansion decision uses NO outcome information.

## 7. Primary endpoints (frozen)

On the high-consensus subset (original agreement >= 0.8):
- E1 agent-level expected-response accuracy per scored condition (paraphrase, reverse,
  synthetic_reverse).
- E2 consensus-level BF_q per question (mean over agents of {paraphrase, reverse}
  faithfulness) and per-condition consensus faithfulness.
- E3 PRIMARY GATE: AUROC(BF_q, consensus_wrong | HC), pair-grouped 2000-replicate bootstrap
  CI (seed 20260913), frozen direction: HIGHER BF_q => LOWER risk (unfaithful -> risky;
  see section 8). Gate passes only if CI lower bound > 0.5 AND point estimate >= 0.60.
- E4 macro/worst-label gates: AUROC computed within each native label subgroup
  (SUPPORTS / REFUTES items); macro = unweighted mean of the two subgroup AUROCs; worst =
  min. Gates: macro CI lower bound > 0.5 (pair-grouped bootstrap) AND worst-label point
  estimate > 0.5 (CI reported). Rationale for point-level worst gate: pilot power with
  per-label n ~ 100 and few errors; a full-scale cohort would use the V3.16.1-style
  worst-label CI gate. Worst-label point <= 0.5 fails the gate.

## 8. Pre-registered risk direction (frozen; no post-hoc sign flip)

- Risk profile definition: a consensus is RISKY if it is NOT appropriately
  evidence-responsive, i.e. (a) unstable under semantic preservation (paraphrase
  faithfulness low) or (b) unresponsive to a genuine natural evidence reversal
  (reverse faithfulness low).
- Direction: higher BF_q (more faithful) => lower risk => higher AUROC(BF_q, consensus_wrong)
  with AUROC > 0.5. Equivalently, unresponsive/inconsistent consensus profiles are
  predicted to be wrong more often than responsive/stable ones.
- Rationale (frozen, theoretical): a panel whose consensus is insensitive to the decisive
  evidence is more likely driven by priors/noise, hence more likely wrong; a panel stable
  under preservation AND responsive under genuine reversal is evidence-driven, hence less
  likely wrong.
- The previous run's point estimate (wrong consensus had lower BF_q) is a recorded FAILED
  result, not a basis for this choice; the direction here is fixed before any round-2 agent
  call and will NOT be changed after results are seen.

## 9. Controls (frozen)

- C1 placebo (semantic-preserving): agent-level and consensus-level paraphrase flip rate.
  If agent-level paraphrase flip rate > 0.30, the semantic-preserving axis is a control
  violation; the claim is restricted accordingly.
- C2 permutation: per-question coin flip on which scored condition is treated as preserve vs
  flip (pseudo BF = 0.5*para + 0.5*(1-rev) or 0.5*(1-para) + 0.5*rev); 1000 permutations;
  distribution of AUROC(pseudo_BF, wrong) must center near 0.5; observed AUROC must exceed
  the 95th percentile.
- C3 agent-level randomization of intervention assignment (reported; weak control by
  construction).
- Reducibility: AUROC(BF_q | agreement == 0.8) CI lower bound > 0.5; Spearman(BF_q,
  agreement) and Spearman(BF_q, mean_confidence) reported (must not be >= 0.9).

## 10. Gate 2 decision rule (frozen)

PASS if and only if ALL of:
1. pipeline completes with >= 0.95 valid records and no unrepairable parser failures;
2. E3 primary gate: AUROC(BF_q, wrong | HC) CI lower bound > 0.5 AND point >= 0.60,
   direction = higher BF_q => lower risk (section 8);
3. macro-label AUROC CI lower bound > 0.5 (pair-grouped bootstrap);
4. worst-label AUROC point estimate > 0.5 (CI reported);
5. C1 placebo does NOT show violation (agent paraphrase flip rate <= 0.30);
6. C2 permutation passes (observed AUROC > 95th percentile of permutation distribution);
7. BF_q not reducible to agreement/confidence (frozen checks in section 9).

FAIL if any criterion fails: record FAIL and diagnose (model behavior / evidence construction
/ oracle definition / sample size / genuine absence of transfer); do NOT force a pass.
No post-hoc sign flip, no silent cohort repair, no metric/cohort change after outcomes.

## 11. Secondary analyses

- S1 AUROC of each per-condition faithfulness (paraphrase / reverse / synthetic_reverse),
  of R_PI (frozen weights 0.1*D_inert + 0.3*flip_inertia + 0.6*frac_shared; D_inert and
  flip_inertia computed over {remove, reverse, synthetic_reverse} flips, frac_shared from
  original-condition citations), and of R_sym (frozen weights 0.3*reverse_inertia +
  0.7*intervention_disagreement, V3.16.1 definitions; reverse = natural swap), on the same
  consensus_wrong target.
- S2 paired bootstrap diffs AUROC(BF_q) - AUROC(R_PI), - AUROC(R_sym),
  - AUROC(mean_confidence), - AUROC(agreement) with CIs (superiority not required for Gate 2;
  that is Phase-4 territory).
- S3 stage-consistency: AUROC per stage (50 pairs each), sign/direction consistency,
  reported as an internal replication attempt (NOT a gate).
- S4 correct-vs-false consensus mean BF_q difference with bootstrap CI.
- S5 consensus-level descriptive behavior: reverse flip rate, synthetic reverse flip rate,
  paraphrase flip rate, remove flip rate (for comparison with frozen V3.16/V10 flip rates).

## 12. Artifacts (all under consensus_stress/round2/)

- phase2_pilot/preregistration.md (this file, frozen first)
- phase2_pilot/selection_manifest.json + selection_audit.json + labels_ledger.json (sealed)
- phase2_pilot/relevance_audit.json (+ relevance_audit_judgments.json)
- phase2_pilot/distractor_manifest.json
- phase2_pilot/paraphrase_manifest.json + paraphrase_generation_stats.json + paraphrase_audit.json
- phase2_pilot/expected_response_contract.json
- phase2_pilot/records_stage1.jsonl, records_stage2.jsonl, records.jsonl (merged, no labels)
- phase2_pilot/preoutcome_features.jsonl (no labels; frozen before merge)
- analysis/analysis.json + analysis/analysis.md + gate2_decision.md
- figures/ (ROC / risk-coverage plots)
- registry.yaml entries appended for every experiment (old entries unchanged)

## 13. Outcome firewall

Labels are merged ONLY in the analysis step after preoutcome features are frozen.
Forbidden score inputs: label, gold_binary, correct, consensus_wrong (mirror frozen R_PI set).
Dataset labels are used only offline to construct the balanced design and artifacts, never at
test time, never in probing or scoring.
