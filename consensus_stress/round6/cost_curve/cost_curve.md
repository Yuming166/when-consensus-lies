# Cost-Benefit Curve: how many calls buy how much reliability?

Protocol: `cs-round6-cost-curve-20260914` (frozen records only; zero new model calls).
Metrics: pair-grouped bootstrap (2,000 replicates), seeds `20260913 + method_index` (AUROC), `+100` (Risk@80), `+200` (paired AUROC), `+300` (paired Risk@80); Risk@80 operating point 0.8. Positive paired differences are `RS_q - method` (RS_q better). calls/item = marginal reversal/stress calls on top of the already-formed 5-agent consensus (total = marginal + 5 original calls).

## Probe constructions

- **reversal-only(K), K in {1,2,5}**: risk = 1 - mean f_reverse over the first K agents (agent_index 0..K-1), natural-reverse condition; f_reverse(agent i) = 1 iff the agent's natural-reverse answer == flip(its own frozen original answer). calls/item = K (marginal).
- **reversal-only(10) = reversal family**: risk = 1 - mean over all 5 agents of f_reverse + f_synthetic_reverse (both use the frozen oracle expectation flip(y0)). calls/item = 10 (marginal); included only to cover the 1/2/5/10 budget list.
- **reversal+paraphrase(2K), K in {1,2,5}**: risk = 1 - mean over first K agents of (f_paraphrase + f_reverse)/2. K=5 equals the frozen BF_q score function (10 scored calls). calls/item = 2K (marginal).
- **RS_q(25)**: frozen risk = -BF_q (parent protocol, 25 calls/item).
- Missing/invalid calls are treated as missing responses (round5 rule); a probe score is the mean over its valid calls, missing only if none are valid. Marginal calls exclude the 5 original consensus calls (the already-formed consensus is the probe's precondition); total = marginal + 5.
- Coarse-score caveat: reversal-only probes take few distinct values (2/3/6/11 distinct scores for K=1/2/5/10), so AUROC is the robust summary; Risk@80 (operating point 0.8) is tie-sensitive at the 80% cut and should be read with its pair-grouped CI.

## HC populations

| Model | HC items | pairs | wrong consensus |
|---:|---:|---:|---:|
| Qwen3.5-4B | 567 | 298 | 65 (11.5%) |
| Ling-3.0-tiny | 574 | 299 | 119 (20.7%) |

## AUROC and Risk@80 by calls/item

| Method | Calls/item (marginal / total) | Qwen AUROC [95%CI] | Qwen Risk@80 [95%CI] | Ling AUROC [95%CI] | Ling Risk@80 [95%CI] |
|---|---:|---|---:|---|---:|---:|
| CST RS_q (proposed) | 25 / 25 | 0.943 [0.924, 0.960] | 0.846 [0.651, 0.981] | 0.896 [0.875, 0.917] | 0.422 [0.272, 0.583] |
| Reversal-only probe (1 call) | 1 / 2 | 0.873 [0.827, 0.918] | 0.750 [0.462, 0.923] | 0.851 [0.826, 0.873] | 0.296 [0.148, 0.484] |
| Reversal-only probe (2 calls) | 2 / 4 | 0.895 [0.846, 0.937] | 0.807 [0.537, 0.943] | 0.866 [0.842, 0.887] | 0.338 [0.179, 0.518] |
| Reversal-only probe (5 calls) | 5 / 10 | 0.931 [0.913, 0.948] | 0.884 [0.556, 0.981] | 0.869 [0.847, 0.891] | 0.348 [0.184, 0.526] |
| Reversal-family probe (10 calls) | 10 / 20 | 0.832 [0.796, 0.867] | 0.480 [0.295, 0.676] | 0.753 [0.729, 0.776] | 0.201 [0.054, 0.355] |
| Reversal+paraphrase (2 calls) | 2 / 4 | 0.873 [0.824, 0.918] | 0.673 [0.435, 0.904] | 0.859 [0.834, 0.882] | 0.369 [0.193, 0.490] |
| Reversal+paraphrase (4 calls) | 4 / 6 | 0.898 [0.847, 0.941] | 0.807 [0.526, 0.942] | 0.878 [0.856, 0.899] | 0.412 [0.231, 0.545] |
| Reversal+paraphrase (10 calls) | 10 / 15 | 0.943 [0.924, 0.960] | 0.846 [0.640, 0.981] | 0.896 [0.876, 0.918] | 0.422 [0.268, 0.587] |

## Paired differences vs RS_q (RS_q - method, on HC intersection)

| Method | Qwen AUROC Δ [CI] | Qwen Risk@80 Δ [CI] | Ling AUROC Δ [CI] | Ling Risk@80 Δ [CI] |
|---|---:|---:|---:|---:|
| Reversal-only probe (1 call) | 0.069 [0.035, 0.109] | 0.096 [0.019, 0.251] | 0.046 [0.029, 0.064] | 0.126 [0.062, 0.167] |
| Reversal-only probe (2 calls) | 0.048 [0.017, 0.086] | 0.039 [0.000, 0.154] | 0.031 [0.016, 0.046] | 0.084 [0.031, 0.128] |
| Reversal-only probe (5 calls) | 0.012 [0.002, 0.023] | -0.039 [-0.038, 0.134] | 0.027 [0.013, 0.042] | 0.074 [0.031, 0.125] |
| Reversal-family probe (10 calls) | 0.111 [0.081, 0.139] | 0.366 [0.229, 0.487] | 0.144 [0.124, 0.164] | 0.221 [0.156, 0.296] |
| Reversal+paraphrase (2 calls) | 0.070 [0.033, 0.111] | 0.173 [0.039, 0.273] | 0.037 [0.023, 0.055] | 0.053 [0.032, 0.126] |
| Reversal+paraphrase (4 calls) | 0.045 [0.013, 0.082] | 0.039 [0.019, 0.173] | 0.019 [0.010, 0.027] | 0.011 [0.010, 0.075] |
| Reversal+paraphrase (10 calls) | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Token accounting (mean tokens/item, from frozen records)

| Model | Reversal-only(5) prompt / completion / total | RS_q(25) prompt / completion / total |
|---|---:|---:|
| Qwen3.5-4B | 1865 / 288 / 2154 | 8825 / 1371 / 10196 |
| Ling-3.0-tiny | 2046 / 130 / 2176 | 9732 / 622 / 10354 |

## Decision: adopt the 5-call cost story?

Pre-registered rule: adopt the 5-call cost story iff reversal-only(5) is not statistically worse than RS_q (paired AUROC CI lower bound <= 0, i.e. the CI includes `reversal5 >= RS_q`).
- **Qwen3.5-4B**: paired AUROC Δ = 0.0121 [0.0024, 0.0231]; adopt = **NO**.
- **Ling-3.0-tiny**: paired AUROC Δ = 0.0270 [0.0129, 0.0416]; adopt = **NO**.

## Conclusion (3 lines)

1. **不采纳“5 calls 成本故事”作为统计等价声明**：reversal-only(5) 与 RS_q(25) 的配对差 CI （RS_q − rev5）在两模型均不含 0（Qwen +0.012 [0.002, 0.023]；Ling +0.027 [0.013, 0.042]），即 5-call 探针在 AUROC 上统计上显著弱于完整 RS_q，差距虽小但不能宣称“5 calls ≈ 25 calls”。
2. **统计上可支持的便宜点是 10 calls/item**：reversal+paraphrase(10) 的逐项分数与 RS_q 完全一致（配对差 Δ=0.000 [0.000, 0.000]，因为 BF_q 只使用 paraphrase+reverse 这 10 个 scored calls）；若论文要降成本主张，应改为“10 calls/item”，而不是 5。
3. **边界**：Qwen 的 Risk@80 上 rev5 并不差（CI 含 0，点估 0.884 vs RS_q 0.846），但 AUROC 两模型均显著更弱；把 synthetic_reverse 加入探针（10-call reversal-family）反而稀释信号（Qwen 0.832 vs rev5 0.931），说明自然反证是核心信号、调用数增加并不单调。
