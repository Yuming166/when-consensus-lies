# Round 7 / W1 — 配对预测基线 S_pair 诊断（P0-2）

- 日期：2026-09-14；Agent W1（P0 审计）。
- 状态：**post-hoc / exploratory robustness analysis**（§16 标签）。零新增模型调用，只读冻结数据。
- 输入：`benchmark/frozen/vitaminc/preoutcome_features.jsonl`（Qwen）、
  `ling_preoutcome_features.jsonl`（Ling）、`labels_ledger.json`（合并仅发生在特征冻结后）。
- 方法：pair-grouped bootstrap 2000 重采样、seed 基 `20260913` + 固定偏移（round5 规则，
  复用 `round3/analysis_lib.py` 约定）；HC 子集（Qwen 567/298 pairs/65 wrong；Ling 574/299/119 wrong）。
- 复现：`consensus_stress/round7/audit/scripts/s_pair_diagnostic.py` → `s_pair_results.json`。

## 1. S_pair 定义（只用配对项的 original 条件答案；无 reverse 调用、无 paraphrase、无标签）

标签约定：gold SUPPORTS→yes、REFUTES→no；reverse 轴的 oracle 为 flip(y0)。在此约定下
“镜像答案==flip(原答)”是 label 一致的配对统计量，“镜像答案==原答”是其信息等价形式
（二值答案下互为补事件）。

设 ŷ_i = 项 i 的 original 条件面板答案（_agent_answers），ŷ_j = 镜像项 j 的 original
答案（同一 pair_id、另一 item_id；取全部 600 项的答案，不限于 HC）：

| 统计量 | 定义 | 语义 |
|---|---|---|
| s_pair_flip(i) | mean_a 1[ŷ_j(a) == flip(ŷ_i(a))] | 镜像答案==flip(原答)；由 View Identity 等于 BF_reverse(i) |
| s_pair_same(i) | mean_a 1[ŷ_j(a) == ŷ_i(a)] | 面板在镜像项上的答案==原项答案（agent 级）= 1 − rev_flip_rate |
| s_pair_panel(i) | 1[consensus_j == consensus_i] | 面板级：镜像项共识==原项共识 |

所有变体在计算时**不触碰 reverse 条件记录**，仅使用冻结的 `_agent_answers`。

## 2. AUROC [CI]（风险方向：值越大越像错误；与 RS_q = -BF_q 同向）

| 特征 | Qwen AUROC [CI] | Ling AUROC [CI] |
|---|---:|---:|
| **RS_q**（risk_bf_q，参照） | **0.943 [0.924, 0.960]** | **0.896 [0.873, 0.917]** |
| **BF_reverse（风险方向，参照）** | **0.931 [0.913, 0.948]** | **0.869 [0.846, 0.891]** |
| **S_pair_flip（风险方向）** | **0.931 [0.912, 0.948]** | **0.869 [0.846, 0.891]** |
| **S_pair_same（原方向即风险向）** | **0.931 [0.912, 0.948]** | **0.869 [0.846, 0.891]** |
| S_pair_panel（原方向即风险向） | 0.893 [0.847, 0.932] | 0.863 [0.838, 0.884] |

配对差（pair-grouped bootstrap，风险方向）：

| 配对差 | Qwen [CI] | Ling [CI] |
|---|---:|---:|
| S_pair_flip − BF_reverse | -0.0000 [-0.0002, 0.0000] | -0.0002 [-0.0009, 0.0003] |
| RS_q − S_pair_flip | +0.0122 [0.0022, 0.0228] | +0.0272 [0.0137, 0.0422] |
| RS_q − S_pair_same | +0.0122 [0.0019, 0.0229] | +0.0272 [0.0132, 0.0418] |
| RS_q − S_pair_panel | +0.0501 [0.0214, 0.0824] | +0.0338 [0.0184, 0.0498] |
| RS_q − BF_reverse | +0.0121 [0.0018, 0.0226] | +0.0270 [0.0130, 0.0424] |

其他证据：

- Spearman(S_pair_flip, BF_reverse) = 0.998 [0.993, 1.000]（Qwen）/ 0.998 [0.994, 1.000]（Ling）。
- 逐项相等：s_pair_flip == bf_reverse 在 99.82%（Qwen）/ 98.43%（Ling）HC 项上**逐项相等**；
  s_pair_flip == rev_flip_rate 在 99.65% / 98.43% 上相等（残差即 §3 的 parse 例外）。
- 参照一致：BF_reverse 风险方向 0.931/0.869 与 reducibility 报告的 reverse 轴
  （0.931 [0.913, 0.947] / 0.869 [0.846, 0.891]）一致；RS_q − S_pair 残差 0.012/0.027
  与 reducibility 报告的 RS_q − reverse 轴配对差（0.012 [0.002, 0.022] / 0.027 [0.013, 0.042]）
  一致。

## 3. 诚实结论：S_pair 能否重建 RS_q 的预测力？

**能——且几乎完全重建。**

1. S_pair（只用配对项两个 original 答案、不用任何 reverse 调用、不用标签）与 BF_reverse
   逐项相等（99.8%/98.4%），Spearman 0.998，配对 AUROC 差 0.0000/0.0002：**S_pair 精确重建
   reverse 轴**（0.931/0.869）。原因是 View Identity：reverse(i) 的答案就是 original(j) 的答案，
   所以“镜像答案==flip(原答)”就是 BF_reverse 的免 reverse 版实现。
2. RS_q 的预测力几乎全部由 reverse 轴承载（reducibility：reverse 轴 0.931/0.869 占 RS_q
   0.943/0.896 的绝大部分；残差增量 AUROC 0.284/0.317 < 0.5 且 CI 排除 0.5，方向反）。
   S_pair 因此重建 RS_q 的 **~98.7%（Qwen，0.931/0.943）/ ~97.0%（Ling，0.869/0.896）**。
3. RS_q 相对 S_pair 的唯一残余是 paraphrase 轴的小增量：配对差 +0.012/+0.027（CI 排除 0，
   统计显著但很小）；paraphrase 轴单独 AUROC 仅 0.60/0.58（弱）。该增量不是镜像结构带来的，
   但它本身也很弱，不足以支撑“反证响应能力是独立强信号”的叙述。
4. **推论（如实写）**：主信号的绝大部分预测力是自然对构造的机械结果——
   由配对项的 original 答案即可重建，reverse 条件没有提供独立于配对结构的测量。
   在此结论下，**独立反证实验（W2，NAACL 计划 §3）是唯一出路**：只有构造
   “非逐字镜像、决策相关、不暴露标签”的独立 counter-evidence 包，才能证明模型
   “对决策相关的反证选择性响应”超越配对机制。若 W2 不成立，论文主贡献只能按
   round6 降级路径表述（CST-Bench + 冻结复现 + 简洁信号，机制上只写
   “错误共识在自然反证轴上的行为模式”，不写独立“证据敏感性”机制）。

### 边界
- S_pair 计算为 post-hoc 审计量（§16 标签），不是预注册门。
- S_pair 使用配对项答案意味着它只能在“有自然配对”的基准上定义；这不否定它在
  CST-Bench 上作为事前可计算特征的可用性，但明确其信息来自配对结构。
- 面板级变体（S_pair_panel）信息量更低（0.893/0.863），agent 级变体是更合理的统计量。
