#!/usr/bin/env python3
"""Round-7 W2: build + freeze cohort.json (first 100 items = first 50 pairs of round3
selection_manifest in manifest order; smoke = first 20 items). No model calls, no labels."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
R6 = HERE.parent.parent / "round6" / "large_model"

PROTOCOL = "cs-paper-ind-ce-20260914-round7-w2"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    pairs_all = sel["pairs"]
    # deterministic manifest order = the exact order in the manifest (round3 build order)
    first50 = pairs_all[:50]
    items: list[str] = []
    for r in first50:
        items.append(f"{r['pair_id']}:support")
        items.append(f"{r['pair_id']}:refute")
    assert len(items) == 100
    smoke = items[:20]
    formal = items[:100]
    assert set(smoke).issubset(set(formal))
    cohort = {
        "protocol": PROTOCOL,
        "cohort_rule": ("first 100 items = first 50 pair_ids of consensus_stress/round3/"
                        "selection_manifest.json in manifest order (support-then-refute per pair); "
                        "identical item set to round6 formal cohort"),
        "n_pairs": 50, "n_items_total": 100,
        "smoke_items": smoke, "formal_items": formal,
        "pairs": [r["pair_id"] for r in first50],
        "items": items,
        "selection_manifest_sha256": sha(R3 / "selection_manifest.json"),
        "paraphrase_manifest_sha256": sha(R3 / "paraphrase_manifest.json"),
    }
    out = HERE / "cohort.json"
    out.write_text(json.dumps(cohort, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    cohort_hash = sha(out)
    r6_hash = sha(R6 / "records.jsonl")
    hashes = {
        "cohort.json": cohort_hash,
        "round6_large_model_records.jsonl": r6_hash,
        "selection_manifest.json": cohort["selection_manifest_sha256"],
        "paraphrase_manifest.json": cohort["paraphrase_manifest_sha256"],
        "labels_ledger.json": sha(R3 / "labels_ledger.json"),
        "preregistration.md": None,  # filled after hash patch
    }
    (HERE / "frozen_hashes.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # patch placeholder hashes in preregistration.md
    pre = HERE / "preregistration.md"
    text = pre.read_text(encoding="utf-8")
    text = text.replace("<recorded-below-after-cohort-freeze>", cohort_hash)
    text = text.replace("<recorded-below-after-freeze>", r6_hash)
    pre.write_text(text, encoding="utf-8")
    hashes["preregistration.md"] = sha(pre)
    (HERE / "frozen_hashes.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("cohort written:", out)
    print("n_pairs:", len(first50), "n_items:", len(items), "smoke:", len(smoke), "formal:", len(formal))
    print("cohort.json sha256:", cohort_hash)
    print("round6 records sha256:", r6_hash)
    print("preregistration.md sha256:", hashes["preregistration.md"])
    print(json.dumps(hashes, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
