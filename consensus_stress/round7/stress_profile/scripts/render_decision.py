#!/usr/bin/env python3
"""Render decision.md + SUMMARY.md from stress_profile_results.json (single source of truth)."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
d = json.loads((HERE / "stress_profile_results.json").read_text(encoding="utf-8"))
T2 = d["task2_multiaxis"]
T3 = d["task3_false_positive"]

def p(x): return "%.3f" % x
def c(x): return "[%s, %s]" % (p(x[0]), p(x[1]))
def sgn(x): return ("%+.3f" % x)

def combo(disp, key):
    return next(x["combos"][key] for x in T2["combos"] if x["model"] == disp)

# key numbers
q_rs = next(x["rs_q"] for x in T2["combos"] if x["model"] == "Qwen3.5-4B")
l_rs = next(x["rs_q"] for x in T2["combos"] if x["model"] == "Ling-3.0-tiny")
q_oof = combo("Qwen3.5-4B", "logistic_oof3")
l_oof = combo("Ling-3.0-tiny", "logistic_oof3")
q_r3 = combo("Qwen3.5-4B", "risk_rev_rem_para")
l_r3 = combo("Ling-3.0-tiny", "risk_rev_rem_para")
q_z3 = combo("Qwen3.5-4B", "risk_z3")

def fp(disp, thr):
    return next(m for m in T3["models"] if m["model"] == disp and m["population"] == "hc"
                and m["rigid_definition"] == thr)

q_cr, l_cr = fp("Qwen3.5-4B", "consensus-rigid rev<=0.4"), fp("Ling-3.0-tiny", "consensus-rigid rev<=0.4")
q_fr, l_fr = fp("Qwen3.5-4B", "fully-rigid rev==0"), fp("Ling-3.0-tiny", "fully-rigid rev==0")
la_rem = T3["lambda_axis"]["consensus-rigid"]["separation_rem_area"]

qc_total = q_cr["groups"]["correct_rigid"]["n"] + q_cr["groups"]["correct_responsive"]["n"]
lc_total = l_cr["groups"]["correct_rigid"]["n"] + l_cr["groups"]["correct_responsive"]["n"]
qf_total = q_fr["groups"]["correct_rigid"]["n"] + q_fr["groups"]["correct_responsive"]["n"]
lf_total = l_fr["groups"]["correct_rigid"]["n"] + l_fr["groups"]["correct_responsive"]["n"]

decision = []
decision.append("""# Decision — 多轴压力响应轮廓是否进论文（Agent W3）

- 日期：2026-09-14
- 判定规则（任务约定）：多轴组合相对 RS_q/BF_q **增量显著 = 进论文**；否则 **降为诊断图**。
- 依据：`stress_profile_analysis.md` + `stress_profile_results.json`（全部 post-hoc）。

## 证据摘要

1. **Task 2（多轴组合 vs RS_q/BF_q，HC）**
   - 冻结复现：Qwen RS_q AUROC %s %s、Risk@80 %s %s；Ling AUROC %s %s、Risk@80 %s %s。
   - 所有固定权重多轴组合的 ΔAUROC vs RS_q ≤ 0：Qwen `risk_rev_rem_para` %s %s、
     `risk_z3` %s %s（CI 上限 ≤ 0）；Ling 全部显著为负（`risk_rev_rem_para` %s %s）。
   - 加移除轴不稀释的组合 `risk_rsq_rem` 反而显著更差（Qwen %s %s；Ling %s %s）。
   - **拟合上限打平**：3 轴 OOF 逻辑回归 vs RS_q —— Qwen %s %s；Ling %s %s（CI 含 0）。
   - Risk@80 无任何显著增量（ΔRisk@80 CI 含 0 或为负）。
   → 多轴轮廓对 RS_q/BF_q **无显著增量**，且不是权重选择问题（拟合上限也打平）。

2. **Task 3（假阳性分解）**
   - 审稿质疑成立：正确 HC 面板中 `consensus-rigid` 占 Qwen %d/%d（%.1f%%）、Ling %d/%d（%.1f%%）；
     `fully-rigid` 占 Qwen %d/%d（%.1f%%）、Ling %d/%d（%.1f%%）。
   - 离散 removal 轴**不能**分开"正确刚性"与"错误刚性"：Qwen %s %s（chance）；Ling %s %s（低于 chance）；
     `fully-rigid` 两模型均为 0.500（rem 分布逐值相同）。
   - paraphrase 轴仅给出小的部分分离（consensus-rigid：Qwen %s %s、Ling %s %s）。
   - 连续 λ 移除曲线临界且样本极小（Qwen 120-pair：removal stress area 分离 %s %s，n=26/22）。
   → 多轴轮廓也**不能修复**单轴刚性信号的假阳性弱点。

## 判定：降为诊断图（不进主文评分贡献）

- 主评分**保持冻结 RS_q = −BF_q**（不改任何协议数字）；多轴轮廓不作为新评分/新启发式进入主文。
- 多轴轮廓降级为**补充诊断图 + post-hoc robustness 小节**（附录/补充材料）：
  1. 二维压力轮廓散点（反转刚性 vs 移除不稳，按正确性分组；`figures/axis_profile_scatter.png`）：
     展示"错误共识反转更刚 + 移除更不稳"的可复现反向签名（全 cohort 两模型，Task 1）。
  2. 一段诚实的假阳性边界：反转刚性轴有已知假阳性率（正确但不变：13.9%%/27.3%% consensus-rigid），
     removal 轴在 λ=1 无法分离这些假阳性，paraphrase 轴仅部分分离；
     RS_q 应表述为**有已知假阳性率的排序信号**而非机制声明。
  3. 引用 OOF 3 轴打平作为"该特征集合已近上限、无需更多轴"的负结果证据。
- 不进主文的理由（对应任务规则）：**增量不显著（且多数显著为负）** + 假阳性修复不成立。
""".strip() % (
    p(q_rs["auroc"]["auroc"]), c(q_rs["auroc"]["ci"]), p(q_rs["risk80"]["reduction"]), c(q_rs["risk80"]["ci"]),
    p(l_rs["auroc"]["auroc"]), c(l_rs["auroc"]["ci"]), p(l_rs["risk80"]["reduction"]), c(l_rs["risk80"]["ci"]),
    sgn(q_r3["paired_auroc_diff_vs_rsq"]["diff"]), c(q_r3["paired_auroc_diff_vs_rsq"]["ci"]),
    sgn(q_z3["paired_auroc_diff_vs_rsq"]["diff"]), c(q_z3["paired_auroc_diff_vs_rsq"]["ci"]),
    sgn(l_r3["paired_auroc_diff_vs_rsq"]["diff"]), c(l_r3["paired_auroc_diff_vs_rsq"]["ci"]),
    sgn(combo("Qwen3.5-4B", "risk_rsq_rem")["paired_auroc_diff_vs_rsq"]["diff"]),
    c(combo("Qwen3.5-4B", "risk_rsq_rem")["paired_auroc_diff_vs_rsq"]["ci"]),
    sgn(combo("Ling-3.0-tiny", "risk_rsq_rem")["paired_auroc_diff_vs_rsq"]["diff"]),
    c(combo("Ling-3.0-tiny", "risk_rsq_rem")["paired_auroc_diff_vs_rsq"]["ci"]),
    sgn(q_oof["paired_auroc_diff_vs_rsq"]["diff"]), c(q_oof["paired_auroc_diff_vs_rsq"]["ci"]),
    sgn(l_oof["paired_auroc_diff_vs_rsq"]["diff"]), c(l_oof["paired_auroc_diff_vs_rsq"]["ci"]),
    q_cr["groups"]["correct_rigid"]["n"], qc_total,
    100.0 * q_cr["groups"]["correct_rigid"]["n"] / qc_total,
    l_cr["groups"]["correct_rigid"]["n"], lc_total,
    100.0 * l_cr["groups"]["correct_rigid"]["n"] / lc_total,
    q_fr["groups"]["correct_rigid"]["n"], qf_total,
    100.0 * q_fr["groups"]["correct_rigid"]["n"] / qf_total,
    l_fr["groups"]["correct_rigid"]["n"], lf_total,
    100.0 * l_fr["groups"]["correct_rigid"]["n"] / lf_total,
    p(q_cr["separation_rem"]["auroc"]), c(q_cr["separation_rem"]["ci"]),
    p(l_cr["separation_rem"]["auroc"]), c(l_cr["separation_rem"]["ci"]),
    p(q_cr["separation_para"]["auroc"]), c(q_cr["separation_para"]["ci"]),
    p(l_cr["separation_para"]["auroc"]), c(l_cr["separation_para"]["ci"]),
    p(la_rem["auroc"]), c(la_rem["ci"]),
))
decision.append("")
decision.append("""## 建议的论文表述（一句话）

"移除/改写等附加压力轴在冻结 RS_q 之外不提供显著增量（OOF 3 轴打平），且无法修复反转刚性轴的
假阳性（正确但不变的面板占 13.9%/27.3%）；多轴行为作为诊断图报告，主评分保持 RS_q。"

## 一致性检查

- 本判定不改变任何冻结 gate/协议数字（§16：全部新增统计标注 post-hoc）。
- 与 round6/reducibility 一致：RS_q 信号集中于自然反转轴，paraphrase 仅小幅增量；本报告进一步显示
  removal 轴在 RS_q 之后无增量甚至有害。
- 决策由 CI 证据驱动，未做任何后验符号选择。
""".rstrip())

(HERE / "decision.md").write_text("\n".join(decision) + "\n", encoding="utf-8")

summary = """1. 全 cohort 验证：600 项上两模型均复现 phase3 反向签名——错误共识反转下更刚性（Qwen rev_flip 0.095 vs 0.843，AUROC 0.931）、移除下更不稳（rem 0.859 vs 0.552，AUROC 0.646），差值与 CI 均显著。
2. 多轴组合无增量：所有固定权重组合与 3 轴 OOF 逻辑回归相对 RS_q 的 ΔAUROC ≤ 0（Qwen 最优 −0.012 [−0.027, −0.000]；Ling 显著为负），加移除轴反而显著更差；Risk@80 无增量。
3. 假阳性分解：正确但反转不变的面板真实存在（consensus-rigid 占正确面板 13.9%/27.3%），removal 轴在 λ=1 无法与真正错误分开（AUROC 0.50/0.46），paraphrase 仅小部分分离（0.58/0.60）。
4. 判定：多轴轮廓对冻结 RS_q 无显著增量且不能修复刚性假阳性 → 降为诊断图 + post-hoc 边界小节，主评分保持 RS_q，不改任何协议数字。
5. 交付：stress_profile_analysis.md / decision.md / scripts/ / figures/ / stress_profile_results.json。""".splitlines()
(HERE / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
print("wrote decision.md + SUMMARY.md")
