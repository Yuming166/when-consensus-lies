# Protocol Amendment V2 — reasoning_effort="low", max_tokens 2048 -> 8192 (2026-10-01, BEFORE full collection)

## Trigger (smoke2 evidence, 15 requests, max_tokens=2048)
`data/smoke2/`: 15/15 HTTP 200 but only 6/15 produced content. Truncated slots burned
the full 2048 budget on reasoning (observed reasoning_content up to ~10.7k chars,
still incomplete). max_tokens alone cannot fix this within a sane budget: on the
hardest smoke item, default effort still truncated at 8192 tokens (35s, empty content).

## Amended parameters (final, applied uniformly to every request)
- `reasoning_effort`: **"low"**  (model card lists effort levels low/high/max, default high)
- `max_tokens`: **8192** (safety margin; hardest smoke item used 2,310 total completion
  tokens at low effort, finish=stop, valid JSON, 9s)
- Verification: on the hardest smoke item (slot 10 request body), low effort yielded
  valid JSON (finish=stop); `effort="low"` also worked but cost 4,811 tokens / 20s;
  default effort truncated even at 8192.

## Fairness note
Qwen3.5-4B is a non-reasoning model at temperature 0; running deepseek-flash at
default (high) reasoning effort would conflate "model family" with "reasoning budget".
Low effort is the closest DeepSeek setting to the Qwen condition, is applied uniformly,
and is frozen before any full-run response is seen. All other protocol elements are
unchanged from PRE_CALL_PLAN.md v1 + Amendment V1 (parser, label rule, features,
primary comparison, no retries/backfill, same ledger schema).

## Supersedes
Amendment V1's max_tokens=2048 is superseded by max_tokens=8192. smoke/smoke2
responses are evidence only and never enter the full-run ledger.
