# CST 投稿证据审计（零模型调用）

日期：2026-09-29。范围仅为 Round 7、natural-reverse 机械等价审计、E1 事后敏感性审计，以及 V3 人工构造审查状态核对。没有启动任何模型/API 调用；没有修改旧阈值、ledger、冻结结果、PECR 主分析或论文主稿。

## 一、实验—控制—观察—能支持什么—不能支持什么

| 实验/控制 | 观察到的原始数字或记录 | 能支持什么 | 不能支持什么 |
|---|---|---|---|
| Round 7 strict independent counter-evidence vs matched placebo | `P(flip|ind_strict)=0.7258`，95% CI `[0.6466,0.8115]`；placebo `0.5141`，CI `[0.4600,0.5772]`；差值 `Δ_CE=+0.2118`，CI `[+0.1160,+0.3097]` | 在该 50-item、5-persona cohort 上，strict 条件的平均翻转率高于匹配 placebo；这提供有限的“相关反证比 placebo 更能引起响应”的行为对比 | 不能称 placebo 惰性：预设 ceiling `<=0.30` 被 `0.5141` 明确超过；不能称独立错误排序已成立；不能外推为通用机制或部署 router |
| Round 7 placebo gate | 预设 placebo gate `P(flip|placebo) <= 0.30`；实际 `0.5141` | 清楚证明控制条件未达到预设惰性门槛；应保留为失败结果 | 不能用正的 `Δ_CE` 追认整个 protocol 成功；不能把“有差异”改写成“placebo clean” |
| Round 7 strict error ranking | high-consensus subset `n=46`，其中 wrong `=3`；`AUROC(S_ind_strict)=0.624`，95% CI `[0.286,0.856]` | 只能说点估计略高于 0.5，但样本极小、区间跨 chance，未提供可靠排序证据 | 不能说 strict counter-evidence score 是独立错误预测器；相对 natural 的 `ΔAUROC=-0.349`，CI `[-0.714,-0.091]`；相对 frozen `RS_q` 为 `-0.318`，CI `[-0.670,-0.106]`，方向反而不利 |
| Natural-reverse prompt audit | reverse(i) 与 paired original(j) 的 prompt 逐字等价 `3,000/3,000`；agent-call answer agreement Qwen `2998/2999=99.97%`、Ling `2989/3000=99.63%`；panel-level `100%/99.83%` | 说明 natural-reverse 不是独立新增证据方向测试；其信号可由 paired-original 行为机械重编码解释 | 不能把 natural-reverse 的高 AUROC 当作独立证据响应机制验证；不能把该轴与 strict independent CE 当作同一种已验证机制 |
| Natural-reverse ranking/reference | Qwen `S_natural AUROC=0.973 [0.912,1.000]`，HC `n=47`；`RS_q=0.943 [0.860,1.000]`；但该轴受上述 prompt identity 约束 | 可报告 frozen protocol 上的行为/预测现象，并同时报告其构造性边界 | 不能声称 causal rigidity、latent responsiveness，或 mirror-independent replication |
| E1 frozen strict parser | hash chain `1,250/1,250` verified；all slots attempted；strict valid `587/1,250`，invalid `663/1,250`；invalid 主要是 schema-field omissions，而非 malformed JSON | 说明 E1 主分析的严格解析覆盖有限，解析失败必须作为主结果边界 | 不能把后续修复当成原始冻结主分析结果；不能把低 strict coverage 隐去 |
| E1 post-hoc bounded parser | recovered `663/663`；587 strict-valid rows retained identical parsed fields | 可做透明的事后 sensitivity analysis，并说明它不是预注册/冻结主结果 | 不能 retroactively repair the primary analysis 或追认 E1 为 confirmatory |
| E1 relaxed placebo/A/A | post-hoc placebo `153/250=61.2%` flips；A/A `0/250=0%`；placebo responses all `yes→no`（153，其他 0） | A/A 稳定；placebo 明显不是预期惰性控制；提示 yes/no forced-choice framing 可能把 irrelevant/insufficient 压成 no | 不能把 placebo 视为 clean sham；不能把单向 flip 解释成已识别的证据方向机制；不能支持错误排序 |
| E1 CE vs placebo, same cases | relaxed same-case `n=250`；placebo `153/250`，CE `174/250`；差 `+8.4 pp`，95% group-bootstrap CI `[-21.9,+30.4] pp`；strict same-case `n=68`，差 `+17.6 pp`，CI `[-19.2,+41.0] pp` | 只能说同案例差异点估计为正但不确定 | 不能说 CE 显著优于 placebo；原先不同 denominator 的 69.7% vs 59.4% 不是有效 paired contrast |
| E1 C1a/C1b placebo implementation | 50 items 中 48/50 intervention strings byte-identical；250 item-persona pairs 中 240/250 request bodies 除 seed 外 identical；relaxed parsed responses `250/250` identical | 说明两种 placebo 不是实质独立的对照复现；应作为 implementation limitation | 不能把 C1a 与 C1b 的一致结果称为两个独立 placebo confirmations |
| V3 full-input human review | 两位 reviewer 各审 `34/34`；用户裁决 3 个分歧（1、3 采 reviewer1，2 采 reviewer2）；最终 `34/34 construction-failure`，`0/17` source groups eligible；model calls `0` | 说明审查工作已记录且未代填模型结果；最重要的发现是候选构造失败 | 不能称 V3 已通过构造有效性、neutral inertness 或 selective-response gate；不能把 reviewer judgment 变成模型证据 |

## 二、Round 7 / natural-reverse / E1 与 V3 的严格分层

### 已观察结果

Round 7 是已完成的 strict independent-counter-evidence pilot，但其 placebo gate 失败。正的 `Δ_CE` 是行为对比，不是完整构念验证。Natural-reverse 的 3,000/3,000 prompt identity 直接限制了其独立性。E1 是 reused cohort 上的 exploratory/post-hoc parser sensitivity audit；严格解析只覆盖 587/1,250，宽松解析下 placebo 仍为 153/250，A/A 为 0/250，且 CE-placebo paired interval 跨零。

### V3 尚无模型结果

V3 的人工审查针对完整四条件输入和逐项目标状态；不是对旧 yes/no 输出的事后三态改写。审查后的状态是：34 道 inherited attempts 全部 construction-failure；0 个有效 source group；没有任何 V3 模型输出。因此以下命题均为**未完成**：

- 构造方向有效；
- neutral 相对 A/A 惰性；
- support/counter 的三态定向响应；
- 错误排序优于 matched strong baseline。

不能用“人工审查已完成”替代“构造通过”，也不能自行补齐缺失材料。

## 三、时间线与事后修订边界

1. Natural-reverse 的 prompt identity 是对冻结数据和协议构造的 post-hoc audit，不是新模型实验。
2. Round 7 原始 formal run 先出现严格解析 `45/50`，随后进行了 documented post-freeze parser correction，恢复至 `50/50`；输入、seed、调用未改，原始时间线仍须保留，不能称 correction 为预注册 parser 结果。
3. Round 7 的 strict CE/placebo 分析保留原 gate：`Δ_CE` 为正且 CI 不跨零，但 placebo ceiling 失败。
4. E1 事后 bounded/relaxed parser 仅作为 sensitivity analysis；不得追认冻结主分析。
5. V3 reviewer adjudication 只解决 3 个语义分歧，不修复缺失的 support/counter 材料；V3 仍为 0 个 eligible source group、0 次模型调用。

## 四、对论文的 GO/NO-GO

### GO（允许写入）

- CST 提供了一个**干预构念有效性的边界证据**：在 Round 7 中，strict CE 的平均翻转率高于 matched placebo（`+0.2118`，CI 不跨零），但这一结论必须与 placebo gate failure 同时呈现。
- Natural-reverse 的主要作用是暴露测量构造的机械等价问题，而非提供独立复现。
- E1 可作为透明的 parser/control sensitivity audit，强调低严格解析覆盖、placebo 非惰性、C1a/C1b 重复和 paired CI 跨零。
- 论文应明确：CST 与 PECR 共享“干预是否引起预期响应”的研究问题，但目前没有证据证明共享机制；PECR 不是 CST 的独立复现，CST 也不是 PECR 的 program-conditioned 复现。

### NO-GO（当前不能写）

- CST 已验证 router、部署就绪或稳定的错误诊断器；
- strict independent CE 已证明优于 strong baseline 的错误排序；
- placebo 已 clean/inert；
- E1 已 confirmatory；
- V3 已通过三态构造/选择性响应门槛；
- CST 与 PECR 已联合验证同一机制。

## 五、来源说明

详细路径和 SHA-256 在 `SOURCE_MANIFEST_SHA256.txt`。本目录只保存审计和写作材料，不复制或修改冻结 records。
