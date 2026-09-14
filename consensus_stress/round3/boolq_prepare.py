"""Phase 6 cross-dataset: balanced BoolQ cohort (fresh, label-symmetric).

Reuses frozen V10 BoolQ evidence extraction (3 units, cosine gates) and the project's
round-1 BoolQ design (reverse = negation prefix; no distractor unit), with the round-2
direction-consistent gate and decision-relevance audit. Conditions:
original / paraphrase / reverse (negation) / remove. BF_q over {paraphrase, reverse}.
Fresh SALT -> fresh 50-yes/50-no cohort from boolq/train.parquet (validation roots are
covered by frozen V11.1/V12; train is the fresh pool, same as round 1).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase2"))
import round3_lib as pl3
import pilot_lib as pl2

ROOT = Path(__file__).resolve().parent
DATASET = ROOT.parents[1] / "data" / "benchmarks" / "boolq" / "train.parquet"
SALT = b"cs-paper-boolq-20260913\n"
PROTOCOL = "cs-paper-boolq-20260913"

CONDITIONS = ("original", "paraphrase", "reverse", "remove")
PRIMARY_SCORED = ("paraphrase", "reverse")
SCORED_ALL = ("paraphrase", "reverse")
FLIP_CONDITIONS = ("remove", "reverse")


def main() -> int:
    pl2.SALT = SALT
    pl2.PROTOCOL_VERSION = PROTOCOL
    pl2.configure_v10()
    items = pl2.v10.load_boolq(DATASET)
    comps = pl2.v10.build_composite_questions(items)
    counts = {l: sum(1 for c in comps if c.label == l) for l in ("yes", "no")}
    print("selected comps:", len(comps), counts)
    if counts != {"yes": 50, "no": 50}:
        raise ValueError(f"selection drift: {counts}")

    selection = {
        "protocol": PROTOCOL,
        "salt": SALT.decode().strip(),
        "dataset": str(DATASET),
        "dataset_sha256": pl3.file_sha256(DATASET),
        "n_agents": pl3.N_AGENTS,
        "partition_table": [sorted(s) for s in pl2.v10.PARTITION_TABLE],
        "agents": [aid for aid, _ in pl2.v10.AGENT_PERSONAS],
        "conditions": list(CONDITIONS),
        "primary_scored": list(PRIMARY_SCORED),
        "reverse_definition": "negation prefix 'Task-local counterfactual: it is false that: <unit>' "
                              "(frozen V10); BoolQ lacks natural counter-evidence (documented)",
        "items": [
            {"cqid": c.cqid, "label": c.label, "question": c.question_text,
             "evidence_units": [{"qid": it.qid, "text": it.passage, "source_root": it.source_root}
                                for it in c.items]}
            for c in comps
        ],
    }
    pl3.write_json(ROOT / "boolq_selection_manifest.json", selection)
    ledger = {"protocol": PROTOCOL, "status": "sealed",
              "items": [{"cqid": c.cqid, "gold_label": c.label} for c in comps]}
    pl3.write_json(ROOT / "boolq_labels_ledger.json", ledger)

    # relevance audit sample: 30 comps, deterministic
    sample = sorted(comps, key=lambda c: pl3.hpair("boolqaudit:" + c.cqid))[:30]
    pl3.write_json(ROOT / "boolq_relevance_audit_sample.json", {
        "protocol": PROTOCOL,
        "rule": ">=24/30 judged decision-relevant (3 evidence units answer the question), else exclude",
        "items": [{"cqid": c.cqid, "label": c.label, "question": c.question_text,
                   "units": [it.passage for it in c.items]} for c in sample],
        "judgments": [],
    })

    # paraphrase artifacts: 300 units x 2 variants
    all_items = [it for c in comps for it in c.items]
    client = pl3.CachedChatClient(ROOT / "cache", max_completion_tokens=pl3.ARTIFACT_MAX_TOKENS)
    manifest, stats = pl3.build_paraphrase_manifest(
        [{"unique_id": it.qid, "evidence": it.passage} for it in all_items], client,
        seed_base=pl3.PARAPHRASE_SEED + 3000)
    pl3.write_json(ROOT / "boolq_paraphrase_manifest.json", manifest)
    pl3.write_json(ROOT / "boolq_paraphrase_generation_stats.json", stats)
    print(json.dumps(stats, indent=2))
    print("ALL_ARTIFACTS_USABLE:", stats["unusable_fraction"] == 0.0)
    return 0 if stats["unusable_fraction"] == 0.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
