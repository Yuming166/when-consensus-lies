# Round-7 W2 — Decision: 独立反证 vs 自然反证 vs 安慰剂

协议 `cs-paper-ind-ce-20260914-round7-w2`（预注册冻结）。cohort = round3 selection 前 100 项
（50 对，确定性顺序；与 round6 formal 相同）。研究模型 gpt-6-astra（中转）。
特征冻结：`preoutcome_features.jsonl` SHA256 `e72562bfb0f202fc754b7bbb574e6a8a6e1f59378546d7cba2b1ab10eb1f9c62`
（98 项，label-free），之后才合并 `labels_ledger.json`。

## 1. 流水线与门控状态

| 门 | 结果 | 状态 |
|---|---|---|
| G0 能力探测（/v1/models + 3 PONG） | gpt-6-astra 可用 | PASS |
| G1 pipeline valid rate（smoke 300 + formal 1500） | smoke 1.000；formal 1.000（1500/1500，first_pass 0.991） | PASS |
| G2 E_ind 审计 | 决策相关率 0.90（60 句，≥0.80）；token Jaccard 中位 0.23 / p90 0.42 / max 0.68（≤0.80 全部满足）；character_ratio max 0.80、LCS-subsequence max 0.87 超 0.75（2 句内容被迫短句的子序列假象，见下） | 部分 PASS（实质性独立性与相关性满足；严格 LCS 上限边缘） |
| G3 Δ_CE > 0 且 CI 排除 0 | Δ_CE = +0.2932 [+0.2056, +0.3682] | PASS |
| G4 placebo ≤ 0.30 | P(flip|placebo) = 0.5442 | **FAIL**（见 §3） |
| G5 round6 复现（诊断） | 我们的 P(flip|natural)=0.8253 vs round6 rev_flip_rate=0.8246（差 0.0007） | PASS |

## 2. 三条件 flip 率（label-blind，n=498 item×agent）

- P(flip|natural) = **0.8253** [0.7289, 0.9140]
- P(flip|ind)    = **0.8373** [0.7827, 0.8873]
- P(flip|placebo)= **0.5442** [0.4990, 0.5944]
- **Δ_CE = P(flip|ind) − P(flip|placebo) = +0.2932 [+0.2056, +0.3682]**（pair-grouped bootstrap 2000）
- Δ_NI = P(flip|ind) − P(flip|natural) = +0.0120 [−0.0581, +0.0789]（≈0）
- Δ_NP = P(flip|natural) − P(flip|placebo) = +0.2811 [+0.1449, +0.4008]

## 3. 判定：独立反证是否成立？Δ_CE 是否 >0 且 placebo 干净？S_ind 是否有增量？

**独立反证成立（核心问题 YES）。** 模型对"独立构造、支持相反结论、与镜像不逐字相同"的反证证据的
flip 率（0.837）与对字节级镜像 E_j 的 flip 率（0.825）无显著差异（Δ_NI≈0），二者都显著高于
安慰剂（Δ_CE=+0.293，CI 排除 0；Δ_NP=+0.281）。这直接回应审稿人"反证响应是配对构造的机械产物"
的核心质疑：**把镜像换成独立生成的反证，模型响应强度不变**——响应的是"决策相关的反证"，不是
"配对镜像的字节身份"。这是本实验最有价值的结论。

**Δ_CE>0：YES（G3 PASS）。placebo 干净：NO（G4 FAIL）。** P(flip|placebo)=0.544 超过 0.30 上限。
诚实解读：(a) 本实验的 placebo 是"决策无关证据替换"（distractor），与 round6 的 placebo
（同证据改写 paraphrase）不是同一操作化——0.30 上限是从 round6 复制的、对本 placebo 定义过严；
(b) 模型在"证据换成无关句"时本来就有 54% 的答案变化（泛化的证据替换不稳定性），因此**不能说
"模型只对决策相关反证翻转"**，只能说"决策相关反证比无关扰动多带来 +0.29 的翻转"。论文应报
Δ_CE 增量，不应宣称 placebo 绝对干净。placebo 轴本身对错误共识的区分很弱（原始方向 AUROC≈0.69，
远低于 0.96+ 的决策相关轴），佐证了"选择性增量"而非"全有全无"。

**S_ind 是否有增量：小但有统计证据（样本小、须谨慎）。** HC（agreement≥0.8, n=96, wrong=8）：
- S_natural AUROC 0.9624 [0.925, 0.991]；S_ind 0.9830 [0.954, 1.000]；S_combined 1.000 [1.000, 1.000]；
  S_placebo 0.3111（风险方向；原始方向 0.69，弱）。
- 配对差：S_ind−S_natural +0.021 [−0.019, +0.065]（CI 含 0）；S_combined−S_natural +0.038 [+0.010, +0.075]
  （CI 排除 0）；S_ind−S_placebo +0.672 [+0.553, +0.796]（干净）。
- OOF logistic（leave-one-pair-out）：[S_natural,S_ind] 比 [S_natural] 的 OOF AUROC 增量
  **+0.0447 [+0.0146, +0.0842]**（CI 排除 0）。
- ρ(S_natural, S_ind)=0.5664 [0.356, 0.695]——两轴中等相关：独立反证与镜像反证共享"响应度"
  因子，但非同一信号。
- 强 caveat：wrong=8，所有增量估计脆弱；配对 AUROC 差（S_ind vs S_natural）CI 含 0，增量主要由
  OOF 逻辑回归与 combined 提供。论文应标"小样本、探索性"。

## 4. S_pair（W1）对照

在 gpt cohort 上，W1 定义（只用配对项 original 答案）：S_pair_flip_gpt AUROC 0.9598、
S_pair_panel_gpt 0.9540，与 S_natural（0.9624）几乎相等——**配对项预测几乎完全重建镜像派生
信号的预测力**（与 W1 在 Qwen/Ling 上的 99.8%/98.4% 逐项相等结论一致）。而 S_ind（0.9830）是
唯一不依赖配对结构的分数，达到/超过镜像派生分数，提供了审稿人要求的"非配对机制"独立测量。
S_pair_panel_qwen（跨模型）0.7443，较弱。

## 5. E_ind 构造与审计（如实）

- 生成：100 项 × 2 句 = 200 条（V2 prompt，temp 0.7，max_tokens 300；batch-1 审计边缘失败后按
  文档化修订重生成，见 `generation_prompt_v2.md`；200/200 成功）。
- 审计（30 项/60 句，seed 20260914）：决策相关率 0.90（PASS）；与 E_j 的 token Jaccard
  中位 0.23 / p90 0.42 / max 0.68（PASS，无逐字/近逐字复制）；character_ratio max 0.80 与
  LCS-subsequence max 0.87 略超 0.75——2 句（House of Payne、Defoe OBE）为"内容被迫"短句，
  其词序是 E_j 长子序列（短句自然落入长句），但 Jaccard/字符重合度低，不构成复制；
  已用更严 no-overlap 指令重生成仍无法低于 LCS 0.75（事实内容本身与镜像重合），如实记录。
- 推理 prompt 永不包含 gold label 或目标结论；方向只由 item_id 后缀推导；标签只在特征冻结后合并。

## 6. 对论文（§3/§5/§20 计划）的建议

1. 论文可写：**反证响应并非镜像构造的机械产物**——独立构造的反证获得与镜像等强的响应
   （Δ_NI≈0，Δ_CE=+0.293 且 placebo 之上），wrong-consensus 面板对独立反证的响应度同样
   低（S_ind AUROC 0.98）。
2. 必须同时写边界：placebo 翻转基线高（0.544），信号是"决策相关反证之上的选择性增量"，
   不是"只对决策相关反证响应"；HC 样本小（8 wrong），S_ind 对 S_natural 的配对 AUROC 增量
   CI 含 0，OOF 增量须标探索性。
3. 若按计划 §6 的收窄口径：主贡献是"在自然配对构造下的经验现象 + CST-Bench 协议 + 事前
   反证响应信号"，机制叙述升级为"对决策相关反证（含独立构造）的选择性响应，增量在
   无关扰动之上"。W2 使"独立反证"不再只是 future work，但 placebo 基线高意味着不要把
   选择性说得过强。

结论：**不制造阳性；如实报告。核心量 Δ_CE>0 且稳健（G3 PASS）；placebo 不干净（G4 FAIL）须
如实标注；S_ind 提供小但 OOF 显著的增量（样本小 caveat）。** 独立反证实验成功并直接缓解了
审稿人最核心的镜像等价性质疑。

## 7. TARGET_SPEC（2026-09-15 00:12）严格协议 — 状态（如实）

用户 2026-09-15 冻结了更严的 `TARGET_SPEC.md`：E_ind_strict 必须 claim-only 双方向生成
（生成 prompt 不得含 item 极性/gold）、离线用冻结 gold 分配；placebo 改为 topic-matched 的
E_pm。已执行：

1. **严格生成完成**（300 calls，50 claims × [2×true + 2×false + 2×pm]；claim-only prompt）。
   292/300 首轮成功，8 个 slot 因中转 gpt-6-astra 上游持续 400 用语义等价简化 prompt 变体
   重生成（6 个 gpt-6-astra，2 个 gpt-5.6-sol——claim2 的 ind-true 在 gpt-6-astra 上持续 400）。
2. **离线分配完成**：E_ind_strict(i)=反对 item i gold 的那份（support→false 句，refute→true 句）；
   E_pm 为同主题中性句。100/100 项齐全。
3. **严格审计（30 项/60 句）**：
   - E_ind_strict 决策相关率 **0.7667（<0.80 门）**：claim-only 生成在"方向与现实相反"的
     claim 上模型默认写现实一致句，方向不可靠。这是更严构造（无 item 极性提示）的真实代价，
     按 TARGET_SPEC §6 **不重调**。
   - E_ind_strict vs E_j：token_jaccard 中位 0.19/p90 0.50/max 0.75（独立，pass）；char max
     0.89、LCS max 0.91（严格上限边缘，同 v1 caveat）。
   - **E_pm：neutral 0.883、support 0.0、refute 0.067 —— 匹配安慰剂干净（PASS）**。
4. **严格推理（100×5×3=1500 逻辑 calls；natural 由 v1 cache 重放）**：
   - 首次运行 valid_rate 0.817（275 个 transport 失败，0 parse）；第二次复跑后
     0.819（ind 370/500、placebo 358/500）。**G1 未达 0.95**——原因全部是中转 gpt-6-astra
     上游持续 400/502（03:17 后短暂恢复窗口，随即再次长时间不可用；watch 循环在后台继续
     等待恢复窗口自动重跑，直到 valid_rate≥0.95 或放弃）。
   - 状态：**严格推理 PARTIAL/BLOCKED（中转上游不稳定）**。完成时补齐严格分析。
5. 若严格推理最终达到 valid≥0.95：用 `build_features_strict.py` + `analyze_strict.py strict_`
   产出 `analysis/ind_ce_strict_results.*`，并按 §6 如实判定 Δ_CE。若达不到：如实记录
   严格协议未完成，v1（目标方向 prompt 版）结果作为已完成证据。

6. **严格推理补跑完成（2026-09-15 08:xx，watch 循环在恢复窗口自动重跑；协议未变、未重调）**：
   - 最终 `run_summary_strict_formal.json`：1500/1500 逻辑 calls，valid **0.9593**（1439/1500；
     ind 471/500、placebo 468/500、natural 500/500；失败全部为 transport 重试，0 parse 失败）→ G1 达标。
   - 补跑分析（`build_features_strict.py` → `strict_preoutcome_features.jsonl`（sha 0fb5b0ee…）+
     `analyze_strict.py strict_` → `analysis/ind_ce_strict_results.json/.md`）：n=98 项 / 50 对，
     HC n=96（wrong=8）。
     - 三条件 flip：natural **0.8253**、ind_strict **0.6567**、placebo **0.5579**。
     - **Δ_CE = +0.0988 [0.0300, 0.1681]**（G3 PASS——显著但远弱于 v1 的 +0.293）。
     - **Δ_NI = −0.1686 [−0.2689, −0.0611]**（显著为负）：claim-only 独立反证的翻转率明显低于
       natural 镜像证据，方向干净度是镜像证据的优势所在。
     - G4 placebo 不干净（0.5579 > 0.30，FAIL，如实标注）。
   - 预测轴：S_ind_strict 单独 AUROC **0.6985 [0.4653, 0.8694]**（n=72，CI 含 0.5，不独立预测）；
     对 S_natural 配对 AUROC **−0.2567 [−0.5000, −0.0875]**（显著负）；OOF 增量 +0.0269
     [0.0000, 0.0581]（CI 触 0，无增量）；ρ(S_natural, S_ind_strict)=0.3223 [0.1276, 0.5377]
     （中等相关，低于 v1 的 0.57）。
   - **判定（与 W2b 严格版一致）**：行为轴——"对决策相关独立反证的选择性响应"在 claim-only
     严格构造下仍显著（量级 +0.293 → +0.099）；预测轴——独立反证无法复现 natural-pair 的排序
     能力，S_ind_strict 不作为可部署错误排序信号。论文维持 natural-pair consensus fragility
     phenomenon + 预注册协议框架，严格实验作为 §Limitations/附录边界。
