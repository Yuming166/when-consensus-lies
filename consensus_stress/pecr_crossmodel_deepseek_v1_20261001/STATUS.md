# Status: 2026-10-01

- DeepSeek V4.1 Flash collection reached all 6,675 slots. API credit was exhausted during the concurrent run: 3,993 HTTP 200, 705 HTTP 429, and 1,977 HTTP 402.
- Frozen no-retry policy preserved failures; no missing slot was backfilled.
- Strict analysis contains 1,192 items from 395 source groups (53.6% coverage).
- Pre-specified Curve HGB minus ordinary three-world HGB AUROC gain: +0.0138, 95% CI [+0.0016, +0.0255].
- Final report: `reports/FINAL_REPORT.md`; coverage details: `reports/COVERAGE_FLOW_DEEPSEEK.json`.
- This is cross-model robustness evidence on a quota-truncated subset, not independent confirmation.
