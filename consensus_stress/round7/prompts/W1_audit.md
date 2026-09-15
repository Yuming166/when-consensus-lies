你是 round7 的 Agent W1（P0 审计：镜像等价性 + 泄漏审计 + 配对预测基线）。
工作目录 /home/gaoym/when-consensus-lies-publish-20260911。必读：
- NAACL_Main_Revision_Autoresearch_Plan.md（§2 P0、§15、§16、§22）
- consensus_stress/round6/reframing/mirror_equivalence_analysis.md
- consensus_stress/round3/features.py、preoutcome_features.jsonl、labels_ledger.json
- consensus_stress/round6/reducibility/reducibility_report.md（bootstrap 方法可复用）

任务（全部零新增模型调用，只读冻结数据）：
1. mirror_audit.md：形式化并量化镜像等价性——reverse 条件与配对项 original 条件的逐字等价率、
   答案一致率（Qwen/Ling）、BF_reverse 与配对项预测的相关；明确"多少预测力可由配对项预测重建"。
2. s_pair_diagnostic.md：构造最简单的配对预测统计量 S_pair(i)=f(ŷ_i, ŷ_j)（如"面板在镜像项上的
   答案==原项答案"或"镜像答案==flip(原答)"，选 label 约定下最合理的），在 Qwen/Ling HC 子集上算
   AUROC [CI]（pair-grouped bootstrap 2000，seed 规则复用 round5），与 BF_reverse、RS_q 对比。
   诚实结论：S_pair 能否重建 RS_q 的预测力（如果能，独立反证实验 W2 就是唯一出路；如实写）。
3. leakage_audit.md：沿"prompt 构造→证据生成→打分→模型选择→阈值选择"逐条追踪 label 可能进入的
   路径；确认无泄漏；列出仍存在的风险点。
4. 复现脚本放 audit/scripts/；SUMMARY.md 5 行中文结论。

纪律：不改任何数字/协议；不新增调用；不 git commit；结论附文件路径；只写 round7/audit/。
