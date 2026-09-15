# Round-7 W2 摘要（5 行中文）

1. 预注册冻结（协议 cs-paper-ind-ce-20260914-round7-w2）：cohort=round3 前 100 项（50 对）、E_ind 生成/审计/三条件推理/门控/防火墙全部哈希（preregistration.md 291b42d6…，cohort.json 57e97b6d…）。
2. 正式 1500/1500 有效（gpt-6-astra temp 0）：P(flip|natural)=0.825、P(flip|ind)=0.837、P(flip|placebo)=0.544；Δ_CE=+0.293 [0.206,0.368]（G3 通过；round6 rev_flip 复现差 0.0007）；S_ind AUROC 0.983、OOF 增量 +0.045 [0.015,0.084]、ρ=0.57（HC n=96/wrong=8 小样本 caveat）。
3. 判定：独立反证成立（ind≈natural>>placebo，直接缓解镜像等价性质疑）；placebo 翻转基线 0.544>0.30（G4 不干净，如实只报选择性增量）；S_pair(W1) 0.954-0.960 与 S_natural 0.962 几乎相等，证明配对项预测重建镜像派生信号，而 S_ind 是唯一不依赖配对结构的分数。
4. TARGET_SPEC（2026-09-15）严格版已执行：claim-only 双方向生成 300 条 + 离线分配 + E_pm 匹配安慰剂；E_ind_strict 决策相关率 0.767（<0.80，claim-only 构造的如实代价，不重调）、E_pm neutral 0.883（干净）。
5. TARGET_SPEC 严格版（claim-only 生成 300 条 + 离线分配 + E_pm 匹配安慰剂；E_ind_strict 决策相关率 0.767<0.80 不重调、E_pm neutral 0.883 干净）于 06:47 补跑完成：1500 逻辑 calls valid **0.9593**（G1 达标）。严格结果（n=98 项/50 对，HC n=96/wrong=8）：flip natural 0.825 / ind_strict 0.657 / placebo 0.558；**Δ_CE=+0.099 [0.030,0.168]**（G3 PASS，显著但弱于 v1 的 +0.293）；**Δ_NI=−0.169 显著为负**（claim-only 方向干净度弱于镜像）；placebo 0.558 不干净（G4 FAIL）；S_ind_strict 单独 AUROC 0.699（CI 含 0.5）、对 S_natural 配对 AUROC −0.257 显著负、OOF 增量 0.027 触 0 → 与 W2b 判定一致：行为轴成立、预测轴不成立，严格版不作为可部署错误排序信号（详见 analysis/ind_ce_decision.md §7、analysis/ind_ce_strict_results.md）。
