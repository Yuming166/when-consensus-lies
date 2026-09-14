# Reducibility & Baseline-Fidelity Audit (Agent C / R3)

- 日期：2026-09-14
- 范围：回答"RS_q/BF_q 是否只是 R_sym 换权重 + paraphrase 轴"；leaderboard 同分布 baseline 合并；
  baseline 忠实度审计。
- 输入（只读，哈希见 §6）：`benchmark/frozen/vitaminc/{preoutcome,ling_preoutcome}_features.jsonl`、
  `benchmark/frozen/vitaminc/labels_ledger.json`、`round3/features.py`（冻结公式来源）、
  `phase0/baseline_manifest.json`（R_sym/R_PI 定义）。
- 方法：无新增模型调用；复用 `round3/analysis_lib.py` 的 pair-grouped bootstrap（2000 重采样、
  seed 基 `20260913` + 固定偏移）。全部统计量在 HC 子集（agreement >= 0.8）上计算：
  Qwen3.5-4B 567 items / 298 pairs / 65 wrong；Ling-3.0-tiny 574 items / 299 pairs / 119 wrong。

## 1. 冻结公式与代数关系

来自 `round3/features.py` 与 `phase0/baseline_manifest.json`（均未修改）：

| 量 | 冻结公式 |
|---|---|
| `bf_paraphrase` | 5 agents 在 paraphrase 条件下的平均 faithfulness（= 1 - para_flip_rate） |
| `bf_reverse` | 5 agents 在 natural-reverse 条件下的平均 faithfulness（= `rev_flip_rate`） |
| `BF_q` / `RS_q` | `BF_q = (bf_paraphrase + bf_reverse)/2`；`RS_q = -BF_q` |
| `R_sym` | `0.3*reverse_inertia + 0.7*intervention_disagreement`，其中 `reverse_inertia = 1 - rev_flip_rate` |
| `R_PI` | `0.1*D_inert + 0.3*flip_inertia + 0.6*frac_shared` |
| flip-rate | `rev_flip_rate`（自然反证下翻 answer 的 agent 占比） |
| disagreement | `intervention_disagreement = min(1, 2*pstdev(per_agent_flip_rate))`（R_sym 的第二项） |
| confidence | `mean_confidence`（original 条件的 5-agent 平均置信度） |

**关键代数观察**：`RS_q = -(bf_paraphrase + rev_flip_rate)/2`，`R_sym = 0.3*(1 - rev_flip_rate) + 0.7*intervention_disagreement`。
两者**唯一共享的成分是自然反证 flip 轴（`rev_flip_rate`）**，且有效权重不同（RS_q 记 -0.5；R_sym 经
`reverse_inertia` 记 -0.3）。第二轴完全不同：RS_q 用 paraphrase faithfulness，R_sym 用
`intervention_disagreement`。因此"RS_q 只是 R_sym 换权重"在代数上**不精确**——权重与第二轴都不同；
但"共享反证轴 + RS_q 多一个 paraphrase 轴"的直觉**方向正确**。

## 2. Spearman 相关（RS_q vs 各基线，pair-grouped 95% CI）

| 基线 | Qwen rho [CI] | Ling rho [CI] |
|---|---:|---:|
| R_sym | 0.822 [0.787, 0.845] | 0.859 [0.822, 0.886] |
| R_PI | 0.252 [0.185, 0.315] | 0.168 [0.117, 0.220] |
| flip-rate (natural reverse) | -0.978 [-0.988, -0.966] | -0.957 [-0.970, -0.939] |
| disagreement (intervention) | 0.209 [0.115, 0.304] | 0.130 [0.039, 0.222] |
| agreement (vote) | -0.347 [-0.409, -0.283] | -0.254 [-0.335, -0.178] |
| confidence (mean) | -0.222 [-0.305, -0.133] | -0.064 [-0.150, 0.021] |
| paraphrase faithfulness (axis) | -0.386 [-0.454, -0.316] | -0.345 [-0.421, -0.268] |

- RS_q 与 R_sym 强正相关（0.82 / 0.86），但远非同构；与 flip-rate 近完全相关（-0.98 / -0.96），
  说明 RS_q 的排序几乎完全由自然反证轴决定。
- 与 R_PI、intervention disagreement、vote agreement、confidence 的相关均弱（|rho| <= 0.35）；
  多数 CI 排除 0（弱但显著），仅 Ling 的 confidence CI 含 0（不显著）。

## 3. 增量 AUROC（RS_q 相对各基线单独做增量，pair-grouped 95% CI）

定义：对每个基线 B，用**不含标签**的 OLS 将 RS_q 对 B 残差化（每个 bootstrap 重采样内重新拟合），
计算残差对 `consensus_wrong` 的 AUROC。若 CI 下限 > 0.5，则 RS_q 在该基线上仍有显著增量信号。
参考：RS_q 原始 AUROC = Qwen 0.943 [0.924, 0.960]；Ling 0.896 [0.875, 0.917]。

| 基线 | Qwen 增量 AUROC [CI] | Ling 增量 AUROC [CI] | Qwen 配对差 RS_q-B [CI] | Ling 配对差 RS_q-B [CI] |
|---|---:|---:|---:|---:|
| R_sym | 0.874 [0.784, 0.931] | 0.787 [0.743, 0.831] | +0.051 [0.028, 0.075] | +0.078 [0.053, 0.106] |
| R_PI | 0.939 [0.918, 0.958] | 0.891 [0.867, 0.912] | +0.315 [0.271, 0.359] | +0.319 [0.290, 0.348] |
| flip-rate (natural reverse) | 0.284 [0.198, 0.381] | 0.317 [0.255, 0.384] | +0.874 [0.837, 0.906] | +0.766 [0.723, 0.806] |
| disagreement (intervention) | 0.941 [0.910, 0.959] | 0.891 [0.867, 0.912] | +0.407 [0.341, 0.479] | +0.421 [0.378, 0.462] |
| agreement (vote) | 0.914 [0.864, 0.951] | 0.888 [0.862, 0.909] | +0.526 [0.468, 0.585] | +0.440 [0.395, 0.487] |
| confidence (mean) | 0.928 [0.905, 0.957] | 0.926 [0.861, 0.943] | +0.671 [0.619, 0.724] | +0.508 [0.459, 0.559] |
| paraphrase faithfulness (axis) | 0.921 [0.901, 0.941] | 0.855 [0.830, 0.881] | +0.542 [0.481, 0.602] | +0.477 [0.421, 0.532] |

解读：

- **相对 R_sym**：增量 AUROC 0.874 / 0.787，CI 下限 0.784 / 0.743 均 > 0.5 —— RS_q 在 R_sym 之外
  **保留显著但适中的增量信号**（相对原始 AUROC 0.943 / 0.896 下降约 0.07 / 0.11）。
- **相对 flip-rate 轴**：增量 AUROC 0.284 / 0.317（< 0.5，方向反转，判别量级 |0.284-0.5| ~ 0.22）。
  进一步验证表明该残差对微小扰动高度敏感（去掉 reverse 轴后剩余成分很弱、方向不稳定），
  即 **RS_q 的可预测力几乎完全由自然反证轴承载**（见 §4）。
- **相对 R_PI / disagreement / vote / confidence**：增量 AUROC >= 0.89 且 CI 下限远超 0.5，
  RS_q 对这几类基线**不可归约**。

## 4. 轴分解（reverse 轴 vs paraphrase 轴）

| 量 | Qwen [CI] | Ling [CI] |
|---|---:|---:|
| RS_q AUROC | 0.943 [0.924, 0.960] | 0.896 [0.875, 0.917] |
| reverse 轴（-rev_flip_rate）AUROC | 0.931 [0.913, 0.947] | 0.869 [0.846, 0.891] |
| paraphrase 轴（-bf_paraphrase）AUROC | 0.599 [0.548, 0.652] | 0.581 [0.542, 0.621] |
| 配对差 RS_q - reverse 轴 | 0.012 [0.002, 0.022] | 0.027 [0.013, 0.042] |
| 配对差 RS_q - paraphrase 轴 | 0.344 [0.295, 0.393] | 0.316 [0.282, 0.349] |
| RS_q 相对 reverse 轴的残差增量 AUROC | 0.284 [0.194, 0.378] | 0.317 [0.257, 0.384] |
| RS_q 相对 paraphrase 轴的残差增量 AUROC | 0.921 [0.901, 0.941] | 0.855 [0.828, 0.880] |

- RS_q 的 AUROC 主要由 reverse 轴贡献（Qwen 0.931/0.943；Ling 0.869/0.896）；paraphrase 轴单独只有
  0.60 / 0.58。
- paraphrase 轴带来**小而统计显著**的增量（配对差 CI 下限 0.002 / 0.013 > 0，两个模型都显著）。
- 作为参照：R_sym（0.892 / 0.818）反而低于单独 reverse 轴（0.931 / 0.869），说明 R_sym 的
  `intervention_disagreement` 项（权重 0.7，自身 AUROC 仅 0.536 / 0.475）对预测是拖累；
  RS_q 相对 R_sym 的优势 = 引入 paraphrase 轴 + 不使用 intervention_disagreement。

## 5. 结论：RS_q/BF_q 是否只是 R_sym 换权重 + paraphrase 轴？

**判定：部分可归约（substantially overlapping），不可严格归约；不构成独立的新启发式。**

1. 代数上不是"只换权重"：R_sym 与 RS_q 仅在自然反证轴上重叠（权重 -0.3 vs -0.5），第二轴不同
   （R_sym 用 intervention_disagreement，RS_q 用 paraphrase）。
2. 经验上高度重叠：rho(RS_q, R_sym) = 0.82 / 0.86；RS_q 的信号几乎全由与 R_sym 共享的反证轴承载
   （reverse 轴单独 AUROC 0.931 / 0.869，占 RS_q 的 0.943 / 0.896 的绝大部分；round-6 的
   reversal-only(5) 探针以 5 个边际调用即达 AUROC 0.931 / 0.869，进一步印证反证轴是主导成分）。
3. RS_q 相对 R_sym 的增量真实存在但适中：残差增量 AUROC 0.874 [0.784, 0.931] / 0.787 [0.743, 0.831]，
   配对差 +0.051 [0.028, 0.075] / +0.078 [0.053, 0.106]（CI 排除 0）。增量来源是 paraphrase 轴 + 丢弃
   intervention_disagreement。
4. 对论文主贡献的含义（对应主指令 §6 的降级路径）：**不 claim "新启发式/新机制信号"**；
   主贡献按"基准 CST-Bench + 冻结复现 + 简洁信号（反证轴）"表述。机制叙述应明确：
   "错误跨近重复自然对相关 -> 自然反证轴可事前预测共识错误"，且该反证轴已被 R_sym 以 0.3 权重捕获，
   RS_q 的相对增益是 paraphrase 轴的小幅增量（配对 AUROC +0.05/+0.08 vs R_sym，两个模型均显著）。
5. BF_q 与 RS_q 只是符号相反：上述所有 AUROC 结论对 BF_q 相同，Spearman 符号取反。

## 6. 复现与哈希

- 脚本：`round6/reducibility/analyze_reducibility.py`（seed 基 `20260913` + 固定偏移；2000 重采样；
  结果 `round6/reducibility/reducibility_results.json`）。
- 输入哈希（sha256）：qwen features `d0c588d05211769c14234377d669881d079dacaac0ebaf2ec9326561d967584d`；
  ling features `35e853cf0815cb1428ec8f2ee671993bd1f87ba8b28ade24a630ac4c79bc26bb`；
  labels `770ede3f79b018c47aa982e6cb3f13b9d504b5c14950f7f1a8f6de196ffcbc5a`。
- 复现：`/storage/gaoym/sp500-forecastability-lab/.venv/bin/python consensus_stress/round6/reducibility/analyze_reducibility.py`

## 7. 外部 baseline 忠实度审计（哪些是原方法、哪些是二值/answer-match 变体）

| Leaderboard 行 | 类别 | 忠实度声明 |
|---|---|---|
| sampling-consistency family | external（adapted proxy） | **非原论文实现**。三变体均基于同一 25 个 temperature-0.7 采样的二值 answer 分布：Self-consistency（Wang et al. 2022）= 1 - 模态频率；SelfCheckGPT（Manakul et al. 2023）= answer-match 概率（**无原版 NLI/自校验管线**）；binary semantic entropy（Kuhn et al.）= yes/no 簇归一化熵（**无双向蕴含聚类**）。 |
| Raw sampled confidence | external（adapted proxy） | 1 - 平均采样置信度；方法无关的常见代理，非特定论文实现。 |
| Isotonic / Temperature confidence | external（adapted proxy） | pair-grouped 5-fold OOF 校准；标准校准家族的自适应实现，非特定论文复现。 |
| Single-agent intervention | external（实为内部消融） | 本项目自己的消融（5 personas -> 1 persona），标记为 external 仅为排序/叙述；非外部发表方法。 |
| R_sym / R_PI / Vote agreement / Frozen confidence | internal | 本项目内部 baseline（冻结公式见 phase0）。 |
| Reversal-only probe (5 calls) | internal（round-6 cost-curve） | 本项目探针（Agent B）：risk = 1 - 5-agent 自然反证平均 faithfulness；5 个边际 calls（含 5 个 original 共识 calls 共 10）；数值逐字取自 `round6/cost_curve/leaderboard_proposal.json`，未重算。 |

结论：leaderboard 中所有 external 行均为 **adapted proxies（二值/answer-match 变体）**，
不能读作原论文方法的复现数值；README §5 已加 adapted-proxy notice，§9 已加边界条目。
