# Raw+Arithmetic44 论文修订记录

## 主线与结构

1. 保留原稿开场：自信、一致的答案仍可能错误，可靠性评估需要观察证据变化后的反应。
2. 收束挑战：方向和响应形状并不能确定回答对应了哪一种算术关系。
3. Benchmark：依赖关系修复的三世界构造、全量单人审查、同代回答绑定、两类复用方式与完整覆盖。
4. Method：Raw 基础 → 算术候选 → 逐世界匹配 → 跨世界持续性 → 44 维表示与固定监督学习。
5. Experiments：同预算主比较、构造信息控制、特征块消融、现象分析。
6. Appendix：完整维度定义、历史 Raw17 兼容控制、覆盖、额外模型和公司隔离复验。

## 写作处理与段落作用

- Abstract / opening：沿用原稿首句和任务切入，删除已不适用于当前队列的 Curve 增益；改为证据对应的挑战、44 维设计、两个主轨道的实际结果。摘要约 191 词。
- Introduction / opening and challenge：前两段保留原稿的大部分叙事。第三段从干预方向过渡到错误算术关系。
- Introduction / method and advantage：明确说明枚举简单计算、保留跨世界匹配和问题对应；不靠复杂术语掩盖实际实现。
- Benchmark / resource contribution：补入 1,699 构造、1,126 多单元格修改、389 文本更新、9,888 精确请求哈希复建；人工有效性与方向未决分开报告。
- Method / technical content：新增候选元组 pi、匹配集合 M、交并集 I/U、持续性 J、切换 S、联合拟合 F_joint、A44 分块公式。维数严格对应 24+16+4；不声称内部推理溯源。
- Experiments / evidence：所有主表、控制表、消融与现象表来自当前冻结 OOF 或本次固定拟合；旧同名结果不混用。
- Limitations / scope：集中为三段，不在每个结论后重复完整限制清单。保留会改变结果解释的关键信息。

## 旧表与新表的处理

| 旧稿内容 | 新稿处理 |
|---|---|
| 大型相关资源表 | 合入 Related Work，以已核实引用说明关系，避免泛泛功能勾选表 |
| CST 主表与大段讨论 | 从主线移除；其任务与当前 Arithmetic44 不一致，旧稿和历史实验不删除 |
| 原始响应模式 | 用当前严格队列重算，附录 Table 8 |
| 原 Curve 主结果 | 当前六行控制阶梯 + PECR 主结果，Table 2 |
| 旧构造信息控制 | 本次新拟合 Table 4；AP 在附录，历史 Raw17 阶梯独立呈现 |
| Curve 家族消融 | 替换为 Arithmetic44 三块消融，Table 5；AP 附录 |
| 旧数值案例表 | 暂不复用未重新绑定的旧案例，不虚构新版案例 |
| 特征定义 | 新版 G96、Raw16、Curve29、Arithmetic44 完整定义 |
| 覆盖表 | 1699/1597 attempts、1597/1537 strict、全 2241 frame |
| 旧 MultiHiertt、神经基线 | 不作为新版方法证据；说明其历史开发性质，原稿仍保存 |
| 新增补充证据 | 既有 Qwen 公司不跨折五分区结果；Qwen3.7/3.8 较弱结果保留 |

## Claim–evidence map

| Claim | Evidence | Status |
|---|---|---|
| 1699 个构造均有人工 Valid 记录 | 发布包 HUMAN_REVIEW_SUMMARY；项目内原始审查记录 | supported，单人总体裁决，不是双人盲审或绝对语义保证 |
| 修复不止改单个数字 | 当前 edit_spec：1126 多单元格，389 文本补丁 | supported，计数可复算 |
| 可复建模型输入 | 当前审计 9888/9888 request hashes | supported，不承诺新模型输出复现 |
| PECR 对强 Raw 的 AUROC 增益 | Qwen +.0259、DeepSeek +.0250；已有校正区间均正 | supported within current grouped development evaluations |
| edited response 增益不由测试的构造描述符单独解释 | 本次 Raw−construction 两条轨道校正 CI 均正 | supported；不等于完全独立于所有 construction 信息 |
| h,t 本身不能解释当前额外增益 | 本次加 h,t 的区间均跨 0；Raw 和 PECR 都包含 h,t | supported within fixed comparison |
| 所有 44 维模块均有稳定正贡献 | 实际 ablation 不支持 | removed；如实报告不同轨道的块贡献 |
| 任意 Qwen 家族/所有模型均稳定获益 | 3.7/3.8 未通过各自“两对照均优”校正标准 | not claimed，附录保留结果 |
| 新数据独立验证已经完成 | 当前主包无此证据 | not claimed |
| 发布地址已包含新包 | 当前新包未自动推送 | not claimed；提交前补匿名链接 |

## 五维自审

1. **贡献**：方法增益是否仍被归到 Curve？否。中心改为确定性算术对应、跨世界匹配与问题条件信息；Curve 是已开发对照。
2. **清晰度**：读者能否知道44从哪来？能。正文定义24+16+4，附录给全部位置顺序。confidence 用 c，question 用 q，source group 用 g，移除 HGB 梯度推导。
3. **实验强度**：对照是否少拿 h,t 或采用较弱学习器？否。主 Raw 同样拥有 G96、Raw16、h,t，全部使用相同固定 HGB 和 OOF。
4. **评估完整性**：是否只保留有利轨道、只报显著块？否。3.7/3.8 与不显著/负点估计的消融均保留；公司隔离结果单独说明。
5. **方法合理性**：是否泄露 gold 或把匹配误写成真实推理？否。匹配阈值与标签阈值分开，候选仅来自可见表格、回答与编辑位置；论述明确是可观察对应。

尚需投稿前处理：三张最终图片；匿名作者与新包匿名发布链接；以接入正式图片后的版式重新确认页数。当前写作与控制实验完成，不自动保证 ARR 分数或录用。
