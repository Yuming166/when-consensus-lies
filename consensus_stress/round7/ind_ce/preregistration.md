# Round 7 (Agent W2) Preregistration — Independent Counter-Evidence vs Natural vs Placebo (VitaminC, gpt-6-astra relay)

Status: **FROZEN before any round-7 W2 experimental call** (relay capability probe and this
document only; the probe touches no cohort item, prompt, or contract).
Protocol id: `cs-paper-ind-ce-20260914-round7-w2`.
Parent protocols: `cs-paper-vitaminc-2026-09-13` (Round 3, Qwen3.5-4B),
`cs-paper-ling-adapted-20260913-round4` (Round 4), `cs-paper-gpt-singlepoint-20260914-round6`
(Round 6, gpt-6-astra). Research plan: `NAACL_Main_Revision_Autoresearch_Plan.md` §3/§4/§5/§16/§22.
Relay: `https://openapi.center/v1` (OpenAI-compatible `/chat/completions`), primary model
`gpt-6-astra` (fallbacks `gpt-5.6-sol`, `gpt-5.5`, recorded per call). Key source: env
`OPENAPI_CENTER_API_KEY` or `~/.codex/private.config.toml` `experimental_bearer_token`; in-memory
only, never written to files/logs/git/memory/output.

## 1. Scientific question (frozen)

For a frozen, label-symmetric VitaminC natural-pair cohort, does a gpt-6-astra 5-agent panel
selectively respond to **independently constructed, decision-relevant counter-evidence**
(`E_ind`) rather than merely reacting to arbitrary evidence perturbation? Compare three
conditions on the same items/agents:

- `natural` — the byte-identical paired mirror counter-evidence `E_j` (round-6 `reverse` layout);
- `ind` — two independently generated counter-evidence sentences `E_ind_a`, `E_ind_b`
  (supporting the opposite conclusion, decision-relevant, not byte-identical to `E_j`);
- `placebo` — decision-irrelevant distractor evidence.

Core quantity (pre-registered, label-blind):

```
Δ_CE = P(flip | ind) − P(flip | placebo)
```

`flip` is defined exactly as in Round 3/6: for item `i` and agent `a`,
`flip(i,a,cond) = 1[ answer_cond(i,a) != answer_original(i,a) ]`, where `answer_original`
is the frozen Round-6 gpt-6-astra original-condition answer (same model, adapted prompt,
temperature 0, same per-agent seed; content-addressed cache keys verified to match for the
`original` condition). `P(flip|cond)` = mean over (item, agent) pairs with valid original +
condition answers.

## 2. Frozen cohort (no reselection, no label use)

- Cohort = **first 100 items = first 50 pair_ids of
  `consensus_stress/round3/selection_manifest.json` in manifest order** (identical to the
  Round-6 formal cohort; 50 SUPPORTS + 50 REFUTES by construction, support-then-refute per pair).
- **Smoke = first 20 items (10 pairs)** → 20 x 5 agents x 3 conditions = **300 calls**.
- **Formal = first 100 items (50 pairs)** → 100 x 5 x 3 = **1,500 calls** (smoke items are a
  subset; cache replays them in the formal run). Hard cap = 100 items.
- Exact lists frozen in `cohort.json` (SHA256 recorded below). Item order = manifest order.

## 3. Independent counter-evidence generation (frozen)

- Model `gpt-6-astra`, temperature **0.7**, max_tokens **300**, no `reasoning_effort` field.
- **Two** sentences per item: `E_ind_a` (slot E01) and `E_ind_b` (slot E02). Two slots are
  required so that all five frozen personas receive at least one counter-evidence unit under the
  frozen 2-of-3 partition table (agent 2 partition = {E02,E03}). This yields up to 200 generation
  calls for 100 items (the round-7 brief's 100-150 line budget is exceeded by design to preserve
  the frozen partition contract; 2 slots x 100 items = 200).
- Deterministic per-item seeds: `seed_a = sha256("ind_ce_gen:"+item_id) % 2^31`,
  `seed_b = seed_a + 1`.
- Direct HTTP, concurrency ~10, up to 3 transport attempts with backoff (2s/5s/10s) for
  429/5xx/timeout; content-addressed cache under `round7/ind_ce/cache/`; HTTP statuses, retries,
  model id, and token usage recorded.
- The generation prompt contains **only** the claim, the original evidence, and the target
  conclusion direction (opposite of the original evidence's polarity). It never names the gold
  label, never uses the word "gold", and never states the item's label. Direction is derived from
  the `item_id` suffix (`:support` → target "the claim is false"; `:refute` → target "the claim
  is true"), never from `labels_ledger.json`.

Frozen generation prompt (system):
```
You are a careful research assistant building a counter-evidence benchmark.
You produce exactly one short factual evidence sentence.
You never include meta-commentary, reasoning, labels, quotes, or anything except the sentence.
```

Frozen generation prompt (user):
```
Claim: {claim}

Original evidence (context only; do NOT copy its wording):
{evidence_i}

Target conclusion: the claim is {target}

Write ONE new evidence sentence (a standalone factual statement, at most 60 words)
that is decision-relevant for evaluating the claim and provides evidence for the
target conclusion above.

Hard constraints:
- Do not copy, quote, or paraphrase the wording of the original evidence.
- Do not begin with meta-phrases such as "It is false that", "Evidence shows",
  "This means", or "The claim is".
- Do not use the words "claim", "evidence", "true", "false", "opposite", "target",
  "conclusion", or "label".
- Output only the sentence.
```
where `{target}` is `false` for `:support` items and `true` for `:refute` items.

## 4. E_ind audit (frozen; 30-item deterministic sample)

- Deterministic 30-item sample from the 100-item cohort: seeded RNG `random.Random(20260914)`
  picks 30 items without replacement from the formal list (item order = manifest order).
- For each sampled item, audit **both** `E_ind_a` and `E_ind_b` (60 sentences).
- (a) **Decision-relevance** (in-model audit, label-blind): gpt-6-astra temp 0, max_tokens 16,
  prompt: `Does the evidence support the claim: {claim}? Answer exactly yes or no.\nEvidence: {E_ind}`
  Expected direction = opposite of item role (`:support` → `no`, `:refute` → `yes`).
  Gate: relevance rate >= **0.80** on the 60 audited sentences.
- (b) **Independence from mirror `E_j`** (model-free, lexical):
  - token_jaccard(E_ind, E_j): median <= 0.55 AND p90 <= 0.70 AND max <= 0.80;
  - character_ratio(E_ind, E_j): median <= 0.75;
  - longest common token-run ratio (LCS length / min(tokens)) < 0.75 for every audited sentence.
  Gates must hold on the audited sample. Full-cohort overlap statistics are also reported.
- (c) Audit reads no gold labels; direction comes from the item_id suffix only.

## 5. Inference run (frozen)

- Three conditions x 5 frozen personas (V10 partition table and personas unchanged) on the
  frozen 100-item cohort. Adapted contract identical to Round 4/6 (`round4/ling_adapted_run.py`):
  server-side agent binding, JSON exemplar, no `agent_id` emission, parser
  `parse_adapted_decision`, one JSON-repair retry with the frozen `REPAIR_SUFFIX`.
- Model `gpt-6-astra`, temperature 0.0, max_tokens 160, deterministic seed
  `v10._agent_seed(agent_index)` = (7101,7207,7313,7421,7529).
- Direct HTTP, concurrency ~13, up to 3 transport attempts with backoff (2s/5s/10s) for
  429/5xx/timeout; content-addressed cache under `round7/ind_ce/cache/`.
- Packet layout (E03 = distractor is constant; E01/E02 are the manipulated decisive slots):
  - `natural`: E01 = `evidence_opp` (mirror `E_j`), E02 = `para1_opp`, E03 = `distractor`
    (byte-identical to the Round-6 `reverse` condition);
  - `ind`: E01 = `E_ind_a`, E02 = `E_ind_b`, E03 = `distractor`;
  - `placebo`: E01 = `distractor`, E02 = `distractor_para`, E03 = `distractor`.
- Inference prompts contain **no gold label and no target conclusion** — only the claim, the
  question "Does the provided evidence support the claim: ...", and the evidence packet.
- Call counts: smoke 300; formal 1,500 (smoke replayed from cache). All three conditions are run
  fresh (no reuse of Round-6 reverse cache) so the three-condition comparison shares identical
  base-prompt construction.

## 6. Gates (frozen; evaluated label-blind where noted)

- **G0 capability:** GET /v1/models returns `gpt-6-astra`; 3x minimal chat probes OK.
- **G1 pipeline:** formal valid_rate >= **0.95** (valid/1,500); smoke valid_rate >= 0.95.
  If smoke < 0.95: diagnose; the only permitted adaptation is the frozen repair retry (already
  present); otherwise STOP and report.
- **G2 E_ind audit:** relevance >= 0.80 and the Section-4 overlap thresholds (label-blind).
- **G3 Δ_CE:** point estimate > 0 AND pair-grouped bootstrap (2,000, seed 20260914+0) 95% CI
  lower bound > 0.
- **G4 placebo:** `P(flip|placebo)` <= **0.30** (label-blind; same ceiling as Round-6 paraphrase
  placebo).
- **G5 replication (diagnostic, not a gate):** |`P(flip|natural)` − Round-6 `rev_flip_rate`|
  <= 0.15 on the overlapping cohort.
- If G1/G2 fail → diagnose and report; no silent protocol repair. If G3/G4 fail (Δ_CE <= 0,
  or placebo not clean) → follow plan §6: narrow the claim, do NOT manufacture a positive.

## 7. Metrics and analysis (label-blind scoring -> freeze -> merge labels)

Label-free features per item (written to `preoutcome_features.jsonl`, NO label fields):
`consensus`, `agreement`, `mean_confidence` (from frozen Round-6 original answers), per-condition
agent flip vectors, `S_natural`, `S_ind`, `S_placebo`, `S_combined`, `S_pair_gpt`, and
`ρ(S_natural, S_ind)`.

- `S_natural(i)` = mean over 5 agents of `flip(i,a,natural)` (Round-3 `rev_flip_rate` analog).
- `S_ind(i)` = mean over 5 agents of `flip(i,a,ind)`.
- `S_placebo(i)` = mean over 5 agents of `flip(i,a,placebo)`.
- `S_combined(i)` = `0.5*S_natural(i) + 0.5*S_ind(i)` (frozen weights).
- `S_pair_gpt(i)` = `1[consensus(i) == consensus(j)]` on the round-6 gpt original consensus
  (panel gave the same verdict on both mirror items = failed to discriminate). `S_pair` from W1:
  if `round7/audit/s_pair_diagnostic.md` + values are available on the overlapping cohort before
  this analysis freezes, W1's definition/values are used as primary `S_pair`; otherwise the
  gpt-based `S_pair_gpt` above is reported and marked as the preregistered fallback.
- Flip-rate CIs and AUROC/Risk@80: pair-grouped bootstrap, 2,000 replicates,
  seed family `20260914 + k` (k=0..9), reusing `round3/analysis_lib.py`.
- AUROC/Risk@80 target: `consensus_wrong` on the high-consensus (HC) subset
  (agreement >= 0.8), labels from `round3/labels_ledger.json` merged ONLY after
  `preoutcome_features.jsonl` is written and hashed (outcome firewall).
- Increment of `S_ind` over `S_natural`: grouped out-of-fold logistic regression
  (leave-one-pair-out) `P(wrong|HC) ~ [S_natural]` vs `[S_natural, S_ind]`; report OOF AUROC
  difference with pair-grouped bootstrap CI. Label-free features are frozen before labels merge;
  the logistic fit itself happens after label merge (labeled analysis), with wide CIs expected at
  HC n≈100 and small wrong-n; reported honestly, not a gate.

## 8. Outcome firewall

Gold labels (`round3/labels_ledger.json`) are merged **only after** the run records and the
label-free `preoutcome_features.jsonl` are written and SHA256-frozen. Before that freeze, no
script reads `labels_ledger.json` or any `gold_label` field; item role/direction comes from the
`item_id` suffix. Labels are never sent to the relay and never used to choose prompts, subsets,
or adapters.

## 9. Instability / failure handling (frozen)

- Consecutive **20** transport failures (503/429/timeout) in a run -> stop immediately, write
  what exists as PARTIAL, no retry-until-complete.
- Relay unavailable for the primary model -> try fallbacks in order; if all fail -> BLOCKED
  record (no fabricated numbers).
- No filtered subset is ever presented as the full result; every summary reports actual call
  counts, parse yield, HTTP/retry stats, token usage, and model id(s).

## 10. Outputs (all under `consensus_stress/round7/ind_ce/`)

preregistration.md (this file), cohort.json, execution_notes.md, run_summary_healthcheck.json,
run_summary_generation.json, run_summary_audit.json, run_summary_smoke.json,
run_summary_formal.json, records.jsonl (raw responses, local), e_ind_artifacts.jsonl,
preoutcome_features.jsonl (label-free) + preoutcome_features_meta.json, analysis/ind_ce_*.md+json,
figures/, artifact_hashes.json, decision.md, SUMMARY.md (5-line Chinese). No git commit; no
changes to frozen Round-3/4/6 artifacts.

## 11. Frozen input hashes (recorded at preregistration time)

- `consensus_stress/round3/selection_manifest.json`:
  `5f575ff873b3243b4916f77ab81269476da937d466eec967eff0934efe39089b`
- `consensus_stress/round3/paraphrase_manifest.json`:
  `5b322c4973328b5323edf8111a4e4195c4a4d895c9890dfb73a8d0f29d514435`
- `consensus_stress/round3/labels_ledger.json`:
  `770ede3f79b018c47aa982e6cb3f13b9d504b5c14950f7f1a8f6de196ffcbc5a`
- `consensus_stress/round6/large_model/records.jsonl`:
  `57e97b6d54d63b7beae2a22604dfc4207ef757006ea0db40f6881a022017376e`
- `consensus_stress/round7/ind_ce/cohort.json`: `e987ba177b72726245189c3a42f64ffaaa0494443d351639680a97eea611413f`

(To be filled at freeze time by `scripts/freeze_cohort.py`, which also writes `artifact_hashes.json`.)

Protocol frozen. No experimental call made at the moment this document is finalized.
