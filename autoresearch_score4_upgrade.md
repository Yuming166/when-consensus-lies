# AutoResearch 指令：When Consensus Lies → CST 升 4 分冲刺（Score-4 Upgrade）

目标：把当前"审稿人共识估计 ~3/5"的 When Consensus Lies → Consensus Stress Testing
提升到**可辩护的 4/5（NAACL main 口径）**。以**多个 agent 并发**方式执行；任何 agent 的
输出都必须可审计、可复现、边界诚实。本指令冻结研究定位与纪律；具体实验一律先预注册。

## 0. 目标定位（先冻结，禁止事后改）

- 新定位（必须采用）：**"counter-evidence responsiveness（反证响应性）作为已形成多
  agent 共识的事前选择性路由信号"** + CST-Bench 基准 + 诚实边界。不再用
  "consensus stress testing framework / expected-response faithfulness / evidence
  insensitivity" 作为机制卖点。
- 必须正面处理的核心事实：`BF_reverse ≡ 模型在自然反证（镜像项）上的正确率`。
  机制叙述从"证据不敏感"降为"错误跨近重复自然对相关 → 可事前预测共识错误"。
- 非目标：不做通用 SOTA、零样本、因果识别声明；不 tune 冻结协议刷分；不把探索性
  结果包装成正式结果；不删除 FAIL/BLOCKED 记录。

## 1. 编排模型与密钥纪律

- 默认编排：服务器 Codex 默认模型（当前 banner 为 ark/glm-5.3；以实际运行 banner 为准）。
- 可选编排/审稿模拟：私有中转 openapi.center（baseURL `https://openapi.center/v1`，
  wire_api=responses）。**必须先过能力门，未过不得依赖**：
  1. `GET /v1/models` 200 且含目标模型；
  2. 一次最小 Responses 调用 `status=completed` 且返回文本，记录 model id；
  3. 同一模型连续 3 次短调用稳定（无 502/429/timeout/"No available accounts"）；
  4. Codex 自定义 provider 必须 `wire_api="responses"`（0.154 拒绝 chat）。
- 密钥纪律：**key 只允许来自环境变量 `OPENAPI_CENTER_API_KEY` 或既有
  `~/.codex/private.config.toml`，禁止写入任何文件、日志、git、记忆、输出**。
  若 key 曾在聊天/命令中出现过，视为已暴露，用后必须建议用户轮换。
- 研究模型调用：本地 Qwen3.5-4B `127.0.0.1:31518`、Ling-3.0-tiny `127.0.0.1:31520`
  （不发送 reasoning_effort）。大模型验证见 Agent D。

## 2. 并发工作流（每个 agent 一个独立写目录，禁止交叉写）

所有新产物放 `consensus_stress/round6/` 下；A/B/C/E **只读冻结数据、零新增模型调用**。

### Agent A — 概念重述与机制审计（R1）→ round6/reframing/
- 任务：重写方法/机制叙述，正面处理 `BF_reverse ≡ 镜像项正确率`；给出 decoupling 分解
  （错误共识中多少 agent 在镜像项仍错 / 翻转），讨论与"刚性"的等价性；把
  "expected-response faithfulness" 降格为 "counter-evidence responsiveness"。
- 交付：`method_narrative_v2.md`、`mirror_equivalence_analysis.md`、对 round3/4 关键段落的
  改写建议（diff 式）。
- 约束：不改任何数字；不引入因果 claim；保留 placebo/permutation 证据的叙述。

### Agent B — 成本-收益曲线与最小探针（R2）→ round6/cost_curve/
- 任务：**只用冻结 records**（round3 Qwen 15,000 条 / round4 Ling 15,000 条）计算
  call 预算曲线：reversal-only 探针 1/2/5/10 个 agent-call、25-call RS_q、以及
  reversal+paraphrase 组合，报告各点 AUROC [CI] 与 Risk@80 [CI]（pair-grouped bootstrap，
  复用 round5 的协议与 seed 规则）。
- 交付：`cost_curve.md` + 把 `reversal-only (5 calls)` 作为一行 baseline 加入
  `benchmark/leaderboard`（更新 csv/json/md 与 README 的 budget 说明）。
- 约束：label-blind；不新增调用；若 5-call 探针 ≥ RS_q 在 CI 内，**主动采纳成本故事**并把
  25-call 主张降级（这是诚实的好结果，不是失败）。

### Agent C — 可归约性与 baseline 审计（R3）→ round6/reducibility/
- 任务：
  1. 计算 RS_q/BF_q 与 R_sym、R_PI、flip-rate、disagreement、confidence 的 Spearman 与
     增量 AUROC（在 HC 子集上、pair-grouped CI），回答"RS_q 是否只是 R_sym 换权重+paraphrase"；
  2. 把 self-consistency / SelfCheckGPT / binary semantic entropy 三个同分布变体在
     leaderboard 中合并为一行"sampling-consistency family"，正文明确其为 adapted proxies；
  3. 审计外部 baseline 忠实度声明（哪些是原方法、哪些是二值/answer-match 变体）。
- 交付：`reducibility_report.md`、更新后的 leaderboard 与 README。
- 约束：只读冻结记录；不改方法公式。

### Agent D — 大模型单点验证（4 分硬门槛）→ round6/large_model/
- 前置：能力门（见 §1）。目标模型：优先 `gpt-6-astra` 或 `gpt-5.6-sol`，备选 `gpt-5.5`。
- 流程（全部预注册后才调用）：
  1. `preregistration.md` 冻结 cohort（复用 round3 冻结 300 对/600 项）、契约
     （answer/confidence/citations；agent_index 服务端绑定，若模型缺 agent_id 则按 round4
     适配记录）、温度 0、max_tokens、budget、门控（pipeline valid≥0.95、within-model
     AUROC CI lb>0.5、placebo≤0.30、permutation、机制 fidelity correct-wrong CI 排 0）；
  2. 20-item smoke（150 calls）→ 若 parse yield <0.95 或错误率过高，记录并停止/降级；
  3. 100–300 item 子集（5 agents × 5 conditions × N）正式跑；稳定且预算允许再补全 600；
  4. 记录 model identity、调用数、parse yield、HTTP/重试统计、token 用量、within-model
     AUROC/Risk@80、机制迁移、以及 Qwen/Ling 冻结分数对该模型错误的迁移 AUROC。
- 交付：`preregistration.md`、`run_summary_*.json`、`records.jsonl`（原始响应留本机）、
  `analysis/large_model_*.md`。
- 约束：label 只能在 score 冻结后合并；**中转不稳时立即停止并记录 BLOCKED/partial，
  禁止用过滤后子集冒充结果**；relay 不可用 → 降级本地 Qwen3.6-35B（若有服务）或如实
  BLOCKED。

### Agent E — 标签平衡与误差质量（SUPPORTS 短板）→ round6/label_balance/
- 任务：错误率匹配/按 label 分层的 AUROC 与 Risk@80（SUPPORTS vs REFUTES，pair-grouped
  CI）；量化"信号主要由 REFUTES 承载"并给出缓解（如分层 bootstrap、条件于 label 的
  报告口径）；评估 SUPPORTS 仅 7 个错误对 worst-label 结论的影响。
- 交付：`label_balance_analysis.md`、可进论文的边界表述。
- 约束：只读冻结记录；不做事后重采样刷分。

### Agent F — 论文重写与定位（依赖 A–E，最后执行）→ round6/paper/
- 任务：基于 A–E 输出重写 abstract / intro / method / claim / limitation：
  新定位一句话 + 反证响应性机制 + 5-call 成本故事 + 可归约性 + 大模型证据 + 标签平衡 +
  BoolQ 特异性负结果 + CST-Bench 复现。
- 交付：`paper_delta.md`（diff 式）+ `abstract_v2.md` + `reviewer_response_template.md`
  （对 R1/R2/R3 的正面应答）。
- 约束：不得引入未被 A–E 支持的数值；所有数字带 CI 与出处。

## 3. 并发编排与合并协议

1. 启动：A、B、C、E 并行 spawn（只读冻结数据，写目录不相交）；D 可在能力门通过后并行；
   F 等待 A–E 完成后再启动。
2. 每个 agent 启动前在 `registry.yaml` 登记（round6 条目，status=running）；结束时更新
   status + 产物清单 + claim 边界。
3. 冲突仲裁：B 与 C 都会改 `benchmark/leaderboard` —— 由主编排串行化这两处写操作
   （B 先加行，C 后合并家族行；或统一让 C 收尾）。
4. 主编排不重复做 agent 的工作；只做整合、门控审查、最终汇总
   `consensus_stress/round6/score4_upgrade_README.md`（每项：结论、证据路径、边界、状态）。
5. 不做 git commit/push，除非用户明确要求；工作树保持可审查。

## 4. 门控与纪律（对每个 agent 通用）

- 任何新模型调用前：预注册 + 哈希冻结（如 round5 的 `0a465509...` 做法）。
- outcome firewall：label 合并必须晚于 score 冻结；label-blind 中间产物先写盘并哈希。
- 复用优先：能算的绝不重跑；只有 D 允许新增模型调用。
- 诚实报告：FAIL/BLOCKED/partial 一律保留；不修符号、不事后翻转、不 tune frozen protocol、
  不把 HTTP 成功当结果（须记录 model identity + parse yield + end-to-end）。

## 5. 验收：什么算"升到 4 分"（全部满足才算达成）

1. A：机制叙述重写完成，R1 正面处理；
2. B：5-call 成本故事落地 + leaderboard 新增 reversal-only 行；
3. C：vs R_sym 可归约性报告 + 同分布 baseline 合并 + baseline 忠实度审计；
4. D：至少一个 GPT 类模型的 within-model 结果（或如实 BLOCKED，且 F 相应降级主张）；
5. E：标签平衡/误差质量分析进论文边界；
6. F：abstract/intro/method/claim/limitation 重写完成，所有数字带 CI 与出处；
7. 全流程 registry 可追溯，无未登记的调用；无 force 结论。

## 6. 明确"做不到就承认"的降级路径

- relay 不可用 → D 用本地 Qwen3.6-35B（若有服务）或 BLOCKED，论文主张相应降为
  "两个小模型 + 边界说明"（上限 ~3.5，不虚报 4）。
- B 显示 5-call ≈ 25-call → 采纳成本故事，主方法主张改为"5 calls/item 的选择性路由信号"。
- C 显示 RS_q ≈ R_sym → 主贡献改为"基准 + 复现 + 简洁信号"，不 claim 新启发式。
