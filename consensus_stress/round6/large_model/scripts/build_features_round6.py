"""Round-6 Agent D: build label-free preoutcome features from relay GPT records.

Reuses Round-3 features.build_features (identical formula). Writes
large_model/preoutcome_features.jsonl (NO label fields) and records its SHA256.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROUND3 = Path(__file__).resolve().parent.parent.parent.parent / "round3"
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROUND3))
from features import build_features  # noqa: E402
import round3_lib as pl  # noqa: E402

def enrich_agent_bf(feats, records):
    """Replicate Round-3 features.main() _agent_bf enrichment (label-free)."""
    from features import flip
    by_q = {}
    for r in records:
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
                    exp = y0 if cond == "paraphrase" else flip(y0)
                    row[cond] = int(d["answer"] == exp)
            f["_agent_bf"][str(i)] = row
    return feats


def main() -> int:
    records = [json.loads(l) for l in (HERE / "records.jsonl").read_text(encoding="utf-8").splitlines() if l]
    feats = build_features(records)
    feats = enrich_agent_bf(feats, records)
    out_path = HERE / "preoutcome_features.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in feats:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    h = hashlib.sha256(out_path.read_bytes()).hexdigest()
    meta = {"protocol": "cs-paper-gpt-singlepoint-20260914-round6",
            "n_records": len(records), "n_features": len(feats),
            "label_free": True, "sha256": h}
    (HERE / "preoutcome_features_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print("feature keys sample:", sorted(feats[0].keys()) if feats else "NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
