"""Round-3 paper-scale: offline paraphrase artifacts (cached; no agent decision calls)."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl

ROOT = Path(__file__).resolve().parent


def main() -> int:
    sel = json.loads((ROOT / "selection_manifest.json").read_text(encoding="utf-8"))
    client = pl.CachedChatClient(ROOT / "cache", max_completion_tokens=pl.ARTIFACT_MAX_TOKENS)
    manifest, stats = pl.build_paraphrase_manifest(sel["evidence"], client,
                                                   seed_base=pl.PARAPHRASE_SEED)
    pl.write_json(ROOT / "paraphrase_manifest.json", manifest)
    pl.write_json(ROOT / "paraphrase_generation_stats.json", stats)
    hashes = {
        "paraphrase_manifest": pl.file_sha256(ROOT / "paraphrase_manifest.json"),
        "selection_manifest": pl.file_sha256(ROOT / "selection_manifest.json"),
        "labels_ledger": pl.file_sha256(ROOT / "labels_ledger.json"),
        "expected_response_contract": pl.file_sha256(ROOT / "expected_response_contract.json"),
        "relevance_audit": pl.file_sha256(ROOT / "relevance_audit.json"),
    }
    pl.write_json(ROOT / "artifact_hashes.json", hashes)
    print(json.dumps(stats, indent=2))
    print("ALL_ARTIFACTS_USABLE:", stats["unusable_fraction"] == 0.0)
    return 0 if stats["unusable_fraction"] == 0.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
