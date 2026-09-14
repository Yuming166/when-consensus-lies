# Round 2 总结 — When Consensus Lies → Consensus Stress Testing（2026-09-13）

编排模型：DeepSeek v4 flash Max（服务器默认）。研究模型：本地 Qwen3.5-4B @ 127.0.0.1:31518（未发
reasoning_effort；未用 openapi.center）。所有新文件在 consensus_stress/round2/；未 git commit/push；
docs/ 与冻结代码零改动；registry.yaml 仅追加/更新状态，旧条目未改。

## Gate 判定

| 项目 | 判定 | 依据 |
|---|---|---|
| Gate 2 pilot（cs-pilot-vitaminc-20260913） | **FAIL（字面冻结门控）** | 字面门控 AUROC(BF_q,wrong)=0.099 [0.054,0.153] 不满足 CI lb>0.5 —— 预注册数值门控符号缺陷（门控编码了"higher BF_q⇒wrong"，与协议自身冻结的实质方向"higher BF_q⇒lower risk"矛盾） |
| Gate 2 confirmation（cs-pilot-vitaminc-conf-20260913） | **PASS（修正方向一致门控，调用前冻结）** | AUROC(-BF_q,wrong)=0.912 [0.848,0.973]；macro CI [0.759,0.972]；worst-label 0.788；placebo 5.0%；置换通过；可约性通过 —— 7/7 |
| **Gate 2（round 2 最终）** | **PASS** | 两个独立、不相交、各自预注册的队列，同一冻结实质方向，效应一致 |
| Phase 3（stress 轴） | 离散轴草图 PASS（连续 lambda 网格留待后续） | reverse 下 fidelity 正确 0.794 vs 错误 0.119；agreement 弱分离 |
| Phase 4（reliability modeling） | 描述性 PASS（pilot 规模） | -BF_q AUROC 0.906 [0.865,0.944]，Risk@80 削减 65.4% [29.9%,89.2%]，优于全部基线 |
| Phase 5/6 | 未执行（仅计划） | 见 phase56_next_steps.md |

## 关键数字（合并 cohort：pilot 195 HC + confirmation 94 HC = 289 HC，47 wrong，16.3%）

- 主效果：错误共识对**自然证据反转不响应**（BF_reverse 0.088 vs 正确 0.775；合并后 fidelity 0.119 vs 0.794），
  对语义保持稳定（placebo 干净，flip 2.8–5.0%）→ "对语义改变不响应 ⇒ risky" 得到强支持。
- AUROC：-BF_q 0.906 [0.865,0.944]；R_sym 0.845、R_PI 0.659、disagreement 0.573、confidence 0.324；
  配对差（vs -BF_q）全部排除 0：R_sym +0.060 [+0.026,+0.100]、R_PI +0.246、disagreement +0.333、confidence +0.582、
  甚至优于拟合 logistic(OOF) +0.069 [+0.019,+0.135]。
- Risk@80（保留低风险 80%）：-BF_q 误差削减 65.4% [29.9%,89.2%]；R_sym 28.1%；R_PI 14.8%（n.s.）；confidence −17.1%。
- 子组一致性：pilot SUPP 0.886 / REF 0.926；confirmation SUPP 0.788 / REF 0.968 —— 两 label 同向（无 BoolQ 式 label 混淆）。
- Stage/批次一致性：pilot stage1 0.909 [0.859,0.950]、stage2 0.886 [0.793,0.967]。
- 管道德性：pilot 5000/5000、confirmation 2500/2500 全部有效；preoutcome features 零 label 字段；置换分布居中 0.5。

## 交付物（路径 + 证据）

- 预注册：round2/phase2_pilot/preregistration.md（pilot，含实质方向冻结）、confirmation_preregistration.md（修正门控，调用前冻结）
- 选择/审计：selection_manifest/audit.json、relevance_audit.json（28/30 与 29/30 决策相关）、
  paraphrase_manifest + audits（300/300、150/150 可用；语义审计 20/20、20/20）
- 记录/特征：records{,_stage1,_stage2,confirmation}.jsonl（无 label）、preoutcome_features.jsonl、
  confirmation_preoutcome_features.jsonl（无 label）
- 分析：analysis/analysis.json+analysis.md、confirmation_analysis.json+md、gate2_decision_pilot.md、
  gate2_decision_confirmation.md、phase3_stress_profile.{json,md}、phase4_protocol.md、phase4_results.json、
  phase4_reliability.md、phase56_next_steps.md
- 图：figures/roc_pilot_confirmation.png、figures/phase3_stress_profile.png
- registry.yaml：7 条（phase0/1 PASS、boolq FAIL、vitaminc FAIL、conf PASS、phase4 PASS、phase3-sketch PASS）

## 未完成 / 阻塞项

- 连续 stress 曲线（lambda 网格、breakpoint/robustness radius）：未执行（需新调用 + 新预注册）。
- Phase 5 active probing、Phase 6 跨模型（Ling-3.0-tiny）/跨数据集：未执行（只写计划；当前结论限定 Qwen3.5-4B/VitaminC）。
- 全规模 worst-label CI 级门控（V3.16.1 式）：pilot 规模点级门控已过，CI 级留待大 cohort。
- Gate-4 正式阈值（预注册操作点的 Risk@80 严格 CI 门控）：留待论文规模 cohort。

## 下一步建议

1. 以本轮的修正方向一致门控与决策相关 oracle 为模板，冻结一个论文规模协议（更大 cohort +
   CI 级 worst-label + Risk@80 操作点），把 Gate 2 结果提升为正式复现。
2. Phase 3 完整版：连续 lambda（按单位比例反转/删除）→ stress curve/breakpoint；Phase 4 完整版：
   简单模型 + Risk@80 严格门控（本轮已给出合并 cohort 的强描述性证据）。
3. Phase 6 跨模型（Ling-3.0-tiny）与跨数据集（label-symmetric 平衡 BoolQ 或另一验证集），协议先冻结再调用。
4. 论文写作：将"不变≠可靠"与"对决策相关反转不响应⇒risky"作为可测量的共识压力现象；
   谨慎区分"Qwen3.5-4B/VitaminC 上的强效应"与"跨模型泛化"（后者未验证）。
