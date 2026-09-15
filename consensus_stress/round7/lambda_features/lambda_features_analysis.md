# Round 7 / W4（融合点 B）— λ 连续压力曲线特征的可归约性分析

- 日期：2026-09-14
- 范围：**frozen phase-3 子集（120 对 / 240 条 item，全部标注 post-hoc）**；Qwen3.5-4B 主分析，
  Ling-3.0-tiny 边界见 §4.5。
- 状态：**exploratory / post-hoc robustness analysis**（`NAACL_Main_Revision_Autoresearch_Plan.md`
  §16）。零新增模型调用；不修改任何冻结数字/协议；不 git commit。
- 方法来源：round-3 `phase3_analyze.py`（冻结特征构造，与 `round3/analysis/phase3_results.json`
  逐位一致）+ round-6 `round6/reducibility/analyze_reducibility.py`（增量 AUROC：label-free OLS
  残差化、pair-grouped bootstrap 2000、seed 基 `20260913` + 独立偏移）。

## 1. 输入与冻结来源（sha256）

| 文件 | 用途 | sha256（前 16 位） |
|---|---|---|
| `round3/records_phase3_lambda.jsonl` | 9,600 条 λ 记录（reversal/removal × 4 λ） | `28f7febf71d81ead` |
| `round3/records.jsonl` | original 答案 + reverse/remove λ=1 锚点 | `ce5280ede80c92f4` |
| `round3/preoutcome_features.jsonl` | 二元轴/RS_q/R_sym 等冻结特征 | `d0c588d05211769c` |
| `round3/labels_ledger.json` | gold label | `770ede3f79b018c4` |
| `benchmark/frozen/vitaminc/ling_preoutcome_features.jsonl` | Ling 冻结特征（仅离散轴） | `35e853cf0815cb14` |

## 2. 方法与口径

- **子集口径**：phase-3 冻结子集 120 对 = 240 items（hash 选取，outcome-free）。HC 子集
  （agreement ≥ 0.8）：Qwen **225 items / 119 pairs / 203 correct / 22 wrong**。
  所有增量 AUROC 均在此 225-item 口径上，**不冒充全 cohort**（全 cohort 见 round-6，567/574 items）。
- **压力特征（reversal 主，removal 副）**，逐位复刻 `phase3_analyze.py`：
  - `stress_area`：flip-prob(λ) 在网格 {0, 0.2, 0.4, 0.6, 0.8, 1.0} 上的梯形积分；
    λ=0 锚 = 0，λ=1 锚 = 主记录 reverse/remove 的平均 flip（= `rev_flip_rate`/`rem_flip_rate`）。
  - `breakpoint`：consensus（多数票）首次翻转的最小 λ，永不翻 = None。
  - `robustness_radius`：breakpoint 的 None→1.0 编码。
  - 风险方向：reversal 轴 `risk = -stress_area`（higher = riskier）；breakpoint/radius 直接
    用作 risk（never-flip=1.0 = 最 rigid = 最 risk）。
- **增量 AUROC**：对每个基线 B，用不含标签的 OLS 将压力特征对 B 残差化（每个 bootstrap 复样内
  重新拟合），残差对 `consensus_wrong` 的 AUROC。若 CI 下限 > 0.5 → 保留显著增量；否则可归约。
  同时给 pair-grouped 配对差（AUROC 差）与 Spearman。
- **验证**：重建的 reversal stress-area AUROC = 0.9485 [0.9252, 0.9683]，与冻结
  `phase3_results.json` 完全一致（n=225, n_groups=119）。

## 3. 结果（Qwen，225-item HC 子集）

### 3.1 各特征 plain AUROC（risk 方向）

| 特征 | AUROC [95% CI] |
|---|---:|
| reversal stress-area（RS_stress = -area；冻结 gate） | 0.948 [0.925, 0.969] |
| reversal breakpoint（never-flip=1.0） | 0.924 [0.897, 0.948] |
| reversal robustness radius（=1.0 永不翻） | 0.924 [0.895, 0.948] |
| removal stress-area（描述性） | 0.319 [0.234, 0.401] |
| removal breakpoint（描述性） | 0.324 [0.212, 0.437] |
| removal robustness radius（描述性） | 0.324 [0.213, 0.431] |

参照基线（同子集）：
- **二元 reverse 轴（`rev_flip_rate`，risk = -rev_flip_rate）**：0.946 [0.922, 0.967]
- **RS_q / BF_q（risk = -bf_q）**：0.966 [0.942, 0.985]
- R_sym（参照）：0.901 [0.857, 0.939]

> 关键观察：reversal stress-area 的 plain AUROC（0.948）与二元 reverse 轴（0.946）几乎相同；
> 而 stress-area 的 λ=1 端点**按构造就是 rev_flip_rate**。二者的差异只可能来自曲线内部形状。

### 3.2 相对"二元 reverse 轴（rev_flip_rate）"的增量

| 压力特征 | 残差增量 AUROC [CI] | 配对差（压力−轴）[CI] | Spearman [CI] |
|---|---:|---:|---:|
| reversal stress-area | 0.476 [0.429, 0.653] | +0.003 [−0.001, +0.009] | 0.743 [0.632, 0.821] |
| reversal breakpoint | 0.539 [0.388, 0.593] | −0.022 [−0.038, −0.009] | 0.677 [0.553, 0.767] |
| reversal robustness radius | 0.539 [0.391, 0.591] | −0.022 [−0.038, −0.009] | 0.677 [0.559, 0.772] |
| removal stress-area（描述性） | 0.508 [0.447, 0.550] | −0.627 [−0.721, −0.540] | −0.220 [−0.330, −0.112] |

- reversal stress-area 相对 rev_flip_rate 的残差增量 AUROC **点估计 ≤ 0.5（0.476）**，CI
  [0.429, 0.653] 含 0.5 → **曲线内部形状无显著增量**；配对差 +0.003（CI 含 0，下界 −0.001）→
  与二元轴在预测力上不可区分。
- breakpoint / robustness radius：增量 CI 均含 0.5，配对差显著为负 → 不仅不增量，反而略差。

### 3.3 相对 RS_q / BF_q 的增量

| 压力特征 | 残差增量 AUROC [CI] | 配对差（压力−RS_q）[CI] | Spearman [CI] |
|---|---:|---:|---:|
| reversal stress-area | 0.561 [0.494, 0.664] | −0.017 [−0.032, −0.002] | 0.714 [0.608, 0.797] |
| reversal breakpoint | 0.563 [0.338, 0.643] | −0.042 [−0.066, −0.019] | 0.647 [0.510, 0.751] |
| reversal robustness radius | 0.563 [0.337, 0.641] | −0.042 [−0.065, −0.021] | 0.647 [0.504, 0.750] |

- stress-area 相对 RS_q 的增量 CI 含 0.5（下界 0.494）；配对差 −0.017 且 CI 排除 0 →
  stress-area 被 RS_q **轻微、统计显著地支配**（RS_q 含 paraphrase 轴小幅增益，与 round-6 全
  cohort 结论一致）。→ 相对 RS_q **完全可归约**。
- breakpoint / robustness radius 相对 RS_q 同样可归约且被支配。

### 3.4 参照：相对 R_sym 的增量（与 round-6 一致）

| 压力特征 | 残差增量 AUROC [CI] | 配对差（压力−R_sym）[CI] |
|---|---:|---:|
| reversal stress-area | 0.870 [0.800, 0.947] | +0.047 [+0.015, +0.085] |
| reversal breakpoint | 0.790 [0.697, 0.866] | +0.023 [−0.008, +0.057] |

压力特征相对 R_sym 的增量显著，**这与 round-6 的 RS_q-vs-R_sym 结论同源**：R_sym 的
`intervention_disagreement` 项（权重 0.7，自身 AUROC ≈ 0.5）是拖累，反证轴才是信号载体。
该对比只是参照，不影响"可归约到二元 reverse 轴 / RS_q"的主判定。

### 3.5 内部形状诊断（排除 λ=1 端点后）

| 特征 | plain AUROC [CI] | 相对 rev_flip_rate 的残差增量 [CI] |
|---|---:|---:|
| reversal flip at λ=0.8 | 0.949 [0.925, 0.970] | 0.460 [0.387, 0.666] |
| reversal interior area [0.2, 0.8]（不含端点段） | 0.948 [0.926, 0.968] | 0.533 [0.466, 0.602] |

排除 λ=1 端点（= rev_flip_rate）后，曲线内部点/内部面积单独预测力 ~0.948 但增量 CI 均含 0.5 →
**内部形状本质上是端点的单调放大，无独立信息**。

### 3.6 机制层面的解释

- rev_flip_rate 分布几乎完美分隔两类：correct 中 159/203（78%）rev_flip_rate = 1.0（全翻转），
  wrong 全部 ≤ 0.2（13 个 0.0、9 个 0.2）。consensus（多数票）层面，22/22 wrong 无 breakpoint
  （rigid），correct 中 31/203 无 breakpoint。
- 因此曲线（面积、breakpoint、radius）的信息已由二元端点承载；曲线是对该效应的**更细粒度机制
  描述**（flip-prob 随 λ 平滑上升 vs 全程 rigid），而非新增的独立预测特征。

## 4. 边界与模型范围

### 4.1 子集口径（明确声明）

- 本分析全部统计量都在 **phase-3 120 对 / 240-item 子集（Qwen HC 225 items / 119 pairs /
  22 wrong）**上；**不等于全 cohort**。全 cohort 口径见 round-6（567/574 items）。子集上正例仅
  22 个，增量测试的统计功效有限（CI 普遍较宽），故"无可归约增量"的结论是**保守**的（若真有
  增量，此样本量下更可能漏报而非误报）。

### 4.2 Ling-3.0-tiny 边界

- **Ling 没有 phase-3 λ 记录**（round-3 Ling 尝试在 pipeline/validity 层失败；
  round-4 `cs-paper-ling-adapted-20260913` 只覆盖主 cohort 5 个离散条件，无 λ 网格）。
  → **Ling 的 per-item λ 压力特征与 λ 曲线可归约性 NOT EVALUABLE**（零新增调用约束下无法补救）。
- 仅能报告同 120 对子集上 Ling 的**离散轴** AUROC（context only，post-hoc）：HC 227 items /
  119 pairs / 43 wrong；`rev_flip_rate` 0.883 [0.846, 0.915]；RS_q 0.910 [0.876, 0.938]；
  R_sym 0.838 [0.787, 0.882]。Ling 的 λ 曲线是否携带独立增量**不可判定**，论文不得作任何
  "Ling λ 曲线"声明。

### 4.3 removal 轴

- removal 轴为冻结协议的描述性副轴：risk=-area 的 AUROC ≈ 0.32（即 wrong consensus 在证据删除
  下**更不稳**，与 reversal 轴符号相反）。相对两基线的增量 CI 均含 0.5（点估计 0.51–0.52），
  配对差显著为负。维持"仅描述性，不作为特征"的冻结定位。

## 5. 结论

- **判定：可归约（reducible）**。λ 连续曲线特征（stress-area / breakpoint / robustness radius）
  相对**二元 reverse 轴（rev_flip_rate）**与 **RS_q/BF_q** 均无可归约性之外的显著增量：
  - 相对 rev_flip_rate：stress-area 残差增量 0.476 [0.429, 0.653]（点 ≤0.5），配对差 +0.003；
    breakpoint/radius 增量 CI 含 0.5 且配对差显著为负。
  - 相对 RS_q：stress-area 增量 0.561 [0.494, 0.664]（CI 含 0.5），配对差 −0.017（被支配）；
    breakpoint/radius 同理被支配。
- **建议：λ 曲线不升为正式特征贡献，保留为 interpretability / 机制图**（详见 `decision.md`）。
- 冻结的 phase-3 stress-area gate（AUROC 0.948）**保持原样**（preregistered, frozen），作为"反证
  响应性效应在连续 λ 下稳健"的机制确认，但不得在 paper 中表述为"除二元 reverse 轴 / RS_q 之外的
  额外预测特征"。

## 6. 复现

- 脚本：`scripts/build_lambda_features.py` → `scripts/analyze_reducibility.py` →
  `scripts/diagnose_interior.py` → `scripts/ling_boundary.py`（全部零新增调用）。
- 种子：`20260913` 基 + 独立偏移（round-3 用 +40/+41，round-6 用 +0..+56；本分析用 +200..+602，
  偏移逐一不重复）。
- 输出：`features_phase3_lambda.jsonl`、`reducibility_results.json`、`interior_diagnostic.json`、
  `ling_boundary_results.json`、`build_features_verify.json`（sha256 见 §1）。
- 运行：`python3 consensus_stress/round7/lambda_features/scripts/{build_lambda_features,analyze_reducibility,diagnose_interior,ling_boundary}.py`
