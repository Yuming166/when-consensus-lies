# PECR DEV eligibility and attrition audit

Audit date: 2026-09-21. This package is offline-only; model calls: 0.

## Bottom line

> PECR is evaluated on a structurally identifiable, source-deduplicated subset of FinQA DEV, not on all 883 official DEV rows.

The selection is output-blind and uses the frozen PECR construction functions. The audit compares the official DEV population, the 182 eligible rows, and the 126 one-per-source-file rows without using model outputs.

## Attrition

| stage | n | share of official DEV | rule |
|---|---:|---:|---|
| official_DEV | 883 | 1.000 | all official DEV rows |
| structurally_eligible | 182 | 0.206 | exact frozen PECR builder: executable program, unique operand mapping, deterministic valid worlds, invariant controls, and bounded numeric transformations |
| one_item_per_source_file | 126 | 0.143 | all eligible source groups, stable SHA-256 ranking; output-blind |

- 883 official DEV rows → 182 structurally eligible rows.
- 182 eligible rows → 126 source groups / selected items.
- 56 eligible rows are not selected because their source file already has another eligible candidate.
- The final 126 items are one per source file; this is deterministic source deduplication, not outcome or model-based filtering.

## Eligibility rejection counts

| frozen reason | count |
|---|---:|
| `count_like_value_not_integer` | 55 |
| `original_execution:primary:InvalidOperation:[<class 'decimal.ConversionSyntax'>]` | 3 |
| `original_extreme_intermediate` | 8 |
| `original_program_gold_mismatch` | 126 |
| `relevant_count_like_value_not_integer` | 3 |
| `relevant_near_zero_divisor_k_-2` | 1 |
| `surface_generation:ValueError:surface_quantization_erased_change` | 3 |
| `unique_operand_count:0` | 78 |
| `unique_operand_count:2` | 353 |
| `unique_operand_count:3` | 17 |
| `unique_operand_count:4` | 6 |
| `unique_operand_count:5` | 2 |
| `unsupported_program_ops` | 46 |

## Structural comparison

The JSON artifact contains full row-level features and categorical distributions. The principal audit dimensions are program length/operator family, question/model-input/context length, numeric-token density, table/text shape, report year, company, and source-file multiplicity.

| cohort | n | companies | source files | mean program length | median model-input chars | median report year |
|---|---:|---:|---:|---:|---:|---:|
| all official DEV | 883 | 97 | 299 | 1.54 | 521 | 2012 |
| ineligible | 701 | 94 | 284 | 1.51 | 520 | 2012 |
| eligible before dedup | 182 | 60 | 126 | 1.68 | 528 | 2012 |
| selected 126 | 126 | 60 | 126 | 1.70 | 504 | 2012 |
| eligible not selected | 56 | 29 | 47 | 1.62 | 570 | 2012 |

## Interpretation boundary

The audit does not attempt to prove that the 126-item cohort is representative. It makes the coverage boundary explicit and exposes the structural differences that a reviewer should see. Any main-paper claim must say `eligible, source-deduplicated FinQA DEV cohort` rather than `FinQA DEV` without qualification.

## Reproducibility

- Re-run: `python prepaper_audit/build_prepaper_audit.py`.
- Official DEV SHA-256: `a847fb7e0d61a3125a1e2909852df6b89f1ee64d2c5ff1bf689e332214deee51`.
- Exact construction implementation: `finqa_convfinqa/13_pecr_v0_2_repaired/pecr_v02_core.py` and `finqa_convfinqa/22_pecr_v0_8_official_dev_one_shot_20260921/prepare_official_dev.py`.
