# Round 7 W2 Target Spec（用户 2026-09-15 冻结目标）

验证核心现象能否**脱离 VitaminC natural-pair / mirror construction 独立成立**。优先级：
causal/protocol validity > 模型复杂度；一切统计用 paired 检验；全程 label leakage 检查。

## 1. 独立反证 E_ind_strict（严格版）
必须同时独立于：
- (a) 配对镜像 E_j：无逐字/近文本重合（jaccard/char/LCS 门限）；
- (b) **gold label**：生成 prompt 不得使用 item 极性/gold（不得从 item_id 后缀推导方向）；
  采用"per-claim 双方向生成"：对每个 claim 只给 claim 文本，生成"支持该 claim 为真"与
  "支持该 claim 为假"两份证据；之后**离线**用冻结 gold 分配 E_ind_strict(i)=反对 item i gold 的那份；
- (c) **原题答案**：生成与推理都不使用模型原答。
推理 prompt 只含 claim + 该条件证据；永不含 gold/target 结论/原答。

## 2. Matched placebo E_pm
内容长度/语气/格式与 E_ind_strict 尽可能匹配，但**不支持反结论**（与结论方向无关/
决策不相关）：同一主题、相近句子数与长度，既不支持也不反驳 claim。

## 3. 核心比较（consensus agents, gpt-6-astra）
Δ_CE = P(flip|E_ind_strict) − P(flip|E_pm)，pair-grouped 95% CI；flip = 条件答 ≠ 冻结原答。

## 4. 预测有效性（outcome reveal 前）
S_ind（independent responsiveness）单独：AUROC、Risk@80（pair-grouped CI）。

## 5. 增量价值
S_ind 相对已有 RS_q / S_natural 的 paired 增量（pair-grouped bootstrap；可加 OOF logistic）；
ρ(S_natural, S_ind)。若 E_ind 无增量，如实报告，不强行加。

## 6. 负结果处理
若 Δ_CE 不显著>0 或 S_ind 无增量/placebo 不干净 → **明确记录 negative result，不优化方法**；
论文据此收窄为 "natural-pair consensus fragility phenomenon + 预注册基准"。

## 7. 交付
reviewer-oriented report（ind_ce_strict/decision.md）：
- W2 成功/部分成功/失败 分别意味着什么（对论文 claim 的影响）；
- 当前方法最合理、最不夸大的最终 claim 建议。
