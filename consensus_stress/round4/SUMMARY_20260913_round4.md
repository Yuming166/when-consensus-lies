# Round 4 总结 — When Consensus Lies → Consensus Stress Testing（2026-09-13，Phase 6 跨模型）

编排模型：DeepSeek v4 flash Max（服务器默认，未用 openapi.center）。研究模型：Qwen3.5-4B
@ 127.0.0.1:31518（仅复用冻结 Round-3 结果，无新调用）；Ling-3.0-tiny @ 127.0.0.1:31520
（GPU5，vLLM 0.29.0，`enable_thinking=false`）。所有新产物在 `consensus_stress/round4/`；
未 git commit/push；未修改 `docs/` 与冻结 Round-3 代码。registry 追加 2 条，当前共 16 条。

## 总判定

| 项目 | 判定 | 关键证据 |
|---|---|---|
| Ling adapted pipeline | **PASS** | 15,000/15,000 有效（100.0%），first-pass 99.95%；每条件 3,000/3,000 |
| Ling within-model 主 gate | **PASS（8/8）** | AUROC(RS_q=-BF_q, wrong\|HC)=0.896 [0.873,0.916]；macro 0.919 [0.895,0.944]；worst-label SUPPORTS 0.881 [0.834,0.928]；placebo 0.061；permutation 0.896>0.564；reducibility 通过 |
| 跨模型 procedure/score transfer | **PASS（有边界）** | Qwen 冻结 item-level RS_q → Ling 错误：0.723 [0.682,0.765]；Ling 自己 RS_q：0.896 [0.873,0.916]；两者 CI lb>0.5。配对差 Qwen-transfer−Ling-own=-0.173 [-0.217,-0.130]，说明 item-level 排序部分模型相关 |
| 机制迁移 | **PASS** | Ling reverse fidelity：correct 0.703 vs wrong 0.029；correct−wrong=0.674 [0.629,0.719]，CI 排零 |
| Phase 5 active probing（可选、离线探索） | **PASS** | 匹配 1 stress condition × 5 agents/item：active reversal AUROC 0.931 [0.912,0.948] vs fixed rotation 0.593 [0.529,0.659]；配对差 +0.338 [+0.269,+0.405] |
| 连续 λ 曲线 | 未执行 | 预注册为可选；离散 natural reverse 条件已足以检验机制迁移 |
| 回退 Qwen3.6-35B | 未触发 | Ling adapted pipeline 100%，无需回退 |

## 主结果与解释

- Cohort：完全复用 Round-3 冻结 300 对 / 600 项及模型无关 artifacts；未重选样本、未改
  oracle、条件、BF_q/RS_q 或门控。
- Ling HC：574/600，错误 119（20.73%）。Ling 自己的 `RS_q=-BF_q` 强于 chance 且通过全部
  预注册门控；Risk@80 误差削减 0.422 [0.274,0.591]。
- Qwen item-level score 直接迁移到 Ling 错误仍显著高于 chance（0.723），但显著低于 Ling
  自己分数；item-level Spearman 仅 0.496。因此支持的目标 claim 是有边界的：
  **压力测试程序与聚合可靠性信号可跨模型家族迁移，而 item-level 排序可能模型相关**。
- 机制复现：Ling 错误共识在自然证据反转下几乎不遵循 expected response（0.029），正确共识
  为 0.703；与 Qwen 上一轮“错误共识 rigid”机制一致。
- Active probing：Phase-3 发现的 reversal 轴作为单一探针，在匹配预算下显著优于 label-blind
  四条件轮转；这是离线探索性结果，不作为 Phase-6 gate 或 rescue。

## 关键交付物

- 预注册：`preregistration.md`；active probing：`active_probing_preregistration.md`
- Registry：`../registry.yaml`（新增 2 条：cross-model PASS；active probing exploratory PASS）
- 运行：`ling_adapted_run.py`、`run_summary_ling.json`、`ling_records.jsonl`（15,000 条）、
  `run_logs/ling_adapted_run.log`
- 特征：`build_features.py`、`ling_preoutcome_features.jsonl`（600 项，无 label）
- 分析：`analysis/ling_adapted_analysis.json`、`analysis/ling_adapted_crossmodel.md`、
  `analysis/active_probe_analysis.json`
- 图：`figures/roc_ling_crossmodel.png`、`figures/risk_coverage_ling_crossmodel.png`、
  `figures/ling_mechanism_reverse.png`、`figures/active_probe_roc.png`
- 审计/执行：`frozen_input_hashes.txt`、`artifact_hashes.json`、`execution_notes.md`、
  `server_status.json`
- 服务：Ling 留在 GPU5（PID 1887239，模型可见）；GPU4/GPU6 未占用。

## 未完成 / 下一步

- 未做 Ling 连续 λ 曲线；若要增强机制图，可在独立预注册下复用 Phase-3 240-item subset。
- Active probing 目前是 Qwen 冻结记录上的离线探索；下一步应预注册真实顺序版（先看 baseline，
  再选 probe，再调用）并在 Ling 或新模型上确认。
- 跨数据集边界仍保留：Round-3 BoolQ FAIL 说明该信号依赖自然反证，不是任意扰动通用信号。
- 论文表述应保持 bounded claim：两个模型家族、一个冻结 VitaminC 自然对协议；不得声称
  universal transfer、zero-shot generalization 或对所有可靠性基线的优越性。
