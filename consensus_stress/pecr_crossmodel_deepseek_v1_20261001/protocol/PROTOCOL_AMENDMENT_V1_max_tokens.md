# Protocol Amendment V1 — max_tokens 384 -> 2048 (2026-10-01, BEFORE full collection)

## Scope
Applies to: DeepSeek V4.1 Flash (`deepseek-flash`) cross-model PECR collection only.
Base protocol: `PRE_CALL_PLAN.md` v1 (frozen 2026-10-01, before any full-run call).

## Trigger (pre-flight smoke evidence)
A 3-request smoke run (`data/smoke/`, slots 1-3, item AMAT/2016/page_30.pdf-2) with the
frozen max_tokens=384 returned HTTP 200 on all requests, but `deepseek-flash` is a
reasoning model: `completion_tokens_details.reasoning_tokens` consumed the full
384-token budget on slots 1 and 3 (finish_reason=length, empty assistant content).
Only slot 2 produced parseable JSON. Continuing at 384 would have produced empty
content for the majority of the 6,675 requests.

## Amended parameter (single change)
- `max_tokens`: 384 -> **2048** for every request.
- Verification smoke (3 calls on the smoke slot-1 request body, max_tokens=2048):
  all returned finish_reason=stop with valid JSON content; reasoning_tokens ~520-570.
- Everything else unchanged: same manifest, same seed=20260928 item order,
  byte-identical system/user prompts, only the `model` field differs from the Qwen
  run; temperature=0; single attempt per (item, world); no retries/backfill;
  same append-only hash-chained ledger schema; same parsed_v2 parser; same label
  rule; same frozen Curve HGB features; same primary comparison
  (within-DeepSeek Curve HGB vs ordinary three-world HGB).

## Fairness note
max_tokens is an API transport budget, not a model-behavior parameter: Qwen3.5-4B
completions used <384 tokens, so raising the cap does not change any Qwen result.
For DeepSeek the cap must cover reasoning tokens plus the JSON answer; 2048 was
chosen as the smallest round value with wide margin (~3.5x observed usage).
The smoke responses at max_tokens=384 are kept under `data/smoke/` as evidence and
are NOT mixed into the full-run ledger (different request bodies).

## Forbidden (unchanged)
No feature/model/threshold selection on DeepSeek results; no touching the 565-item
holdout; no parser revision after collection; negative results reported in full.
