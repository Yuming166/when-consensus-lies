你是 round7 的 Agent W2b（严格版独立反证实验 + 审稿人报告）。工作目录
/home/gaoym/when-consensus-lies-publish-20260911。必读（按优先级）：
- consensus_stress/round7/ind_ce/TARGET_SPEC.md（用户冻结的严格目标，最高准则）
- NAACL_Main_Revision_Autoresearch_Plan.md（§3/4/5/16/22）
- consensus_stress/round7/ind_ce/preregistration.md（W2 现有协议，可参考但不复制其 label-coupled 生成）
- consensus_stress/round7/ind_ce/（W2 产物：e_ind_artifacts.jsonl、records_*.jsonl、run_summary_*.json、
  scripts/；只读，不修改）
- consensus_stress/round6/large_model/relay_large_model_run.py（中转批量调用/重试模式）

目标：按 TARGET_SPEC 做**严格版**独立反证实验，写 review-oriented report。写目录：
consensus_stress/round7/ind_ce_strict/（全新目录，与 W2 完全隔离，禁止写 round7/ind_ce/）。

流程（全部先预注册到 ind_ce_strict/preregistration.md 并哈希）：
1. 预注册：cohort=round3 selection 前 50 项（25 对，确定性顺序；与 W2 的 100 项子集有重叠没关系）；
   生成与推理模型 gpt-6-astra（OPENAPI_CENTER_API_KEY 环境变量，直连 HTTP，重试 8 次/退避）。
2. 严格生成 E_ind_strict：对每个 claim（不读 item_id 后缀极性、不读 labels_ledger、不用模型原答），
   只给 claim 文本，要求 gpt-6-astra 分别生成"支持 claim 为真"与"支持 claim 为假"两段证据
   （temp 0.7，max_tokens 300，2 句/段，具体事实，禁 meta 词）；**离线**用冻结 gold 分配
   E_ind_strict(i)=反对该 item gold 的那份。审计 30 条：决策相关（≥0.80）、与 E_j 的
   jaccard/char/LCS 门限、以及"生成输入不含极性/gold"的日志核验。
3. 匹配 placebo E_pm：同一 claim 同长度/语气/格式生成"既不支持也不反驳 claim 的主题相关段"
   （决策不相关但表面匹配）；审计格式匹配 + 决策无关。
4. 推理：5 personas × {ind_strict, placebo_matched}（natural 复用 W2/round6 已有 gpt 记录，不重跑；
   flip 用冻结 gpt 原答）。50 项 × 5 × 2 = 500 次调用；smoke 20 项先行，pipeline valid≥0.95。
5. 分析（label-blind 打分→冻结→合并 label）：Δ_CE=P(flip|ind)−P(flip|pm) [pair-grouped CI]；
   S_ind_strict 单独 AUROC/Risk@80；S_ind_strict 相对 RS_q/S_natural 的 paired 增量（bootstrap）
   与 ρ(S_natural, S_ind_strict)；placebo ceiling（≤0.30）；leakage audit（推理 prompt 无
   gold/target/原答）。
6. 负结果处理：Δ_CE 不显著>0 / S_ind 无增量 / placebo 不干净 → 如实记录 negative，
   **不优化方法**；判定论文应否收窄为 natural-pair consensus fragility phenomenon。
7. 交付 ind_ce_strict/：
   - preregistration.md、execution_notes.md、run_summary_*.json、records.jsonl、preoutcome_features.jsonl
   - analysis/（含全部 CI 与 paired 检验）、artifact_hashes.json
   - **decision.md（reviewer-oriented report）**：明确写
     (a) W2/W2b 成功/部分成功/失败分别意味着什么（对论文 claim 的三种路径）；
     (b) 当前方法最合理、最不夸大的最终 claim（一段可直接进论文 limitation/conclusion 的英文表述）。
   - SUMMARY.md（5 行中文）
纪律：causal/protocol validity 优先；不 git commit；不写 round7/ind_ce/；最多 50 项。
