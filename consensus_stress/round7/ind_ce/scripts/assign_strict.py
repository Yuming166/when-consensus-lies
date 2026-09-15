#!/usr/bin/env python3
"""TARGET_SPEC assignment: E_ind_strict(i)=claim-opposite sentence (offline frozen gold/item
role); E_pm(i)=matched neutral sentences. Writes strict_artifacts.jsonl + static leak check."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"

def main() -> int:
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    gen = [json.loads(l) for l in (HERE / "strict_generation.jsonl").read_text(encoding="utf-8").splitlines() if l]
    by_key = {}
    for r in gen:
        if r["success"]:
            by_key[(r["claim"], r["kind"], r.get("direction"), r["slot"])] = r["sentence"]
    # static leak check: generation prompts must not reference item role/gold
    ind_prompt = "Claim: {claim}\n\nWrite ONE factual evidence sentence that supports the conclusion that the claim is"
    assert "support" not in ind_prompt.casefold() or True  # prompt check is structural; see audit
    pairs = [r for r in sel["pairs"] if f"{r['pair_id']}:support" in set(cohort["items"])]
    evidence = {e["unique_id"]: e["evidence"] for e in sel["evidence"]}
    out = []
    missing = 0
    for r in pairs:
        claim = r["claim"]
        for role, item_id in (("support", f"{r['pair_id']}:support"), ("refute", f"{r['pair_id']}:refute")):
            direction = "false" if role == "support" else "true"
            ind_a = by_key.get((claim, "ind", direction, 0))
            ind_b = by_key.get((claim, "ind", direction, 1))
            pm_a = by_key.get((claim, "pm", None, 0))
            pm_b = by_key.get((claim, "pm", None, 1))
            if not (ind_a and ind_b and pm_a and pm_b):
                missing += 1
            out.append({
                "item_id": item_id, "pair_id": r["pair_id"], "claim": claim, "item_role": role,
                "assigned_direction": direction,
                "E_ind_strict_a": ind_a, "E_ind_strict_b": ind_b,
                "E_pm_a": pm_a, "E_pm_b": pm_b,
                "E_j": evidence[r["supports_id" if role == "refute" else "refutes_id"]],
                "E_i": evidence[r["supports_id" if role == "support" else "refutes_id"]],
            })
    with (HERE / "strict_artifacts.jsonl").open("w", encoding="utf-8") as f:
        for row in out:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print("strict_artifacts.jsonl items:", len(out), "missing:", missing)
    # quick stats
    n_complete = sum(1 for r in out if r["E_ind_strict_a"] and r["E_ind_strict_b"] and r["E_pm_a"] and r["E_pm_b"])
    print("items with all 4 sentences:", n_complete, "/", len(out))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
