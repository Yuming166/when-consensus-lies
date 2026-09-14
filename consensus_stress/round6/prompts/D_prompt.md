你是 When Consensus Lies -> Consensus Stress Testing 升 4 分战役的 Agent D（大模型单点验证）。
工作目录：/home/gaoym/when-consensus-lies-publish-20260911。先读主指令
autoresearch_score4_upgrade.md 的第 1/2/4/5/6 节（Agent D 一节与降级路径）。

目标：用私有中转 openapi.center 上的大模型（优先 gpt-6-astra，备用 gpt-5.6-sol / gpt-5.5），
在冻结的 round3 VitaminC 300 对 cohort 上跑【100 项】单点验证，产出 within-model 结果与
机制迁移证据。中转不可用就如实 BLOCKED，绝不伪造。

环境：
- 中转：base https://openapi.center/v1，OpenAI 兼容；key 从环境变量 OPENAPI_CENTER_API_KEY 读（已有）。
- 本地研究端点（不要动）：Qwen3.5-4B 127.0.0.1:31518、Ling-3.0-tiny 127.0.0.1:31520。
- 复用：consensus_stress/round3/run_agents.py、pilot_lib.py、features.py、round4 的契约适配
  （agent_index 服务端绑定，若模型缺 agent_id）。

流程（严格按顺序，先预注册再调用）：
1. 健康检查：GET /v1/models；对 gpt-6-astra 发 1 次最小 chat/completions（temperature 0，
   max_tokens 16）；连续 3 次成功才算可用；失败则依次试 gpt-5.6-sol、gpt-5.5；全失败则
   检查本地是否已有 Qwen3.6-35B 服务（pgrep -af vllm；不要启动新 GPU），都没有 -> 写
   BLOCKED 记录并结束。
2. 预注册：round6/large_model/preregistration.md（冻结+哈希）。固定：cohort = round3
   selection_manifest 中前 100 个 pair_id（按 manifest 顺序）；5 条件 × 5 personas；
   契约 answer/confidence/cited_evidence_ids（缺 agent_id 按 round4 方式服务端绑定并记录）；
   temperature 0、max_tokens 160；门控：pipeline valid>=0.95、within-model
   AUROC(RS_q, wrong|HC) CI lb>0.5、placebo paraphrase flip<=0.30、permutation、
   机制 fidelity correct-wrong CI 排 0；outcome firewall（label 合并晚于 score 冻结）。
3. 20-item smoke（20×25=500 calls）：直接 HTTP 并发（~10-16 workers）调
   /v1/chat/completions，带重试与 cache（round6/large_model/cache/）。parse yield<0.95
   时按预注册契约适配（如加 JSON exemplar）或记录 BLOCKED。
4. 100-item 正式跑（2,500 calls），记录 model identity、调用数、parse yield、HTTP 状态/
   重试统计、token 用量。错误率过高（如连续 20 次 503/429 或超时）立即停止并如实记录 partial。
5. 特征与指标：复用 round3 features.py 构建 preoutcome features（label-free，先写盘哈希），
   合并 round3 labels_ledger；算 within-model AUROC/Risk@80（pair-grouped CI）、
   Qwen/Ling 冻结分数对该模型错误的迁移 AUROC、机制 fidelity（correct vs wrong）。

交付（写到 consensus_stress/round6/large_model/）：
- preregistration.md、execution_notes.md、run_summary_*.json、records.jsonl（本机保留）
- analysis/large_model_*.md、figures（如有）
- SUMMARY.md（5 行中文摘要：模型、parse yield、AUROC/Risk@80、迁移、BLOCKED/partial 如实）

纪律：最多 100 项；label 只能在 score 冻结后合并；不得用过滤子集冒充完整结果；
不 git commit；中转不稳立即停止并记录。
