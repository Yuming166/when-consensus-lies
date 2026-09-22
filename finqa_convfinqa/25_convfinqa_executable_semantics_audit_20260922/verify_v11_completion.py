#!/usr/bin/env python3
"""Requirement-by-requirement completion audit for the ConvFinQA v0.11 freeze."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V10 = HERE.parent / "24_pecr_v0_10_missing_probe_imputation_20260922"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check(condition: bool, evidence: str, failures: list[str]) -> None:
    if not condition:
        failures.append(evidence)


def main() -> None:
    failures: list[str] = []
    evidence: dict[str, Any] = {}

    # FinQA v0.10 freeze boundary.
    v10_contract = load(V10 / "PECR_V0_10_FROZEN_CONTRACT.json")
    v10_results = load(V10 / "V10_PHASE_A_RESULTS.json")
    v10_audit = load(V10 / "V10_DATASET_AUDIT.json")
    v10_manifest = load(V10 / "V10_ARTIFACT_MANIFEST.json")
    check(v10_contract["status"] == "FROZEN_PHASE_A_NO_NEW_MODEL_CALLS", "FinQA v0.10 contract is not frozen/no-new-calls", failures)
    check(v10_results["model_calls"] == 0, "FinQA v0.10 phase-A results report nonzero model calls", failures)
    check(v10_audit["model_calls"] == 0, "FinQA v0.10 dataset audit reports nonzero model calls", failures)
    check(v10_manifest["model_calls"] == 0, "FinQA v0.10 artifact manifest reports nonzero model calls", failures)
    check(v10_results["historical_artifacts_modified"] is False, "FinQA v0.10 historical artifacts are marked modified", failures)
    evidence["finqa_v0_10"] = {
        "contract_status": v10_contract["status"],
        "phase_a_status": v10_results["status"],
        "phase_a_model_calls": v10_results["model_calls"],
        "dataset_audit_model_calls": v10_audit["model_calls"],
        "artifact_manifest_model_calls": v10_manifest["model_calls"],
        "historical_artifacts_modified": v10_results["historical_artifacts_modified"],
    }

    # ConvFinQA audit and freeze artifacts.
    audit = load(HERE / "CONVFINQA_EXECUTABLE_SEMANTICS_AUDIT.json")
    train_audit = load(HERE / "TRAIN_TURN_AUDIT.json")
    dev_audit = load(HERE / "DEV_TURN_AUDIT.json")
    test_audit = load(HERE / "TEST_TURN_PRIVATE_AUDIT.json")
    contract = load(HERE / "CONVFINQA_V0_11_FROZEN_CONTRACT.json")
    static = load(HERE / "V11_STATIC_FREEZE_AUDIT.json")

    check(audit["decision"]["status"] == "PROCEED_TO_FREEZE_REPLICATION_CONTRACT", "ConvFinQA audit did not pass the freeze gate", failures)
    check(audit["model_calls"] == 0, "ConvFinQA executable audit reports nonzero model calls", failures)
    check(audit["source"]["data_zip_sha256"] == "d764271fae60d81b62e6d58dfc481807ebc8cfbcd633811241723c4a2101072a", "ConvFinQA data archive hash changed", failures)
    check(audit["source"]["expected_main_commit"] == "cf3eed2d5984960bf06bb8145bcea5e80b0222a6", "ConvFinQA source commit changed", failures)
    check(audit["split_overlap"]["train_dev_disjoint_at_conversation_level"] is True, "train/dev conversation overlap exists", failures)
    check(audit["split_overlap"]["train_dev_disjoint_at_source_file_level"] is True, "train/dev source-file overlap exists", failures)
    check(audit["decision"]["eligible_train_turns"] == 1814, "unexpected eligible train count", failures)
    check(audit["decision"]["eligible_dev_turns"] == 283, "unexpected eligible dev count", failures)
    check(audit["decision"]["eligible_train_one_per_conversation"] == 1344, "unexpected train conversation capacity", failures)
    check(audit["decision"]["eligible_dev_one_per_conversation"] == 198, "unexpected dev conversation capacity", failures)
    check(audit["history_semantics"]["symbolic_reference_audit"]["train_turn"]["all_observed_references_local_to_current_program"] is True, "train symbolic reference locality failed", failures)
    check(audit["history_semantics"]["symbolic_reference_audit"]["dev_turn"]["all_observed_references_local_to_current_program"] is True, "dev symbolic reference locality failed", failures)
    check(test_audit["summary"]["unavailable_rows"] == test_audit["summary"]["rows"], "private test rows were treated as labeled audit rows", failures)

    # Requirement-level checks over every eligible record.
    for name, audit_obj in [("train", train_audit), ("dev", dev_audit)]:
        records = audit_obj["records"]
        eligible = [r for r in records if r["status"] == "ELIGIBLE"]
        check(audit_obj["summary"]["history_all_checks_pass"] == audit_obj["summary"]["history_checked_rows"], f"{name} history consistency has failures", failures)
        for row in eligible:
            rid = row.get("id", "<missing>")
            check(row.get("turn_type") == "program_turn", f"{name}:{rid} not program_turn", failures)
            check(row.get("base_execution_error") is None and row.get("base_answer_alignment") is True, f"{name}:{rid} base execution/alignment failure", failures)
            check(row.get("candidate_count") == 1, f"{name}:{rid} candidate count is not one", failures)
            target = row.get("target") or {}
            dep = target.get("dependency_path") or []
            check(bool(dep) and dep[-1] == row.get("base_program_trace_length", 0) - 1, f"{name}:{rid} dependency does not reach final step", failures)
            worlds = (row.get("world_diagnostics") or {}).get("worlds", {})
            invariants = (row.get("world_diagnostics") or {}).get("invariant_worlds", {})
            check(set(worlds) == {"-2", "-1", "1", "2"}, f"{name}:{rid} missing one or more k worlds", failures)
            check(set(invariants) == {"1", "2"}, f"{name}:{rid} missing invariant worlds", failures)
            for k, diag in worlds.items():
                check(diag.get("dual_execute_agrees") is True, f"{name}:{rid}:k={k} dual executor mismatch", failures)
                check(diag.get("result_changed") is True, f"{name}:{rid}:k={k} result did not change", failures)
                check(len(diag.get("input_diff_paths", [])) == 1, f"{name}:{rid}:k={k} input mutation not single-target", failures)
            for variant, diag in invariants.items():
                check(diag.get("preserves_result") is True, f"{name}:{rid}:invariant={variant} changed result", failures)
                check(len(diag.get("input_diff_paths", [])) == 1, f"{name}:{rid}:invariant={variant} mutation not single-target", failures)
        evidence[f"{name}_eligible_records"] = len(eligible)

    # Frozen contract and static audit.
    check(contract["status"] == "FROZEN_PRE_MODEL_CALL_NO_MODEL_CALLS", "v0.11 contract is not frozen before calls", failures)
    check(contract["request_contract"]["model_calls_authorized"] is False, "v0.11 contract authorizes calls unexpectedly", failures)
    check(contract["offline_audit_gate"]["minimum_primary_capacity_pass"] is True, "v0.11 minimum capacity gate failed", failures)
    check(static["summary"]["all_checks_pass"] is True, "v0.11 static freeze audit did not pass", failures)
    for key, value in contract["artifacts"].items():
        if not key.endswith("_sha256"):
            continue
        artifact_key = key[:-7]
        check(artifact_key in contract["artifacts"], f"unmapped artifact hash {key}", failures)
        if artifact_key in contract["artifacts"]:
            path = HERE / contract["artifacts"][artifact_key]
            check(path.exists(), f"missing artifact {path.name}", failures)
            if path.exists():
                check(sha256(path) == value, f"artifact hash mismatch {path.name}", failures)
    evidence["convfinqa"] = {
        "audit_status": audit["decision"]["status"],
        "eligible_train_turns": audit["decision"]["eligible_train_turns"],
        "eligible_dev_turns": audit["decision"]["eligible_dev_turns"],
        "primary_train_conversations": audit["decision"]["eligible_train_one_per_conversation"],
        "primary_dev_conversations": audit["decision"]["eligible_dev_one_per_conversation"],
        "source_sensitivity_train": audit["capacity"]["train_turn"]["one_per_source_file"],
        "source_sensitivity_dev": audit["capacity"]["dev_turn"]["one_per_source_file"],
        "train_dev_source_disjoint": audit["decision"]["train_dev_source_disjoint"],
        "train_dev_conversation_disjoint": audit["decision"]["train_dev_conversation_disjoint"],
        "model_calls": audit["model_calls"],
    }
    result = {
        "protocol": "ConvFinQA_PECR_v0.11_completion_audit",
        "date": "2026-09-22",
        "status": "PASS" if not failures else "FAIL",
        "model_calls": 0,
        "failures": failures,
        "evidence": evidence,
    }
    (HERE / "V11_COMPLETION_AUDIT.json").write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "failures": len(failures), "model_calls": 0, "evidence": evidence}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
