"""Build Ling preoutcome features using the unchanged round-3 definitions."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "round3"))
from features import build_features, flip  # noqa: E402
import round3_lib as pl  # noqa: E402


def main() -> int:
    records = [json.loads(line) for line in
               (HERE / "ling_records.jsonl").read_text(encoding="utf-8").splitlines() if line]
    feats = build_features(records)
    by_question: dict[str, dict] = {}
    for record in records:
        by_question.setdefault(record["cqid"], {})[
            (record["agent_index"], record["condition"])] = record["decision"]
    for row in feats:
        decisions = by_question[row["cqid"]]
        row["_agent_bf"] = {}
        for agent_index in range(pl.N_AGENTS):
            original = decisions.get((agent_index, "original"), {}).get("answer")
            agent_row = {}
            for condition in pl.SCORED_ALL:
                decision = decisions.get((agent_index, condition), {})
                if original is None or not decision:
                    agent_row[condition] = None
                else:
                    expected = original if condition == "paraphrase" else flip(original)
                    agent_row[condition] = int(decision["answer"] == expected)
            row["_agent_bf"][str(agent_index)] = agent_row
    pl.write_jsonl(HERE / "ling_preoutcome_features.jsonl", feats)
    print(f"ling preoutcome features: {len(feats)} items (NO label fields)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
