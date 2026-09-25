# 你需要做什么：PECR 人工审阅

## 重要：需要真人判断
这些材料不能由脚本或模型替代。Stage A 构造方向审阅应交给未看过这 20 题模型回答、冻结 expected signs、风险分数和 correctness labels 的独立审阅者。若你本人此前已看过这些逐题信息，你可以检查材料，但不应把自己的判断计作盲法独立审阅。

## A. 20 题构造方向审阅
1. 只把 `CONSTRUCTION_STAGE_A_DIRECTION_BLIND_V2.jsonl` 和 `CONSTRUCTION_STAGE_A_FORM_V2.csv` 交给审阅者。
2. 不发送任何 Stage-B key、BLK/AMT coordinator note 或包含冻结方向的旧文件。
3. 请审阅者逐题填写 minus/plus 方向、计算/语义理由、文本一致性与不确定性，并保留原始回传文件。
4. 收到后不要改动文件；记录审阅者身份（可用匿名编码）和 UTC 日期，计算 SHA-256，再交回项目维护者。冻结并哈希 Stage A 后，才可揭示冻结方向并生成分歧表。

## B. 28 个唯一题目的答案语义复核
1. 请独立审阅者使用 `ANSWER_GOLD_REVIEW_28_UNIQUE_ITEMS_V2.jsonl` 与 `ANSWER_GOLD_REVIEW_FORM_28_V2.csv`，逐题判断回答是否在语义上回答问题、与 gold 的差异属于数值/百分比/单位/舍入/抽取或其他何种原因。
2. 35 条队列记录包含 28 个唯一题目和 7 条重复记录；按 28 个唯一题目填写一次，并保留对应队列序号。
3. 审阅者看得到 gold answer，但看不到冻结 correctness label 和 PECR 风险分数。返回后原样保存并哈希，再与冻结标签比较。

## 完成后
把两份填好的表（以及审阅者匿名 ID、UTC 日期和 SHA-256）交回项目维护者。不要自行改 signs、labels、scores、manifest 或主结果；所有更正只进入明确标记为 post-hoc 的分歧/敏感性分析。
