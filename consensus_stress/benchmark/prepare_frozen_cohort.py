#!/usr/bin/env python3
"""Package frozen Round-3/Round-4 CST-Bench inputs without reselection."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
CS = PROJECT / "consensus_stress"
R3 = CS / "round3"
R4 = CS / "round4"
OUT = HERE / "frozen"

CORE = {
    R3 / "selection_manifest.json": "5f575ff873b3243b4916f77ab81269476da937d466eec967eff0934efe39089b",
    R3 / "paraphrase_manifest.json": "5b322c4973328b5323edf8111a4e4195c4a4d895c9890dfb73a8d0f29d514435",
    R3 / "preoutcome_features.jsonl": "d0c588d05211769c14234377d669881d079dacaac0ebaf2ec9326561d967584d",
    R3 / "labels_ledger.json": "770ede3f79b018c47aa982e6cb3f13b9d504b5c14950f7f1a8f6de196ffcbc5a",
    R4 / "ling_preoutcome_features.jsonl": "35e853cf0815cb1428ec8f2ee671993bd1f87ba8b28ade24a630ac4c79bc26bb",
    R3 / "records.jsonl": "ce5280ede80c92f471ff73b1b8fe1c0fc339bd057aae67825e54f7d42a706a08",
    R4 / "ling_records.jsonl": "fc0e32126b3ce0a1c5394d11a706a072611a9fd12797b3624789cc0dda62d4d2",
}

VITAMINC = [
    R3 / "selection_manifest.json",
    R3 / "paraphrase_manifest.json",
    R3 / "expected_response_contract.json",
    R3 / "labels_ledger.json",
    R3 / "preoutcome_features.jsonl",
    R3 / "records.jsonl",
    R4 / "ling_preoutcome_features.jsonl",
    R4 / "ling_records.jsonl",
    R4 / "run_summary_ling.json",
]

BOOLQ = [
    R3 / "boolq_selection_manifest.json",
    R3 / "boolq_paraphrase_manifest.json",
    R3 / "boolq_labels_ledger.json",
    R3 / "boolq_preoutcome_features.jsonl",
    R3 / "boolq_records.jsonl",
    R3 / "run_summary_boolq.json",
    R3 / "analysis" / "boolq_analysis.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_group(paths: list[Path], destination: Path) -> list[dict[str, str]]:
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    for src in paths:
        if not src.exists():
            raise FileNotFoundError(src)
        dst = destination / src.name
        shutil.copy2(src, dst)
        rows.append({"source": str(src.relative_to(PROJECT)), "packaged": str(dst.relative_to(HERE)),
                     "sha256": sha256(dst), "bytes": dst.stat().st_size})
    return rows


def main() -> int:
    for src, expected in CORE.items():
        actual = sha256(src)
        if actual != expected:
            raise RuntimeError(f"frozen hash mismatch: {src}: {actual} != {expected}")
    manifest = {
        "protocol": "cs-round5-matched-baselines-cst-bench-20260913",
        "selection_rule": "exact reuse; no reselection or replacement",
        "vitaminc_main_split": copy_group(VITAMINC, OUT / "vitaminc"),
        "boolq_specificity_split": copy_group(BOOLQ, OUT / "boolq"),
        "core_hash_checks": {str(src.relative_to(PROJECT)): expected for src, expected in CORE.items()},
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (OUT / "SHA256SUMS").open("w", encoding="utf-8") as handle:
        for split_key in ("vitaminc_main_split", "boolq_specificity_split"):
            for row in manifest[split_key]:
                packaged = Path(row["packaged"]).relative_to(OUT.relative_to(HERE))
                handle.write(f'{row["sha256"]}  {packaged.as_posix()}\n')
    print(json.dumps({"packaged_files": sum(len(manifest[k]) for k in ("vitaminc_main_split", "boolq_specificity_split")),
                      "manifest": str((OUT / "manifest.json").relative_to(HERE))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
