#!/usr/bin/env python3
"""Freeze ConvFinQA Stage-1 Qwen replication inputs and evaluator.

This is an offline-only builder.  It does not call a model or the network.  The
v0.11 executable-semantics contract remains immutable; this addendum only
materializes Stage-1 worlds/prompts and records the current-turn answer
semantics needed by the evaluator.

Primary correctness is normalized numeric correctness, not item-level QA-answer
copying.  ConvFinQA exposes annotation.exe_ans for the current turn but does
not expose a reliable current-turn answer surface for every program turn.  We
therefore normalize an optional percent sign in model outputs and compare to
the current-turn executable answer with a frozen display-tolerance rule.  A
question-derived unit hint is recorded for audit and prompting, but it is not
used to turn later item-level qa/qa_0/qa_1 answers into current-turn labels.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
AUDIT_DIR = REPO / "finqa_convfinqa" / "25_convfinqa_executable_semantics_audit_20260922"
DATA_DIR = AUDIT_DIR / "upstream_data" / "extracted" / "data"
CONTRACT_V11 = AUDIT_DIR / "CONVFINQA_V0_11_FROZEN_CONTRACT.json"
PUBLIC_DEV = AUDIT_DIR / "V11_PRIMARY_DEV_ONE_PER_CONVERSATION_PUBLIC.jsonl"
GOLD_DEV = AUDIT_DIR / "V11_PRIMARY_DEV_ONE_PER_CONVERSATION_GOLD.jsonl"
PUBLIC_TRAIN = AUDIT_DIR / "V11_PRIMARY_TRAIN_ONE_PER_CONVERSATION_PUBLIC.jsonl"
GOLD_TRAIN = AUDIT_DIR / "V11_PRIMARY_TRAIN_ONE_PER_CONVERSATION_GOLD.jsonl"
RAW_DEV = DATA_DIR / "dev_turn.json"
RAW_TRAIN = DATA_DIR / "train_turn.json"

PROTOCOL = "ConvFinQA_PECR_v0.11_stage1_qwen_replication"
CONTRACT_NAME = "CONVFINQA_STAGE1_QWEN_REPLICATION_CONTRACT"
FREEZE_DATE = "2026-09-22"
EXPECTED_MODEL = "Qwen3.5-4B"
ENDPOINT = "http://127.0.0.1:31518/v1/chat/completions"
MODELS_ENDPOINT = "http://127.0.0.1:31518/v1/models"
WORLD_ORDER = ("original", "relevant_k_minus2", "relevant_k_minus1", "relevant_k_plus1", "relevant_k_plus2")
K_BY_LABEL = {
    "relevant_k_minus2": -2,
    "relevant_k_minus1": -1,
    "relevant_k_plus1": 1,
    "relevant_k_plus2": 2,
}

SYSTEM_PROMPT = (
    "You are a careful financial numerical question solver. Use only the question and supplied context. "
    "Return exactly one JSON object with keys answer and confidence. Preserve the answer unit: include a "
    "percent sign for percentage answers (for example 7.6%), and do not include a percent sign for "
    "plain-number answers. Do not convert percentages to fractions. Confidence must be a number from 0 to 1. "
    "Do not include reasoning or any other keys."
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def parse_surface(raw: Any) -> dict[str, Any] | None:
    if raw is None or isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not text or len(text) > 128:
        return None
    percent = "%" in text
    parentheses = "(" in text and ")" in text
    cleaned = text.replace("$", "").replace(",", "").replace("%", "")
    cleaned = cleaned.replace("(", "").replace(")", "")
    cleaned = re.sub(r"\s+", "", cleaned)
    if not cleaned or cleaned in {"+", "-", "."}:
        return None
    negative = text.startswith("-") or parentheses
    try:
        value = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None
    if negative:
        value = -abs(value)
    normalized = value / Decimal(100) if percent else value
    decimals = len(cleaned.split(".", 1)[1]) if "." in cleaned else 0
    return {
        "text": text,
        "value": value,
        "normalized": normalized,
        "percent": percent,
        "decimals": decimals,
    }


def normalized_display_tolerance(surface: Any) -> Decimal | None:
    parsed = parse_surface(surface)
    if parsed is None:
        return None
    tol = Decimal(1).scaleb(-int(parsed["decimals"])) / Decimal(2)
    return tol / Decimal(100) if parsed["percent"] else tol


def mapped_qa(raw_row: dict[str, Any], annotation: dict[str, Any]) -> dict[str, Any] | None:
    turn = annotation.get("turn_ind")
    split = annotation.get("qa_split")
    qas = {k: v for k, v in raw_row.items() if k == "qa" or k.startswith("qa_")}
    if not isinstance(turn, int) or not isinstance(split, list) or not (0 <= turn < len(split)):
        return None
    key = "qa" if "qa" in raw_row else f"qa_{split[turn]}"
    value = qas.get(key)
    return value if isinstance(value, dict) else None


def infer_unit_hint(raw_row: dict[str, Any]) -> tuple[str, str]:
    """Infer a current-turn display hint without using it as the primary label.

    The rule is frozen before model calls. Explicit current-turn wording wins;
    item-level QA answers are only a fallback for ratio-like turns, never for a
    plain intermediate change/value turn.
    """
    annotation = raw_row["annotation"]
    question = str(annotation["cur_dial"][-1]).lower()
    program = str(annotation["cur_program"])
    # A constant rescaling question asks for a plain rescaled number, even when
    # a later item-level answer happens to carry a percent sign.
    if re.search(r"\bdivided?\s+by\s+(?:100|1000|1000000)\b", question):
        return "plain", "explicit_constant_scaling"
    if re.search(r"\bpercent(?:age)?\b|\bportion\b|\bproportion\b|\bgrowth\s+rate\b|\brate\s+of\b", question):
        return "percent", "explicit_percent_or_proportion"
    # Ratio is intentionally treated as a plain ratio, not as a percent.
    if re.search(r"\bratio\b", question):
        return "plain", "explicit_ratio"
    if re.search(r"\b(?:change|difference|increase|decrease|decline|variation|net change)\b\s+(?:divided?\s+by|over|relative to)\b", question):
        return "percent", "explicit_relative_change"
    if re.search(r"\brepresent\b.*\b(?:relation|total|amount|value)\b", question):
        mapped = mapped_qa(raw_row, annotation)
        if mapped and "%" in str(mapped.get("answer", "")):
            return "percent", "relative_representation_with_percent_qa_fallback"
        return "percent", "relative_representation"
    if re.search(r"\b(?:change|increase|decrease|decline|difference|variation|sum|total)\b", question):
        return "plain", "explicit_plain_change"
    if re.search(r"\b(?:average|amount|number|total|value|expense|price|dollar|shares?|revenue|income|cash|debt|facilit|reserves?|cost|balance|dividend|millions?|billions?|how many)\b", question):
        return "plain", "explicit_plain_quantity"
    mapped = mapped_qa(raw_row, annotation)
    if mapped and "%" in str(mapped.get("answer", "")) and (program.strip().startswith("divide(") or ", divide(" in program):
        return "percent", "ratio_program_percent_qa_fallback"
    # Remaining executable arithmetic turns are plain unless the program is a
    # ratio whose surface cannot be inferred from the current turn.  This final
    # rule is deterministic and all selected rows are audited below.
    return "plain", "default_plain_executable"


def mutate_path(input_obj: dict[str, Any], target: dict[str, Any], new_raw: str) -> dict[str, Any]:
    out = copy.deepcopy(input_obj)
    block = str(target["block"])
    index = int(target["index"])
    if block == "table":
        out[block][index][int(target["column"])] = new_raw
    else:
        out[block][index] = new_raw
    return out


def canonical_input(public_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": "convfinqa-turn-input-v1",
        "dialogue_history": list(public_row["dialogue_history"]),
        "pre_text": list(public_row.get("pre_text", [])),
        "table": [list(row) for row in public_row.get("table", [])],
        "post_text": list(public_row.get("post_text", [])),
    }


def render_table(table: list[list[Any]]) -> str:
    if not table:
        return "(empty)"
    return "\n".join(" | ".join(str(cell) for cell in row) for row in table)


def render_input(public_row: dict[str, Any], world_input: dict[str, Any]) -> str:
    history = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(world_input["dialogue_history"]))
    pre = "\n".join(f"- {x}" for x in world_input["pre_text"]) or "(none)"
    post = "\n".join(f"- {x}" for x in world_input["post_text"]) or "(none)"
    return (
        "Input version: convfinqa-turn-input-v1\n\n"
        "Conversation questions (the last is the current question):\n"
        f"{history}\n\n"
        "Pre-text:\n"
        f"{pre}\n\n"
        "Table:\n"
        f"{render_table(world_input['table'])}\n\n"
        "Post-text:\n"
        f"{post}"
    )


def prompt_record(public_row: dict[str, Any], world_label: str, world_input: dict[str, Any]) -> dict[str, Any]:
    user_content = render_input(public_row, world_input)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_content}]
    prompt_hash = sha256_bytes(canonical_json(messages).encode("utf-8"))
    return {
        "world_id": f"{public_row['id']}::{world_label}",
        "item_id": public_row["id"],
        "world_label": world_label,
        "conversation_id": public_row["conversation_id"],
        "filename": public_row["filename"],
        "turn_index": public_row["turn_index"],
        "fresh_conversation": True,
        "input_sha256": sha256_bytes(canonical_json(world_input).encode("utf-8")),
        "messages": messages,
        "prompt_hash": prompt_hash,
        "prompt_kind": "convfinqa_stage1_qwen_replication",
        "leakage_audit": {
            "messages_contain_only_input_and_fixed_instructions": True,
            "metadata_hits": [],
        },
    }


def expected_records(public_row: dict[str, Any], gold_row: dict[str, Any], raw_row: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    internal = gold_row["internal_gold"]
    target = internal["target"]
    diagnostics = internal["world_diagnostics"]
    base_exe = raw_row["annotation"]["exe_ans"]
    unit_hint, unit_reason = infer_unit_hint(raw_row)
    base_tol = normalized_display_tolerance(base_exe)
    qa = mapped_qa(raw_row, raw_row["annotation"])
    qa_surface = qa.get("answer") if qa else None
    qa_tol = normalized_display_tolerance(qa_surface)
    tolerance = max(x for x in (base_tol, qa_tol) if x is not None) if any(x is not None for x in (base_tol, qa_tol)) else Decimal("0.5")
    base_input = canonical_input(public_row)
    public: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []
    for label in WORLD_ORDER:
        if label == "original":
            world_input = copy.deepcopy(base_input)
            expected = Decimal(str(base_exe))
            k = 0
            source_new_raw = None
            program_result = str(base_exe)
        else:
            k = K_BY_LABEL[label]
            diag = diagnostics["worlds"][str(k)]
            source_new_raw = str(diag["source_new_raw"])
            world_input = mutate_path(base_input, target, source_new_raw)
            expected = Decimal(str(diag["program_result"]))
            program_result = str(diag["program_result"])
        p = prompt_record(public_row, label, world_input)
        public.append({
            "world_id": p["world_id"],
            "item_id": p["item_id"],
            "world_label": label,
            "input_sha256": p["input_sha256"],
            "input": world_input,
            "messages": p["messages"],
            "prompt_hash": p["prompt_hash"],
            "prompt_kind": p["prompt_kind"],
            "fresh_conversation": True,
            "leakage_audit": p["leakage_audit"],
        })
        gold.append({
            "world_id": p["world_id"],
            "item_id": p["item_id"],
            "world_label": label,
            "arm": "original" if label == "original" else "relevant",
            "k": k,
            "conversation_id": public_row["conversation_id"],
            "filename": public_row["filename"],
            "source_group_id": public_row["source_group_id"],
            "turn_index": public_row["turn_index"],
            "current_question": public_row["current_question"],
            "program_ops": list(internal.get("program_ops", [])),
            "unit_hint": unit_hint,
            "unit_hint_reason": unit_reason,
            "unit_hint_is_primary_label": False,
            "expected_normalized_answer": format(expected, "f"),
            "expected_program_result": program_result,
            "expected_tolerance": format(tolerance, "f"),
            "tolerance_rule": "max(half-unit tolerance from current annotation.exe_ans surface, mapped item-level QA answer surface when available), after percent normalization; item-level QA answer never supplies the expected value",
            "current_annotation_exe_ans": base_exe,
            "current_precision_surface": str(base_exe),
            "mapped_qa_answer_surface": qa_surface,
            "mapped_qa_answer_used_for_value": False,
            "input_sha256": p["input_sha256"],
            "prompt_hash": p["prompt_hash"],
            "target_path": [target["block"], int(target["index"]), target.get("column")],
            "source_new_raw": source_new_raw,
            "changed_paths": [] if label == "original" else diagnostics["worlds"][str(k)]["input_diff_paths"],
            "program_sha256": sha256_bytes(str(internal["program"]).encode("utf-8")) if label == "original" else None,
        })
    return public, gold


def audit_and_build() -> None:
    required = [CONTRACT_V11, PUBLIC_DEV, GOLD_DEV, PUBLIC_TRAIN, GOLD_TRAIN, RAW_DEV, RAW_TRAIN]
    missing = [str(x) for x in required if not x.exists()]
    if missing:
        raise SystemExit(f"missing required frozen artifact: {missing}")
    v11 = load_json(CONTRACT_V11)
    if v11.get("status") != "FROZEN_PRE_MODEL_CALL_NO_MODEL_CALLS" or v11.get("model_calls") != 0:
        raise SystemExit("v0.11 contract is not the expected immutable pre-call contract")
    datasets = {
        "dev": (load_jsonl(PUBLIC_DEV), load_jsonl(GOLD_DEV), {x["id"]: x for x in load_json(RAW_DEV)}),
        "train": (load_jsonl(PUBLIC_TRAIN), load_jsonl(GOLD_TRAIN), {x["id"]: x for x in load_json(RAW_TRAIN)}),
    }
    all_prompts: list[dict[str, Any]] = []
    all_public_worlds: list[dict[str, Any]] = []
    all_gold: list[dict[str, Any]] = []
    unit_rows: list[dict[str, Any]] = []
    counts = Counter()
    for split, (public_rows, gold_rows, raw_by_id) in datasets.items():
        if [x["id"] for x in public_rows] != [x["id"] for x in gold_rows]:
            raise SystemExit(f"{split}: public/gold item ordering mismatch")
        gold_by_id = {x["id"]: x for x in gold_rows}
        split_public: list[dict[str, Any]] = []
        split_gold: list[dict[str, Any]] = []
        for public_row in public_rows:
            item_id = public_row["id"]
            raw_row = raw_by_id.get(item_id)
            if raw_row is None:
                raise SystemExit(f"{split}/{item_id}: missing raw current turn")
            unit_hint, unit_reason = infer_unit_hint(raw_row)
            unit_rows.append({
                "split": split,
                "id": item_id,
                "conversation_id": public_row["conversation_id"],
                "filename": public_row["filename"],
                "turn_index": public_row["turn_index"],
                "current_question": public_row["current_question"],
                "current_program": raw_row["annotation"]["cur_program"],
                "current_exe_ans": raw_row["annotation"]["exe_ans"],
                "unit_hint": unit_hint,
                "unit_hint_reason": unit_reason,
                "mapped_qa_answer": (mapped_qa(raw_row, raw_row["annotation"]) or {}).get("answer"),
                "primary_correctness_uses_unit_hint": False,
            })
            counts[f"{split}.unit.{unit_hint}"] += 1
            worlds_public, worlds_gold = expected_records(public_row, gold_by_id[item_id], raw_row)
            split_public.extend(worlds_public)
            split_gold.extend(worlds_gold)
        all_public_worlds.extend(split_public)
        all_gold.extend(split_gold)
        split_prompts = []
        for row in split_public:
            split_prompts.append({k: row[k] for k in ("world_id", "item_id", "world_label", "input_sha256", "messages", "prompt_hash", "prompt_kind", "fresh_conversation", "leakage_audit")})
        write_jsonl(HERE / f"STAGE1_{split.upper()}_WORLD_INPUTS_PUBLIC.jsonl", split_public)
        write_jsonl(HERE / f"STAGE1_{split.upper()}_WORLD_GOLD.jsonl", split_gold)
        write_jsonl(HERE / f"STAGE1_{split.upper()}_PROMPTS.jsonl", split_prompts)
        write_json(HERE / f"STAGE1_{split.upper()}_ANSWER_UNIT_AUDIT.json", {
            "protocol": PROTOCOL,
            "split": split,
            "items": len(public_rows),
            "worlds": len(split_public),
            "unit_hint_counts": dict(Counter(x["unit_hint"] for x in unit_rows if x["split"] == split)),
            "unit_hint_reason_counts": dict(Counter(x["unit_hint_reason"] for x in unit_rows if x["split"] == split)),
            "primary_correctness_is_unit_invariant": True,
            "mapped_item_level_answers_are_not_current_turn_targets": True,
            "model_calls": 0,
        })
    # Inputs are grouped split-wise for fitting later, but Stage 1 DEV execution
    # is the only model-call target.  Keep both files in a single fixed order.
    dev_prompts = load_jsonl(HERE / "STAGE1_DEV_PROMPTS.jsonl")
    dev_gold = load_jsonl(HERE / "STAGE1_DEV_WORLD_GOLD.jsonl")
    if [x["world_id"] for x in dev_prompts] != [x["world_id"] for x in dev_gold]:
        raise SystemExit("DEV prompt/gold world ordering mismatch")
    prompt_spec = {
        "version": "convfinqa-stage1-prompt-v1",
        "system_prompt": SYSTEM_PROMPT,
        "model_visible_fields": ["dialogue_history", "pre_text", "table", "post_text"],
        "dialogue_rule": "Render every question in dialogue_history in order; the last question is the current turn. Do not add answers or programs to the visible prompt.",
        "mutation_rule": "Only the audited target numeric surface is changed in relevant worlds; dialogue history is not mutated.",
        "answer_unit_rule": "Ask the model to preserve the unit implied by the current question; evaluator primary correctness normalizes optional percent signs and does not use item-level QA answer surfaces as current-turn labels.",
        "forbidden_visible_fields": ["program", "exe_ans", "target", "world_diagnostics", "annotation", "qa", "gold", "correctness", "unit_hint"],
        "response_contract": {"format": "json_object", "required_keys": ["answer", "confidence"], "optional_keys": [], "confidence_range": [0, 1]},
    }
    prompt_spec_hash = sha256_bytes(canonical_json(prompt_spec).encode("utf-8"))
    contract = {
        "contract": CONTRACT_NAME,
        "protocol": PROTOCOL,
        "version": "stage1",
        "freeze_date": FREEZE_DATE,
        "status": "FROZEN_PRE_MODEL_CALL",
        "claim_boundary": "Stage-1 Qwen ConvFinQA replication only. No result or PECR effectiveness claim is established until the frozen DEV worlds are executed and independently analyzed.",
        "model_calls": 0,
        "authorization": {"model_calls_authorized": True, "authorization_basis": "user-requested staged confirmatory execution after v0.11 offline audit and this answer-unit addendum freeze"},
        "data": {
            "v11_contract_sha256": sha256_file(CONTRACT_V11),
            "public_dev_sha256": sha256_file(PUBLIC_DEV),
            "gold_dev_sha256": sha256_file(GOLD_DEV),
            "public_train_sha256": sha256_file(PUBLIC_TRAIN),
            "gold_train_sha256": sha256_file(GOLD_TRAIN),
            "raw_dev_sha256": sha256_file(RAW_DEV),
            "raw_train_sha256": sha256_file(RAW_TRAIN),
        },
        "selection": {"primary_dev_items": len(load_jsonl(PUBLIC_DEV)), "primary_train_items": len(load_jsonl(PUBLIC_TRAIN)), "selection_is_inherited_from_frozen_v11": True, "post_selection_outcome_tuning": False},
        "worlds": {"labels": list(WORLD_ORDER), "dev_items": len(load_jsonl(PUBLIC_DEV)), "dev_worlds": len(dev_gold), "train_items": len(load_jsonl(PUBLIC_TRAIN)), "train_worlds": len(load_jsonl(PUBLIC_TRAIN)) * 5, "stage1_model_call_budget": len(dev_gold)},
        "model_identity": {"endpoint": ENDPOINT, "models_endpoint": MODELS_ENDPOINT, "expected_model": EXPECTED_MODEL, "identity_rule": "Verify /v1/models immediately before calls; abort on identity drift; no fallback model."},
        "request_contract": {"temperature": 0.0, "top_p": 1.0, "n": 1, "stream": False, "response_format": {"type": "json_object"}, "retries": 0, "fallback": False, "workers": 1, "fresh_conversation_per_world": True, "timeout_seconds": 180, "max_tokens": 180},
        "prompt_spec": {"spec": prompt_spec, "sha256": prompt_spec_hash},
        "answer_evaluator": {
            "primary": "normalized_numeric_correctness",
            "current_turn_target": "annotation.exe_ans for original; deterministic counterfactual program result for relevant worlds",
            "item_level_qa_answer_used_as_current_target": False,
            "surface_parser": "optional percent sign divides numeric value by 100; currency/commas/parentheses accepted; non-scalar text rejected",
            "tolerance": "max(half displayed unit from current annotation.exe_ans surface, half displayed unit from mapped item-level QA answer surface when available), after percent normalization; fixed before model calls",
            "unit_hint": "question-derived audit/prompt hint only; not a primary correctness gate",
            "unit_hint_rule_version": "convfinqa-current-turn-unit-v1",
        },
        "metrics": {"primary": ["AUROC(S2, original_correct)", "AUROC(full_CEF, original_correct)"], "null": ["global label permutation", "within-operation label permutation"], "confidence_interval": "item bootstrap and filename-cluster bootstrap frozen in analysis script", "stage1_stop_rule": "If Qwen DEV primary S2 and full CEF signals both fail their predeclared gates, do not execute Stage 2/3."},
    }
    write_json(HERE / "CONVFINQA_STAGE1_QWEN_REPLICATION_CONTRACT.json", contract)
    write_jsonl(HERE / "STAGE1_ANSWER_UNIT_AUDIT.jsonl", unit_rows)
    write_json(HERE / "STAGE1_PROMPT_SPEC.json", prompt_spec)
    audit = {
        "protocol": PROTOCOL,
        "status": "PASS",
        "model_calls": 0,
        "frozen_contract_status": v11.get("status"),
        "unit_hint_counts": dict(Counter(x["unit_hint"] for x in unit_rows)),
        "unit_hint_reason_counts": dict(Counter(x["unit_hint_reason"] for x in unit_rows)),
        "primary_normalized_evaluator": True,
        "item_level_qa_answers_not_used_as_current_targets": True,
        "dev_items": len(load_jsonl(PUBLIC_DEV)),
        "dev_worlds": len(dev_gold),
        "train_items": len(load_jsonl(PUBLIC_TRAIN)),
        "train_worlds": len(load_jsonl(PUBLIC_TRAIN)) * 5,
        "prompt_spec_sha256": prompt_spec_hash,
        "contract_sha256": sha256_file(HERE / "CONVFINQA_STAGE1_QWEN_REPLICATION_CONTRACT.json"),
        "failures": [],
    }
    write_json(HERE / "STAGE1_STATIC_FREEZE_AUDIT.json", audit)
    (HERE / "STAGE1_FREEZE_STATUS.md").write_text(
        "# ConvFinQA Stage 1 freeze\n\n"
        "Status: **FROZEN_PRE_MODEL_CALL**\n\n"
        f"- Qwen DEV worlds: **{len(dev_gold)}** ({len(load_jsonl(PUBLIC_DEV))} items × 5).\n"
        f"- Qwen TRAIN worlds prepared for Stage 2: **{len(load_jsonl(PUBLIC_TRAIN))*5}**.\n"
        "- Primary evaluator: normalized current-turn executable answer; item-level QA answers are not current-turn labels.\n"
        "- Model calls made by builder: **0**.\n"
        "- v0.11 audit/contract modified: **false**.\n",
        encoding="utf-8",
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    audit_and_build()
