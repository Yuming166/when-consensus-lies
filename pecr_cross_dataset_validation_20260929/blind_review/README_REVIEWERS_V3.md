# MultiHiertt 三世界构造盲审说明（V3）

## 目的

本盲审用于检查 MultiHiertt DEV 冻结候选中的财务反事实构造是否合理。它不是模型效果评估，也不是对全部候选题目有效率的估计。样本由预先固定的随机规则抽取，不能根据审阅结果换题或补题。

本包包含 60 个题目，来自 60 个不同的 document-proxy group，并按四类运算各抽取 15 题。每题包含 original、positive 和 negative 三个 world。包中不提供 program、gold answer、expected direction、correctness label、模型回答或风险分数。

## 文件

- `MULTIHIERTT_BLIND_REVIEW_PACKAGE_V3_REBUILT.json`：只读审阅材料。
- `MULTIHIERTT_BLIND_REVIEW_FORM_V3_REVIEWER_A.tsv`：Reviewer A 独立填写表。
- `MULTIHIERTT_BLIND_REVIEW_FORM_V3_REVIEWER_B.tsv`：Reviewer B 独立填写表。
- `MULTIHIERTT_BLIND_REVIEW_MUTATION_VALIDATION_V3.json`：自动生成与格式完整性检查；不是人工有效性结论。

## 盲审规则

1. 两位审阅者必须独立完成，不要互相讨论，也不要查看对方的表格。
2. 只使用 JSON 包中的题目、段落和三张表。不得查找或读取原始 program、gold answer、模型输出、风险分数、正确性标签、expected direction、旧值/新值内部字段或其他未随包提供的信息。
3. 不要修改 JSON 包，不要删除任何题目；即使题目明显无效或无法判断，也必须保留该行并填写结果。
4. 每道题分别判断：
   - 编辑位置：被标记的表格单元格是否确实是一个可识别、可解释的财务数值；
   - 财务语义：original、positive、negative 的数值变化是否与表头、行列、年份和附近文本相容；
   - 单位一致性：三种 world 是否保持相同单位、量纲和格式含义；
   - positive world：在不改变问题其他条件时，编辑是否表示合理的增加/正向变化；
   - negative world：在不改变问题其他条件时，编辑是否表示合理的减少/反向变化；
   - overall：该三 world 构造是否足以用于后续算法实验。
5. 结果字段只使用：
   - `VALID`：所有关键检查均通过，且三 world 的含义清楚；
   - `INVALID`：至少一个关键检查明确失败；
   - `UNCERTAIN`：信息不足或存在无法解决的歧义，不能可靠判定为 VALID。
6. `reason_codes` 请使用逗号分隔的代码（可多选）：
   - `EDIT_LOCATION_OK` / `EDIT_LOCATION_BAD`
   - `FINANCIAL_SEMANTICS_OK` / `FINANCIAL_SEMANTICS_BAD`
   - `UNIT_OK` / `UNIT_BAD`
   - `POSITIVE_DIRECTION_OK` / `POSITIVE_DIRECTION_BAD`
   - `NEGATIVE_DIRECTION_OK` / `NEGATIVE_DIRECTION_BAD`
   - `TEXT_CONFLICT`
   - `INSUFFICIENT_CONTEXT`
   - `OTHER`
7. `notes` 用简短文字说明依据。若选择 `INVALID` 或 `UNCERTAIN`，请明确指出是哪一个表格、单元格或语义关系导致问题；不要填写模型正确性判断。
8. 审阅日期和审阅者标识请按实际情况填写。不要代填另一位审阅者的信息。

## 交付方式

完成后分别保存各自的 TSV，不要合并或覆盖对方文件。将两份填写后的 TSV 连同审阅者标识、日期和任何独立备注返回项目负责人。后续只能由项目负责人按预先规定的规则汇总分歧；Codex 不代替审阅者做判断，也不把一个样本的结果外推为全部 504 个冻结候选的有效率。

## 重要限制

“60/60 VALID”（如果出现）只能表示这 60 个被抽样题目被审阅者判为 VALID，不能表述为 MultiHiertt DEV 全部构造有效，也不能称为 report-level independent confirmation。项目总体定位仍是：`NO-GO for report-level independent confirmation; conditional GO for algorithm-frozen cross-dataset DEV reproduction`。
