# Saved PECR performance and ablations

All rows use the saved 1,735-item OOF universe (1,375 errors / 360 correct), 424 source groups, and coverage 100%. The Transformer rows are saved exploratory development outputs; the HGB rows are the audited zero-call recomputation.

| Method | AUROC | AUPRC | Δ AUROC vs Curve | 95% source-group CI | Coverage | Role |
|---|---:|---:|---:|---|---:|---|
| graph_only | 0.7275 | 0.9032 | -0.0862 | [-0.1102, -0.0629] | 100.0% | structural baseline |
| two_world_hgb | 0.7722 | 0.9201 | -0.0416 | [-0.0605, -0.0224] | 100.0% | two-world HGB; positive/original response only |
| three_world_hgb | 0.7978 | 0.9308 | -0.0160 | [-0.0269, -0.0041] | 100.0% | ordinary three-world HGB |
| three_world_curve_hgb | 0.8138 | 0.9371 | — | — | 100.0% | audited Curve HGB |
| full | 0.7924 | 0.9265 | -0.0213 | [-0.0336, -0.0077] | 100.0% | Transformer full |
| no_consistency | 0.7914 | 0.9217 | -0.0224 | [-0.0350, -0.0086] | 100.0% | Transformer ablation |
| no_edit | 0.7915 | 0.9236 | -0.0223 | [-0.0346, -0.0084] | 100.0% | Transformer ablation |
| no_numeric | 0.7924 | 0.9264 | -0.0213 | [-0.0333, -0.0079] | 100.0% | Transformer ablation |
| no_reverse | 0.7922 | 0.9264 | -0.0215 | [-0.0337, -0.0079] | 100.0% | Transformer ablation |
| shuffle | 0.7926 | 0.9265 | -0.0212 | [-0.0332, -0.0076] | 100.0% | Transformer shuffled-pair ablation |
| no_hgb | 0.5247 | 0.8052 | -0.2891 | [-0.3325, -0.2416] | 100.0% | Transformer without HGB branch |

Additional saved comparison: two-world HGB − ordinary three-world HGB = −0.02565, 95% CI [−0.04280, −0.00914]. Curve HGB − ordinary three-world HGB = +0.01595, 95% CI [+0.00411, +0.02689] under the saved source-group bootstrap protocol (B=2,000, seed 20260928).

Caution: the source-group intervals quantify uncertainty conditional on fixed OOF predictions; they do not remove repeated development-set model-selection bias. Transformer ablation CIs are post hoc paired rechecks of saved OOF files, not preregistered confirmation tests.
