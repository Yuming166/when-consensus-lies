# Completed coverage with target-native DeepSeek track

| Cohort | Frame | Requested | Strict | Groups | Error / correct | Requested outside strict |
|---|---:|---:|---:|---:|---:|---:|
| qwen_generation_aligned | 2241 | 2225 | 2142 | 452 | 1699 / 443 | 83 |
| deepseek_shared_qwen | 2241 | 2225 | 2050 | 448 | 1257 / 793 | 175 |
| deepseek_generation_aligned | 2241 | 2225 | 2050 | 448 | 1257 / 793 | 175 |

Each cohort has 2,241 rows, including 2,225 requested and 16 unrequested construction exclusions. DeepSeek target-native strict support is unchanged: 2,050 rows / 448 groups; 175 requested exclusions are 54 valid unknown-label, 79 invalid known-label and 42 invalid unknown-label rows. Native G96 exists only for those 2,050 strict rows. All 191 other rows explicitly say not_computed; shared Qwen G is never substituted.

attempted_frame_final.jsonl / .csv is the final three-cohort coverage view; the original two-cohort attempted_frame exports remain the as-before audit. Unrequested offline_parser_valid is null in the completed view. The upstream exclusion eligibility flag is preserved separately; recorded statuses remain unknown.

All six native methods are now available as saved post-hoc fixed-method results. The old report stating four methods missing describes availability before the authorized supplement and is retained.
