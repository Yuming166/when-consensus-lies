# Agent A（概念重述 / R1）摘要
1. 形式化 R1：单 agent 层 BF_reverse 在"原答正确"时恒等于镜像项正确率、原答错误时互为补数；共识两层聚合下，错误共识中 Qwen 90.5% / Ling 97.1% 的 agent 调用保持原错答（即镜像项判对）、仅 9.5% / 2.9% 翻转，0.703 vs 0.029 由镜像 gold 与错误共识答案的标签对齐完全解释。
2. 机制叙述从 evidence insensitivity / stress-testing framework 降为 counter-evidence responsiveness，产出 method_narrative_v2.md（定位+收窄 claim+保留证据）、mirror_equivalence_analysis.md（证明+decoupling）、rewrite_suggestions.md（round3/round4/README 的 diff 式改写，供 Agent F）。
3. 未改任何已报告数字（AUROC 0.943/0.896、Risk@80 0.846/0.422、placebo 0.038、permutation、reducibility、0.703/0.029 原样引用附路径）；decoupling 计数为冻结 records 只读派生（decoupling_audit.py/.json 同目录）。
4. 边界：零新增模型调用、未写其他目录、未 git commit、无因果识别；BoolQ 特异性负结果与自然反证的具体性边界保留。
