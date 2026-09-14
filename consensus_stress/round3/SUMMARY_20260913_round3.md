# Round 3 总结 — When Consensus Lies → Consensus Stress Testing（2026-09-13，论文规模）

编排模型：DeepSeek v4 flash Max（服务器默认，未用 openapi.center）。研究模型：本地
Qwen3.5-4B @ 127.0.0.1:31518（无 reasoning_effort）；跨模型 Ling-3.0-tiny @ 127.0.0.1:31520
（vLLM 0.29.0 新装于 GPU5，`enable_thinking=false`，ninja 修复后成功启动；未占用 GPU4/GPU6）。
所有新产物在 `consensus_stress/round3/`；未 git commit/push；docs/ 与冻结代码零改动；
registry.yaml 追加 7 条新条目（旧 7 条原样保留）。

## Gate 判定

| 项目 | 判定 | 依据 |
|---|---|---|
| Gate 2 论文规模（cs-paper-vitaminc-20260913，300 对/600 项） | **PASS（8/8 门控）** | AUROC(RS_q=-BF_q, wrong\|HC)=0.943 [0.924,0.960]；macro 0.952 [0.904,0.995]；worst-label SUPPORTS 0.917 [0.819,0.999]（CI 级）；placebo 0.038；permutation 0.943>0.596；reducibility 通过 |
| Phase 4 正式版（cs-paper-phase4-20260913） | **PASS（P1-P6）** | Risk@80 0.846 [0.638,0.981]（CI lb>0）；配对差 vs R_sym +0.051 [+0.029,+0.075]、vs R_PI +0.315 [+0.271,+0.360]；Risk@80 相对 R_sym +0.347、R_PI +0.847（CI 全排 0）；isotonic ECE 0.057→0.013 |
| Phase 3 完整版（cs-paper-phase3-20260913） | **PASS（reversal 轴）** | stress-area AUROC 0.948 [0.925,0.968]；correct 平均 stress area 0.436 vs wrong 0.032；wrong 共识在 λ∈[0,1] 全部 rigid（robustness radius 1.0，22/22 无 breakpoint） |
| Phase 6 跨模型（cs-paper-ling-20260913） | **FAIL（管线层，如实）** | Ling 有效率 0.311 < 0.95；主导失败=缺 agent_id（6890 例）；tiny 模型无法满足冻结严格 JSON 契约 → 实质 gate 不可评估，未在 31% 过滤子集上伪造结果；无 parser/oracle/gate 事后放宽 |
| Phase 6 跨数据集 FEVER（cs-paper-fever-20260913） | **BLOCKED（构造层）** | FEVER validation 无同 claim S/R 自然对；近重复 claim 对语义审计仅 1/60 通过（E_R 基本= E_S，不能作自然反证）→ 未跑 agent 调用，无结果声明 |
| Phase 6 跨数据集 BoolQ（cs-paper-boolq-20260913） | **FAIL（特异性边界，如实）** | 平衡 50/50，管线 100% 有效；主 AUROC 0.449 [0.308,0.579]（方向反转），label 子组相反（no 0.073 / yes 0.745），Risk@80 n.s.，permutation 失败 → 机制要求"自然反证"，非任何扰动（特异性证据） |
| Phase 5 active probing | 未执行 | 预算/门控不允许；下一步计划写入 phase56_next_steps.md |

## 关键数字（论文规模主 cohort：300 pairs / 600 items，567 HC，65 wrong=11.5%）

- 主效应：错误共识对自然证据反转完全不响应（reverse 条件 mean fidelity：correct 组明显高于 wrong 组；
  Phase-3 连续曲线：correct flip 0→85% 随 λ 单调上升，wrong 0→12% 几乎不动）。
- **AUROC(RS_q, wrong|HC)=0.943 [0.924,0.960]**（round2 基线 0.906 [0.865,0.944] 保持/超越）。
- **Risk@80 误差削减 0.846 [0.638,0.981]**（round2 0.654 [0.299,0.892]）。
- 配对差（vs RS_q，全部 CI 排 0）：R_sym +0.051 [+0.029,+0.075]、R_PI +0.315 [+0.271,+0.360]、
  disagreement +0.360、confidence +0.671；Risk@80 配对差 vs R_sym +0.347 [+0.152,+0.502]、R_PI +0.847 [+0.677,+0.984]。
- 简单模型：冻结复合 BF_q（0.943）≈ 拟合 logistic OOF（0.941，配对差 CI 含 0）→ "概念而非拟合"；
  isotonic ECE 0.057→0.013。
- 子组一致性：SUPPORTS 0.917 / REFUTES 0.986（两 label 同向，无 BoolQ 式混淆；REFUTES 承载 89% 错误质量）。

## 交付物（路径 + 证据）

- 预注册/协议：round3/preregistration.md（调用前冻结，方向 RS_q=-BF_q 从开头写对，CI 级 worst-label，
  Risk@80 操作点 0.8 + 严格 CI gate）；expected_response_contract.json
- 选择/审计：selection_manifest/audit.json（300 对，与 round2 的 150 对及 V3.16/V3.16.1 页面全不相交，
  cr>=0.85/tj>=0.70 放宽至论文规模）、labels_ledger.json（sealed）、relevance_audit.json（30/30）、
  paraphrase_manifest + audit（900/900 usable、30/30 语义保持）、artifacts_repair_note.md（1 个 distractor
  因 citation 句无法改写，调用前确定性替换并记录）
- 记录/特征：records{,_stage1,_stage2}.jsonl（15000 条，无 label）、preoutcome_features.jsonl（600 项，无 label）
- 分析：analysis/analysis.json+md、gate2_decision_paper.md、phase3_results.json+phase3_lambda.md、
  ling_crossmodel.md、fever_crossdataset.md、boolq_analysis.json+boolq_crossdataset.md、phase56_next_steps.md
- 图：figures/roc_paper_scale.png、risk_coverage_paper_scale.png、phase3_stress_curve.png
- 跨模型/跨数据集数据：ling_records.jsonl（5000 条）、boolq_records.jsonl（2000 条）+ 各自
  preoutcome_features/labels/analysis、fever_audit.json（构造阻塞证据）
- registry.yaml：14 条（新增 7 条，状态见上）

## 未完成 / 阻塞项

- 跨模型实质复现（Ling）：管线层 FAIL；需下一轮预注册模型能力适配（如去掉 agent_id 校验并以
  task-assignment 绑定 agent，或加冻结 JSON exemplar，或换能守契约的第二模型）后再测实质门控。
- 跨数据集正复现：FEVER 结构不支持自然反证（BLOCKED）；BoolQ 为特异性负结果（方向反转）——两者均如实保留。
- Phase 5 active probing：未执行（仅计划）。
- SUPPORTS worst-label CI 较宽（7 wrong），已通过 CI 级门控但需更多 REFUTES 侧平衡数据时注意。

## 下一步建议

1. 论文写作可用：论文规模 Gate 2 PASS + Phase 4 正式 PASS + Phase 3 连续 stress 曲线（0.948），
   全部 CI 级门控；明确"Qwen3.5-4B/VitaminC 上的强效应 + 自然反证特异性（BoolQ 负结果作为因果特异性证据）"。
2. 跨模型：按 ling_crossmodel.md 的 next-round 设计（先冻结适配再调用）；或选用能守 JSON 契约的
   第二模型（如 Ling-3.5 级或小指令模型）。
3. 跨数据集：寻找带天然双证据对比的数据集（contrastive fact-verification / QA 构造）以完成正复现。
4. Phase 5：把 Phase-3 的 reversal 轴作为唯一探针做 active probing 的匹配预算比较。
5. 如需上线数字/图：figures/*.png 已按论文风格输出；analysis.md 表格可直接嵌入 paper 的 results 表。
