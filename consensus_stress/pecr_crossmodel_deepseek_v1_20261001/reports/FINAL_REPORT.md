# DeepSeek V4.1 Flash cross-model PECR test — final report (v1)

**Date:** 2026-10-01
**Status:** Collection complete, but the API credit expired during the run. The pre-specified within-DeepSeek primary comparison is available on the frozen strict-analysis subset; this is a **quota-truncated, non-random 53.6% coverage cross-model robustness analysis**, not an independent confirmation and not the 565-item holdout.

## 1. Research question and protocol

The frozen question was whether audited three-world Curve HGB outperforms ordinary three-world HGB on **the same DeepSeek responses**, with the same item set, same three calls per item, same parser/coverage rules, and source-group cross-validation. The protocol used the FinQA `dev_train` construction, seed 20260928 item order, byte-identical prompts, temperature 0, and no retry/backfill.

Two protocol amendments were written before the full run:

1. `max_tokens` was increased to accommodate DeepSeek reasoning tokens.
2. The final full run used `max_tokens=8192` and `reasoning_effort="low"`. Low effort was fixed uniformly as the closest non-reasoning setting to the Qwen condition; no full-run response was used to choose it.

No post-collection parser, feature, threshold, or model selection was performed.

## 2. Request accounting and quota interruption

| Quantity | Count |
|---|---:|
| Requested construction candidates | 2,225 |
| Requested slots | 6,675 |
| HTTP 200 | 3,993 |
| HTTP 429 | 705 |
| HTTP 402 | 1,977 |
| HTTP 200 with valid top-level response JSON | 3,946 |
| HTTP 200 with invalid/empty assistant JSON | 47 |

The failures began at slot 1551. HTTP 429 and 402 responses were interleaved in the concurrent queue; 402 was the terminal credit condition. The frozen no-retry rule records these failures rather than replacing them.

Item-level coverage was:

| Flow | Items | Source groups |
|---|---:|---:|
| Attempted candidates | 2,225 | 453 |
| All three worlds returned HTTP 200 | 1,285 | 405 |
| All three worlds had top-level JSON | 1,248 | 400 |
| Original world had a known correctness label | 1,276 | — |
| Passed strict numeric/unit/confidence parser and had all three responses + label | **1,192** | **395** |

The strict set therefore covers **1,192/2,225 (53.57%)** of attempted items, not the full candidate cohort. Its support is 743 error and 449 correct original answers. Exclusions overlap: API failure, response invalidity, and original-answer unlabeled status are recorded as separate non-exclusive markers. The full flow and token totals are in `COVERAGE_FLOW_DEEPSEEK.json`.

Recorded token usage for all returned calls was 4,250,894 prompt and 4,804,583 completion tokens (9,055,477 total). Billing must be checked against the provider account; these are model-reported usage only.

## 3. Primary within-DeepSeek result

All metrics use `original_incorrect=1`, five source-group folds, identical strict items, and source-group bootstrap intervals (B=2,000, seed 20260928).

| Method | AUROC | AUPRC |
|---|---:|---:|
| Graph only | 0.7211 | 0.7896 |
| Two-world HGB | 0.7809 | 0.8178 |
| Ordinary three-world HGB | 0.8015 | 0.8293 |
| **Three-world Curve HGB** | **0.8153** | **0.8445** |

Pre-specified paired AUROC differences:

| Comparison | Delta AUROC | Source-group 95% CI |
|---|---:|---|
| **Curve HGB − ordinary three-world HGB** | **+0.0138** | **[+0.0016, +0.0255]** |
| Ordinary three-world HGB − graph only | +0.0804 | [+0.0568, +0.1049] |
| Two-world HGB − ordinary three-world HGB | −0.0206 | [−0.0322, −0.0095] |

Thus the primary within-DeepSeek comparison remained positive with its bootstrap interval above zero **on the available strict subset**. The result supports cross-model usefulness of the bidirectional response representation, but missingness was caused by quota/rate failures and is not plausibly completely random. It must not be described as complete FinQA replication or independent confirmation.

## 4. Qwen reference

The audited Qwen development result used 1,735 strict items (1,375 error / 360 correct; 424 source groups):

| Model family | Ordinary three-world | Curve HGB | Curve − ordinary three-world |
|---|---:|---:|---|
| Qwen3.5-4B | 0.7978 | 0.8138 | +0.0160 [+0.0041, +0.0269] |
| DeepSeek V4.1 Flash | 0.8015 | 0.8153 | +0.0138 [+0.0016, +0.0255] |

The cohorts have different sample sizes and label balances, so the AUROC levels are not directly causally comparable. The comparable design element is the same-budget paired method contrast within each family.

## 5. Secondary transfer analysis

Descriptive one-direction transfers, without new model selection:

| Training responses | Evaluation responses | Curve AUROC | 95% CI | AUPRC |
|---|---|---:|---|---:|
| Qwen | DeepSeek | 0.7418 | [0.7094, 0.7714] | 0.7781 |
| DeepSeek | Qwen | 0.8075 | [0.7814, 0.8341] | 0.9303 |

The DeepSeek-trained model transferred close to its Qwen development level; the Qwen-trained model dropped on DeepSeek. These are secondary descriptive results and should not replace the within-model primary comparison.

## 6. Integrity checks

- Ledger contains 6,675 records with no missing slots.
- The record hash chain recomputes with zero errors; head is `5bec6a0d4f08c264c062bf69adbcb62160e1cda8f84ca8988de56d967c0d994d`.
- Every HTTP-200 response reports model `deepseek-flash`.
- Ledger request bodies are authoritative: each records `max_tokens=8192` and `reasoning_effort="low"`. The collection script docstring still contains the obsolete `384` wording, but it does not control constants and is retained unchanged for provenance.
- The frozen parser checks numeric answers, bounded confidence, units, and all three worlds.
- Audited array-independence, negative-world invariance for two-world features, named feature dimensions, and curve-feature preservation tests passed.
- No failed slot was retried or backfilled; no 565-item holdout data were read.

## 7. Claim boundaries

**Supported:** Under the frozen protocol and available 1,192-item subset, DeepSeek V4.1 Flash also shows a positive within-model paired gain for Curve HGB over ordinary three-world HGB, with source-group bootstrap CI above zero. This supports cross-model robustness of the response-curve signal beyond Qwen.

**Not supported:** independent holdout confirmation; complete 2,225-item DeepSeek coverage; claims that transfer is symmetrically strong; claims about unseen groups or the 565-item two-world holdout; claims that low-effort DeepSeek exactly equals Qwen model behavior. The prompt and scoring pipeline are program-conditioned because FinQA programs guide construction/expected direction; this is not an end-to-end oracle-free method.

## 8. Decision

Use this result as a **quota-truncated cross-model robustness analysis**. A complete confirmation would require a versioned second pass under an explicit amendment after account top-up, preserving V1 as the failed-budget run and pre-specifying which missing slots are eligible—without treating the current positive subset as the final complete cohort.
