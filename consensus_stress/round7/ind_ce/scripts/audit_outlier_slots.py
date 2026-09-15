#!/usr/bin/env python3
"""Re-audit specific (item_id, slot) pairs after outlier regeneration; merge into
audit_sample.jsonl and recompute run_summary_audit.json (same gate logic as audit script)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))
from relay_client import RelayChatClient, write_json, write_jsonl
from audit_ind_evidence import AUDIT_PROMPT, expected_dir, parse_yn, token_jaccard, character_ratio, lcs_token_ratio

SLOTS = [
    ("5ee3949bc9e77c0008cd002b:18da75e3ad00:refute", 0),
    ("5ee3949bc9e77c0008cd002b:18da75e3ad00:refute", 1),
    ("5ec55991c9e77c000842e01a:34831fd95810:support", 1),
    ("5ece9462c9e77c0008466ce8:756245021f7b:refute", 0),
    ("5ece9462c9e77c0008466ce8:756245021f7b:refute", 1),
]

def main() -> int:
    arts = [json.loads(l) for l in (HERE / "e_ind_artifacts.jsonl").read_text(encoding="utf-8").splitlines() if l]
    by_key = {(r["item_id"], r["slot"]): r for r in arts}
    old = [json.loads(l) for l in (HERE / "audit_sample.jsonl").read_text(encoding="utf-8").splitlines() if l]
    client = RelayChatClient(HERE / "cache", model="gpt-6-astra")
    new_rows = []
    for item_id, slot in SLOTS:
        rec = by_key[(item_id, slot)]
        claim = rec["claim"]; e = rec["E_ind"]; ej = rec["evidence_j"]
        messages = [{"role": "user", "content": AUDIT_PROMPT.format(claim=claim, e_ind=e)}]
        answer = None
        for _ in range(2):
            try:
                r = client.call(messages, seed=77_101 + slot, model="gpt-6-astra",
                                temperature=0.0, max_tokens=16)
            except Exception as exc:
                print("transport fail", item_id, slot, exc)
                answer = None
                break
            answer = parse_yn(r.content)
            if answer is not None:
                break
        exp = expected_dir(item_id)
        row = {"item_id": item_id, "pair_id": rec["pair_id"], "slot": slot,
               "E_ind": e, "evidence_j": ej, "claim": claim,
               "expected": exp, "answer": answer,
               "decision_relevant": answer == exp,
               "token_jaccard_vs_Ej": round(token_jaccard(e, ej), 4),
               "character_ratio_vs_Ej": round(character_ratio(e, ej), 4),
               "lcs_token_ratio_vs_Ej": round(lcs_token_ratio(e, ej), 4),
               "attempts": [{"note": "post-regen re-audit"}]}
        new_rows.append(row)
        print(item_id, "slot", slot, "rel:", row["decision_relevant"], "jacc:", row["token_jaccard_vs_Ej"],
              "char:", row["character_ratio_vs_Ej"], "lcs:", row["lcs_token_ratio_vs_Ej"], flush=True)
    # merge
    merged = [r for r in old if (r["item_id"], r["slot"]) not in set(SLOTS)] + new_rows
    merged.sort(key=lambda r: (r["item_id"], r["slot"]))
    write_jsonl(HERE / "audit_sample.jsonl", merged)
    # recompute summary
    out = merged
    rel_rate = sum(1 for r in out if r["decision_relevant"]) / max(1, len(out))
    jac = [r["token_jaccard_vs_Ej"] for r in out]
    cr = [r["character_ratio_vs_Ej"] for r in out]
    lcs = [r["lcs_token_ratio_vs_Ej"] for r in out]
    def pct(vals, q):
        s = sorted(vals); return s[min(len(s)-1, int(q*len(s)))]
    overlap_pass = (pct(jac,0.5)<=0.55 and pct(jac,0.9)<=0.70 and max(jac)<=0.80
                    and pct(cr,0.5)<=0.75 and max(lcs)<0.75)
    summary = {"stage": "e_ind_audit", "model": "gpt-6-astra", "temperature": 0.0,
               "audit_sample_seed": 20260914, "audit_sample_n": 30,
               "n_items": len({r["item_id"] for r in out}), "n_sentences": len(out),
               "decision_relevant": {"n": len(out), "rate": round(rel_rate, 4),
                                     "gate_ge_0.80": rel_rate >= 0.80},
               "independence_vs_Ej": {
                   "token_jaccard": {"median": round(pct(jac,0.5),4), "p90": round(pct(jac,0.9),4), "max": round(max(jac),4)},
                   "character_ratio": {"median": round(pct(cr,0.5),4), "max": round(max(cr),4)},
                   "lcs_token_ratio": {"max": round(max(lcs),4)},
                   "gates": {"token_jaccard": {"median": 0.55, "p90": 0.70, "max": 0.80},
                             "character_ratio": {"median": 0.75}, "lcs_token_ratio": {"max": 0.75}},
                   "pass": overlap_pass},
               "note": "5 outlier slots re-audited after stricter regeneration; merged into sample",
               "http_stats": dict(client.stats["http"]), "transport_retries": client.stats["transport_retries"],
               "cache_hits": client.stats["cache_hits"]}
    write_json(HERE / "run_summary_audit.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
