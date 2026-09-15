# Round 7 / W1 — Label-Leakage Audit（P0-3）

- 日期：2026-09-14；Agent W1（P0 审计）。
- 状态：只读静态审计 + 代码/产物追踪；零新增模型调用。
- 复现：`consensus_stress/round7/audit/scripts/leakage_audit.py` →
  `leakage_audit_evidence.json`。
- 追踪路径：prompt 构造 → 证据生成 → 打分 → 模型选择 → 阈值选择。

## 0. 审计对象与“泄漏”定义

本审计检查：基准的 gold label（SUPPORTS/REFUTES）是否在**模型调用/证据构造/得分计算/
模型与阈值选择**的任一环节进入，从而让 `RS_q` 的事前可计算性失效。评价阶段（特征冻结后
合并标签算 AUROC/Risk@80/配对差）不属于泄漏，属正常评估，但需确认没有把标签用于
**选择**（cohort/模型/阈值/方向/操作点）。

## 1. Prompt 构造 — 无泄漏

- 冻结代码 `round3/round3_lib.py::build_messages`：system = persona；user = claim +
  evidence_packet（E01..E03 文本）+ JSON 契约 + agent_id。**不含任何 gold label**：
  静态扫描 build_messages 块内 label 相关 token = 空（`leakage_audit_evidence.json`
  `prompt_code.build_messages_label_tokens == []`）。
- `view.condition` 字段（original/reverse/…）**永不进入 prompt**；条件只决定证据文本
  的映射（`unit_texts`）。这是 mirror_audit §2 逐字等价成立的原因，也意味着
  “reverse 提示含答案”的泄漏路径不存在。
- `Composite.gold_label` 仅用于 item 簿记（item_id 后缀 support/refute），不进入
  build_messages（已验证 `gold_label_in_messages_builder = false`）。

## 2. 证据生成 — 无泄漏

- **自然对选择**（`prepare_selection.py`，离线）：
  - 过滤条件全部与标签无关：每页一对（character_ratio 降序、token_jaccard、case_id）、
    cr ≥ 0.85 ∧ tj ≥ 0.70、排除冻结 V3.16/V3.16.1 页面与 round2 已用 pair_id、
    排序 = sha256(SALT + page)。无任何模型输出或后续 outcome 参与。
  - 代码显式声明 `label_use = "gold label used ONLY offline to construct the balanced
    design; never sent to agents, never used in probing or scoring"`。
  - gold label 在 selection_manifest 中出现是自然对定义本身（同一 claim 的 SUPPORTS/
    REFUTES 文档构成配对），是基准的构造标签，不是推理阶段的答案泄漏。
  - stage 1/2 拆分按索引，stage 2 仅由 stage-1 完整率/审计（≥0.95 有效记录）决定，
    **不用任何 outcome**（`run_agents.py` 注释与代码）。
- **Paraphrase 生成**（离线，缓存）：`PARAPHRASE_PROMPT` 只含证据文本，无 label token
  （扫描为空）；900 units，899 可用（unusable 0.11%）；语义保持审计按预注册 ≥80% 抽样
  （`paraphrase_audit.json`/`relevance_audit.json`）。生成结果不含答案，只含复述文本。
- **Distractor**：`token_jaccard(claim, D) ≤ 0.05`、确定性选择，与标签无关。

## 3. 打分（score computation）— 无泄漏

- `round3/features.py` 是 records（模型答案）的纯函数：**不读取任何标签**
  （features.py 中无 gold_label/labels_ledger 引用；唯一 “label” token 是 docstring
  “NO label fields”）。
- `preoutcome_features.jsonl` / `ling_preoutcome_features.jsonl`：扫描全部 key，
  gold/label/wrong/consensus_wrong/outcome/truth 相关 key = **空**
  （`leakage_audit_evidence.json` `features_label_free.*.scan.label_token_keys == []`）。
- `labels_ledger.json`：`status = "sealed_until_preoutcome_features_are_frozen"`；
  只含 `item_id` + `gold_label` + protocol + status；sha256 `770ede3f…` 与
  round5 预注册记录的冻结哈希一致。标签只在 `analyze.py::load_merged`（特征冻结之后）
  合并计算 `consensus_wrong`。
- 关键代数事实：`bf_reverse`/`rev_flip_rate` 是 y_j(a) 与 flip(y_i(a)) 的比较，只依赖
  模型答案与翻转运算符，不依赖 gold；gold 只影响解读（镜像 gold = flip(G_i)），
  这是 mirror_audit 的构造性纠缠，不是泄漏。

## 4. 模型选择 — 无 outcome 后选择

- Qwen3.5-4B：round3 预注册冻结于任何 round3 调用之前（`round3/preregistration.md`
  Status: FROZEN before ANY round-3 model call）。
- Ling-3.0-tiny：round4 预注册冻结于任何 round4 调用之前（`round4/preregistration.md`），
  作为第二模型做跨模型复现；协议仅改响应契约（agent_id 省略 + 固定 exemplar），
  证据/oracle/条件/得分/门全部不变。模型与调用参数在各自标签合并之前即已固定。
- round5（外部 baseline）在预注册冻结后调用，未新增模型；round6 cost-curve 复用同一模型。
- 无“先看结果再选模型”路径：所有模型调用都在其预注册冻结之后、标签合并之前发生。

## 5. 阈值/方向/操作点选择 — 无 post-hoc 选择

- HC 子集阈值 `agreement ≥ 0.8`：预注册 §5（round3），冻结于调用前。
- `RS_q = -BF_q`（higher = riskier）：预注册 §5，冻结于调用前（`gate2_decision_paper.md`
  明示 “Risk form RS_q = -BF_q …, frozen before calls”）。
- E2 主门（AUROC CI lb > 0.5 且 point ≥ 0.60）、E3 macro、E4 worst-label、E5 placebo
  （paraphrase flip ≤ 0.30）、E6 permutation（1000）、E7 reducibility、Phase 4
  Risk@80 coverage=0.8：全部预注册。
- `gate2_decision_paper.md` 明确 “No post-hoc sign flip, no silent cohort/metric repair”。
- round5 校准 baseline（isotonic/temperature）是**唯一使用标签的 baseline**：标签只在
  预指定的 pair-grouped 5-fold OOF 内拟合，不用于选择 prompt/采样/聚合/模型/阈值/门
  （round5 预注册 §2 明示）。已如实披露为 label-using。

## 6. 标签盲产物（额外证据）

- round5：`qwen_baseline_scores_label_blind.jsonl` / `ling_baseline_scores_label_blind.jsonl`
  （标签合并前写入并哈希；扫描无 label key）。
- round6 cost-curve：`probe_scores_label_blind_qwen.jsonl` / `probe_scores_label_blind_ling.jsonl`
  （标签盲；扫描无 label key）。
- 这些文件的存在与哈希（见 evidence JSON）支持“打分先于标签合并”的流程声明。

## 7. 结论：未发现确认的泄漏路径

沿“prompt 构造 → 证据生成 → 打分 → 模型选择 → 阈值选择”逐条追踪，**未发现标签进入
事前计算或选择环节的路径**：prompt 无标签；证据文本按构造生成、无答案；特征文件无标签字段；
标签在特征冻结后仅用于评估；HC 阈值、RS_q 方向、门限、操作点全部预注册；模型调用均在
预注册冻结后发生。round5/round6 的标签盲分数文件进一步佐证流程防火墙。

## 8. 仍存在的风险点（如实列出）

1. **构造性纠缠（最重要）**：reverse 轴的 oracle flip(y0) 与镜像 gold = flip(G_i) 对齐，
   使 BF_reverse 成为“配对项答案 + 标签对齐”的 re-encoding（mirror_audit §6）。这不是
   泄漏（模型没看到标签），但会让审稿人质疑主信号的独立性——这正是 NAACL 计划 §2 的
   核心 objection，**只有 W2 独立反证实验能打破**。
2. **协议设计污染（non-leakage risk）**：reverse 轴定义与方向（flip 期望）在 round2
   早期数据上成型后冻结；round3 与之页面/pair 不相交，故无逐项泄漏，但审稿人可质疑
   “协议围绕现象设计”。缓解：round2/round3 数据不相交 + 全部预注册。
3. **防火墙是程序性而非密码性**：selection/paraphrase manifest 含构造性标签
   （自然对定义所需）；若某流程在文档记录之前合并标签，单凭产物无法检测。现有证据为
   冻结哈希 + ledger seal 状态 + 代码路径；建议在发布材料中保留该审计与哈希链。
4. **校准 baseline 是 label-using**：isotonic/temperature 在 OOF 内用标签（已披露）；
   若读者误读为 outcome-blind 会高估其方法学地位，报告中需持续标注。
5. **评估期的标签使用**：AUROC/Risk@80/配对差在标签合并后计算，属于评估而非选择；
   但 coverage=0.8、HC=0.8 等操作点必须保持预注册值（当前一致，无 post-hoc 切换）。
6. **残余模型非确定性**：reverse(i) 与 original(j) 逐字相同但 Ling 有 11/3000
   agent-call 答案不一致（parse-repair/模型侧），不影响泄漏结论，但在逐项相等类
   声明中应注明（见 mirror_audit §3）。
