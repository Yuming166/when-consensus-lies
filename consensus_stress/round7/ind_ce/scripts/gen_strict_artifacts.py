#!/usr/bin/env python3
"""TARGET_SPEC strict generation: claim-only dual-direction E_ind_strict + matched E_pm.
Item-blind generation (claim text + direction only); offline gold-based assignment later.
No item role / item id / original evidence / gold in any generation prompt."""
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
N_WORKERS = 10
MAX_CONSEC_FAIL = 20

SYSTEM_GEN = (
    "You are a careful research assistant building a counter-evidence benchmark. "
    "You produce exactly one short factual evidence sentence. "
    "You never include meta-commentary, reasoning, labels, quotes, or anything except the sentence."
)

IND_USER = (
    "Claim: {claim}\n\n"
    "Write ONE factual evidence sentence that supports the conclusion that the claim is "
    "{direction} ({direction} = the claim holds / does not hold).\n\n"
    "Requirements:\n"
    "- A standalone factual sentence (at most 60 words) that directly bears on whether the "
    "claim is {direction}.\n"
    "- Use concrete facts (dates, numbers, names, attributes) rather than vague wording.\n"
    "- Do not copy the claim's wording verbatim.\n"
    "- Do not begin with meta-phrases such as \"It is false that\", \"Evidence shows\", "
    "\"This means\", or \"The claim is\".\n"
    "- Do not use the words \"claim\", \"evidence\", \"true\", \"false\", \"opposite\", "
    "\"target\", \"conclusion\", or \"label\".\n"
    "- Output only the sentence."
)

PM_USER = (
    "Claim: {claim}\n\n"
    "Write ONE neutral factual sentence about the same subject/topic as the claim, similar "
    "in length, that NEITHER supports NOR refutes the claim.\n\n"
    "Requirements:\n"
    "- The sentence must be about the same subject but must NOT address the claim's assertion "
    "(do not confirm or contradict it).\n"
    "- Use concrete facts (dates, numbers, names, attributes) where possible.\n"
    "- Do not copy the claim's wording verbatim.\n"
    "- Do not begin with meta-phrases such as \"It is false that\", \"Evidence shows\", "
    "\"This means\", or \"The claim is\".\n"
    "- Do not use the words \"claim\", \"evidence\", \"true\", \"false\", \"opposite\", "
    "\"target\", \"conclusion\", \"label\", \"neutral\", or \"support\".\n"
    "- Output only the sentence."
)

BANNED_PREFIXES = (
    "it is false that", "evidence shows", "this means", "the claim is", "in reality",
    "the truth is", "contrary", "actually,", "however", "note that", "the evidence",
)


def parse_gen(content: str) -> str | None:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    text = re.sub(r'^["\']+|["\']+$', "", text.strip())
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    sent = lines[0].rstrip(".")
    low = sent.casefold()
    for bp in BANNED_PREFIXES:
        if low.startswith(bp):
            return None
    words = re.findall(r"[a-z0-9]+", low)
    if not (5 <= len(words) <= 60):
        return None
    return sent + "."


def seed_for(claim: str, kind: str, direction: str, slot: int) -> int:
    h = int(hashlib.sha256(f"strict:{claim}:{kind}:{direction}:{slot}".encode()).hexdigest(), 16)
    return h % (2 ** 31)


def load_claims() -> list[tuple[str, list[str]]]:
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    pairs = [r for r in sel["pairs"] if f"{r['pair_id']}:support" in set(cohort["items"])]
    by_claim: dict[str, list[str]] = {}
    for r in pairs:
        by_claim.setdefault(r["claim"], []).append(f"{r['pair_id']}:support")
        by_claim.setdefault(r["claim"], []).append(f"{r['pair_id']}:refute")
    return sorted(by_claim.items())


def run_one(client: RelayChatClient, claim: str, kind: str, direction: str, slot: int) -> dict:
    if kind == "ind":
        user = IND_USER.format(claim=claim, direction=direction)
    else:
        user = PM_USER.format(claim=claim)
    seed = seed_for(claim, kind, direction, slot)
    messages = [{"role": "system", "content": SYSTEM_GEN}, {"role": "user", "content": user}]
    attempts = []
    sentence = None
    final_error = None
    for _ in range(2):
        try:
            result = client.call(messages, seed=seed, model=GEN_MODEL,
                                 temperature=GEN_TEMP, max_tokens=GEN_MAX_TOKENS)
        except (RuntimeError, ValueError) as e:
            final_error = f"{type(e).__name__}: {e}"
            attempts.append({"transport_error": final_error, "http_status": None, "cache_hit": False})
            continue
        attempt = {"transport_error": None, "http_status": result.http_status,
                   "cache_hit": result.cache_hit, "cache_key": result.cache_key,
                   "model": result.model, "usage": dict(result.usage)}
        sentence = parse_gen(result.content)
        attempts.append(attempt)
        if sentence is not None:
            final_error = None
            break
        final_error = "parse failed"
    return {"kind": kind, "claim": claim, "direction": direction if kind == "ind" else None,
            "slot": slot, "seed": seed, "success": sentence is not None,
            "sentence": sentence, "attempts": attempts, "final_error": final_error}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    args = ap.parse_args()
    claims = load_claims()
    print(f"claims: {len(claims)}", flush=True)
    tasks = []
    for claim, _items in claims:
        for d in ("true", "false"):
            for slot in (0, 1):
                tasks.append((claim, "ind", d, slot))
        for slot in (0, 1):
            tasks.append((claim, "pm", None, slot))
    expected = len(tasks)
    print(f"tasks: {expected} (ind 4/claim + pm 2/claim)", flush=True)
    client = RelayChatClient(HERE / "cache", model=GEN_MODEL)
    rows: list[dict] = []
    start = time.monotonic()
    consec = 0
    aborted = False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_one, client, c, k, d, s): None for c, k, d, s in tasks}
        for fut in as_completed(futs):
            rec = fut.result()
            rows.append(rec)
            consec = 0 if rec["success"] else consec + 1
            if consec >= MAX_CONSEC_FAIL:
                aborted = True
                for f in futs:
                    f.cancel()
                print(f"ABORT after {consec} failures at {len(rows)}/{expected}", flush=True)
                break
            if len(rows) % 50 == 0 or len(rows) == expected:
                ok = sum(1 for r in rows if r["success"])
                print(f"[strict-gen] {len(rows)}/{expected} ok={ok} elapsed={time.monotonic()-start:.0f}s", flush=True)
    rows.sort(key=lambda r: (r["claim"], r["kind"], r.get("direction") or "", r["slot"]))
    write_jsonl(HERE / "strict_generation.jsonl", rows)
    summary = {"stage": "strict_generation", "model": GEN_MODEL, "temperature": GEN_TEMP,
               "expected_calls": expected, "records": len(rows), "aborted": aborted,
               "success": sum(1 for r in rows if r["success"]),
               "valid_rate": round(sum(1 for r in rows if r["success"]) / max(1, len(rows)), 4),
               "http_stats": dict(client.stats["http"]), "transport_retries": client.stats["transport_retries"],
               "cache_hits": client.stats["cache_hits"], "elapsed_seconds": round(time.monotonic() - start, 2)}
    write_json(HERE / "run_summary_strict_generation.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
