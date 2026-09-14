"""CS-pilot shared library (Phase 2, BoolQ).

Reuses frozen V10 selection/evidence/prompt/parser logic read-only from
/home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src. New code here is the
consensus-stress pilot: cached Qwen3.5-4B client, paraphrase condition,
expected-response bookkeeping.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

import sys
FROZEN_SRC = Path("/home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src")
if str(FROZEN_SRC) not in sys.path:
    sys.path.insert(0, str(FROZEN_SRC))

from sp500_forecastability import pilot_llm_v10 as v10  # frozen reference (read-only)

PROTOCOL_VERSION = "cs-pilot-boolq-2026-09-12"
SALT = b"cs-pilot-boolq-2026-09-12\n"
ENDPOINT = "http://127.0.0.1:31518/v1/chat/completions"
MODEL = "Qwen3.5-4B"
MAX_COMPLETION_TOKENS = 160
MAX_ATTEMPTS = 2
N_AGENTS = v10.N_AGENTS
CONDITIONS = ("original", "paraphrase", "remove", "reverse", "substitute")
SCORED_CONDITIONS = ("paraphrase", "reverse", "substitute")
MAX_RESPONSE_BYTES = 1_000_000
REPAIR_SUFFIX = (
    "\n\nYour previous response violated the required JSON contract. "
    "Return only the exact JSON object, with no explanation or extra fields."
)
PARAPHRASE_SEED = 20_260_912
SUBSTITUTE_SEED = 20_260_912


def configure_v10() -> None:
    v10.SALT = SALT
    v10.PROTOCOL_VERSION = PROTOCOL_VERSION
    v10.CQID_PROTOCOL_VERSION = PROTOCOL_VERSION
    v10.CQID_PREFIX = "cs"
    v10.FORMAL_EXAMPLES = 100
    v10.FORMAL_PER_LABEL = 50
    v10.DEFAULT_DATASET = Path("data/benchmarks/boolq/train.parquet")


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def write_jsonl(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class ChatResult:
    content: str
    model: str
    usage: Mapping[str, int | None]
    http_status: int
    latency_seconds: float
    cache_hit: bool
    cache_key: str


class CachedChatClient:
    """Content-addressed OpenAI-compatible client; NO reasoning_effort field."""

    def __init__(self, cache_dir: Path, timeout: float = 90.0,
                 max_completion_tokens: int = MAX_COMPLETION_TOKENS) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.max_completion_tokens = max_completion_tokens

    def call(self, messages: Sequence[Mapping[str, str]], *, seed: int) -> ChatResult:
        payload = {
            "model": MODEL,
            "messages": list(messages),
            "temperature": 0.0,
            "max_tokens": getattr(self, "max_completion_tokens", MAX_COMPLETION_TOKENS),
            "seed": seed,
        }
        material = {"endpoint": ENDPOINT, "request": payload}
        key = hashlib.sha256(canonical_json(material).encode()).hexdigest()
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            cached = json.loads(path.read_text(encoding="utf-8"))
            return ChatResult(
                content=str(cached["content"]),
                model=str(cached["model"]),
                usage=dict(cached.get("usage") or {}),
                http_status=int(cached.get("http_status", 200)),
                latency_seconds=0.0,
                cache_hit=True,
                cache_key=key,
            )
        body = canonical_json(payload).encode("utf-8")
        req = urllib_request.Request(
            ENDPOINT, data=body, headers={"Content-Type": "application/json"}, method="POST",
        )
        started = time.monotonic()
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                status = int(response.status)
        except urllib_error.HTTPError as error:
            detail = error.read(4096).decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {error.code}: {detail}") from error
        except (urllib_error.URLError, TimeoutError) as error:
            raise RuntimeError(f"chat request failed: {error}") from error
        latency = time.monotonic() - started
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("chat response exceeded the one-megabyte safety limit")
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        result = ChatResult(
            content=content,
            model=str(data.get("model", MODEL)),
            usage=dict(data.get("usage") or {}),
            http_status=status,
            latency_seconds=latency,
            cache_hit=False,
            cache_key=key,
        )
        out = {
            "content": result.content, "model": result.model, "usage": dict(result.usage),
            "http_status": result.http_status, "latency_seconds": result.latency_seconds,
            "cache_hit": result.cache_hit, "cache_key": result.cache_key,
        }
        self.cache_dir.joinpath(f"{key}.json").write_text(
            json.dumps(out, ensure_ascii=False, sort_keys=True), encoding="utf-8",
        )
        return result


# --- selection (mirrors frozen v10 with fresh salt) ------------------------ #

def load_composites(dataset_path: Path) -> list:
    configure_v10()
    items = v10.load_boolq(dataset_path)
    comps = v10.build_composite_questions(items)
    counts = {label: 0 for label in ("yes", "no")}
    for comp in comps:
        counts[comp.label] += 1
    if counts != {"yes": 50, "no": 50}:
        raise ValueError(f"selection drifted: {counts}")
    return comps


# --- paraphrase generation ------------------------------------------------- #

PARAPHRASE_PROMPT = (
    "Paraphrase the following evidence sentence without changing its meaning, "
    "polarity, factual content, or named entities. Do not add or remove negation, "
    "do not change numbers or dates, do not introduce new information, and do not "
    "add meta-language such as 'paraphrase' or 'original'. Keep approximately the "
    "same length. Output only the paraphrased sentence.\n\n"
    "Evidence sentence:\n{text}"
)


def parse_paraphrase_response(content: str, src_tokens: int):
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    sentences = [s.strip() for s in re.split(r"[\n]+", text) if s.strip()]
    if not sentences:
        return None
    rewrite = sentences[0]
    rewrite = re.sub(r"^[-*]\s+", "", rewrite)
    if not rewrite:
        return None
    rt = max(1, len(rewrite.split()))
    if not (0.5 <= rt / max(1, src_tokens) <= 2.0):
        return None
    return rewrite


def build_paraphrase_manifest(items, *, client):
    manifest = {}
    stats = {"n_items": len(items), "n_ok": 0, "n_unusable": 0, "in_window": 0}
    for idx, item in enumerate(items):
        prompt = PARAPHRASE_PROMPT.format(text=item.passage)
        src_tokens = max(1, len(item.passage.split()))
        try:
            result = client.call([{"role": "user", "content": prompt}], seed=PARAPHRASE_SEED)
            rewrite = parse_paraphrase_response(result.content, src_tokens)
        except (KeyError, OSError, RuntimeError, TypeError, ValueError):
            rewrite = None
        if rewrite is None:
            manifest[item.qid] = {"paraphrase_sentence": "", "usable": False,
                                  "deviation_log": ["paraphrase_failed"]}
            stats["n_unusable"] += 1
        else:
            in_window = bool(0.5 <= len(rewrite.split()) / max(1, src_tokens) <= 2.0)
            manifest[item.qid] = {"paraphrase_sentence": rewrite, "usable": True,
                                  "in_length_window": in_window}
            stats["n_ok"] += 1
            if in_window:
                stats["in_window"] += 1
        if (idx + 1) % 50 == 0 or idx == len(items) - 1:
            print(f"[paraphrase-gen] {idx+1}/{len(items)} ok={stats['n_ok']}", flush=True)
    stats["unusable_fraction"] = stats["n_unusable"] / max(1, stats["n_items"])
    stats["passed_fail_fast"] = stats["unusable_fraction"] == 0.0
    return manifest, stats


# --- substitute generation (strengthened contract + bounded repair) --------- #

SUBSTITUTE_STRONG_PROMPT = (
    'You will see a Wikipedia passage that was used to answer the following '
    'yes/no question: "{question}". The gold answer was "{src_answer}".\n\n'
    'Write a single plain-text sentence that would support the OPPOSITE answer '
    '("{opp}") for this question. The sentence must stay on the same topic and '
    'use the same main entity, must clearly support the opposite answer (use '
    'explicit negation or a directly contradicting fact), must not introduce new '
    'named entities, must not contain meta-language such as "rewritten", '
    '"opposite", or "question", and must be between {lo} and {hi} whitespace '
    'tokens (target exactly {target} tokens). Output only the sentence.\n\n'
    'Original passage: {passage}'
)


def build_substitute_manifest_cs(items, *, client):
    """Opposite-supporting rewrite artifacts with a strengthened prompt and a
    bounded two-repair pass. Contract: same topic/entity, opposite support,
    length window 0.5-1.5x. max_tokens=256 avoids truncation. All documented
    in the preregistration (Amendments A/B) before any agent call."""
    client.max_completion_tokens = 256
    manifest = {}
    stats = {"n_items": len(items), "n_ok": 0, "n_unusable": 0,
             "n_repaired": 0, "in_window": 0}
    for idx, item in enumerate(items):
        src_tokens = max(1, len(item.passage.split()))
        lo = max(1, int(0.5 * src_tokens))
        hi = max(1, int(1.5 * src_tokens))
        opp = "no" if item.label == "yes" else "yes"
        def attempt(prompt_text, seed):
            try:
                res = client.call([{"role": "user", "content": prompt_text}], seed=seed)
                return pl_parse(res.content, src_tokens)
            except (KeyError, OSError, RuntimeError, TypeError, ValueError):
                return None
        rewrite = attempt(
            SUBSTITUTE_STRONG_PROMPT.format(question=item.question, src_answer=item.label,
                                            opp=opp, lo=lo, hi=hi, target=src_tokens,
                                            passage=item.passage),
            SUBSTITUTE_SEED,
        )
        repaired = 0
        if rewrite is None and repaired < 2:
            repaired = 1
            rewrite = attempt(
                SUBSTITUTE_STRONG_PROMPT.format(question=item.question, src_answer=item.label,
                                                opp=opp, lo=lo, hi=hi, target=src_tokens,
                                                passage=item.passage),
                SUBSTITUTE_SEED + 1,
            )
        if rewrite is None and repaired < 2:
            repaired = 2
            rewrite = attempt(
                SUBSTITUTE_STRONG_PROMPT.format(question=item.question, src_answer=item.label,
                                                opp=opp, lo=lo, hi=hi, target=src_tokens,
                                                passage=item.passage),
                SUBSTITUTE_SEED + 2,
            )
        if rewrite is None:
            manifest[item.qid] = {"substitute_sentence": "", "usable": False,
                                  "deviation_log": ["rewrite_failed_after_two_repairs"],
                                  "source_label": item.label, "source_root": item.source_root}
            stats["n_unusable"] += 1
        else:
            in_window = bool(lo <= len(rewrite.split()) <= hi)
            log = ["llm_negative_paraphrase_strong"]
            if repaired:
                log.append(f"bounded_repair_{repaired}")
            manifest[item.qid] = {"substitute_sentence": rewrite, "usable": True,
                                  "in_length_window": in_window, "deviation_log": log,
                                  "source_label": item.label, "source_root": item.source_root}
            stats["n_ok"] += 1
            if repaired:
                stats["n_repaired"] += 1
            if in_window:
                stats["in_window"] += 1
        if (idx + 1) % 50 == 0 or idx == len(items) - 1:
            print(f"[substitute-gen-cs] {idx+1}/{len(items)} ok={stats['n_ok']} "
                  f"repaired={stats['n_repaired']}", flush=True)
    stats["unusable_fraction"] = stats["n_unusable"] / max(1, stats["n_items"])
    stats["passed_fail_fast"] = stats["unusable_fraction"] == 0.0
    return manifest, stats


def pl_parse(content, src_tokens):
    """Single-sentence parse for substitute artifacts with a RELAXED length
    window (Amendment C): floor: min 5 tokens only; ceiling 3.0x; abs cap 80 (Amendment C final).
    Rationale: the local Qwen3.5-4B endpoint produces terse but semantically
    opposite rewrites that the frozen 0.5-1.5x window rejects. Semantic
    opposition is guarded separately by the offline audit (Amendment B)."""
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    sentences = [x.strip() for x in re.split(r"[\n]+", text) if x.strip()]
    if not sentences:
        return None
    rewrite = sentences[0]
    rewrite = re.sub(r"^[-*]\s+", "", rewrite)
    if not rewrite:
        return None
    n = len(rewrite.split())
    if n < 5 or n > 80:
        return None
    if n > int(3.0 * src_tokens):
        return None
    return rewrite


# --- evidence views -------------------------------------------------------- #

def build_evidence_view(composite, agent_index, condition,
                        substitute_manifest=None, paraphrase_manifest=None):
    partition_ids = v10.PARTITION_TABLE[agent_index]
    items = []
    for i, item in enumerate(composite.items):
        eid = f"E0{i + 1}"
        if eid not in partition_ids:
            continue
        if condition == "original":
            text = item.passage
        elif condition == "remove":
            continue
        elif condition == "reverse":
            text = f"Task-local counterfactual: it is false that: {item.passage}"
        elif condition == "substitute":
            assert substitute_manifest is not None
            text = str(substitute_manifest.get(item.qid, {}).get("substitute_sentence") or item.passage)
        elif condition == "paraphrase":
            assert paraphrase_manifest is not None
            text = str(paraphrase_manifest.get(item.qid, {}).get("paraphrase_sentence") or item.passage)
        else:
            raise ValueError(f"unknown condition: {condition}")
        items.append((eid, text))
    return v10.EvidenceView(condition=condition, items=tuple(items))


# --- one agent call -------------------------------------------------------- #

def run_one_agent_call(client, composite, view, *, agent_index):
    agent_id, persona = v10.AGENT_PERSONAS[agent_index]
    attempts = []
    decision = None
    final_error = None
    repair = False
    for _ in range(MAX_ATTEMPTS):
        try:
            messages = v10.build_messages(
                composite, view, agent_id=agent_id, persona=persona, repair=repair,
            )
            if repair and not messages[-1]["content"].endswith(REPAIR_SUFFIX):
                messages[-1] = dict(messages[-1])
                messages[-1]["content"] = messages[-1]["content"] + REPAIR_SUFFIX
            result = client.call(messages, seed=v10._agent_seed(agent_index))
        except (RuntimeError, TypeError, ValueError) as error:
            final_error = f"{type(error).__name__}: {error}"
            attempts.append({"parse_error": None, "transport_error": final_error,
                             "http_status": None, "cache_hit": False})
            continue
        attempt = {
            "parse_error": None, "transport_error": None,
            "http_status": result.http_status, "cache_hit": result.cache_hit,
            "cache_key": result.cache_key,
            "usage": dict(result.usage), "latency_seconds": result.latency_seconds,
        }
        try:
            decision = v10.parse_forced_qa_decision(
                result.content, expected_agent_id=agent_id,
                allowed_evidence_ids=view.allowed_evidence_ids,
            )
        except (TypeError, ValueError) as error:
            final_error = f"{type(error).__name__}: {error}"
            attempt["parse_error"] = final_error
            attempts.append(attempt)
            repair = True
            continue
        attempts.append(attempt)
        final_error = None
        break
    return {
        "protocol_version": PROTOCOL_VERSION,
        "cqid": composite.cqid,
        "agent_id": agent_id,
        "agent_index": agent_index,
        "condition": view.condition,
        "partition": sorted(v10.PARTITION_TABLE[agent_index]),
        "success": decision is not None,
        "first_pass_valid": decision is not None and len(attempts) == 1,
        "attempts": attempts,
        "decision": decision,
        "final_error": final_error,
    }
