"""Build preoutcome features from FEVER records (same frozen feature definitions)."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl
from features import build_features

ROOT = Path(__file__).resolve().parent


def main() -> int:
    rows = [json.loads(l) for l in (ROOT / "fever_records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    feats = build_features(rows)
    pl.write_jsonl(ROOT / "fever_preoutcome_features.jsonl", feats)
    print(f"fever preoutcome features: {len(feats)} items (NO label fields)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
