# Round 7 (Agent W2b) Preregistration — STRICT Independent Counter-Evidence vs Matched Placebo (VitaminC, gpt-6-astra)

Status: **FROZEN before any round-7 W2b experimental call** (this document, the cohort
freeze, and capability probes only; no cohort-item prompt, evidence generation, or
inference call is made before this file is hashed).
Protocol id: `cs-paper-ind-ce-strict-20260915-round7-w2b`.
Parent protocols: `cs-paper-vitaminc-2026-09-13` (Round 3, Qwen3.5-4B),
`cs-paper-gpt-singlepoint-20260914-round6` (Round 6, gpt-6-astra),
`cs-paper-ind-ce-20260914-round7-w2` (Round 7 W2, label-coupled E_ind). Research plan:
`NAACL_Main_Revision_Autoresearch_Plan.md` §3/§4/§5/§16/§22. Frozen target:
`consensus_stress/round7/ind_ce/TARGET_SPEC.md` (highest authority).
Relay: `https://openapi.center/v1` (OpenAI-compatible `/chat/completions`), primary model
`gpt-6-astra` (fallbacks `gpt-5.6-sol`, `gpt-5.5`, recorded per call). Key: env
`OPENAPI_CENTER_API_KEY` or `~/.codex/private.config.toml` `experimental_bearer_token`;
in-memory only, never written to files/logs/git/memory/output.

## 0. Why this protocol exists (strict version)

W2's E_ind generation was **label-coupled**: for each item it read the `item_id` suffix
(`:support` / `:refute`) to derive the target conclusion direction, and it fed the
original evidence `E_i` into the generation prompt. A skeptical reviewer can object that
(i) direction is derived from the item identity, i.e. from the gold-polarity structure,
and (ii) the generated evidence could inherit wording from the original/mirror evidence.
TARGET_SPEC §1 therefore requires a **strict** construction that is independent of
(a) mirror text, (b) gold label / item polarity, and (c) the model's original answers:

- Generation input = **only the claim text** (shared verbatim by both mirror items of a
  pair). No item_id, no `:support`/`:refute`, no gold, no `labels_ledger`, no original or
  mirror evidence, no model original answers.
- Per claim, one call generates **both** directions in a single response: `SEGMENT_TRUE`
  (2 sentences supporting claim-true) and `SEGMENT_FALSE` (2 sentences supporting
  claim-false). The model never knows which item (or which direction) will be used for
  which item.
- **Offline, after generation is complete and hashed**, frozen gold assigns
  `E_ind_strict(i)` = the segment that OPPOSES item `i`'s gold:
  `gold=SUPPORTS -> SEGMENT_FALSE`, `gold=REFUTES -> SEGMENT_TRUE`.
- A **matched placebo** `E_pm(i)` is generated per claim: topic-relevant, matched
  length/tone/format, but decision-irrelevant (neither supports nor refutes the claim).
- Natural (mirror) condition is **reused** from frozen W2/round-6 gpt records (no rerun);
  flip is always against the frozen round-6 gpt original answer.

This answers the plan's P0/P1 question: does counter-evidence responsiveness survive when
the counter-evidence is constructed without any mirror text, item polarity, or gold?

## 1. Scientific question (frozen)

For a frozen, label-symmetric VitaminC natural-pair cohort (first 50 items = 25 pairs),
does a gpt-6-astra 5-agent panel **selectively respond to independently constructed,
decision-relevant counter-evidence** (`E_ind_strict`) rather than merely reacting to
arbitrary evidence perturbation? Compare on the same items/agents:

- `ind_strict` — single-slot packet `E01 = E_ind_strict(i)` (generated claim-only,
  assigned offline to oppose the item's gold);
- `pm` — single-slot packet `E01 = E_pm(i)` (matched placebo, decision-irrelevant);
- `natural` — **reused** frozen W2/round-6 gpt records (mirror `E_j` layout; no rerun).

Core quantity (pre-registered, label-blind):

```
Δ_CE = P(flip | ind_strict) − P(flip | pm)
```

`flip(i,a,cond) = 1[ answer_cond(i,a) != answer_original(i,a) ]`, where
`answer_original` is the frozen Round-6 gpt-6-astra original-condition answer (same
model, adapted contract, temperature 0, same per-agent seed; content-addressed cache).
`P(flip|cond)` = mean over (item, agent) pairs with valid original + condition answers.

## 2. Frozen cohort (no reselection, no label use)

- Cohort = **first 50 items = first 25 pair_ids of
  `consensus_stress/round3/selection_manifest.json` in manifest order**
  (support-then-refute per pair; 25 SUPPORTS + 25 REFUTES by construction). Overlap with
  W2's 100-item cohort is intentional (25 of W2's 50 pairs); the strict protocol is fully
  isolated in `round7/ind_ce_strict/` and never writes to `round7/ind_ce/`.
- **Smoke = first 20 items (10 pairs)** -> 20 x 5 agents x 2 conditions = **200 calls**.
- **Formal = all 50 items (25 pairs)** -> 50 x 5 x 2 = **500 calls** (smoke items replay
  from cache). Hard cap = 50 items.
- Exact item list frozen in `cohort.json` (SHA256 recorded below). Item order = manifest
  order. No labels are consulted to select or order the cohort.

### 2.1 Known frozen-data gap (pre-registered handling)

Round-6 original record for (`5ec7d50dc9e77c0008442245:590d0ddcb433:support`, agent 1)
is missing (final_error `http 429`, transport failed after 3 attempts). Handling (frozen):
- (item,agent) pair-level flip analyses (Δ_CE etc.) use every available original answer
  (249/250 for this cohort); the missing pair is excluded from **both** conditions
  symmetrically.
- Item-level feature rows (`preoutcome_features.jsonl`) follow the W2/round-3 rule:
  an item is included only if **all 5** frozen original answers exist. The support half of
  the affected pair is therefore excluded from item-level analyses (expected n=49, 25
  pairs, one pair contributing 1 item); this is reported honestly, not patched.

## 3. Strict evidence generation (frozen; label-free)

Model `gpt-6-astra`, temperature **0.7**, max_tokens **300**, no `reasoning_effort` field.
Direct HTTP (relay), concurrency ~8, up to **8 transport attempts** with backoff
(2s/4s/8s/15s/30s/45s/60s) for 429 / 5xx / 400-with-"upstream" / timeout; content-addressed
cache under `round7/ind_ce_strict/cache/`; HTTP statuses, retries, model id, and token
usage recorded per call. One call per claim for the dual-direction segment (25 claims) and
one call per claim for the placebo (25 claims) = **50 generation calls total**.

Generation input = **only the claim** (verbatim, shared by the two mirror items of the
pair). The prompt never contains: item_id / pair_id, the strings `:support`/`:refute`,
`SUPPORTS`/`REFUTES`, `gold`, `label`, the original or mirror evidence text, any model
answer, or any statement of which item the evidence will be used for. The exact user
prompt is logged per call (`prompt_log`) for the audit's input-cleanliness check.

Deterministic per-claim seeds (no labels):
- dual: `seed_dual = sha256("ind_ce_strict_dual:" + pair_id) % 2^31`
- placebo: `seed_pm = sha256("ind_ce_strict_pm:" + pair_id) % 2^31`

### 3.1 Dual-direction prompt (frozen)

System:
```
You are a careful research assistant building a counter-evidence benchmark.
You produce exactly two short factual evidence segments.
You never include meta-commentary, reasoning, labels, quotes, or anything
except the two formatted lines.
```

User:
```
Claim: {claim}

Write exactly two evidence segments about this claim.

SEGMENT_TRUE — exactly 2 sentences of concrete factual content that, if accurate,
supports the claim being TRUE.
SEGMENT_FALSE — exactly 2 sentences of concrete factual content that, if accurate,
supports the claim being FALSE.

Output exactly two lines, each starting with the marker and a pipe, followed by the
two sentences joined by a space:
<T>|sentence1. sentence2.
<F>|sentence1. sentence2.

Hard constraints:
- Each segment is exactly 2 sentences and at most 70 words total.
- Use concrete facts (names, dates, numbers, attributes), never vague or hedged wording.
- Both segments must concern the same subject matter as the claim.
- Do not copy or paraphrase the claim wording beyond the necessary subject nouns.
- Do not begin sentences with meta-phrases such as "It is false that", "Evidence shows",
  "This means", or "The claim is".
- Do not use the words: claim, evidence, true, false, support, target, conclusion,
  label, statement, segment, direction inside the sentences themselves.
- No quotes, no explanation, no extra text.
```

### 3.2 Matched placebo prompt (frozen)

System:
```
You are a careful research assistant building a benchmark control condition.
You produce exactly two sentences of factual background content.
You never include meta-commentary, reasoning, labels, quotes, or anything except
the two sentences.
```

User:
```
Claim: {claim}

Write exactly two sentences of factual background content about the subject of the
claim that NEITHER support NOR refute the claim: the content is topically related but
gives no information that helps decide whether the claim is true or false.

Output exactly one line with the two sentences joined by a space:
sentence1. sentence2.

Hard constraints:
- Exactly 2 sentences and at most 70 words total.
- Use concrete facts (names, dates, numbers, attributes), never vague or hedged wording.
- Topically related to the claim's subject but decision-neutral: a reader cannot tell
  from these sentences whether the claim is true or false.
- Do not copy or paraphrase the claim wording beyond the necessary subject nouns.
- Do not begin sentences with meta-phrases such as "Evidence shows", "This means",
  or "The claim is".
- Do not use the words: claim, evidence, true, false, support, refute, target,
  conclusion, label, statement, sentence inside the sentences themselves.
- No quotes, no explanation, no extra text.
```

### 3.3 Parsing / validity (frozen)

- Dual response: split into lines; keep lines matching `^<T>\|` / `^<F>\|`; split the
  remainder into sentences on `(?<=[.!?])\s+`; **require exactly 2 sentences per
  segment**; strip outer quotes/fences; reject if any sentence starts with a banned
  prefix or contains a banned word; reject if segment word count > 70.
- Placebo response: one line, exactly 2 sentences, <= 70 words, no banned prefix/word.
- One repair attempt per call (append repair suffix: "Your previous output was invalid.
  Return only the required formatted sentences."). If still invalid -> record FAILED
  (success=false, final_error) and exclude that claim's two items from downstream
  analysis (completeness reported). If > 10% of generation calls fail, STOP and report.

## 4. Offline gold assignment (frozen; the ONLY label-consuming step)

After generation artifacts `e_gen_artifacts.jsonl` are written and SHA256-frozen,
`assign_strict.py` reads the frozen `round3/labels_ledger.json` and writes
`e_ind_strict_artifacts.jsonl`:

- `E_ind_strict(i) = SEGMENT_FALSE` if `gold(i) == SUPPORTS`, else `SEGMENT_TRUE`
  (i.e. always the segment opposing item `i`'s gold);
- `E_pm(i) = placebo` segment of item `i`'s pair.

The assignment is deterministic, mechanical, and uses no model call. Generation prompts
never depend on this step. All inference/audit prompts contain only claim + evidence
text; they never contain gold, `target`, or the model's original answer.

## 5. Audit (frozen; label-blind; 30 items = first 15 pairs)

Deterministic sample: **first 30 items in cohort order (pairs 0-14)**. Judge = gpt-6-astra,
temperature 0, max_tokens 16, direct relay, deterministic seeds `99101 + k`.

1. **Direction-compliance / decision-relevance (label-blind).** For each of the 30 items,
   judge BOTH segments (the `SEGMENT_TRUE` and `SEGMENT_FALSE` of the item's pair):
   - `Q_T`: "Does the evidence support the claim being TRUE? Answer exactly yes or no.
     Evidence: {text}"
   - `Q_F`: "Does the evidence support the claim being FALSE? Answer exactly yes or no.
     Evidence: {text}"
   Decision-relevant := (Q_T == yes) for SEGMENT_TRUE and (Q_F == yes) for SEGMENT_FALSE.
   Gate: mean compliance over the 60 segment-judgments >= **0.80**. Because the assigned
   `E_ind_strict(i)` is the segment whose requested direction opposes item `i`'s gold,
   compliance in the requested direction IS decision-relevance of the strict
   counter-evidence, evaluated without reading gold.
2. **Independence from mirror evidence (label-blind, conservative).** For each audited
   item, compare `E_ind_strict(i)` against **both** original evidence texts of its pair
   (`supports_evidence`, `refutes_evidence` from the selection manifest) and take the max
   for each overlap statistic. This is gold-free and bounds (>=) the overlap against the
   true mirror `E_j` (which is the paired item's original evidence — identifying it
   exactly requires gold, so the max-over-both bound is the preregistered label-blind
   gate; overlap vs the true `E_j` is additionally reported post-hoc after label merge).
   Gates (max over the two pair evidences): token jaccard median <= 0.40, p90 <= 0.55,
   max <= 0.70; character ratio (difflib SequenceMatcher) median <= 0.50, max <= 0.70;
   LCS token ratio max <= 0.65.
3. **Generation-input cleanliness (log check).** For the 30 audited items, verify from the
   logged `prompt_log` that the generation user prompt: contains the claim text; does NOT
   contain the item_id / pair_id; does NOT contain `:support`/`:refute`;
   `SUPPORTS`/`REFUTES`; `gold`; `label`; nor any of the pair's evidence texts. All 30 must
   pass (otherwise the generation was not claim-only -> audit FAIL).
4. **Placebo format + irrelevance.** For each audited item, judge:
   "Does this text bear on the truth of the claim in EITHER direction (supporting or
   refuting it)? Answer exactly yes or no. Text: {pm}". Expect "no" for >= **0.80**.
   Format match: exactly 2 sentences; per-sentence word counts within [0.5, 2.0]x of the
   corresponding `E_ind_strict` segment; no banned words/prefixes.

Audit outputs: `audit_sample.jsonl`, `run_summary_audit.json`. Audit calls do not read
gold and do not reveal which segment will be assigned to which item.

## 6. Inference (frozen; label-free)

- Model gpt-6-astra, temperature 0.0, max_tokens 160, deterministic per-agent seeds
  `v10._agent_seed(agent_index)` = (7101, 7207, 7313, 7421, 7529); adapted contract
  (`round4/ling_adapted_run.build_messages` + `parse_adapted_decision`, JSON
  {answer, confidence, cited_evidence_ids}).
- 5 frozen personas (`v10.AGENT_PERSONAS`).
- **Single-slot packet**: both new conditions present exactly one evidence unit
  `E01 = E_ind_strict(i)` (`ind_strict`) or `E01 = E_pm(i)` (`pm`); all 5 agents see the
  same single unit. This is a deliberate, preregistered deviation from the 3-slot 2-of-3
  partition table of the mirror layout: the strict design asks each persona how it
  responds to exactly one piece of independently constructed evidence, avoiding any
  filler/distractor dilution and any need for a second counter-evidence slot. The
  inference contract (JSON decision, persona system prompts, seeds) is otherwise
  identical to round-6/W2.
- Inference prompts contain only the claim + the evidence packet; **never** gold, target
  conclusion, or the model's original answer. `messages_sha256` is logged per record.
- `natural` is NOT rerun: `S_natural` is reused from frozen W2 round-7 records
  (`round7/ind_ce/records.jsonl`, condition `natural`, byte-identical layout to round-6
  `reverse`) and frozen round-6 originals.
- Smoke (20 items, 200 calls) must reach valid_rate >= **0.95** before the formal run.
  Formal = 50 items, 500 calls (smoke cached). Abort after 20 consecutive transport
  failures; write PARTIAL and report.

## 7. Gates (frozen; evaluated label-blind where noted)

- **G0 capability:** GET /v1/models lists `gpt-6-astra`; 3 minimal chat probes OK.
- **G1 pipeline:** smoke valid_rate >= 0.95 AND formal valid_rate >= 0.95.
- **G2 audit:** direction-compliance/relevance >= 0.80; independence overlap thresholds;
  generation-input cleanliness all-pass; placebo irrelevance >= 0.80 and format match.
- **G3 Δ_CE:** point estimate > 0 AND pair-grouped bootstrap (2,000, seed 20260915+0)
  95% CI lower bound > 0.
- **G4 placebo ceiling:** `P(flip|pm)` <= **0.30** (label-blind).
- **G5 (diagnostic, not a gate):** report `|P(flip|ind_strict) − P(flip|natural)|` and
  W2 natural replication on the 50-item overlap (|our natural reuse − W2 value| <= 0.05).
- If G1/G2 fail -> diagnose and report; no silent protocol repair. If G3/G4 fail
  (Δ_CE <= 0, no increment, or placebo not clean) -> follow TARGET_SPEC §6 / plan §6:
  record the negative result, do NOT optimize the method, and narrow the paper claim to
  the natural-pair consensus-fragility phenomenon.

## 8. Metrics and analysis (label-blind scoring -> freeze -> merge labels)

Label-free per-item features (`preoutcome_features.jsonl`, NO label fields, written and
hashed BEFORE any label read): `consensus`, `agreement`, `mean_confidence`
(from frozen round-6 original answers), per-condition agent flip vectors,
`S_natural`, `S_ind_strict`, `S_pm`, `RS_q`, `S_combined_natural_ind`.

- `S_natural(i)` = mean over 5 agents of `flip(i,a,natural)` (reused W2/round-6 gpt).
- `S_ind_strict(i)` = mean over 5 agents of `flip(i,a,ind_strict)`.
- `S_pm(i)` = mean over 5 agents of `flip(i,a,pm)`.
- `RS_q(i)` = `-bf_q(i)` from frozen `round3/preoutcome_features.jsonl` (Qwen frozen
  risk score; `bf_q == (bf_paraphrase + bf_reverse)/2` verified on all 600 rows).
- `S_combined_natural_ind(i)` = 0.5*S_natural + 0.5*S_ind_strict (frozen weights).
- Risk direction: higher = riskier, `R_* = -S_*` (higher flip rate = more responsive =
  lower risk), matching W2/round-6 convention.

After the feature freeze (SHA256 recorded), labels from `round3/labels_ledger.json` are
merged: `gold_label`, `gold_yes`, `consensus_wrong = (consensus=="yes") != gold_yes`.
Analyses (all pair-grouped bootstrap, 2,000 replicates, seed family 20260915+k):

1. `Δ_CE = P(flip|ind_strict) − P(flip|pm)` over (item,agent) pairs, CI seed +0.
2. `S_ind_strict` alone: AUROC and Risk@80 on the HC subset (agreement >= 0.8),
   CI seeds +1 / +2.
3. Paired increments: `R_ind_strict − R_natural`, `R_ind_strict − RS_q`,
   `R_ind_strict − R_pm` (diagnostic) with CI seed +3; `ρ(S_natural, S_ind_strict)`
   with pair-grouped CI seed +4.
4. OOF logistic increment (diagnostic, not a gate): leave-one-pair-out logistic
   `P(wrong|HC) ~ [S_natural]` vs `[S_natural, S_ind_strict]`, and
   `~ [RS_q]` vs `[RS_q, S_ind_strict]`; OOF AUROC difference with pair-grouped CI
   seed +5. Small HC wrong-n expected; reported honestly.
5. Leakage audit: for the 30 audited items x 2 conditions x 5 agents (300 records),
   rebuild the inference messages from logged artifacts and verify the prompt contains
   claim + E01 text only; no gold/target/original-answer/mirror evidence; no item_id.
6. Completeness: per-condition call counts, parse yield, HTTP/retry stats, model ids,
   token usage, excluded items (missing originals / failed generation) reported in every
   summary.

## 9. Outcome firewall

Gold labels are merged ONLY after (a) all run records, (b) `e_gen_artifacts.jsonl`,
(c) `e_ind_strict_artifacts.jsonl`, (d) `preoutcome_features.jsonl` are written and
SHA256-frozen. Before that freeze, no script reads `labels_ledger.json` or any
`gold_label` field (the sole exception is `assign_strict.py`, which runs strictly after
generation is complete and frozen, and writes only the assigned texts + directions;
`preoutcome_features.jsonl` is built without reading that gold field). Labels are never
sent to the relay and never used to choose prompts, subsets, or adapters.

## 10. Instability / failure handling (frozen)

- Consecutive 20 transport failures in a run -> stop immediately, write PARTIAL, report.
- Relay unavailable for primary model -> fallbacks in order; if all fail -> BLOCKED
  record (no fabricated numbers).
- No filtered subset is ever presented as the full result; every summary reports actual
  call counts, parse yield, HTTP/retry stats, token usage, and model id(s).

## 11. Outputs (all under `consensus_stress/round7/ind_ce_strict/`)

preregistration.md (this file), cohort.json, execution_notes.md,
run_summary_healthcheck.json, run_summary_generation.json, run_summary_audit.json,
run_summary_smoke.json, run_summary_formal.json, records_smoke.jsonl, records.jsonl,
e_gen_artifacts.jsonl, e_ind_strict_artifacts.jsonl, audit_sample.jsonl,
preoutcome_features.jsonl + preoutcome_features_meta.json, analysis/strict_results.json +
analysis/strict_results.md, artifact_hashes.json, decision.md (reviewer-oriented),
SUMMARY.md (5-line Chinese). No git commit. No writes to `round7/ind_ce/` or any frozen
Round-3/4/6 artifact.

## 12. Frozen input hashes (recorded at freeze time)

Filled by `scripts/freeze_cohort.py`, which writes `cohort.json` and
`artifact_hashes.json` (SHA256 of this file, selection_manifest.json, labels_ledger.json,
round3/preoutcome_features.jsonl, round6 records.jsonl, round7/ind_ce records.jsonl, and
cohort.json itself). Protocol frozen. No experimental call is made at the moment this
document is finalized.
