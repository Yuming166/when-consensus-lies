# [SUPERSEDED] Astra6 Final Editorial Review — submission_v1 收尾审查

> **历史快照，不代表当前投稿包状态。** 本文件记录的是 2026-09-16 早先的 pre-fix 静态检查；其中 B1 的 LaTeX 伪命令问题已在当前 `md2tex_submission.py`/`main.tex` 中修复，并由 `audit/final_static_audit_20260916.md` 重新核验。当前仍没有 PDF/BibTeX 编译证据。

**substantive review returned_model:** unavailable（本轮 relay 审稿请求在返回前被中断）
**substantive review HTTP status:** not returned
**separate minimal relay health probe:** `returned_model=gpt-6-astra`; `HTTP status=200`（仅证明私人中转可达，不是本文的实质审稿响应）
**审查日期：** 2026-09-16
**审查方式：** 基于最终 `submission_v1` 文件的本地静态检查；未继续等待网络；未修改论文、BibTeX 或实验数据。

## 审查完成边界

本文件是早先 pre-fix 快照的本地静态收尾报告，不应冒充已经收到 Astra6 的 substantive editorial response，也不应覆盖当前的 final static audit。检查对象是当时的 `manuscript.md`、`latex/main.tex`、`references.bib` 和 `README.md`；当前状态以 `audit/final_static_audit_20260916.md` 为准。

## 总体 verdict

**BLOCKED（投稿打包层面）；科学主张边界大体已收窄，但当前 LaTeX 仍有必须修复的转换伪命令，且没有 PDF 编译证据。**

## Blocking issues

### B1. LaTeX 中存在明显的 md2tex 转义伪命令

**证据：** `submission_v1/latex/main.tex:70,72,74,86,640,848,852,858` 出现 `\textbackslash{}to`、`\textbackslash{}ll`、`\textbackslash{}times`、`\textbackslash{}[`/`\textbackslash{}]`、`\textbackslash{}Delta`、`\textbackslash{}rho`、`\textbackslash{}approx`、`\textbackslash{}leq`。这些不是期望的 `\to`、`\ll`、`\times`、`\[`、`\]`、`\Delta`、`\rho`、`\approx`、`\leq` 数学命令，可能导致错误渲染或编译问题。

**最小修复：** 修复 `md2tex_submission.py` 的反斜杠转义规则或在生成后的 TeX 中逐项纠正，然后重新做静态检查和实际编译。当前只确认命令/分隔符计数，不能确认 PDF。

### B2. 没有 PDF/BibTeX 编译证据

当前环境此前确认没有 `pdflatex`、`xelatex`、`lualatex`、`tectonic`、`bibtex` 或 `latexmk`。因此不能把静态通过写成“PDF 编译通过”，也不能宣称交付了可视化验证的终稿。修复 B1 后，应在有 TeX 工具的环境中至少跑一次 LaTeX/BibTeX，并检查 overfull boxes、表格溢出和引用警告。

## Major issues

### M1. 当前 citation key 覆盖已通过，但 bibliographic validation 仍应作为发布前检查

对当前文件做 key-level 静态检查：LaTeX 使用 **18 个唯一 citation keys**，`[CITE]` 占位符为 **0**，当前 `references.bib` 中未发现缺失 key；有 4 个未使用条目：`deyoung-etal-2019-eraser`、`jia-liang-2017-adversarial`、`romano-sesia-candes-2020-adaptive-coverage`、`yang-etal-2018-hotpotqa`。

这不是当前的 missing-key blocker，但提交前应删除未使用条目或明确它们只是参考文献库残留，并让 `citation_validation.json` 与当前 BibTeX 版本保持同一快照。上述结论是静态 key 一致性，不等于本报告重新核验了外部文献元数据。

### M2. `S_ind` 的 protocol-version 边界在摘要/Method 与详细审计段落间仍有歧义

稿件正确地把独立 claim-only counter-evidence 定义为 mechanism probe 而非 independent predictor，并拒绝 pooled across-runs range。但 `latex/main.tex:188` 将“final strict TARGET_SPEC run”的 OOF increment 写为 `+0.027`；`latex/main.tex:846` 又明确区分 strict 25-pair analysis 的 `+0.004 [-0.074,0.047]` 与 larger cached strict analysis 的 `+0.027 [0.000,0.058]`。

**最小修复：** 将摘要/Method 的一句话改成与 `:846` 完全相同的三行/表格结构：W2 v1、strict 25-pair TARGET_SPEC、larger cached strict analysis，各自写 cohort、AUROC、OOF increment；不要单独把 `+0.027` 叫作无限定的“final strict run”。保留“mechanism probe, not independent predictor”。

### M3. Risk@80 的双版本边界虽已记录，但发布包仍需防止误读

`README.md` 明确保留 preregistered Phase-4 Qwen Risk@80 `0.846 [0.638,0.981]`，并把 matched-baseline leaderboard 的另一次重算 lower bound `0.651` 标成 separate analysis；正文使用 preregistered 版本。这是诚实的边界，但 source-of-truth 仍容易被读者混淆。

**最小修复：** 在正文表注或附录 source map 明确写“主文只报告 preregistered estimate；`0.651` 仅属于独立 matched-baseline leaderboard 重算，不用于替换主结果”。在没有回源核对 cohort、bootstrap 实现和分母前，不要把两者合并或自行选择一个版本。

### M4. Reproducibility 部分还是“Appendix Plan”，不是实际附录

`latex/main.tex:900--1016` 和对应 Markdown 使用大量未来时态（“will provide”“will report”），但正文末尾实际只提供计划，没有真正附上的统计表、source map、hash map 或独立 CE 表。若 `submission_v1` 被作为可投稿终稿，这会让可复现性承诺与交付物不匹配。

**最小修复：** 要么把真实 appendix/补充材料加入投稿包，要么把章节标题和措辞改为当前确实交付的 artifact inventory，避免把未交付内容写成已具备的复现材料。

### M5. Section 交叉引用仍有编号歧义

Markdown 的 heading 层级目前已规范为 `# 1...# 7`、`## 3.1`、`### 3.1.1`；LaTeX 也对应使用 `section/subsection/subsubsection`。但 `latex/main.tex:806`（对应 Markdown 附近）把 Section 5 内部四部分称作“Section 1、Section 2、Section 3、Section 4”，容易与全文 Section 1--4 混淆。

**最小修复：** 改成“the four parts below”或明确引用 `Sections 5.1--5.4`；逐一审查正文中的裸 `Section 1/2/3/4` 是否指全文章节。

## Minor issues

### m1. 静态分隔符/环境检查通过，但这不是语义检查

当前 TeX 静态计数为：花括号 `324/324`，inline math `\\(`/`\\)` 为 `111/111`，display math `\\[`/`\\]` 为 `10/10`，环境 `begin/end` 为 `23/23`，未发现未闭合环境。6 个 table 环境均有闭合的 `tabularx`。这些结果支持“结构未明显截断”，但不能覆盖 B1 的伪命令、表格溢出或编译器警告。

### m2. 主要数字和边界陈述在正文中基本自洽

当前稿件重复使用的主要锚点包括 Qwen AUROC `0.943 [0.924,0.960]`、Risk@80 `0.846 [0.638,0.981]`，Ling AUROC `0.896 [0.873,0.916]`、Risk@80 `0.422`，gpt-6-astra single-point AUROC `0.969 [0.935,0.995]`，Qwen→Ling AUROC `0.723 [0.682,0.765]`，以及 BoolQ `0.449 [0.308,0.579]`。主文没有把 README 中独立 leaderboard 的 `0.651` 偷换进 preregistered claim。

### m3. 表格可读性仍需编译后人工看一遍

静态检查没有发现未闭合 table 或明显缺失的 `&` 结构；但表格含长列标题、区间和 `tabularx`，应在真实编译后检查列宽、caption、label 和双栏浮动位置。特别是 Round10 表的分层方向效应不应在排版时被误读为额外预测结果。

### m4. 个别术语可进一步统一

正文有时使用 `RS_q`/`S_natural` 的纯文本形式，有时使用数学形式。投稿版可统一为 `\(RS_q\)`、`\(S_{\mathrm{natural}}\)`，以减少读者把诊断量当作主分数的风险。

## 已通过的关键 claim-boundary 检查

- `RS_q=-BF_q` 被作为 primary predictive score；`S_natural` 被作为独立 natural-mirror diagnostic。当前没有发现把二者写成等价量的残留句子。
- Round10 文字已披露 `16 generation + 2 audit + 160 inference = 178 logical calls`、`145/160` valid、`10/16` generation parse-valid、`6/16` format-invalid but recorded/audited、`10/16` clean agree 与 `10/16` clean contradict、方向效应 `+0.44 [0.24,0.65]`、`35/37`、Probe1-inclusive `44/46`、Probe1 为 `2 items / 9 agent rows`、post-hoc/one batched audit、clean cell `n=3`，并明确不是 AUROC、generalization、causal 或 mediation 分析。当前主要问题是该段的 TeX 区间转义伪命令，而不是科学 caveat 缺失。
- `S_ind` 已明确为 mechanism probe，不是 independent predictor；W2 v1 与 strict protocol 也已有分开记录，但应按 M2 改成完全不歧义的表格/措辞。
- 没有发现正向的 universal/general rigidity、zero-shot/model-independent transfer、SOTA/superiority、S&P500 alpha/financial predictability 或“解释 LLM 失败”的明确过度主张；相关词主要出现在否定性边界中。仍需在 TeX 修复后复查表注和标题。

## 最小修复顺序

1. 修复 `main.tex` 中所有 `\\textbackslash{}` 数学伪命令，并从转换器重新生成，避免手工修复后被覆盖。
2. 把 `S_ind` 的三个 protocol/version/cohort 结果统一成一张明确的 protocol-specific 表述，消除 `+0.027` 与 `+0.004` 的歧义。
3. 在正文或附录 source map 中强化 preregistered Risk@80 与 separate leaderboard recomputation 的边界。
4. 将 `Section 1--4` 的内部指代改为真实全文编号或“four parts below”。
5. 决定交付真实 appendix 还是把 “Appendix Plan” 改成已交付 artifact inventory。
6. 在有 TeX 工具的环境中运行 LaTeX/BibTeX；检查 PDF、引用警告、表格溢出和最终 overclaim。
7. 完成上述后再请求一次 Astra6 substantive editorial review；本文件本身不应被误读为该调用已经返回。
