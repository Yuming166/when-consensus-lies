# Decision — λ 连续压力曲线特征（融合点 B）

- 日期：2026-09-14
- 状态：**exploratory / post-hoc**（`NAACL_Main_Revision_Autoresearch_Plan.md` §16）；
  120 对 / 240-item phase-3 子集口径（Qwen HC 225 items / 119 pairs / 22 wrong），不冒充全 cohort。
- 输入证据：`lambda_features_analysis.md`（含全部 CI 与脚本路径）。

## 判定

**λ 连续曲线特征（stress-area / breakpoint / robustness radius）可归约到二元 reverse 轴
（`rev_flip_rate`）与 RS_q/BF_q → 不升为正式特征贡献，保留为 interpretability / 机制图。**

判定依据（pair-grouped 95% CI）：

1. 相对二元 reverse 轴：
   - reversal stress-area 残差增量 AUROC = 0.476 [0.429, 0.653]（点估计 ≤ 0.5，CI 含 0.5）；
     配对差 +0.003 [−0.001, +0.009] → 与 rev_flip_rate 在预测力上不可区分。
   - reversal breakpoint / robustness radius 残差增量 CI 含 0.5，配对差 −0.022 [−0.038, −0.009]
     显著为负 → 不增量且略被支配。
   - 排除 λ=1 端点（端点按构造 = rev_flip_rate）后，内部面积 [0.2, 0.8] 的增量 = 0.533
     [0.466, 0.602]（含 0.5）→ 曲线内部形状无独立信息。
2. 相对 RS_q/BF_q：
   - reversal stress-area 残差增量 0.561 [0.494, 0.664]（CI 含 0.5）；配对差 −0.017
     [−0.032, −0.002]（CI 排除 0）→ 被 RS_q 轻微、统计显著地支配。
   - breakpoint / radius 同理被支配。
3. 相对 R_sym 的增量显著（0.870 [0.800, 0.947]）与 round-6 同源：R_sym 含 0.7 权重的
   intervention_disagreement 拖累；该对比不改判 1/2。

机制解释：correct consensus 78%（159/203）在自然反证下 rev_flip_rate=1.0，wrong 全部 ≤0.2；
曲线是端点 flip 的单调放大，breakpoint/radius 是多数票层面的同一效应。连续曲线提供了
**更细的机制描述**（flip-prob 平滑上升 vs 全程 rigid），但不携带独立预测信号。

## 对论文的含义（推荐表述）

- **保留**：phase-3 冻结 gate（stress-area AUROC 0.948 [0.925, 0.969]，preregistered）作为
  "反证响应性效应在连续 λ 下稳健"的机制确认；曲线图（correct vs wrong 的 flip-prob(λ) 曲线、
  breakpoint/robustness-radius 分布）作为 interpretability 图。
- **不 claim**："λ 曲线是独立于 rev_flip_rate / RS_q 的新特征"、"breakpoint 提供额外预测力"。
- **一句话定位**：主预测信号 = 二元自然反证轴（rev_flip_rate，被 R_sym 以 0.3 权重部分捕获，
  RS_q 额外加 paraphrase 轴小幅增益）；连续 λ 曲线是同一信号的机制可视化。
- **Ling**：无 λ 记录，λ 曲线可归约性 NOT EVALUABLE；论文不得对 Ling 作任何 λ 曲线声明。

## 边界清单

1. 全部数字为 120 对子集口径（Qwen HC 225/119/22；Ling 仅离散轴 227/119/43）。
2. 正例仅 22 个，CI 宽；"无增量"为保守结论（低功效，不误报增量）。
3. 零新增模型调用；只读冻结记录；未修改任何冻结数字/协议。
4. 交付目录：`round7/lambda_features/`；不 git commit。
