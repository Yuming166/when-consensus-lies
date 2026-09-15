#!/usr/bin/env python3
"""Hash all round7/ind_ce deliverable artifacts."""
import hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    targets = [
        "preregistration.md", "cohort.json", "frozen_hashes.json",
        "execution_notes.md", "run_summary_healthcheck.json",
        "run_summary_generation.json", "run_summary_audit.json",
        "strict_preregistration.md", "TARGET_SPEC_frozen_copy.md", "strict_generation.jsonl",
        "run_summary_strict_generation.json", "strict_artifacts.jsonl",
        "strict_audit_sample.jsonl", "run_summary_strict_audit.json",
        "strict_records.jsonl", "run_summary_strict_formal.json",
        "strict_preoutcome_features.jsonl", "strict_preoutcome_features_meta.json",
        "analysis/ind_ce_strict_results.json", "analysis/ind_ce_strict_results.md",
        "run_summary_smoke.json", "run_summary_formal.json",
        "records_smoke.jsonl", "records.jsonl", "e_ind_artifacts.jsonl",
        "audit_sample.jsonl", "e_ind_artifacts_v1_batch.jsonl", "generation_prompt_v2.md",
        "preoutcome_features.jsonl", "preoutcome_features_meta.json",
        "analysis/ind_ce_results.json", "analysis/ind_ce_results.md",
        "analysis/ind_ce_decision.md", "SUMMARY.md",
    ]
    out = {}
    for name in targets:
        p = HERE / name
        if p.exists():
            out[name] = sha(p)
        else:
            out[name] = None
    figures = sorted(p.name for p in (HERE / "figures").glob("*.png"))
    out["figures"] = {f: sha(HERE / "figures" / f) for f in figures}
    scripts = sorted(p.name for p in (HERE / "scripts").glob("*.py"))
    out["scripts"] = {f: sha(HERE / "scripts" / f) for f in scripts}
    (HERE / "artifact_hashes.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
