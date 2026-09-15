#!/usr/bin/env python3
"""Regenerate specific E_ind slots with a stricter no-overlap instruction (max 2 attempts)."""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts")); sys.path.insert(0, str(HERE.parent.parent / "round3"))
from gen_ind_evidence import load_composites, target_for, parse_gen, gen_seed, SYSTEM_GEN, REPAIR_SUFFIX
from relay_client import RelayChatClient

STRICTER_SUFFIX = (
    "\n\nADDITIONAL HARD CONSTRAINT: The new sentence must not reuse any contiguous phrase "
    "of 4 or more words from the original evidence, and must share less than half of its "
    "vocabulary with the original evidence. Rewrite the sentence accordingly."
)

def main() -> int:
    slots = [
        ("5ee3949bc9e77c0008cd002b:18da75e3ad00:refute", 0),
        ("5ee3949bc9e77c0008cd002b:18da75e3ad00:refute", 1),
        ("5ec55991c9e77c000842e01a:34831fd95810:support", 1),
        ("5ece9462c9e77c0008466ce8:756245021f7b:refute", 0),
        ("5ece9462c9e77c0008466ce8:756245021f7b:refute", 1),
    ]
    comps = load_composites()
    by_item = {c.item_id: c for c in comps}
    rows = [json.loads(l) for l in (HERE / "e_ind_artifacts.jsonl").read_text(encoding="utf-8").splitlines() if l]
    client = RelayChatClient(HERE / "cache", model="gpt-6-astra")
    from gen_ind_evidence import USER_TEMPLATE
    n_fixed = 0
    for item_id, slot in slots:
        comp = by_item[item_id]
        target = target_for(item_id)
        orig = "true" if target == "false" else "false"
        user = USER_TEMPLATE.format(claim=comp.claim, evidence_i=comp.evidence, orig=orig, target=target)
        sent = None
        for attempt in range(2):
            msgs = [{"role": "system", "content": SYSTEM_GEN}, {"role": "user", "content": user}]
            if attempt == 1:
                msgs[-1] = dict(msgs[-1]); msgs[-1]["content"] = msgs[-1]["content"] + STRICTER_SUFFIX
            r = client.call(msgs, seed=gen_seed(item_id, slot) + 10_000 + attempt,
                            model="gpt-6-astra", temperature=0.7, max_tokens=300)
            sent = parse_gen(r.content)
            if sent is not None:
                break
        # replace row
        rows = [r for r in rows if not (r["item_id"] == item_id and r["slot"] == slot)]
        rows.append({"protocol_version": "cs-paper-ind-ce-20260914-round7-w2",
                     "stage": "e_ind_generation", "item_id": item_id, "pair_id": comp.pair_id,
                     "claim": comp.claim, "evidence_i": comp.evidence, "evidence_j": comp.evidence_opp,
                     "target": target, "slot": slot, "seed": gen_seed(item_id, slot),
                     "success": sent is not None, "E_ind": sent,
                     "attempts": [{"note": "outlier regeneration, stricter no-overlap"}],
                     "final_error": None if sent else "regen failed",
                     "regen": True})
        n_fixed += 1 if sent is not None else 0
        print(item_id, "slot", slot, "->", "OK" if sent else "FAIL", ":", (sent or "")[:160], flush=True)
    rows.sort(key=lambda r: (r["item_id"], r["slot"]))
    with (HERE / "e_ind_artifacts.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    print("total:", len(rows), "success:", sum(1 for r in rows if r["success"]), "fixed:", n_fixed)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
