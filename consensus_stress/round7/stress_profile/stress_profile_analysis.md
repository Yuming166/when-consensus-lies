# Round 7 融合点 A — 多轴压力响应轮廓（Agent W3，exploratory/post-hoc）

- 日期：2026-09-14
- 状态：**exploratory / post-hoc robustness analysis**（按 NAACL_Main_Revision_Autoresearch_Plan §16，
  全部统计为新增后验分析，不改变任何冻结协议数字）。
- 范围：零新增模型调用，纯冻结特征分析。回答四个问题：
  1. 移除轴反向签名是否在 600 项全 cohort（Qwen/Ling）成立（phase3 仅 120 对 Qwen 子集）；
  2. 多轴风险组合相对 RS_q/BF_q 是否有显著增量；
  3. "原答正确但反转下不变（镜像答错）"面板能否在 removal/λ 轴上与真正错误面板分开；
  4. 多轴轮廓是否值得进论文（见 decision.md）。
- 输入（只读；sha256）：
  `benchmark/frozen/vitaminc/preoutcome_features.jsonl`
  `d0c588d05211769c14234377d669881d079dacaac0ebaf2ec9326561d967584d`；
  `ling_preoutcome_features.jsonl`
  `35e853cf0815cb1428ec8f2ee671993bd1f87ba8b28ade24a630ac4c79bc26bb`；
  `labels_ledger.json` `770ede3f79b018c47aa982e6cb3f13b9d504b5c14950f7f1a8f6de196ffcbc5a`；
  λ 轴另读 `round3/records.jsonl` + `round3/records_phase3_lambda.jsonl`（Qwen 120-pair
  subset，均已冻结）。
- 方法：复用 `round3/analysis_lib.py` pair-grouped bootstrap（2000 重采样，自然对水平）。
  冻结 RS_q 复现用原 seed 基 `20260913`；**所有新增统计用独立 post-hoc seed 基
  `20260913+1000`**，见 scripts/stress_common.py。

## 0. 冻结特征与风险方向（round3/features.py，未修改）

| 轴 | 冻结特征 | 风险方向（越高越险） |
|---|---|---|
| natural reversal（反证） | `rev_flip_rate`（5 agent 翻转占比；`bf_reverse` 数值上等于它，599/600 项一致，1 项因单次 reverse 调用缺失） | `1 - rev_flip_rate`（反转刚性） |
| removal（证据移除） | `rem_flip_rate` | `rem_flip_rate`（移除不稳） |
| paraphrase（改写） | `para_flip_rate`（`bf_paraphrase = 1 - para_flip_rate`） | `para_flip_rate` |
| synthetic reverse | `synth_flip_rate` | `synth_flip_rate` |
| 冻结复合 | `BF_q = (bf_paraphrase + bf_reverse)/2`；`RS_q = -BF_q` | `RS_q` |

代数关系（与 round6/reducibility 一致）：`RS_q = -(1 - rev_flip_rate + para_flip_rate)/2`。

## 1. Task 1 — 移除轴反向签名（全 cohort 验证，post-hoc）

phase3（120-pair / 225-HC，仅 Qwen）发现：错误共识在**反转下更刚性**（`rev_flip_rate` 更低）、在**移除下更不稳**（`rem_flip_rate` 更高）。下表在 600 项全 cohort 与 HC 子集上复现（两模型）。

### 1.1 各轴 flip-rate 均值与正确−错误差（pair-grouped 95% CI）

| 模型 | 人群 | n(c/w) | 轴 | mean 正确 | mean 错误 | 差(正确−错误) [CI] |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5-4B | 全 600 | 524/76 | reversal `rev_flip_rate` | 0.8302 | 0.1342 | +0.696 [0.634, 0.756] |
| Qwen3.5-4B | 全 600 | 524/76 | removal `rem_flip_rate` | 0.5492 | 0.8053 | -0.256 [-0.311, -0.194] |
| Qwen3.5-4B | 全 600 | 524/76 | paraphrase `para_flip_rate` | 0.0260 | 0.1184 | -0.092 [-0.153, -0.044] |
| Qwen3.5-4B | HC | 502/65 | reversal `rev_flip_rate` | 0.8434 | 0.0954 | +0.748 [0.685, 0.808] |
| Qwen3.5-4B | HC | 502/65 | removal `rem_flip_rate` | 0.5522 | 0.8585 | -0.306 [-0.366, -0.240] |
| Qwen3.5-4B | HC | 502/65 | paraphrase `para_flip_rate` | 0.0163 | 0.1077 | -0.091 [-0.152, -0.039] |
| Ling-3.0-tiny | 全 600 | 473/127 | reversal `rev_flip_rate` | 0.6964 | 0.0472 | +0.649 [0.605, 0.695] |
| Ling-3.0-tiny | 全 600 | 473/127 | removal `rem_flip_rate` | 0.6211 | 0.8598 | -0.239 [-0.281, -0.197] |
| Ling-3.0-tiny | 全 600 | 473/127 | paraphrase `para_flip_rate` | 0.0444 | 0.1228 | -0.078 [-0.120, -0.039] |
| Ling-3.0-tiny | HC | 455/119 | reversal `rev_flip_rate` | 0.7029 | 0.0286 | +0.674 [0.629, 0.715] |
| Ling-3.0-tiny | HC | 455/119 | removal `rem_flip_rate` | 0.6281 | 0.8773 | -0.249 [-0.291, -0.206] |
| Ling-3.0-tiny | HC | 455/119 | paraphrase `para_flip_rate` | 0.0334 | 0.1126 | -0.079 [-0.122, -0.041] |

### 1.2 各轴风险表示单独 AUROC（HC 子集；风险方向如上）

| 模型 | 反转刚性 `1-rev` | 移除不稳 `rem` | 改写不稳 `para` | 合成反转 `synth` |
|---|---:|---:|---:|---:|
| Qwen3.5-4B | 0.931 [0.912, 0.947] | 0.646 [0.608, 0.684] | 0.599 [0.549, 0.656] | 0.573 [0.517, 0.630] |
| Ling-3.0-tiny | 0.869 [0.846, 0.891] | 0.614 [0.587, 0.641] | 0.581 [0.542, 0.620] | 0.604 [0.572, 0.633] |

**结论 1（全 cohort 复现成功）**：两个模型在 600 项全 cohort 与 HC 子集上都稳定复现 phase3 的反向签名：
- 反转刚性：正确共识 `rev_flip_rate` 显著高于错误（Qwen HC 差 +0.748 [+0.685, +0.808]；Ling HC +0.674 [+0.629, +0.715]；
  全 cohort 亦显著），即错误共识在反证下显著更刚性。
- 移除不稳：错误共识 `rem_flip_rate` 显著高于正确（Qwen HC 差 −0.306 [−0.366, −0.240]；Ling HC −0.249 [−0.291, −0.206]），
  即错误共识在证据移除下显著更不稳（与反转轴方向相反）。
- 方向自洽：反转刚性单独 AUROC 0.931/0.869，移除不稳单独 0.646/0.614，改写不稳 0.599/0.581——反转轴是主信号，移除轴是
  一个方向相反、独立但较弱的轴。
- phase3 的 120-pair 子集结论推广到全 cohort 且跨模型成立；本段为 post-hoc 验证，不改变冻结 gate 数字。

## 2. Task 2 — 多轴组合 vs RS_q / BF_q（HC 子集，post-hoc）

多轴风险表示（全部无标签、固定权重；`logistic_oof3` 为 pair-grouped 5-fold OOF 拟合上限诊断）：

| 表示 | 构造 |
|---|---|
| `risk_rev_rem` | `(1−rev) + rem`（反转刚性 + 移除不稳） |
| `risk_rev_rem_para` | `(1−rev) + rem + para`（三轴等权） |
| `risk_rsq_rem` | `RS_q + rem`（冻结复合上加移除轴，不稀释） |
| `risk_z3` | `z(1−rev)+z(rem)+z(para)`（HC 上 z-score 等权） |
| `risk_rem_para` | `rem + para`（仅非反转轴，参照） |
| `logistic_oof3` | 3 轴 OOF 逻辑回归（post-hoc 拟合上限） |

### 2.1 Qwen3.5-4B（HC n=567, pairs=298, wrong=65）

冻结复现：RS_q AUROC = **0.943 [0.924, 0.960]**，Risk@80 = **0.846 [0.638, 0.981]**。

| 表示 | AUROC [CI] | Risk@80 [CI] | ΔAUROC vs RS_q [CI] | ΔRisk@80 vs RS_q [CI] | ρ vs RS_q |
|---|---:|---:|---:|---:|---:|
| logistic_oof3 | 0.942 [0.922, 0.959] | 0.865 [0.656, 0.981] | -0.001 [-0.006, 0.004] | +0.019 [-0.039, 0.039] | 0.840 |
| risk_rem_para | 0.717 [0.683, 0.750] | 0.210 [-0.057, 0.410] | -0.226 [-0.257, -0.197] | -0.635 [-0.783, -0.516] | 0.347 |
| risk_rev_rem | 0.899 [0.870, 0.929] | 0.807 [0.484, 0.923] | -0.043 [-0.069, -0.020] | -0.039 [-0.194, 0.000] | 0.687 |
| risk_rev_rem_para | 0.921 [0.892, 0.948] | 0.827 [0.583, 0.961] | -0.022 [-0.038, -0.006] | -0.019 [-0.114, 0.019] | 0.722 |
| risk_rsq_rem | 0.891 [0.855, 0.926] | 0.807 [0.554, 0.905] | -0.052 [-0.084, -0.021] | -0.039 [-0.175, 0.000] | 0.669 |
| risk_z3 | 0.931 [0.906, 0.954] | 0.865 [0.599, 0.961] | -0.012 [-0.027, -0.000] | +0.019 [-0.078, 0.020] | 0.786 |

### 2.2 Ling-3.0-tiny（HC n=574, pairs=299, wrong=119）

冻结复现：RS_q AUROC = **0.896 [0.875, 0.917]**，Risk@80 = **0.422 [0.261, 0.587]**。

| 表示 | AUROC [CI] | Risk@80 [CI] | ΔAUROC vs RS_q [CI] | ΔRisk@80 vs RS_q [CI] | ρ vs RS_q |
|---|---:|---:|---:|---:|---:|
| logistic_oof3 | 0.891 [0.868, 0.912] | 0.412 [0.237, 0.569] | -0.005 [-0.013, 0.002] | -0.011 [-0.063, 0.021] | 0.930 |
| risk_rem_para | 0.681 [0.650, 0.714] | 0.138 [0.023, 0.317] | -0.215 [-0.244, -0.189] | -0.284 [-0.329, -0.190] | 0.477 |
| risk_rev_rem | 0.843 [0.818, 0.869] | 0.327 [0.187, 0.528] | -0.053 [-0.073, -0.033] | -0.095 [-0.126, -0.031] | 0.803 |
| risk_rev_rem_para | 0.873 [0.847, 0.896] | 0.390 [0.242, 0.574] | -0.024 [-0.038, -0.011] | -0.032 [-0.052, 0.011] | 0.868 |
| risk_rsq_rem | 0.848 [0.817, 0.877] | 0.390 [0.240, 0.570] | -0.048 [-0.075, -0.025] | -0.032 [-0.053, 0.011] | 0.797 |
| risk_z3 | 0.861 [0.832, 0.891] | 0.390 [0.245, 0.565] | -0.035 [-0.057, -0.016] | -0.032 [-0.063, 0.010] | 0.859 |

**结论 2（多轴组合无显著增量）**：
- **没有任何固定权重多轴组合在 AUROC 上显著超过 RS_q**。Qwen 所有组合 ΔAUROC ≤ 0 且 CI 上限 ≤ 0
  （最优 `risk_z3` −0.012 [−0.027, −0.000]；`risk_rev_rem_para` −0.022 [−0.038, −0.006]）；Ling 全部显著为负
  （`risk_rev_rem_para` −0.024 [−0.038, −0.011]）。加移除轴（`risk_rsq_rem`）反而显著降低 AUROC
  （Qwen −0.052 [−0.084, −0.021]；Ling −0.048 [−0.075, −0.025]）——移除轴在 RS_q 之后提供的是噪声而非信息。
- **拟合上限同样打平**：3 轴 OOF 逻辑回归 AUROC 与 RS_q 无显著差异（Qwen −0.001 [−0.006, +0.004]；
  Ling −0.005 [−0.013, +0.002]），说明不是固定权重选择问题，而是三轴集合本身不包含超过 RS_q 的增量信息。
- **Risk@80 无增量**：所有组合的 ΔRisk@80 CI 都含 0 或为负（Qwen 最优 `risk_z3` +0.019 [−0.078, +0.020]）。
- 判定：多轴轮廓相对冻结 RS_q/BF_q **不构成显著增量**；RS_q 已是该特征集合上的近似上限。

## 3. Task 3 — 假阳性分解：'正确共识在反转下也不变'（post-hoc）

审稿质疑：'正确共识也会不变'。我们挑出**原答正确但反转下不变（镜像答错）**的面板：
- `consensus-rigid`：`rev_flip_rate ≤ 0.4`（多数票在反转下保持不变）；
- `fully-rigid`：`rev_flip_rate = 0`（无任何 agent 翻转）。

### 3.1 刚性面板规模与 removal/para 轴行为（HC 子集）

| 模型 | 定义 | n 刚性 | 正确刚性 | 错误刚性 | 正确刚 rem | 错误刚 rem | 正确刚 para | 错误刚 para |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5-4B | consensus-rigid rev<=0.4 | 130 | 70 | 60 | 0.8286 | 0.8767 | 0.0229 | 0.1100 |
| Qwen3.5-4B | fully-rigid rev==0 | 92 | 46 | 46 | 0.9130 | 0.9130 | 0.0000 | 0.0174 |
| Ling-3.0-tiny | consensus-rigid rev<=0.4 | 243 | 124 | 119 | 0.8919 | 0.8773 | 0.0226 | 0.1126 |
| Ling-3.0-tiny | fully-rigid rev==0 | 204 | 102 | 102 | 0.9118 | 0.9118 | 0.0157 | 0.0588 |

### 3.2 分离 AUROC：能否把'正确刚性'与'真正错误刚性'分开（pair-grouped 95% CI）

| 模型 | 定义 | removal `rem` [CI] | paraphrase `para` [CI] | rem+para [CI] |
|---|---|---:|---:|---:|
| Qwen3.5-4B | consensus-rigid rev<=0.4 | 0.501 [0.441, 0.557] | 0.583 [0.521, 0.646] | 0.588 [0.536, 0.639] |
| Qwen3.5-4B | fully-rigid rev==0 | 0.500 [0.500, 0.500] | 0.533 [0.500, 0.576] | 0.512 [0.500, 0.533] |
| Ling-3.0-tiny | consensus-rigid rev<=0.4 | 0.461 [0.434, 0.487] | 0.604 [0.567, 0.642] | 0.567 [0.536, 0.601] |
| Ling-3.0-tiny | fully-rigid rev==0 | 0.500 [0.500, 0.500] | 0.558 [0.529, 0.588] | 0.550 [0.523, 0.579] |

### 3.3 λ 轴（Qwen phase3 120-pair 子集，HC）

**consensus-rigid**（正确 n=26 / 错误 n=22）：
- 移除应力面积（`removal_stress_area`）分离 AUROC = **0.624 [0.505, 0.754]**（n_c=26, n_w=22, pairs=26）；反转应力面积 = 0.400 [0.316, 0.467]。
- 移除 flip 曲线（λ=0,0.2,0.4,0.6,0.8,1）：正确刚性 [0.0, 0.1385, 0.2462, 0.3, 0.5308, 0.7231]；错误刚性 [0.0, 0.2114, 0.3273, 0.3705, 0.6205, 0.7727]。
- 反转 flip 曲线：正确刚性 [0.0, 0.0308, 0.0462, 0.0692, 0.1231, 0.1308]；错误刚性 [0.0, 0.0091, 0.0364, 0.0182, 0.0545, 0.0818]。

**fully-rigid**（正确 n=13 / 错误 n=13）：
- 移除应力面积（`removal_stress_area`）分离 AUROC = **0.565 [0.426, 0.704]**（n_c=13, n_w=13, pairs=13）；反转应力面积 = 0.500 [0.500, 0.500]。
- 移除 flip 曲线（λ=0,0.2,0.4,0.6,0.8,1）：正确刚性 [0.0, 0.1538, 0.3077, 0.2923, 0.5692, 0.7692]；错误刚性 [0.0, 0.2038, 0.2923, 0.3769, 0.6115, 0.7692]。
- 反转 flip 曲线：正确刚性 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]；错误刚性 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]。

**结论 3（诚实回答审稿质疑）**：
- **审稿质疑成立**：反转刚性轴确有不可忽略的假阳性——`consensus-rigid` 占全部 HC 的
  Qwen 70/567（12.3%）、Ling 124/574（21.6%），占**正确面板**的 70/502（13.9%）、124/455（27.3%）；
  `fully-rigid` 占正确面板 46/502（9.2%）、102/455（22.4%）。单一反转轴不能把这些'正确但不变'的
  面板与真正错误面板区分开，这是该轴的真实局限。
- **离散 removal 轴（λ=1 anchor）不能修复假阳性**：`rem_flip_rate` 分离 AUROC 在 Qwen 为 0.501
  [0.441, 0.557]（chance），Ling 为 0.461 [0.434, 0.487]（显著低于 chance，方向相反）；
  `fully-rigid` 两模型均为 0.500（分布完全相同，0.913 vs 0.913）。'正确刚性'与'错误刚性'在
  证据移除下都同样高度不稳（~0.91 flip），因此 **'移除不稳'不能作为刚性假阳性的补救轴**。
- **paraphrase 轴给出小而显著的部分分离**：`consensus-rigid` 下 Qwen 0.583 [0.521, 0.646]、
  Ling 0.604 [0.567, 0.642]（CI 下限 > 0.5）；`fully-rigid` 下更弱（0.533 [0.500, 0.576] /
  0.558 [0.529, 0.588]）。
- **连续 λ 移除曲线只有临界证据**（Qwen 子集，样本小）：`consensus-rigid` 下移除应力面积分离
  0.624 [0.505, 0.754]（CI 下限刚过 0.5）；`fully-rigid` 下 0.565 [0.426, 0.704]（不显著，n=13/13）。
  中间 λ（0.2–0.8）错误刚性面板的移除 flip 一致更高（如 λ=0.4：0.327 vs 0.246），但样本量不足以支撑强结论。
- 对论文的正确表述：把刚性信号定位为**有已知假阳性率的排序信号**（而非'只有错误共识不变'的机制声明），
  并附上本假阳性分解作为 post-hoc 诊断。

## 4. 复现与边界

- 脚本：`round7/stress_profile/scripts/`（`analyze_signature.py` / `analyze_multi_axis.py` /
  `analyze_false_positive.py` / `lambda_features.py` / `make_figures.py` / `render_report.py`）。
  复现：`/storage/gaoym/sp500-forecastability-lab/.venv/bin/python scripts/analyze_*.py`。
- seed：冻结 RS_q 复现用 `20260913`（与 round3 一致）；全部新增 post-hoc 统计用 `20260913+1000` 基
  （`stress_common.POSTHOC_BASE`），2000 次 pair-grouped 重采样。
- 输入哈希与输入文件见头部；未修改任何冻结协议/数字；新增统计一律标注 post-hoc。
- 边界：λ 轴数据仅 Qwen phase3 120-pair 子集（240 项，HC 225 项）；Ling 无 λ 网格数据。
  `rev_flip_rate` 与 `bf_reverse` 在 599/600 项一致（1 项单次 reverse 调用缺失，round3 已记录）。
- bootstrap 复现说明：冻结 RS_q 用原 seed 基复现，Qwen 0.943 [0.924, 0.960] 与 round3 一致；Ling 0.896
  [0.875, 0.917] 与 round6/reducibility 一致（paper v4 §4.7 的 [0.873, 0.916] 为另一 seed 的
  ±0.002 级 bootstrap 差异，不影响任何 gate 结论）。
- 图：`figures/axis_profile_scatter.png`（两模型 HC 的二维压力轮廓散点）、
  `figures/lambda_separation.png`（Qwen λ 子集按正确性分组的翻转曲线）。
