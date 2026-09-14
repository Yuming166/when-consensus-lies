"""Offline Phase-5 matched-budget active-probe pilot on frozen round-3 Qwen features."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
R3 = HERE.parent / "round3"
sys.path.insert(0, str(R3))
import analysis_lib as al  # noqa: E402

CONDITIONS = ("paraphrase", "reverse", "synthetic_reverse", "remove")
SEED = 20_260_913 + 500


def load_merged() -> list[dict]:
    rows = [json.loads(line) for line in
            (R3 / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines() if line]
    ledger = json.loads((R3 / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {row["item_id"]: row["gold_label"] for row in ledger["items"]}
    for row in rows:
        label = gold[row["item_id"]]
        row["gold_label"] = label
        row["gold_yes"] = label == "SUPPORTS"
        row["consensus_wrong"] = int((row["consensus"] == "yes") != row["gold_yes"])
        row["risk_active"] = 1.0 - row["bf_reverse"]
        digest = hashlib.sha256(("round4-fixed-rotation:" + row["item_id"]).encode()).digest()
        condition = CONDITIONS[digest[0] % len(CONDITIONS)]
        row["fixed_condition"] = condition
        if condition == "paraphrase":
            row["risk_fixed"] = 1.0 - row["bf_paraphrase"]
        elif condition == "reverse":
            row["risk_fixed"] = 1.0 - row["bf_reverse"]
        elif condition == "synthetic_reverse":
            row["risk_fixed"] = 1.0 - row["bf_synthetic_reverse"]
        else:
            row["risk_fixed"] = 1.0 - row["rem_flip_rate"]
    return rows


def main() -> None:
    rows = [row for row in load_merged() if row["agreement"] >= al.HC_THRESHOLD]
    active = al.group_bootstrap(rows, "risk_active", seed=SEED + 1)
    fixed = al.group_bootstrap(rows, "risk_fixed", seed=SEED + 2)
    active_risk80 = al.risk_at_80_bootstrap(rows, "risk_active", seed=SEED + 3)
    fixed_risk80 = al.risk_at_80_bootstrap(rows, "risk_fixed", seed=SEED + 4)
    paired_auroc = al.paired_bootstrap_diff(rows, "risk_active", "risk_fixed", seed=SEED + 5)
    paired_risk80 = al.risk_at_80_paired_diff(rows, "risk_active", "risk_fixed", seed=SEED + 6)
    result = {
        "protocol": "cs-round4-phase5-active-probe-offline-20260913",
        "n_hc": len(rows),
        "n_wrong": sum(row["consensus_wrong"] for row in rows),
        "condition_counts": dict(Counter(row["fixed_condition"] for row in rows)),
        "active": {"auroc": active, "risk_at_80": active_risk80},
        "fixed_rotation": {"auroc": fixed, "risk_at_80": fixed_risk80},
        "paired_active_minus_fixed": {"auroc": paired_auroc, "risk_at_80": paired_risk80},
        "gates": {
            "primary_auroc_ci_lb_gt_0": bool(paired_auroc["ci"][0] > 0),
            "secondary_risk80_ci_lb_gt_0": bool(paired_risk80["ci"][0] > 0),
        },
    }
    result["gates"]["all_pass"] = all(result["gates"].values())
    out = HERE / "analysis" / "active_probe_analysis.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
