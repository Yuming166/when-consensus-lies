#!/usr/bin/env python3
"""Round-7 W1 P0 audit (3/3): label-leakage trace along
prompt construction -> evidence generation -> scoring -> model selection ->
threshold selection. READ-ONLY static verification of the frozen pipeline.

This script verifies structural facts (label-free feature files, sealed ledger,
label-blind baseline/probe files, no label tokens in prompt/paraphrase code,
pre-registered thresholds). It cannot prove process intent; the prose audit in
leakage_audit.md interprets these facts along each path.

Outputs: consensus_stress/round7/audit/leakage_audit_evidence.json
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _audit_common as C

OUT = HERE.parent / "leakage_audit_evidence.json"

LABEL_TOKENS = ("gold", "label", "wrong", "consensus_wrong", "outcome", "truth")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def scan_keys(path: Path) -> dict:
    keys: set[str] = set()
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        keys.update(d.keys())
        n += 1
        if n >= 50:
            break
    hits = sorted(k for k in keys if any(t in k.lower() for t in LABEL_TOKENS))
    return {"n_lines_scanned": n, "n_keys": len(keys), "label_token_keys": hits}


def main() -> int:
    ledger = C.load_ledger()
    ev = {
        "protocol": "round7-w1-p0-leakage-audit",
        "status": "read-only static verification; zero new model calls",
        "label_ledger": {
            "status": ledger["status"], "n_items": len(ledger["items"]),
            "item_fields": sorted(ledger["items"][0].keys()),
            "sha256": sha256(C.R3 / "labels_ledger.json"),
        },
        "features_label_free": {},
        "prompt_code": {},
        "paraphrase": {},
        "label_blind_scores": {},
        "thresholds": {},
        "selection": {},
        "hashes": {},
    }

    # 1) preoutcome feature files must not carry label fields
    for mk in ("qwen", "ling"):
        p = C.MODEL_FILES[mk]["features"]
        ev["features_label_free"][mk] = {
            "path": str(p.relative_to(C.CS.parent)),
            "sha256": sha256(p), "scan": scan_keys(p),
        }

    # 2) prompt construction code: no label tokens in messages builder
    src = (C.R3 / "round3_lib.py").read_text(encoding="utf-8")
    prompt_block = src[src.index("def build_messages"):src.index("def run_one_agent_call")]
    hits = [t for t in LABEL_TOKENS if re.search(rf"\b{t}\b", prompt_block, re.IGNORECASE)]
    ev["prompt_code"] = {
        "file": "round3/round3_lib.py",
        "build_messages_label_tokens": hits,
        "note": "gold_label exists in Composite for item bookkeeping only; never enters build_messages",
        "gold_label_in_messages_builder": "gold_label" in hits,
    }
    # features.py must not load labels at all
    feats_src = (C.R3 / "features.py").read_text(encoding="utf-8")
    ev["prompt_code"]["features_py_label_tokens"] = [
        t for t in LABEL_TOKENS if re.search(rf"\b{t}\b", feats_src)
    ]

    # 3) paraphrase generation: prompt has no label tokens; usable stats
    pm = json.loads((C.R3 / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    stats = json.loads((C.R3 / "paraphrase_generation_stats.json").read_text(encoding="utf-8"))
    para_src = src[src.index("PARAPHRASE_PROMPT = "):src.index("def parse_paraphrase_response")]
    ev["paraphrase"] = {
        "prompt_label_tokens": [t for t in LABEL_TOKENS if re.search(rf"\b{t}\b", para_src)],
        "n_units": len(pm),
        "generation_stats": stats,
        "manifest_sha256": sha256(C.R3 / "paraphrase_manifest.json"),
    }

    # 4) label-blind score files (round5 baselines, round6 cost-curve probes)
    for p, name in [
        (C.CS / "round5" / "qwen_baseline_scores_label_blind.jsonl", "round5 qwen baselines"),
        (C.CS / "round5" / "ling_baseline_scores_label_blind.jsonl", "round5 ling baselines"),
        (C.CS / "round6" / "cost_curve" / "label_blind" / "probe_scores_label_blind_qwen.jsonl", "round6 qwen probes"),
        (C.CS / "round6" / "cost_curve" / "label_blind" / "probe_scores_label_blind_ling.jsonl", "round6 ling probes"),
    ]:
        if p.exists():
            ev["label_blind_scores"][name] = {"path": str(p), "sha256": sha256(p), "scan": scan_keys(p)}
        else:
            ev["label_blind_scores"][name] = {"path": str(p), "exists": False}

    # 5) frozen thresholds / gates (from preregistration text + analysis code)
    pre = (C.R3 / "preregistration.md").read_text(encoding="utf-8")
    ev["thresholds"] = {
        "hc_threshold": "agreement >= 0.8 (preregistered, round3 preregistration §5)",
        "hc_in_code": C.HC_THRESHOLD,
        "risk_direction": "RS_q = -BF_q, higher = riskier (frozen before calls; gate2_decision_paper.md)",
        "e2_gate": "AUROC CI lb > 0.5 and point >= 0.60 (preregistered)",
        "risk80_coverage": "coverage = 0.8 (preregistered, phase 4)",
        "prereg_mentions_label_firewall": bool(re.search(r"seal|firewall|frozen before any", pre, re.I)),
        "label_ledger_status_field": ledger["status"],
    }
    # selection code: gold labels used offline for balanced design only
    sel_src = (C.R3 / "prepare_selection.py").read_text(encoding="utf-8")
    ev["selection"] = {
        "label_use_statement": re.search(r'"label_use":\s*"([^"]+)"', sel_src).group(1) if re.search(r'"label_use":\s*"([^"]+)"', sel_src) else None,
        "eligible_filters_label_free": [
            "one pair per page (cr desc, tj desc, case_id)",
            "character_ratio >= 0.85 and token_jaccard >= 0.70",
            "exclude frozen V3.16/V3.16.1 pages and round2 pair_ids",
            "hash ordering by sha256(SALT + page)",
        ],
        "selection_manifest_sha256": sha256(C.R3 / "selection_manifest.json"),
    }

    for p, name in [
        (C.R3 / "artifact_hashes.json", "round3 artifact_hashes.json"),
        (C.R3 / "analysis" / "analysis.json", "round3 analysis.json"),
        (C.R3 / "records.jsonl", "round3 records.jsonl"),
        (C.R4 / "ling_records.jsonl", "round4 ling records"),
    ]:
        if p.exists():
            ev["hashes"][name] = sha256(p)

    OUT.write_text(json.dumps(ev, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(ev, indent=2, sort_keys=True))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
