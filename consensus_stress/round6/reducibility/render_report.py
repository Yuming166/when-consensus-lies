#!/usr/bin/env python3
"""Render reducibility_report.md from reducibility_results.json (single source of truth)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.load(open(HERE / "reducibility_results.json"))
# Build the table view directly from reducibility_results.json (single source of truth).
t = {"models": []}
for m in d["models"]:
    tm = {"name": m["model"],
          "rs": {"a": m["rs_q_auroc"]["auroc"], "ci": m["rs_q_auroc"]["ci"]},
          "axes": m["axes"], "baselines": {}}
    for k, v in m["baselines"].items():
        tm["baselines"][k] = {
            "name": v["name"],
            "rho": v["spearman_rs_q"]["rho"], "rho_ci": v["spearman_rs_q"]["ci"],
            "inc": v["incremental_auroc_resid_rs_q_on_b"]["auroc"],
            "inc_ci": v["incremental_auroc_resid_rs_q_on_b"]["ci"],
            "pair": v["paired_auroc_diff_rs_q_minus_b"]["diff"],
            "pair_ci": v["paired_auroc_diff_rs_q_minus_b"]["ci"]}
    t["models"].append(tm)

def p(x): return "%.3f" % x
def c(x): return "[%s, %s]" % (p(x[0]), p(x[1]))

out = []
out.append("""# Reducibility & Baseline-Fidelity Audit (Agent C / R3)

- 日期：2026-09-14
- 范围：回答"RS_q/BF_q 是否只是 R_sym 换权重 + paraphrase 轴"；leaderboard 同分布 baseline 合并；
  baseline 忠实度审计。
- 输入（只读，哈希见 §6）：`benchmark/frozen/vitaminc/{preoutcome,ling_preoutcome}_features.jsonl`、
  `benchmark/frozen/vitaminc/labels_ledger.json`、`round3/features.py`（冻结公式来源）、
  `phase0/baseline_manifest.json`（R_sym/R_PI 定义）。
- 方法：无新增模型调用；复用 `round3/analysis_lib.py` 的 pair-grouped bootstrap（2000 重采样、
  seed 基 `20260913` + 固定偏移）。全部统计量在 HC 子集（agreement >= 0.8）上计算：
  Qwen3.5-4B 567 items / 298 pairs / 65 wrong；Ling-3.0-tiny 574 items / 299 pairs / 119 wrong。

## 1. 冻结公式与代数关系

来自 `round3/features.py` 与 `phase0/baseline_manifest.json`（均未修改）：

| 量 | 冻结公式 |
|---|---|
| `bf_paraphrase` | 5 agents 在 paraphrase 条件下的平均 faithfulness（= 1 - para_flip_rate） |
| `bf_reverse` | 5 agents 在 natural-reverse 条件下的平均 faithfulness（= `rev_flip_rate`） |
| `BF_q` / `RS_q` | `BF_q = (bf_paraphrase + bf_reverse)/2`；`RS_q = -BF_q` |
| `R_sym` | `0.3*reverse_inertia + 0.7*intervention_disagreement`，其中 `reverse_inertia = 1 - rev_flip_rate` |
| `R_PI` | `0.1*D_inert + 0.3*flip_inertia + 0.6*frac_shared` |
| flip-rate | `rev_flip_rate`（自然反证下翻 answer 的 agent 占比） |
| disagreement | `intervention_disagreement = min(1, 2*pstdev(per_agent_flip_rate))`（R_sym 的第二项） |
| confidence | `mean_confidence`（original 条件的 5-agent 平均置信度） |

**关键代数观察**：`RS_q = -(bf_paraphrase + rev_flip_rate)/2`，`R_sym = 0.3*(1 - rev_flip_rate) + 0.7*intervention_disagreement`。
两者**唯一共享的成分是自然反证 flip 轴（`rev_flip_rate`）**，且有效权重不同（RS_q 记 -0.5；R_sym 经
`reverse_inertia` 记 -0.3）。第二轴完全不同：RS_q 用 paraphrase faithfulness，R_sym 用
`intervention_disagreement`。因此"RS_q 只是 R_sym 换权重"在代数上**不精确**——权重与第二轴都不同；
但"共享反证轴 + RS_q 多一个 paraphrase 轴"的直觉**方向正确**。
""".strip())

# ---- Table 2: Spearman ----
out.append("")
out.append("## 2. Spearman 相关（RS_q vs 各基线，pair-grouped 95% CI）")
out.append("")
out.append("| 基线 | Qwen rho [CI] | Ling rho [CI] |")
out.append("|---|---:|---:|")
order = ["R_sym", "R_PI", "rev_flip_rate", "intervention_disagreement", "agreement", "mean_confidence", "bf_paraphrase"]
for k in order:
    q = t["models"][0]["baselines"][k]; l = t["models"][1]["baselines"][k]
    out.append("| %s | %s %s | %s %s |" % (q["name"], p(q["rho"]), c(q["rho_ci"]), p(l["rho"]), c(l["rho_ci"])))
out.append("")
out.append("""- RS_q 与 R_sym 强正相关（0.82 / 0.86），但远非同构；与 flip-rate 近完全相关（-0.98 / -0.96），
  说明 RS_q 的排序几乎完全由自然反证轴决定。
- 与 R_PI、intervention disagreement、vote agreement、confidence 的相关均弱（|rho| <= 0.35）；
  多数 CI 排除 0（弱但显著），仅 Ling 的 confidence CI 含 0（不显著）。
""".rstrip())

# ---- Table 3: Incremental AUROC ----
out.append("")
out.append("## 3. 增量 AUROC（RS_q 相对各基线单独做增量，pair-grouped 95% CI）")
out.append("")
out.append("""定义：对每个基线 B，用**不含标签**的 OLS 将 RS_q 对 B 残差化（每个 bootstrap 重采样内重新拟合），
计算残差对 `consensus_wrong` 的 AUROC。若 CI 下限 > 0.5，则 RS_q 在该基线上仍有显著增量信号。
参考：RS_q 原始 AUROC = Qwen 0.943 [0.924, 0.960]；Ling 0.896 [0.875, 0.917]。
""".strip())
out.append("")
out.append("| 基线 | Qwen 增量 AUROC [CI] | Ling 增量 AUROC [CI] | Qwen 配对差 RS_q-B [CI] | Ling 配对差 RS_q-B [CI] |")
out.append("|---|---:|---:|---:|---:|")
for k in order:
    q = t["models"][0]["baselines"][k]; l = t["models"][1]["baselines"][k]
    out.append("| %s | %s %s | %s %s | +%s %s | +%s %s |" % (
        q["name"], p(q["inc"]), c(q["inc_ci"]), p(l["inc"]), c(l["inc_ci"]),
        p(q["pair"]), c(q["pair_ci"]), p(l["pair"]), c(l["pair_ci"])))
out.append("")
out.append("""解读：

- **相对 R_sym**：增量 AUROC 0.874 / 0.787，CI 下限 0.784 / 0.743 均 > 0.5 —— RS_q 在 R_sym 之外
  **保留显著但适中的增量信号**（相对原始 AUROC 0.943 / 0.896 下降约 0.07 / 0.11）。
- **相对 flip-rate 轴**：增量 AUROC 0.284 / 0.317（< 0.5，方向反转，判别量级 |0.284-0.5| ~ 0.22）。
  进一步验证表明该残差对微小扰动高度敏感（去掉 reverse 轴后剩余成分很弱、方向不稳定），
  即 **RS_q 的可预测力几乎完全由自然反证轴承载**（见 §4）。
- **相对 R_PI / disagreement / vote / confidence**：增量 AUROC >= 0.89 且 CI 下限远超 0.5，
  RS_q 对这几类基线**不可归约**。
""".rstrip())

# ---- Table 4: Axis decomposition ----
q0 = t["models"][0]; l0 = t["models"][1]
out.append("")
out.append("## 4. 轴分解（reverse 轴 vs paraphrase 轴）")
out.append("")
out.append("| 量 | Qwen [CI] | Ling [CI] |")
out.append("|---|---:|---:|")
def axis_row(label, key):
    qv = q0["axes"][key]; lv = l0["axes"][key]
    if "paired" in key:
        out.append("| %s | %s %s | %s %s |" % (label, p(qv["diff"]), c(qv["ci"]), p(lv["diff"]), c(lv["ci"])))
    else:
        out.append("| %s | %s %s | %s %s |" % (label, p(qv["auroc"]), c(qv["ci"]), p(lv["auroc"]), c(lv["ci"])))
out.append("| RS_q AUROC | %s %s | %s %s |" % (p(q0["rs"]["a"]), c(q0["rs"]["ci"]), p(l0["rs"]["a"]), c(l0["rs"]["ci"])))
axis_row("reverse 轴（-rev_flip_rate）AUROC", "risk_reverse_axis_minus_rev_flip_rate")
axis_row("paraphrase 轴（-bf_paraphrase）AUROC", "risk_paraphrase_axis_minus_bf_paraphrase")
axis_row("配对差 RS_q - reverse 轴", "paired_auroc_diff_rs_q_minus_reverse_axis")
axis_row("配对差 RS_q - paraphrase 轴", "paired_auroc_diff_rs_q_minus_paraphrase_axis")
axis_row("RS_q 相对 reverse 轴的残差增量 AUROC", "incremental_rs_q_over_reverse_axis")
axis_row("RS_q 相对 paraphrase 轴的残差增量 AUROC", "incremental_rs_q_over_paraphrase_axis")
out.append("")
out.append("""- RS_q 的 AUROC 主要由 reverse 轴贡献（Qwen 0.931/0.943；Ling 0.869/0.896）；paraphrase 轴单独只有
  0.60 / 0.58。
- paraphrase 轴带来**小而统计显著**的增量（配对差 CI 下限 0.002 / 0.013 > 0，两个模型都显著）。
- 作为参照：R_sym（0.892 / 0.818）反而低于单独 reverse 轴（0.931 / 0.869），说明 R_sym 的
  `intervention_disagreement` 项（权重 0.7，自身 AUROC 仅 0.536 / 0.475）对预测是拖累；
  RS_q 相对 R_sym 的优势 = 引入 paraphrase 轴 + 不使用 intervention_disagreement。
""".rstrip())

out.append("")
out.append("""## 5. 结论：RS_q/BF_q 是否只是 R_sym 换权重 + paraphrase 轴？

**判定：部分可归约（substantially overlapping），不可严格归约；不构成独立的新启发式。**

1. 代数上不是"只换权重"：R_sym 与 RS_q 仅在自然反证轴上重叠（权重 -0.3 vs -0.5），第二轴不同
   （R_sym 用 intervention_disagreement，RS_q 用 paraphrase）。
2. 经验上高度重叠：rho(RS_q, R_sym) = 0.82 / 0.86；RS_q 的信号几乎全由与 R_sym 共享的反证轴承载
   （reverse 轴单独 AUROC 0.931 / 0.869，占 RS_q 的 0.943 / 0.896 的绝大部分；round-6 的
   reversal-only(5) 探针以 5 个边际调用即达 AUROC 0.931 / 0.869，进一步印证反证轴是主导成分）。
3. RS_q 相对 R_sym 的增量真实存在但适中：残差增量 AUROC 0.874 [0.784, 0.931] / 0.787 [0.743, 0.831]，
   配对差 +0.051 [0.028, 0.075] / +0.078 [0.053, 0.106]（CI 排除 0）。增量来源是 paraphrase 轴 + 丢弃
   intervention_disagreement。
4. 对论文主贡献的含义（对应主指令 §6 的降级路径）：**不 claim "新启发式/新机制信号"**；
   主贡献按"基准 CST-Bench + 冻结复现 + 简洁信号（反证轴）"表述。机制叙述应明确：
   "错误跨近重复自然对相关 -> 自然反证轴可事前预测共识错误"，且该反证轴已被 R_sym 以 0.3 权重捕获，
   RS_q 的相对增益是 paraphrase 轴的小幅增量（配对 AUROC +0.05/+0.08 vs R_sym，两个模型均显著）。
5. BF_q 与 RS_q 只是符号相反：上述所有 AUROC 结论对 BF_q 相同，Spearman 符号取反。

## 6. 复现与哈希

- 脚本：`round6/reducibility/analyze_reducibility.py`（seed 基 `20260913` + 固定偏移；2000 重采样；
  结果 `round6/reducibility/reducibility_results.json`）。
- 输入哈希（sha256）：qwen features `d0c588d05211769c14234377d669881d079dacaac0ebaf2ec9326561d967584d`；
  ling features `35e853cf0815cb1428ec8f2ee671993bd1f87ba8b28ade24a630ac4c79bc26bb`；
  labels `770ede3f79b018c47aa982e6cb3f13b9d504b5c14950f7f1a8f6de196ffcbc5a`。
- 复现：`/storage/gaoym/sp500-forecastability-lab/.venv/bin/python consensus_stress/round6/reducibility/analyze_reducibility.py`

## 7. 外部 baseline 忠实度审计（哪些是原方法、哪些是二值/answer-match 变体）

| Leaderboard 行 | 类别 | 忠实度声明 |
|---|---|---|
| sampling-consistency family | external（adapted proxy） | **非原论文实现**。三变体均基于同一 25 个 temperature-0.7 采样的二值 answer 分布：Self-consistency（Wang et al. 2022）= 1 - 模态频率；SelfCheckGPT（Manakul et al. 2023）= answer-match 概率（**无原版 NLI/自校验管线**）；binary semantic entropy（Kuhn et al.）= yes/no 簇归一化熵（**无双向蕴含聚类**）。 |
| Raw sampled confidence | external（adapted proxy） | 1 - 平均采样置信度；方法无关的常见代理，非特定论文实现。 |
| Isotonic / Temperature confidence | external（adapted proxy） | pair-grouped 5-fold OOF 校准；标准校准家族的自适应实现，非特定论文复现。 |
| Single-agent intervention | external（实为内部消融） | 本项目自己的消融（5 personas -> 1 persona），标记为 external 仅为排序/叙述；非外部发表方法。 |
| R_sym / R_PI / Vote agreement / Frozen confidence | internal | 本项目内部 baseline（冻结公式见 phase0）。 |
| Reversal-only probe (5 calls) | internal（round-6 cost-curve） | 本项目探针（Agent B）：risk = 1 - 5-agent 自然反证平均 faithfulness；5 个边际 calls（含 5 个 original 共识 calls 共 10）；数值逐字取自 `round6/cost_curve/leaderboard_proposal.json`，未重算。 |

结论：leaderboard 中所有 external 行均为 **adapted proxies（二值/answer-match 变体）**，
不能读作原论文方法的复现数值；README §5 已加 adapted-proxy notice，§9 已加边界条目。
""".rstrip())

(HERE / "reducibility_report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("wrote reducibility_report.md, lines:", len(out))
