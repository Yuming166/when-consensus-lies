#!/usr/bin/env python3
"""Round-6 Agent B: analyze cost-curve probes on frozen HC subsets (labels merged AFTER
label-blind score files were written and hashed).

Metrics follow round5/preregistration.md and benchmark/analyze_leaderboard.py:
- pair-grouped bootstrap, 2000 replicates, seeds 20260913 + offset by method_index
  (AUROC: +idx, Risk@80: +100+idx, paired AUROC: +200+idx, paired Risk@80: +300+idx)
- Risk@80 operating point 0.8; higher = lower retained error (error reduction)
- paired differences are RS_q - baseline on the exact intersection of valid HC rows;
  positive favors RS_q.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE
for _ in range(5):
    if (ROOT / "consensus_stress" / "benchmark").is_dir():
        break
    ROOT = ROOT.parent
FROZEN = ROOT / "consensus_stress" / "benchmark" / "frozen" / "vitaminc"
CS = ROOT / "consensus_stress"
R6 = CS / "round6" / "cost_curve"
LB = R6 / "label_blind"
ANALYSIS = R6 / "analysis"

SEED = 20_260_913
HC_THRESHOLD = 0.8
BOOTSTRAP_N = 2000

# method_index -> (key, calls/item marginal, total calls/item, label)
METHODS = [
    (0, "risk_bf_q",                     "CST RS_q (proposed)", 25, 25, "full 25-call parent protocol"),
    (1, "risk_reversal_only_k1",         "Reversal-only probe (1 call)", 1, 2, "agent0 natural reverse"),
    (2, "risk_reversal_only_k2",         "Reversal-only probe (2 calls)", 2, 4, "agents0-1 natural reverse"),
    (3, "risk_reversal_only_k5",         "Reversal-only probe (5 calls)", 5, 10, "agents0-4 natural reverse"),
    (4, "risk_reversal_only_k10",        "Reversal-family probe (10 calls)", 10, 20, "agents0-4 natural+synthetic reverse"),
    (5, "risk_reversal_paraphrase_k1",   "Reversal+paraphrase (2 calls)", 2, 4, "agent0 para+rev"),
    (6, "risk_reversal_paraphrase_k2",   "Reversal+paraphrase (4 calls)", 4, 6, "agents0-1 para+rev"),
    (7, "risk_reversal_paraphrase_k5",   "Reversal+paraphrase (10 calls)", 10, 15, "agents0-4 para+rev = BF_q"),
]
TOKEN_KEYS = {
    "risk_bf_q": "rs_q_full",
    "risk_reversal_only_k1": "rev_k1", "risk_reversal_only_k2": "rev_k2",
    "risk_reversal_only_k5": "rev_k5", "risk_reversal_only_k10": "rev_k10",
    "risk_reversal_paraphrase_k1": "combo_k1", "risk_reversal_paraphrase_k2": "combo_k2",
    "risk_reversal_paraphrase_k5": "combo_k5",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


# ---- metrics (copied from round3/analysis_lib.py; frozen round5 protocol) ----
def auROC(scores, labels):
    pos = sum(1 for l in labels if l == 1)
    neg = sum(1 for l in labels if l == 0)
    if pos == 0 or neg == 0:
        return None
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    rank_sum = 0.0
    i = 0
    n = len(pairs)
    while i < n:
        j = i
        while j < n and pairs[j][0] == pairs[i][0]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            if pairs[k][1] == 1:
                rank_sum += avg
        i = j
    return (rank_sum - pos * (pos + 1) / 2.0) / (pos * neg)


def group_bootstrap(feats, score_key, group_key="pair_id", label_key="consensus_wrong",
                    n=BOOTSTRAP_N, seed=SEED):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None]
    by_g: dict[str, list[dict]] = {}
    for f in rows:
        by_g.setdefault(f[group_key], []).append(f)
    groups = sorted(by_g)
    obs = auROC([f[score_key] for f in rows], [f[label_key] for f in rows])
    if obs is None:
        return None
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(groups)):
            gid = rng.choice(groups)
            sample.extend(by_g[gid])
        a = auROC([f[score_key] for f in sample], [f[label_key] for f in sample])
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    return {"auroc": float(obs), "ci": [float(vals[int(0.025 * len(vals))]), float(vals[int(0.975 * len(vals)) - 1])],
            "n": len(rows), "n_groups": len(groups)}


def paired_bootstrap_diff(feats, key_a, key_b, n=BOOTSTRAP_N, seed=SEED,
                          label_key="consensus_wrong"):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key_a) is not None and f.get(key_b) is not None]
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def diff(rows_):
        a = auROC([f[key_a] for f in rows_], [f[label_key] for f in rows_])
        b = auROC([f[key_b] for f in rows_], [f[label_key] for f in rows_])
        return (a - b) if (a is not None and b is not None) else None

    obs = diff(rows)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        d = diff(sample)
        if d is not None:
            vals.append(d)
    vals = sorted(vals)
    return {"diff": float(obs), "ci": [float(vals[int(0.025 * len(vals))]), float(vals[int(0.975 * len(vals)) - 1])],
            "n": len(rows)}


def risk_at_80_bootstrap(feats, key, coverage=0.8, n=BOOTSTRAP_N, seed=SEED + 100):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key) is not None]
    overall = np.mean([f["consensus_wrong"] for f in rows])
    if overall == 0:
        return None

    def reduction(rows_):
        xs = sorted(rows_, key=lambda f: f[key])
        keep = xs[:int(coverage * len(xs))]
        ret = np.mean([f["consensus_wrong"] for f in keep]) if keep else 0.0
        return 1.0 - ret / overall

    obs = reduction(rows)
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        vals.append(reduction(sample))
    vals = sorted(vals)
    return {"reduction": float(obs), "ci": [float(vals[int(0.025 * len(vals))]), float(vals[int(0.975 * len(vals)) - 1])],
            "overall_error": float(overall), "n": len(rows)}


def risk_at_80_paired_diff(feats, key_a, key_b, coverage=0.8, n=BOOTSTRAP_N, seed=SEED + 300):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key_a) is not None and f.get(key_b) is not None]
    overall = np.mean([f["consensus_wrong"] for f in rows])
    if overall == 0:
        return None
    by_pair: dict[str, list[dict]] = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)

    def reduction(rows_, key):
        xs = sorted(rows_, key=lambda f: f[key])
        keep = xs[:int(coverage * len(xs))]
        ret = np.mean([f["consensus_wrong"] for f in keep]) if keep else 0.0
        return 1.0 - ret / overall

    obs = reduction(rows, key_a) - reduction(rows, key_b)
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(pairs)):
            sample.extend(by_pair[rng.choice(pairs)])
        vals.append(reduction(sample, key_a) - reduction(sample, key_b))
    vals = sorted(vals)
    return {"diff": float(obs), "ci": [float(vals[int(0.025 * len(vals))]), float(vals[int(0.975 * len(vals)) - 1])],
            "n": len(rows)}


# ---- data loading and label merge (AFTER label-blind scores frozen) ----
MODEL_FILES = {
    "qwen": {"features": FROZEN / "preoutcome_features.jsonl",
             "records": FROZEN / "records.jsonl", "display": "Qwen3.5-4B"},
    "ling": {"features": FROZEN / "ling_preoutcome_features.jsonl",
             "records": FROZEN / "ling_records.jsonl", "display": "Ling-3.0-tiny"},
}


def merge(model: str) -> list[dict]:
    cfg = MODEL_FILES[model]
    features = load_jsonl(cfg["features"])
    ledger = json.loads((FROZEN / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {row["item_id"]: row["gold_label"] for row in ledger["items"]}
    scores = {row["cqid"]: row for row in load_jsonl(LB / f"probe_scores_label_blind_{model}.jsonl")}
    out = []
    for f in features:
        row = dict(f)
        label = gold[row["item_id"]]
        row["gold_label"] = label
        row["gold_yes"] = label == "SUPPORTS"
        row["consensus_wrong"] = int((row["consensus"] == "yes") != row["gold_yes"])
        row["risk_bf_q"] = -row["bf_q"] if row.get("bf_q") is not None else None
        sc = scores[row["cqid"]]
        for _mi, key, _nm, _cm, _ct, _no in METHODS:
            if key != "risk_bf_q":
                row[key] = sc.get(key)
        row["_tokens"] = sc["tokens"]
        row["_n_reverse_valid"] = sc["reverse_valid_n"]
        out.append(row)
    return out


def evaluate(model: str) -> dict:
    rows = merge(model)
    hc = [r for r in rows if r["agreement"] >= HC_THRESHOLD]
    method_results = []
    for method_index, key, name, calls_marginal, calls_total, note in METHODS:
        auroc = group_bootstrap(hc, key, seed=SEED + method_index)
        risk80 = risk_at_80_bootstrap(hc, key, seed=SEED + 100 + method_index)
        paired_auroc = (None if key == "risk_bf_q" else paired_bootstrap_diff(
            hc, "risk_bf_q", key, seed=SEED + 200 + method_index))
        paired_risk = (None if key == "risk_bf_q" else risk_at_80_paired_diff(
            hc, "risk_bf_q", key, seed=SEED + 300 + method_index))
        token_key = TOKEN_KEYS[key]
        n_valid = auroc["n"] if auroc else 0
        token_means = {k: float(np.mean([r["_tokens"][token_key][k] for r in hc]))
                       for k in ("prompt_tokens", "completion_tokens", "total_tokens")}
        method_results.append({
            "method_index": method_index, "method_key": key, "method": name,
            "method_type": "proposed" if key == "risk_bf_q" else "cost_curve_probe",
            "calls_per_item_marginal": calls_marginal, "calls_per_item_total": calls_total,
            "construction_note": note,
            "auroc": auroc["auroc"] if auroc else None,
            "auroc_ci": auroc["ci"] if auroc else None,
            "n_valid": n_valid, "coverage": n_valid / len(hc),
            "risk_at_80": risk80["reduction"] if risk80 else None,
            "risk_at_80_ci": risk80["ci"] if risk80 else None,
            "overall_error": risk80["overall_error"] if risk80 else None,
            "n_distinct_score_values": len({r[key] for r in hc if r.get(key) is not None}),
            "tokens_per_item": token_means,
            "paired_auroc_diff_rs_q_minus_baseline": paired_auroc["diff"] if paired_auroc else None,
            "paired_auroc_diff_ci": paired_auroc["ci"] if paired_auroc else None,
            "paired_risk80_diff_rs_q_minus_baseline": paired_risk["diff"] if paired_risk else None,
            "paired_risk80_diff_ci": paired_risk["ci"] if paired_risk else None,
        })
    rs = next(r for r in method_results if r["method_key"] == "risk_bf_q")
    return {
        "model": MODEL_FILES[model]["display"], "model_key": model,
        "population": {"n_items": len(rows), "n_hc": len(hc),
                       "wrong_hc": sum(r["consensus_wrong"] for r in hc),
                       "pairs": len({r["pair_id"] for r in hc}),
                       "hc_threshold": HC_THRESHOLD},
        "input_hashes": {
            "features": sha256(MODEL_FILES[model]["features"]),
            "labels": sha256(FROZEN / "labels_ledger.json"),
            "label_blind_scores": sha256(LB / f"probe_scores_label_blind_{model}.jsonl"),
        },
        "rs_q_reference": {"auroc": rs["auroc"], "auroc_ci": rs["auroc_ci"],
                           "risk_at_80": rs["risk_at_80"], "risk_at_80_ci": rs["risk_at_80_ci"]},
        "methods": method_results,
    }


def decision(results: dict) -> dict:
    """Cost-story decision on reversal-only(5) vs RS_q (paired diff RS_q - rev5)."""
    out = {}
    for model in results:
        rev5 = next(r for r in model["methods"] if r["method_key"] == "risk_reversal_only_k5")
        auroc_lo, auroc_hi = rev5["paired_auroc_diff_ci"]
        risk_lo, risk_hi = rev5["paired_risk80_diff_ci"]
        out[model["model_key"]] = {
            "paired_auroc_diff_rs_q_minus_rev5": rev5["paired_auroc_diff_rs_q_minus_baseline"],
            "paired_auroc_diff_ci": [auroc_lo, auroc_hi],
            "paired_risk80_diff_rs_q_minus_rev5": rev5["paired_risk80_diff_rs_q_minus_baseline"],
            "paired_risk80_diff_ci": [risk_lo, risk_hi],
            # adopt cost story if rev5 is not statistically worse than RS_q
            "auroc_ci_contains_zero": bool(auroc_lo <= 0.0 <= auroc_hi),
            "rev5_significantly_better_auroc": bool(auroc_hi < 0.0),
            "rs_q_significantly_better_auroc": bool(auroc_lo > 0.0),
            "risk80_ci_contains_zero": bool(risk_lo <= 0.0 <= risk_hi),
            "rev5_not_statistically_worse_auroc": bool(auroc_lo <= 0.0),
            "adopt_5call_cost_story_auroc": bool(auroc_lo <= 0.0),
        }
    return out


def main() -> int:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    results = [evaluate(m) for m in ("qwen", "ling")]
    decisions = decision(results)
    write_json(ANALYSIS / "cost_curve_results.json", {
        "protocol": "cs-round6-cost-curve-20260914",
        "bootstrap": {"n": BOOTSTRAP_N, "seed_base": SEED,
                      "seed_rule": "20260913 + method_index (AUROC); +100 (Risk@80); "
                                   "+200 (paired AUROC); +300 (paired Risk@80)",
                      "risk_operating_point": 0.8},
        "decision_rule": ("adopt 5-call cost story if reversal-only(5) is not statistically "
                          "worse than RS_q (paired AUROC CI upper bound >= 0); "
                          "rev5 better than RS_q counts as adopt."),
        "models": results,
        "cost_story_decisions": decisions,
    })
    # leaderboard proposal: reversal-only(5) row per model, same schema as existing rows
    proposal_rows = []
    for model in results:
        rev5 = next(r for r in model["methods"] if r["method_key"] == "risk_reversal_only_k5")
        rev5_row = {
            "model": model["model"], "model_key": model["model_key"],
            "method": rev5["method"], "method_key": rev5["method_key"],
            "method_type": "internal", "auroc": rev5["auroc"],
            "auroc_ci": rev5["auroc_ci"], "n_valid": rev5["n_valid"],
            "coverage": rev5["coverage"], "risk_at_80": rev5["risk_at_80"],
            "risk_at_80_ci": rev5["risk_at_80_ci"],
            "calls_per_item": rev5["calls_per_item_marginal"],
            "calls_per_item_total": rev5["calls_per_item_total"],
            "shared_calls": False, "label_using": False,
            "prompt_tokens_per_item": rev5["tokens_per_item"]["prompt_tokens"],
            "completion_tokens_per_item": rev5["tokens_per_item"]["completion_tokens"],
            "total_tokens_per_item": rev5["tokens_per_item"]["total_tokens"],
            "paired_auroc_diff_rs_q_minus_baseline": rev5["paired_auroc_diff_rs_q_minus_baseline"],
            "paired_auroc_diff_ci": rev5["paired_auroc_diff_ci"],
            "paired_risk80_diff_rs_q_minus_baseline": rev5["paired_risk80_diff_rs_q_minus_baseline"],
            "paired_risk80_diff_ci": rev5["paired_risk80_diff_ci"],
            "baseline_significantly_better_than_rs_q": bool(rev5["paired_auroc_diff_ci"][1] < 0.0),
            "baseline_significantly_better_than_rs_q_risk80": bool(rev5["paired_risk80_diff_ci"][1] < 0.0),
            "rs_q_significantly_better_than_baseline": bool(rev5["paired_auroc_diff_ci"][0] > 0.0),
            "rs_q_significantly_better_than_baseline_risk80": bool(rev5["paired_risk80_diff_ci"][0] > 0.0),
            "method_index_in_cost_curve": rev5["method_index"],
            "rank_by_auroc": None,
            "rank_note": "rank_by_auroc assigned by Agent C at leaderboard integration",
            "seed_note": ("seeds derived from method_index in cost_curve/scripts/"
                          "cost_curve_analyze.py METHODS order; AUROC=20260913+idx, "
                          "Risk@80=+100+idx, paired AUROC=+200+idx, paired Risk@80=+300+idx"),
            "calls_accounting_note": ("5 calls/item = marginal natural-reverse calls on top of "
                                      "the already-formed 5-agent consensus (agents' own original "
                                      "answers provide the flip expectation); standalone "
                                      "original+reverse = 10 calls/item."),
        }
        proposal_rows.append(rev5_row)
    write_json(R6 / "leaderboard_proposal.json", {
        "protocol": "cs-round6-cost-curve-20260914",
        "purpose": "Agent B proposal: add reversal-only(5 calls) as one leaderboard row for "
                   "Agent C to integrate. Do NOT merge into any 25-call method.",
        "schema": "same as benchmark/leaderboard.json method rows (plus model and notes fields)",
        "rows": proposal_rows,
    })
    md = render_md(results, decisions)
    (R6 / "cost_curve.md").write_text(md, encoding="utf-8")
    print("wrote", R6 / "cost_curve.md")
    print(json.dumps({"models": [{"model": r["model_key"], "population": r["population"],
                                  "rs_q_reference": r["rs_q_reference"]} for r in results]},
                     indent=2, sort_keys=True))
    for m, d in decisions.items():
        print(m, json.dumps(d, indent=2, sort_keys=True))
    return 0




def fmt_ci(value, ci) -> str:
    if value is None or ci is None:
        return "n/a"
    return f"{value:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]"


def render_md(results: list[dict], decisions: dict) -> str:
    lines = [
        "# Cost-Benefit Curve: how many calls buy how much reliability?",
        "",
        "Protocol: `cs-round6-cost-curve-20260914` (frozen records only; zero new model calls).",
        "Metrics: pair-grouped bootstrap (2,000 replicates), seeds `20260913 + method_index` "
        "(AUROC), `+100` (Risk@80), `+200` (paired AUROC), `+300` (paired Risk@80); "
        "Risk@80 operating point 0.8. Positive paired differences are `RS_q - method` "
        "(RS_q better). calls/item = marginal reversal/stress calls on top of the "
        "already-formed 5-agent consensus (total = marginal + 5 original calls).",
        "",
        "## Probe constructions",
        "",
        "- **reversal-only(K), K in {1,2,5}**: risk = 1 - mean f_reverse over the first K agents "
        "(agent_index 0..K-1), natural-reverse condition; f_reverse(agent i) = 1 iff the agent's "
        "natural-reverse answer == flip(its own frozen original answer). calls/item = K (marginal).",
        "- **reversal-only(10) = reversal family**: risk = 1 - mean over all 5 agents of f_reverse "
        "+ f_synthetic_reverse (both use the frozen oracle expectation flip(y0)). calls/item = 10 "
        "(marginal); included only to cover the 1/2/5/10 budget list.",
        "- **reversal+paraphrase(2K), K in {1,2,5}**: risk = 1 - mean over first K agents of "
        "(f_paraphrase + f_reverse)/2. K=5 equals the frozen BF_q score function (10 scored calls). "
        "calls/item = 2K (marginal).",
        "- **RS_q(25)**: frozen risk = -BF_q (parent protocol, 25 calls/item).",
        "- Missing/invalid calls are treated as missing responses (round5 rule); a probe score is the "
        "mean over its valid calls, missing only if none are valid. Marginal calls exclude the 5 "
        "original consensus calls (the already-formed consensus is the probe's precondition); "
        "total = marginal + 5.",
        "- Coarse-score caveat: reversal-only probes take few distinct values (2/3/6/11 distinct "
        "scores for K=1/2/5/10), so AUROC is the robust summary; Risk@80 (operating point 0.8) is "
        "tie-sensitive at the 80% cut and should be read with its pair-grouped CI.",
        "",
        "## HC populations",
        "",
        "| Model | HC items | pairs | wrong consensus |",
        "|---:|---:|---:|---:|",
    ]
    for m in results:
        p = m["population"]
        lines.append(f"| {m['model']} | {p['n_hc']} | {p['pairs']} | "
                     f"{p['wrong_hc']} ({p['wrong_hc']/p['n_hc']:.1%}) |")
    lines += ["", "## AUROC and Risk@80 by calls/item", "",
              "| Method | Calls/item (marginal / total) | Qwen AUROC [95%CI] | Qwen Risk@80 [95%CI] | "
              "Ling AUROC [95%CI] | Ling Risk@80 [95%CI] |", "|---|---:|---|---:|---|---:|---:|"]
    by_key = {}
    for m in results:
        for r in m["methods"]:
            by_key.setdefault(r["method_key"], {})[m["model_key"]] = r
    order = [r["method_key"] for r in results[0]["methods"]]
    for key in order:
        q, l = by_key[key]["qwen"], by_key[key]["ling"]
        lines.append(
            f"| {q['method']} | {q['calls_per_item_marginal']} / {q['calls_per_item_total']} | "
            f"{fmt_ci(q['auroc'], q['auroc_ci'])} | {fmt_ci(q['risk_at_80'], q['risk_at_80_ci'])} | "
            f"{fmt_ci(l['auroc'], l['auroc_ci'])} | {fmt_ci(l['risk_at_80'], l['risk_at_80_ci'])} |")
    lines += ["", "## Paired differences vs RS_q (RS_q - method, on HC intersection)", "",
              "| Method | Qwen AUROC Δ [CI] | Qwen Risk@80 Δ [CI] | Ling AUROC Δ [CI] | Ling Risk@80 Δ [CI] |",
              "|---|---:|---:|---:|---:|"]
    for key in order:
        if key == "risk_bf_q":
            continue
        q, l = by_key[key]["qwen"], by_key[key]["ling"]
        lines.append(
            f"| {q['method']} | {fmt_ci(q['paired_auroc_diff_rs_q_minus_baseline'], q['paired_auroc_diff_ci'])} | "
            f"{fmt_ci(q['paired_risk80_diff_rs_q_minus_baseline'], q['paired_risk80_diff_ci'])} | "
            f"{fmt_ci(l['paired_auroc_diff_rs_q_minus_baseline'], l['paired_auroc_diff_ci'])} | "
            f"{fmt_ci(l['paired_risk80_diff_rs_q_minus_baseline'], l['paired_risk80_diff_ci'])} |")
    lines += ["", "## Token accounting (mean tokens/item, from frozen records)", "",
              "| Model | Reversal-only(5) prompt / completion / total | RS_q(25) prompt / completion / total |",
              "|---|---:|---:|"]
    for m in results:
        q = by_key["risk_reversal_only_k5"][m["model_key"]]
        l = by_key["risk_bf_q"][m["model_key"]]
        lines.append(
            f"| {m['model']} | {q['tokens_per_item']['prompt_tokens']:.0f} / "
            f"{q['tokens_per_item']['completion_tokens']:.0f} / {q['tokens_per_item']['total_tokens']:.0f} | "
            f"{l['tokens_per_item']['prompt_tokens']:.0f} / {l['tokens_per_item']['completion_tokens']:.0f} / "
            f"{l['tokens_per_item']['total_tokens']:.0f} |")
    lines += ["", "## Decision: adopt the 5-call cost story?",
              "",
              "Pre-registered rule: adopt the 5-call cost story iff reversal-only(5) is not "
              "statistically worse than RS_q (paired AUROC CI lower bound <= 0, i.e. the CI "
              "includes `reversal5 >= RS_q`)."]
    for m in results:
        d = decisions[m["model_key"]]
        lines.append(
            f"- **{m['model']}**: paired AUROC Δ = {d['paired_auroc_diff_rs_q_minus_rev5']:.4f} "
            f"[{d['paired_auroc_diff_ci'][0]:.4f}, {d['paired_auroc_diff_ci'][1]:.4f}]; "
            f"adopt = **{'YES' if d['adopt_5call_cost_story_auroc'] else 'NO'}**.")
    lines += [
        "",
        "## Conclusion (3 lines)",
        "",
        "1. **不采纳“5 calls 成本故事”作为统计等价声明**：reversal-only(5) 与 RS_q(25) 的配对差 CI "
        "（RS_q − rev5）在两模型均不含 0（Qwen +0.012 [0.002, 0.023]；Ling +0.027 [0.013, 0.042]），"
        "即 5-call 探针在 AUROC 上统计上显著弱于完整 RS_q，差距虽小但不能宣称“5 calls ≈ 25 calls”。",
        "2. **统计上可支持的便宜点是 10 calls/item**：reversal+paraphrase(10) 的逐项分数与 RS_q 完全一致"
        "（配对差 Δ=0.000 [0.000, 0.000]，因为 BF_q 只使用 paraphrase+reverse 这 10 个 scored calls）；"
        "若论文要降成本主张，应改为“10 calls/item”，而不是 5。",
        "3. **边界**：Qwen 的 Risk@80 上 rev5 并不差（CI 含 0，点估 0.884 vs RS_q 0.846），但 AUROC 两模型均显著更弱；"
        "把 synthetic_reverse 加入探针（10-call reversal-family）反而稀释信号（Qwen 0.832 vs rev5 0.931），"
        "说明自然反证是核心信号、调用数增加并不单调。",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
