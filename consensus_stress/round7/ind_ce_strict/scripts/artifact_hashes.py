#!/usr/bin/env python3
"""Round-7 W2b: final artifact hashes for ind_ce_strict."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
FILES = [
    "preregistration.md", "cohort.json", "e_gen_artifacts.jsonl",
    "e_ind_strict_artifacts.jsonl", "audit_sample.jsonl", "records_smoke.jsonl",
    "records.jsonl", "preoutcome_features.jsonl", "preoutcome_features_meta.json",
    "run_summary_healthcheck.json", "run_summary_generation.json",
    "run_summary_parser_correction.json", "run_summary_assignment.json",
    "run_summary_audit.json", "run_summary_smoke.json", "run_summary_formal.json",
    "analysis/strict_results.json", "analysis/strict_results.md",
    "execution_notes.md", "decision.md", "SUMMARY.md",
]

def main() -> int:
    hashes = {}
    for f in FILES:
        p = HERE / f
        if p.exists():
            hashes[f] = hashlib.sha256(p.read_bytes()).hexdigest()
        else:
            hashes[f] = None
    out = {"stage": "final_artifact_hashes", "protocol": "cs-paper-ind-ce-strict-20260915-round7-w2b",
           "hashes": hashes}
    (HERE / "artifact_hashes.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
