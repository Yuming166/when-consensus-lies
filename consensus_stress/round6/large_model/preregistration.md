# Round 6 (Agent D) Preregistration — Large-Model Single-Point Validation (VitaminC, relay GPT-class)

Status: **FROZEN before any round-6 experimental large-model call.** Only the capability gate
(GET /v1/models + 3 x minimal chat/completions `max_tokens=16` "PONG") and this document
were completed before freezing. Those probes touch no cohort item, prompt, or contract.
Protocol id: `cs-paper-gpt-singlepoint-20260914-round6`.
Parent protocol: `cs-paper-vitaminc-2026-09-13` (Round 3, Qwen3.5-4B) and
`cs-paper-ling-adapted-20260913-round4` (Round 4, Ling-3.0-tiny).
Relay: private relay `https://openapi.center/v1`, OpenAI-compatible `/v1/chat/completions`.
Key source: environment variable `OPENAPI_CENTER_API_KEY` or existing
`~/.codex/private.config.toml` `experimental_bearer_token`; loaded in-memory only, never
written to files, logs, git, memory, or output.

## 1. Scientific question (frozen)

On a frozen, label-symmetric VitaminC natural-pair cohort, does the outcome-blind
counter-evidence-responsiveness profile `RS_q = -BF_q` (higher = riskier) of a relay
GPT-class model separate that model's own high-consensus wrong decisions from its correct
ones (within-model AUROC), and does the round-3/round-4 mechanism narrative
(natural-reversal fidelity lower on wrong than on correct consensus) reproduce?
Item-level transfer of Qwen/Ling frozen `RS_q` to the GPT model's errors is reported as
secondary evidence, not as a gate.

## 2. Frozen cohort and artifacts (no reselection, no label use)

- Cohort = **first 100 pair_ids of `consensus_stress/round3/selection_manifest.json` in
  manifest order** (all stage 1) = **200 items** (100 SUPPORTS + 100 REFUTES, label-symmetric
  by construction). Exact lists are frozen in `cohort_first100_pairs.json` (SHA256 recorded below).
- Subsets (deterministic, item order = manifest order, support-then-refute per pair):
  - **Smoke: first 20 items** (10 pairs) → 20 x 5 agents x 5 conditions = **500 calls**.
  - **Formal: first 100 items** (50 pairs) → 100 x 5 x 5 = **2,500 calls** (smoke items are a
    subset; cache makes their calls cache hits in the formal run). Budget cap = 100 items.
- Reuse the frozen model-agnostic artifacts unchanged: paraphrases (`paraphrase_manifest.json`),
  natural supports/refutes evidence, distractors, frozen V10 partitions/personas, and the
  decision-relevance-aware expected-response oracle (R1-R6) from Round 3.
- Reuse the sealed Round-3 label ledger **only after** preoutcome features are frozen and hashed
  (outcome firewall, Section 7).

## 3. Model-capability contract adaptation (pre-registered before calls)

Same adaptation rationale as Round 4 (the model is never trusted to self-identify; agent
identity is bound server-side):

1. The user prompt does **not** ask the model to emit `agent_id`.
2. Every prompt contains the frozen JSON shape exemplar (values explicitly illustrative,
   identical across all items/agents/conditions):
   `{"answer":"yes","confidence":0.75,"cited_evidence_ids":[]}`
3. The parser requires exactly `answer`, `confidence`, `cited_evidence_ids`; validates
   answer in {yes,no}; confidence finite in [0,1]; citations a unique list of non-empty
   strings drawn from the assigned packet (empty list allowed when packet empty). If the model
   emits `agent_id`, it is ignored as transport metadata.
4. Agent identity is bound server-side by the dispatcher to the frozen `agent_index` and its
   frozen persona/partition; every record stores `assigned_agent_id` + `agent_index`.
5. One JSON-repair retry with the frozen Round-3 `REPAIR_SUFFIX`; a call is valid only if it
   passes the adapted parser; no post-hoc imputation or filtering.

## 4. Model calls (frozen)

- Primary model `gpt-6-astra`; fallback order `gpt-5.6-sol`, then `gpt-5.5` (same relay).
  The chosen model is recorded per call (model identity), and `run_summary_*.json` records the
  actual model id(s).
- temperature 0.0, max_tokens 160, deterministic seed per frozen agent
  (`v10._agent_seed(agent_index)`), NO `reasoning_effort` field.
- Direct HTTP `POST /v1/chat/completions`, concurrent workers 10-16, content-addressed cache
  under `round6/large_model/cache/`, one automatic retry on transport failure inside the
  dispatcher (frozen retry policy: up to 2 HTTP attempts with backoff for 429/503/timeout;
  per-record attempt logs kept).
- Call counts: smoke 500; formal 2,500 (total unique 100 items x 25 = 2,500; smoke replayed
  from cache). Max items = 100 (hard cap).

## 5. Within-model gates (frozen; evaluated on the GPT model's own records)

Evaluate on the high-consensus (HC) subset, `agreement >= 0.8`, with pair-grouped bootstrap
(2,000 replicates, seed 20260913-family, reuse Round-3 `analysis_lib.py`), `RS_q = -BF_q`
as risk (higher = riskier):

- **G1 pipeline:** valid calls / formal calls >= 0.95; if < 0.95, execution-layer result
  (no substantive gate on a model-dependent valid subset), diagnose and report.
- **G2 primary AUROC:** `AUROC(RS_q, consensus_wrong | HC)` pair-grouped CI lower bound > 0.5
  (point estimate reported; point >= 0.60 reported as secondary).
- **G3 placebo:** per-agent paraphrase infidelity (flip) rate <= 0.30.
- **G4 permutation:** observed primary AUROC > 95th percentile of the pre-registered
  permutation distribution (per-question preserve/flip-swap, 1,000 permutations).
- **G5 mechanism fidelity:** on HC, wrong-group `bf_reverse` lower than correct-group
  `bf_reverse`; pair-grouped bootstrap CI for mean (correct - wrong) difference excludes 0.
- **Risk@80** (retain lowest-risk 80%) error-reduction CI reported alongside, not a gate.

All gates must pass for a PASS; otherwise FAIL with diagnosis. No post-hoc sign flip, no
silent cohort/metric repair, no test-set changes after outcomes.

## 6. Cross-model transfer (secondary, not a gate)

- Qwen frozen `RS_q` (Round-3 `preoutcome_features.jsonl`) and Ling frozen `RS_q`
  (Round-4 `ling_preoutcome_features.jsonl`), keyed by `item_id`/`cqid`, evaluated by
  pair-grouped AUROC against the GPT model's own `consensus_wrong` on the GPT HC subset.
- Reported separately; low item-level correlation does not invalidate within-model transfer.

## 7. Outcome firewall

Gold labels are merged **only after** the GPT model's records and label-free preoutcome
features are written and hashed. Forbidden score inputs before merge: gold label, gold binary,
correctness, `consensus_wrong`, and any outcome-derived selector. Labels are never sent to the
relay and never used to choose prompts, probes, adapters, or subsets.

## 8. Instability / failure handling (frozen)

- Consecutive 20 transport failures (503/429/timeout) -> stop immediately, write what exists
  as PARTIAL, no retry-until-complete.
- Relay unavailable for the chosen model -> try fallbacks in order; if all fail -> BLOCKED
  record (no fabricated numbers). Local Qwen3.6-35B fallback only if an already-running vLLM
  service is found (no new GPU start); otherwise BLOCKED.
- No filtered subset is ever presented as the full result; every summary reports actual
  call counts, parse yield, HTTP/retry stats, and token usage.

## 9. Outputs (all under `consensus_stress/round6/large_model/`)

preregistration.md (this file), cohort_first100_pairs.json, execution_notes.md,
run_summary_healthcheck.json, run_summary_smoke.json, run_summary_formal.json,
records.jsonl (raw responses kept local), analysis/large_model_*.md + JSON + figures,
SUMMARY.md (5-line Chinese summary). No git commit; no changes to frozen Round-3/4 artifacts.

## 10. Frozen input hashes (recorded at preregistration time)

- `consensus_stress/round3/selection_manifest.json`:
  `5f575ff873b3243b4916f77ab81269476da937d466eec967eff0934efe39089b`
- `consensus_stress/round3/paraphrase_manifest.json`:
  `5b322c4973328b5323edf8111a4e4195c4a4d895c9890dfb73a8d0f29d514435`
- `consensus_stress/round3/labels_ledger.json`:
  `770ede3f79b018c47aa982e6cb3f13b9d504b5c14950f7f1a8f6de196ffcbc5a`
- `consensus_stress/round3/records.jsonl`:
  `ce5280ede80c92f471ff73b1b8fe1c0fc339bd057aae67825e54f7d42a706a08`
- `consensus_stress/round3/preoutcome_features.jsonl`:
  `d0c588d05211769c14234377d669881d079dacaac0ebaf2ec9326561d967584d`
- `consensus_stress/round4/ling_records.jsonl`:
  `fc0e32126b3ce0a1c5394d11a706a072611a9fd12797b3624789cc0dda62d4d2`
- `consensus_stress/round4/ling_preoutcome_features.jsonl`:
  `35e853cf0815cb1428ec8f2ee671993bd1f87ba8b28ade24a630ac4c79bc26bb`
- `consensus_stress/round6/large_model/cohort_first100_pairs.json`:
  `69618101aa56f1f5a8b32cad26357c185547b65ac367c20f083aeaf3bad2c572`

Protocol frozen. No experimental call made at the moment this document is finalized.
