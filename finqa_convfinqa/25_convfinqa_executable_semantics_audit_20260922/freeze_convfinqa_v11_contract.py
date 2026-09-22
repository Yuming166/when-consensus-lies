#!/usr/bin/env python3
"""Freeze the offline ConvFinQA v0.11 replication/confirmation contract.

This script performs no model or network calls.  It consumes the completed
executable-semantics audit and creates deterministic one-per-conversation
primary manifests plus one-per-source-file sensitivity manifests.  It does
not authorize model calls; a later runner must verify endpoint identities and
use this frozen package unchanged.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "upstream_data" / "extracted" / "data"
AUDIT_PATH = HERE / "CONVFINQA_EXECUTABLE_SEMANTICS_AUDIT.json"
TRAIN_AUDIT_PATH = HERE / "TRAIN_TURN_AUDIT.json"
DEV_AUDIT_PATH = HERE / "DEV_TURN_AUDIT.json"
TRAIN_DATA_PATH = DATA_DIR / "train_turn.json"
DEV_DATA_PATH = DATA_DIR / "dev_turn.json"
DATA_ZIP_PATH = HERE / "upstream_data" / "data.zip"

PROTOCOL = "ConvFinQA_PECR_v0.11_prospective_replication_and_missing_probe_confirmation"
CONTRACT = "PECR_V0_11_CONVFINQA_FROZEN_REPLICATION_CONTRACT"
FREEZE_DATE = "2026-09-22"
DATA_COMMIT = "cf3eed2d5984960bf06bb8145bcea5e80b0222a6"
DATA_ZIP_SHA256 = "d764271fae60d81b62e6d58dfc481807ebc8cfbcd633811241723c4a2101072a"
SELECTION_RULE = "sort eligible rows by (conversation_id, turn_index, id); keep the first row per conversation_id"
SOURCE_SELECTION_RULE = "sort eligible rows by (filename, turn_index, id); keep the first row per filename"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n" for row in rows), encoding="utf-8")


def selected_public_record(audit_record: dict[str, Any], raw_row: dict[str, Any], policy: str) -> dict[str, Any]:
    annotation = raw_row.get("annotation") or {}
    target = audit_record.get("target")
    if not isinstance(target, dict):
        raise ValueError(f"missing target for eligible row {audit_record.get('id')}")
    return {
        "selection_policy": policy,
        "id": audit_record["id"],
        "conversation_id": audit_record["conversation_id"],
        "filename": audit_record["filename"],
        "source_group_id": audit_record["source_group_id"],
        "turn_index": audit_record["turn_index"],
        "turn_type": audit_record["turn_type"],
        "dialogue_history": list(annotation["cur_dial"]),
        "current_question": annotation["cur_dial"][-1],
        "pre_text": list(raw_row.get("pre_text", [])),
        "table": [list(row) for row in raw_row.get("table", [])],
        "post_text": list(raw_row.get("post_text", [])),
        "internal_gold": {
            "program": annotation["cur_program"],
            "exe_ans": annotation["exe_ans"],
            "target": target,
            "program_ops": audit_record.get("program_ops", []),
            "world_diagnostics": audit_record.get("world_diagnostics", {}),
        },
    }


def select(records: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    eligible = [r for r in records if r.get("status") == "ELIGIBLE"]
    ordered = sorted(eligible, key=lambda r: (str(r[key]), int(r.get("turn_index") or 0), str(r.get("id"))))
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in ordered:
        value = str(record[key])
        if value in seen:
            continue
        seen.add(value)
        out.append(record)
    return out


def public_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key != "internal_gold"}


def gold_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "conversation_id": row["conversation_id"],
        "filename": row["filename"],
        "source_group_id": row["source_group_id"],
        "turn_index": row["turn_index"],
        "internal_gold": row["internal_gold"],
    }


def main() -> None:
    required = [AUDIT_PATH, TRAIN_AUDIT_PATH, DEV_AUDIT_PATH, TRAIN_DATA_PATH, DEV_DATA_PATH, DATA_ZIP_PATH]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit(f"missing required audit/data artifact: {missing}")
    audit = load_json(AUDIT_PATH)
    train_audit = load_json(TRAIN_AUDIT_PATH)
    dev_audit = load_json(DEV_AUDIT_PATH)
    train_raw = {row["id"]: row for row in load_json(TRAIN_DATA_PATH)}
    dev_raw = {row["id"]: row for row in load_json(DEV_DATA_PATH)}
    train_records = train_audit["records"]
    dev_records = dev_audit["records"]

    primary_train = select(train_records, "conversation_id")
    primary_dev = select(dev_records, "conversation_id")
    source_train = select(train_records, "filename")
    source_dev = select(dev_records, "filename")

    def materialize(records: list[dict[str, Any]], raw: dict[str, Any], policy: str) -> list[dict[str, Any]]:
        out = []
        for record in records:
            if record["id"] not in raw:
                raise ValueError(f"audit row missing from raw data: {record['id']}")
            out.append(selected_public_record(record, raw[record["id"]], policy))
        return out

    primary_train_rows = materialize(primary_train, train_raw, SELECTION_RULE)
    primary_dev_rows = materialize(primary_dev, dev_raw, SELECTION_RULE)
    source_train_rows = materialize(source_train, train_raw, SOURCE_SELECTION_RULE)
    source_dev_rows = materialize(source_dev, dev_raw, SOURCE_SELECTION_RULE)

    # Hard integrity checks before writing the contract.
    train_source = {x["filename"] for x in primary_train_rows}
    dev_source = {x["filename"] for x in primary_dev_rows}
    train_conv = {x["conversation_id"] for x in primary_train_rows}
    dev_conv = {x["conversation_id"] for x in primary_dev_rows}
    if train_source & dev_source or train_conv & dev_conv:
        raise SystemExit("train/dev primary manifests are not disjoint")
    if len({x["conversation_id"] for x in primary_train_rows}) != len(primary_train_rows):
        raise SystemExit("duplicate train conversation in primary manifest")
    if len({x["conversation_id"] for x in primary_dev_rows}) != len(primary_dev_rows):
        raise SystemExit("duplicate dev conversation in primary manifest")
    for row in [*primary_train_rows, *primary_dev_rows, *source_train_rows, *source_dev_rows]:
        if not row["dialogue_history"] or row["current_question"] != row["dialogue_history"][-1]:
            raise SystemExit(f"dialogue history invariant failed for {row['id']}")
        if not row["internal_gold"]["program"] or not row["internal_gold"]["target"]:
            raise SystemExit(f"internal gold invariant failed for {row['id']}")

    paths = {
        "primary_train": HERE / "V11_PRIMARY_TRAIN_ONE_PER_CONVERSATION.jsonl",
        "primary_dev": HERE / "V11_PRIMARY_DEV_ONE_PER_CONVERSATION.jsonl",
        "source_train": HERE / "V11_SENSITIVITY_TRAIN_ONE_PER_SOURCE.jsonl",
        "source_dev": HERE / "V11_SENSITIVITY_DEV_ONE_PER_SOURCE.jsonl",
    }
    public_paths = {key: HERE / path.name.replace(".jsonl", "_PUBLIC.jsonl") for key, path in paths.items()}
    gold_paths = {key: HERE / path.name.replace(".jsonl", "_GOLD.jsonl") for key, path in paths.items()}
    for key, rows in {
        "primary_train": primary_train_rows,
        "primary_dev": primary_dev_rows,
        "source_train": source_train_rows,
        "source_dev": source_dev_rows,
    }.items():
        write_jsonl(paths[key], rows)
        write_jsonl(public_paths[key], [public_projection(row) for row in rows])
        write_jsonl(gold_paths[key], [gold_projection(row) for row in rows])

    prompt_spec = {
        "version": "convfinqa-turn-prompt-v1",
        "model_visible_fields": ["dialogue_history", "pre_text", "table", "post_text"],
        "dialogue_rule": "Render every question in dialogue_history in order; the last question is the current turn. Do not add answers or programs to the visible prompt.",
        "source_scope": ["pre_text", "table", "post_text"],
        "mutation_rule": "Only the unique audited target numeric surface is changed in relevant worlds; dialogue history is not mutated.",
        "forbidden_visible_fields": ["program", "exe_ans", "target", "world_diagnostics", "annotation", "qa", "gold", "correctness"],
        "response_contract": {
            "format": "json_object",
            "required_keys": ["answer"],
            "optional_keys": ["confidence"],
            "answer_rule": "Answer the current last dialogue question; do not output a program or explanation unless the runner's fixed parser explicitly permits it.",
        },
    }
    prompt_spec_hash = hashlib.sha256(canonical_json(prompt_spec).encode("utf-8")).hexdigest()

    contract = {
        "contract": CONTRACT,
        "protocol": PROTOCOL,
        "version": "v0.11",
        "freeze_date": FREEZE_DATE,
        "status": "FROZEN_PRE_MODEL_CALL_NO_MODEL_CALLS",
        "claim_boundary": "Offline executable-semantics feasibility and capacity only. No ConvFinQA model result, PECR effectiveness claim, external validation claim, or distillation improvement claim is established by this freeze.",
        "model_calls": 0,
        "data": {
            "repository": "https://github.com/czyssrs/ConvFinQA",
            "main_commit": DATA_COMMIT,
            "data_zip_sha256": sha256(DATA_ZIP_PATH),
            "audit_sha256": sha256(AUDIT_PATH),
            "train_turn_audit_sha256": sha256(TRAIN_AUDIT_PATH),
            "dev_turn_audit_sha256": sha256(DEV_AUDIT_PATH),
            "private_test_policy": "test_turn_private has dialogue text but no gold program/executable answer fields; it is unavailable for this offline confirmation freeze and must not be used as a labeled confirmation set.",
            "finqa_v0_10_contract_sha256": "85bd5d32bb88c4be6f0af37bc8d9fe94299093a72338348370523335d3a82207",
            "finqa_v0_10_primary_feature_family_sha256": "b04224277fde686ba28a50361f6a25dbaa3a4aff0e92c56606baa5ab9dc00f24",
        },
        "offline_audit_gate": {
            "status": audit["decision"]["status"],
            "eligible_train_turns": audit["decision"]["eligible_train_turns"],
            "eligible_dev_turns": audit["decision"]["eligible_dev_turns"],
            "primary_train_one_per_conversation": len(primary_train_rows),
            "primary_dev_one_per_conversation": len(primary_dev_rows),
            "sensitivity_train_one_per_source": len(source_train_rows),
            "sensitivity_dev_one_per_source": len(source_dev_rows),
            "train_dev_source_disjoint": audit["decision"]["train_dev_source_disjoint"],
            "train_dev_conversation_disjoint": audit["decision"]["train_dev_conversation_disjoint"],
            "minimum_primary_capacity_gate": "primary train >= 200 and primary dev >= 150 and train/dev source disjoint",
            "minimum_primary_capacity_pass": bool(len(primary_train_rows) >= 200 and len(primary_dev_rows) >= 150 and audit["decision"]["train_dev_source_disjoint"]),
        },
        "selection": {
            "primary_unit": "conversation_id",
            "primary_rule": SELECTION_RULE,
            "primary_train_manifest": paths["primary_train"].name,
            "primary_dev_manifest": paths["primary_dev"].name,
            "sensitivity_unit": "filename/source file",
            "sensitivity_rule": SOURCE_SELECTION_RULE,
            "sensitivity_train_manifest": paths["source_train"].name,
            "sensitivity_dev_manifest": paths["source_dev"].name,
            "post_selection_outcome_tuning": False,
            "primary_cluster_field_for_uncertainty": "filename/source_group_id",
            "reason_primary_is_conversation": "One-per-source-file leaves only 114 dev items, below the predeclared 150-item confirmation capacity; primary uses one per conversation and reports source-cluster sensitivity.",
        },
        "hypotheses": {
            "replication": "On ConvFinQA, sparse executable response score S2 from original/-1/+1 predicts original answer correctness above chance.",
            "missing_probe": "Observed mild-probe response geometry contains information about the outcomes of unexecuted -2/+2 probes and reconstructed CEF improves over fixed S2 without additional deployment calls.",
        },
        "worlds_and_budget": {
            "teacher_collection_worlds": ["original", "relevant_k_minus2", "relevant_k_minus1", "relevant_k_plus1", "relevant_k_plus2"],
            "deployment_worlds": ["original", "relevant_k_minus1", "relevant_k_plus1"],
            "calls_per_item_for_deployment": 3,
            "calls_per_item_for_full_teacher_evaluation": 5,
            "full_cef": "mean(correctness over relevant_k_minus2, relevant_k_minus1, relevant_k_plus1, relevant_k_plus2)",
            "s2": "mean(correctness over relevant_k_minus1 and relevant_k_plus1)",
            "missing_targets": ["target_minus2 = correctness(relevant_k_minus2)", "target_plus2 = correctness(relevant_k_plus2)"],
            "reconstructed_cef": "(correct_minus1 + correct_plus1 + p_minus2 + p_plus2) / 4",
        },
        "prompt_spec": {
            "spec": prompt_spec,
            "sha256": prompt_spec_hash,
            "fresh_conversation_per_world": True,
            "gold_and_annotation_hidden_from_model": True,
            "question_history_visible": True,
        },
        "features_and_leakage": {
            "observed_worlds_only": ["original", "relevant_k_minus1", "relevant_k_plus1"],
            "allowed_observed_gold_oracle": "Executable counterfactual gold may be used by the evaluator to derive observed probe residual/direction/unit features, matching the FinQA PECR boundary.",
            "forbidden_features": ["relevant_k_minus2 response", "relevant_k_plus2 response", "full CEF", "original correctness", "unexecuted-probe gold-derived feature"],
            "primary_feature_family": "The frozen FinQA v0.10 all_response_rich mapping, ported without feature search; exact feature definitions and model coefficients must be frozen before calls.",
            "direct_correctness_student": "Diagnostic control only; it cannot select features, models, thresholds, or prompts.",
        },
        "models": {
            "qwen": {
                "endpoint": "http://127.0.0.1:31518/v1/chat/completions",
                "models_endpoint": "http://127.0.0.1:31518/v1/models",
                "expected_model": "Qwen3.5-4B",
            },
            "ling": {
                "endpoint": "http://127.0.0.1:31520/v1/chat/completions",
                "models_endpoint": "http://127.0.0.1:31520/v1/models",
                "expected_model": "Ling-3.0-tiny",
            },
            "identity_rule": "Verify /v1/models immediately before calls; abort on identity drift; no fallback model.",
        },
        "request_contract": {
            "temperature": 0.0,
            "top_p": 1.0,
            "n": 1,
            "stream": False,
            "response_format": {"type": "json_object"},
            "retries": 0,
            "fallback": False,
            "workers": 1,
            "fresh_conversation_per_world": True,
            "timeout_seconds": 180,
            "max_tokens": 180,
            "model_calls_authorized": False,
            "authorization_boundary": "Authorization remains false until a separate runner is reviewed against this frozen contract and the prompt/input artifact hashes.",
        },
        "metrics_and_gates": {
            "primary_replication": ["AUROC(S2, original_correct)", "group-bootstrap 95% CI with filename clusters", "permutation control"],
            "primary_distillation": ["AUROC(reconstructed_CEF, original_correct) - AUROC(S2, original_correct)", "paired group-bootstrap 95% CI", "MAE/reconstruction Spearman versus full CEF", "GapClosure"],
            "practical_delta_threshold": 0.02,
            "interpretation": "PASS_STRONG requires delta >= 0.02 and CI lower > 0; PASS_PRACTICAL_ONLY requires delta >= 0.02 with CI crossing 0; otherwise NO_MEANINGFUL_GAIN. These are confirmation labels, not claims of universal superiority.",
            "model_reporting": "Report Qwen and Ling separately; pooled analysis is secondary and must not replace per-model results.",
        },
        "artifacts": {
            "primary_train_manifest_internal_combined": paths["primary_train"].name,
            "primary_dev_manifest_internal_combined": paths["primary_dev"].name,
            "source_sensitivity_train_manifest_internal_combined": paths["source_train"].name,
            "source_sensitivity_dev_manifest_internal_combined": paths["source_dev"].name,
            "primary_train_public": public_paths["primary_train"].name,
            "primary_dev_public": public_paths["primary_dev"].name,
            "source_sensitivity_train_public": public_paths["source_train"].name,
            "source_sensitivity_dev_public": public_paths["source_dev"].name,
            "primary_train_gold": gold_paths["primary_train"].name,
            "primary_dev_gold": gold_paths["primary_dev"].name,
            "source_sensitivity_train_gold": gold_paths["source_train"].name,
            "source_sensitivity_dev_gold": gold_paths["source_dev"].name,
        },
    }
    artifact_paths = {
        "primary_train_manifest_internal_combined": paths["primary_train"],
        "primary_dev_manifest_internal_combined": paths["primary_dev"],
        "source_sensitivity_train_manifest_internal_combined": paths["source_train"],
        "source_sensitivity_dev_manifest_internal_combined": paths["source_dev"],
        "primary_train_public": public_paths["primary_train"],
        "primary_dev_public": public_paths["primary_dev"],
        "source_sensitivity_train_public": public_paths["source_train"],
        "source_sensitivity_dev_public": public_paths["source_dev"],
        "primary_train_gold": gold_paths["primary_train"],
        "primary_dev_gold": gold_paths["primary_dev"],
        "source_sensitivity_train_gold": gold_paths["source_train"],
        "source_sensitivity_dev_gold": gold_paths["source_dev"],
    }
    for key, path in artifact_paths.items():
        contract["artifacts"][f"{key}_sha256"] = sha256(path)
    contract_path = HERE / "CONVFINQA_V0_11_FROZEN_CONTRACT.json"
    write_json(contract_path, contract)

    status = {
        "status": contract["status"],
        "contract": contract_path.name,
        "model_calls": 0,
        "primary_train": len(primary_train_rows),
        "primary_dev": len(primary_dev_rows),
        "source_sensitivity_train": len(source_train_rows),
        "source_sensitivity_dev": len(source_dev_rows),
        "train_dev_source_disjoint": audit["decision"]["train_dev_source_disjoint"],
        "prompt_spec_sha256": prompt_spec_hash,
    }
    write_json(HERE / "V11_FREEZE_STATUS.json", status)
    (HERE / "V11_FREEZE_STATUS.md").write_text(
        "# ConvFinQA v0.11 freeze status (2026-09-22)\n\n"
        f"- Status: **{contract['status']}**\n"
        "- Model/API calls: **0**\n"
        f"- Primary one-per-conversation manifests: train **{len(primary_train_rows)}**, dev **{len(primary_dev_rows)}**\n"
        f"- Source-file sensitivity manifests: train **{len(source_train_rows)}**, dev **{len(source_dev_rows)}**\n"
        "- Public prompt inputs and internal gold ledgers are written as separate artifacts.\n"
        f"- Train/dev source-file disjoint: **{audit['decision']['train_dev_source_disjoint']}**\n"
        "- Primary contract is frozen before any ConvFinQA model call.\n\n"
        "The primary unit is one eligible executable program turn per conversation, selected by earliest turn index then stable ID. One-per-source-file is retained as a sensitivity analysis because it yields only 114 dev items. Private test labels are unavailable and are not used.\n",
        encoding="utf-8",
    )
    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
