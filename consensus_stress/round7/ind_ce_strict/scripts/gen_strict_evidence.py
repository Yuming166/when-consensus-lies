#!/usr/bin/env python3
"""Round-7 W2b STRICT: generate dual-direction counter-evidence segments + matched
placebo per CLAIM. Generation input = claim text ONLY (no item_id, no polarity, no
gold, no labels_ledger, no evidence_i/j, no original answers). Both directions are
generated in one call so the model never knows which item/direction will be used.
Offline gold assignment happens later in assign_strict.py. No labels read here."""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
sys.path.insert(0, str(HERE / "scripts"))
from relay_client import RelayChatClient, write_json, write_jsonl  # noqa: E402

GEN_MODEL = "gpt-6-astra"
GEN_TEMP = 0.7
GEN_MAX_TOKENS = 300
N_WORKERS = 8
MAX_CONSEC_FAIL = 20
MAX_WORDS_PER_SEGMENT = 70
PROTOCOL = "cs-paper-ind-ce-strict-20260915-round7-w2b"

SYSTEM_DUAL = (
    "You are a careful research assistant building a counter-evidence benchmark. "
    "You produce exactly two short factual evidence segments. "
    "You never include meta-commentary, reasoning, labels, quotes, or anything except "
    "the two formatted lines."
)
USER_DUAL = (
    "Claim: {claim}\n\n"
    "Write exactly two evidence segments about this claim.\n\n"
    "SEGMENT_TRUE - exactly 2 sentences of concrete factual content that, if accurate, "
    "supports the claim being TRUE.\n"
    "SEGMENT_FALSE - exactly 2 sentences of concrete factual content that, if accurate, "
    "supports the claim being FALSE.\n\n"
    "Output exactly two lines, each starting with the marker and a pipe, followed by the "
    "two sentences joined by a space:\n"
    "<T>|sentence1. sentence2.\n"
    "<F>|sentence1. sentence2.\n\n"
    "Hard constraints:\n"
    "- Each segment is exactly 2 sentences and at most 70 words total.\n"
    "- Use concrete facts (names, dates, numbers, attributes), never vague or hedged wording.\n"
    "- Both segments must concern the same subject matter as the claim.\n"
    "- Do not copy or paraphrase the claim wording beyond the necessary subject nouns.\n"
    "- Do not begin sentences with meta-phrases such as \"It is false that\", \"Evidence shows\", "
    "\"This means\", or \"The claim is\".\n"
    "- Do not use the words: claim, evidence, true, false, support, target, conclusion, "
    "label, statement, segment, direction inside the sentences themselves.\n"
    "- No quotes, no explanation, no extra text."
)

SYSTEM_PM = (
    "You are a careful research assistant building a benchmark control condition. "
    "You produce exactly two sentences of factual background content. "
    "You never include meta-commentary, reasoning, labels, quotes, or anything except "
    "the two sentences."
)
USER_PM = (
    "Claim: {claim}\n\n"
    "Write exactly two sentences of factual background content about the subject of the "
    "claim that NEITHER support NOR refute the claim: the content is topically related "
    "but gives no information that helps decide whether the claim is true or false.\n\n"
    "Output exactly one line with the two sentences joined by a space:\n"
    "sentence1. sentence2.\n\n"
    "Hard constraints:\n"
    "- Exactly 2 sentences and at most 70 words total.\n"
    "- Use concrete facts (names, dates, numbers, attributes), never vague or hedged wording.\n"
    "- Topically related to the claim's subject but decision-neutral: a reader cannot tell "
    "from these sentences whether the claim is true or false.\n"
    "- Do not copy or paraphrase the claim wording beyond the necessary subject nouns.\n"
    "- Do not begin sentences with meta-phrases such as \"Evidence shows\", \"This means\", "
    "or \"The claim is\".\n"
    "- Do not use the words: claim, evidence, true, false, support, refute, target, "
    "conclusion, label, statement, sentence inside the sentences themselves.\n"
    "- No quotes, no explanation, no extra text."
)
REPAIR_SUFFIX = (
    "\n\nYour previous output was invalid. Return only the required formatted sentences, "
    "no quotes, no explanation."
)

BANNED_PREFIXES = (
    "it is false that", "evidence shows", "this means", "the claim is", "in reality",
    "the truth is", "contrary", "actually,", "however", "note that", "the evidence",
    "the statement",
)
BANNED_WORDS_DUAL = {"claim", "evidence", "true", "false", "support", "target",
                     "conclusion", "label", "statement", "segment", "direction",
                     "sentence"}
BANNED_WORDS_PM = {"claim", "evidence", "true", "false", "support", "refute", "target",
                   "conclusion", "label", "statement", "sentence"}

_SENT_BOUND = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    parts = [s.strip() for s in _SENT_BOUND.split(text.strip())]
    return [s for s in parts if s]


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def clean_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n?```$", "", t)
    return re.sub(r'^["\']+|["\']+$', "", t.strip())


def validate_segment(sent_text: str, banned: set[str]) -> str | None:
    """Return normalized 2-sentence segment or None."""
    sents = split_sentences(sent_text)
    if len(sents) != 2:
        return None
    out = []
    for s in sents:
        low = s.casefold()
        for bp in BANNED_PREFIXES:
            if low.startswith(bp):
                return None
        ws = words(s)
        if any(w in banned for w in ws):
            return None
        if not (3 <= len(ws) <= MAX_WORDS_PER_SEGMENT):
            return None
        out.append(s)
    return " ".join(out)


def parse_dual(content: str) -> dict[str, str] | None:
    text = clean_fence(content)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    seg: dict[str, str] = {}
    for ln in lines:
        m = re.match(r"^<([TF])>\|?\s*(.+)$", ln, re.IGNORECASE)
        if not m:
            continue
        key = "T" if m.group(1).upper() == "T" else "F"
        seg[key] = m.group(2)
    if set(seg) != {"T", "F"}:
        return None
    t = validate_segment(seg["T"], BANNED_WORDS_DUAL)
    f = validate_segment(seg["F"], BANNED_WORDS_DUAL)
    if t is None or f is None:
        return None
    return {"T": t, "F": f}


def parse_placebo(content: str) -> str | None:
    text = clean_fence(content)
    # take first non-empty line if multiple
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    return validate_segment(lines[0], BANNED_WORDS_PM)


def seed_for(kind: str, pair_id: str) -> int:
    return int(hashlib.sha256(f"ind_ce_strict_{kind}:{pair_id}".encode()).hexdigest(), 16) % (2 ** 31)


def load_claims() -> list[dict]:
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    pair_ids = set(cohort["pairs"])
    claims = []
    for p in sel["pairs"]:
        if p["pair_id"] in pair_ids:
            claims.append({"pair_id": p["pair_id"], "claim": p["claim"]})
    assert len(claims) == 25
    claims.sort(key=lambda c: cohort["pairs"].index(c["pair_id"]))
    return claims


def run_gen(client: RelayChatClient, kind: str, claim: str, pair_id: str) -> dict:
    system = SYSTEM_DUAL if kind == "dual" else SYSTEM_PM
    user = (USER_DUAL if kind == "dual" else USER_PM).format(claim=claim)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    seed = seed_for("dual" if kind == "dual" else "pm", pair_id)
    attempts = []
    parsed = None
    final_error = None
    for attempt in range(2):
        msgs = list(messages)
        if attempt == 1:
            msgs[-1] = dict(msgs[-1])
            msgs[-1]["content"] = msgs[-1]["content"] + REPAIR_SUFFIX
        try:
            result = client.call(msgs, seed=seed, model=GEN_MODEL,
                                 temperature=GEN_TEMP, max_tokens=GEN_MAX_TOKENS)
        except (RuntimeError, ValueError) as e:
            final_error = f"{type(e).__name__}: {e}"
            attempts.append({"transport_error": final_error, "http_status": None,
                             "cache_hit": False})
            continue
        attempt_rec = {"transport_error": None, "http_status": result.http_status,
                       "cache_hit": result.cache_hit, "cache_key": result.cache_key,
                       "model": result.model, "usage": dict(result.usage),
                       "latency_seconds": result.latency_seconds}
        try:
            parsed = parse_dual(result.content) if kind == "dual" else parse_placebo(result.content)
        except Exception as e:
            parsed = None
            attempt_rec["parse_error"] = f"{type(e).__name__}: {e}"
        attempts.append(attempt_rec)
        if parsed is not None:
            final_error = None
            break
        final_error = f"parse failed after {len(attempts)} attempt(s)"
    row = {
        "protocol_version": PROTOCOL,
        "stage": "e_strict_generation",
        "kind": kind, "pair_id": pair_id, "claim": claim,
        "seed": seed, "prompt_log": user,
        "success": parsed is not None,
        "segment_true": parsed.get("T") if isinstance(parsed, dict) else None,
        "segment_false": parsed.get("F") if isinstance(parsed, dict) else None,
        "placebo": parsed if isinstance(parsed, str) else None,
        "attempts": attempts, "final_error": final_error,
    }
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    args = ap.parse_args()
    claims = load_claims()
    print(f"claims: {len(claims)}", flush=True)
    client = RelayChatClient(HERE / "cache", model=GEN_MODEL)
    tasks = [(kind, c["claim"], c["pair_id"])
             for c in claims for kind in ("dual", "pm")]
    expected = len(tasks)
    rows: list[dict] = []
    start = time.monotonic()
    consec = 0
    aborted = False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_gen, client, kind, claim, pid): (pid, kind)
                for kind, claim, pid in tasks}
        for fut in as_completed(futs):
            rec = fut.result()
            rows.append(rec)
            consec = 0 if rec["success"] else consec + 1
            if consec >= MAX_CONSEC_FAIL:
                aborted = True
                for f in futs:
                    f.cancel()
                print(f"ABORT after {consec} consecutive failures at {len(rows)}/{expected}", flush=True)
                break
            if len(rows) % 10 == 0 or len(rows) == expected:
                ok = sum(1 for r in rows if r["success"])
                print(f"[gen] {len(rows)}/{expected} ok={ok} elapsed={time.monotonic()-start:.0f}s", flush=True)
    rows.sort(key=lambda r: (r["pair_id"], r["kind"]))
    write_jsonl(HERE / "e_gen_artifacts.jsonl", rows)
    summary = {
        "stage": "e_strict_generation", "model": GEN_MODEL, "temperature": GEN_TEMP,
        "max_tokens": GEN_MAX_TOKENS, "expected_calls": expected, "records": len(rows),
        "aborted": aborted, "success": sum(1 for r in rows if r["success"]),
        "valid_rate": round(sum(1 for r in rows if r["success"]) / max(1, len(rows)), 4),
        "per_kind": {k: {"n": sum(1 for r in rows if r["kind"] == k),
                         "success": sum(1 for r in rows if r["kind"] == k and r["success"])}
                     for k in ("dual", "pm")},
        "http_stats": dict(client.stats["http"]),
        "transport_retries": client.stats["transport_retries"],
        "cache_hits": client.stats["cache_hits"],
        "models_seen": dict(client.stats["models_seen"]),
        "elapsed_seconds": round(time.monotonic() - start, 2),
        "token_usage": {
            "prompt_tokens": sum(a.get("usage", {}).get("prompt_tokens") or 0 for r in rows for a in r["attempts"]),
            "completion_tokens": sum(a.get("usage", {}).get("completion_tokens") or 0 for r in rows for a in r["attempts"])},
    }
    write_json(HERE / "run_summary_generation.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
