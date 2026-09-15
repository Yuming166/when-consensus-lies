#!/usr/bin/env python3
"""Round-7 W2b STRICT audit: 30 items (first 15 pairs), label-blind.
1) direction-compliance (decision-relevance) of both generated segments;
2) independence vs pair evidences (token jaccard / char ratio / LCS, max over both);
3) generation-input cleanliness from logged prompts;
4) placebo format match + decision-irrelevance.
No gold read. No item polarity read (audit covers both segments regardless of
assignment)."""
from __future__ import annotations
import json, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
sys.path.insert(0, str(HERE / "scripts"))
from relay_client import RelayChatClient, write_json, write_jsonl  # noqa: E402

AUDIT_MODEL = "gpt-6-astra"
AUDIT_TEMP = 0.0
AUDIT_MAX_TOKENS = 16
AUDIT_SEED_BASE = 99101
AUDIT_N_ITEMS = 30
RELEVANCE_MIN = 0.80
PLACEBO_IRRELEVANCE_MIN = 0.80
OVERLAP = {
    "token_jaccard": {"median": 0.40, "p90": 0.55, "max": 0.70},
    "character_ratio": {"median": 0.50, "max": 0.70},
    "lcs_token_ratio": {"max": 0.65},
}

PROMPT_T = ("Does the evidence support the claim being TRUE? Answer exactly yes or no.\n"
            "Claim: {claim}\nEvidence: {text}")
PROMPT_F = ("Does the evidence support the claim being FALSE? Answer exactly yes or no.\n"
            "Claim: {claim}\nEvidence: {text}")
PROMPT_PM = ("Does this text bear on the truth of the claim in EITHER direction "
             "(supporting or refuting it)? Answer exactly yes or no.\n"
             "Claim: {claim}\nText: {text}")


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def token_jaccard(a: str, b: str) -> float:
    ta, tb = set(tokens(a)), set(tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def character_ratio(a: str, b: str) -> float:
    import difflib
    return difflib.SequenceMatcher(
        None, re.sub(r"\s+", " ", a).strip().casefold(),
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


def parse_yn(content: str) -> str | None:
    m = re.search(r"\b(yes|no)\b", content.casefold())
    return m.group(1) if m else None


_SENT_BOUND = re.compile(r"(?<=[.!?])\s+")


def sent_count(text: str) -> int:
    return len([s for s in _SENT_BOUND.split(text.strip()) if s.strip()])


def load_data():
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    ev_by_id = {e["unique_id"]: e["evidence"] for e in sel["evidence"]}
    pairs = {p["pair_id"]: p for p in sel["pairs"] if p["pair_id"] in set(cohort["pairs"])}
    assigned = [json.loads(l) for l in
                (HERE / "e_ind_strict_artifacts.jsonl").read_text(encoding="utf-8").splitlines() if l]
    gen = {}
    for line in (HERE / "e_gen_artifacts.jsonl").read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        r = json.loads(line)
        gen.setdefault(r["pair_id"], {})[r["kind"]] = r
    return cohort, ev_by_id, pairs, assigned, gen


def run_judge(client, prompt: str, seed: int) -> dict:
    attempts = []
    ans = None
    for _ in range(2):
        try:
            r = client.call([{"role": "user", "content": prompt}], seed=seed,
                            model=AUDIT_MODEL, temperature=AUDIT_TEMP,
                            max_tokens=AUDIT_MAX_TOKENS)
        except (RuntimeError, ValueError) as e:
            attempts.append({"transport_error": f"{type(e).__name__}: {e}",
                             "http_status": None, "cache_hit": False})
            continue
        attempt = {"transport_error": None, "http_status": r.http_status,
                   "cache_hit": r.cache_hit, "cache_key": r.cache_key,
                   "model": r.model, "usage": dict(r.usage)}
        ans = parse_yn(r.content)
        attempts.append(attempt)
        if ans is not None:
            break
    return {"answer": ans, "attempts": attempts}


def main() -> int:
    cohort, ev_by_id, pairs, assigned, gen = load_data()
    items = [r for r in assigned if r["success"]]
    items = items[:AUDIT_N_ITEMS]
    items_index = {r["item_id"]: i for i, r in enumerate(items)}
    print(f"audit items: {len(items)}", flush=True)
    client = RelayChatClient(HERE / "cache", model=AUDIT_MODEL)
    def work(rec):
        it, pid = rec["item_id"], rec["pair_id"]
        p = pairs[pid]
        evs = [ev_by_id[p["supports_id"]], ev_by_id[p["refutes_id"]]]
        seg_t, seg_f = rec["segment_true"], rec["segment_false"]
        e_strict, e_pm = rec["E_ind_strict"], rec["E_pm"]
        k = items_index[rec["item_id"]] * 3
        jt = run_judge(client, PROMPT_T.format(claim=rec["claim"], text=seg_t), AUDIT_SEED_BASE + k)
        jf = run_judge(client, PROMPT_F.format(claim=rec["claim"], text=seg_f), AUDIT_SEED_BASE + k + 1)
        jp = run_judge(client, PROMPT_PM.format(claim=rec["claim"], text=e_pm), AUDIT_SEED_BASE + k + 2)
        stats = {s: max(fn(e_strict, ev) for ev in evs)
                 for s, fn in (("token_jaccard", token_jaccard),
                               ("character_ratio", character_ratio),
                               ("lcs_token_ratio", lcs_token_ratio))}
        gdual = gen.get(pid, {}).get("dual", {})
        gpm = gen.get(pid, {}).get("pm", {})
        prompts = [gdual.get("prompt_log", ""), gpm.get("prompt_log", "")]
        from gen_strict_evidence import USER_DUAL, USER_PM
        tpl_ok = (prompts[0] == USER_DUAL.format(claim=rec["claim"])
                  and prompts[1] == USER_PM.format(claim=rec["claim"]))
        no_id = all(it not in pr and pid not in pr for pr in prompts)
        no_polarity = all(":support" not in pr and ":refute" not in pr
                          and "SUPPORTS" not in pr and "REFUTES" not in pr
                          and "gold" not in pr.casefold() for pr in prompts)
        no_evidence = all(ev not in pr for pr in prompts for ev in evs)
        input_clean = bool(tpl_ok and no_id and no_polarity and no_evidence)
        pm_sents = sent_count(e_pm)
        strict_words = len(tokens(e_strict))
        pm_words = len(tokens(e_pm))
        fmt_ok = (pm_sents == 2 and 0.5 <= pm_words / max(1, strict_words) <= 2.0)
        return {
            "item_id": it, "pair_id": pid, "claim": rec["claim"],
            "segment_true": seg_t, "segment_false": seg_f,
            "E_ind_strict": e_strict, "E_pm": e_pm,
            "judge_T_answers": jt["answer"], "judge_F_answers": jf["answer"],
            "judge_pm_irrelevant": jp["answer"] == "no",
            "direction_compliance_T": jt["answer"] == "yes",
            "direction_compliance_F": jf["answer"] == "yes",
            "overlap_max_vs_pair_evidences": stats,
            "input_clean": input_clean,
            "placebo_format_ok": fmt_ok,
            "placebo_sentences": pm_sents, "e_strict_words": strict_words,
            "e_pm_words": pm_words,
            "attempts": {"T": jt["attempts"], "F": jf["attempts"], "PM": jp["attempts"]},
        }
    out = []
    done = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(work, rec): rec for rec in items}
        for fut in as_completed(futs):
            out.append(fut.result())
            done += 1
            if done % 10 == 0 or done == len(items):
                print(f"[audit] {done}/{len(items)} done", flush=True)
    out.sort(key=lambda r: items_index[r["item_id"]])
    write_jsonl(HERE / "audit_sample.jsonl", out)

    n = len(out)
    comp = [r for r in out if r["judge_T_answers"] is not None and r["judge_F_answers"] is not None]
    rel_rate = (sum(1 for r in comp if r["direction_compliance_T"]) +
                sum(1 for r in comp if r["direction_compliance_F"])) / max(1, 2 * len(comp))
    pm_irr = sum(1 for r in out if r["judge_pm_irrelevant"]) / max(1, n)
    fmt_rate = sum(1 for r in out if r["placebo_format_ok"]) / max(1, n)
    input_clean_all = all(r["input_clean"] for r in out)

    def pct(vals, q):
        s = sorted(vals)
        return s[min(len(s) - 1, int(q * len(s)))]

    jac = [r["overlap_max_vs_pair_evidences"]["token_jaccard"] for r in out]
    cr = [r["overlap_max_vs_pair_evidences"]["character_ratio"] for r in out]
    lcs = [r["overlap_max_vs_pair_evidences"]["lcs_token_ratio"] for r in out]
    overlap_pass = (
        pct(jac, 0.5) <= OVERLAP["token_jaccard"]["median"]
        and pct(jac, 0.9) <= OVERLAP["token_jaccard"]["p90"]
        and max(jac) <= OVERLAP["token_jaccard"]["max"]
        and pct(cr, 0.5) <= OVERLAP["character_ratio"]["median"]
        and max(cr) <= OVERLAP["character_ratio"]["max"]
        and max(lcs) <= OVERLAP["lcs_token_ratio"]["max"])
    summary = {
        "stage": "e_ind_strict_audit", "model": AUDIT_MODEL, "temperature": AUDIT_TEMP,
        "audit_n_items": n, "audit_n_judgments": len(comp) * 2,
        "direction_compliance_rate": round(rel_rate, 4),
        "gate_relevance_ge_0.80": rel_rate >= RELEVANCE_MIN,
        "placebo_irrelevance_rate": round(pm_irr, 4),
        "gate_placebo_irrelevance_ge_0.80": pm_irr >= PLACEBO_IRRELEVANCE_MIN,
        "placebo_format_ok_rate": round(fmt_rate, 4),
        "generation_input_clean": input_clean_all,
        "independence_vs_pair_evidences_max": {
            "token_jaccard": {"median": round(pct(jac, 0.5), 4), "p90": round(pct(jac, 0.9), 4),
                              "max": round(max(jac), 4)},
            "character_ratio": {"median": round(pct(cr, 0.5), 4), "max": round(max(cr), 4)},
            "lcs_token_ratio": {"max": round(max(lcs), 4)},
            "gates": OVERLAP, "pass": overlap_pass,
        },
        "http_stats": dict(client.stats["http"]),
        "transport_retries": client.stats["transport_retries"],
        "cache_hits": client.stats["cache_hits"],
    }
    write_json(HERE / "run_summary_audit.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
