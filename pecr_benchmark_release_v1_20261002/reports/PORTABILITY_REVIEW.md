# Standalone numerical benchmark portability review

Status: final acceptance review passes. Both generation-aligned tracks and the historical shared-Qwen track pass moved-core portability, canonical coverage and exact clean replay. The independent review itself performed zero fits and did not read gold, raw ledgers, holdout, model checkpoints or model APIs. A separately authorized native-reference construction performed exactly 20 fixed HGB fits; that construction and the independent review are recorded separately.

## Copy and adapt

- Qwen corrected: copy the four `data/strict` files, fold provenance, `data/schema.json`, full effective HGB parameters, and saved refit OOF/runtime/metrics. The queue is 2,142 rows / 452 groups, 1,699 errors / 443 correct.
- DeepSeek shared: copy the four strict cohort files and fold provenance from the previous numeric export; copy its component OOF (five methods) and the archival graph-only prediction. The queue is 2,050 rows / 448 groups, 1,257 errors / 793 correct.
- DeepSeek native: copy `G96_NATIVE.npz`, `G96_SCHEMA.json` and native reference OOF/runtime/audit. The native matrix has explicit `item_ids`, `groups`, `G96_native`; the original reference OOF includes `y`, `outer_fold` and four source-comparison predictions. A separately versioned six-method reference now exists in `reference/deepseek_aligned`: existing native Raw/Full were copied exactly, while Graph-only and three fixed component masks were constructed with 20 fits. The final uniform replay must refit all six native methods; the four source-comparison predictions can then reuse corresponding shared/native results without extra fits.
- Copy the verified numeric Curve33 arithmetic and shared evaluation helper into local package source. Adapt loaders to package-relative cohort paths. The old corrected preparation script still loads its sibling numeric code in preparation mode; the old native entry also defaults to a sibling bundle. Neither is portable unchanged. Do not include or invoke gold/ledger preparation stages in the release training path.
- Include all 2,241 attempted rows in a sanitized frame, their requested/construction flags, recorded per-world parser/unit status, saved label status and strict/exclusion partition. Qwen requested exclusions are 52 valid/unknown-label + 7 invalid/known-label + 24 invalid/unknown-label = 83; 16 unrequested construction exclusions are separate. Keep unknown states unknown.

## Exact matrix contract

Six primary matrices have dimensions 96, 113, 129, 124, 125, 121 in graph-only, Raw, Full, no-normalization, no-curvature/asymmetry and no-direction order. Graph-only must be an independent copy; all concatenations must allocate independent arrays. Raw17 equals the first 17 Curve33 columns. Family deletion uses the saved feature names while preserving original order.

G96 has an intentional historical duplicate name `answer_number_count` at indices 4 and 35. Preserve both columns and index-aware `column_identity`; do not deduplicate names. Native G96 must retain exactly the same feature order and saved float64 representation of frozen float32 graph values. Its saved matrix hash contract includes dtype, shape and C-order bytes.

## DeepSeek graph-only reference boundary

The archival graph-only prediction exists on the same 2,050 y/groups, with AUROC 0.7672062929 and AUPRC 0.8186421248. The same archival file's Raw and Full predictions are elementwise identical to current component OOF. Original graph-only code uses the same G96 float64 copy, GroupKFold(5), and HGB parameters.

Before release fitting, the retained same-runtime evidence covered only the five component methods. Release clean fitting now confirms the archived graph-only prediction elementwise: `audit/FIRST_PASS_DEEPSEEK_EXACT.json` and the complete repaired 70-fit acceptance OOF both pass all six DeepSeek shared methods. Its source remains archival; its actual numerical reproduction is now verified.

## Runtime and budget

Observed runtime: Python 3.13.13, NumPy 2.5.3, SciPy 1.18.1, scikit-learn 1.9.0, threadpoolctl 3.6.0. Freeze the complete effective HGB parameter dictionary, including defaults, plus threadpool limit 1. The original recipe is max_iter=250, max_leaf_nodes=15, learning_rate=0.05, l2_regularization=1, random_state=20260928. Package installs and platform compatibility still need clean-environment evidence; a requirements file alone does not prove reproduction.

The initial complete entry used Qwen 30 + DeepSeek shared 30 + native extra 10 = 70 fits. Its first execution completed fitting but failed during export because the historical evaluation included three additional contrasts; that failure is retained. The repaired entry completed another fixed 70-fit run with every saved prediction and recomputed point/interval exact. Extra historical contrasts are explicitly retained as not recomputed, rather than changing the fixed five-contrast specification.

The final three-track entry uses 30 fits each for Qwen corrected, DeepSeek shared and DeepSeek native = 90 fits, plus zero fits for native-source aliases. Four native control references were separately constructed with 20 fixed fits and are explicit post-hoc additions, not recovered historical results. Existing folds are saved post-hoc assignments; validation preserves them without claiming a historical freeze date.

## Independent acceptance

Both the earlier two-track and final three-track isolated checks have passed. The root agent owns the pinned clean virtual-environment 90-fit replay and difference receipts. Review checks use the package's public numerical inputs and saved references only.

This release supports standalone replay of precomputed numerical features and saved labels. It does not recreate model generations or financial graph extraction from original private inputs, and does not by itself establish generalization or acceptance claims.

## Independent moved-core checks

Copied only package src/protocol/cohorts/reference into a fresh unrelated directory with no old sibling projects, datasets or ledgers. Both isolated-interpreter default-root validation and a separate launcher-only `--root` validation passed in the fresh pinned virtual environment. The launcher-only directory has no cohort/reference files, so the latter verifies that the explicit root is used. Both runs reported fits=0. The complete receipts and core hashes are retained in the machine-readable review.

The numeric benchmark entry reads only local package resources. Original absolute source paths in archival metadata are provenance, not input dependencies. The separate opt-in financial prompt reconstruction entry is not imported by the numeric benchmark.

The final three-track checks copied only src/cohorts/reference/protocol/coverage and the manifest, excluding bytecode, into clean unrelated directories. Fresh pinned-venv `-I -B` checks passed both with the copied default root and with a separate launcher-only directory whose explicit `--root` points at the moved package. All three cohorts, six methods per cohort and native aliases pass, and copied core hashes remain unchanged. These checks performed zero fits. The final validator prioritizes `FINAL_SUMMARY.json` and independently verifies the canonical attempted frame and unknown-status guards.

## Independent canonical coverage checks

All 35 independent checks pass for `coverage/attempted_frame_final.jsonl` and its CSV/summary. The 6,723 rows are three complete 2,241-row frames, each with 2,225 requested and 16 unrequested items. IDs/groups retain identical frame order across tracks; strict member IDs, saved labels and groups match the numerical cohorts exactly. Qwen's 83 requested exclusions are 52 valid/unknown-label, seven invalid/known-label and 24 invalid/unknown-label. Each DeepSeek track's 175 are 54, 79 and 42 respectively.

Recorded per-world states and offline parser states are separate. All unrequested states remain unknown, with parser validity null; they are not promoted to success. Native G is computed for exactly the 2,050 strict items and explicitly not computed for the other 191. Original-answer, label-target and native/Qwen G field hashes match on their strict generation-aligned tracks. The earlier 4,482-row two-track coverage remains preserved. Coverage/code hashes were unchanged during these checks; all 24 originally audited numerical-source hashes also remain unchanged.

## Final clean replay and contract

The root-owned final clean environment completed exactly 90 fits, with one-thread limits and no system-site packages. Independent receipt review passes all 31 checks: all 69 recorded training-input file hashes match the current release, all three six-method OOFs and the four source aliases reproduce reference metadata and predictions elementwise, every difference CSV contains only its header, and all saved point estimates and paired intervals match exactly. The shared DeepSeek graph-only archival reference also reproduces exactly. Each cohort uses 2,000 paired source-group bootstrap draws, seed 20260928, with zero degenerate draws.

Fifteen additional final-contract/latest-moved checks pass. `protocol/FINAL_RELEASE_SPEC.json` and `MANIFEST.json` are authoritative: Qwen corrected and DeepSeek native are generation-aligned tracks, while DeepSeek shared-Qwen is a historical source track. Six method vectors, their fixed feature-family masks, column order, dimensions, complete 21 HGB parameters and bootstrap protocol are unchanged. The final planned and actual fit counts are both 90; source-comparison aliases require zero extra fits. Old phase-one specifications remain preserved and explicitly superseded.

Actual release-task history is retained: 70 fits in the first failed export, 70 in the repaired existing suite, 20 in post-hoc native reference completion and 90 in final clean replay, totaling 250 fits. Launcher/schema guard failures contributed zero fits. No seed, parameter or sample search occurred. There are no outstanding checks in this independent portability review; this verdict verifies numerical replay and provenance bounds, not an independent generalization or paper-acceptance claim.
