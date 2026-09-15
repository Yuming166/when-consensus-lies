你是 round7 的 Agent W3（融合点 A：多轴压力响应轮廓）。
工作目录 /home/gaoym/when-consensus-lies-publish-20260911。必读：
- NAACL_Main_Revision_Autoresearch_Plan.md（§16 标注 exploratory/post-hoc）
- consensus_stress/round6/paper/（v4 草稿 §4.6/§4.7）
- consensus_stress/round3/preoutcome_features.jsonl、labels_ledger.json（600 项，已含
  rev_flip_rate / rem_flip_rate / synth_flip_rate / para_flip_rate / bf_*）
- consensus_stress/round3/analysis/analysis.md、round6/reducibility/reducibility_report.md

任务（零新增调用，纯冻结特征分析，全部标注 exploratory/post-hoc robustness analysis）：
1. 移除轴反向签名验证：在 600 项全 cohort（Qwen/Ling）上验证"错误共识在移除下更不稳、反转下更刚性"
   （phase3 只看了 120 对子集）；给出 flip 率对比与 CI。
2. 多轴组合 vs BF_q：构造若干多轴风险表示（如 reversal 非响应 + removal 不稳 + paraphrase 不稳），
   在 Qwen/Ling HC 子集上算 AUROC/Risk@80（pair-grouped CI），与 RS_q/BF_q 配对差；报告是否显著增量。
3. 假阳性分解：把"原答正确但反转下不变（镜像答错）"的面板挑出来，看它们在 removal/λ 轴上与
   真正错误面板能否分开（直接回应"正确共识也会不变"的审稿质疑）。
4. 结论 stress_profile/decision.md：多轴轮廓是否值得进论文（增量显著=进；否则=降为诊断图）。

交付：stress_profile_analysis.md、decision.md、scripts/、SUMMARY.md（5 行中文）。
只写 round7/stress_profile/；不 git commit；不改协议数字（新增统计一律标注 post-hoc）。
