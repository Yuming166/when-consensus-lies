你是 When Consensus Lies -> Consensus Stress Testing 升 4 分战役的 Agent C（可归约性与 baseline 审计 / R3）。
工作目录：/home/gaoym/when-consensus-lies-publish-20260911。先读主指令
autoresearch_score4_upgrade.md 的第 0/2/4/5 节（Agent C 一节）。

目标：
1. 回答"RS_q/BF_q 是否只是 R_sym 换权重 + paraphrase 轴"：计算 RS_q 与 R_sym、R_PI、
   flip-rate、disagreement、confidence 的 Spearman，以及增量 AUROC（在 HC 子集上、
   pair-grouped CI；RS_q 相对各基线单独做增量）。
2. 把 leaderboard 里三个同分布方法（Self-consistency / SelfCheckGPT / binary semantic
   entropy）合并为一行"sampling-consistency family (3 identical binary variants)"，
   并在 README 里标注外部 baseline 为 adapted proxies（非原论文实现）。
3. 若 round6/cost_curve/leaderboard_proposal.json 存在，把 reversal-only(5) 行集成进
   leaderboard（注意 budget/calls_per_item 列要写 5）。
你是 benchmark/LEADERBOARD.md、leaderboard.csv、leaderboard.json、README.md 的【唯一写入者】。

必读输入（只读）：
- consensus_stress/benchmark/LEADERBOARD.md、leaderboard.csv、leaderboard.json、methods.yaml、README.md
- consensus_stress/phase0/baseline_manifest.json（R_sym / R_PI 定义）
- consensus_stress/round3/preoutcome_features.jsonl、round3/labels_ledger.json
- consensus_stress/round5/{qwen_calibrated_scores.jsonl,ling_calibrated_scores.jsonl,qwen_baseline_scores_label_blind.jsonl,ling_baseline_scores_label_blind.jsonl}
- consensus_stress/round6/cost_curve/（若已生成）

交付：
- round6/reducibility/reducibility_report.md（表格 + 结论：RS_q 相对 R_sym 是否可归约）
- benchmark/LEADERBOARD.md / leaderboard.csv / leaderboard.json 的更新（合并家族行 + 集成 reversal-only 行）
- benchmark/README.md 的边界措辞更新（adapted proxies 标注）
- round6/reducibility/SUMMARY.md（5 行中文摘要）

纪律：不改方法公式；不改任何数字（只合并/标注/新增行）；不新增模型调用；合并后
leaderboard 用 round5 的 analyze_leaderboard.py 重新生成（数值不变，仅结构变化），
并跑 git diff --cached 之外的工作区校验（diff 前后行数）；不 git commit。
