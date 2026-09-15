#!/usr/bin/env python3
"""Render stress_profile_analysis.md / decision.md / SUMMARY.md from results JSON."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
d = json.loads((HERE / "stress_profile_results.json").read_text(encoding="utf-8"))
T1, T2, T3 = d["task1_signature"], d["task2_multiaxis"], d["task3_false_positive"]

def p(x): return "%.3f" % x
def c(x): return "[%s, %s]" % (p(x[0]), p(x[1]))
def f4(x): return "%.4f" % x
def sgn(x): return ("%+.3f" % x)

MODEL_ORDER = ["Qwen3.5-4B", "Ling-3.0-tiny"]

def model_key(display):
    return "qwen" if display == "Qwen3.5-4B" else "ling"

out = []
out.append("""# Round 7 融合点 A — 多轴压力响应轮廓（Agent W3，exploratory/post-hoc）

- 日期：2026-09-14
- 状态：**exploratory / post-hoc robustness analysis**（按 NAACL_Main_Revision_Autoresearch_Plan §16，
  全部统计为新增后验分析，不改变任何冻结协议数字）。
- 范围：零新增模型调用，纯冻结特征分析。回答四个问题：
  1. 移除轴反向签名是否在 600 项全 cohort（Qwen/Ling）成立（phase3 仅 120 对 Qwen 子集）；
  2. 多轴风险组合相对 RS_q/BF_q 是否有显著增量；
  3. "原答正确但反转下不变（镜像答错）"面板能否在 removal/λ 轴上与真正错误面板分开；
  4. 多轴轮廓是否值得进论文（见 decision.md）。
- 输入（只读；sha256）：
  `benchmark/frozen/vitaminc/preoutcome_features.jsonl`
  `d0c588d05211769c14234377d669881d079dacaac0ebaf2ec9326561d967584d`；
  `ling_preoutcome_features.jsonl`
  `35e853cf0815cb1428ec8f2ee671993bd1f87ba8b28ade24a630ac4c79bc26bb`；
  `labels_ledger.json` `770ede3f79b018c47aa982e6cb3f13b9d504b5c14950f7f1a8f6de196ffcbc5a`；
  λ 轴另读 `round3/records.jsonl` + `round3/records_phase3_lambda.jsonl`（Qwen 120-pair
  subset，均已冻结）。
- 方法：复用 `round3/analysis_lib.py` pair-grouped bootstrap（2000 重采样，自然对水平）。
  冻结 RS_q 复现用原 seed 基 `20260913`；**所有新增统计用独立 post-hoc seed 基
  `20260913+1000`**，见 scripts/stress_common.py。

## 0. 冻结特征与风险方向（round3/features.py，未修改）

| 轴 | 冻结特征 | 风险方向（越高越险） |
|---|---|---|
| natural reversal（反证） | `rev_flip_rate`（5 agent 翻转占比；`bf_reverse` 数值上等于它，599/600 项一致，1 项因单次 reverse 调用缺失） | `1 - rev_flip_rate`（反转刚性） |
| removal（证据移除） | `rem_flip_rate` | `rem_flip_rate`（移除不稳） |
| paraphrase（改写） | `para_flip_rate`（`bf_paraphrase = 1 - para_flip_rate`） | `para_flip_rate` |
| synthetic reverse | `synth_flip_rate` | `synth_flip_rate` |
| 冻结复合 | `BF_q = (bf_paraphrase + bf_reverse)/2`；`RS_q = -BF_q` | `RS_q` |

代数关系（与 round6/reducibility 一致）：`RS_q = -(1 - rev_flip_rate + para_flip_rate)/2`。
""".strip())

# ---------------- Section 1: Task 1 signature ----------------
out.append("")
out.append("## 1. Task 1 — 移除轴反向签名（全 cohort 验证，post-hoc）")
out.append("")
out.append("phase3（120-pair / 225-HC，仅 Qwen）发现：错误共识在**反转下更刚性**（`rev_flip_rate` 更低）、"
           "在**移除下更不稳**（`rem_flip_rate` 更高）。下表在 600 项全 cohort 与 HC 子集上复现（两模型）。")
out.append("")
out.append("### 1.1 各轴 flip-rate 均值与正确−错误差（pair-grouped 95% CI）")
out.append("")
out.append("| 模型 | 人群 | n(c/w) | 轴 | mean 正确 | mean 错误 | 差(正确−错误) [CI] |")
out.append("|---|---|---|---:|---:|---:|---:|")
for m in T1["models"]:
    disp = m["model"]
    pop = "全 600" if m["population"] == "all" else "HC"
    for axis, axname in (("reversal_rigidity", "reversal `rev_flip_rate`"),
                         ("removal_instability", "removal `rem_flip_rate`"),
                         ("paraphrase_instability", "paraphrase `para_flip_rate`")):
        r = m[axis]
        out.append("| %s | %s | %d/%d | %s | %s | %s | %s %s |" % (
            disp, pop, m["n_correct"], m["n_wrong"], axname,
            f4(r["mean_correct"]), f4(r["mean_wrong"]), sgn(r["gap_correct_minus_wrong"]), c(r["gap_ci"])))
out.append("")
out.append("### 1.2 各轴风险表示单独 AUROC（HC 子集；风险方向如上）")
out.append("")
out.append("| 模型 | 反转刚性 `1-rev` | 移除不稳 `rem` | 改写不稳 `para` | 合成反转 `synth` |")
out.append("|---|---:|---:|---:|---:|")
for disp in MODEL_ORDER:
    m = next(x for x in T1["models"] if x["model"] == disp and x["population"] == "hc")
    cells = []
    for axis in ("reversal_rigidity", "removal_instability", "paraphrase_instability", "synthetic_reverse_flip"):
        a = m[axis]["auroc_risk_axis"]
        cells.append("%s %s" % (p(a["auroc"]), c(a["ci"])))
    out.append("| %s | %s | %s | %s | %s |" % (disp, *cells))
out.append("")
out.append("""**结论 1（全 cohort 复现成功）**：两个模型在 600 项全 cohort 与 HC 子集上都稳定复现 phase3 的反向签名：
- 反转刚性：正确共识 `rev_flip_rate` 显著高于错误（Qwen HC 差 +0.748 [+0.685, +0.808]；Ling HC +0.674 [+0.629, +0.715]；
  全 cohort 亦显著），即错误共识在反证下显著更刚性。
- 移除不稳：错误共识 `rem_flip_rate` 显著高于正确（Qwen HC 差 −0.306 [−0.366, −0.240]；Ling HC −0.249 [−0.291, −0.206]），
  即错误共识在证据移除下显著更不稳（与反转轴方向相反）。
- 方向自洽：反转刚性单独 AUROC 0.931/0.869，移除不稳单独 0.646/0.614，改写不稳 0.599/0.581——反转轴是主信号，移除轴是
  一个方向相反、独立但较弱的轴。
- phase3 的 120-pair 子集结论推广到全 cohort 且跨模型成立；本段为 post-hoc 验证，不改变冻结 gate 数字。
""".rstrip())

# ---------------- Section 2: Task 2 multi-axis vs RS_q ----------------
out.append("")
out.append("## 2. Task 2 — 多轴组合 vs RS_q / BF_q（HC 子集，post-hoc）")
out.append("")
out.append("多轴风险表示（全部无标签、固定权重；`logistic_oof3` 为 pair-grouped 5-fold OOF 拟合上限诊断）：")
out.append("")
out.append("| 表示 | 构造 |")
out.append("|---|---|")
out.append("| `risk_rev_rem` | `(1−rev) + rem`（反转刚性 + 移除不稳） |")
out.append("| `risk_rev_rem_para` | `(1−rev) + rem + para`（三轴等权） |")
out.append("| `risk_rsq_rem` | `RS_q + rem`（冻结复合上加移除轴，不稀释） |")
out.append("| `risk_z3` | `z(1−rev)+z(rem)+z(para)`（HC 上 z-score 等权） |")
out.append("| `risk_rem_para` | `rem + para`（仅非反转轴，参照） |")
out.append("| `logistic_oof3` | 3 轴 OOF 逻辑回归（post-hoc 拟合上限） |")
out.append("")
for disp in MODEL_ORDER:
    m = next(x for x in T2["combos"] if x["model"] == disp)
    rs = m["rs_q"]
    out.append("### 2.%d %s（HC n=%d, pairs=%d, wrong=%d）" % (
        1 if disp == "Qwen3.5-4B" else 2, disp, m["hc"]["n_items"], m["hc"]["n_pairs"], m["hc"]["wrong"]))
    out.append("")
    out.append("冻结复现：RS_q AUROC = **%s %s**，Risk@80 = **%s %s**。" % (
        p(rs["auroc"]["auroc"]), c(rs["auroc"]["ci"]), p(rs["risk80"]["reduction"]), c(rs["risk80"]["ci"])))
    out.append("")
    out.append("| 表示 | AUROC [CI] | Risk@80 [CI] | ΔAUROC vs RS_q [CI] | ΔRisk@80 vs RS_q [CI] | ρ vs RS_q |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for k, cm in m["combos"].items():
        a, r = cm["auroc"], cm["risk80"]
        pa, pr = cm["paired_auroc_diff_vs_rsq"], cm["paired_risk80_diff_vs_rsq"]
        sp = cm["spearman_vs_rsq"]
        out.append("| %s | %s %s | %s %s | %s %s | %s %s | %s |" % (
            k, p(a["auroc"]), c(a["ci"]), p(r["reduction"]), c(r["ci"]),
            sgn(pa["diff"]), c(pa["ci"]), sgn(pr["diff"]), c(pr["ci"]), p(sp["rho"])))
    out.append("")
out.append("""**结论 2（多轴组合无显著增量）**：
- **没有任何固定权重多轴组合在 AUROC 上显著超过 RS_q**。Qwen 所有组合 ΔAUROC ≤ 0 且 CI 上限 ≤ 0
  （最优 `risk_z3` −0.012 [−0.027, −0.000]；`risk_rev_rem_para` −0.022 [−0.038, −0.006]）；Ling 全部显著为负
  （`risk_rev_rem_para` −0.024 [−0.038, −0.011]）。加移除轴（`risk_rsq_rem`）反而显著降低 AUROC
  （Qwen −0.052 [−0.084, −0.021]；Ling −0.048 [−0.075, −0.025]）——移除轴在 RS_q 之后提供的是噪声而非信息。
- **拟合上限同样打平**：3 轴 OOF 逻辑回归 AUROC 与 RS_q 无显著差异（Qwen −0.001 [−0.006, +0.004]；
  Ling −0.005 [−0.013, +0.002]），说明不是固定权重选择问题，而是三轴集合本身不包含超过 RS_q 的增量信息。
- **Risk@80 无增量**：所有组合的 ΔRisk@80 CI 都含 0 或为负（Qwen 最优 `risk_z3` +0.019 [−0.078, +0.020]）。
- 判定：多轴轮廓相对冻结 RS_q/BF_q **不构成显著增量**；RS_q 已是该特征集合上的近似上限。
""".rstrip())

# ---------------- Section 3: Task 3 false-positive decomposition ----------------
out.append("")
out.append("## 3. Task 3 — 假阳性分解：'正确共识在反转下也不变'（post-hoc）")
out.append("")
out.append("审稿质疑：'正确共识也会不变'。我们挑出**原答正确但反转下不变（镜像答错）**的面板：")
out.append("- `consensus-rigid`：`rev_flip_rate ≤ 0.4`（多数票在反转下保持不变）；")
out.append("- `fully-rigid`：`rev_flip_rate = 0`（无任何 agent 翻转）。")
out.append("")
out.append("### 3.1 刚性面板规模与 removal/para 轴行为（HC 子集）")
out.append("")
out.append("| 模型 | 定义 | n 刚性 | 正确刚性 | 错误刚性 | 正确刚 rem | 错误刚 rem | 正确刚 para | 错误刚 para |")
out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
for m in T3["models"]:
    if m["population"] != "hc":
        continue
    g = m["groups"]
    out.append("| %s | %s | %d | %d | %d | %s | %s | %s | %s |" % (
        m["model"], m["rigid_definition"], m["n_rigid"], g["correct_rigid"]["n"], g["wrong_rigid"]["n"],
        f4(g["correct_rigid"]["rem_flip_rate"]), f4(g["wrong_rigid"]["rem_flip_rate"]),
        f4(g["correct_rigid"]["para_flip_rate"]), f4(g["wrong_rigid"]["para_flip_rate"])))
out.append("")
out.append("### 3.2 分离 AUROC：能否把'正确刚性'与'真正错误刚性'分开（pair-grouped 95% CI）")
out.append("")
out.append("| 模型 | 定义 | removal `rem` [CI] | paraphrase `para` [CI] | rem+para [CI] |")
out.append("|---|---|---:|---:|---:|")
for m in T3["models"]:
    if m["population"] != "hc":
        continue
    sr, sp_, srp = m["separation_rem"], m["separation_para"], m["separation_rem_para"]
    out.append("| %s | %s | %s %s | %s %s | %s %s |" % (
        m["model"], m["rigid_definition"], p(sr["auroc"]), c(sr["ci"]),
        p(sp_["auroc"]), c(sp_["ci"]), p(srp["auroc"]), c(srp["ci"])))
out.append("")
out.append("### 3.3 λ 轴（Qwen phase3 120-pair 子集，HC）")
out.append("")
la = T3["lambda_axis"]
for k in ("consensus-rigid", "fully-rigid"):
    e = la[k]
    out.append("**%s**（正确 n=%d / 错误 n=%d）：" % (k, e["n_correct_rigid"], e["n_wrong_rigid"]))
    out.append("- 移除应力面积（`removal_stress_area`）分离 AUROC = **%s %s**（n_c=%d, n_w=%d, pairs=%d）；"
               "反转应力面积 = %s %s。" % (
        p(e["separation_rem_area"]["auroc"]), c(e["separation_rem_area"]["ci"]),
        e["separation_rem_area"]["n_correct_rigid"], e["separation_rem_area"]["n_wrong_rigid"],
        e["separation_rem_area"]["n_pairs"],
        p(e["separation_rev_area"]["auroc"]), c(e["separation_rev_area"]["ci"])))
    out.append("- 移除 flip 曲线（λ=0,0.2,0.4,0.6,0.8,1）：正确刚性 %s；错误刚性 %s。" % (
        e["curve_removal_correct"], e["curve_removal_wrong"]))
    out.append("- 反转 flip 曲线：正确刚性 %s；错误刚性 %s。" % (e["curve_reversal_correct"], e["curve_reversal_wrong"]))
    out.append("")
out.append("""**结论 3（诚实回答审稿质疑）**：
- **审稿质疑成立**：反转刚性轴确有不可忽略的假阳性——`consensus-rigid` 占全部 HC 的
  Qwen 70/567（12.3%）、Ling 124/574（21.6%），占**正确面板**的 70/502（13.9%）、124/455（27.3%）；
  `fully-rigid` 占正确面板 46/502（9.2%）、102/455（22.4%）。单一反转轴不能把这些'正确但不变'的
  面板与真正错误面板区分开，这是该轴的真实局限。
- **离散 removal 轴（λ=1 anchor）不能修复假阳性**：`rem_flip_rate` 分离 AUROC 在 Qwen 为 0.501
  [0.441, 0.557]（chance），Ling 为 0.461 [0.434, 0.487]（显著低于 chance，方向相反）；
  `fully-rigid` 两模型均为 0.500（分布完全相同，0.913 vs 0.913）。'正确刚性'与'错误刚性'在
  证据移除下都同样高度不稳（~0.91 flip），因此 **'移除不稳'不能作为刚性假阳性的补救轴**。
- **paraphrase 轴给出小而显著的部分分离**：`consensus-rigid` 下 Qwen 0.583 [0.521, 0.646]、
  Ling 0.604 [0.567, 0.642]（CI 下限 > 0.5）；`fully-rigid` 下更弱（0.533 [0.500, 0.576] /
  0.558 [0.529, 0.588]）。
- **连续 λ 移除曲线只有临界证据**（Qwen 子集，样本小）：`consensus-rigid` 下移除应力面积分离
  0.624 [0.505, 0.754]（CI 下限刚过 0.5）；`fully-rigid` 下 0.565 [0.426, 0.704]（不显著，n=13/13）。
  中间 λ（0.2–0.8）错误刚性面板的移除 flip 一致更高（如 λ=0.4：0.327 vs 0.246），但样本量不足以支撑强结论。
- 对论文的正确表述：把刚性信号定位为**有已知假阳性率的排序信号**（而非'只有错误共识不变'的机制声明），
  并附上本假阳性分解作为 post-hoc 诊断。
""".rstrip())

# ---------------- Section 4: reproducibility ----------------
out.append("")
out.append("## 4. 复现与边界")
out.append("")
out.append("""- 脚本：`round7/stress_profile/scripts/`（`analyze_signature.py` / `analyze_multi_axis.py` /
  `analyze_false_positive.py` / `lambda_features.py` / `make_figures.py` / `render_report.py`）。
  复现：`/storage/gaoym/sp500-forecastability-lab/.venv/bin/python scripts/analyze_*.py`。
- seed：冻结 RS_q 复现用 `20260913`（与 round3 一致）；全部新增 post-hoc 统计用 `20260913+1000` 基
  （`stress_common.POSTHOC_BASE`），2000 次 pair-grouped 重采样。
- 输入哈希与输入文件见头部；未修改任何冻结协议/数字；新增统计一律标注 post-hoc。
- 边界：λ 轴数据仅 Qwen phase3 120-pair 子集（240 项，HC 225 项）；Ling 无 λ 网格数据。
  `rev_flip_rate` 与 `bf_reverse` 在 599/600 项一致（1 项单次 reverse 调用缺失，round3 已记录）。
- bootstrap 复现说明：冻结 RS_q 用原 seed 基复现，Qwen 0.943 [0.924, 0.960] 与 round3 一致；Ling 0.896
  [0.875, 0.917] 与 round6/reducibility 一致（paper v4 §4.7 的 [0.873, 0.916] 为另一 seed 的
  ±0.002 级 bootstrap 差异，不影响任何 gate 结论）。
- 图：`figures/axis_profile_scatter.png`（两模型 HC 的二维压力轮廓散点）、
  `figures/lambda_separation.png`（Qwen λ 子集按正确性分组的翻转曲线）。
""".rstrip())

(HERE / "stress_profile_analysis.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("wrote stress_profile_analysis.md,", len(out), "lines")
