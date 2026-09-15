# Round 7 / W1 — Mirror-Equivalence Audit (P0-1)

- 日期：2026-09-14；Agent W1（P0 审计）。
- 状态：**post-hoc / exploratory robustness analysis**（§16 标签）。零新增模型调用，只读冻结数据。
- 输入（全部冻结，未修改）：
  - `consensus_stress/round3/selection_manifest.json`、`round3/paraphrase_manifest.json`
    （prompt 重建所需）、`round3/round3_lib.py`（冻结的 build_view/build_messages）。
  - `consensus_stress/benchmark/frozen/vitaminc/preoutcome_features.jsonl`（Qwen，sha256
    `d0c588d0…`）、`ling_preoutcome_features.jsonl`（Ling，`35e853cf…`）、
    `labels_ledger.json`（`770ede3f…`）、`records.jsonl`、`ling_records.jsonl`。
- 方法：pair-grouped bootstrap（2000 重采样、seed 基 `20260913` + 固定偏移，round5 规则），
  复用 `round3/analysis_lib.py` 约定。统计量均在 HC 子集（agreement ≥ 0.8；Qwen 567 items /
  298 pairs / 65 wrong；Ling 574 / 299 / 119 wrong）上计算。
- 复现：`consensus_stress/round7/audit/scripts/mirror_audit.py` → `mirror_audit.json`。

## 1. 形式化：什么是镜像等价

自然对 (i, j) 共享 claim C 与 distractor D，证据交换：
- 项 i：gold G_i、own evidence E_i、counter-evidence E_j；
- 镜像项 j：gold G_j = flip(G_i)、own evidence E_j、counter-evidence E_i。

冻结的 `unit_texts`/`build_view`/`build_messages`（`round3/round3_lib.py`）只使用
claim、persona、partition 与证据文本；`view.condition` 永不进入 prompt。因此对每个
agent a：

```
reverse(i) 的 view/messages ≡ original(j) 的 view/messages   (View Identity)
Y(i, reverse, a) = Y(j, original, a) =: y_j(a)               （T=0 确定性）
```

单次调用层（round6 `mirror_equivalence_analysis.md` Lemma 1）：

```
BF_reverse(i) = mean_a 1[y_j(a) == flip(y_i(a))]
```

即 **BF_reverse(i) 是配对项两个 original 答案 (y_i, y_j) 的确定性函数**，与
reverse 条件本身是否被调用无关；flip 是标签无关的运算符，gold 只通过“镜像 gold =
flip(G_i)”影响解读，不进入得分计算。

## 2. 逐字等价率（prompt 层，本地重建）

从冻结 manifest 重建全部 600 项 × 5 agent 的 prompt 字节：

| 量 | 结果 |
|---|---|
| unit_texts(reverse(i)) == unit_texts(original(j)) | 3000 / 3000（100%） |
| build_messages(reverse(i)) 与 original(j) 逐字节一致 | 3000 / 3000（100%） |

结论：reverse 条件与配对项 original 条件**逐字等价（100%）**，这是构造事实而非近似。

## 3. 答案一致率（密封 records 实测）

| 层 | Qwen3.5-4B | Ling-3.0-tiny |
|---|---|---|
| agent-call：Y(reverse(i),a)==Y(original(j),a) | 2998/2999 = **99.97%** | 2989/3000 = **99.63%** |
| item 级（5 agent 全同） | 598/599 = 99.83% | 590/600 = 98.33% |
| panel 共识级（reverse(i) 共识==original(j) 共识） | 599/599 = 100% | 599/600 = 99.83% |

残差（Qwen 1 次、Ling 11 次 agent-call）为 parse-repair / 模型侧非确定性路径，
不是协议差异（prompt 逐字相同，见 §2）。

## 4. BF_reverse 与配对项预测的相关（HC，pair-grouped Spearman [CI]）

| 配对 | Qwen rho [CI]（exact 率） | Ling rho [CI]（exact 率） |
|---|---:|---:|
| BF_reverse(i) vs BF_reverse(j) | **0.996 [0.986, 1.000]**（99.65%） | **0.995 [0.987, 1.000]**（97.39%） |
| BF_reverse(i) vs rev_flip_rate(j) | 0.994 [0.984, 1.000] | 0.995 [0.987, 1.000] |
| BF_reverse(i) vs RS_q(j) | **-0.975 [-0.986, -0.961]** | **-0.951 [-0.966, -0.932]** |
| RS_q(i) vs RS_q(j) | 0.955 [0.932, 0.976] | 0.915 [0.884, 0.941] |
| BF_reverse(i) vs agreement(j) | 0.369 [0.290, 0.451] | 0.093 [0.020, 0.169] |
| BF_reverse(i) vs bf_paraphrase(j) | 0.301 [0.224, 0.381] | 0.112 [0.037, 0.189] |
| BF_reverse(i) vs mean_confidence(j) | 0.234 [0.148, 0.319] | 0.006 [-0.077, 0.091] |

说明：冻结公式下 `bf_reverse` 与 `rev_flip_rate` 定义相同（都为“reverse 答案≠原答案”的
agent 占比），且对称于配对（flip 为对合），故 BF_reverse(i)≡BF_reverse(j)、
rev_flip_rate(i)≡rev_flip_rate(j) 几乎逐项成立（残差仅来自 §3 的 parse 例外）。
因此 BF_reverse 与“配对项预测”的相关接近 ±1 是**代数必然**，不是经验巧合。

## 5. 多少预测力可由配对项预测重建（HC，AUROC [CI]，风险方向）

| 预测器（预测 item i 的 consensus_wrong） | Qwen AUROC [CI] | Ling AUROC [CI] |
|---|---:|---:|
| 自身 RS_q(i) [参照] | 0.943 [0.922, 0.962] | 0.896 [0.876, 0.917] |
| 镜像项完整风险 RS_q(j)，只用镜像的调用 | **0.909 [0.886, 0.932]** | **0.827 [0.795, 0.856]** |
| 镜像 reverse 轴 rev_flip_rate(j)（风险方向） | 0.931 [0.912, 0.948] | 0.870 [0.845, 0.892] |
| 镜像 BF_reverse(j)（风险方向） | 0.931 [0.913, 0.948] | 0.870 [0.847, 0.892] |
| 镜像 bf_paraphrase(j) | 0.515 [0.479, 0.548] | 0.567 [0.543, 0.593] |
| 镜像 agreement(j) | 0.507 [0.462, 0.548] | 0.555 [0.532, 0.575] |

- **只用镜像项 j 的调用**（j 的 reverse 调用 = item i 的 original 调用）预测 item i 的
  错误，RS_q(j) 达 0.909/0.827，即自身 RS_q 的 96.4% / 92.2%。
- 配对项错误联合：Qwen both-wrong 仅 5/567、Ling 0/574；wrong(i) 并不蕴含 wrong(j)。
  重建不来自“镜像项也错”，而来自 reverse 轴本身是配对 original 答案的确定性函数
  （与标签无关）。
- 更极端的重建——只用两个 original 条件的面板答案、完全不用任何 reverse 调用——
  见 `s_pair_diagnostic.md`（S_pair 精确重建 reverse 轴，AUROC 0.931/0.869）。

## 6. 结论（镜像等价）

1. reverse(i) 与 original(j) 逐字等价（100%），答案一致率 99.97%/99.63%（agent-call），
   panel 共识级 100%/99.83%。
2. BF_reverse(i) 是配对 original 答案 (ŷ_i, ŷ_j) 与 flip 算子的**确定性 re-encoding**，
   不测量独立于配对结构的“证据响应能力”。BF_reverse(i)≡BF_reverse(j)、
   corr(BF_reverse(i), RS_q(j))≈-0.96/-0.95 均为代数/构造必然。
3. 配对项预测可重建：只用镜像调用重建 96.4%/92.2% 的 RS_q AUROC（0.909/0.827 vs
   0.943/0.896）；只用配对 original 答案（S_pair，见 companion 文档）重建 100% 的
   reverse 轴、约 98.7%/97.0% 的 RS_q AUROC。
4. 与 round6/reframing/mirror_equivalence_analysis.md 一致：reverse 轴是
   “标签对齐的 re-encoding”，非独立探针。此处补充了逐字等价率、答案一致率、相关与
   重建量的量化（全部为新导出，不改任何冻结数字）。

### 边界
- 所有数字为冻结数据上的新导出；参照值（0.943/0.896 等）仅复述，未修改。
- 分析仅适用于 natural-reversal 轴（VitaminC）。BoolQ 的 negation-prefix reverse 不是
  镜像项，在本等价之外（round3/analysis/boolq_crossdataset.md）。
