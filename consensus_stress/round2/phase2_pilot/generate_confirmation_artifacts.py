"""Confirmation cohort offline paraphrase artifacts (cached; no agent decision calls)."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import round2_lib as pl

ROOT = Path(__file__).resolve().parent
PREFIX = "confirmation"


def main() -> int:
    sel = json.loads((ROOT / f"{PREFIX}_selection_manifest.json").read_text(encoding="utf-8"))
    client = pl.CachedChatClient(ROOT / "cache", max_completion_tokens=pl.ARTIFACT_MAX_TOKENS)
    manifest, stats = pl.build_paraphrase_manifest(sel["evidence"], client,
                                                   seed_base=pl.PARAPHRASE_SEED + 1000)
    pl.write_json(ROOT / f"{PREFIX}_paraphrase_manifest.json", manifest)
    pl.write_json(ROOT / f"{PREFIX}_paraphrase_generation_stats.json", stats)
    print(json.dumps(stats, indent=2))
    print("ALL_ARTIFACTS_USABLE:", stats["unusable_fraction"] == 0.0)
    return 0 if stats["unusable_fraction"] == 0.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
