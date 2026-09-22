# v0.10 analyzer repair audit

- Status: **POST_HOC_IMPLEMENTATION_AUDIT_PASS**
- Date: **2026-09-22**
- Contract: `finqa_convfinqa/24_pecr_v0_10_missing_probe_imputation_20260922/PECR_V0_10_FROZEN_CONTRACT.json`
- Contract SHA-256: `85bd5d32bb88c4be6f0af37bc8d9fe94299093a72338348370523335d3a82207`

## What was repaired

The frozen v0.10 contract already declared a 43-feature `all_response_rich` family containing `original_confidence` and `original_confidence_valid`. The first offline analyzer execution failed with `KeyError: original_confidence` because the implementation had not materialized those two declared fields in each feature row. The repair only completed the feature row and rewrote the direction-sign calculation explicitly; it did not change the contract, add or remove a feature family, or issue model calls.

- Declared primary feature count: `43`
- Computed feature count: `43`
- Contract hash matches computed feature-list hash: **True**
- Forbidden outcome-derived feature names: `[]`
- Confidence-validity derivation audit: **PASS**
- Additional model calls caused by repair: **0**

The repair was mechanically determinable from the frozen contract and raw confidence fields before any result-dependent choice. `original_correct` was not used as a feature, training target, or selection signal.

## Fixed primary result

The reported 43-feature primary result remains:

- student AUROC: `0.747400`
- S2 AUROC: `0.650825`
- full CEF AUROC: `0.686962`
- student minus S2: `0.096575`
- item-bootstrap 95% CI: `[0.018271, 0.173972]`
- head AUROCs: `-2=0.875410`, `+2=0.840694`

## Omission sensitivity (post-hoc only)

As an audit, the same frozen GBDT settings were refit after omitting the two declared original-confidence features. This is not a replacement result and was not used for selection:

- 41-feature student AUROC: `0.748117`
- 41-feature student minus S2: `0.097292`
- 41-feature item-bootstrap 95% CI: `[0.018843, 0.174122]`

The primary claim is therefore not dependent on a hidden post-hoc feature addition; the repaired analysis conforms to the pre-existing 43-feature contract, and the 41-feature omission gives a nearly identical sensitivity result.

## Claim boundary

This audit supports an implementation-integrity statement only. It does not authorize retuning, change the frozen result, or establish a new performance claim.
