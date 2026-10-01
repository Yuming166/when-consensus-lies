# Pre-specified Curve component ablations — 2026-10-01

## Boundary

This is a **zero-call, versioned diagnostic** on existing three-world responses. It does **not** touch ledgers, frozen manifests, labels, old OOF arrays, the 565-item holdout, or prior reports. All classifiers use identical items, labels, source-group folds, parser rules, coverage, and HGB settings. Results are development-data mechanism diagnostics, not independent confirmation.

A runtime drift was found while extending the ablation to Qwen: the historical 2026-09-28 Qwen report (`Curve 0.8138`; paired gain `+0.0160 [ +0.0041, +0.0269 ]`) is **not exactly reproduced** by the same code and feature hash in the 2026-10-01 runtime (`0.8154`; paired gain `+0.0107 [-0.0032,+0.0230]`). Restoring NumPy 2.5.2, using scikit-learn 1.9.1, or forcing one thread did not restore the old output. Therefore **historical Qwen metrics are not mixed into this component table**. The Qwen replication below is a same-runtime recompute. Old artifacts remain unchanged.

## Cohorts

| Response family | Items | Source groups | Errors/correct |
|---|---:|---:|---:|
| DeepSeek complete attempt | 2050 | 448 | 1257/793 |
| Qwen same-runtime recompute | 1735 | 424 | 1375/360 |

## Method performance

| Feature set | DeepSeek AUROC | DeepSeek AUPRC | Qwen AUROC (same runtime) | Qwen AUPRC |
|---|---:|---:|---:|---:|
| Full Curve | 0.8412 | 0.8653 | 0.8154 | 0.9353 |
| Raw 3-world | 0.8259 | 0.8485 | 0.8047 | 0.9339 |
| Full − input normalization | 0.8426 | 0.8608 | 0.8099 | 0.9341 |
| Full − curvature/asymmetry | 0.8369 | 0.8590 | 0.8109 | 0.9331 |
| Full − direction information | 0.8376 | 0.8620 | 0.8135 | 0.9356 |

## Fixed paired AUROC contrasts

| Contrast | DeepSeek Δ | DeepSeek 95% CI | Qwen Δ | Qwen 95% CI |
|---|---:|---:|---:|---:|
| Full Curve − Raw 3-world (primary) | +0.0153 | [+0.0070, +0.0235] | +0.0107 | [-0.0032, +0.0230] |
| No normalization − Full | +0.0014 | [-0.0042, +0.0070] | -0.0055 | [-0.0152, +0.0042] |
| No curvature/asymmetry − Full | -0.0042 | [-0.0105, +0.0020] | -0.0044 | [-0.0112, +0.0026] |
| No direction − Full | -0.0035 | [-0.0106, +0.0037] | -0.0019 | [-0.0115, +0.0078] |

## Design reading

1. **The overall added Curve block is the defensible effect.** On the complete DeepSeek attempt, Full Curve beats the fair raw three-world baseline by **+0.0153** with CI **[+0.0070, +0.0235]**. The same-runtime Qwen recompute is directionally positive but its CI crosses zero.
2. **Do not attribute the gain to input normalization.** Removing normalized slope/input-scale features does **not** hurt DeepSeek AUROC and even raises its point estimate; it reduces DeepSeek AUPRC. The Qwen AUROC change is small and CI crosses zero. Thus normalized slopes are not the mechanism carrying the headline gain.
3. **Curvature/asymmetry and direction information remain mechanistically plausible but not individually established.** Both leave-one-family contrasts have negative point estimates in both response families, consistent with some contribution, but both CIs cross zero.
4. **Paper wording should therefore bind the gain to the full audited Curve representation**, not to a post-hoc “normalization wins” or “direction alone wins” narrative. The raw 17-dim three-world feature vector is the same-budget comparator.

## Implementation checks

For both runs: frozen feature SHA-256 matched, arrays do not share memory, and each named feature family was removed exactly. All implementation tests passed. No API/model request was issued.

## Recommended ARR-facing wording

> A pre-registered, finite decomposition shows that the gain is attributable to the complete audited bidirectional response-curve representation rather than to a single post-hoc feature family. Removing input normalization does not reduce AUROC, while removing curvature/asymmetry or direction-consistency features produces small, non-significant point decreases. We therefore interpret subfamily effects as diagnostic and do not claim a uniquely causal component.
