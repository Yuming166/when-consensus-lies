# Saved results

All values below are copied from the immutable source OOF reports packaged under `reference/source_reports/`. They are conditional cross-validated development estimates on previously explored data.

| Track | Input | AUROC | AUPRC |
|---|---|---:|---:|
| Qwen3.5-4B | Raw | 0.8035 | 0.9266 |
| Qwen3.5-4B | Curve | 0.8029 | 0.9296 |
| Qwen3.5-4B | Raw+Arithmetic44 | 0.8294 | 0.9399 |
| DeepSeek V4.1 Flash | Raw | 0.7818 | 0.8131 |
| DeepSeek V4.1 Flash | Curve | 0.7839 | 0.8184 |
| DeepSeek V4.1 Flash | Raw+Arithmetic44 | 0.8068 | 0.8297 |

The saved source-group bootstrap reports give Qwen AUROC deltas of +0.0259 over Raw (campaign-adjusted 95% CI [+0.0060, +0.0453]) and +0.0265 over Curve ([+0.0067, +0.0456]). DeepSeek gives +0.0250 over Raw (fixed-family 95% CI [+0.0125, +0.0378]) and +0.0229 over Curve ([+0.0087, +0.0378]). The adjustment families follow the original track-specific fixed analyses and differ across tracks; see `results/primary_contrasts.csv`.

Component ablations are reported in `tables/raw44_component_ablation.tex`. In the six-contrast family, Qwen full Raw+44 exceeds the version without per-world alignment by +0.01765 AUROC (adjusted 95% CI [+0.00331, +0.03264]); its other two removal contrasts cross zero. DeepSeek full Raw+44 exceeds the version without cross-world consistency by +0.01400 (adjusted 95% CI [+0.00496, +0.02388]); its other two removal contrasts cross zero.

The two cohorts have different model-specific labels and supports. These are not independent new-question confirmation results, and the intervals do not account for training variance or prior method selection.
