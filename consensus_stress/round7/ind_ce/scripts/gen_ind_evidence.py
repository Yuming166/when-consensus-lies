#!/usr/bin/env python3
"""Round-7 W2: generate independent counter-evidence E_ind_a/E_ind_b per item.
gpt-6-astra temp 0.7 max_tokens 300, direct relay HTTP, concurrency ~10, cache, retry.
Label-blind: direction from item_id suffix; never reads labels_ledger/gold_label."""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
sys.path.insert(0, str(R3))
sys.path.insert(0, str(HERE / "scripts"))
import round3_lib as pl  # noqa: E402
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

# Batch-1 prompt (audit: relevance 0.783/1.0; direction often missed on refute items).
# Replaced by USER_TEMPLATE (V2) below after documented batch-1 audit marginal failure.
USER_TEMPLATE = (  # V2: explicit original polarity + opposite target; adopted for batch 2
    "Claim: {claim}\n\n"
    "Original evidence (its polarity is context only; do NOT copy its wording):\n{evidence_i}\n\n"
    "The original evidence supports the conclusion that the claim is {orig}.\n\n"
    "Construct NEW evidence that supports the OPPOSITE conclusion: the claim is {target}.\n\n"
    "The new evidence must:\n"
    "- be a standalone factual sentence (at most 60 words) that DIRECTLY asserts a fact "
    "consistent with the claim being {target};\n"
    "- be decision-relevant: a reader should be able to tell from the sentence alone that it "
    "bears on whether the claim is {target};\n"
    "- use concrete facts (dates, numbers, names, attributes) rather than vague or hedged wording;\n"
    "- not copy, quote, or paraphrase the wording of the original evidence;\n"
    "- not begin with meta-phrases such as \"It is false that\", \"Evidence shows\", "
    "\"This means\", or \"The claim is\";\n"
    "- not use the words \"claim\", \"evidence\", \"true\", \"false\", \"opposite\", \"target\", "
    "\"conclusion\", or \"label\".\n\n"
    "Output only the sentence."
)
REPAIR_SUFFIX = "\n\nYour previous output was invalid. Return only the sentence, no quotes, no explanation."

BANNED_PREFIXES = (
    "it is false that", "evidence shows", "this means", "the claim is", "in reality",
    "the truth is", "contrary", "actually,", "however", "note that", "the evidence",
)
BANNED_WORDS = {"claim", "evidence", "true", "false", "opposite", "target", "conclusion", "label",
                "statement", "sentence"}


def target_for(item_id: str) -> str:
    if item_id.endswith(":support"):
        return "false"
    if item_id.endswith(":refute"):
        return "true"
    raise ValueError(f"cannot derive target from item_id: {item_id}")


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
    if any(w in BANNED_WORDS for w in words):
        return None
    return sent + "."


def load_composites() -> list[pl.Composite]:
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((R3 / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    pairs = [r for r in sel["pairs"] if f"{r['pair_id']}:support" in set(cohort["items"])]
    assert len(pairs) == 50
    distractors = {r["pair_id"]: pl.Distractor(
        distractor_id=r["distractor_id"], distractor_page=r["distractor_page"],
        evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["distractor_id"]))
        for r in pairs}
    natural = [pl.NaturalPair(
        pair_id=r["pair_id"], case_id=r["case_id"], page=r["page"], claim=r["claim"],
        supports_id=r["supports_id"], refutes_id=r["refutes_id"],
        supports_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["supports_id"]),
        refutes_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == r["refutes_id"]),
        character_ratio=float(r["character_ratio"]), token_jaccard=float(r["token_jaccard"]))
        for r in pairs]
    comps = pl.build_composites(natural, distractors, artifacts)
    by_item = {c.item_id: c for c in comps}
    return [by_item[i] for i in cohort["items"]]


def gen_seed(item_id: str, slot: int) -> int:
    h = int(hashlib.sha256(f"ind_ce_gen:{item_id}".encode()).hexdigest(), 16) % (2 ** 31)
    return h + slot


def run_one(client: RelayChatClient, comp: pl.Composite, slot: int) -> dict:
    item_id = comp.item_id
    target = target_for(item_id)
    orig = "true" if target == "false" else "false"
    user = USER_TEMPLATE.format(claim=comp.claim, evidence_i=comp.evidence, orig=orig, target=target)
    messages = [{"role": "system", "content": SYSTEM_GEN}, {"role": "user", "content": user}]
    seed = gen_seed(item_id, slot)
    attempts = []
    sentence = None
    final_error = None
    repair = False
    for _ in range(2):
        try:
            msgs = list(messages)
            if repair:
                msgs[-1] = dict(msgs[-1])
                msgs[-1]["content"] = msgs[-1]["content"] + REPAIR_SUFFIX
            result = client.call(msgs, seed=seed, model=GEN_MODEL,
                                 temperature=GEN_TEMP, max_tokens=GEN_MAX_TOKENS)
        except (RuntimeError, ValueError) as e:
            final_error = f"{type(e).__name__}: {e}"
            attempts.append({"transport_error": final_error, "http_status": None,
                             "cache_hit": False})
            repair = True
            continue
        attempt = {"transport_error": None, "http_status": result.http_status,
                   "cache_hit": result.cache_hit, "cache_key": result.cache_key,
                   "model": result.model, "usage": dict(result.usage),
                   "latency_seconds": result.latency_seconds}
        try:
            sentence = parse_gen(result.content)
        except Exception as e:
            sentence = None
            attempt["parse_error"] = f"{type(e).__name__}: {e}"
        attempts.append(attempt)
        if sentence is not None:
            final_error = None
            break
        repair = True
        final_error = f"parse failed after {len(attempts)} attempt(s)"
    return {
        "protocol_version": "cs-paper-ind-ce-20260914-round7-w2",
        "stage": "e_ind_generation",
        "item_id": item_id, "pair_id": comp.pair_id,
        "claim": comp.claim,
        "evidence_i": comp.evidence,
        "evidence_j": comp.evidence_opp,
        "target": target,
        "slot": slot, "seed": seed,
        "success": sentence is not None,
        "E_ind": sentence,
        "attempts": attempts, "final_error": final_error,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    args = ap.parse_args()

    comps = load_composites()
    print(f"items: {len(comps)}", flush=True)
    client = RelayChatClient(HERE / "cache", model=GEN_MODEL)
    tasks = [(comp, slot) for comp in comps for slot in (0, 1)]
    expected = len(tasks)
    rows: list[dict] = []
    start = time.monotonic()
    consec = 0
    aborted = False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_one, client, comp, slot): (comp.item_id, slot)
                for comp, slot in tasks}
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
            if len(rows) % 50 == 0 or len(rows) == expected:
                ok = sum(1 for r in rows if r["success"])
                print(f"[gen] {len(rows)}/{expected} ok={ok} elapsed={time.monotonic()-start:.0f}s", flush=True)
    rows.sort(key=lambda r: (r["item_id"], r["slot"]))
    write_jsonl(HERE / "e_ind_artifacts.jsonl", rows)
    summary = {
        "stage": "e_ind_generation", "model": GEN_MODEL, "temperature": GEN_TEMP,
        "max_tokens": GEN_MAX_TOKENS, "expected_calls": expected, "records": len(rows),
        "aborted": aborted, "success": sum(1 for r in rows if r["success"]),
        "valid_rate": round(sum(1 for r in rows if r["success"]) / max(1, len(rows)), 4),
        "http_stats": dict(client.stats["http"]), "transport_retries": client.stats["transport_retries"],
        "cache_hits": client.stats["cache_hits"], "models_seen": dict(client.stats["models_seen"]),
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
