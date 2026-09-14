# Agent E 摘要（label balance / 误差质量，round6）

1. 信号在两个 label 内都成立：Qwen 分 label AUROC SUPPORTS 0.917 [0.819,0.999] / REFUTES 0.986 [0.973,0.995]，Ling 0.881 [0.834,0.928] / 0.957 [0.934,0.977]，均 CI lb>0.5；SUPPORTS 7 个错误（Qwen）7/7 落在 label 内风险最高 27%，Mann-Whitney p≈4e-6，非噪声。
2. “信号由 REFUTES 承载”在描述层面成立且可量化：REFUTES 错误质量占 89.2%（Qwen）/89.1%（Ling），pooled AUROC 的 concordance 份额 89.3%/88.9%，与错误占比几乎一致、未不成比例放大。
3. 错误率匹配（post-hoc 诊断，非 gate）：把两侧错误数匹配后 pooled AUROC 仍 ≈0.92（Qwen）/0.875（Ling），CI 下界 ≥0.84——信号不是标签不平衡的伪影；但冻结 pooled 0.943 确被 REFUTES 高质量排序部分抬升，论文应以分 label 为主口径。
4. worst-label 稳健性：SUPPORTS leave-one-out jackknife AUROC 在 [0.903,0.944]（Qwen）/ [0.872,0.886]（Ling），全部 >0.8，无单点驱动；但 Qwen SUPPORTS−REFUTES 差异 CI 含 0，只能称“数值最差”，Ling 才显著（CI 排 0）。
5. 措辞：构造对称（300+300 项、同证据/提示）≠ 错误率对称（8.3–8.7× 不对称、跨模型一致，是行为发现）；limitation 段落与主报告口径见 label_balance_analysis.md §4.3/§5，零新增模型调用、只读冻结数据。
