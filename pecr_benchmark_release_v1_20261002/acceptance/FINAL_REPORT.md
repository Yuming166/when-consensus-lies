# PECR benchmark actual release acceptance

PASS: two generation-aligned benchmark tracks plus the preserved shared-G historical track. This is local release preparation, not an upload or a new model validation.

## Source, generation and coverage

Qwen current labels, original response features and three-world Curve are bound by explicit item/response hashes. Native DeepSeek G96, labels and three worlds use the same original merged generation. Shared-Qwen G is explicitly cross-model and appears only as the historical/source track. DeepSeek label binding is recipe/file/ID-based and audited post-hoc: missing historical per-response label freeze hashes are not invented and gold correctness was not independently rechecked.

| Track | Strict rows | Groups | Folds | Error / correct | Requested coverage | Requested outside strict |
|---|---:|---:|---:|---:|---:|---:|
| qwen_generation_aligned | 2142 | 452 | 5 | 1699 / 443 | 96.27% | 83 |
| deepseek_generation_aligned | 2050 | 448 | 5 | 1257 / 793 | 92.13% | 175 |
| deepseek_shared_qwen | 2050 | 448 | 5 | 1257 / 793 | 92.13% | 175 |

Canonical coverage is `coverage/attempted_frame_final.jsonl/.csv`: 6,723 cohort/item records, 2,241 unique items per track, 2,225 requested and 16 unrequested per track. Qwen requested exclusions: 52 valid/unlabeled + 7 invalid/labeled + 24 invalid/unlabeled = **83**. DeepSeek exclusions: 54 + 79 + 42 = **175** per track. All per-world parse/unit/label/construction states remain visible. Unrequested parser validity is null, recorded status unknown; upstream exclusion eligibility is kept separately. Native G is not computed outside its fixed 2,050 rows and is never imputed from shared G.

## Same OOF primary and fixed component results

All numbers and intervals below come from the final clean OOF, with error=1 positive. Graph-only contains original answer information and is not an equal-call-budget baseline. The paired source-group bootstrap is fixed at 2,000 attempts, seed20260928; no degenerate retry, search or multiplicity correction.

### qwen_generation_aligned

| Method | AUROC | AP |
|---|---:|---:|
| graph_only | 0.751619 | 0.910388 |
| raw_three_world | 0.818593 | 0.938748 |
| full_curve | 0.832590 | 0.945045 |
| no_input_normalization | 0.819790 | 0.940868 |
| no_curvature_asymmetry | 0.834435 | 0.943681 |
| no_direction_information | 0.820878 | 0.937729 |

| Fixed contrast | Delta AUROC [95% CI] | Delta AP [95% CI] |
|---|---|---|
| full_minus_raw | +0.013997 [+0.004301, +0.024177] | +0.006297 [+0.002147, +0.010292] |
| full_minus_graph | +0.080971 [+0.057733, +0.104268] | +0.034657 [+0.023741, +0.046146] |
| full_minus_no_input_normalization | +0.012800 [+0.004961, +0.020570] | +0.004176 [+0.000634, +0.007779] |
| full_minus_no_curvature_asymmetry | -0.001844 [-0.009082, +0.005778] | +0.001364 [-0.002493, +0.005776] |
| full_minus_no_direction_information | +0.011713 [+0.002302, +0.021874] | +0.007316 [+0.001828, +0.013315] |

Bootstrap valid/degenerate: 2000/0; draw hash `76d4a74cfd17549f35562afb66053a2d2d4821319364b60c51f5824aec5d8eac`.

### deepseek_generation_aligned

| Method | AUROC | AP |
|---|---:|---:|
| graph_only | 0.797714 | 0.837084 |
| raw_three_world | 0.838587 | 0.858700 |
| full_curve | 0.850204 | 0.869699 |
| no_input_normalization | 0.850872 | 0.872122 |
| no_curvature_asymmetry | 0.843116 | 0.862355 |
| no_direction_information | 0.845096 | 0.864269 |

| Fixed contrast | Delta AUROC [95% CI] | Delta AP [95% CI] |
|---|---|---|
| full_minus_raw | +0.011617 [+0.004454, +0.018688] | +0.010999 [+0.000802, +0.020706] |
| full_minus_graph | +0.052490 [+0.035920, +0.069632] | +0.032615 [+0.016138, +0.050063] |
| full_minus_no_input_normalization | -0.000668 [-0.005710, +0.004181] | -0.002423 [-0.010452, +0.005198] |
| full_minus_no_curvature_asymmetry | +0.007088 [+0.001517, +0.012776] | +0.007344 [+0.000194, +0.014829] |
| full_minus_no_direction_information | +0.005107 [-0.000393, +0.010358] | +0.005430 [-0.002050, +0.012507] |

Bootstrap valid/degenerate: 2000/0; draw hash `a3b033a320702a8c4800225cd02f3fc259bae5a53fea55e3a3ca9f2dc58bb694`.

### deepseek_shared_qwen

| Method | AUROC | AP |
|---|---:|---:|
| graph_only | 0.767206 | 0.818642 |
| raw_three_world | 0.825887 | 0.848527 |
| full_curve | 0.841156 | 0.865345 |
| no_input_normalization | 0.842603 | 0.860791 |
| no_curvature_asymmetry | 0.836916 | 0.859018 |
| no_direction_information | 0.837624 | 0.861953 |

| Fixed contrast | Delta AUROC [95% CI] | Delta AP [95% CI] |
|---|---|---|
| full_minus_raw | +0.015269 [+0.007026, +0.023505] | +0.016818 [+0.005960, +0.028296] |
| full_minus_graph | +0.073950 [+0.054879, +0.092173] | +0.046703 [+0.028332, +0.065152] |
| full_minus_no_input_normalization | -0.001448 [-0.007005, +0.004172] | +0.004555 [-0.003571, +0.012769] |
| full_minus_no_curvature_asymmetry | +0.004240 [-0.001998, +0.010543] | +0.006327 [-0.001673, +0.014364] |
| full_minus_no_direction_information | +0.003532 [-0.003728, +0.010644] | +0.003392 [-0.005128, +0.012245] |

Bootstrap valid/degenerate: 2000/0; draw hash `a3b033a320702a8c4800225cd02f3fc259bae5a53fea55e3a3ca9f2dc58bb694`.

No best-variant replacement: Qwen no-curvature and DeepSeek native no-normalization have higher AUROC points than their respective Full methods. Full remains the fixed method. Native curvature-removal contrast is a newly completed post-hoc control; it is not independent mechanism confirmation. Confidence intervals condition on saved OOF and do not measure training uncertainty or selection correction.

## Actual clean execution and complete fit accounting

A fresh Python3.13.13 venv independently installed all pinned packages; include-system-site-packages=false. The numerical core was moved outside the source tree without old sibling directories. Final benchmark/numeric/evaluation code, parameters, all cohort files and all reference bytes are identical to those used in the clean execution.

| Phase | Actual HGB fits | Outcome |
|---|---:|---|
| First existing-suite pass | 70 | Report export failed on an extra historical contrast key; retained without claiming full success |
| Repaired existing-suite pass | 70 | Both main six-method suites and original native source contrast exactly reproduced |
| Native fixed suite completion | 20 | Four new controls; two existing native OOF methods reused |
| Final unified clean entry | 90 | Three six-method tracks and reused source contrast; every saved prediction, point and interval exact |
| Total this release task | 250 | No changed seed/parameter/sample or best-result selection |

Two earlier startup guards failed before fitting: isolated Python module path, and legacy schema identity serialization. Both corrections and the mutable-finalization audit guard are recorded. They did not change matrix values, labels, folds or HGB settings. The final fixed entry completed; checkpoints retain numeric OOF predictions only, never model weights.

## Acceptance checklist

| Gate | Evidence | Outcome |
|---|---|---|
| Same-generation target/features/Curve | `audit/native_generation_binding_audit.json`, current Qwen binding receipts | PASS for two aligned tracks; shared historical exception explicit |
| IDs/groups/folds/column order/hash trace | `audit/FINAL_NUMERIC_CHECK.json`, per-cohort schema and reference maps | PASS |
| Finite, nonsharing, exact Raw/Curve arithmetic/support | Three-track loader and independent portability checks | PASS |
| Actual clean primary/component/ref-origin reproduction | `acceptance/clean_refit_final/` | PASS, 90 fits, every prediction and saved interval exact |
| Full attempted frame including 83 Qwen exclusions | `coverage/FINAL_*`, canonical 6,723-row table | PASS |
| Three-world executable reconstruction | `intervention/REBUILD_AUDIT.json` | PASS, 13,350 / 13,350 canonical request hashes |
| Future generation policy dependencies/interfaces | `src/frozen/`, `intervention/NEW_GENERATION_PROTOCOL.md` | PASS, 23 synthetic policy checks; no future model run |
| Source preservation/privacy/scope | Old sealed artifact/source hashes; bounded export scan | PASS; no model API/gold regeneration/holdout/push |

The reconstruction needs the user-supplied original FinQA TRAIN bytes; only permitted input text leaves are decoded, without gold/program decoding. Default execution writes hashes only. Optional input export goes to a new private directory outside the public release. The actual saved profiles use Qwen max_tokens384 and DeepSeek max_tokens8192/reasoning_effortlow; collector prose was not treated as runtime evidence.

## Unavailable provenance and interpretation limits

Required source files missing: **none**. Exact historical DeepSeek per-row label freeze/hash receipts never existed and remain unavailable. Twenty-seven old Qwen structured originals could not be recovered from `../pecr_trd_delta_method_development_v3_20260926/v3_2/data/raw_ledger_sealed.jsonl`; per-row line/hash diagnostics remain in `reference/qwen/generation_map.jsonl`. These old answers are not inputs to the corrected generation. Missing collection batch/finished/recorded status remains unknown.

This release supports historical-response error ranking and exactly reconstructable intervention inputs. It does not establish effectiveness for a newly called model, official FinQA execution accuracy, semantic/causal validity of interventions, independent confirmation, or a review score. New responses need newly aligned labels/G96 and separately versioned strict queues. Old labels/OOF/primary/V16/V17 and all inspected private sources remain unchanged.
