# PECR Cross-Model Test — DeepSeek V4.1 Flash — Pre-Call Plan (v1, 2026-10-01)

## 0. Status
- Draft frozen protocol. **Zero model calls made.** Execution requires: (a) a working
  DeepSeek endpoint + API key + exact model ID; (b) one explicit budget authorization.

## 1. Research question
Does the PECR bidirectional response-curve representation replicate on a different
model family? Specifically: on DeepSeek V4.1 flash responses, does audited Curve HGB
beat ordinary three-world HGB under the same items, same three calls per item, same
coverage rules — as it did on Qwen3.5-4B (ΔAUROC +0.0160, CI [+0.0041, +0.0269],
development split)?

This is a cross-model robustness / generality analysis on the FinQA dev_train
construction. It is NOT independent confirmation and does NOT touch the 565-item
holdout.

## 2. Frozen inputs (identical to Qwen collection)
- Manifest: `pecr_bidirectional_development_v1_20260928/data/construction_manifest_dev_train.jsonl`
  filtered to `bidirectional.construction_status == "valid_candidate"` → 2,225 items.
- Order: same shuffle, `seed=20260928` → identical item order as the Qwen full-dev run.
- Worlds per item: `original`, `positive`, `negative` (3 calls/item) → 6,675 requests.
- Prompts: byte-identical system + user templates from `run_full_dev_collection.py`;
  only the `model` field changes. Request bodies hashed (SHA-256) before sending.
- Sampling: `temperature=0`, `max_tokens=384`.
- Retry policy: single attempt per (item, world); transport/HTTP/parse failures are
  recorded in the ledger and never retried or backfilled.
- Ledger: append-only, hash-chained, identical schema to the Qwen run
  (`slot`, `attempt_id` prefixed `deepseek-full-`, `request_sha256`, `response_sha256`).

## 3. Frozen post-processing (fixed BEFORE seeing any DeepSeek response)
- Parser: the existing `parsed_v2` parser as-is. No parser revision after collection;
  if parse yield collapses for DeepSeek, that is reported as a result, not fixed.
- Label rule: `original_incorrect` derived from DeepSeek's original-world answer vs
  FinQA gold answer under the same normalization/comparison rule used for Qwen.
  Positive/negative world answers are NEVER compared to gold for features or labels.
- Feature extraction: frozen Curve HGB feature builder (audited v2). Features use only
  question/evidence structure + the three parsed responses.

## 4. Frozen evaluation (only primary comparison pre-committed)
- Primary: **within-DeepSeek** — Curve HGB vs ordinary three-world HGB, same source-group
  5-fold split as Qwen, ΔAUROC (error-positive) with source-group paired bootstrap CI
  (2,000 resamples), plus AUPRC, coverage, and class support.
- Secondary (descriptive): transfer — Qwen-trained frozen Curve HGB scored on DeepSeek
  features; graph-only and two-world HGB same-budget chain on DeepSeek.
- Forbidden: selecting features/models/thresholds on DeepSeek results; re-running with
  modified rules and still calling it the same analysis; touching the 565-item holdout;
  any Transformer candidate.

## 5. Budget
- 6,675 chat calls at temperature 0. Prompt ≈ 1.2–1.8k tokens, completion ≤384 tokens.
- Rough volume: ~9–12M input tokens, ~2.5M output tokens total. Cost depends on the
  provider's DeepSeek V4.1 flash pricing — to be confirmed with the working endpoint.

## 6. Access blocker found 2026-10-01
- `http://10.63.0.72:8317/v1` (config.toml `custom`/"deepseek" provider): stored key
  returns HTTP 401 `Invalid API key`; `/v1/models` unusable.
- openapi.center keys (…c4f14a, …bbf2ed): model lists contain only OpenAI-family
  models (gpt-5.2/5.3/5.4/5.5, image, audio) — **no DeepSeek models**.
- Needed from user: working DeepSeek V4.1 flash endpoint + key + exact model ID.

## 7. Deliverables after the run
Raw ledger + hashes, parse/label audit, feature table, OOF predictions, primary +
secondary results with CIs, coverage flow, cross-model comparison report vs Qwen,
claim–evidence update. Negative or null results are reported in full.
