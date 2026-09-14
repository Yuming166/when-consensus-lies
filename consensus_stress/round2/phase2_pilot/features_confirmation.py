"""Confirmation cohort: preoutcome features (NO label fields)."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import round2_lib as pl
from features import build_features as build_pilot_features  # reuse identical logic

ROOT = Path(__file__).resolve().parent
PREFIX = "confirmation"


def main() -> int:
    rows = [json.loads(l) for l in (ROOT / f"{PREFIX}_records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    feats = build_pilot_features(rows)
    # per-agent per-condition faithfulness (same as pilot features.py)
    by_q = {}
    for r in rows:
        by_q.setdefault(r["cqid"], {})[(r["agent_index"], r["condition"])] = r["decision"]
    for f in feats:
        q = by_q[f["cqid"]]
        f["_agent_bf"] = {}
        for i in range(pl.N_AGENTS):
            y0 = q.get((i, "original"), {}).get("answer")
            row = {}
            for cond in pl.SCORED_ALL:
                d = q.get((i, cond), {})
                if y0 is None or not d:
                    row[cond] = None
                else:
                    exp = y0 if cond == "paraphrase" else ("no" if y0 == "yes" else "yes")
                    row[cond] = int(d["answer"] == exp)
            f["_agent_bf"][str(i)] = row
    pl.write_jsonl(ROOT / f"{PREFIX}_preoutcome_features.jsonl", feats)
    print(f"confirmation preoutcome features: {len(feats)} items (NO label fields)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
