# Round 7 / W4 SUMMARY（融合点 B：λ 曲线可归约性）

1. 在冻结 120 对/240-item phase-3 子集（Qwen HC 225/119/22）上重建 per-item λ 压力特征
   （stress-area、breakpoint、robustness radius，reversal 主/removal 副），stress-area AUROC
   0.948 与冻结 gate 逐位一致（全部标注 post-hoc，零新增调用）。
2. 相对二元 reverse 轴（rev_flip_rate）：stress-area 残差增量 0.476 [0.429, 0.653]（点≤0.5），
   配对差 +0.003；breakpoint/radius 增量 CI 含 0.5 且配对差显著为负 → 曲线无独立预测增量。
3. 相对 RS_q/BF_q：stress-area 增量 0.561 [0.494, 0.664]（CI 含 0.5），配对差 −0.017 被支配 →
   同样可归约；相对 R_sym 的增量（0.870）与 round-6 同源，不改判。
4. 判定：λ 曲线可归约 → 不升为正式特征贡献，保留为 interpretability/机制图；冻结 stress-area
   gate 保持原样作为机制确认；Ling 无 λ 记录，λ 曲线可归约性 NOT EVALUABLE。
5. 交付：lambda_features_analysis.md、decision.md、scripts/（4 个零调用脚本）、结果 JSON；
   全部为 120 对子集口径，不冒充全 cohort；未 git commit。
