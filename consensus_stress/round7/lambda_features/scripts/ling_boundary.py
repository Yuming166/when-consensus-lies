#!/usr/bin/env python3
"""W4 (round7): Ling-3.0-tiny boundary for lambda-curve reducibility.

No Ling phase-3 lambda records exist (round3 Ling attempt failed the pipeline gate;
round4 'cs-paper-ling-adapted-20260913' covered only the main-cohort conditions:
original/paraphrase/reverse/remove/synthetic_reverse, no lambda grid). Therefore
per-item Ling lambda stress features CANNOT be built and Ling lambda-curve
reducibility is NOT EVALUABLE (zero new calls allowed).

For context only, this script reports the discrete-axis AUROCs (rev_flip_rate,
RS_q/BF_q, R_sym) on the SAME 120-pair subset from the frozen Ling preoutcome
features, so the reader sees what Ling does have vs does not have. All numbers
here are 120-pair-subset scope and post-hoc/exploratory.

Outputs: ling_boundary_results.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

CS = Path(__file__).resolve().parents[3]
FROZEN = CS / "benchmark" / "frozen" / "vitaminc"
HERE = Path(__file__).resolve().parent.parent
R3 = CS / "round3"
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))
import analysis_lib as al

SEED_BASE = 20_260_913
OFFSET_START = 400
HC_THRESHOLD = 0.8


def main():
    rows = [json.loads(l) for l in (FROZEN / "ling_preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if l]
    ledger = json.loads((FROZEN / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    sub_pairs = set(json.loads(l)["pair_id"] for l in (HERE / "features_phase3_lambda.jsonl").read_text(encoding="utf-8").splitlines() if l)
    sub = []
    for r in rows:
        if r["pair_id"] not in sub_pairs:
            continue
        r["gold_label"] = gold[r["item_id"]]
        r["consensus_wrong"] = int((r["consensus"] == "yes") != (r["gold_label"] == "SUPPORTS"))
        r["risk_rev_axis"] = -r["rev_flip_rate"]
        r["risk_bf_q"] = -r["bf_q"]
        sub.append(r)
    hc = [r for r in sub if r["agreement"] >= HC_THRESHOLD]

    offset = OFFSET_START
    res = {
        "protocol": "round7-W4-ling-boundary",
        "scope": "frozen Ling-3.0-tiny features (round4 adapted protocol), same 120-pair "
                 "phase-3 subset; HC agreement>=0.8",
        "status": "exploratory / post-hoc; context only",
        "lambda_records_available": False,
        "note": "No Ling phase-3 lambda records exist; Ling per-item lambda stress "
                "features and lambda-curve reducibility are NOT EVALUABLE.",
        "hc": {"n_items": len(hc), "n_pairs": len({r["pair_id"] for r in hc}),
               "wrong": sum(r["consensus_wrong"] for r in hc)},
        "baselines_auroc": {},
    }
    for key, risk_key, name in (("rev_flip_rate", "risk_rev_axis", "binary reverse axis (rev_flip_rate)"),
                                ("bf_q", "risk_bf_q", "RS_q/BF_q (= -bf_q)"),
                                ("R_sym", "R_sym", "R_sym (reference)")):
        res["baselines_auroc"][key] = {
            "name": name,
            "auroc": al.group_bootstrap(hc, risk_key, seed=SEED_BASE + offset),
        }
        offset += 1
    out = HERE / "ling_boundary_results.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
