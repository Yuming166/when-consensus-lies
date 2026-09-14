# Phase 2 Pilot Preregistration — Expected-Response Faithfulness on BoolQ (Qwen3.5-4B)

Status: FROZEN before any agent model call. Protocol id: `cs-pilot-boolq-2026-09-12`.
All artifact generation (selection, substitutes, paraphrases) and all agent calls happen
only after this file is written and the registry entry is PROPOSED/RUNNING.

## 1. Research question (Gate 2)

When 5 Qwen3.5-4B agents form a high-consensus answer on BoolQ, does an outcome-blind
expected-response faithfulness profile (measured by controlled evidence stress) distinguish
correct consensus from false consensus, beyond ordinary confidence / vote agreement, and does
the distinction survive null/placebo controls?

## 2. Population and selection (frozen)

- Dataset: `data/benchmarks/boolq/train.parquet` (9427 rows).
  - Rationale (amended before any model call): all 558 eligible BoolQ VALIDATION roots are already
    covered by frozen V11.1 (200) + V12/V12.1 (358) selections. Using train gives the pilot a
    genuinely independent cohort with no overlap with any frozen formal selection, so the pilot's
    R_PI baseline is computed fresh on unseen questions. This amendment was made before any agent call.
- Eligibility: same deterministic 3-sentence evidence-unit extraction as frozen V10
  (MIN_SENTENCE_TOKENS=8, MAX_SENTENCE_TOKENS=80, cosine overlap gates 0.08/0.10/0.60,
  FACTS_PER_QUESTION=3). Source root = sha256(question + passage).
- Selection: N=100 questions, 50 `yes` + 50 `no` (BoolQ gold answer used ONLY for balance
  in offline selection, exactly as the frozen project does; never sent to the model, never
  used in probing/scoring). Order fixed by sha256(SALT + cqid) with
  SALT = b"cs-pilot-boolq-2026-09-12\n".
- 5 agents, 2-of-3 evidence partition table identical to frozen V10.
- Agent personas identical to frozen V10 (literal_evidence, skeptical_auditor,
  consistency_checker, counterfactual_reasoner, minimal_judge).

## 3. Conditions and expected-response oracle (frozen; no label, no correctness used)

| condition | construction | expected response Y*(T) |
|---|---|---|
| original | frozen V10 packet (2 units) | reference Y0 |
| paraphrase | LLM meaning-preserving paraphrase of each packet unit (label-free prompt, offline artifact) | Y* = Y0 (no deterministic change) |
| reverse | "Task-local counterfactual: it is false that: <unit>" (same as frozen V10) | Y* = flip(Y0) |
| substitute | LLM opposite-supporting rewrite of each packet unit (same generation contract as frozen V10; offline artifact, gold answer used only to write the artifact) | Y* = flip(Y0) |
| remove | empty packet (same as frozen V10) | NO-FORCED-RESPONSE (unscored for faithfulness; descriptive only) |

Per-agent Y0 is the agent's own original-condition answer. Expected responses are defined
from the transformation semantics alone, before any agent call (plan Rule 7).

## 4. Model calls

- Endpoint: http://127.0.0.1:31518/v1/chat/completions, model `Qwen3.5-4B`, temperature 0.0,
  seed fixed per (agent,condition) call, max_tokens 160, prompt-only JSON (no server-side
  response_format), no `reasoning_effort` field.
- Artifact calls: 100 questions x 3 units = 300 substitute rewrites + 300 paraphrases = 600.
- Agent calls: 100 questions x 5 agents x 5 conditions = 2500.
- Total ~3100 unique calls; all cached by content hash; retries capped at 2 with a frozen
  repair suffix identical in spirit to the frozen V1 REPAIR_SUFFIX.

## 5. Primary endpoints (frozen)

On the high-consensus subset (original agreement >= 0.8, matching frozen threshold):
- E1 (agent-level expected-response accuracy): fraction of (agent, scored condition) pairs with
  observed == expected, overall and per condition (paraphrase, reverse, substitute).
- E2 (consensus-level BF_q): for each question, mean over agents of faithfulness across the
  three scored conditions. Also per-condition consensus faithfulness
  (fraction of agents with expected response in that condition).
- E3 (primary gate): AUROC(BF_q, consensus_wrong) with 1000-question bootstrap 95% CI.
  Gate passes only if CI lower bound > 0.5 AND point estimate >= 0.60.

## 6. Secondary analyses

- S1: AUROC of each per-condition faithfulness feature (paraphrase / reverse / substitute) and
  of R_PI (frozen weights 0.1/0.3/0.6 on D_inert/flip_inertia/frac_shared computed from pilot
  records with frozen definitions) on the same consensus_wrong target.
- S2: paired bootstrap difference AUROC(BF_q) - AUROC(mean_confidence), - AUROC(agreement),
  - AUROC(R_PI). Reported with CIs; superiority to R_PI is NOT required for Gate 2 (that is
  Phase 4 Gate 4), but reducibility to confidence/agreement is checked:
  AUROC(BF_q | agreement==0.8) must still exceed 0.5 after conditioning on agreement, and
  Spearman(BF_q, agreement) and Spearman(BF_q, mean_confidence) are reported.
- S3: label-symmetric reporting (yes/no subgroups) given the known BoolQ asymmetry.
- S4: correct-vs-false consensus mean BF_q difference with bootstrap CI.

## 7. Controls (frozen)

- C1 placebo (semantic-preserving): paraphrase flip rate at agent level and consensus level.
  If agent-level paraphrase flip rate > 0.30, the semantic-preserving axis is flagged as a
  control violation and reported; the claim is then restricted accordingly.
- C2 permutation: shuffle per-question condition labels (which condition is scored as
  preserving vs reversing) 1000 times; distribution of AUROC(BF_permuted, consensus_wrong)
  must center near 0.5; observed AUROC must exceed the 95th percentile of the permutation
  distribution.
- C3 randomization of intervention assignment at the agent level: re-assign agents' condition
  responses randomly and re-compute BF_q -> AUROC near 0.5.

## 8. Gate 2 decision rule (frozen)

PASS if and only if ALL of:
1. pipeline completes with >= 0.95 valid records and no unrepairable parser failures;
2. E3 gate passes (CI lower bound > 0.5, point >= 0.60);
3. C2 permutation control passes (observed AUROC > 95th pct of permutation distribution);
4. C1 placebo control does NOT show violation (paraphrase flip rate <= 0.30);
5. BF_q is not reducible to agreement/confidence: after conditioning on agreement==0.8,
   AUROC still > 0.5 (CI lower bound), and Spearman(BF_q, agreement) and
   Spearman(BF_q, mean_confidence) are not >= 0.9.

FAIL if any criterion fails: record FAIL and decide kill/reformulate/behavioral-only.
No interim metric inspection beyond smoke validity before all calls complete.

## 9. Artifacts (all under consensus_stress/phase2/)

- selection_manifest.json (100 questions, evidence units, partitions)
- substitute_manifest.json / paraphrase_manifest.json (frozen before agent calls)
- expected_response_contract.json (condition -> expected response rule)
- records.jsonl (raw agent outputs, cache)
- preoutcome_features.jsonl (features computed from records; no label fields)
- analysis/analysis.json + analysis/analysis.md (after label merge)

## 10. Outcome firewall

Labels are merged ONLY in the analysis step after preoutcome features are frozen.
Forbidden score inputs: label, gold_binary, correct, consensus_wrong (mirror frozen R_PI set).
Substitute generation uses gold answer offline to construct the frozen artifact (frozen
project practice), never at test time.

## Amendment A (before any agent call; artifact generation only)

- Substitute rewrite generation uses `max_tokens=256` (technical fix: the frozen
  160-token cap truncated ~32% of rewrites on the local Qwen3.5-4B endpoint; truncation
  caused false length-window failures, not semantic failures).
- A bounded SINGLE repair call is allowed per failed substitute (mirroring the frozen
  V12.1 bounded second-repair pattern), emphasizing the frozen 0.5-1.5x length window.
  Fail-fast still applies if an item remains unusable after one repair.
- These changes affect only offline artifact generation; they do not touch the
  evaluation protocol, the expected-response oracle, or any agent-decision call.

## Amendment B (before any agent call; artifact generation only)

- Substitute generation uses a strengthened artifact prompt (explicit opposite-support,
  explicit negation/contradiction, no meta-language, same entity/topic, 0.5-1.5x length
  window) instead of the frozen V10 rewrite prompt, because the frozen prompt produced a
  ~32% length-window failure rate on the local Qwen3.5-4B endpoint and several
  semantically non-opposite rewrites in smoke tests.
- Up to TWO bounded repair attempts are allowed per substitute (3 total calls max per item).
- Artifact validity audit (offline, before agent calls): the orchestrator reads a random
  sample of >= 30 generated substitutes and judges whether each clearly supports the
  opposite answer. If < 80% of the audited sample is judged opposite-supporting, the
  substitute condition is treated as a WEAK/no-forced-response condition for expected
  response scoring (per plan 4.1 "no-forced-response" category) and reported as a
  limitation; the reverse and paraphrase conditions carry the primary expected-response
  analysis.

## Amendment C (before any agent call; artifact generation only)

- The substitute artifact length window is RELAXED for the pilot from the frozen
  0.5-1.5x to 0.30x-3.0x (min 5 tokens, abs cap 80), because the local Qwen3.5-4B
  endpoint produces terse but semantically opposite single-sentence rewrites that the
  frozen window rejects (41% usable under the strict window vs terse rewrites of ~8-15
  tokens). The semantic requirement (clearly supports the opposite answer, same
  entity/topic) is unchanged and is guarded by the offline audit in Amendment B.
  This is an offline artifact-generation parameter; the evaluation protocol and
  expected-response oracle are unchanged.

## Amendment C2 (before any agent call; artifact generation only)

- The relative floor (0.30x) is removed from the substitute artifact parser;
  only a 5-token absolute floor, a 3.0x ceiling, and an 80-token cap remain.
  The local model's terse rewrites for long source sentences (44-59 tokens)
  fell below the relative floor despite being single-sentence and semantically
  opposite. Semantic opposition is still guarded by the offline audit (B).
