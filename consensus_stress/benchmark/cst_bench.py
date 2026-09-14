"""Shared CST-Bench runner utilities (local endpoints only)."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

BENCH = Path(__file__).resolve().parent
PROJECT = BENCH.parent.parent
ROUND3 = PROJECT / "consensus_stress" / "round3"
for p in (ROUND3, Path("/home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src")):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import round3_lib as pl
from sp500_forecastability import pilot_llm_v10 as v10

PROTOCOL = "cs-round5-matched-baselines-cst-bench-20260913"
N_PAIRS = 300
N_SAMPLES = 25
N_REPLICATES = 5
TEMPERATURE = 0.7
MAX_TOKENS = 160
CONDITION_ORDER = ("original", "paraphrase", "reverse", "synthetic_reverse", "remove")
JSON_EXEMPLAR = '{"answer":"yes","confidence":0.75,"cited_evidence_ids":[]}'
MODELS = {
    "qwen": {
        "endpoint": "http://127.0.0.1:31518/v1/chat/completions",
        "model": "Qwen3.5-4B",
    },
    "ling": {
        "endpoint": "http://127.0.0.1:31520/v1/chat/completions",
        "model": "Ling-3.0-tiny",
    },
}


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def load_frozen_inputs() -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    sel = json.loads((ROUND3 / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((ROUND3 / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {
        uid: {"para1": row["para1"], "para2": row["para2"]}
        for uid, row in para.items() if row.get("usable")
    }
    if len(artifacts) != len(para):
        raise RuntimeError("unusable paraphrase encountered; frozen cohort must not be repaired")
    return sel, artifacts


def build_all_composites() -> list[pl.Composite]:
    sel, artifacts = load_frozen_inputs()
    pairs = sel["pairs"][:N_PAIRS]
    if len(pairs) != N_PAIRS:
        raise RuntimeError(f"expected {N_PAIRS} frozen pairs, found {len(pairs)}")
    distractors = {
        row["pair_id"]: pl.Distractor(
            distractor_id=row["distractor_id"], distractor_page=row["distractor_page"],
            evidence=next(e["evidence"] for e in sel["evidence"]
                          if e["unique_id"] == row["distractor_id"]),
        ) for row in pairs
    }
    natural = [
        pl.NaturalPair(
            pair_id=row["pair_id"], case_id=row["case_id"], page=row["page"], claim=row["claim"],
            supports_id=row["supports_id"], refutes_id=row["refutes_id"],
            supports_evidence=next(e["evidence"] for e in sel["evidence"]
                                   if e["unique_id"] == row["supports_id"]),
            refutes_evidence=next(e["evidence"] for e in sel["evidence"]
                                  if e["unique_id"] == row["refutes_id"]),
            character_ratio=float(row["character_ratio"]), token_jaccard=float(row["token_jaccard"]),
        ) for row in pairs
    ]
    comps = pl.build_composites(natural, distractors, artifacts)
    return sorted(comps, key=lambda c: c.cqid)


def build_messages(comp: pl.Composite, view: v10.EvidenceView, *, persona: str) -> list[dict[str, str]]:
    system = (
        "You are a binary evidence judge before a separate selective router. "
        f"Your fixed decision style is: {persona} "
        "Treat packet statements as task-local evidence, including counterfactual "
        "statements. When evidence is empty or insufficient, use your best "
        "general-knowledge judgment. You must choose yes or no; you cannot abstain. "
        "Do not provide reasoning, analysis, or chain-of-thought. Return only one "
        "JSON object."
    )
    task_payload = {
        "question": f"Does the provided evidence support the claim: {comp.claim}",
        "evidence_packet": [{"evidence_id": eid, "text": text} for eid, text in view.items],
    }
    user = (
        "Answer the yes/no question under the task-local evidence. yes means the "
        "evidence SUPPORTS the claim; no means the evidence REFUTES the claim. "
        "answer must be exactly 'yes' or 'no'. Confidence is the probability that "
        "your answer is correct. cited_evidence_ids must be a unique list of "
        "non-empty evidence IDs drawn only from the packet; use [] if no packet "
        "evidence is cited.\n\nRequired keys: answer, confidence, cited_evidence_ids. "
        "Do not include any other key. JSON shape (values are illustrative only): "
        f"{JSON_EXEMPLAR}\n\nTask payload:\n"
        f"{json.dumps(task_payload, ensure_ascii=False, indent=2)}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def parse_decision(content: str, allowed_evidence_ids: set[str]) -> dict[str, Any]:
    payload = v10._extract_json_object(content)
    required = {"answer", "confidence", "cited_evidence_ids"}
    missing = required - set(payload)
    unknown = set(payload) - required - {"agent_id"}
    if missing:
        raise ValueError(f"missing decision fields: {sorted(missing)}")
    if unknown:
        raise ValueError(f"unexpected decision fields: {sorted(unknown)}")
    answer = payload["answer"]
    if answer not in {"yes", "no"}:
        raise ValueError("answer must be yes or no")
    confidence = payload["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise TypeError("confidence must be numeric")
    confidence = float(confidence)
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be finite and in [0,1]")
    cites = payload["cited_evidence_ids"]
    if not isinstance(cites, list) or isinstance(cites, (str, bytes)):
        raise TypeError("cited_evidence_ids must be a list")
    if any(not isinstance(c, str) or not c for c in cites):
        raise TypeError("citations must be non-empty strings")
    if len(set(cites)) != len(cites):
        raise ValueError("citations must be unique")
    if set(cites) - allowed_evidence_ids:
        raise ValueError("citation outside packet")
    return {"answer": answer, "confidence": confidence, "cited_evidence_ids": list(cites)}


@dataclass(frozen=True)
class ChatResult:
    content: str
    model: str
    usage: dict[str, int | None]
    http_status: int
    latency_seconds: float
    cache_hit: bool
    cache_key: str


class SamplingChatClient:
    """One-attempt, content-addressed OpenAI-compatible client at temperature 0.7."""

    def __init__(self, cache_dir: Path, endpoint: str, model: str,
                 timeout: float = 90.0) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.endpoint = endpoint
        self.model = model
        self.timeout = timeout

    def call(self, messages: list[dict[str, str]], *, seed: int) -> ChatResult:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "seed": seed,
        }
        material = {"endpoint": self.endpoint, "request": payload}
        key = hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            cached = json.loads(path.read_text(encoding="utf-8"))
            return ChatResult(
                content=str(cached["content"]), model=str(cached["model"]),
                usage=dict(cached.get("usage") or {}), http_status=int(cached.get("http_status", 200)),
                latency_seconds=0.0, cache_hit=True, cache_key=key,
            )
        req = urllib_request.Request(
            self.endpoint, data=canonical_json(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        started = time.monotonic()
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read(1_000_001)
                status = int(response.status)
        except urllib_error.HTTPError as error:
            detail = error.read(4096).decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {error.code}: {detail}") from error
        except (urllib_error.URLError, TimeoutError) as error:
            raise RuntimeError(f"chat request failed: {error}") from error
        if len(raw) > 1_000_000:
            raise ValueError("response exceeds safety limit")
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        result = ChatResult(
            content=content, model=str(data.get("model", self.model)),
            usage=dict(data.get("usage") or {}), http_status=status,
            latency_seconds=time.monotonic() - started, cache_hit=False, cache_key=key,
        )
        path.write_text(json.dumps({
            "content": result.content, "model": result.model, "usage": result.usage,
            "http_status": result.http_status, "latency_seconds": result.latency_seconds,
            "cache_hit": result.cache_hit, "cache_key": result.cache_key,
        }, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return result


def make_tasks(comps: list[pl.Composite]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for item_index, comp in enumerate(comps):
        for sample_index in range(N_SAMPLES):
            tasks.append({
                "comp": comp, "item_index": item_index, "family": "sampling",
                "condition": "original", "sample_index": sample_index,
                "seed": 20_260_913 + 100 * item_index + sample_index,
            })
        for condition_index, condition in enumerate(CONDITION_ORDER):
            for replicate in range(N_REPLICATES):
                j = N_SAMPLES + condition_index * N_REPLICATES + replicate
                tasks.append({
                    "comp": comp, "item_index": item_index, "family": "intervention",
                    "condition": condition, "sample_index": j, "replicate": replicate,
                    "seed": 20_260_913 + 100 * item_index + j,
                })
    return tasks


def run_task(client: SamplingChatClient, task: dict[str, Any]) -> dict[str, Any]:
    comp: pl.Composite = task["comp"]
    view = pl.build_view(comp, 0, task["condition"])
    _, persona = v10.AGENT_PERSONAS[0]
    messages = build_messages(comp, view, persona=persona)
    record = {
        "protocol": PROTOCOL, "model": client.model, "endpoint": client.endpoint,
        "cqid": comp.cqid, "item_id": comp.item_id, "pair_id": comp.pair_id,
        "stage": comp.stage, "agent_index": 0, "family": task["family"],
        "condition": task["condition"], "sample_index": task["sample_index"],
        "replicate": task.get("replicate"), "seed": task["seed"],
        "partition": sorted(view.allowed_evidence_ids), "success": False,
        "decision": None, "final_error": None, "http_status": None,
        "cache_hit": False, "cache_key": None, "content_sha256": None,
        "usage": {}, "latency_seconds": None,
    }
    try:
        result = client.call(messages, seed=task["seed"])
    except (RuntimeError, ValueError) as error:
        record["final_error"] = f"{type(error).__name__}: {error}"
        return record
    record.update({
        "http_status": result.http_status, "cache_hit": result.cache_hit,
        "cache_key": result.cache_key, "content_sha256": sha256_text(result.content),
        "usage": dict(result.usage), "latency_seconds": result.latency_seconds,
    })
    try:
        record["decision"] = parse_decision(result.content, set(view.allowed_evidence_ids))
        record["success"] = True
    except (TypeError, ValueError) as error:
        record["final_error"] = f"{type(error).__name__}: {error}"
    return record


def run_model(model_key: str, output_dir: Path, *, workers: int = 24,
              limit_items: int | None = None) -> dict[str, Any]:
    if model_key not in MODELS:
        raise ValueError(f"unknown model key: {model_key}")
    cfg = MODELS[model_key]
    comps = build_all_composites()
    if limit_items is not None:
        comps = comps[:limit_items]
    tasks = make_tasks(comps)
    expected = len(tasks)
    client = SamplingChatClient(output_dir / f"cache_{model_key}", cfg["endpoint"], cfg["model"])
    records: list[dict[str, Any]] = []
    started = time.monotonic()
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_task, client, task) for task in tasks]
        for future in as_completed(futures):
            records.append(future.result())
            done += 1
            if done % 500 == 0 or done == expected:
                ok = sum(r["success"] for r in records)
                elapsed = time.monotonic() - started
                rate = done / elapsed if elapsed else 0.0
                eta = (expected - done) / rate if rate else 0.0
                print(f"[{model_key}] {done}/{expected} valid={ok} "
                      f"elapsed={elapsed:.0f}s eta={eta:.0f}s", flush=True)
    records.sort(key=lambda r: (r["cqid"], r["family"], r["sample_index"]))
    write_jsonl(output_dir / f"{model_key}_baseline_records.jsonl", records)
    summary = {
        "protocol": PROTOCOL, "model_key": model_key, "model": cfg["model"],
        "endpoint": cfg["endpoint"], "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS, "items": len(comps), "expected_calls": expected,
        "records": len(records), "success": sum(r["success"] for r in records),
        "valid_rate": round(sum(r["success"] for r in records) / max(1, len(records)), 6),
        "per_family": {
            family: {
                "n": sum(r["family"] == family for r in records),
                "success": sum(r["family"] == family and r["success"] for r in records),
            } for family in ("sampling", "intervention")
        },
        "per_condition": {
            cond: {
                "n": sum(r["condition"] == cond for r in records),
                "success": sum(r["condition"] == cond and r["success"] for r in records),
            } for cond in CONDITION_ORDER
        },
        "elapsed_seconds": round(time.monotonic() - started, 2),
        "workers": workers,
    }
    write_json(output_dir / f"{model_key}_baseline_run_summary.json", summary)
    return summary
