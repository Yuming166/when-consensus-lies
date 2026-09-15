1. 全 cohort 验证：600 项上两模型均复现 phase3 反向签名——错误共识反转下更刚性（Qwen rev_flip 0.095 vs 0.843，AUROC 0.931）、移除下更不稳（rem 0.859 vs 0.552，AUROC 0.646），差值与 CI 均显著。
2. 多轴组合无增量：所有固定权重组合与 3 轴 OOF 逻辑回归相对 RS_q 的 ΔAUROC ≤ 0（Qwen 最优 −0.012 [−0.027, −0.000]；Ling 显著为负），加移除轴反而显著更差；Risk@80 无增量。
3. 假阳性分解：正确但反转不变的面板真实存在（consensus-rigid 占正确面板 13.9%/27.3%），removal 轴在 λ=1 无法与真正错误分开（AUROC 0.50/0.46），paraphrase 仅小部分分离（0.58/0.60）。
4. 判定：多轴轮廓对冻结 RS_q 无显著增量且不能修复刚性假阳性 → 降为诊断图 + post-hoc 边界小节，主评分保持 RS_q，不改任何协议数字。
5. 交付：stress_profile_analysis.md / decision.md / scripts/ / figures/ / stress_profile_results.json。
