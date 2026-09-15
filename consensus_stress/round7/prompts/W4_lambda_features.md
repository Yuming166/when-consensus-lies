你是 round7 的 Agent W4（融合点 B：λ 连续压力曲线特征的可归约性）。
工作目录 /home/gaoym/when-consensus-lies-publish-20260911。必读：
- NAACL_Main_Revision_Autoresearch_Plan.md（§16 标注 exploratory/post-hoc）
- consensus_stress/round3/analysis/phase3_lambda.md、records_phase3_lambda.jsonl（9,600 条）
- consensus_stress/round3/preoutcome_features.jsonl、labels_ledger.json
- consensus_stress/round6/reducibility/reducibility_report.md（增量 AUROC 方法）

任务（零新增调用，240-item phase3 子集，全部标注 post-hoc）：
1. 从 λ 记录构建 per-item 压力特征：stress-area、breakpoint λ、robustness radius（reversal 轴），
   removal 轴同法；Qwen/Ling。
2. 可归约性：这些压力特征相对"二元 reverse 轴（rev_flip_rate）"的增量 AUROC（pair-grouped CI）；
   以及相对 RS_q/BF_q 的增量。若不可归约 → λ 曲线可升为正式特征贡献；若可归约 → 建议保留为
   interpretability 图。
3. 边界：明确这是 120 对子集口径，不冒充全 cohort。

交付：lambda_features_analysis.md、decision.md、scripts/、SUMMARY.md（5 行中文）。
只写 round7/lambda_features/；不 git commit。
