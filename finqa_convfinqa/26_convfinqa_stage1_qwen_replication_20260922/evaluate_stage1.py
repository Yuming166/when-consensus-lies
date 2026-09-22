#!/usr/bin/env python3
"""Offline analysis for frozen ConvFinQA Stage-1 Qwen DEV records."""
from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "CONVFINQA_STAGE1_QWEN_REPLICATION_CONTRACT.json"
PROMPTS = HERE / "STAGE1_DEV_PROMPTS.jsonl"
GOLD = HERE / "STAGE1_DEV_WORLD_GOLD.jsonl"
RAW = HERE / "STAGE1_QWEN_DEV_RAW_RECORDS.jsonl"
OUT = HERE / "STAGE1_QWEN_DEV_ANALYSIS.json"
MD = HERE / "STAGE1_QWEN_DEV_ANALYSIS.md"
NULL_SEED = 20260922
BOOTSTRAP_REPS = 5000
NULL_REPS = 5000


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def parse_surface(raw: Any) -> dict[str, Any] | None:
    if raw is None or isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not text or len(text) > 128:
        return None
    percent = "%" in text
    parentheses = "(" in text and ")" in text
    cleaned = text.replace("$", "").replace(",", "").replace("%", "").replace("(", "").replace(")", "")
    cleaned = "".join(cleaned.split())
    if not cleaned or cleaned in {"+", "-", "."}:
        return None
    negative = text.startswith("-") or parentheses
    try:
        value = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None
    if negative:
        value = -abs(value)
    return {"normalized": value / Decimal(100) if percent else value, "percent": percent, "text": text}


def auc(scores: list[float], labels: list[int]) -> float | None:
    if len(scores) != len(labels) or not scores:
        return None
    positives = [s for s, y in zip(scores, labels) if y == 1]
    negatives = [s for s, y in zip(scores, labels) if y == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    for p in positives:
        for n in negatives:
            wins += 1.0 if p > n else 0.5 if p == n else 0.0
    return wins / (len(positives) * len(negatives))


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def bootstrap_auc(scores: list[float], labels: list[int], *, seed: int = NULL_SEED, reps: int = BOOTSTRAP_REPS) -> dict[str, Any]:
    observed = auc(scores, labels)
    rng = random.Random(seed)
    vals: list[float] = []
    invalid = 0
    n = len(labels)
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        value = auc([scores[i] for i in idx], [labels[i] for i in idx])
        if value is None:
            invalid += 1
        else:
            vals.append(value)
    return {"observed": observed, "replicates": reps, "valid_replicates": len(vals), "invalid_replicates": invalid, "ci_95": [percentile(vals, 0.025), percentile(vals, 0.975)]}


def bootstrap_delta(scores_a: list[float], scores_b: list[float], labels: list[int], *, seed: int = NULL_SEED, reps: int = BOOTSTRAP_REPS) -> dict[str, Any]:
    observed_a = auc(scores_a, labels)
    observed_b = auc(scores_b, labels)
    observed = None if observed_a is None or observed_b is None else observed_a - observed_b
    rng = random.Random(seed)
    vals: list[float] = []
    invalid = 0
    n = len(labels)
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        a = auc([scores_a[i] for i in idx], [labels[i] for i in idx])
        b = auc([scores_b[i] for i in idx], [labels[i] for i in idx])
        if a is None or b is None:
            invalid += 1
        else:
            vals.append(a - b)
    return {"observed": observed, "replicates": reps, "valid_replicates": len(vals), "invalid_replicates": invalid, "ci_95": [percentile(vals, 0.025), percentile(vals, 0.975)]}


def cluster_bootstrap_auc(rows: list[dict[str, Any]], score_key: str, label_key: str, *, cluster_key: str = "filename", seed: int = NULL_SEED + 1, reps: int = BOOTSTRAP_REPS) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[cluster_key])].append(row)
    group_values = list(groups.values())
    scores = [float(r[score_key]) for r in rows]
    labels = [int(r[label_key]) for r in rows]
    observed = auc(scores, labels)
    rng = random.Random(seed)
    vals: list[float] = []
    invalid = 0
    for _ in range(reps):
        sampled = [group_values[rng.randrange(len(group_values))] for _ in group_values]
        flat = [r for group in sampled for r in group]
        value = auc([float(r[score_key]) for r in flat], [int(r[label_key]) for r in flat])
        if value is None:
            invalid += 1
        else:
            vals.append(value)
    return {"cluster_key": cluster_key, "cluster_count": len(group_values), "observed": observed, "replicates": reps, "valid_replicates": len(vals), "invalid_replicates": invalid, "ci_95": [percentile(vals, 0.025), percentile(vals, 0.975)]}


def permutation_p(scores: list[float], labels: list[int], *, groups: list[str] | None = None, seed: int = NULL_SEED + 2, reps: int = NULL_REPS) -> dict[str, Any]:
    observed = auc(scores, labels)
    rng = random.Random(seed)
    if observed is None:
        return {"observed": None, "replicates": reps, "p_ge_observed": None, "valid_replicates": 0}
    null: list[float] = []
    if groups is None:
        for _ in range(reps):
            perm = list(labels)
            rng.shuffle(perm)
            value = auc(scores, perm)
            if value is not None:
                null.append(value)
    else:
        positions: dict[str, list[int]] = defaultdict(list)
        for i, group in enumerate(groups):
            positions[str(group)].append(i)
        for _ in range(reps):
            perm = list(labels)
            for idx in positions.values():
                values = [labels[i] for i in idx]
                rng.shuffle(values)
                for i, value in zip(idx, values):
                    perm[i] = value
            value = auc(scores, perm)
            if value is not None:
                null.append(value)
    return {"observed": observed, "replicates": reps, "valid_replicates": len(null), "p_ge_observed": (1 + sum(x >= observed for x in null)) / (len(null) + 1) if null else None, "null_p95": percentile(null, 0.95)}


def score_record(record: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_surface(record.get("answer")) if record.get("valid") else None
    try:
        expected = Decimal(str(gold["expected_normalized_answer"]))
        tolerance = Decimal(str(gold["expected_tolerance"]))
    except (InvalidOperation, KeyError, TypeError, ValueError):
        expected = None
        tolerance = None
    numeric_valid = parsed is not None and expected is not None and tolerance is not None
    correct = bool(numeric_valid and abs(parsed["normalized"] - expected) <= tolerance)
    return {
        "world_id": gold["world_id"], "item_id": gold["item_id"], "world_label": gold["world_label"], "arm": gold["arm"], "filename": gold["filename"], "source_group_id": gold["source_group_id"], "program_ops": gold.get("program_ops", []), "unit_hint": gold["unit_hint"], "predicted_raw": record.get("answer"), "predicted_unit": None if parsed is None else ("percent" if parsed["percent"] else "plain"), "schema_valid": bool(record.get("valid")), "numeric_valid": numeric_valid, "predicted_normalized": None if parsed is None else format(parsed["normalized"], "f"), "expected_normalized": None if expected is None else format(expected, "f"), "tolerance": None if tolerance is None else format(tolerance, "f"), "answer_correct": correct, "confidence": record.get("confidence"), "parse_error": record.get("parse_error"),
    }


def item_rows(scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in scored:
        grouped[row["item_id"]][row["world_label"]] = row
    output: list[dict[str, Any]] = []
    for item_id in sorted(grouped):
        worlds = grouped[item_id]
        required = {"original", "relevant_k_minus2", "relevant_k_minus1", "relevant_k_plus1", "relevant_k_plus2"}
        if not required.issubset(worlds):
            continue
        base = worlds["original"]
        relevant = [worlds[x] for x in ("relevant_k_minus2", "relevant_k_minus1", "relevant_k_plus1", "relevant_k_plus2")]
        row = {
            "item_id": item_id, "filename": base["filename"], "source_group_id": base["source_group_id"], "program_ops": base.get("program_ops", []), "original_correct": int(base["answer_correct"]), "original_schema_valid": int(base["schema_valid"]), "original_numeric_valid": int(base["numeric_valid"]), "s2": (int(worlds["relevant_k_minus1"]["answer_correct"]) + int(worlds["relevant_k_plus1"]["answer_correct"])) / 2.0, "full_cef": sum(int(x["answer_correct"]) for x in relevant) / 4.0, "minus2_correct": int(worlds["relevant_k_minus2"]["answer_correct"]), "minus1_correct": int(worlds["relevant_k_minus1"]["answer_correct"]), "plus1_correct": int(worlds["relevant_k_plus1"]["answer_correct"]), "plus2_correct": int(worlds["relevant_k_plus2"]["answer_correct"]), "unit_hint": base["unit_hint"],
        }
        output.append(row)
    return output


def signal_metrics(rows: list[dict[str, Any]], score_key: str) -> dict[str, Any]:
    scores = [float(x[score_key]) for x in rows]
    labels = [int(x["original_correct"]) for x in rows]
    groups = [str(x["program_ops"]) for x in rows]
    by_filename = cluster_bootstrap_auc(rows, score_key, "original_correct", seed=NULL_SEED + (10 if score_key == "s2" else 11))
    item = bootstrap_auc(scores, labels, seed=NULL_SEED + (20 if score_key == "s2" else 21))
    global_perm = permutation_p(scores, labels, seed=NULL_SEED + (30 if score_key == "s2" else 31))
    within_perm = permutation_p(scores, labels, groups=groups, seed=NULL_SEED + (40 if score_key == "s2" else 41))
    gate = bool(item["observed"] is not None and item["observed"] > 0.5 and item["ci_95"][0] is not None and item["ci_95"][0] > 0.5 and global_perm["p_ge_observed"] is not None and global_perm["p_ge_observed"] < 0.05 and within_perm["p_ge_observed"] is not None and within_perm["p_ge_observed"] < 0.05)
    return {"auroc": item, "filename_cluster_bootstrap": by_filename, "global_permutation": global_perm, "within_operation_permutation": within_perm, "gate": gate}


def main() -> None:
    contract = load_json(CONTRACT)
    prompts = load_jsonl(PROMPTS)
    gold = load_jsonl(GOLD)
    raw = load_jsonl(RAW)
    expected_ids = [x["world_id"] for x in prompts]
    failures: list[dict[str, Any]] = []
    if len(raw) != len(expected_ids):
        failures.append({"reason": "record_count_mismatch", "observed": len(raw), "expected": len(expected_ids)})
    raw_by_id = {}
    for record in raw:
        wid = record.get("world_id")
        if wid in raw_by_id:
            failures.append({"reason": "duplicate_world_id", "world_id": wid})
        raw_by_id[wid] = record
    prompt_by_id = {x["world_id"]: x for x in prompts}
    gold_by_id = {x["world_id"]: x for x in gold}
    for wid in expected_ids:
        if wid not in raw_by_id:
            failures.append({"reason": "missing_world_id", "world_id": wid})
            continue
        r = raw_by_id[wid]
        p = prompt_by_id[wid]
        g = gold_by_id[wid]
        for field in ("input_sha256", "prompt_hash"):
            if r.get(field) != p.get(field) or r.get(field) != g.get(field):
                failures.append({"reason": f"{field}_mismatch", "world_id": wid})
        if r.get("returned_model") not in (None, contract["model_identity"]["expected_model"]):
            failures.append({"reason": "identity_drift", "world_id": wid, "returned_model": r.get("returned_model")})
    scored = [score_record(raw_by_id[wid], gold_by_id[wid]) for wid in expected_ids if wid in raw_by_id]
    rows = item_rows(scored)
    s2 = signal_metrics(rows, "s2") if rows else {}
    full = signal_metrics(rows, "full_cef") if rows else {}
    delta = bootstrap_delta([x["full_cef"] for x in rows], [x["s2"] for x in rows], [x["original_correct"] for x in rows], seed=NULL_SEED + 100)
    unit_counts = defaultdict(int)
    unit_mismatch = defaultdict(int)
    for x in scored:
        unit_counts[x["unit_hint"]] += 1
        if x["numeric_valid"] and x["predicted_unit"] is not None and x["predicted_unit"] != x["unit_hint"]:
            unit_mismatch[f"{x['unit_hint']}<-{x['predicted_unit']}"] += 1
    result = {
        "protocol": contract["protocol"], "contract": contract["contract"], "status": "ANALYSIS_PASS" if not failures and len(scored) == len(gold) else "FAIL_CLOSED", "model_calls": len(raw), "record_count": len(raw), "gold_count": len(gold), "validation_failures": failures, "scored_world_count": len(scored), "item_count": len(rows), "positive_original_correct": sum(x["original_correct"] for x in rows), "negative_original_correct": sum(1 - x["original_correct"] for x in rows), "parse_schema_valid_rate": sum(x["schema_valid"] for x in scored) / len(scored) if scored else None, "numeric_valid_rate": sum(x["numeric_valid"] for x in scored) / len(scored) if scored else None, "unit_hint_counts": dict(unit_counts), "unit_mismatch_counts_diagnostic_only": dict(unit_mismatch), "s2": s2, "full_cef": full, "full_minus_s2_delta": delta, "stage1_core_gate": bool(s2.get("gate") and full.get("gate")), "stage2_authorized_by_metrics": False, "claim_boundary": "Qwen ConvFinQA Stage-1 diagnostic analysis only; Stage 2/3 remain separately gated and no cross-task distillation claim is established by this artifact.",
    }
    write_json(OUT, result)
    lines = ["# ConvFinQA Stage-1 Qwen DEV analysis", "", f"Status: **{result['status']}**", f"- worlds: {len(raw)} / {len(gold)}", f"- items: {len(rows)}", f"- schema-valid rate: {result['parse_schema_valid_rate']}", f"- S2 AUROC: {s2.get('auroc', {}).get('observed')} CI={s2.get('auroc', {}).get('ci_95')} gate={s2.get('gate')}", f"- Full CEF AUROC: {full.get('auroc', {}).get('observed')} CI={full.get('auroc', {}).get('ci_95')} gate={full.get('gate')}", f"- Full minus S2 paired delta: {delta.get('observed')} CI={delta.get('ci_95')}", f"- Core gate: **{result['stage1_core_gate']}**", "", "Primary correctness is normalized current-turn executable numeric correctness. Unit mismatch counts are diagnostic only; item-level QA answers were not used as current-turn targets.", ""]
    MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "ANALYSIS_PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
