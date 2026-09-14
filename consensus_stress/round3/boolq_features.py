"""Build preoutcome features from BoolQ records (BoolQ-adapted BF_q over {paraphrase, reverse})."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl
import features as featmod

ROOT = Path(__file__).resolve().parent


def main() -> int:
    rows = [json.loads(l) for l in (ROOT / "boolq_records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    # BoolQ-adapted scored/flip definitions
    pl.PRIMARY_SCORED = ("paraphrase", "reverse")
    pl.SCORED_ALL = ("paraphrase", "reverse")
    featmod.FLIP_CONDITIONS = ("remove", "reverse")
    for r in rows:
        r.setdefault("item_id", r["cqid"])
        r.setdefault("pair_id", r["cqid"])
        r.setdefault("stage", 1)
    feats = featmod.build_features(rows)
    pl.write_jsonl(ROOT / "boolq_preoutcome_features.jsonl", feats)
    print(f"boolq preoutcome features: {len(feats)} items (NO label fields)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
