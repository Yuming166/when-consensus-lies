#!/usr/bin/env python3
"""Analyze CST-Bench methods and build the frozen leaderboard."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.isotonic import IsotonicRegression

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
CS = PROJECT / "consensus_stress"
R3 = CS / "round3"
R5 = CS / "round5"
FROZEN = HERE / "frozen" / "vitaminc"
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))
import analysis_lib as al

SEED = 20_260_913
HC_THRESHOLD = 0.8

METHODS = [
    {"key": "risk_bf_q", "name": "CST RS_q (proposed)", "type": "proposed",
     "calls_per_item": 25, "token_scope": "internal_all", "shared": False, "label_using": False},
    {"key": "risk_R_sym", "name": "R_sym (internal)", "type": "internal",
     "calls_per_item": 25, "token_scope": "internal_all", "shared": False, "label_using": False},
    {"key": "risk_R_PI", "name": "R_PI (internal)", "type": "internal",
     "calls_per_item": 25, "token_scope": "internal_all", "shared": False, "label_using": False},
    {"key": "risk_vote_agreement", "name": "Vote agreement", "type": "internal",
     "calls_per_item": 5, "token_scope": "internal_original", "shared": False, "label_using": False},
    {"key": "risk_frozen_confidence", "name": "Frozen mean confidence", "type": "internal",
     "calls_per_item": 5, "token_scope": "internal_original", "shared": False, "label_using": False},
    {"key": "risk_self_consistency_disagreement", "name": "Self-consistency disagreement", "type": "external",
     "calls_per_item": 25, "token_scope": "sample", "shared": True, "label_using": False},
    {"key": "risk_selfcheck_answer_match", "name": "SelfCheckGPT answer-match", "type": "external",
     "calls_per_item": 25, "token_scope": "sample", "shared": True, "label_using": False},
    {"key": "risk_semantic_entropy_binary", "name": "Binary semantic entropy", "type": "external",
     "calls_per_item": 25, "token_scope": "sample", "shared": True, "label_using": False},
    {"key": "risk_sample_mean_confidence", "name": "Raw sampled confidence", "type": "external",
     "calls_per_item": 25, "token_scope": "sample", "shared": True, "label_using": False},
    {"key": "risk_isotonic_sample_confidence", "name": "Isotonic confidence", "type": "external",
     "calls_per_item": 25, "token_scope": "sample", "shared": True, "label_using": True},
    {"key": "risk_temperature_sample_confidence", "name": "Temperature confidence", "type": "external",
     "calls_per_item": 25, "token_scope": "sample", "shared": True, "label_using": True},
    {"key": "risk_single_agent_intervention", "name": "Single-agent intervention", "type": "external",
     "calls_per_item": 25, "token_scope": "intervention", "shared": False, "label_using": False},
]

MODEL_FILES = {
    "qwen": {
        "features": FROZEN / "preoutcome_features.jsonl",
        "records": FROZEN / "records.jsonl",
        "display": "Qwen3.5-4B",
    },
    "ling": {
        "features": FROZEN / "ling_preoutcome_features.jsonl",
        "records": FROZEN / "ling_records.jsonl",
        "display": "Ling-3.0-tiny",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def usage_number(usage: dict, key: str) -> float:
    value = usage.get(key)
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0


def record_usage(record: dict) -> dict:
    attempts = record.get("attempts") or []
    usage = attempts[-1].get("usage") if attempts else record.get("usage")
    return dict(usage or {})


def token_stats_external(records: list[dict], family: str) -> dict[str, float]:
    by_item: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        if rec["family"] == family:
            by_item[rec["cqid"]].append(rec)
    sums = {"prompt_tokens": [], "completion_tokens": [], "total_tokens": []}
    for cqid in sorted(by_item):
        recs = by_item[cqid]
        for key, values in sums.items():
            values.append(sum(usage_number(r.get("usage", {}), key) for r in recs))
    return {key: float(np.mean(vals)) if vals else 0.0 for key, vals in sums.items()}


def token_stats_internal(records: list[dict], scope: str) -> dict[str, float]:
    by_item: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        if scope == "internal_original" and rec["condition"] != "original":
            continue
        by_item[rec["cqid"]].append(rec)
    sums = {"prompt_tokens": [], "completion_tokens": [], "total_tokens": []}
    for cqid in sorted(by_item):
        recs = by_item[cqid]
        for key, values in sums.items():
            values.append(sum(usage_number(record_usage(r), key) for r in recs))
    return {key: float(np.mean(vals)) if vals else 0.0 for key, vals in sums.items()}


def merge_outcomes(model_key: str) -> tuple[list[dict], dict]:
    cfg = MODEL_FILES[model_key]
    features = load_jsonl(cfg["features"])
    ledger = json.loads((FROZEN / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {row["item_id"]: row["gold_label"] for row in ledger["items"]}
    external = {row["cqid"]: row for row in
                load_jsonl(R5 / f"{model_key}_baseline_scores_label_blind.jsonl")}
    for row in features:
        label = gold[row["item_id"]]
        row["gold_label"] = label
        row["gold_yes"] = label == "SUPPORTS"
        row["consensus_wrong"] = int((row["consensus"] == "yes") != row["gold_yes"])
        row["risk_bf_q"] = -row["bf_q"] if row.get("bf_q") is not None else None
        row["risk_R_sym"] = row.get("R_sym")
        row["risk_R_PI"] = row.get("R_PI")
        row["risk_vote_agreement"] = 1.0 - row["agreement"]
        row["risk_frozen_confidence"] = 1.0 - row["mean_confidence"]
        ext = external.get(row["cqid"], {})
        for key, value in ext.items():
            if key not in {"cqid", "item_id", "pair_id"}:
                row[f"ext_{key}"] = value
        for method in METHODS:
            if method["key"].startswith("risk_self") or method["key"] in {
                "risk_semantic_entropy_binary", "risk_sample_mean_confidence",
                "risk_single_agent_intervention"}:
                row[method["key"]] = row.get(f"ext_{method['key']}")
    hashes = {
        "features": sha256(cfg["features"]),
        "labels": sha256(FROZEN / "labels_ledger.json"),
        "external_label_blind_scores": sha256(R5 / f"{model_key}_baseline_scores_label_blind.jsonl"),
    }
    return features, hashes


def calibration_folds(rows: list[dict]) -> dict[str, int]:
    pairs = sorted({row["pair_id"] for row in rows})
    return {pair: i % 5 for i, pair in enumerate(pairs)}


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def temperature_risk(confidence: np.ndarray, temperature: float) -> np.ndarray:
    z = np.log(np.clip(confidence, 0.01, 0.99) / (1.0 - np.clip(confidence, 0.01, 0.99)))
    return 1.0 - sigmoid(z / temperature)


def fit_temperature(confidence: np.ndarray, labels: np.ndarray) -> float:
    def objective(t: float) -> float:
        p = np.clip(temperature_risk(confidence, t), 1e-6, 1.0 - 1e-6)
        return float(-np.mean(labels * np.log(p) + (1.0 - labels) * np.log(1.0 - p)))
    result = minimize_scalar(objective, bounds=(0.05, 20.0), method="bounded")
    return float(result.x)


def add_oof_calibrations(rows: list[dict]) -> list[dict]:
    hc = [row for row in rows if row["agreement"] >= HC_THRESHOLD]
    folds = calibration_folds(hc)
    by_pair: dict[int, list[dict]] = defaultdict(list)
    for row in hc:
        by_pair[folds[row["pair_id"]]].append(row)
    out = []
    for fold, test_rows in sorted(by_pair.items()):
        train_rows = [row for f, rows in by_pair.items() if f != fold for row in rows]
        train_x = np.array([row["ext_sample_mean_confidence"] for row in train_rows
                            if row.get("ext_sample_mean_confidence") is not None], dtype=float)
        train_y = np.array([row["consensus_wrong"] for row in train_rows
                            if row.get("ext_sample_mean_confidence") is not None], dtype=float)
        iso = IsotonicRegression(y_min=0.0, y_max=1.0, increasing=False, out_of_bounds="clip")
        iso.fit(train_x, train_y)
        temperature = fit_temperature(train_x, train_y)
        for row in test_rows:
            confidence = row.get("ext_sample_mean_confidence")
            if confidence is None:
                iso_risk = temp_risk = 1.0
            else:
                iso_risk = float(iso.predict([[confidence]])[0])
                temp_risk = float(temperature_risk(np.array([confidence]), temperature)[0])
            row["risk_isotonic_sample_confidence"] = iso_risk
            row["risk_temperature_sample_confidence"] = temp_risk
            out.append({
                "cqid": row["cqid"], "item_id": row["item_id"], "pair_id": row["pair_id"],
                "fold": fold, "sample_mean_confidence": confidence,
                "risk_isotonic_sample_confidence": iso_risk,
                "risk_temperature_sample_confidence": temp_risk,
                "temperature_fit": temperature,
            })
    return out


def evaluate_model(model_key: str) -> dict:
    rows, hashes = merge_outcomes(model_key)
    calibrated = add_oof_calibrations(rows)
    write_jsonl = R5 / f"{model_key}_calibrated_scores.jsonl"
    with write_jsonl.open("w", encoding="utf-8") as handle:
        for row in calibrated:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    hc = [row for row in rows if row["agreement"] >= HC_THRESHOLD]
    records_internal = load_jsonl(MODEL_FILES[model_key]["records"])
    records_external = load_jsonl(R5 / f"{model_key}_baseline_records.jsonl")
    tokens = {
        "internal_all": token_stats_internal(records_internal, "internal_all"),
        "internal_original": token_stats_internal(records_internal, "internal_original"),
        "sample": token_stats_external(records_external, "sampling"),
        "intervention": token_stats_external(records_external, "intervention"),
    }

    method_results = []
    for method_index, method in enumerate(METHODS):
        key = method["key"]
        auroc = al.group_bootstrap(hc, key, seed=SEED + method_index)
        risk80 = al.risk_at_80_bootstrap(hc, key, seed=SEED + 100 + method_index)
        if method["type"] == "proposed":
            paired_auroc = paired_risk80 = None
        else:
            paired_auroc = al.paired_bootstrap_diff(
                hc, "risk_bf_q", key, seed=SEED + 200 + method_index)
            paired_risk80 = al.risk_at_80_paired_diff(
                hc, "risk_bf_q", key, seed=SEED + 300 + method_index)
        token = tokens[method["token_scope"]]
        result = {
            "method": method["name"], "method_key": key, "method_type": method["type"],
            "auroc": auroc["auroc"] if auroc else None,
            "auroc_ci": auroc["ci"] if auroc else None,
            "n_valid": auroc["n"] if auroc else 0,
            "coverage": (auroc["n"] / len(hc)) if auroc else 0.0,
            "risk_at_80": risk80["reduction"] if risk80 else None,
            "risk_at_80_ci": risk80["ci"] if risk80 else None,
            "calls_per_item": method["calls_per_item"],
            "shared_calls": method["shared"], "label_using": method["label_using"],
            "prompt_tokens_per_item": token["prompt_tokens"],
            "completion_tokens_per_item": token["completion_tokens"],
            "total_tokens_per_item": token["total_tokens"],
            "paired_auroc_diff_rs_q_minus_baseline": paired_auroc["diff"] if paired_auroc else None,
            "paired_auroc_diff_ci": paired_auroc["ci"] if paired_auroc else None,
            "paired_risk80_diff_rs_q_minus_baseline": paired_risk80["diff"] if paired_risk80 else None,
            "paired_risk80_diff_ci": paired_risk80["ci"] if paired_risk80 else None,
        }
        if paired_auroc and paired_auroc["ci"]:
            lo, hi = paired_auroc["ci"]
            result["baseline_significantly_better_than_rs_q"] = bool(hi < 0.0)
            result["rs_q_significantly_better_than_baseline"] = bool(lo > 0.0)
        else:
            result["baseline_significantly_better_than_rs_q"] = False
            result["rs_q_significantly_better_than_baseline"] = False
        if paired_risk80 and paired_risk80["ci"]:
            risk_lo, risk_hi = paired_risk80["ci"]
            result["baseline_significantly_better_than_rs_q_risk80"] = bool(risk_hi < 0.0)
            result["rs_q_significantly_better_than_baseline_risk80"] = bool(risk_lo > 0.0)
        else:
            result["baseline_significantly_better_than_rs_q_risk80"] = False
            result["rs_q_significantly_better_than_baseline_risk80"] = False
        method_results.append(result)

    method_results.sort(key=lambda r: (
        -(r["auroc"] if r["auroc"] is not None else -1.0),
        -(r["risk_at_80"] if r["risk_at_80"] is not None else -1.0),
        r["calls_per_item"], r["method"]))
    for rank, row in enumerate(method_results, 1):
        row["rank_by_auroc"] = rank
    rs_row = next(r for r in method_results if r["method_key"] == "risk_bf_q")
    baselines = [r for r in method_results if r["method_key"] != "risk_bf_q"]
    return {
        "model": MODEL_FILES[model_key]["display"], "model_key": model_key,
        "population": {
            "n_items": len(rows), "n_hc": len(hc),
            "wrong_hc": sum(r["consensus_wrong"] for r in hc),
            "hc_threshold": HC_THRESHOLD,
            "pairs": len({r["pair_id"] for r in hc}),
        },
        "input_hashes": hashes,
        "token_accounting": tokens,
        "calibration": {
            "method": "pair-grouped 5-fold OOF; isotonic decreasing; temperature log-loss",
            "rows": len(calibrated),
            "fold_counts": {str(k): sum(r["fold"] == k for r in calibrated) for k in range(5)},
        },
        "methods": method_results,
        "sota_summary": {
            "best_method_by_auroc_point": method_results[0]["method"],
            "best_auroc": method_results[0]["auroc"],
            "rs_q_rank_by_auroc": rs_row["rank_by_auroc"],
            "rs_q_auroc": rs_row["auroc"],
            "baselines_significantly_better_than_rs_q": [
                r["method"] for r in baselines if r["baseline_significantly_better_than_rs_q"]],
            "rs_q_statistically_maintains_sota": not any(
                r["baseline_significantly_better_than_rs_q"] for r in baselines),
            "rs_q_point_best": rs_row["rank_by_auroc"] == 1,
        },
    }


def fmt_ci(value: float | None, ci: list[float] | None) -> str:
    if value is None or ci is None:
        return "n/a"
    return f"{value:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]"


def fmt_value(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def write_outputs(results: list[dict]) -> None:
    combined = {
        "protocol": "cs-round5-matched-baselines-cst-bench-20260913",
        "primary_model": "Qwen3.5-4B",
        "secondary_model": "Ling-3.0-tiny",
        "ranking_rule": "AUROC point estimate, then Risk@80, then lower calls/item; descriptive only",
        "models": results,
    }
    write_json(HERE / "leaderboard.json", combined)
    (R5 / "analysis").mkdir(parents=True, exist_ok=True)
    write_json(R5 / "analysis" / "baseline_leaderboard.json", combined)

    fields = ["model", "rank_by_auroc", "method", "method_type", "auroc", "auroc_ci_low",
              "auroc_ci_high", "risk_at_80", "risk_at_80_ci_low", "risk_at_80_ci_high",
              "calls_per_item", "total_tokens_per_item", "n_valid", "coverage",
              "paired_auroc_diff_rs_q_minus_baseline", "paired_auroc_diff_ci_low",
              "paired_auroc_diff_ci_high",
              "paired_risk80_diff_rs_q_minus_baseline", "paired_risk80_diff_ci_low",
              "paired_risk80_diff_ci_high", "baseline_significantly_better_than_rs_q",
              "baseline_significantly_better_than_rs_q_risk80", "shared_calls", "label_using"]
    with (HERE / "leaderboard.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for model in results:
            for row in model["methods"]:
                out = {"model": model["model"]}
                ci_fields = {
                    "auroc_ci_low": ("auroc_ci", 0), "auroc_ci_high": ("auroc_ci", 1),
                    "risk_at_80_ci_low": ("risk_at_80_ci", 0),
                    "risk_at_80_ci_high": ("risk_at_80_ci", 1),
                    "paired_auroc_diff_ci_low": ("paired_auroc_diff_ci", 0),
                    "paired_auroc_diff_ci_high": ("paired_auroc_diff_ci", 1),
                    "paired_risk80_diff_ci_low": ("paired_risk80_diff_ci", 0),
                    "paired_risk80_diff_ci_high": ("paired_risk80_diff_ci", 1),
                }
                for field in fields[1:]:
                    if field in ci_fields:
                        base, index = ci_fields[field]
                        value = row.get(base)
                        value = value[index] if isinstance(value, list) and len(value) == 2 else None
                    else:
                        value = row.get(field)
                    out[field] = value
                writer.writerow(out)

    lines = [
        "# CST-Bench Leaderboard",
        "",
        "Protocol: `cs-round5-matched-baselines-cst-bench-20260913`. Ranking is descriptive:",
        "AUROC point estimate, then Risk@80, then lower calls/item. CIs are pair-grouped",
        "bootstrap intervals. Positive paired differences (`RS_q - baseline`) favor RS_q.",
        "",
    ]
    for model in results:
        pop = model["population"]
        sota = model["sota_summary"]
        lines += [
            f"## {model['model']}",
            "",
            (
                f"HC population: {pop['n_hc']} items / {pop['pairs']} pairs; wrong consensus = "
                f"{pop['wrong_hc']} ({pop['wrong_hc'] / pop['n_hc']:.1%})."
            ),
            "",
            "| Rank | Method | AUROC [95% CI] | Risk@80 [95% CI] | Calls/item | Tokens/item | Paired AUROC Δ vs RS_q [CI] | Paired Risk@80 Δ vs RS_q [CI] | Baseline significantly better on AUROC? |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        for row in model["methods"]:
            paired = fmt_ci(row["paired_auroc_diff_rs_q_minus_baseline"], row["paired_auroc_diff_ci"])
            paired_risk = fmt_ci(row["paired_risk80_diff_rs_q_minus_baseline"], row["paired_risk80_diff_ci"])
            better = "YES" if row["baseline_significantly_better_than_rs_q"] else (
                "—" if row["method_key"] == "risk_bf_q" else "no")
            lines.append(
                f"| {row['rank_by_auroc']} | {row['method']} | "
                f"{fmt_ci(row['auroc'], row['auroc_ci'])} | "
                f"{fmt_ci(row['risk_at_80'], row['risk_at_80_ci'])} | "
                f"{row['calls_per_item']} | {row['total_tokens_per_item']:.0f} | {paired} | "
                f"{paired_risk} | {better} |")
        lines += [
            "",
            (
                f"Point best: **{sota['best_method_by_auroc_point']}** "
                f"(AUROC {sota['best_auroc']:.3f}). RS_q rank: {sota['rs_q_rank_by_auroc']}."
            ),
            (
                f"Baseline(s) significantly better than RS_q by paired AUROC CI: "
                f"{', '.join(sota['baselines_significantly_better_than_rs_q']) or 'none'}. "
                f"RS_q statistically maintains SOTA: **{'YES' if sota['rs_q_statistically_maintains_sota'] else 'NO'}**."
            ),
            "",
        ]
    lines += [
        "## Claim boundary",
        "",
        "- Qwen is the primary model; Ling is secondary.",
        "- The leaderboard covers the frozen 300-pair VitaminC natural-pair main split and HC subsets.",
        "- BoolQ is packaged as a specificity/negative-control split and is not part of this leaderboard.",
        "- No universal transfer, zero-shot, or all-domain SOTA claim is supported.",
        "",
    ]
    (HERE / "LEADERBOARD.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", choices=("qwen", "ling"), default=["qwen", "ling"])
    args = parser.parse_args()
    results = [evaluate_model(model) for model in args.models]
    write_outputs(results)
    print(json.dumps([{ "model": r["model"], **r["sota_summary"]} for r in results], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
