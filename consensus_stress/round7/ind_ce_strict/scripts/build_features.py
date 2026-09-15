#!/usr/bin/env python3
"""Round-7 W2b: build label-free preoutcome features (NO label fields) from
strict records (ind_strict, pm), frozen W2 natural records, frozen round-6 gpt
original answers, and frozen round-3 Qwen features (RS_q = -bf_q). Items require
all 5 frozen original answers AND successful strict generation/assignment."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
R6 = HERE.parent.parent / "round6" / "large_model"
W2 = HERE.parent / "ind_ce"
PROTOCOL = "cs-paper-ind-ce-strict-20260915-round7-w2b"
CONDITIONS = ("ind_strict", "pm")


def flip(y0, y1):
    return int(y0 != y1)


def load_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l]


def main() -> int:
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    # strict records (smoke + formal; smoke subset replayed in formal)
    strict = {}
    for fn in ("records_smoke.jsonl", "records.jsonl"):
        for r in load_jsonl(HERE / fn):
            if r.get("decision"):
                strict[(r["item_id"], r["agent_index"], r["condition"])] = r["decision"]
    # W2 natural records (reused, read-only)
    natural = {}
    for r in load_jsonl(W2 / "records.jsonl"):
        if r.get("decision") and r["condition"] == "natural":
            natural[(r["item_id"], r["agent_index"])] = r["decision"]
    # round6 originals
    orig = {}
    for r in load_jsonl(R6 / "records.jsonl"):
        if r["condition"] == "original" and r.get("decision"):
            orig[(r["item_id"], r["agent_index"])] = r["decision"]
    # round3 Qwen features (RS_q = -bf_q)
    qwen = {r["item_id"]: r for r in load_jsonl(R3 / "preoutcome_features.jsonl")}
    # assigned strict artifacts
    assigned = {r["item_id"]: r for r in load_jsonl(HERE / "e_ind_strict_artifacts.jsonl")
                if r.get("success")}
    sys.path.insert(0, str(R3))
    import round3_lib as pl  # noqa: E402

    feats = []
    excluded = {"missing_original": [], "missing_generation": [], "no_consensus_yes": []}
    for it in cohort["items"]:
        orig_answers = [orig.get((it, i)) for i in range(5)]
        if any(d is None for d in orig_answers):
            excluded["missing_original"].append(it)
            continue
        if it not in assigned:
            excluded["missing_generation"].append(it)
            continue
        answers = [d["answer"] for d in orig_answers]
        confs = [d["confidence"] for d in orig_answers]
        consensus = max(set(answers), key=answers.count)
        row = {
            "protocol_version": PROTOCOL,
            "item_id": it, "pair_id": ":".join(it.split(":")[:2]),
            "cqid": pl.cqid_for(it),
            "consensus": consensus, "agreement": round(answers.count(consensus) / 5.0, 4),
            "mean_confidence": round(sum(confs) / 5.0, 4),
            "conf_dispersion": round(max(confs) - min(confs), 4),
        }
        # per-condition flip stats
        for cond in CONDITIONS + ("natural",):
            flips = []
            for i in range(5):
                if cond == "natural":
                    d = natural.get((it, i))
                else:
                    d = strict.get((it, i, cond))
                if d:
                    flips.append(flip(orig_answers[i]["answer"], d["answer"]))
            row[f"S_{cond}"] = round(sum(flips) / 5.0, 4) if len(flips) == 5 else None
            row[f"n_{cond}"] = len(flips)
            row[f"_agent_flip_{cond}"] = [int(x) for x in flips]
        # RS_q (Qwen frozen risk score)
        bf_q = qwen.get(it, {}).get("bf_q")
        row["RS_q"] = round(-bf_q, 4) if bf_q is not None else None
        # combined (frozen weights)
        a, b = row.get("S_natural"), row.get("S_ind_strict")
        row["S_combined_natural_ind"] = round(0.5 * a + 0.5 * b, 4) if (a is not None and b is not None) else None
        feats.append(row)
    feats.sort(key=lambda r: cohort["items"].index(r["item_id"]))
    (HERE / "preoutcome_features.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in feats) + "\n",
        encoding="utf-8")
    meta = {
        "stage": "preoutcome_features_freeze", "protocol_version": PROTOCOL,
        "n_items": len(feats), "n_pairs": len({f["pair_id"] for f in feats}),
        "excluded": excluded,
        "sha256": hashlib.sha256((HERE / "preoutcome_features.jsonl").read_bytes()).hexdigest(),
        "note": "label-free; labels merged only after this hash is recorded",
    }
    (HERE / "preoutcome_features_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
