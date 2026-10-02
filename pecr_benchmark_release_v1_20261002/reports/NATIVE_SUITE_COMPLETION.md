# Fixed native-G suite completion

This post-hoc completion creates four new fixed control references on the existing 2,050-row / 448-group DeepSeek queue. Native Raw and Full predictions are copied from the existing source comparison; neither is refitted. This is not recovery of four historical references.

Exactly 20 HGB fits: native Graph-only plus the three already fixed feature-family masks, five saved folds each. Complete 21 effective parameters and one-thread limits are unchanged. There is no seed, parameter, row, threshold or method search.

| Native-G method | Status | AUROC | AUPRC |
|---|---|---:|---:|
| graph_only | new_post_hoc_fixed_suite_completion | 0.797714 | 0.837084 |
| raw_three_world | existing_saved_native_oof_reused | 0.838587 | 0.858700 |
| full_curve | existing_saved_native_oof_reused | 0.850204 | 0.869699 |
| no_input_normalization | new_post_hoc_fixed_suite_completion | 0.850872 | 0.872122 |
| no_curvature_asymmetry | new_post_hoc_fixed_suite_completion | 0.843116 | 0.862355 |
| no_direction_information | new_post_hoc_fixed_suite_completion | 0.845096 | 0.864269 |

| Fixed contrast | Delta AUROC [95% CI] | Delta AUPRC [95% CI] |
|---|---|---|
| full_minus_raw | 0.011617 [0.004454, 0.018688] | 0.010999 [0.000802, 0.020706] |
| full_minus_graph | 0.052490 [0.035920, 0.069632] | 0.032615 [0.016138, 0.050063] |
| full_minus_no_input_normalization | -0.000668 [-0.005710, 0.004181] | -0.002423 [-0.010452, 0.005198] |
| full_minus_no_curvature_asymmetry | 0.007088 [0.001517, 0.012776] | 0.007344 [0.000194, 0.014829] |
| full_minus_no_direction_information | 0.005107 [-0.000393, 0.010358] | 0.005430 [-0.002050, 0.012507] |

Intervals condition on saved OOF predictions and use 2,000 source-group paired percentile draws, seed 20260928. These post-hoc controls do not establish independent confirmation or necessity of every curve family.

Numeric inputs, parameters and evaluation-source hashes are verified before/after fitting. Existing source references are preserved. Native schema and matrix hash, exact IDs/y/groups/folds, common support, finite/nonsharing matrices and per-method checkpoints are verified. No gold, ledger, holdout, checkpoint model or API is read.

The completion itself is reference construction, not the later independent uniform release reproduction. The root agent will separately validate the newly frozen six-method reference in the final clean acceptance run.

Run from a package with preserved inputs: `python src/freeze_native_suite.py --outdir reference/deepseek_aligned_new_version`; an existing output directory is refused.
