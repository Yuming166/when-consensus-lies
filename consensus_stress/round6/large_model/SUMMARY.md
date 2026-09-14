# Round 6 Agent D — 大模型单点验证摘要（gpt-6-astra @ openapi.center 中转）

1. **模型与执行**：私有中转 `openapi.center` 的 gpt-6-astra 通过能力门（GET /v1/models + 3 次最小调用全 200）；正式跑 100 项 × 5 条件 × 5 personas = 2,500 次逻辑调用（实际 HTTP 约 1,028 次新调用，其余为镜像等价视图 cache 命中；1,785 个 cache 文件），2,483/2,500 有效（parse yield 0.9932），失败 17 条全部为 429/502/400 中转传输错误、**0 条解析失败**，无需契约适配。
2. **Within-model 指标（HC，n=96，wrong=8，错误率 8.3%）**：AUROC(RS_q, wrong|HC) = 0.969 [0.935, 0.995]（CI lb > 0.5，通过）；Risk@80 错误削减 = 1.000 [0.836, 1.000]（8 个错误全部落在最高风险 20%）。
3. **机制迁移**：frozen Qwen RS_q → gpt 错误 AUROC 0.838 [0.693, 0.950]、Ling RS_q → 0.737 [0.568, 0.862]（均 CI lb > 0.5，次要证据）；机制 fidelity（correct−wrong 的 bf_reverse 差）= 0.832 [0.745, 0.928]，CI 排除 0，通过。
4. **门控**：pipeline 0.9932 ≥ 0.95、placebo paraphrase flip 0.039 ≤ 0.30、permutation obs 0.969 > p95 0.894、机制 fidelity 均通过；标签仅在 label-free 特征冻结（SHA256 f1d167aa…）后合并。
5. **边界**：单点 100 项验证（非全 cohort 600 项），HC 错误仅 8 条、CI 宽；2 项因 original 条件传输失败按 round3 特征规则排除（非 outcome 过滤）；未 BLOCKED、未 partial，但属小样本验证，不应外推为全 cohort 或零样本结论。
