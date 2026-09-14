"""Round-6 Agent D: relay GPT-class single-point run (smoke 20 + formal 100 items).

Reuses Round-3 composites/views/personas/partitions and Round-4 adapted contract
(server-side agent binding, JSON exemplar, adapted parser). Direct HTTP
/chat/completions to the private relay with content-addressed cache + transport retry.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys, time
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROUND3 = Path(__file__).resolve().parent.parent.parent / "round3"
ROUND4 = Path(__file__).resolve().parent.parent.parent / "round4"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROUND3))
sys.path.insert(0, str(ROUND4))
import round3_lib as pl  # noqa: E402
from sp500_forecastability import pilot_llm_v10 as v10  # noqa: E402
from ling_adapted_run import build_messages, parse_adapted_decision  # noqa: E402

RELAY_BASE = "https://openapi.center/v1"
DEFAULT_MODEL = "gpt-6-astra"
FALLBACK_MODELS = ("gpt-5.6-sol", "gpt-5.5")
MAX_TOKENS = 160
N_WORKERS = 13
MAX_TRANSPORT_ATTEMPTS = 3
BACKOFF = (2.0, 5.0, 10.0)
MAX_RESPONSE_BYTES = 1_000_000


def load_key() -> str:
    k = os.environ.get("OPENAPI_CENTER_API_KEY")
    if k:
        return k
    s = (Path.home() / ".codex" / "private.config.toml").read_text(encoding="utf-8")
    m = re.search(r'experimental_bearer_token\s*=\s*"([^"]+)"', s)
    if not m:
        raise RuntimeError("no relay key available (env OPENAPI_CENTER_API_KEY or private.config.toml)")
    return m.group(1)


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class RelayChatClient:
    """OpenAI-compatible chat client with cache, transport retry, key in-memory."""

    def __init__(self, cache_dir: Path, model: str, timeout: float = 120.0,
                 key: str | None = None) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = model
        self.timeout = timeout
        self.key = key if key is not None else load_key()
        self.endpoint = RELAY_BASE + "/chat/completions"
        self.stats = {"http": {}, "transport_retries": 0, "cache_hits": 0, "errors": 0}

    def call(self, messages, *, seed: int, model: str | None = None) -> pl.ChatResult:
        model = model or self.model
        payload = {"model": model, "messages": list(messages),
                   "temperature": 0.0, "max_tokens": MAX_TOKENS, "seed": seed}
        material = {"endpoint": self.endpoint, "request": payload}
        key = hashlib.sha256(canonical_json(material).encode()).hexdigest()
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            cached = json.loads(path.read_text(encoding="utf-8"))
            self.stats["cache_hits"] += 1
            return pl.ChatResult(content=str(cached["content"]), model=str(cached["model"]),
                                 usage=dict(cached.get("usage") or {}),
                                 http_status=int(cached.get("http_status", 200)),
                                 latency_seconds=0.0, cache_hit=True, cache_key=key)
        last_err: str | None = None
        last_status = None
        for attempt in range(MAX_TRANSPORT_ATTEMPTS):
            try:
                result = self._post(payload)
                self.stats["http"][result.http_status] = self.stats["http"].get(result.http_status, 0) + 1
                if result.http_status == 200:
                    out = {"content": result.content, "model": result.model,
                           "usage": dict(result.usage), "http_status": result.http_status,
                           "latency_seconds": result.latency_seconds, "cache_hit": False,
                           "cache_key": key}
                    self.cache_dir.joinpath(f"{key}.json").write_text(
                        json.dumps(out, ensure_ascii=False, sort_keys=True), encoding="utf-8")
                    return result
                # non-200: treat 429/5xx as retryable, else raise
                last_status = result.http_status
                last_err = f"http {result.http_status}"
                if result.http_status not in (429, 500, 502, 503, 504):
                    raise RuntimeError(f"HTTP {result.http_status}: {result.content[:300]}")
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                self.stats["errors"] += 1
            if attempt < MAX_TRANSPORT_ATTEMPTS - 1:
                time.sleep(BACKOFF[min(attempt, len(BACKOFF) - 1)])
                self.stats["transport_retries"] += 1
        raise RuntimeError(f"transport failed after {MAX_TRANSPORT_ATTEMPTS} attempts: {last_err}")

    def _post(self, payload) -> pl.ChatResult:
        body = canonical_json(payload).encode("utf-8")
        req = urllib.request.Request(self.endpoint, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", "Bearer " + self.key)
        started = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                status = int(response.status)
        except urllib.error.HTTPError as e:
            detail = e.read(4096).decode("utf-8", errors="replace")
            # synthesize a result so non-200 status is captured
            return pl.ChatResult(content=detail[:500], model=str(payload["model"]),
                                 usage={}, http_status=e.code, latency_seconds=time.monotonic()-started,
                                 cache_hit=False, cache_key="")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise RuntimeError(f"transport: {e}") from e
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("response exceeded 1MB")
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        return pl.ChatResult(content=content, model=str(data.get("model", payload["model"])),
                             usage=dict(data.get("usage") or {}), http_status=status,
                             latency_seconds=time.monotonic() - started, cache_hit=False, cache_key="")


def build_composites(pairs_n: int) -> list[pl.Composite]:
    sel = json.loads((ROUND3 / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((ROUND3 / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    pairs = sel["pairs"][:pairs_n]
    distractors = {row["pair_id"]: pl.Distractor(
        distractor_id=row["distractor_id"], distractor_page=row["distractor_page"],
        evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == row["distractor_id"]))
        for row in pairs}
    natural = [pl.NaturalPair(
        pair_id=row["pair_id"], case_id=row["case_id"], page=row["page"], claim=row["claim"],
        supports_id=row["supports_id"], refutes_id=row["refutes_id"],
        supports_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == row["supports_id"]),
        refutes_evidence=next(e["evidence"] for e in sel["evidence"] if e["unique_id"] == row["refutes_id"]),
        character_ratio=float(row["character_ratio"]), token_jaccard=float(row["token_jaccard"]))
        for row in pairs]
    return pl.build_composites(natural, distractors, artifacts)


def run_one(client: RelayChatClient, comp: pl.Composite, view: v10.EvidenceView,
            agent_index: int) -> dict:
    assigned_agent_id, persona = v10.AGENT_PERSONAS[agent_index]
    attempts: list[dict] = []
    decision = None
    final_error = None
    repair = False
    for _ in range(pl.MAX_ATTEMPTS):
        try:
            messages = build_messages(comp, view, persona=persona, repair=repair)
            result = client.call(messages, seed=v10._agent_seed(agent_index))
        except (RuntimeError, TypeError, ValueError) as error:
            final_error = f"{type(error).__name__}: {error}"
            attempts.append({"parse_error": None, "transport_error": final_error,
                             "http_status": None, "cache_hit": False})
            repair = True
            continue
        attempt = {"parse_error": None, "transport_error": None,
                   "http_status": result.http_status, "cache_hit": result.cache_hit,
                   "cache_key": result.cache_key, "model": result.model,
                   "usage": dict(result.usage),
                   "latency_seconds": result.latency_seconds}
        try:
            decision = parse_adapted_decision(result.content, set(view.allowed_evidence_ids))
        except (TypeError, ValueError) as error:
            final_error = f"{type(error).__name__}: {error}"
            attempt["parse_error"] = final_error
            attempts.append(attempt)
            repair = True
            continue
        attempts.append(attempt)
        final_error = None
        break
    model = next((a.get("model") for a in attempts if a.get("model")), None)
    return {"protocol_version": "cs-paper-gpt-singlepoint-20260914-round6",
            "model": model,
            "cqid": comp.cqid, "pair_id": comp.pair_id, "item_id": comp.item_id,
            "stage": comp.stage, "assigned_agent_id": assigned_agent_id,
            "agent_index": agent_index, "condition": view.condition,
            "partition": sorted(view.allowed_evidence_ids),
            "success": decision is not None,
            "first_pass_valid": decision is not None and len(attempts) == 1,
            "attempts": attempts, "decision": decision, "final_error": final_error}


MAX_CONSECUTIVE_FAILURES = 20

def run_batch(client, comps, *, workers, label) -> tuple[list[dict], dict]:
    tasks = [(comp, agent_index, condition)
             for comp in comps for agent_index in range(pl.N_AGENTS) for condition in pl.CONDITIONS]
    expected = len(tasks)
    records: list[dict] = []
    start = time.monotonic()
    done = 0
    consec_fail = 0
    aborted = False
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_one, client, comp, pl.build_view(comp, agent_index, condition), agent_index): None
                   for comp, agent_index, condition in tasks}
        for fut in as_completed(futures):
            rec = fut.result()
            records.append(rec)
            done += 1
            if rec["success"]:
                consec_fail = 0
            else:
                consec_fail += 1
                if consec_fail >= MAX_CONSECUTIVE_FAILURES:
                    aborted = True
                    for f in futures:
                        f.cancel()
                    print(f"[{label}] ABORT after {consec_fail} consecutive failures at {done}/{expected}", flush=True)
                    break
            if done % 200 == 0 or done == expected:
                ok = sum(1 for r in records if r["success"])
                rate = done / max(0.001, time.monotonic() - start)
                print(f"[{label}] {done}/{expected} success={ok} rate={rate:.1f}/s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["agent_index"], r["condition"]))
    summary = {"label": label, "model": client.model, "expected_calls": expected,
               "records": len(records), "aborted": aborted,
               "success": sum(1 for r in records if r["success"]),
               "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4),
               "first_pass_rate": round(sum(1 for r in records if r["first_pass_valid"]) / max(1, len(records)), 4),
               "http_stats": dict(client.stats["http"]), "transport_retries": client.stats["transport_retries"],
               "cache_hits": client.stats["cache_hits"],
               "elapsed_seconds": round(time.monotonic() - start, 2),
               "token_usage": {"prompt_tokens": sum(a.get("usage", {}).get("prompt_tokens") or 0 for r in records for a in r["attempts"]),
                               "completion_tokens": sum(a.get("usage", {}).get("completion_tokens") or 0 for r in records for a in r["attempts"])},
               "per_condition": {cond: {"n": sum(1 for r in records if r["condition"] == cond),
                                        "success": sum(1 for r in records if r["condition"] == cond and r["success"])}
                                 for cond in pl.CONDITIONS}}
    return records, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=N_WORKERS)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--smoke-only", action="store_true")
    args = ap.parse_args()

    cohort = json.loads((HERE / "cohort_first100_pairs.json").read_text(encoding="utf-8"))
    smoke_items = set(cohort["smoke_items"])
    formal_items = set(cohort["formal_items"])
    comps_all = build_composites(100)
    by_item = {c.item_id: c for c in comps_all}
    comps_smoke = [by_item[i] for i in cohort["smoke_items"]]
    comps_formal = [by_item[i] for i in cohort["formal_items"]]
    print(f"comps smoke={len(comps_smoke)} formal={len(comps_formal)}", flush=True)

    client = RelayChatClient(HERE / "cache", model=args.model)
    print(f"model={args.model} workers={args.workers}", flush=True)

    # ---- smoke ----
    recs_smoke, sum_smoke = run_batch(client, comps_smoke, workers=args.workers, label="smoke")
    pl.write_jsonl(HERE / "records_smoke.jsonl", recs_smoke)
    pl.write_json(HERE / "run_summary_smoke.json", sum_smoke)
    print(json.dumps(sum_smoke, ensure_ascii=False, indent=2), flush=True)
    if args.smoke_only:
        return 0

    # ---- formal (smoke items replay from cache) ----
    recs_formal, sum_formal = run_batch(client, comps_formal, workers=args.workers, label="formal")
    pl.write_jsonl(HERE / "records.jsonl", recs_formal)
    pl.write_json(HERE / "run_summary_formal.json", sum_formal)
    print(json.dumps(sum_formal, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
