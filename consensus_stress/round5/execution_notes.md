# Round 5 execution notes

- Preregistration was frozen and hashed before any Round-5 call:
  `0a465509c807e1b0d81ccb86585721bede36c57cb51832519219ff93bbd714bb`.
- Endpoints: Qwen3.5-4B at `127.0.0.1:31518`; Ling-3.0-tiny at `127.0.0.1:31520`.
  No `reasoning_effort` field was sent. The embedding endpoint was not used because the
  pre-registered SelfCheckGPT variant was answer-match.
- A 50-call preflight was run for each model after preregistration. The full run reused those
  cache entries, so the unique call footprint remained exactly 30,000 calls per model.
- Qwen full run: 30,000/30,000 records, 29,987 valid (99.9567%), elapsed 1,311.89 s.
  Invalid calls were retained as missing responses; no repair call was made.
- Ling full run: 30,000/30,000 records, 30,000 valid (100.0%), elapsed 2,314.31 s.
- Total unique Round-5 research-model calls: 60,000; valid 59,987 (99.9783%).
- Total reported API token usage: Qwen 12,509,692 total tokens; Ling 12,688,129 total tokens.
- Label-blind external scores were written and hashed before `analyze_leaderboard.py` merged
  gold labels. Isotonic and temperature calibration were then computed only with pre-specified
  pair-grouped five-fold OOF fits.
- No new GPU process was launched or restarted. The existing Qwen service is hosted on GPU4 and
  the existing Ling service on GPU5; GPU6 was not called. This note records the pre-existing
  service placement required by the requested endpoints.
- Two implementation-only bugs were fixed after preregistration and before final analysis:
  a default file-path substitution bug in `build_baseline_scores.py`, and a relative-path bug
  when writing `frozen/SHA256SUMS`. Neither changed the cohort, prompt, sampling parameters,
  baseline formulas, calibration folds, metrics, gates, or any model call.
- No git commit or push was performed; `docs/` and Round-3/Round-4 frozen code were not modified.
