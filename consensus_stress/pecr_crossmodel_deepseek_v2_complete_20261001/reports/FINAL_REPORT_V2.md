# DeepSeek V4.1 Flash cross-model PECR test — complete-attempt V2 report

**Date:** 2026-10-01  
**Status:** post-top-up complete attempt; primary analysis complete.

## 1. What changed in V2

V1 preserved the original no-retry rule after API credit exhaustion. V2 was preregistered before any new model output and only retried the **2,682 V1 slots with HTTP 429 or 402**. It did not retry V1 HTTP-200 slots, including the **47 V1 HTTP-200 slots with invalid assistant JSON**. V1 remains immutable; the merged ledger links V1 HTTP-200 records to one V2 response for each formerly failed slot.

- V1 HTTP-200 records preserved: **3,993**
- V2 backfilled records: **2,682**
- V2 HTTP-429 / HTTP-402 / other errors: **0 / 0 / 0**
- Full-runner V2 requests: **2,681**; the one remaining eligible slot used the pre-runner HTTP-200 smoke response, as frozen
- Merged records: **6,675/6,675 HTTP 200**
- Merged hash-chain errors: **0**; hash-chain head `f767ae1294b7c33cfad909a23d445db41899d75f16d32b088c255dd39d0d47ef`; ledger-file SHA-256 begins `78c9aa03f012bfbf`

The ledger uses the frozen prompt, `deepseek-flash`, temperature 0, `max_tokens=8192`, and `reasoning_effort=low` for all requests. All returned records report model `deepseek-flash`.

## 2. Cohort flow

| Flow | Items | Source groups |
|---|---:|---:|
| Requested construction cohort | 2225 | 453 |
| All three worlds HTTP 200 and reported DeepSeek | 2225 | — |
| All three assistant JSON objects present | 2150 | — |
| All three pass strict numeric/confidence response parsing | 2104 | — |
| Original-world correctness label known | 2129 | — |
| **Strict analysis cohort** | **2050** | **448** |

The strict cohort covers **2050/2225 (92.13%)** of requested items and **448/453 (98.90%)** of requested source groups. Class support is **1257 original-error** and **793 original-correct** items.

The 47 V1 invalid-assistant slots were intentionally not retried. Across the merged attempt, **87 HTTP-200 records** ended with `finish_reason=length` and no valid assistant JSON; the merged strict cohort also excludes nonnumeric or out-of-range responses. The non-exclusive failure markers and item-level parse patterns are in `COVERAGE_FLOW_DEEPSEEK_V2.json`.

Mutually exclusive endpoint statuses are:

| Endpoint status | Items |
|---|---:|
| Strict valid response + known label | 2050 |
| Invalid response + known label | 79 |
| Valid response + unknown label | 54 |
| Invalid response + unknown label | 42 |

## 3. Primary within-DeepSeek result

All methods use the same strict items, the same original/positive/negative DeepSeek responses, `original_incorrect=1` as the positive class, five source-group outer folds, and source-group bootstrap intervals (B=2,000, seed 20260928).

| Method | AUROC | AUPRC |
|---|---:|---:|
| Graph only | 0.7672 | 0.8186 |
| Two-world HGB | 0.8139 | 0.8418 |
| Ordinary three-world HGB | 0.8259 | 0.8485 |
| **Three-world Curve HGB** | **0.8412** | **0.8653** |

| Pre-specified paired contrast | Δ AUROC | Source-group 95% CI |
|---|---:|---:|
| **Curve HGB − ordinary three-world HGB** | **+0.0153** | **[+0.0070, +0.0235]** |
| Ordinary three-world HGB − graph only | +0.0587 | [+0.0405, +0.0772] |

The primary interval is above zero. All implementation checks passed: independent arrays, two-world negative-world invariance, named dimensions, and preservation of curve features.

## 4. Cross-model context and transfer

| Response family / cohort | Ordinary three-world | Curve HGB | Paired Curve gain |
|---|---:|---:|---:|
| Qwen3.5-4B, 1,735-item dev result | 0.7978 | 0.8138 | +0.0160 [+0.0041, +0.0269] |
| DeepSeek V4.1 Flash, 2,050-item complete attempt | 0.8259 | 0.8412 | +0.0153 [+0.0070, +0.0235] |

Fixed one-direction transfers are secondary and descriptive:

| Train → evaluate | Curve AUROC | 95% CI | AUPRC |
|---|---:|---:|---:|
| Qwen → DeepSeek | 0.7559 | [0.7322, 0.7808] | 0.7772 |
| DeepSeek → Qwen | 0.8146 | [0.7890, 0.8398] | 0.9313 |

The two cohorts differ in size and label balance, so AUROC levels are not a direct model-ranking comparison. Transfer intervals are marginal, not paired method contrasts.

## 5. Token accounting

| Attempt | Prompt tokens | Completion tokens | Total tokens |
|---|---:|---:|---:|
| V1 original run | 4,250,894 | 4,804,583 | 9,055,477 |
| V2 backfill | 2,835,472 | 3,387,588 | 6,223,060 |
| Merged complete attempt | 7,086,366 | 8,192,171 | 15,278,537 |

These are model-reported usage fields, not a provider invoice.

## 6. Supported and unsupported claims

**Supported:** On the complete-attempt strict cohort, Curve HGB gives a paired AUROC gain over same-budget ordinary three-world HGB with a source-group bootstrap CI above zero. The qualitative direction reproduces the Qwen development result.

**Also supported:** the pipeline returned a response for every requested slot, preserved V1, followed the frozen retry eligibility rule, and used the same frozen parser/features/statistics without response-conditioned parser changes.

**Not supported:** independent holdout confirmation; freedom from FinQA dev_train selection exposure; complete parsing (87 invalid assistant JSON records remain); symmetric transfer; claims about the separate 565-item holdout; or a claim that V2 independently replicates V1. The construction is program-conditioned, not oracle-free.

## 7. Recommended wording

“On a post-top-up complete DeepSeek V4.1 Flash attempt of the 2,225-item FinQA dev_train construction, 2050 items passed the strict three-world parser and label requirements. With identical items and three calls per item, Curve HGB improved error-ranking AUROC over ordinary three-world HGB by +0.0153 (source-group 95% CI +0.0070 to +0.0235). This is a cross-model robustness analysis within the development dataset, not an independent confirmation.”
