#!/usr/bin/env python3
"""TARGET_SPEC strict audit (30-item sample, seed 20260914):
E_ind_strict: decision-relevance (expected opposite of item role) + independence vs E_j.
E_pm: decision-irrelevance (majority neutral; <=0.30 support and <=0.30 refute)."""
from __future__ import annotations
import json, random, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))
from relay_client import RelayChatClient, write_json, write_jsonl  # noqa: E402
from audit_ind_evidence import token_jaccard, character_ratio, lcs_token_ratio  # noqa: E402

AUDIT_MODEL = "gpt-6-astra"
SAMPLE_SEED = 20260914
SAMPLE_N = 30

REL_PROMPT = (
    "Does the evidence support the claim: {claim}? Answer exactly yes or no.\nEvidence: {e}"
)
IRR_PROMPT = (
    "For the claim: {claim}\nDoes the following evidence support the claim, refute the claim, "
    "or is it neutral (irrelevant to whether the claim is true)? Answer exactly support, refute, "
    "or neutral.\nEvidence: {e}"
)


def expected_dir(item_role: str) -> str:
    return "no" if item_role == "support" else "yes"


def parse_yn(content: str) -> str | None:
    m = re.search(r"\b(yes|no)\b", content.casefold())
    return m.group(1) if m else None


def parse_3way(content: str) -> str | None:
    m = re.search(r"\b(support|refute|neutral)\b", content.casefold())
    return m.group(1) if m else None


def audit(client, prompt, parse, seed):
    messages = [{"role": "user", "content": prompt}]
    for _ in range(2):
        try:
            r = client.call(messages, seed=seed, model=AUDIT_MODEL, temperature=0.0, max_tokens=16)
        except Exception:
            return None
        ans = parse(r.content)
        if ans is not None:
            return ans
    return None


def main() -> int:
    arts = [json.loads(l) for l in (HERE / "strict_artifacts.jsonl").read_text(encoding="utf-8").splitlines() if l]
    rng = random.Random(SAMPLE_SEED)
    sample = rng.sample([a["item_id"] for a in arts], SAMPLE_N)
    by_item = {a["item_id"]: a for a in arts}
    client = RelayChatClient(HERE / "cache", model=AUDIT_MODEL)
    rows = []
    for idx, it in enumerate(sample):
        a = by_item[it]
        exp = expected_dir(a["item_role"])
        for slot in (0, 1):
            e = a[f"E_ind_strict_{'a' if slot == 0 else 'b'}"]
            rel = audit(client, REL_PROMPT.format(claim=a["claim"], e=e), parse_yn, 78_101 + slot)
            rows.append({
                "item_id": it, "slot": slot, "kind": "E_ind_strict", "expected": exp, "answer": rel,
                "decision_relevant": rel == exp,
                "token_jaccard_vs_Ej": round(token_jaccard(e or "", a["E_j"]), 4),
                "character_ratio_vs_Ej": round(character_ratio(e or "", a["E_j"]), 4),
                "lcs_token_ratio_vs_Ej": round(lcs_token_ratio(e or "", a["E_j"]), 4),
                "text": e, "E_j": a["E_j"], "claim": a["claim"],
            })
        for slot in (0, 1):
            e = a[f"E_pm_{'a' if slot == 0 else 'b'}"]
            way = audit(client, IRR_PROMPT.format(claim=a["claim"], e=e), parse_3way, 78_201 + slot)
            rows.append({"item_id": it, "slot": slot, "kind": "E_pm", "way": way, "text": e,
                         "claim": a["claim"], "E_j": a["E_j"]})
        if (idx + 1) % 10 == 0:
            print(f"[strict-audit] {idx+1}/{len(sample)}", flush=True)
    write_jsonl(HERE / "strict_audit_sample.jsonl", rows)
    ind = [r for r in rows if r["kind"] == "E_ind_strict"]
    pm = [r for r in rows if r["kind"] == "E_pm"]
    rel_rate = sum(1 for r in ind if r["decision_relevant"]) / max(1, len(ind))
    jac = [r["token_jaccard_vs_Ej"] for r in ind]
    cr = [r["character_ratio_vs_Ej"] for r in ind]
    lcs = [r["lcs_token_ratio_vs_Ej"] for r in ind]
    def pct(v, q):
        s = sorted(v); return s[min(len(s)-1, int(q*len(s)))]
    sup = sum(1 for r in pm if r["way"] == "support") / max(1, len(pm))
    ref = sum(1 for r in pm if r["way"] == "refute") / max(1, len(pm))
    neu = sum(1 for r in pm if r["way"] == "neutral") / max(1, len(pm))
    summary = {
        "stage": "strict_audit", "model": AUDIT_MODEL, "sample_seed": SAMPLE_SEED, "sample_n": SAMPLE_N,
        "E_ind_strict": {"n": len(ind), "relevance_rate": round(rel_rate, 4), "gate_ge_0.80": rel_rate >= 0.80,
                         "token_jaccard": {"median": round(pct(jac, .5), 4), "p90": round(pct(jac, .9), 4), "max": round(max(jac), 4)},
                         "character_ratio": {"median": round(pct(cr, .5), 4), "max": round(max(cr), 4)},
                         "lcs_token_ratio": {"max": round(max(lcs), 4)}},
        "E_pm": {"n": len(pm), "support_rate": round(sup, 4), "refute_rate": round(ref, 4),
                 "neutral_rate": round(neu, 4),
                 "gate_support_le_0.30": sup <= 0.30, "gate_refute_le_0.30": ref <= 0.30,
                 "majority_neutral": neu >= 0.5},
        "http_stats": dict(client.stats["http"]), "transport_retries": client.stats["transport_retries"],
        "cache_hits": client.stats["cache_hits"],
    }
    write_json(HERE / "run_summary_strict_audit.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1), flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
