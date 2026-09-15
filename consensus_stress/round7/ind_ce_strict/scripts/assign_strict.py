#!/usr/bin/env python3
"""Round-7 W2b: OFFLINE gold assignment of strict counter-evidence.

Runs ONLY after e_gen_artifacts.jsonl is complete and hashed. This is the single
label-consuming step: reads round3/labels_ledger.json and maps each item to the
generated segment that OPPOSES its gold (gold=SUPPORTS -> SEGMENT_FALSE,
gold=REFUTES -> SEGMENT_TRUE). Placebo is per-pair. No model calls."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
PROTOCOL = "cs-paper-ind-ce-strict-20260915-round7-w2b"


def main() -> int:
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    ledger = json.loads((R3 / "labels_ledger.json").read_text(encoding="utf-8"))
    gold = {it["item_id"]: it["gold_label"] for it in ledger["items"]}
    gen = {}
    for line in (HERE / "e_gen_artifacts.jsonl").read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        r = json.loads(line)
        gen.setdefault(r["pair_id"], {})[r["kind"]] = r
    out = []
    missing = []
    for it in cohort["items"]:
        pid = ":".join(it.split(":")[:2])
        g = gold.get(it)
        dual = gen.get(pid, {}).get("dual", {})
        pm = gen.get(pid, {}).get("pm", {})
        if (not dual.get("success")) or (not pm.get("success")) or g is None:
            missing.append(it)
            out.append({"item_id": it, "pair_id": pid, "gold_label": g,
                        "success": False, "E_ind_strict": None, "E_pm": None,
                        "direction": None})
            continue
        if g == "SUPPORTS":
            e = dual["segment_false"]; direction = "false"
        elif g == "REFUTES":
            e = dual["segment_true"]; direction = "true"
        else:
            missing.append(it)
            out.append({"item_id": it, "pair_id": pid, "gold_label": g,
                        "success": False, "E_ind_strict": None, "E_pm": None,
                        "direction": None})
            continue
        out.append({
            "protocol_version": PROTOCOL, "stage": "e_ind_strict_assignment",
            "item_id": it, "pair_id": pid, "claim": dual["claim"],
            "gold_label": g,  # label-consuming step (offline, after generation frozen)
            "direction": direction,  # requested direction of the assigned segment
            "E_ind_strict": e, "E_pm": pm["placebo"],
            "segment_true": dual["segment_true"], "segment_false": dual["segment_false"],
            "success": True,
        })
    out.sort(key=lambda r: cohort["items"].index(r["item_id"]))
    (HERE / "e_ind_strict_artifacts.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in out) + "\n",
        encoding="utf-8")
    summary = {
        "stage": "e_ind_strict_assignment", "n_items": len(out),
        "n_success": sum(1 for r in out if r["success"]),
        "n_missing": len(missing), "missing": missing,
        "e_gen_sha256": hashlib.sha256(
            (HERE / "e_gen_artifacts.jsonl").read_bytes()).hexdigest(),
    }
    (HERE / "run_summary_assignment.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
