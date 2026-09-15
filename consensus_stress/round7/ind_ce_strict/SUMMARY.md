# Round-7 W2b（严格版独立反证）摘要

1. 预注册后完成严格版实验：E_ind_strict 只输入 claim 双向生成、离线按冻结 gold 分配反方证据，placebo 为同主题匹配且决策无关；50 项 × 5 personas × {ind_strict, placebo}，smoke valid 0.995、formal valid 0.998（G1 通过），全程未写 round7/ind_ce/、未 git commit。
2. 审计通过关键严格性：E_ind_strict 与镜像证据文本独立（token jaccard 中位 0.185/最大 0.467，char/LCS 均过门限）、生成输入仅含 claim（30/30 干净）、推理 prompt 无 gold/原答（299 重建校验 sha 全匹配）；方向相关率 0.783（整体，略低于 0.80 门限；实际分配段 0.80），placebo 格式匹配 1.0、决策无关 0.80。
3. 主结果：Δ_CE = P(flip|ind_strict) − P(flip|placebo) = +0.212（95% CI [+0.116, +0.310]，G3 通过）：平均层面“对决策相关独立反证的选择性响应”脱离镜像结构仍然成立。
4. 负结果（如实记录，不调方法）：placebo 不干净（0.514 > 0.30，G4 失败）；S_ind_strict 单独不预测错误（HC AUROC 0.624，CI 含 0.5），相对 S_natural（−0.349 [−0.714, −0.091]）与 RS_q（−0.318）无增量且显著为负，ρ(S_natural, S_ind_strict) ≈ 0.03。
5. 判定：论文主张收窄为“natural-pair consensus fragility phenomenon + 预注册配对干预协议”；严格版仅支撑平均响应选择性这一较弱行为声明，不声称独立生成反证可作为可部署的错误排序信号（详见 decision.md）。
