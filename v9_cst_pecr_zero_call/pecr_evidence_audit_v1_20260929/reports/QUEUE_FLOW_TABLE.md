# PECR queue-flow audit (read-only)

| Stage | Items | Source groups | Error | Correct | Unlabeled | /2,241 | /2,225 candidates |
|---|---:|---:|---:|---:|---:|---:|---:|
| manifest | 2241 | 453 | 1390 | 363 | 488 | 1.000 | 1.007 |
| mechanical_candidate | 2225 | 453 | 1379 | 361 | 485 | 0.993 | 1.000 |
| three_world_requests | 2225 | 453 | 1379 | 361 | 485 | 0.993 | 1.000 |
| json_complete | 2223 | 453 | 1378 | 360 | 485 | 0.992 | 0.999 |
| label_eligible | 1753 | 424 | 1390 | 363 | 0 | 0.782 | 0.788 |
| strict_analysis | 1735 | 424 | 1375 | 360 | 0 | 0.774 | 0.780 |

Interpretation: `1,735/1,735` is only the strict analysis table’s internal feature/OOF coverage. Relative to all 2,225 mechanical candidates, strict analysis coverage is 1,735/2,225 = 77.98%; relative to the 2,241 manifest it is 77.42%. JSON-complete means a parsed JSON object was recorded for all three worlds, not that numeric answer, unit, and confidence parsing succeeded.

Failure flags are overlapping. The 16 identity-break candidates are not assigned a mutually exclusive semantic category; they are mechanically excluded from the request queue, while parser, label, and request failures may co-occur.
