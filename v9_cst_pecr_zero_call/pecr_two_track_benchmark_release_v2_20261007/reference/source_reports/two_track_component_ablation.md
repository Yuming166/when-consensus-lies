# Raw+44 component ablation: Qwen3.5-4B and DeepSeek V4.1 Flash

## Cohorts and protocol

Both tracks use their saved labels and five source-group folds. Qwen3.5-4B has 1,597 items / 413 groups; DeepSeek V4.1 Flash has 1,537 strict paired items / 407 groups. The cohorts are evaluated separately, not pooled. The same HGB parameters, 250 iterations and feature-column order are used for the five views within each track.

Arithmetic44 is partitioned by its frozen column schema: indices 0–23 are original/positive/negative per-world numerical-alignment features; 24–39 are cross-world consistency features; 40–43 are four question-operation cues. The three ablations drop one complete block at a time. Raw is the matched G96+Raw16+h,t baseline; Full adds all 44 features.

## OOF results

| Model track | Input | Dim. | AUROC | AUPRC | Full − ablated AUROC (familywise 95% CI) |
|---|---|---:|---:|---:|---|
| Qwen3.5-4B | Raw baseline | 114 | 0.8035 | 0.9266 | — |
| Qwen3.5-4B | Full Raw+44 | 158 | 0.8294 | 0.9399 | — |
| Qwen3.5-4B | −Per-world alignment | 134 | 0.8117 | 0.9319 | +0.0177 [+0.0033, +0.0326] |
| Qwen3.5-4B | −Cross-world consistency | 142 | 0.8334 | 0.9420 | -0.0040 [-0.0138, +0.0059] |
| Qwen3.5-4B | −Question-operation cues | 154 | 0.8340 | 0.9425 | -0.0046 [-0.0119, +0.0028] |
| DeepSeek V4.1 Flash | Raw baseline | 114 | 0.7818 | 0.8131 | — |
| DeepSeek V4.1 Flash | Full Raw+44 | 158 | 0.8068 | 0.8297 | — |
| DeepSeek V4.1 Flash | −Per-world alignment | 134 | 0.8028 | 0.8326 | +0.0040 [-0.0072, +0.0155] |
| DeepSeek V4.1 Flash | −Cross-world consistency | 142 | 0.7928 | 0.8185 | +0.0140 [+0.0050, +0.0239] |
| DeepSeek V4.1 Flash | −Question-operation cues | 154 | 0.8016 | 0.8285 | +0.0052 [-0.0025, +0.0131] |

### Context: complete-method gain over the Raw baseline

The previously reported paired comparisons provide context for the ablations. On Qwen3.5-4B, Full Raw+44 improves AUROC over Raw by +0.0259 (campaign-adjusted 95% source-group interval [+0.0060, +0.0453]); over Curve29 the gain is +0.0265 ([+0.0067, +0.0456]). On DeepSeek V4.1 Flash, Full Raw+44 improves over Raw by +0.0250 (family-corrected 95% source-group interval [+0.0125, +0.0378]); over Curve by +0.0229 ([+0.0087, +0.0378]). These are inherited comparisons from the existing track reports, not additional contrasts in this six-test ablation family. Both intervals exclude zero.

The leave-one-block-out pattern differs by model track: removing per-world numerical alignment produces the clearest AUROC drop for Qwen, while removing cross-world consistency produces the clearest drop for DeepSeek. This is a conditional component contribution, not an additive attribution. For Qwen, the family-corrected AUPRC interval for per-world alignment includes zero; for DeepSeek, the family-corrected AUPRC interval for cross-world consistency is above zero. On Qwen, removing the joint or question-operation block slightly raises AUROC at the point estimate, but the corrected intervals include zero. These are conditional OOF development findings, not independent new-question confirmation.

### Paired contrasts

The primary contrast is full Raw+44 minus each feature-family ablation. A positive delta means the full method scores higher. The reported simultaneous intervals use 5,000 paired source-group bootstrap draws and Bonferroni correction over six AUROC ablation contrasts. Company-cluster intervals are a sensitivity analysis; their folds are not company-disjoint.

**Qwen3.5-4B**

| Removed feature family | Δ AUROC | 95% source-group CI | Familywise 95% CI | Δ AUPRC | Δ error recall@10% |
|---|---:|---|---|---:|---:|
| Per-world alignment | +0.0177 | [+0.0065, +0.0289] | [+0.0033, +0.0326] | +0.0080 | +0.0016 |
| Cross-world consistency | -0.0040 | [-0.0114, +0.0035] | [-0.0138, +0.0059] | -0.0021 | -0.0008 |
| Question-operation cues | -0.0046 | [-0.0101, +0.0010] | [-0.0119, +0.0028] | -0.0026 | -0.0008 |

**DeepSeek V4.1 Flash**

| Removed feature family | Δ AUROC | 95% source-group CI | Familywise 95% CI | Δ AUPRC | Δ error recall@10% |
|---|---:|---|---|---:|---:|
| Per-world alignment | +0.0040 | [-0.0040, +0.0121] | [-0.0072, +0.0155] | -0.0029 | -0.0048 |
| Cross-world consistency | +0.0140 | [+0.0071, +0.0213] | [+0.0050, +0.0239] | +0.0112 | +0.0048 |
| Question-operation cues | +0.0052 | [-0.0004, +0.0111] | [-0.0025, +0.0131] | +0.0012 | -0.0012 |

### Company-cluster sensitivity (appendix)

| Track | Removed block | Δ AUROC | Familywise 95% company-cluster CI |
|---|---|---:|---|
| Qwen3.5-4B | Per-world alignment | +0.0177 | [+0.0024, +0.0356] |\n| Qwen3.5-4B | Cross-world consistency | -0.0040 | [-0.0133, +0.0051] |\n| Qwen3.5-4B | Question-operation cues | -0.0046 | [-0.0108, +0.0026] |\n| DeepSeek V4.1 Flash | Per-world alignment | +0.0040 | [-0.0066, +0.0160] |\n| DeepSeek V4.1 Flash | Cross-world consistency | +0.0140 | [+0.0059, +0.0232] |\n| DeepSeek V4.1 Flash | Question-operation cues | +0.0052 | [-0.0019, +0.0124] |\n\nEach track contains 117 companies. Source-group folds were used for fitting, and companies may occur in more than one fold; these intervals resample saved OOF scores and are a clustering sensitivity analysis, not a company-held-out test.\n\n## Interpretation limits

The ablation intervals condition on OOF predictions and do not include model-selection or training variability. Removing a block tests its incremental value in this fixed HGB representation; it does not establish that matched cells reflect the model's actual reasoning. The existing positive Raw+44-versus-Raw results are documented in the parent Qwen and DeepSeek reports; this table focuses on the contribution of the three prespecified feature families. No new questions or API requests were used.

## Reproducibility

Fifty fixed HGB fits completed (50); saved Raw and Full OOF predictions were checked against both reference tracks. Source-group folds are isolated; same-company items can occur in different folds. Feature, label, ID, fold, matrix-order and interval checks are recorded in `audit/VALIDATION.json`.
