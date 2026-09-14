你是 When Consensus Lies -> Consensus Stress Testing 升 4 分战役的 Agent B（成本-收益曲线 / R2）。
工作目录：/home/gaoym/when-consensus-lies-publish-20260911。先读主指令
autoresearch_score4_upgrade.md 的第 0/2/4/5 节（Agent B 一节）。

目标：用【冻结 records 只算、零新增模型调用】的方式回答："多少调用换多少可靠性？"
验证/量化：reversal-only 探针（5 calls/item）是否与 25-call RS_q 统计上相当（配对差 CI 是否含 0）。

必读输入（只读，禁止修改）：
- consensus_stress/benchmark/frozen/vitaminc/records.jsonl（Qwen 15,000 条）
- consensus_stress/benchmark/frozen/vitaminc/ling_records.jsonl（Ling 15,000 条）
- consensus_stress/benchmark/frozen/vitaminc/{preoutcome_features.jsonl,labels_ledger.json,selection_manifest.json}
- consensus_stress/benchmark/README.md（§5 budget 规则）、round5/preregistration.md（指标与 bootstrap 协议：
  pair-grouped 2000 次、seed 20260913+method_index、Risk@80 操作点 0.8）
- 可复用 round5 的 benchmark/build_baseline_scores.py 与 analyze_leaderboard.py 的逻辑（复制到你的目录再改）

任务：
1. 在 Qwen（primary）与 Ling（secondary）各自 HC 子集上，计算以下各点的 AUROC [95%CI] 与
   Risk@80 [95%CI]（pair-grouped bootstrap）：reversal-only 探针在 agent-call 预算
   1/2/5/10、reversal+paraphrase 组合、完整 RS_q（25 calls）。明确每个点的 calls/item。
2. 对"reversal-only(5) vs RS_q(25)"给出配对差 CI（RS_q - reversal5，正=RS_q 优）。
3. 输出 leaderboard_proposal.json：把 reversal-only(5) 作为一行（含全部 leaderboard 列，
   与现有行同 schema），供 Agent C 集成。不要把 reversal-only 混入现有 25-call 方法。

交付（写到 consensus_stress/round6/cost_curve/）：
- cost_curve.md（表格 + 3 行以内结论：是否采纳"5 calls 成本故事"）
- leaderboard_proposal.json
- 复现脚本（copy 到 cost_curve/scripts/）+ 中间 label-blind 分数文件（先写盘再合并 label）
- SUMMARY.md（5 行中文摘要 + 边界）

纪律：label-blind 中间产物先写盘；不改 benchmark/LEADERBOARD.*（那是 Agent C 唯一写的）；
不新增模型调用；若 5-call ≥ RS_q 在 CI 内，结论写"采纳成本故事"，这是好结果不是失败。
