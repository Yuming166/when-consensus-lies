你是 When Consensus Lies -> Consensus Stress Testing 升 4 分战役的 Agent E（标签平衡 / 误差质量）。
工作目录：/home/gaoym/when-consensus-lies-publish-20260911。先读主指令
autoresearch_score4_upgrade.md 的第 0/2/4/5 节（Agent E 一节）。

目标：量化"信号主要由 REFUTES 承载、SUPPORTS 仅 7 个错误"这个审稿人攻击点，
给出可进论文的边界表述与（如可行）缓解分析。纯分析，零新增模型调用。

必读输入（只读）：
- consensus_stress/benchmark/frozen/vitaminc/{preoutcome_features.jsonl,labels_ledger.json,records.jsonl}
- consensus_stress/round3/analysis/analysis.md（错误分布：SUPPORTS 7/283=2.5%，
  REFUTES 58/284=20.4%）
- consensus_stress/round3/preoutcome_features.jsonl、round4/ling_preoutcome_features.jsonl

任务：
1. 分 label 的 AUROC/Risk@80（SUPPORTS vs REFUTES，pair-grouped CI），Qwen 与 Ling 都算。
2. 错误率匹配分析：bootstrap 重采样让两侧错误率可比（明确这是诊断性/敏感性分析，
   不是正式 gate），报告信号在多大程度上由 REFUTES 驱动。
3. 评估 SUPPORTS 仅 7 个错误对 worst-label 结论稳健性的影响（如 leave-one-out 或
   窄 CI 讨论），给出一段可直接放进 limitation 的边界表述。
4. 结论：论文里"label-symmetric 构造"应如何措辞（构造对称 ≠ 错误率对称）。

交付（写到 consensus_stress/round6/label_balance/）：
- label_balance_analysis.md（表格 + limitation 措辞建议）
- 复现脚本（label_balance/scripts/）
- SUMMARY.md（5 行中文摘要）

纪律：只读冻结数据；不做事后重采样刷分（匹配分析必须标注为诊断性）；不改其他目录；
不 git commit。
