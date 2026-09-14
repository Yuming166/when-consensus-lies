# Execution Notes — Round 6 Agent D (Large-Model Single-Point Validation)

Protocol: `cs-paper-gpt-singlepoint-20260914-round6` (frozen in `preregistration.md`,
SHA256 `e4552e2407b81894f1aae5628ff536fa0073a966296e0509a8a836e19f10840e`).

## Capability gate (17:42-17:46 +08:00)
- The launch wrapper `round6/run_agent.sh` probe failed because the tmux windows were
  created before `tmux setenv` exported `OPENAPI_CENTER_API_KEY` (probe ran key-less).
  Fallback to server default happened in the wrapper, but Agent D re-probed the relay
  directly per the D instruction (key loaded in-memory from allowed sources only).
- `GET /v1/models` -> 200; `gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.5` all present.
- `gpt-6-astra` minimal chat (temperature 0, max_tokens 16): 3/3 consecutive successes
  (status 200, model=gpt-6-astra, ~12-15s each). See `run_summary_healthcheck.json`.
- No key value was written to any file, log, git, memory, or output.

## Preregistration (17:48 +08:00)
- `preregistration.md` frozen; cohort `cohort_first100_pairs.json` frozen
  (100 pairs / 200 items; smoke=first 20 items; formal=first 100 items).
- Frozen-input hashes recorded in preregistration (Section 10).

## Smoke (started 17:52 +08:00)
- 20 items x 5 agents x 5 conditions = 500 calls, 13 workers, model gpt-6-astra.
- First item (25 calls) ran sequentially as an end-to-end validation: 25/25 valid,
  first-pass 25/25, HTTP 200 x25, 0 retries.
- Smoke run in progress; progress logged to `smoke_run.log`; summary ->
  `run_summary_smoke.json`, records -> `records_smoke.jsonl`.

(To be continued after smoke + formal run.)

## Smoke (completed 19:03 +08:00)
- 20 items x 25 = 500 logical calls; final replay valid **500/500 (1.000)**, first-pass 1.000.
- Smoke gate (pipeline valid >= 0.95) **PASS**; no contract adaptation needed (0 parse errors).
- HTTP statuses on the smoke re-run: 200 x 15 new + 429 x 1 (retried to success), 485 cache hits
  (mirror-equivalent views of the 10 pairs). See `run_summary_smoke.json`.

## Formal run (completed ~20:39 +08:00)
- 100 items x 5 agents x 5 conditions = 2,500 logical calls; **2,483 valid (0.9932 >= 0.95, G1 PASS)**;
  first-pass rate 0.9472; 0 parse failures.
- HTTP stats (all internal attempts): 200 x 1511, 429 x 826, 502 x 115, 400 x 125
  ("Upstream request failed" from the relay); transport retries 929; cache hits 1,472;
  elapsed 5,521 s (~92 min).
- 17/2,500 records failed on transport only (429/502/400); no filter was applied to the 2,483
  valid records for pipeline reporting (valid rate computed on ALL 2,500 calls).
- Model identity: `gpt-6-astra` in all 2,483 successful records; the 17 failed records have no decision.
- Logical token usage (incl. cache replays): 5,534,850 prompt / 171,187 completion tokens.

## Features & metrics (outcome firewall honored)
- Label-free preoutcome features: 98/100 items (2 items excluded by the Round-3 rule "all 5
  original answers required" because their `original` calls failed on transport; NOT outcome-driven).
- Feature file SHA256 `f1d167aad462da7dc2af8efae593685f386e3b434e8d36af79361b7989204e03` frozen,
  then labels merged from `round3/labels_ledger.json`.
- Within-model HC n=96, wrong=8 (8.3%); AUROC(RS_q, wrong|HC)=0.969 [0.935, 0.995];
  Risk@80 reduction=1.000 [0.836, 1.000]; placebo 0.0394; permutation obs 0.969 > p95 0.894;
  mechanism correct-wrong bf_reverse diff=0.832 [0.745, 0.928]. All five gates PASS.
- Transfer (secondary): Qwen RS_q -> gpt wrong|HC AUROC 0.838 [0.693, 0.950];
  Ling RS_q -> 0.737 [0.568, 0.862]; Spearman(src, gpt RS_q): Qwen 0.679, Ling 0.366.

## Final status
- **No BLOCKED, no PARTIAL.** Relay stayed up; no 20-consecutive-failure abort triggered.
- Key never written to disk/log/git/memory/output; loaded in-memory from env/private config only.
- No git commit performed.

## Independent verification
- Manual AUROC(RS_q, wrong|HC)=0.9695 matches analysis_lib (0.9695); correct/wrong mean
  bf_reverse 0.9068/0.075 (diff 0.8318); placebo 0.0394; Qwen transfer 0.8381 — all re-confirmed.
- No secret material found in any file (only header-construction code in the runner); key in-memory only.
- No git commit; worktree unchanged except round6/ + registry status.
