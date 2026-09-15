你是 round7 的 Agent W2（最高价值新实验：独立反证 vs 自然反证 vs 安慰剂）。
工作目录 /home/gaoym/when-consensus-lies-publish-20260911。必读：
- NAACL_Main_Revision_Autoresearch_Plan.md（§3/4/5/16/22，三条件实验与防火墙）
- consensus_stress/round6/large_model/relay_large_model_run.py（可复用的中转批量调用模式）
- consensus_stress/round3/run_agents.py、pilot_lib.py（冻结 prompt/契约）
- consensus_stress/round3/selection_manifest.json（cohort）
- consensus_stress/round6/paper/revision/revise_with_astra.py（中转调用范例）

目标：构造"独立反证证据包"E_ind——支持相反结论、决策相关、**不与配对镜像证据逐字相同**、
不暴露 gold label 到推理 prompt；然后做三条件对比 P(flip|natural) vs P(flip|ind) vs P(flip|placebo)，
核心量 Δ_CE = P(flip|ind) - P(flip|placebo)。研究模型用 gpt-6-astra（中转，OPENAPI_CENTER_API_KEY 环境变量）。

流程（严格顺序，全部先预注册）：
1. preregistration.md（冻结+哈希）：cohort=round3 selection 前 100 项（50 对，确定性顺序）；
   E_ind 生成 prompt（只用 claim+原文证据+目标结论方向，**推理 prompt 永不包含 gold label 或目标结论**）；
   生成模型 gpt-6-astra、temp 0.7、max_tokens 300；审计样本 30 条（决策相关 + 与 E_j 的 token 重合度上限）；
   推理条件 natural/ind/placebo × 5 personas；温度 0；门控：pipeline valid>=0.95、Δ_CE 方向与 CI、
   placebo flip 上限；outcome firewall（label 只在特征冻结后合并）。
2. 生成 E_ind（100-150 条，gpt-6-astra 直连 HTTP，并发~10，retry，cache 到 round7/ind_ce/cache/），
   记录 model id、HTTP 统计。审计 30 条（决策相关率、与 E_j 重合度、独立性）。
3. 20-item smoke（20×5×3=300 calls）→ parse yield>=0.95 才继续；否则按预注册适配或停止。
4. 正式 100 项 × 5 agents × 3 conditions = 1,500 calls（gpt-6-astra 直连，并发~13），
   错误率过高（连续 20 次 503/429/超时）立即停止并如实 partial。
5. 指标：三条件 flip 率与 Δ_CE [CI]；S_natural、S_ind、combined、S_placebo、S_pair（来自 W1）的
   AUROC/Risk@80（pair-grouped 2000，seed 20260914+idx）；S_ind 相对 S_natural 的增量（OOF logistic，
   label-free 特征先冻结）；ρ(S_natural, S_ind)。全部 label-blind 打分→冻结→合并 label。
6. 结论写进 ind_ce/decision.md：独立反证是否成立？Δ_CE 是否>0 且 placebo 干净？S_ind 是否有增量？
   如实报告；若 E_ind 构造失败/与镜像不可区分/Δ_CE<=0，按计划 §6 走（收窄 claim），不制造阳性。

交付：preregistration.md、execution_notes.md、run_summary_*.json、records.jsonl（本机）、
preoutcome_features.jsonl（label-free）、analysis/ind_ce_*.md+json、figures/、artifact_hashes.json、
SUMMARY.md（5 行中文）。只写 round7/ind_ce/；不 git commit；最多 100 项。
