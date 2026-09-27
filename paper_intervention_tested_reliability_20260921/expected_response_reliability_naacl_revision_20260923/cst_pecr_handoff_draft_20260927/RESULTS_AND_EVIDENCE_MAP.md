# Results and evidence map

All estimates below retain the source report's cohort, scoring, and evidence-status boundaries.

## CST

| Study | Result | Interpretation boundary |
|---|---|---|
| Early BoolQ E3 gate | AUROC 0.363; 95% CI [0.102, 0.611] | Point estimate is reverse-direction; interval includes chance. Gate 2 failed; later phases were not run under the original gate. |
| Strict independent-counter-evidence pilot (as summarized in the archived V11 manuscript) | Flip contrast +0.2118 [0.1160, 0.3097]; placebo flip 0.5141; only 3 high-consensus wrong cases; independent-score AUROC 0.624 [0.286, 0.856] | Placebo criterion failed; behavior contrast is not reliable error-ranking evidence. |
| Round-8 VitaminC E1 method search | 1,250 requests; 587 parser-valid (47.0%). On common support: A/A 0/149 flips; C1a and C1b each 41/69 (59.4%; CI [50.7%, 69.7%]); natural opposing evidence 92/132 (69.7%; CI [51.5%, 86.2%]). | Reused 50-item development cohort; exploratory selection. Placebo is not inert, effective coverage is limited, and no error-prediction claim follows. C1a was selected only by a frozen tie rule, not superiority. |

Primary CST source: `consensus_stress/round8/method_search_e1_run_v2_ling_local_20260926/CST_E1_FINAL_REPORT.md`. Earlier gate/pilot synthesis: `paper_intervention_tested_reliability_20260921/expected_response_reliability_naacl_revision_20260923/manuscript_v11_construct_validity_and_confirmation_plan_20260926/main.tex` and `consensus_stress/SUMMARY_20260913.md`.

## PECR original fixed-cohort TEST analysis

- FinQA selected TEST cohort: 157 items, 139 scorable; 94 errors among 139.
- Program-conditioned relation risk: error AUROC 0.7337 (95% CI [0.6615, 0.7991]); AUPRC 0.8164.
- Difference versus fixed majority-direction baseline: +0.0500 AUROC (95% CI [−0.0092, +0.1215]); superiority not established.
- The 18 unscorable items were subsequently all labeled incorrect, a material outcome-associated missingness concern.
- Gold executable programs and transformed program results condition construction; only scoring is numeric-answer-blind. This is not end-to-end oracle-free.

Source manuscript: `paper_intervention_tested_reliability_20260921/expected_response_reliability_naacl_revision_20260923/manuscript_v7_two_reviewer_sensitivity_20260925/main.tex` (and subsequent V11 draft for the expanded audit/limitations).

## PECR 565-item holdout collection and analysis

- Sealed collection: 1,130 request slots; 1,129 HTTP-200 terminal records; 860 parser-valid and 269 invalid. Slot 608 (mutated world) is unknown, not retried; later slots completed. This collection receipt alone is not an effectiveness result.
- Post-collection V1.4 analysis: 565 unique score rows; labels for 565, of which 412 were labeled under the project-specific free-text numeric rule (355 errors, 57 correct) and 153 did not yield a valid numeric original answer. Primary paired relation comparison support: n=357 across 108 source groups (312 errors, 45 correct).
- On paired support, relation-augmented error AUROC 0.7171 versus graph-only 0.6919; paired difference +0.0259, source-group bootstrap 95% CI [−0.0135, +0.0651]. AUPRC difference +0.0132 [−0.0008, +0.0292]. Not statistically decisive.
- Secondary full-coverage comparison on 412 labeled items: PECR 0.7049 versus graph-only 0.6864; difference +0.0193 [−0.0133, +0.0532].
- Important chronology limitation: V1.2 read target answers before halting on a parser schema mismatch; exact decode time lacks independent timestamp. V1.3 corrected parser/polarity after that reveal. V1.4 corrected reporting/provenance, not rows/metrics. Thus not a clean preregistered confirmation. Scoring is a project-specific free-text numeric match, not official FinQA execution scoring. Missing labels are outcome-associated under the project rule.

Sources:
- `v9_cst_pecr_zero_call/pecr_holdout_confirmation_v3_20260927/analysis_v1_4/results/ANALYSIS_REPORT_V1_4.json`
- `v9_cst_pecr_zero_call/pecr_holdout_confirmation_v3_20260927/analysis_v1_4/results/RESULTS_SUMMARY_V1_4.csv`
- `v9_cst_pecr_zero_call/pecr_holdout_confirmation_v3_20260927/reports/POST_COLLECTION_SEAL_V3_1.json`

## PECR repair and repairability

- Post-hoc end-to-end repair V2, nominal trigger budget 85 per policy. PECR: 83 labeled triggers, 78 valid repairs, 0 corrections, 0 harms; net gain 0. Graph policy: 1 correction, 0 harms; confidence: 3 corrections, 1 harm; random: 3 corrections, 4 harms. Paired/source-group intervals are wide and policy differences include zero. Invalid repair was scored intention-to-treat as no-op. This does not show PECR repair superiority.
- OOF development-validation, 359 selections per policy. Net gains: PECR risk only +0.28 pp (95% CI [−1.39, +1.95]); PECR×repairability −0.28 pp [−1.67, +1.11]; PECR×model-score disagreement +0.28 pp [−2.23, +2.79]; combined+abstention +1.39 pp [−0.84, +3.62]. Paired difference of combined+abstention versus risk-only +1.09 pp [−1.40, +3.90]. No stable benefit established; this split was used during development.

Sources:
- `v9_cst_pecr_zero_call/pecr_holdout_confirmation_v3_20260927/repair_study_v2/results/PECR_HOLDOUT_END_TO_END_REPAIR_TABLE_V2.md`
- `v9_cst_pecr_zero_call/repairability_validation_v1_20260927/results/REPAIRABILITY_VALIDATION_TABLE_V1_1.md`

## Reproducibility / integrity note
The source artifact locations above are local to the originating workspace and are not all included in this GitHub handoff. This package contains a curated report of results, not raw data. Before submission, independently replay calculations from authorized source artifacts, verify all hashes and citations, and preserve the stated unknown/provenance limitations.

### Source report hashes (SHA-256)
- CST Round-8 E1 report: `244ff600b288507428eb7920931af5c6e3a90f260656085e6f89bd5b803d41bd`
- PECR holdout analysis V1.4 JSON: `786a36e9e8cb091ea5145dbd5ca6244cf0f38f72bd386eafde1dd0abcdade4e8`
- PECR holdout repair V2 JSON: `d6a62dcec4b0cc3f9ab32b4caa345dfb9eaa165921668cbb9b9e1a18cdf1aa86`
- Repairability validation V1.1 JSON: `bfcd1b87b4b963d47c50a6bb48a85e5bf81692481fa30743ea94825d77bb2c73`
