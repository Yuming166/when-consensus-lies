你是 round7 的 Agent W5（论文 v5 整合与改写）。工作目录 /home/gaoym/when-consensus-lies-publish-20260911。
必读：
- NAACL_Main_Revision_Autoresearch_Plan.md（§7-§21：三贡献、call 记账、叙述、减防御性措辞、标题、检查清单）
- consensus_stress/round6/paper/naacl_draft_v4_astra.md（当前 v4）
- round7 其他 workstream 产物（audit/、ind_ce/、stress_profile/、lambda_features/ 的 decision.md 与 SUMMARY）
- consensus_stress/round6/paper/sections/（v4 分节来源）

任务（等 W1-W4 完成后执行）：
1. 按计划 §8 重构为三贡献（经验现象/评估协议/实证验证），§9 把 call 记账改为
   "5 consensus + 10 main probe + auxiliary diagnostics"（不再称主方法为 25-call）。
2. 整合 W1-W4 结论：S_pair 诊断、独立反证 Δ_CE（若成立）、多轴轮廓/λ 特征（若进论文）、
   或按计划 §6 收窄 claim。
3. §18 削减防御性措辞（去掉重复的 "We do not claim.../A reviewer might..."），写成自信的科学论证。
4. 更新 title 候选（§19）、摘要、limitation、conclusion。
5. 产出 round7/paper/naacl_draft_v5_astra.md（完整 markdown）+ 对 v4 的 delta 说明
   （paper/paper_delta_v4_to_v5.md）。不生成 LaTeX（主编排后续统一处理）。
6. 每条新表述必须能追溯到 round7 对应产物；数字带 CI；不新增未验证 claim。

只写 round7/paper/；不 git commit；若某些 workstream 未完成，如实标注"待 Wx 结论"并继续其余部分。
