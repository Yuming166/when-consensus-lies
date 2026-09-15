#!/usr/bin/env python3
"""Round-7 W2: audit 30-item deterministic sample of E_ind (decision-relevance + independence).
Label-blind: expected direction from item_id suffix; no labels_ledger/gold_label read."""
from __future__ import annotations
import argparse, json, random, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))
from relay_client import RelayChatClient, write_json, write_jsonl  # noqa: E402

AUDIT_MODEL = "gpt-6-astra"
AUDIT_TEMP = 0.0
AUDIT_MAX_TOKENS = 16
AUDIT_SAMPLE_SEED = 20260914
AUDIT_SAMPLE_N = 30
RELEVANCE_MIN = 0.80
OVERLAP = {"token_jaccard": {"median": 0.55, "p90": 0.70, "max": 0.80},
           "character_ratio": {"median": 0.75},
           "lcs_token_ratio": {"max": 0.75}}

AUDIT_PROMPT = (
    "Does the evidence support the claim: {claim}? "
    "Answer exactly yes or no.\nEvidence: {e_ind}"
)


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def token_jaccard(a: str, b: str) -> float:
    ta, tb = set(tokens(a)), set(tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def character_ratio(a: str, b: str) -> float:
    import difflib
    return difflib.SequenceMatcher(None, re.sub(r"\s+", " ", a).strip().casefold(),
                                   re.sub(r"\s+", " ", b).strip().casefold()).ratio()


def lcs_token_ratio(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    m, n = len(ta), len(tb)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        row, prev = dp[i], dp[i - 1]
        for j in range(1, n + 1):
            row[j] = prev[j - 1] + 1 if ta[i - 1] == tb[j - 1] else max(prev[j], row[j - 1])
    return dp[m][n] / min(m, n)


def expected_dir(item_id: str) -> str:
    return "no" if item_id.endswith(":support") else "yes"


def parse_yn(content: str) -> str | None:
    m = re.search(r"\b(yes|no)\b", content.casefold())
    return m.group(1) if m else None


def run_one(client: RelayChatClient, rec: dict, slot: int) -> dict:
    item_id = rec["item_id"]
    e_ind = rec["E_ind"] if slot == 0 else rec["E_ind_b"]
    claim = rec["claim"]
    messages = [{"role": "user", "content": AUDIT_PROMPT.format(claim=claim, e_ind=e_ind)}]
    attempts = []
    answer = None
    for _ in range(2):
        try:
            result = client.call(messages, seed=77_101 + slot, model=AUDIT_MODEL,
                                 temperature=AUDIT_TEMP, max_tokens=AUDIT_MAX_TOKENS)
        except (RuntimeError, ValueError) as e:
            attempts.append({"transport_error": f"{type(e).__name__}: {e}",
                             "http_status": None, "cache_hit": False})
            continue
        attempt = {"transport_error": None, "http_status": result.http_status,
                   "cache_hit": result.cache_hit, "cache_key": result.cache_key,
                   "model": result.model, "usage": dict(result.usage)}
        answer = parse_yn(result.content)
        attempts.append(attempt)
        if answer is not None:
            break
    exp = expected_dir(item_id)
    ej = rec["evidence_j"]
    e = e_ind if e_ind is not None else ""
    return {
        "item_id": item_id, "pair_id": rec["pair_id"], "slot": slot,
        "E_ind": e, "evidence_j": ej, "claim": claim,
        "expected": exp, "answer": answer,
        "decision_relevant": answer == exp,
        "token_jaccard_vs_Ej": round(token_jaccard(e, ej), 4),
        "character_ratio_vs_Ej": round(character_ratio(e, ej), 4),
        "lcs_token_ratio_vs_Ej": round(lcs_token_ratio(e, ej), 4),
        "attempts": attempts,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    rows = [json.loads(l) for l in (HERE / "e_ind_artifacts.jsonl").read_text(encoding="utf-8").splitlines() if l]
    by_item = {r["item_id"]: r for r in rows if r["slot"] == 0}
    item_ids = sorted(by_item)
    rng = random.Random(AUDIT_SAMPLE_SEED)
    sample = rng.sample(item_ids, AUDIT_SAMPLE_N)
    print(f"full cohort items={len(item_ids)} audit sample={len(sample)}", flush=True)

    client = RelayChatClient(HERE / "cache", model=AUDIT_MODEL)
    out: list[dict] = []
    for idx, it in enumerate(sample):
        rec = by_item[it]
        for slot in (0, 1):
            if slot == 1 and rec.get("E_ind_b") is None:
                rec["E_ind_b"] = next((r["E_ind"] for r in rows
                                       if r["item_id"] == it and r["slot"] == 1), None)
            out.append(run_one(client, rec, slot))
        if (idx + 1) % 10 == 0 or idx == len(sample) - 1:
            print(f"[audit] {idx+1}/{len(sample)} done", flush=True)
    write_jsonl(HERE / "audit_sample.jsonl", out)

    rel = [r for r in out if r["decision_relevant"] is not None]
    relevant_rate = sum(1 for r in out if r["decision_relevant"]) / max(1, len(out))
    jac = [r["token_jaccard_vs_Ej"] for r in out]
    cr = [r["character_ratio_vs_Ej"] for r in out]
    lcs = [r["lcs_token_ratio_vs_Ej"] for r in out]

    def pct(vals, q):
        s = sorted(vals)
        return s[min(len(s) - 1, int(q * len(s)))]

    overlap_pass = (pct(jac, 0.5) <= OVERLAP["token_jaccard"]["median"]
                    and pct(jac, 0.9) <= OVERLAP["token_jaccard"]["p90"]
                    and max(jac) <= OVERLAP["token_jaccard"]["max"]
                    and pct(cr, 0.5) <= OVERLAP["character_ratio"]["median"]
                    and max(lcs) <= OVERLAP["lcs_token_ratio"]["max"])
    summary = {
        "stage": "e_ind_audit", "model": AUDIT_MODEL, "temperature": AUDIT_TEMP,
        "audit_sample_seed": AUDIT_SAMPLE_SEED, "audit_sample_n": AUDIT_SAMPLE_N,
        "n_items": len(sample), "n_sentences": len(out),
        "decision_relevant": {
            "n": len(out), "rate": round(relevant_rate, 4),
            "gate_ge_0.80": relevant_rate >= RELEVANCE_MIN,
        },
        "independence_vs_Ej": {
            "token_jaccard": {"median": round(pct(jac, 0.5), 4), "p90": round(pct(jac, 0.9), 4),
                              "max": round(max(jac), 4)},
            "character_ratio": {"median": round(pct(cr, 0.5), 4), "max": round(max(cr), 4)},
            "lcs_token_ratio": {"max": round(max(lcs), 4)},
            "gates": OVERLAP,
            "pass": overlap_pass,
        },
        "http_stats": dict(client.stats["http"]), "transport_retries": client.stats["transport_retries"],
        "cache_hits": client.stats["cache_hits"],
    }
    write_json(HERE / "run_summary_audit.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
