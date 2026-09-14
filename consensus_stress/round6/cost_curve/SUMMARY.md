# Agent B SUMMARY — 成本-收益曲线（reversal-only 探针 vs RS_q）

1. **数据与方法**：只用冻结 records（Qwen/Ling 各 15,000 条），零新增模型调用；label-blind 中间分数先写盘并哈希（qwen `e5ce424f…`、ling `39f11d77…`）后再合并 label；pair-grouped bootstrap 2,000 次、seed `20260913+method_index` 与 Risk@80=0.8 完全复用 round5/benchmark 协议。
2. **成本曲线**：在两模型各自 HC 子集（Qwen n=567 / Ling n=574）上报告 reversal-only 1/2/5/10 calls、reversal+paraphrase 2/4/10 calls、完整 RS_q(25 calls) 的 AUROC 与 Risk@80（均带 95%CI）。
3. **关键结论**：reversal-only(5) vs RS_q(25) 配对差 CI 不含 0（Qwen AUROC +0.012 [0.002, 0.023]；Ling +0.027 [0.013, 0.042]，正=RS_q 优）→ **不采纳“5 calls ≈ 25 calls”作为统计等价声明**。
4. **可支持的降成本点**：10-call reversal+paraphrase 与 RS_q 逐项分数完全相同（配对差 Δ=0.000 [0.000, 0.000]）；Qwen 的 Risk@80 上 rev5 并不差（CI 含 0，点估 0.884 vs RS_q 0.846），但 AUROC 两模型均显著更弱。
5. **边界**：primary=Qwen（Ling 为 secondary，不能救 Qwen）；结论限于 frozen VitaminC 300-pair 的 HC 子集；reversal-only(10)（加入 synthetic_reverse）反而稀释信号（Qwen 0.832 vs rev5 0.931）；未改 `benchmark/LEADERBOARD.*`（归 Agent C）；`leaderboard_proposal.json` 已按现有 schema 提供 reversal-only(5) 行。
