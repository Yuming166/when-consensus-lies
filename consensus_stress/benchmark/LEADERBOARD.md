# CST-Bench Leaderboard

Protocol: `cs-round5-matched-baselines-cst-bench-20260913`. Ranking is descriptive:
AUROC point estimate, then Risk@80, then lower calls/item. CIs are pair-grouped
bootstrap intervals. Positive paired differences (`RS_q - baseline`) favor RS_q.

## Qwen3.5-4B

HC population: 567 items / 298 pairs; wrong consensus = 65 (11.5%).

| Rank | Method | AUROC [95% CI] | Risk@80 [95% CI] | Calls/item | Tokens/item | Paired AUROC Δ vs RS_q [CI] | Paired Risk@80 Δ vs RS_q [CI] | Baseline significantly better on AUROC? |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | CST RS_q (proposed) | 0.943 [0.924, 0.960] | 0.846 [0.651, 0.981] | 25 | 10208 | n/a | n/a | — |
| 2 | Single-agent intervention | 0.925 [0.900, 0.948] | 0.769 [0.514, 0.942] | 25 | 10163 | 0.018 [-0.001, 0.039] | 0.077 [0.000, 0.210] | no |
| 3 | R_sym (internal) | 0.892 [0.864, 0.916] | 0.499 [0.281, 0.754] | 25 | 10208 | 0.051 [0.029, 0.075] | 0.347 [0.154, 0.502] | no |
| 4 | Frozen mean confidence | 0.728 [0.676, 0.775] | 0.268 [-0.004, 0.445] | 5 | 2157 | 0.215 [0.165, 0.270] | 0.578 [0.464, 0.774] | no |
| 5 | Binary semantic entropy | 0.645 [0.580, 0.712] | 0.249 [0.063, 0.475] | 25 | 10687 | 0.297 [0.228, 0.369] | 0.597 [0.393, 0.748] | no |
| 6 | Self-consistency disagreement | 0.645 [0.575, 0.712] | 0.249 [0.063, 0.485] | 25 | 10687 | 0.297 [0.229, 0.374] | 0.597 [0.401, 0.749] | no |
| 7 | SelfCheckGPT answer-match | 0.645 [0.575, 0.711] | 0.249 [0.072, 0.479] | 25 | 10687 | 0.297 [0.231, 0.370] | 0.597 [0.405, 0.744] | no |
| 8 | Raw sampled confidence | 0.628 [0.558, 0.693] | 0.095 [-0.148, 0.316] | 25 | 10687 | 0.314 [0.248, 0.383] | 0.751 [0.598, 0.910] | no |
| 9 | R_PI (internal) | 0.628 [0.584, 0.673] | -0.001 [-0.246, 0.257] | 25 | 10208 | 0.315 [0.271, 0.359] | 0.847 [0.684, 0.978] | no |
| 10 | Isotonic confidence | 0.585 [0.513, 0.651] | 0.037 [-0.202, 0.276] | 25 | 10687 | 0.358 [0.288, 0.432] | 0.809 [0.634, 0.963] | no |
| 11 | Vote agreement | 0.583 [0.530, 0.638] | 0.095 [-0.071, 0.382] | 5 | 2157 | 0.360 [0.305, 0.412] | 0.751 [0.532, 0.844] | no |
| 12 | Temperature confidence | 0.580 [0.503, 0.652] | 0.076 [-0.181, 0.325] | 25 | 10687 | 0.363 [0.284, 0.443] | 0.770 [0.597, 0.928] | no |

Point best: **CST RS_q (proposed)** (AUROC 0.943). RS_q rank: 1.
Baseline(s) significantly better than RS_q by paired AUROC CI: none. RS_q statistically maintains SOTA: **YES**.

## Ling-3.0-tiny

HC population: 574 items / 299 pairs; wrong consensus = 119 (20.7%).

| Rank | Method | AUROC [95% CI] | Risk@80 [95% CI] | Calls/item | Tokens/item | Paired AUROC Δ vs RS_q [CI] | Paired Risk@80 Δ vs RS_q [CI] | Baseline significantly better on AUROC? |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | CST RS_q (proposed) | 0.896 [0.875, 0.917] | 0.422 [0.272, 0.583] | 25 | 10357 | n/a | n/a | — |
| 2 | Single-agent intervention | 0.883 [0.860, 0.905] | 0.412 [0.239, 0.556] | 25 | 10312 | 0.014 [-0.003, 0.030] | 0.011 [-0.021, 0.085] | no |
| 3 | R_sym (internal) | 0.818 [0.787, 0.847] | 0.212 [0.033, 0.366] | 25 | 10357 | 0.078 [0.053, 0.104] | 0.210 [0.155, 0.309] | no |
| 4 | Frozen mean confidence | 0.611 [0.568, 0.655] | 0.128 [-0.051, 0.230] | 5 | 2177 | 0.285 [0.236, 0.330] | 0.294 [0.253, 0.430] | no |
| 5 | Raw sampled confidence | 0.587 [0.543, 0.632] | 0.075 [-0.073, 0.224] | 25 | 10834 | 0.309 [0.260, 0.358] | 0.347 [0.273, 0.439] | no |
| 6 | Temperature confidence | 0.585 [0.541, 0.629] | 0.075 [-0.079, 0.212] | 25 | 10834 | 0.312 [0.263, 0.362] | 0.347 [0.260, 0.438] | no |
| 7 | R_PI (internal) | 0.577 [0.553, 0.602] | -0.103 [-0.269, 0.050] | 25 | 10357 | 0.319 [0.292, 0.347] | 0.525 [0.448, 0.608] | no |
| 8 | Isotonic confidence | 0.568 [0.523, 0.614] | 0.075 [-0.072, 0.217] | 25 | 10834 | 0.329 [0.278, 0.378] | 0.347 [0.277, 0.444] | no |
| 9 | Binary semantic entropy | 0.562 [0.527, 0.600] | 0.086 [-0.040, 0.260] | 25 | 10834 | 0.334 [0.295, 0.373] | 0.336 [0.231, 0.413] | no |
| 10 | Self-consistency disagreement | 0.562 [0.527, 0.601] | 0.086 [-0.046, 0.252] | 25 | 10834 | 0.334 [0.292, 0.372] | 0.336 [0.231, 0.406] | no |
| 11 | SelfCheckGPT answer-match | 0.562 [0.527, 0.600] | 0.086 [-0.030, 0.260] | 25 | 10834 | 0.334 [0.297, 0.374] | 0.336 [0.229, 0.409] | no |
| 12 | Vote agreement | 0.544 [0.512, 0.579] | 0.054 [-0.072, 0.219] | 5 | 2177 | 0.353 [0.322, 0.385] | 0.368 [0.273, 0.431] | no |

Point best: **CST RS_q (proposed)** (AUROC 0.896). RS_q rank: 1.
Baseline(s) significantly better than RS_q by paired AUROC CI: none. RS_q statistically maintains SOTA: **YES**.

## Claim boundary

- Qwen is the primary model; Ling is secondary.
- The leaderboard covers the frozen 300-pair VitaminC natural-pair main split and HC subsets.
- BoolQ is packaged as a specificity/negative-control split and is not part of this leaderboard.
- No universal transfer, zero-shot, or all-domain SOTA claim is supported.
