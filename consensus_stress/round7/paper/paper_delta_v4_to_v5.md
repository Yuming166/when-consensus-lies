# Paper Delta: v4 → v5 (round-7 integration, Agent W5)

- 日期：2026-09-15
- 输入：`consensus_stress/round6/paper/naacl_draft_v4_astra.md`（v4 基线）、
  `NAACL_Main_Revision_Autoresearch_Plan.md`（§7–§21）、round-7 各 workstream 产物
  （`audit/`、`ind_ce/`、`ind_ce_strict/`、`stress_profile/`、`lambda_features/` 的
  decision.md / SUMMARY / analysis md / results JSON）。
- 产出：`consensus_stress/round7/paper/naacl_draft_v5_astra.md`（完整 markdown，1268 行）。
- 约束遵守：只写 `round7/paper/`；不生成 LaTeX；不 git commit；不修改任何冻结协议数字。

## 1. 状态结论（W1–W4 + W2b 是否完成）

| workstream | 产物 | 状态 | 是否已整合进 v5 |
|---|---|---|---|
| W1（P0 审计） | `round7/audit/{mirror_audit,s_pair_diagnostic,leakage_audit}.md` | 完成（rc=0） | 是（§3.5、§3.6、§4.6） |
| W2（独立反证，label-coupled） | `round7/ind_ce/analysis/ind_ce_results.md` + `decision.md` | 完成 | 是（§4.7） |
| W2b（独立反证，strict claim-only） | `round7/ind_ce_strict/decision.md` | 完成（rc=0） | 是（§4.7、§6） |
| W3（多轴压力轮廓） | `round7/stress_profile/stress_profile_analysis.md` + `decision.md` | 完成 | 是（§4.8、§6、§8） |
| W4（λ 曲线可归约性） | `round7/lambda_features/lambda_features_analysis.md` + `decision.md` | 完成 | 是（§4.8、§6、§8） |

无 "待 Wx 结论" 项：monitor 日志显示 W2/W2b 于 2026-09-15 01:42 完成并启动 W5。

## 2. 结构性变更（对应计划 §7–§9、§18、§19）

### 2.1 三贡献重构（§8）
v4 的贡献列表（5 条，评分/跨模型/特异性/控制/诚实解读）重构为计划 §8 的三条：
- **C1 经验现象**：错误共识对决策相关反证响应不足（rev_flip 0.843 vs 0.095 / 0.703 vs 0.029；
  RS_q AUROC 0.943 [0.924, 0.960] / 0.896 [0.873, 0.916]）。
- **C2 评估协议（CST-Bench）**：事前（pre-outcome）压力测试协议，显式 call 记账
  （5 consensus + 10 main probe + 10 auxiliary diagnostics），outcome firewall、冻结队列、
  预注册 gates、pair-grouped bootstrap。
- **C3 实证验证**：冻结评估 + 对照 + 跨模型 + round-7 压力测试（S_pair、独立反证、
  多轴轮廓、λ 曲线）对机制边界的刻画。

### 2.2 Call 记账修正（§9）
- 全文不再把主方法称为 "25-call"：新增 §3.3 记账表
  （consensus 5 / main probe 10 / auxiliary diagnostics 10），并显式声明
  "the main score requires 10 probe calls after initial consensus formation"。
- Table 5/6/7 的 Calls/item 列改为 "probe / protocol"（RS_q = 10 / 25；
  reversal-only(5) = 5 / 10 等）。
- §4.5 与 §5.4 保留 cost-curve 结论：10-call probe 无损（Δ=0.000），5-call reversal-only
  在 paired AUROC 上显著更弱（Qwen +0.012 [0.002, 0.023]；Ling +0.027 [0.013, 0.042]），
  不声称 "5 calls ≈ 10 calls"。

### 2.3 削减防御性措辞（§18）
- 删除 v4 的 "Appendix A — Reviewer Q&A"（6 个小节全部以 "A reviewer might..." 形式展开）
  与文末 "Claims We Explicitly Do Not Make" 列表。
- 将实质内容吸收进正文：
  - mirror-equivalence / S_pair → §3.5 + §4.6（一次性、带量化）；
  - 单 agent ablation 讨论 → §4.4（"Single-agent intervention" 段落）；
  - R_sym reducibility → §4.9；
  - 单一数据集 / 零样本边界 / GPT 单点 → §6 Limitations 第 3 条 + §4.11；
  - baseline fairness → §4.4 + §6 第 8 条。
- 全文扫描确认无 "We do not claim / A reviewer might / We emphasize / This does not mean"
  重复句式（残留 0 处 "We do not claim"；边界全部改写为事实陈述，
  如 "RS_q is not the best Risk@80 point in every comparison..."）。

### 2.4 Title 候选（§19）
v5 顶部新增 "Title candidates" 块，3 个候选 + 推荐：
1. **When Consensus Lies: Stress-Testing Multi-Agent Agreement with Counter-Evidence**（推荐，
   匹配协议+现象最终框架）；
2. v4 原标题（保留为候选 2，经验结果未变）；
3. 简短变体（仅在前置排序语义下可接受）。

### 2.5 摘要 / limitation / conclusion 更新
- 摘要：重写为现象+协议+验证三贡献结构，加入 10-probe-call 记账、S_pair 结论、
  独立反证 Δ_CE 与 strict 无增量边界、BoolQ 特异性；全部数字带 CI。
- Limitations：从 v4 的 9 条重写为 8 条，新增 round-7 边界
  （natural-pair 属性、独立反证行为/预测两轴分离、多轴/λ post-hoc 边界），
  保留 label 不对称、Ling 契约适配、cost、无因果/代理 baseline/无多重校正。
- Conclusion：三贡献收尾，给出"选择性验证信号"而非"机制/真理性"定位，
  deployment 明确"conditional on obtaining counter-evidence"。

## 3. round-7 新内容与可追溯性（每条新表述 → 产物）

| v5 位置 | 新表述（要点） | 来源产物 |
|---|---|---|
| §1.2 / §3.5 / §4.6 | reverse(i)≡original(j) 逐字等价 3000/3000；答案一致 99.97%/99.63%；BF_reverse(i)≡BF_reverse(j) rho 0.996/0.995（exact 99.65%/97.39%） | `round7/audit/mirror_audit.md` |
| §4.6 | 镜像项重建：RS_q(j) 预测 item i 错误 AUROC 0.909 [0.886, 0.932] / 0.827 [0.795, 0.856]（96.4%/92.2%）；both-wrong 5/567、0/574 | `round7/audit/mirror_audit.md` §5 |
| §3.5 / §4.6 | S_pair 定义与重建：AUROC 0.931 [0.912, 0.948] / 0.869 [0.846, 0.891]；逐项相等 99.82%/98.43%；Spearman 0.998；配对差 −0.0000/−0.0002；RS_q−S_pair +0.0122 [0.0022, 0.0228] / +0.0272 [0.0137, 0.0422]；重建 RS_q ~98.7%/97.0%；S_pair_panel 0.893/0.863 | `round7/audit/s_pair_diagnostic.md` + `s_pair_results.json` |
| §3.6 | 泄漏审计：无 label 进入事前计算/选择（静态扫描 + 代码追踪） | `round7/audit/leakage_audit.md` |
| §4.7 (W2) | 三条件 flip 率 0.8253/0.8373/0.5442；Δ_CE +0.2932 [+0.2056, +0.3682]；Δ_NI +0.0120 [−0.0581, +0.0789]；placebo 不干净 0.5442（G4 FAIL）；E_ind 审计 0.90 相关、token Jaccard max 0.68；S_ind/S_natural/S_combined AUROC 0.9830/0.9624/1.0000；配对差 +0.0206 [−0.0187, +0.0646]；OOF +0.0447 [+0.0146, +0.0842]；ρ 0.5664 [0.3557, 0.6945] | `round7/ind_ce/analysis/ind_ce_results.md` + `decision.md` + `ind_ce_results.json` |
| §4.7 (W2b) | strict claim-only：Δ_CE +0.2118 [+0.1160, +0.3097]；P(flip|ind_strict) 0.7258、placebo_matched 0.5141（不干净）；S_ind_strict AUROC 0.624 [0.286, 0.856]（3 wrong）；S_ind−S_natural −0.349 [−0.714, −0.091]；S_ind−RS_q −0.318 [−0.670, −0.106]；ρ 0.033 [−0.044, 0.478]；OOF +0.004 [−0.074, 0.047]；审计（独立性 PASS、泄漏 PASS、方向合规 0.783 边缘） | `round7/ind_ce_strict/decision.md` + `analysis/strict_results.json` |
| §4.8 (W3) | 全 cohort 反转/移除反向签名（Qwen HC +0.748 [+0.685, +0.808] / −0.306 [−0.366, −0.240]；Ling +0.674 [+0.629, +0.715] / −0.249 [−0.291, −0.206]；removal AUROC 0.646/0.614）；多轴无增量（risk_z3 −0.012 [−0.027, −0.000]；risk_rsq_rem −0.052 [−0.084, −0.021] / −0.048 [−0.075, −0.025]；OOF3 打平 −0.001 [−0.006, +0.004] / −0.005 [−0.013, +0.002]）；假阳性分解（consensus-rigid 占正确 13.9%/27.3%；removal 分离 0.501/0.461；para 0.583/0.604） | `round7/stress_profile/stress_profile_analysis.md` + `decision.md` + `stress_profile_results.json` |
| §4.8 (W4) | λ 曲线可归约：stress-area AUROC 0.948 [0.925, 0.969]（复现冻结 gate）；vs rev_flip 残差 0.476 [0.429, 0.653]；vs RS_q 残差 0.561 [0.494, 0.664]、配对差 −0.017 [−0.032, −0.002]；breakpoint/radius 显著为负；内部形状 0.533 [0.466, 0.602]；Ling NOT EVALUABLE | `round7/lambda_features/lambda_features_analysis.md` + `decision.md` + `reducibility_results.json` |
| §8 | 图 1 `axis_profile_scatter.png`、图 2 `lambda_separation.png`（诊断图，非主文评分） | `round7/stress_profile/figures/` |

判定采纳（与 workstream decision 一致）：
- W1：S_pair 结论如实写入（主信号大部分是自然对构造的机械结果；reverse 条件无独立于
  配对结构的测量），并作为 §4.6 + §3.5 的量化边界。
- W2/W2b：**部分成功**——行为轴（平均翻转选择性）成立且 Δ_CE>0；预测轴（独立排序信号）
  不成立（strict 负增量、ρ≈0）。因此论文按计划 §6 收窄 claim：主贡献 = 自然配对经验现象 +
  CST-Bench 协议 + 事前反证响应信号；独立反证仅支撑"平均选择性响应"弱声明，不作为
  独立可部署排序信号；placebo 不干净如实标注（选择性增量，非全有全无）。
- W3：多轴轮廓**不进主评分**（增量不显著/负），降为诊断图 + post-hoc 边界小节；
  主评分保持冻结 RS_q。
- W4：λ 曲线**不升为特征贡献**，保留为 interpretability/机制图；Ling 无 λ 声明。

## 4. 数字一致性说明

- v4 的 373/373 冻结数字在 v5 中**原样保留**（gates、leaderboard、cost、reducibility、
  per-label、gpt 单点、BoolQ/FEVER）；仅表格编号因插入 round-7 内容重排
  （v4 Table 9–13 → v5 Table 11–15；新增 v5 Table 9–10 为 S_pair）。
- round-7 全部为冻结数据上的新导出（S_pair、mirror/leakage audit、stress profile、λ）或
  预注册的新协议（W2/W2b）；post-hoc 分析均标注 "post-hoc / exploratory"。
- 已知 seed 级 ±0.002 差异（如 Ling RS_q CI [0.873, 0.916] vs W3 复现 [0.875, 0.917]）
  在 W3 analysis 中已说明为不同 bootstrap seed 基的复现差异，不影响任何 gate；v5 正文沿用
  v4 冻结口径，W3 数字仅在 W3 小节内按 W3 报告引用。
- Table 5/6/7 的 Calls/item 列是**记账口径变更**（§9），不是数字变更；Token 记账
  （10,196/10,354 = 全 25-call 协议）表述同步修正。

## 5. 未改动 / 未新增声明

- 未改动任何冻结 gate 判定、协议公式（BF_q、RS_q、R_sym、R_PI）、HC=0.8、方向符号。
- 未新增任何无 CI 的数字；所有新数字可追溯到上方来源文件。
- 未把 W2/W2b 的 S_ind 作为主评分或可部署增量信号；未把多轴/λ 作为特征贡献；
  未对 Ling 作 λ 声明；未声称跨数据集/零样本/前沿模型全 cohort。
- 未生成 LaTeX；未 git commit（工作区 `round7/paper/` 为唯一写入）。

## 6. Post-W5 follow-up（2026-09-15 08:xx，W2 严格推理补跑完成后的小改）

W5 收稿时 W2 的 100 项 TARGET_SPEC 严格推理仍是 PARTIAL（中转上游 400/502）；watch 循环于
2026-09-15 06:47 补跑完成（1500 逻辑 calls，valid 0.9593，G1 达标）。补跑分析后对 v5 做**最小
事实补充**（未改任何冻结数字、未改结论）：

1. §4.7 W2b 小节后新增 "W2 strict (claim-only TARGET_SPEC, 100 items / 50 pairs)" 段：
   Δ_CE = +0.0988 [+0.0300, +0.1681]（G3 PASS，方向与 W2b 的 +0.212 一致但量级更小）；
   Δ_NI = −0.1686 [−0.2689, −0.0611]（claim-only 显著低于镜像）；placebo 0.558 不干净（G4 FAIL）；
   预测轴不成立（S_ind_strict HC AUROC 0.699 CI 含 0.5；配对 ΔAUROC vs S_natural −0.257；
   OOF 增量 +0.027 CI 触 0；ρ=0.322）。
2. 同步把三处 "Δ_NI ≈ 0" 限定为 label-coupled 版本成立（+0.012），claim-only 版本显著为负
   （−0.169）：§4.7 Reading、§4.11 讨论段、§6 边界段。
3. 数据源：`consensus_stress/round7/ind_ce/analysis/ind_ce_strict_results.{json,md}`、
   `ind_ce/SUMMARY.md`、`ind_ce/analysis/ind_ce_decision.md` §7。
