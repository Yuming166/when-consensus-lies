# Protocol Amendment V3 — post-top-up backfill (2026-10-01)

## Motivation and authorization

The V1 run hit provider quota exhaustion. V1 remains immutable. After the user reported
that the DeepSeek account was topped up, this versioned amendment authorizes exactly one
backfill attempt for V1 slots that terminated in HTTP 429 or HTTP 402.

## Eligibility

Eligibility is computed only from the immutable V1 hash-chained ledger and is limited to:

- V1 `http_status == 429`; or
- V1 `http_status == 402`.

The expected eligible count is 2,682 slots. V1 HTTP-200 slots, including the 47
HTTP-200 slots whose assistant JSON was invalid, are **not** eligible. This avoids
response-conditioned selective retries. Driver/transport errors are absent in V1.

## Request and collection policy

- Same manifest, same seed-20260928 slot order, same three worlds, same prompts, same
  model `deepseek-flash`, same `temperature=0`, same `max_tokens=8192`, and same
  `reasoning_effort="low"` as the V1 amended run.
- Exactly one new attempt per eligible slot.
- Workers are reduced from 16 to 12 because V1's provider error showed a balance-based
  concurrency ceiling near 12. This is a transport setting only.
- No other retries, no backfill beyond this list, no API-side correction, and no use of
  correctness labels or analysis scores to select slots.

## Assembly and analysis

A V2 merged ledger selects the immutable V1 record for every V1 HTTP-200 slot and the
new V2 record for every eligible slot. The two source ledgers are retained separately.
Labels are regenerated from the merged original-world responses using the same frozen
numeric tolerance rule. Parsing, strict coverage, features, model parameters, folds,
primary comparison, and bootstrap remain the audited V2 feature/analysis implementation.
The primary comparison remains Curve HGB minus ordinary three-world HGB on the same
strict merged cohort.

This run is a post-quota amendment, not the originally specified single-attempt V1
protocol. It can support a complete-attempt cross-model robustness analysis, but cannot
erase the fact that V1 was interrupted.

## Forbidden

No 565-item holdout; no feature/model/threshold selection on the merged DeepSeek
responses; no selective re-parsing or replacement of HTTP-200 invalid assistant outputs;
no deletion or overwrite of V1.
