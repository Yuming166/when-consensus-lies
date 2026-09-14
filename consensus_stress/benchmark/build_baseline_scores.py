#!/usr/bin/env python3
"""Build label-blind Round-5 per-item external baseline scores."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
ROUND5 = PROJECT / "consensus_stress" / "round5"
CONDITIONS = ("original", "paraphrase", "reverse", "synthetic_reverse", "remove")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flip(answer: str) -> str:
    return "no" if answer == "yes" else "yes"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build_scores(records: list[dict]) -> list[dict]:
    by_item: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    metadata: dict[str, dict] = {}
    for rec in records:
        by_item[rec["cqid"]][rec["family"]].append(rec)
        metadata.setdefault(rec["cqid"], {"item_id": rec["item_id"], "pair_id": rec["pair_id"]})

    rows: list[dict] = []
    for cqid in sorted(by_item):
        item = by_item[cqid]
        sampling = sorted(item.get("sampling", []), key=lambda r: r["sample_index"])
        valid_samples = [r for r in sampling if r["success"] and r["decision"]]
        answers = [r["decision"]["answer"] for r in valid_samples]
        confs = [float(r["decision"]["confidence"]) for r in valid_samples]
        p_yes = answers.count("yes") / len(answers) if answers else 0.0
        p_no = answers.count("no") / len(answers) if answers else 0.0
        modal = max(set(answers), key=answers.count) if answers else None
        # Tie-breaking by first valid call is pre-registered.
        if answers:
            counts = {a: answers.count(a) for a in set(answers)}
            best = max(counts.values())
            modal = next(a for a in answers if counts[a] == best)
        p2 = p_yes * p_yes + p_no * p_no
        entropy = 0.0
        for p in (p_yes, p_no):
            if p > 0:
                entropy -= p * math.log2(p)
        mean_conf = sum(confs) / len(confs) if confs else None
        row = {
            "cqid": cqid,
            "item_id": metadata[cqid]["item_id"],
            "pair_id": metadata[cqid]["pair_id"],
            "sample_attempted_n": len(sampling),
            "sample_valid_n": len(valid_samples),
            "sample_p_yes": p_yes,
            "sample_p_no": p_no,
            "sample_modal_answer": modal,
            "risk_self_consistency_disagreement": 1.0 - max(p_yes, p_no) if answers else 1.0,
            "risk_selfcheck_answer_match": 1.0 - p2 if answers else 1.0,
            "risk_semantic_entropy_binary": entropy if answers else 1.0,
            "sample_mean_confidence": mean_conf,
            "risk_sample_mean_confidence": 1.0 - mean_conf if mean_conf is not None else 1.0,
        }

        intervention = item.get("intervention", [])
        by_rep: dict[int, dict[str, dict]] = defaultdict(dict)
        for rec in intervention:
            if rec.get("replicate") is not None:
                by_rep[int(rec["replicate"])][rec["condition"]] = rec
        usable = []
        per_rep = {}
        for rep in range(5):
            original = by_rep.get(rep, {}).get("original")
            paraphrase = by_rep.get(rep, {}).get("paraphrase")
            reverse = by_rep.get(rep, {}).get("reverse")
            if not (original and paraphrase and reverse):
                continue
            if not all(r["success"] and r["decision"] for r in (original, paraphrase, reverse)):
                continue
            y0 = original["decision"]["answer"]
            f_para = int(paraphrase["decision"]["answer"] == y0)
            f_rev = int(reverse["decision"]["answer"] == flip(y0))
            value = 0.5 * f_para + 0.5 * f_rev
            usable.append(value)
            per_rep[str(rep)] = {"original": y0, "f_paraphrase": f_para, "f_reverse": f_rev,
                                 "replicate_bf": value}
        bf_single = sum(usable) / len(usable) if usable else None
        row.update({
            "intervention_attempted_n": len(intervention),
            "intervention_usable_replicates": len(usable),
            "intervention_per_replicate": per_rep,
            "bf_single": bf_single,
            "risk_single_agent_intervention": -bf_single if bf_single is not None else None,
            "intervention_condition_valid_n": {
                cond: sum(r["success"] for r in intervention if r["condition"] == cond)
                for cond in CONDITIONS
            },
        })
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("qwen", "ling"), required=True)
    parser.add_argument("--records", type=Path, default=None)
    args = parser.parse_args()
    records_path = args.records if args.records is not None else \
        ROUND5 / f"{args.model}_baseline_records.jsonl"
    records = load_jsonl(records_path)
    if len(records) != 30_000:
        raise RuntimeError(f"expected 30,000 full-cohort records, found {len(records)}")
    rows = build_scores(records)
    if len(rows) != 600:
        raise RuntimeError(f"expected 600 score rows, found {len(rows)}")
    out = ROUND5 / f"{args.model}_baseline_scores_label_blind.jsonl"
    write_jsonl(out, rows)
    summary = {
        "model": args.model,
        "records_path": str(records_path.relative_to(PROJECT)),
        "records_sha256": sha256(records_path),
        "records": len(records),
        "record_valid": sum(r["success"] for r in records),
        "score_rows": len(rows),
        "scores_path": str(out.relative_to(PROJECT)),
        "scores_sha256": sha256(out),
        "sample_rows_with_all_25_valid": sum(r["sample_valid_n"] == 25 for r in rows),
        "intervention_rows_with_all_5_replicates": sum(
            r["intervention_usable_replicates"] == 5 for r in rows),
    }
    summary_path = ROUND5 / f"{args.model}_baseline_scores_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
