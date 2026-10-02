# Full attempted coverage and unit/parse boundary

| Cohort | Frame | Requested | Strict | Error/correct | Groups | Requested outside strict |
|---|---:|---:|---:|---:|---:|---:|
| qwen_generation_aligned | 2241 | 2225 | 2142 | 1699/443 | 452 | 83 |
| deepseek_shared_qwen | 2241 | 2225 | 2050 | 1257/793 | 448 | 175 |

| Mutually exclusive partition | Qwen corrected | DeepSeek shared G |
|---|---:|---:|
| strict_parsed_labeled | 2142 | 2050 |
| valid_unknown_label | 52 | 54 |
| invalid_known_label | 7 | 79 |
| invalid_unknown_label | 24 | 42 |
| unrequested_construction_exclusion | 16 | 16 |

Partitions sum to2241. Qwen requested outside strict is83=52+7+24; DeepSeek outside strict is175=54+79+42.
A strict parser does not imply compatible units. Unit strings are normalized by the historical strip/lower/percent replacements only, with no conversion.
Each cohort has all2241 rows in attempted_frame exports, including per-world recorded status, offline parser status, unit state, label missingness, source hashes and G origin.
Unknown recorded status is never upgraded to success. Unrequested records retain unknown parser state.

## Per-world offline parsing
qwen_generation_aligned / original: {"answer_not_numeric": 26, "unknown_unrequested": 16, "valid": 2199}
qwen_generation_aligned / positive: {"answer_not_numeric": 22, "missing_json": 1, "unknown_unrequested": 16, "valid": 2202}
qwen_generation_aligned / negative: {"answer_not_numeric": 22, "missing_json": 1, "unknown_unrequested": 16, "valid": 2202}
deepseek_shared_qwen / original: {"answer_not_numeric": 35, "missing_json": 8, "ok": 2182, "unknown": 16}
deepseek_shared_qwen / positive: {"answer_not_numeric": 34, "missing_json": 39, "ok": 2152, "unknown": 16}
deepseek_shared_qwen / negative: {"answer_not_numeric": 31, "missing_json": 40, "ok": 2154, "unknown": 16}

## Strict unit combinations
qwen_generation_aligned: {"empty_mismatch": 103, "empty_same": 153, "nonempty_mismatch": 111, "nonempty_same": 1775}
deepseek_shared_qwen: {"empty_mismatch": 102, "empty_same": 51, "nonempty_mismatch": 279, "nonempty_same": 1618}
