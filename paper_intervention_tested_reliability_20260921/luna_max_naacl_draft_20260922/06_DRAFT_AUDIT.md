# Draft audit — Luna Max NAACL draft

- Source draft: `/home/gaoym/when-consensus-lies-astra6-credit-20260918/paper_intervention_tested_reliability_20260921/luna_max_naacl_draft_20260922/05_NAACL_FIRST_DRAFT_SEGMENTED.md`
- Cleaned draft: `/home/gaoym/when-consensus-lies-astra6-credit-20260918/paper_intervention_tested_reliability_20260921/luna_max_naacl_draft_20260922/06_NAACL_FIRST_DRAFT_CLEANED.md`
- Mechanical status: **PASS_MECHANICAL**
- Source chars: `55124`; cleaned chars: `54957`
- Citation placeholders remaining: **14**

## Structural repairs applied
- Removed the assembler wrapper title and retained one canonical title.
- Renumbered Experimental Protocol to Section 4 and Results to Section 5.
- Added consistent numbering for Related Work (6.x) and Discussion (7.x).
- Renumbered Limitations and Conclusion to Sections 8 and 9.
- Renamed the reproducibility section to Appendix A.

## Load-bearing value checks
- PASS `CST paper-scale AUROC` = `0.943` (occurrences: 4)
- PASS `CST 50-pair AUROC` = `0.912` (occurrences: 4)
- PASS `CST direction contrast` = `+0.44` (occurrences: 4)
- PASS `S&P B6` = `0.6320` (occurrences: 4)
- PASS `S&P B8` = `0.6177` (occurrences: 4)
- PASS `S&P paired delta` = `-0.0143` (occurrences: 4)
- PASS `FinQA Qwen full CEF` = `0.9008` (occurrences: 4)
- PASS `FinQA Qwen S2` = `0.8317` (occurrences: 4)
- PASS `FinQA Ling full CEF` = `0.8477` (occurrences: 4)
- PASS `FinQA Ling S2` = `0.8379` (occurrences: 4)
- PASS `ConvFinQA Qwen S2` = `0.6508` (occurrences: 8)
- PASS `ConvFinQA Qwen full CEF` = `0.6870` (occurrences: 4)
- PASS `missing head -2` = `0.8754` (occurrences: 4)
- PASS `missing head +2` = `0.8407` (occurrences: 4)
- PASS `imputed score` = `0.7474` (occurrences: 6)
- PASS `imputed delta` = `+0.0966` (occurrences: 4)
- PASS `imputed item CI lower` = `+0.0183` (occurrences: 4)
- PASS `imputed item CI upper` = `+0.1740` (occurrences: 4)
- PASS `Ling zero-shot score` = `0.8536` (occurrences: 2)
- PASS `Ling zero-shot delta` = `+0.0262` (occurrences: 2)
- PASS `Ling transfer CI lower` = `-0.0539` (occurrences: 2)
- PASS `Ling transfer CI upper` = `+0.1436` (occurrences: 2)

## Claim-boundary checks
- PASS: no unqualified forbidden-positive claim pattern detected.
- PASS: no duplicate legacy section numbering detected.

## Citation work remaining
- `[CITATION NEEDED]` placeholders are intentionally retained; bibliography insertion still requires a dated related-work/source audit.
- This audit does not invent references or convert placeholders into citations.

## Scope note
- This is a deterministic local cleanup and consistency audit; it does not change experimental records, frozen contracts, or result values.
