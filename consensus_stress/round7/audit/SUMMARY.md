# Round 7 / W1 — P0 审计摘要

1. 镜像等价：reverse(i) 与配对项 original(j) 的 prompt 逐字等价 3000/3000（100%），答案一致率 99.97%（Qwen）/99.63%（Ling，agent-call），panel 共识级 100%/99.83%；BF_reverse(i) 是配对 original 答案的确定性 re-encoding，BF_reverse(i)≡BF_reverse(j)（rho≈0.995，逐项相等 99.7%/97.4%）。
2. 配对重建：只用镜像项调用，RS_q(j) 预测 item i 错误达 0.909/0.827（自身 RS_q 0.943/0.896 的 96.4%/92.2%）；只用两个 original 答案的 S_pair 精确重建 reverse 轴（AUROC 0.931/0.869，与 BF_reverse 配对差 0.0000/0.0002，Spearman 0.998）。
3. S_pair 结论：能——S_pair 重建 RS_q 预测力的约 98.7%/97.0%，唯一残余是 paraphrase 轴小增量（RS_q−S_pair = +0.012/+0.027，CI>0 但单独 AUROC 仅 0.60/0.58）；主信号大部分是自然对构造的机械结果，独立反证实验 W2 是唯一出路（如实结论）。
4. 泄漏审计：沿 prompt 构造→证据生成→打分→模型选择→阈值选择逐条追踪，未发现 label 进入事前计算或选择环节的路径（prompt/特征文件无标签、标签在特征冻结后仅用于评估、HC=0.8 与 RS_q=-BF_q 均预注册、round5/round6 分数文件标签盲）；仍存风险=镜像 oracle 与标签对齐的构造性纠缠（非泄漏，需 W2 打破）+ 协议设计污染风险。
5. 产物：`round7/audit/{mirror_audit,s_pair_diagnostic,leakage_audit}.md` + `scripts/{mirror_audit,s_pair_diagnostic,leakage_audit}.py` + 三个 JSON；全部零新增模型调用、只读冻结数据、post-hoc 标签；未 commit。
