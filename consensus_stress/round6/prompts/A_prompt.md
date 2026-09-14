你是 When Consensus Lies -> Consensus Stress Testing 升 4 分战役的 Agent A（概念重述 / R1）。
工作目录：/home/gaoym/when-consensus-lies-publish-20260911。先读主指令
autoresearch_score4_upgrade.md 的第 0/2/4/5 节，再开始。

目标：正面处理 R1 攻击——"BF_reverse 在反转轴上恒等于模型在自然反证（镜像项）上的正确率，
expected-response faithfulness 是标签对齐的 re-encoding"。把机制叙述从
"evidence insensitivity / consensus stress testing framework" 降为
"counter-evidence responsiveness（反证响应性）"。

必读输入（只读）：
- consensus_stress/round3/analysis/analysis.md、round3/analysis/gate2_decision_paper.md
- consensus_stress/round3/preregistration.md（oracle 定义：reversal 期望 = flip(y0)）
- consensus_stress/round4/analysis/ling_adapted_crossmodel.md（机制迁移 0.703 vs 0.029）
- consensus_stress/phase1/claim_attack.md、phase1/novelty_map.md
- consensus_stress/benchmark/README.md

交付（全部写到 consensus_stress/round6/reframing/，不要动其他目录、不要改数字、不要新调用模型、不要 git commit）：
1. mirror_equivalence_analysis.md：形式化证明 BF_reverse ≡ 镜像项正确率（对单个 agent 调用、
   对 consensus 聚合两层），并给出 decoupling 分解——在错误共识中，多少 agent 在镜像项上仍错、
   多少翻转；讨论该等价性对"刚性/证据不敏感"叙述的含义。
2. method_narrative_v2.md：新的方法/机制叙述（counter-evidence responsiveness），
   包含一句话定位、机制 claim 的收窄版本、保留哪些证据（placebo 0.038、permutation、
   reducibility、Risk@80/AUROC 数字不变）。
3. rewrite_suggestions.md：对 round3/round4 关键段落与 benchmark/README 相关句子的
   diff 式改写建议（旧句 -> 新句），供 Agent F 使用。

纪律：不得声称因果识别；不得引入新数字；所有结论附文件路径。
最后用中文写一份 5 行以内的摘要（写到 reframing/SUMMARY.md），说明你改了什么、边界是什么。
