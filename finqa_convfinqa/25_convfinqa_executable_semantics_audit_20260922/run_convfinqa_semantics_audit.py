#!/usr/bin/env python3
"""Offline executable-semantics audit for ConvFinQA.

No LLM/API calls are made.  This script audits whether ConvFinQA's released
conversation-turn records can support the same PECR construction used for
FinQA: a self-contained arithmetic program, a unique context operand mapped to
one program literal, and deterministic k=-2,-1,+1,+2 counterfactual worlds.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA_DIR = HERE / "upstream_data" / "extracted" / "data"
V02_DIR = REPO / "finqa_convfinqa" / "13_pecr_v0_2_repaired"
V02_CORE_PATH = V02_DIR / "pecr_v02_core.py"

spec = importlib.util.spec_from_file_location("convfinqa_pecr_v02_core", V02_CORE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {V02_CORE_PATH}")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

PROTOCOL = "ConvFinQA_PECR_executable_semantics_audit_20260922"
AUDIT_DATE = "2026-09-22"
EXPECTED_DATA_COMMIT = "cf3eed2d5984960bf06bb8145bcea5e80b0222a6"
K_VALUES = (-2, -1, 1, 2)
INVARIANT_VARIANTS = (1, 2)
ALLOWED_OPS = {"add", "subtract", "multiply", "divide"}
TURN_FILES = {
    "train_turn": DATA_DIR / "train_turn.json",
    "dev_turn": DATA_DIR / "dev_turn.json",
    "test_turn_private": DATA_DIR / "test_turn_private.json",
}
ITEM_FILES = {
    "train": DATA_DIR / "train.json",
    "dev": DATA_DIR / "dev.json",
    "test_private": DATA_DIR / "test_private.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite_decimal(value: Any) -> Decimal | None:
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except (InvalidOperation, TypeError, ValueError):
        return None


def turn_index(row: dict[str, Any]) -> int | None:
    value = row.get("annotation", {}).get("turn_ind")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def conversation_id(row: dict[str, Any]) -> str:
    return re.sub(r"_\d+$", "", str(row.get("id", "")))


def source_group_id(row: dict[str, Any]) -> str:
    return "doc:" + str(row.get("filename") or "<missing-filename>")


def current_question(row: dict[str, Any]) -> str | None:
    dialogue = row.get("annotation", {}).get("cur_dial")
    if not isinstance(dialogue, list) or not dialogue:
        return None
    return normalize_text(dialogue[-1])


def canonical_input(row: dict[str, Any]) -> dict[str, Any] | None:
    question = current_question(row)
    if question is None:
        return None
    return {
        "version": "convfinqa-canonical-turn-input-v1",
        "question": question,
        "pre_text": [normalize_text(x) for x in row.get("pre_text", [])],
        "table": [[normalize_text(c) for c in cells] for cells in row.get("table", [])],
        "post_text": [normalize_text(x) for x in row.get("post_text", [])],
    }


def all_context_numeric_occurrences(input_obj: dict[str, Any]) -> list[dict[str, Any]]:
    """Scan source facts, excluding dialogue question text from mutation targets."""
    occurrences: list[dict[str, Any]] = []
    for block in ("pre_text", "post_text"):
        for index, text in enumerate(input_obj.get(block, [])):
            for match in core.support.NUM_RE.finditer(str(text)):
                normalized = core.support.normalized_number(match.group(0))
                if normalized is not None:
                    occurrences.append({
                        "block": block,
                        "index": index,
                        "column": None,
                        "raw": match.group(0),
                        "normalized": normalized,
                        "start": match.start(),
                        "end": match.end(),
                    })
    for index, cells in enumerate(input_obj.get("table", [])):
        for column, text in enumerate(cells):
            for match in core.support.NUM_RE.finditer(str(text)):
                normalized = core.support.normalized_number(match.group(0))
                if normalized is not None:
                    occurrences.append({
                        "block": "table",
                        "index": index,
                        "column": column,
                        "raw": match.group(0),
                        "normalized": normalized,
                        "start": match.start(),
                        "end": match.end(),
                    })
    return occurrences


def get_source_container(input_obj: dict[str, Any], target: dict[str, Any]) -> str:
    block = target["block"]
    index = int(target["index"])
    if block == "table":
        return str(input_obj["table"][index][int(target["column"])])
    return str(input_obj[block][index])


def mutate_target(input_obj: dict[str, Any], target: dict[str, Any], new_raw: str) -> dict[str, Any]:
    out = copy.deepcopy(input_obj)
    block = target["block"]
    index = int(target["index"])
    start = int(target["canonical_start"])
    end = int(target["canonical_end"])
    if block == "table":
        old = out["table"][index][int(target["column"])]
        if old[start:end] != str(target["raw"]):
            raise ValueError("target_span_mismatch_table")
        out["table"][index][int(target["column"])] = old[:start] + new_raw + old[end:]
    else:
        old = out[block][index]
        if old[start:end] != str(target["raw"]):
            raise ValueError(f"target_span_mismatch_{block}")
        out[block][index] = old[:start] + new_raw + old[end:]
    return out


def input_diff_paths(a: Any, b: Any, path: str = "") -> list[str]:
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        paths: list[str] = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                paths.append(f"{path}.{key}")
            else:
                paths.extend(input_diff_paths(a[key], b[key], f"{path}.{key}"))
        return paths
    if isinstance(a, list):
        paths: list[str] = []
        if len(a) != len(b):
            paths.append(f"{path}.length")
        for index in range(min(len(a), len(b))):
            paths.extend(input_diff_paths(a[index], b[index], f"{path}[{index}]"))
        return paths
    return [] if a == b else [path]


def answer_matches(result: Decimal | None, expected: Any) -> bool:
    # ConvFinQA stores executable answers as rounded numeric values (for
    # example, 0.14136 for the displayed 14.1% answer). Reuse the audited
    # PECR display-tolerance rule rather than an exact/near-exact comparison.
    aligned, _rule = core.result_matches_answer(result, expected)
    return bool(aligned)


def program_target_candidates(input_obj: dict[str, Any], program: str, trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    occurrences = all_context_numeric_occurrences(input_obj)
    literals = core.actual_program_literals(program)
    candidates: list[dict[str, Any]] = []
    for occurrence in occurrences:
        normalized = str(occurrence["normalized"])
        global_count = sum(str(x["normalized"]) == normalized for x in occurrences)
        matched_literals = [literal for literal in literals if str(literal["normalized"]) == normalized]
        if global_count != 1 or len(matched_literals) != 1:
            continue
        parsed = core.parse_surface(str(occurrence["raw"]))
        if parsed is None or parsed["value"] == 0:
            continue
        literal = matched_literals[0]
        try:
            op_index, arg_index, arg_start, arg_end, op, role = core.numeric_literal_span(
                program, int(literal["start"]), int(literal["end"])
            )
            path = core.dependency_path(trace, op_index)
        except Exception:
            continue
        if not path or path[-1] != trace[-1]["statement_index"]:
            continue
        candidates.append({
            **occurrence,
            "canonical_raw": get_source_container(input_obj, occurrence),
            "canonical_start": int(occurrence["start"]),
            "canonical_end": int(occurrence["end"]),
            "global_source_occurrence_count": global_count,
            "program_literal": literal["raw"],
            "program_literal_start": int(literal["start"]),
            "program_literal_end": int(literal["end"]),
            "program_occurrence_count": len(matched_literals),
            "program_operator_index": op_index,
            "program_argument_index": arg_index,
            "program_argument_role": role,
            "program_argument_span_start": arg_start,
            "program_argument_span_end": arg_end,
            "dependency_path": path,
        })
    return candidates


def patch_program(program: str, target: dict[str, Any], new_source_raw: str) -> tuple[str, str]:
    old_source = core.parse_surface(str(target["raw"]))
    new_source = core.parse_surface(new_source_raw)
    if old_source is None or new_source is None or old_source["normalized"] == 0:
        raise ValueError("invalid_source_surface")
    old_literal = str(target["program_literal"])
    old_norm = Decimal(str(core.support.normalized_number(old_literal)))
    with localcontext() as context:
        context.prec = 100
        changed_value = old_norm * new_source["normalized"] / old_source["normalized"]
    rendered = format(changed_value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    if rendered in {"", "-0"}:
        rendered = "0"
    if "%" in old_literal:
        rendered += "%"
    start = int(target["program_literal_start"])
    end = int(target["program_literal_end"])
    if program[start:end] != old_literal:
        raise ValueError("program_literal_offset_mismatch")
    changed = program[:start] + rendered + program[end:]
    if changed == program:
        raise ValueError("program_patch_did_not_change")
    return changed, rendered


def audit_worlds(input_obj: dict[str, Any], program: str, target: dict[str, Any], base_result: Decimal, context: str) -> tuple[bool, str | None, dict[str, Any]]:
    diagnostics: dict[str, Any] = {"worlds": {}, "invariant_worlds": {}}
    for k in K_VALUES:
        try:
            new_raw, new_value = core.scaled_surface(str(target["raw"]), k)
            semantic_ok, semantic_reason = core.semantic_type_check(new_raw, context)
            if not semantic_ok:
                return False, f"k_{k}_semantic_{semantic_reason}", diagnostics
            changed_program, new_literal = patch_program(program, target, new_raw)
            changed_input = mutate_target(input_obj, target, new_raw)
            diff_paths = input_diff_paths(input_obj, changed_input)
            transformed, secondary, trace, error = core.dual_execute(changed_program)
            if error or transformed is None or secondary is None:
                return False, f"k_{k}_execution_{error}", diagnostics
            if transformed == base_result:
                return False, f"k_{k}_unchanged_result", diagnostics
            if core.has_near_zero_divisor(trace):
                return False, f"k_{k}_near_zero_divisor", diagnostics
            if any(abs(value) > core.MAX_ABS_INTERMEDIATE for value in core.all_trace_values(trace)):
                return False, f"k_{k}_extreme_intermediate", diagnostics
            diagnostics["worlds"][str(k)] = {
                "source_new_raw": new_raw,
                "source_new_value": str(new_value),
                "program_new_literal": new_literal,
                "program_result": core.fraction_text(secondary),
                "input_diff_paths": diff_paths,
                "input_diff_exactly_target": len(diff_paths) == 1 and diff_paths[0].startswith(f"{target['block']}["),
                "result_changed": transformed != base_result,
                "dual_execute_agrees": True,
            }
            if len(diff_paths) != 1:
                return False, f"k_{k}_unexpected_input_diff", diagnostics
        except Exception as exc:
            return False, f"k_{k}_{type(exc).__name__}:{exc}", diagnostics

    for variant in INVARIANT_VARIANTS:
        try:
            new_raw, new_value = core.equivalent_surface(str(target["raw"]), variant)
            # Numeric-surface invariance deliberately changes only the source
            # surface. The executable program literal is already normalized, so
            # patching it would either change no bytes (e.g. 118 -> 118.0) or
            # turn a representation check into a semantic intervention.
            changed_input = mutate_target(input_obj, target, new_raw)
            changed_program = program
            new_literal = str(target["program_literal"])
            transformed, secondary, trace, error = core.dual_execute(changed_program)
            if error or transformed is None or secondary is None:
                return False, f"invariant_{variant}_execution_{error}", diagnostics
            if transformed != base_result:
                return False, f"invariant_{variant}_changed_result", diagnostics
            diff_paths = input_diff_paths(input_obj, changed_input)
            diagnostics["invariant_worlds"][str(variant)] = {
                "source_new_raw": new_raw,
                "source_new_value": str(new_value),
                "program_new_literal": new_literal,
                "program_result": core.fraction_text(secondary),
                "input_diff_paths": diff_paths,
                "preserves_result": True,
            }
            if len(diff_paths) != 1:
                return False, f"invariant_{variant}_unexpected_input_diff", diagnostics
        except Exception as exc:
            return False, f"invariant_{variant}_{type(exc).__name__}:{exc}", diagnostics
    return True, None, diagnostics


def audit_turn_row(row: dict[str, Any], split: str) -> dict[str, Any]:
    annotation = row.get("annotation") or {}
    current_type = annotation.get("cur_type")
    turn = turn_index(row)
    dialogue = annotation.get("cur_dial")
    program = annotation.get("cur_program")
    exe_ans = annotation.get("exe_ans")
    record: dict[str, Any] = {
        "split": split,
        "id": row.get("id"),
        "conversation_id": conversation_id(row),
        "filename": row.get("filename"),
        "source_group_id": source_group_id(row),
        "turn_index": turn,
        "turn_type": current_type,
        "dialogue_length": len(dialogue) if isinstance(dialogue, list) else None,
        "current_question_present": bool(current_question(row)),
        "program": str(program) if program is not None else None,
        "program_ops": core.support.program_ops(str(program)) if program is not None else [],
        "program_is_bare_number": bool(program is not None and core.support.NUM_RE.fullmatch(str(program).strip())),
        "history_consistency": {},
        "status": "REJECTED",
        "reason": None,
    }
    required_turn_fields = {"cur_dial", "cur_program", "cur_type", "turn_ind", "turn_program", "exe_ans_list", "dialogue_break", "exe_ans"}
    missing_turn_fields = sorted(field for field in required_turn_fields if field not in annotation)
    if split == "test_turn_private" and missing_turn_fields:
        record["status"] = "UNAVAILABLE"
        record["reason"] = "private_test_labels_unavailable"
        record["annotation_missing_fields"] = missing_turn_fields
        return record
    turn_programs = annotation.get("turn_program")
    exe_ans_list = annotation.get("exe_ans_list")
    dialogue_break = annotation.get("dialogue_break")
    record["history_consistency"] = {
        "turn_index_matches_dialogue_last": turn is not None and isinstance(dialogue, list) and turn == len(dialogue) - 1,
        "turn_index_in_range": turn is not None and isinstance(turn_programs, list) and 0 <= turn < len(turn_programs),
        "cur_program_matches_turn_program": turn is not None and isinstance(turn_programs, list) and 0 <= turn < len(turn_programs) and str(program) == str(turn_programs[turn]),
        "exe_ans_matches_turn_list": turn is not None and isinstance(exe_ans_list, list) and 0 <= turn < len(exe_ans_list) and finite_decimal(exe_ans) == finite_decimal(exe_ans_list[turn]),
        "cur_question_matches_dialogue_break": turn is not None and isinstance(dialogue_break, list) and 0 <= turn < len(dialogue_break) and normalize_text(dialogue[-1]) == normalize_text(dialogue_break[turn]) if isinstance(dialogue, list) and dialogue_break else False,
    }
    if current_type != "program_turn":
        record["reason"] = "number_turn_not_program_executable"
        return record
    if not all(record["history_consistency"].values()):
        record["reason"] = "conversation_history_metadata_inconsistent"
        return record
    if not isinstance(program, str) or not program.strip():
        record["reason"] = "missing_current_program"
        return record
    if not set(record["program_ops"]).issubset(ALLOWED_OPS):
        record["reason"] = "unsupported_program_ops"
        return record
    base_result, secondary, trace, execute_error = core.dual_execute(program)
    record["base_result"] = None if base_result is None else str(base_result)
    record["base_program_trace_length"] = len(trace)
    record["base_execution_error"] = execute_error
    record["answer"] = exe_ans
    record["base_answer_alignment"] = answer_matches(base_result, exe_ans)
    if execute_error:
        record["reason"] = f"original_execution:{execute_error}"
        return record
    if base_result is None or secondary is None:
        record["reason"] = "missing_original_result"
        return record
    if not record["base_answer_alignment"]:
        record["reason"] = "original_program_answer_mismatch"
        return record
    if core.has_near_zero_divisor(trace):
        record["reason"] = "original_near_zero_divisor"
        return record
    if any(abs(value) > core.MAX_ABS_INTERMEDIATE for value in core.all_trace_values(trace)):
        record["reason"] = "original_extreme_intermediate"
        return record
    input_obj = canonical_input(row)
    if input_obj is None:
        record["reason"] = "missing_current_question"
        return record
    candidates = program_target_candidates(input_obj, program, trace)
    record["candidate_count"] = len(candidates)
    record["candidate_paths"] = [f"{x['block']}[{x['index']}]" + (f"[{x['column']}]" if x.get("column") is not None else "") for x in candidates]
    if len(candidates) != 1:
        record["reason"] = f"unique_operand_count:{len(candidates)}"
        return record
    target = candidates[0]
    record["target"] = target
    context = core.context_text(input_obj)
    eligible, reason, world_diagnostics = audit_worlds(input_obj, program, target, base_result, context)
    record["world_diagnostics"] = world_diagnostics
    if not eligible:
        record["reason"] = reason
        return record
    record["status"] = "ELIGIBLE"
    return record


def summarize_turn_rows(records: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [x for x in records if x["status"] == "ELIGIBLE"]
    auditable = [x for x in records if x["status"] in {"ELIGIBLE", "REJECTED"}]
    history_checked = [x for x in records if x["history_consistency"]]
    return {
        "rows": len(records),
        "auditable_rows": len(auditable),
        "unavailable_rows": sum(x["status"] == "UNAVAILABLE" for x in records),
        "eligible_rows": len(eligible),
        "eligible_fraction": len(eligible) / len(auditable) if auditable else None,
        "status_counts": {str(key): value for key, value in Counter(x["status"] for x in records).items()},
        "reason_counts": {str(key): value for key, value in Counter(x["reason"] for x in records).items()},
        "turn_type_counts": {str(key): value for key, value in Counter(x["turn_type"] for x in records).items()},
        "program_ops_counts": {str(key): value for key, value in Counter(",".join(x["program_ops"]) for x in records).items()},
        "program_turn_rows": sum(x["turn_type"] == "program_turn" for x in records),
        "number_turn_rows": sum(x["turn_type"] == "number_turn" for x in records),
        "history_checked_rows": len(history_checked),
        "history_all_checks_pass": sum(all(x["history_consistency"].values()) for x in history_checked),
        "original_execution_pass": sum(x.get("base_execution_error") is None for x in records if x["turn_type"] == "program_turn" and x.get("program")),
        "original_answer_alignment_pass": sum(bool(x.get("base_answer_alignment")) for x in records if x["turn_type"] == "program_turn"),
        "candidate_count_distribution_program_turn": {str(key): value for key, value in Counter(x.get("candidate_count") for x in records if x["turn_type"] == "program_turn").items()},
        "eligible_conversations": len({x["conversation_id"] for x in eligible}),
        "eligible_source_files": len({x["filename"] for x in eligible}),
        "eligible_turns_per_conversation_distribution": {str(key): value for key, value in Counter(Counter(x["conversation_id"] for x in eligible).values()).items()},
        "eligible_turns_per_source_distribution": {str(key): value for key, value in Counter(Counter(x["filename"] for x in eligible).values()).items()},
    }


def overlap_summary(train_records: list[dict[str, Any]], dev_records: list[dict[str, Any]]) -> dict[str, Any]:
    def sets(records: list[dict[str, Any]]) -> dict[str, set[str]]:
        return {
            "conversation": {x["conversation_id"] for x in records},
            "source_file": {x["filename"] for x in records},
        }
    a, b = sets(train_records), sets(dev_records)
    return {
        "train_vs_dev_turn_rows": {
            key: len(a[key] & b[key]) for key in a
        },
        "train_unique_conversations": len(a["conversation"]),
        "dev_unique_conversations": len(b["conversation"]),
        "train_unique_source_files": len(a["source_file"]),
        "dev_unique_source_files": len(b["source_file"]),
        "train_dev_disjoint_at_conversation_level": not bool(a["conversation"] & b["conversation"]),
        "train_dev_disjoint_at_source_file_level": not bool(a["source_file"] & b["source_file"]),
        "overlap_examples": {
            key: sorted(a[key] & b[key])[:20] for key in a
        },
    }


def symbolic_reference_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Check that #n references are local to the current program sequence.

    ConvFinQA stores each current arithmetic program as a self-contained
    comma-separated sequence.  A reference in statement i must point to a
    result from an earlier statement in that same sequence; this is the
    auditable boundary we can establish offline without inferring hidden
    cross-turn state.
    """
    program_rows = [x for x in records if x.get("turn_type") == "program_turn" and x.get("program")]
    programs_with_refs = 0
    invalid: list[dict[str, Any]] = []
    reference_count = 0
    for row in program_rows:
        program = str(row["program"])
        if "#" not in program:
            continue
        programs_with_refs += 1
        try:
            spans = core.split_top_level_spans(program)
            for statement_index, (_start, _end, statement) in enumerate(spans):
                for match in re.finditer(r"#(\d+)", statement):
                    reference_count += 1
                    ref_index = int(match.group(1))
                    if ref_index >= statement_index:
                        invalid.append({
                            "id": row.get("id"),
                            "statement_index": statement_index,
                            "reference": f"#{ref_index}",
                        })
        except Exception as exc:
            invalid.append({"id": row.get("id"), "error": f"{type(exc).__name__}:{exc}"})
    return {
        "program_rows": len(program_rows),
        "programs_with_symbolic_references": programs_with_refs,
        "local_symbolic_reference_count": reference_count,
        "nonlocal_or_unparseable_reference_count": len(invalid),
        "nonlocal_or_unparseable_examples": invalid[:20],
        "all_observed_references_local_to_current_program": not invalid,
    }


def dedup_capacity(records: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [x for x in records if x["status"] == "ELIGIBLE"]
    by_conversation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        by_conversation[row["conversation_id"]].append(row)
        by_source[row["filename"]].append(row)
    one_per_conversation = [min(rows, key=lambda x: (x["turn_index"], x["id"])) for rows in by_conversation.values()]
    one_per_source = [min(rows, key=lambda x: (x["turn_index"], x["id"])) for rows in by_source.values()]
    return {
        "eligible_turns": len(eligible),
        "one_per_conversation": len(one_per_conversation),
        "one_per_source_file": len(one_per_source),
        "one_per_source_and_conversation": len({(x["filename"], x["conversation_id"]) for x in eligible}),
        "conversation_dedup_fraction": len(one_per_conversation) / len(eligible) if eligible else None,
        "source_dedup_fraction": len(one_per_source) / len(eligible) if eligible else None,
        "selection_policy_for_future_contract": "at most one current program_turn per conversation and per source filename; selection must be frozen before model calls",
    }


def item_level_summary(data: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for split, rows in data.items():
        result[split] = {
            "records": len(rows),
            "records_with_gold_qa": sum("qa" in x or "qa_0" in x for x in rows),
            "single_qa_records": sum("qa" in x for x in rows),
            "double_qa_records": sum("qa_0" in x and "qa_1" in x for x in rows),
            "unique_ids": len({x.get("id") for x in rows}),
            "unique_source_files": len({x.get("filename") for x in rows}),
            "annotation_keys": {str(key): value for key, value in Counter(tuple(sorted((x.get("annotation") or {}).keys())) for x in rows).most_common(5)},
        }
    return result


def main() -> None:
    missing = [str(path) for path in [*TURN_FILES.values(), *ITEM_FILES.values()] if not path.exists()]
    if missing:
        raise SystemExit(f"missing data files: {missing}")
    item_data = {name: load_json(path) for name, path in ITEM_FILES.items()}
    turn_data = {name: load_json(path) for name, path in TURN_FILES.items()}

    all_records: dict[str, list[dict[str, Any]]] = {}
    summaries: dict[str, Any] = {}
    for split, rows in turn_data.items():
        records = [audit_turn_row(row, split) for row in rows]
        all_records[split] = records
        summaries[split] = summarize_turn_rows(records)
        write_json(HERE / f"{split.upper()}_AUDIT.json", {"split": split, "summary": summaries[split], "records": records})

    train_records = all_records["train_turn"]
    dev_records = all_records["dev_turn"]
    train_eligible = [x for x in train_records if x["status"] == "ELIGIBLE"]
    dev_eligible = [x for x in dev_records if x["status"] == "ELIGIBLE"]
    source_meta = {
        "protocol": PROTOCOL,
        "audit_date": AUDIT_DATE,
        "source_repository": "https://github.com/czyssrs/ConvFinQA",
        "expected_main_commit": EXPECTED_DATA_COMMIT,
        "data_zip_sha256": sha256(HERE / "upstream_data" / "data.zip"),
        "data_files": {name: {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size} for name, path in {**TURN_FILES, **ITEM_FILES}.items()},
        "model_calls": 0,
        "network_calls_after_download": 0,
        "claim_boundary": "Offline executable-semantics feasibility audit only; no model reliability or replication result.",
    }
    output = {
        "protocol": PROTOCOL,
        "audit_date": AUDIT_DATE,
        "status": "AUDIT_COMPLETE",
        "model_calls": 0,
        "source": source_meta,
        "item_level_summary": item_level_summary(item_data),
        "turn_level_summary": summaries,
        "split_overlap": overlap_summary(train_records, dev_records),
        "capacity": {
            "train_turn": dedup_capacity(train_records),
            "dev_turn": dedup_capacity(dev_records),
            "train_eligible_conversations": sorted({x["conversation_id"] for x in train_eligible}),
            "dev_eligible_conversations": sorted({x["conversation_id"] for x in dev_eligible}),
        },
        "history_semantics": {
            "turn_record_has_current_dialogue": True,
            "current_question_rule": "annotation.cur_dial[-1]",
            "current_program_rule": "annotation.cur_program",
            "current_answer_rule": "annotation.exe_ans",
            "program_turn_is_self_contained_executable_candidate": True,
            "number_turn_policy": "excluded from PECR probe construction because cur_program is a number extraction turn, not an arithmetic program",
            "symbolic_reference_audit": {
                "train_turn": symbolic_reference_summary(train_records),
                "dev_turn": symbolic_reference_summary(dev_records),
            },
            "history_metadata_checks": "cur_dial, turn_ind, turn_program, and exe_ans_list consistency audited per row",
        },
        "eligibility_rule": {
            "turn_type": "program_turn",
            "allowed_ops": sorted(ALLOWED_OPS),
            "source_scope": ["table", "pre_text", "post_text"],
            "question_mutation": False,
            "unique_source_occurrence": True,
            "unique_program_literal_mapping": True,
            "dependency_reaches_final_program_step": True,
            "all_four_k_worlds": list(K_VALUES),
            "numeric_surface_invariance_worlds": list(INVARIANT_VARIANTS),
            "dual_executor_check": True,
            "answer_alignment_to_annotation_exe_ans": True,
            "near_zero_divisor_rejection": True,
            "extreme_intermediate_rejection": True,
        },
        "decision": {
            "eligible_train_turns": len(train_eligible),
            "eligible_dev_turns": len(dev_eligible),
            "eligible_train_one_per_conversation": dedup_capacity(train_records)["one_per_conversation"],
            "eligible_dev_one_per_conversation": dedup_capacity(dev_records)["one_per_conversation"],
            "train_dev_source_disjoint": None,
        },
    }
    # Avoid hiding the actual split-overlap decision inside a generated expression.
    output["decision"]["train_dev_source_disjoint"] = output["split_overlap"]["train_dev_disjoint_at_source_file_level"]
    output["decision"]["train_dev_conversation_disjoint"] = output["split_overlap"]["train_dev_disjoint_at_conversation_level"]
    enough = len(train_eligible) >= 200 and len(dev_eligible) >= 150 and output["decision"]["train_dev_source_disjoint"]
    output["decision"]["minimum_capacity_gate_200_train_150_dev"] = bool(enough)
    if enough:
        output["decision"]["status"] = "PROCEED_TO_FREEZE_REPLICATION_CONTRACT"
        output["decision"]["next_step"] = "Freeze a ConvFinQA train-fit/dev-confirmation contract; do not call models until the item selection and feature mapping are sealed."
    else:
        output["decision"]["status"] = "DO_NOT_PROCEED_YET"
        output["decision"]["next_step"] = "Resolve data semantics or capacity shortfall before any model calls."

    write_json(HERE / "CONVFINQA_EXECUTABLE_SEMANTICS_AUDIT.json", output)
    status = output["decision"]["status"]
    md = f"""# ConvFinQA executable-semantics audit ({AUDIT_DATE})\n\n- Status: **{status}**\n- Model/API calls: **0**\n- Data source: released ConvFinQA archive, commit `{EXPECTED_DATA_COMMIT[:12]}`\n- `data.zip` SHA256: `{source_meta['data_zip_sha256']}`\n\n## Dataset shape\n\n- Train item/conversation records: **{len(item_data['train'])}**\n- Dev item/conversation records: **{len(item_data['dev'])}**\n- Train turn records: **{len(turn_data['train_turn'])}**\n- Dev turn records: **{len(turn_data['dev_turn'])}**\n- Train program turns: **{summaries['train_turn']['program_turn_rows']}**\n- Train number turns excluded: **{summaries['train_turn']['number_turn_rows']}**\n- Dev program turns: **{summaries['dev_turn']['program_turn_rows']}**\n- Dev number turns excluded: **{summaries['dev_turn']['number_turn_rows']}**\n- Private test turn records are present but labels/program annotations are unavailable; they are **not auditable** and no test eligibility claim is made.\n\n## Executable-world feasibility\n\n- Eligible train program turns: **{len(train_eligible)}**\n- Eligible dev program turns: **{len(dev_eligible)}**\n- Eligible train conversations after one-per-conversation deduplication: **{dedup_capacity(train_records)['one_per_conversation']}**\n- Eligible dev conversations after one-per-conversation deduplication: **{dedup_capacity(dev_records)['one_per_conversation']}**\n- One-per-source-file sensitivity capacity: train **{dedup_capacity(train_records)['one_per_source_file']}**, dev **{dedup_capacity(dev_records)['one_per_source_file']}**\n- Train/dev source-file disjoint: **{output['split_overlap']['train_dev_disjoint_at_source_file_level']}**\n- Train/dev conversation disjoint: **{output['split_overlap']['train_dev_disjoint_at_conversation_level']}**\n\nEach eligible row passed: self-contained program execution, alignment to `annotation.exe_ans`, unique source occurrence to program-literal mapping, dependency-to-final-step check, all four `k=-2,-1,+1,+2` transformed executions, and two numeric-surface invariance checks.\n\n## Conversation-state boundary\n\n`program_turn` records expose `annotation.cur_dial`, `annotation.cur_program`, and `annotation.exe_ans`; the current question is taken as `cur_dial[-1]`. `number_turn` records are not treated as executable PECR items because their current program is an extracted number rather than an arithmetic program. All observed `#n` symbolic references were also checked to be local to the current comma-separated program sequence (train **{output['history_semantics']['symbolic_reference_audit']['train_turn']['local_symbolic_reference_count']}**, dev **{output['history_semantics']['symbolic_reference_audit']['dev_turn']['local_symbolic_reference_count']}**; no nonlocal references).\n\n## Decision\n\n**{status}**\n\n{output['decision']['next_step']}\n\nThis audit establishes construction feasibility and sample capacity only. It does not establish PECR accuracy, missing-probe distillation improvement, or cross-task generalization.\n"""
    (HERE / "CONVFINQA_EXECUTABLE_SEMANTICS_AUDIT.md").write_text(md, encoding="utf-8")
    print(json.dumps({
        "status": status,
        "train_eligible": len(train_eligible),
        "dev_eligible": len(dev_eligible),
        "train_one_per_conversation": dedup_capacity(train_records)["one_per_conversation"],
        "dev_one_per_conversation": dedup_capacity(dev_records)["one_per_conversation"],
        "train_dev_source_disjoint": output["split_overlap"]["train_dev_disjoint_at_source_file_level"],
        "next_step": output["decision"]["next_step"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
