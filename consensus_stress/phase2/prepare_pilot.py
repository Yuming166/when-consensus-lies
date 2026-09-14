"""CS pilot: selection + frozen intervention artifacts (substitute + paraphrase).

Writes selection_manifest.json (with labels for offline balance audit),
labels_ledger.json (sealed), substitute_manifest.json, paraphrase_manifest.json,
expected_response_contract.json, and artifact hashes. NO agent decision calls here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_lib as pl

ROOT = Path(__file__).resolve().parent
DATASET = ROOT.parents[1] / "data" / "benchmarks" / "boolq" / "train.parquet"


def expected_response_contract() -> dict:
    return {
        "protocol": pl.PROTOCOL_VERSION,
        "oracle_definition": {
            "original": "reference Y0 (agent's own original answer)",
            "paraphrase": "Y* = Y0 (no deterministic change; semantic-preserving)",
            "reverse": "Y* = flip(Y0) (explicit polarity reversal)",
            "substitute": "Y* = flip(Y0) (opposite-supporting rewrite artifact)",
            "remove": "NO-FORCED-RESPONSE (unscored for faithfulness; descriptive only)",
        },
        "scored_conditions": list(pl.SCORED_CONDITIONS),
        "oracle_basis": "transformation semantics only; frozen before any agent call",
        "label_use": "gold answer used ONLY offline to (a) balance selection, (b) write "
                     "opposite-supporting substitutes; never sent to agents, never in scoring",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, default=DATASET)
    args = ap.parse_args()

    comps = pl.load_composites(args.dataset)
    counts = {l: sum(1 for c in comps if c.label == l) for l in ("yes", "no")}
    print(f"selected {len(comps)} composites ({counts})")

    selection = {
        "protocol": pl.PROTOCOL_VERSION,
        "salt": pl.SALT.decode().strip(),
        "dataset": str(args.dataset),
        "dataset_sha256": pl.file_sha256(args.dataset),
        "n_agents": pl.N_AGENTS,
        "conditions": list(pl.CONDITIONS),
        "partition_table": [sorted(s) for s in pl.v10.PARTITION_TABLE],
        "agents": [aid for aid, _ in pl.v10.AGENT_PERSONAS],
        "items": [
            {
                "cqid": c.cqid,
                "label": c.label,
                "question": c.question_text,
                "evidence_units": [{"qid": it.qid, "text": it.passage,
                                    "source_root": it.source_root} for it in c.items],
            }
            for c in comps
        ],
    }
    pl.write_json(ROOT / "selection_manifest.json", selection)
    ledger = {
        "protocol": pl.PROTOCOL_VERSION,
        "status": "sealed_until_preoutcome_features_are_frozen",
        "items": [{"cqid": c.cqid, "gold_label": c.label} for c in comps],
    }
    pl.write_json(ROOT / "labels_ledger.json", ledger)
    pl.write_json(ROOT / "expected_response_contract.json", expected_response_contract())

    all_items = [it for c in comps for it in c.items]
    client = pl.CachedChatClient(ROOT / "cache")

    print("generating substitutes...")
    sub_manifest, sub_stats = pl.build_substitute_manifest_cs(all_items, client=client)
    pl.write_json(ROOT / "substitute_manifest.json", sub_manifest)
    pl.write_json(ROOT / "substitute_generation_stats.json", sub_stats)

    print("generating paraphrases...")
    para_manifest, para_stats = pl.build_paraphrase_manifest(all_items, client=client)
    pl.write_json(ROOT / "paraphrase_manifest.json", para_manifest)
    pl.write_json(ROOT / "paraphrase_generation_stats.json", para_stats)

    artifact_hashes = {
        "selection_manifest": pl.file_sha256(ROOT / "selection_manifest.json"),
        "labels_ledger": pl.file_sha256(ROOT / "labels_ledger.json"),
        "expected_response_contract": pl.file_sha256(ROOT / "expected_response_contract.json"),
        "substitute_manifest": pl.file_sha256(ROOT / "substitute_manifest.json"),
        "paraphrase_manifest": pl.file_sha256(ROOT / "paraphrase_manifest.json"),
    }
    pl.write_json(ROOT / "artifact_hashes.json", artifact_hashes)
    print("artifact hashes:", json.dumps(artifact_hashes, indent=2))
    print("substitute stats:", json.dumps(sub_stats, indent=2))
    print("paraphrase stats:", json.dumps(para_stats, indent=2))
    ok = (sub_stats["unusable_fraction"] == 0.0 and para_stats["unusable_fraction"] == 0.0)
    print("ALL_ARTIFACTS_USABLE:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
