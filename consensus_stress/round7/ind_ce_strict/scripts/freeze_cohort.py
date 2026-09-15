#!/usr/bin/env python3
"""Round-7 W2b: freeze cohort (first 50 items = first 25 pairs, manifest order) and
record SHA256 of preregistration + frozen inputs. Run BEFORE any experimental call.
No labels read; cohort order is manifest order (support-then-refute per pair)."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
R6 = HERE.parent.parent / "round6" / "large_model"
W2 = HERE.parent / "ind_ce"
N_PAIRS = 25


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    pairs = sel["pairs"][:N_PAIRS]
    assert len(pairs) == N_PAIRS
    items = []
    for p in pairs:
        assert p["items"][0]["item_id"].endswith(":support")
        assert p["items"][1]["item_id"].endswith(":refute")
        items.extend([p["items"][0]["item_id"], p["items"][1]["item_id"]])
    assert len(items) == 2 * N_PAIRS
    assert len(set(items)) == len(items)
    cohort = {
        "protocol_version": "cs-paper-ind-ce-strict-20260915-round7-w2b",
        "cohort_rule": ("first 50 items = first 25 pair_ids of "
                        "consensus_stress/round3/selection_manifest.json in manifest order "
                        "(support-then-refute per pair)"),
        "n_pairs": N_PAIRS, "n_items": len(items),
        "pairs": [p["pair_id"] for p in pairs],
        "items": items,
        "smoke_items": items[:20],  # first 10 pairs
        "smoke_pairs": [p["pair_id"] for p in pairs[:10]],
    }
    out = HERE / "cohort.json"
    out.write_text(json.dumps(cohort, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    prereg = HERE / "preregistration.md"
    hashes = {
        "preregistration.md": sha256(prereg),
        "cohort.json": sha256(out),
        "round3/selection_manifest.json": sha256(R3 / "selection_manifest.json"),
        "round3/labels_ledger.json": sha256(R3 / "labels_ledger.json"),
        "round3/preoutcome_features.jsonl": sha256(R3 / "preoutcome_features.jsonl"),
        "round6/large_model/records.jsonl": sha256(R6 / "records.jsonl"),
        "round7/ind_ce/records.jsonl": sha256(W2 / "records.jsonl"),
        "round7/ind_ce/e_ind_artifacts.jsonl": sha256(W2 / "e_ind_artifacts.jsonl"),
    }
    (HERE / "artifact_hashes.json").write_text(
        json.dumps({"stage": "preregistration_freeze", "hashes": hashes},
                   ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"n_items": len(items), "n_pairs": N_PAIRS,
                      "prereg_sha256": hashes["preregistration.md"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
