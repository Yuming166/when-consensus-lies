# Fixed Raw+Arithmetic44 attribution controls

Completed 2026-10-07 (Asia/Shanghai): **90 fixed HGB fits**, no model/API requests, no reference-answer or holdout access. Inputs, labels, rows, and folds come unchanged from the sibling `pecr_two_track_benchmark_release_v2_20261007`. Existing release files were not modified. The protocol and its SHA-256 were written before fitting; these are post-hoc development controls, not independent confirmation.

## Results

| Feature view | Dimensions | Qwen AUROC | DeepSeek AUROC |
|---|---:|---:|---:|
| G96 | 96 | .7379 | .7260 |
| G96 + clean construction metadata | 99 | .7421 | .7386 |
| G96 + Raw16 | 112 | .8023 | .7819 |
| G96 + Raw16 + h,t (Raw) | 114 | .8035 | .7818 |
| G96 + Curve29 | 125 | .8029 | .7839 |
| Raw + Arithmetic44 | 158 | .8294 | .8068 |

The clean construction descriptors are `expected_direction_up`, signed actual operand edit `h`, and relative edit `t`. G96 already includes original-answer information. No edited-world response dynamics enter the construction-only addition. This control does not exhaust every conceivable piece of construction metadata.

Raw minus the construction model: Qwen **+.0614 [.0236,.0995]**; DeepSeek **+.0432 [.0158,.0710]** AUROC, with Bonferroni-adjusted paired source-group intervals across four contrasts in two tracks. Adding h,t alone to G96+Raw16 has intervals spanning zero on both tracks. The results support the incremental value of observed intervention responses beyond the tested descriptors, not complete independence from construction information.

## Historical compatibility

Three extra controls retain the inherited Raw17[16] scalar `construction_absolute_delta`: G96 + four construction descriptors, G96+Raw17, and G96+Raw17+h,t. These are diagnostic only. The field is not assumed to equal abs(h), and its repaired-input alignment remains unresolved. The main clean comparisons exclude it on both sides.

## Files and reproduction

- `protocol/PROTOCOL.json`, `PROTOCOL.sha256`: pre-fit plan, source hashes, contrasts and statistics.
- `protocol/HGB_PARAMS.json`: the exact released learner configuration.
- `src/run.py`: fixed runner; refuses to overwrite `results/`.
- `results/METRICS.csv`, `CONTRASTS.csv`, `RESULTS.json`: complete metrics, nominal and adjusted intervals, support, feature-matrix hashes and exact-refit checks.
- `results/*_OOF.csv`, `*_OOF.npz`: all predictions with unchanged IDs, groups, folds and labels.
- `results/VALIDATION.json`: PASS; original Raw, Curve and Raw+44 predictions reproduced exactly on both tracks.
- `results/RUNTIME.json`: runtime versions, 90 completed fits, 106 seconds observed elapsed time.

Use the environment lock from the source release. Copy this directory without its generated `results/` into a new sibling directory, then run `python src/run.py`. No source corpus is required. Bootstrap uses 10,000 paired group draws, seed 20260928; its weighted metric implementation was checked against scikit-learn. AUROC and AP are separately corrected eight-comparison families. Intervals condition on the fitted OOF and omit training and earlier selection variance. Paper-ready tables are in the sibling manuscript package.
