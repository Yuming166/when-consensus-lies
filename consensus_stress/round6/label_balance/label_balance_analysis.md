# Label Balance & Error Quality — SUPPORTS vs REFUTES（Agent E, round6）

协议：`score4-upgrade-20260914` → Agent E。只读冻结数据，零新增模型调用。
输入：`benchmark/frozen/vitaminc/preoutcome_features.jsonl`（Qwen，与 round3 哈希一致）、
`benchmark/frozen/vitaminc/ling_preoutcome_features.jsonl`（Ling，与 round4 哈希一致）、
`benchmark/frozen/vitaminc/labels_ledger.json`；对照 `round3/analysis/analysis.md`。

回答审稿人攻击点：**“信号主要由 REFUTES 承载、SUPPORTS 仅 7 个错误”**。
本报告所有新统计量均为 post-hoc 边界/敏感性分析；冻结 Gate 数字（G2/G3/G4 等）不改动，
仅在下方标注。复现：`scripts/label_balance_analysis.py`（含 seed 规则）。

## 0. 一页结论（Key numbers）

| 量 | Qwen3.5-4B | Ling-3.0-tiny |
|---|---|---|
| HC 项 / 错误数 | 567 / 65（11.5%） | 574 / 119（20.7%） |
| SUPPORTS 错误率 | **7 / 283 = 2.5%**（Wilson CI [1.2%, 5.0%]） | 13 / 296 = 4.4%（[2.6%, 7.4%]） |
| REFUTES 错误率 | 58 / 284 = 20.4%（[16.1%, 25.5%]） | 106 / 278 = 38.1%（[32.6%, 44.0%]） |
| 错误率比 REFUTES/SUPPORTS | 8.3× | 8.7× |
| REFUTES 错误质量占比 | 58/65 = 89.2% | 106/119 = 89.1% |
| pooled AUROC(RS_q) | 0.943 [0.924, 0.960]（冻结） | 0.896 [0.873, 0.916]（round4） |
| SUPPORTS AUROC | 0.917 [0.819, 0.999] | 0.881 [0.834, 0.928] |
| REFUTES AUROC | 0.986 [0.973, 0.995] | 0.957 [0.934, 0.977] |
| SUPPORTS−REFUTES AUROC 差 | −0.069 [−0.169, +0.007]（CI 含 0） | −0.076 [−0.133, −0.021]（CI 排 0） |
| 匹配诊断 pooled AUROC（post-hoc） | ≈0.919 [0.903, 0.935] | ≈0.875 [0.863, 0.887] |
| SUPPORTS LOO jackknife AUROC | [0.903, 0.944]，全部 >0.8 | [0.872, 0.886]，全部 >0.8 |

三条主线结论：

1. **信号在两个 label 内都成立**：SUPPORTS 与 REFUTES 的分 label AUROC 均显著高于 0.5
   （Qwen 0.917/0.986，Ling 0.881/0.957；Mann-Whitney 单侧 p 均 < 1e-5）。SUPPORTS 的
   7 个错误不是噪声：7/7 落在该 label 内风险最高 27%，5/7 落在最高 11%。
2. **pooled 数字确实由 REFUTES 承载**：REFUTES 错误质量占 89.2%（Qwen）/ 89.1%（Ling），
   与 pooled AUROC 的 concordance 归因份额 89.3% / 88.9% 几乎一致——份额≈错误占比，
   并非不成比例地放大。
3. **但信号不是不平衡的伪影**：把两侧错误数匹配（SUPPORTS 上匹配到 REFUTES 的 58 个
   错误，或双侧都匹配到 7 个错误）后，pooled AUROC 仍为 ≈0.92（Qwen）/ 0.875（Ling），
   CI 下界远高于 0.5。即“0.943 是否被 REFUTES 抬升”的回答是：部分抬升（pooled 0.943 vs
   匹配后 0.92），但抬升来自 REFUTES 错误本身极强的可排序性（0.986），不是标签不平衡
   的统计伪影。

## 1. 数据与复现校验

- Qwen 特征 = round3 `preoutcome_features.jsonl`（sha256 `d0c588d0…`，与 frozen 一致）。
- Ling 特征 = round4 `ling_preoutcome_features.jsonl`（sha256 `35e853cf…`，与 frozen 一致）。
- 标签仅来自 `labels_ledger.json`（600 项，300 SUPPORTS + 300 REFUTES 构造对称）。
- 复现校验：pooled AUROC（Qwen 0.9429 [0.9239, 0.9602]；Ling 0.8964 [0.8734, 0.9165]）、
  pooled Risk@80（Qwen 0.8460 [0.6357, 0.9808]；Ling 0.4220 [0.2743, 0.5910]）、
  分 label AUROC 与 round3/round4 冻结数字逐一吻合（差异 < 1e-4）。

Seed 规则（脚本内注释为证）：
- 分 label AUROC 复现用历史 seed：Qwen `20260913`（round3 analyze.py）、
  Ling `20260913+402`（round4 SEED+2）。
- round6 新增统计统一用 `20260913+600`（Agent E 块）+ 每统计量固定偏移
  （Risk@80 +10，label-diff +20，匹配诊断 +30/+31），2000 replicates，pair-grouped。

## 2. Task 1 — 分 label 的 AUROC / Risk@80（pair-grouped CI）

`RS_q = -BF_q`，越高越风险。分 label 子集 = 该 label 的 HC 项（pair-grouped bootstrap）。

### Qwen3.5-4B（567 HC）

| label | n | 错误 n（率） | AUROC [95% CI] | Risk@80 [95% CI]（label 内） | label 内保留 80% 后绝对错误率 |
|---|---|---|---|---|---|
| SUPPORTS | 283 | 7（2.5%） | 0.917 [0.819, 0.999] | 0.642 [0.165, 1.000] | ≈0.9% |
| REFUTES | 284 | 58（20.4%） | 0.986 [0.973, 0.995] | 0.871 [0.687, 0.976] | ≈2.6% |
| pooled | 567 | 65（11.5%） | 0.943 [0.924, 0.960]（冻结 G2） | 0.846 [0.638, 0.981]（冻结） | — |

### Ling-3.0-tiny（574 HC）

| label | n | 错误 n（率） | AUROC [95% CI] | Risk@80 [95% CI]（label 内） | label 内保留 80% 后绝对错误率 |
|---|---|---|---|---|---|
| SUPPORTS | 296 | 13（4.4%） | 0.881 [0.834, 0.928] | 0.807 [0.283, 0.904] | ≈0.8% |
| REFUTES | 278 | 106（38.1%） | 0.957 [0.934, 0.977] | 0.338 [0.253, 0.432] | ≈25.2% |
| pooled | 574 | 119（20.7%） | 0.896 [0.873, 0.916]（round4） | 0.422 [0.274, 0.591]（round4） | — |

阅读注意（必须写进论文）：

- 分 label Risk@80 是 **label 内相对降幅**，跨 label 直接比较会混淆基线错误率差异：
  Qwen REFUTES 0.871 高于 SUPPORTS 0.642，是因为 REFUTES 基线 20.4% 有更多可“砍”的错误；
  Ling 反之（SUPPORTS 0.807 > REFUTES 0.338）也是基线差异（4.4% vs 38.1%）所致。
  绝对口径（保留 80% 后错误率）更可读：两模型 SUPPORTS 都压到 ≈1%，Qwen REFUTES 2.6%，
  Ling REFUTES 仍 25.2%（Ling 的 REFUTES 错误即使低风险区也很顽固）。
- 分 label AUROC 差异（SUPPORTS − REFUTES，same-pair bootstrap）：Qwen −0.069
  [−0.169, +0.007]（95% CI 含 0，**不能声称 Qwen SUPPORTS 显著更差**，只是数值最差）；
  Ling −0.076 [−0.133, −0.021]（CI 排 0，Ling SUPPORTS 显著更差）。
- “worst label = SUPPORTS”在两个模型中都成立于**点估计**层面；G4（worst-label CI
  lb > 0.5）在两模型均通过（Qwen 0.819，Ling 0.834）。

## 3. Task 2 — 错误率匹配与信号归因（诊断性 / 敏感性，**不是正式 gate**）

本节全部为 post-hoc 诊断：不改冻结协议、不用于任何 gate 判定、不重新定义主指标。

### 3.1 精确归因：concordance 份额（无重采样，精确）

pooled AUROC 的分子 = 所有 (错误项, 正确项) 对的 concordant mass，可按错误项所在
label 可加分解（脚本 `auROC_concordance`，与 pooled AUROC 精确一致，差 < 1e-9）。

| 模型 | SUPPORTS-wrong 份额 | REFUTES-wrong 份额 | 错误质量占比（REFUTES） |
|---|---|---|---|
| Qwen | 10.7% | **89.3%** | 89.2% |
| Ling | 11.1% | **88.9%** | 89.1% |

结论：**pooled AUROC 的排序信息约 89% 由 REFUTES 错误承载，且份额几乎等于其错误质量
占比（89%），并未被不成比例地放大。** 换句话说，审稿人“信号主要由 REFUTES 承载”在
描述层面成立，且机制是透明的：REFUTES 错误多（8.3–8.7×）且可排序性强。

### 3.2 匹配诊断：错误数匹配后的 pooled AUROC（bootstrap，post-hoc）

两种反事实（2000 replicates，pair-grouped，seed 20260913+600+30/31）：

- **Up（把 SUPPORTS 匹配到 REFUTES 的错误数）**：Qwen 双侧各 58 错误 → pooled AUROC
  **0.919 [0.903, 0.935]**；Ling 双侧各 106 → **0.875 [0.863, 0.887]**。
- **Down（双侧都匹配到 SUPPORTS 的错误数）**：Qwen 双侧各 7 → **0.920 [0.868, 0.958]**；
  Ling 双侧各 13 → **0.875 [0.842, 0.909]**。

解释（边界诚实）：

- 即使把两侧错误数强行拉平（上匹配或下匹配），pooled AUROC 仍 ≈0.92（Qwen）/
  ≈0.875（Ling），CI 下界 ≥0.84。**信号不是“REFUTES 错误数量多”这一不平衡造成的伪影**；
  分 label AUROC 本身就同时 >0.88。
- 但 matched-up 的 0.919 明显低于冻结 pooled 0.943（差 ≈0.024，Qwen）：0.943 的部分
  水平来自 REFUTES 那 58 个错误近乎完美的排序（分 label 0.986）。因此论文应把
  **分 label 视角作为主报告口径**，pooled 0.943 定位为“REFUTES 主导错误质量下的综合值”。

### 3.3 “信号由 REFUTES 驱动多少”的量化表述（供论文使用）

> REFUTES items carry 89% of the HC error mass (Qwen 58/65; Ling 106/119) and 89% of the
> pooled AUROC concordant mass. Per-label AUROC remains high in both labels (Qwen
> SUPPORTS 0.917 [0.819,0.999] vs REFUTES 0.986 [0.973,0.995]; Ling 0.881 [0.834,0.928] vs
> 0.957 [0.934,0.977]), and diagnostic error-count-matched pooling (both labels matched to
> 7 / 58 errors per label) keeps pooled AUROC ≈0.92 / 0.875 with 95% CI lower bounds
> ≥0.84. The pooled estimate is therefore REFUTES-dominated by composition, but the
> ordering signal is present and strong within each label and is not an artifact of label
> imbalance.

## 4. Task 3 — SUPPORTS 仅 7 个错误对 worst-label 结论的稳健性

### 4.1 leave-one-out（jackknife）分 label AUROC

对每个 label 的 HC 项逐一剔除重算 AUROC（Qwen SUPPORTS 283 次 / Ling 296 次）：

| 模型 | label | full AUROC | LOO 范围 | 全部 >0.5 / >0.8 |
|---|---|---|---|---|
| Qwen | SUPPORTS | 0.917 | **[0.903, 0.944]** | 是 / 是 |
| Qwen | REFUTES | 0.986 | [0.985, 0.986] | 是 / 是 |
| Ling | SUPPORTS | 0.881 | **[0.872, 0.886]** | 是 / 是 |
| Ling | REFUTES | 0.957 | [0.955, 0.958] | 是 / 是 |

任何单个 SUPPORTS 错误（或单个正确项）都无法把 SUPPORTS AUROC 拉到 0.8 以下：
**worst-label 结论不是“一个错误撑起来的”。**

### 4.2 窄样本下的支撑证据

- SUPPORTS 7 个错误的 risk 百分位（Qwen）：73.9 / 74.9 / 89.1 / 98.2 / 98.9 / 99.7 / 100
  —— 7/7 落在该 label 风险最高 27%，5/7 在最高 11%；Ling 13 个错误平均百分位 89.4%，
  最低 68.2%。**错误一致地处于高风险区，不是随机散布。**
- Mann-Whitney（单侧 greater，ties 正态近似）：Qwen SUPPORTS p≈3.7e-6（7 正/276 负）；
  Ling SUPPORTS p≈3.5e-7（13 正/283 负）。即便只有 7 个正样本，SUPPORTS 内排序
  “错误风险更高”也不可能是随机。
- 窄 CI 讨论：Qwen SUPPORTS 的 CI 宽度 0.18（[0.819, 0.999]）远大于 REFUTES 的 0.022，
  故 0.917 的**点估计精度低**；门控只看 CI 下界（>0.5），两模型均通过。Wilson CI 显示
  SUPPORTS 真实错误率可能在 1.2%–5.0%（Qwen），即“7 个错误”本身也只是小样本估计。

### 4.3 可直接放入 limitation 的段落（EN，配中文注释）

> **Small positive counts for the SUPPORTS label.** The construction is label-symmetric
> (300 SUPPORTS + 300 REFUTES items, one per pair, identical evidence views), but model
> error rates are strongly asymmetric: only 7/283 (2.5%) of Qwen HC SUPPORTS items are
> wrong versus 58/284 (20.4%) of REFUTES items (Ling: 13/296 = 4.4% vs 106/278 = 38.1%).
> Consequently the pooled AUROC (0.943 Qwen; 0.896 Ling) reflects a cohort in which ~89%
> of errors are REFUTES, and ~89% of the pooled AUROC concordant mass is carried by
> REFUTES-wrong items. Three checks bound this threat: (i) per-label AUROC is significantly
> above 0.5 in both labels for both models (SUPPORTS 0.917 [0.819,0.999] Qwen and 0.881
> [0.834,0.928] Ling; REFUTES 0.986 and 0.957), with SUPPORTS leave-one-error-out AUROC in
> [0.903, 0.944] / [0.872, 0.886]; (ii) diagnostic error-count-matched pooling, which is a
> post-hoc sensitivity analysis rather than a gate, keeps pooled AUROC ≈0.92 (Qwen) and
> ≈0.875 (Ling) with CI lower bounds ≥0.84; (iii) the SUPPORTS point estimate has low
> precision (7 positives; CI width 0.18), so we report the worst-label result at the
> confidence-interval level (both CI lower bounds > 0.5) and do not claim that SUPPORTS is
> *significantly* harder than REFUTES for Qwen (difference CI includes 0; for Ling the
> difference CI excludes 0).

## 5. Task 4 — “label-symmetric 构造”应如何措辞

**构造对称 ≠ 错误率对称。** 论文中关于标签平衡的措辞建议（三层）：

1. **构造层（不变）**：CST-Bench 的构造是 label-symmetric——每对自然项生成一个
   SUPPORTS 项与一个 REFUTES 项（600 项 = 300+300），二者共享同一证据视图、同一提示
   模板、同一 oracle，仅镜像证据结论。这保证两个 label 在**样本量与暴露度**上对称。
2. **行为层（发现）**：模型在两 label 上的错误率高度不对称（Qwen 2.5% vs 20.4%，
   Ling 4.4% vs 38.1%，比率 8.3–8.7×），且跨两个模型家族一致。这是**关于模型行为的
   实证发现**（支持性共识比反驳性共识可靠得多；或证据方向影响可靠性），不是构造缺陷。
3. **报告层（口径）**：由于错误质量约 89% 落在 REFUTES，pooled 指标本质上是
   “REFUTES 主导错误质量下的综合值”。因此论文应：(a) 主报告分 label 的 AUROC/Risk@80；
   (b) pooled 数字标注 REFUTES 错误占比与 concordance 份额；(c) 把错误率匹配分析标为
   post-hoc 敏感性分析；(d) 不因 SUPPORTS 点估计最低就声称其“显著更难”（Qwen 差异 CI
   含 0）。措辞示例：

> “CST-Bench is label-symmetric by construction, but label-symmetric construction does
> not imply label-symmetric error rates: both models err 8–9× more often on REFUTES than
> on SUPPORTS items. We therefore report label-stratified AUROC/Risk@80 as the primary
> view; pooled estimates are REFUTES-dominated by error composition (≈89% of errors and
> ≈89% of AUROC concordant mass) and are presented with this composition stated.”

## 6. 结论与边界清单

| # | 结论 | 证据 | 边界 |
|---|---|---|---|
| E1 | 两 label 内信号均成立且显著 | 分 label AUROC 0.917/0.986（Qwen）、0.881/0.957（Ling），CI lb>0.5，MW p<1e-5 | SUPPORTS 点估计精度低（7/13 个正样本） |
| E2 | pooled 指标由 REFUTES 承载 | 错误质量 89.1–89.2%；concordance 份额 88.9–89.3% | 份额≈错误占比，非不成比例 |
| E3 | 信号不是不平衡伪影 | 错误数匹配后 pooled AUROC ≈0.92 / 0.875，CI lb ≥0.84 | post-hoc 诊断，非 gate |
| E4 | worst-label（SUPPORTS）结论稳健 | LOO [0.903,0.944]（Qwen）/ [0.872,0.886]（Ling），7/7 错误在 label 内风险最高 27% | Qwen SUPPORTS vs REFUTES 差异 CI 含 0，只能称“数值最差” |
| E5 | 构造对称 ≠ 错误率对称 | 构造 300+300；错误率 8.3–8.7× 不对称且跨模型一致 | 是行为发现，非构造缺陷；措辞见 §5 |

未做的（如实）：零新增模型调用；未改动冻结协议与 Gate；未把匹配分析包装成正式结果；
未对其他目录写入（除 registry.yaml 中 Agent E 状态更新与 round6/label_balance/ 产物）。

## 7. 复现

- 脚本：`scripts/label_balance_analysis.py`（`python3 scripts/label_balance_analysis.py`，
  约 24 s，输出 `label_balance_analysis_results.json`）。
- 依赖：numpy；scipy（仅 §4.2 的 Mann-Whitney p 值，脚本本体不依赖）。
- 附加：`mannwhitney_pvalues.json`（MW 单侧 p 值，post-hoc 支撑证据）。
- Seed：复现历史数字用 round3/round4 原 seed；新增统计用 20260913+600 块（见 §1）。
