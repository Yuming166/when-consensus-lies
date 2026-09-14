"""Round-2 CS pilot shared library (VitaminC natural pairs).

Reuses frozen V10 personas, 2-of-3 partition table, and the yes/no JSON parser
read-only from /home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src. New code here
is the round-2 consensus-stress pilot: selection from VitaminC natural pairs,
decision-relevance-aware expected-response bookkeeping, cached Qwen3.5-4B client.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

import sys
FROZEN_SRC = Path("/home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src")
if str(FROZEN_SRC) not in sys.path:
    sys.path.insert(0, str(FROZEN_SRC))

from sp500_forecastability import pilot_llm_v10 as v10  # frozen reference (read-only)

PROTOCOL_VERSION = "cs-pilot-vitaminc-2026-09-13"
SALT = b"cs-pilot-vitaminc-2026-09-13\n"
ENDPOINT = "http://127.0.0.1:31518/v1/chat/completions"
MODEL = "Qwen3.5-4B"
AGENT_MAX_TOKENS = 160
ARTIFACT_MAX_TOKENS = 256
MAX_ATTEMPTS = 2
N_AGENTS = v10.N_AGENTS
CONDITIONS = ("original", "paraphrase", "reverse", "synthetic_reverse", "remove")
PRIMARY_SCORED = ("paraphrase", "reverse")
SECONDARY_SCORED = ("synthetic_reverse",)
SCORED_ALL = PRIMARY_SCORED + SECONDARY_SCORED
N_STAGE1_PAIRS = 50
N_STAGE2_PAIRS = 50
TOTAL_PAIRS = N_STAGE1_PAIRS + N_STAGE2_PAIRS
MAX_RESPONSE_BYTES = 1_000_000
REPAIR_SUFFIX = (
    "\n\nYour previous response violated the required JSON contract. "
    "Return only the exact JSON object, with no explanation or extra fields."
)
PARAPHRASE_SEED = 20_260_913
REVERSE_PREFIX = "Task-local counterfactual: it is false that: "


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


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def character_ratio(a: str, b: str) -> float:
    import difflib
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def token_jaccard(a: str, b: str) -> float:
    ta, tb = set(tokens(a)), set(tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def hpair(key: str) -> str:
    return hashlib.sha256(SALT + key.encode()).hexdigest()


def cqid_for(item_id: str) -> str:
    return "cs2_" + hashlib.sha256(SALT + item_id.encode()).hexdigest()[:16]


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
                 max_completion_tokens: int = AGENT_MAX_TOKENS) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.max_completion_tokens = max_completion_tokens

    def call(self, messages: Sequence[Mapping[str, str]], *, seed: int) -> ChatResult:
        payload = {
            "model": MODEL,
            "messages": list(messages),
            "temperature": 0.0,
            "max_tokens": self.max_completion_tokens,
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


# --- selection (offline; no model calls) ----------------------------------- #

def load_vitaminc_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def load_frozen_excluded_pages() -> set[str]:
    base = Path("/home/gaoym/.tmp_sp500_naacl_symmetric_20260909/results")
    pages: set[str] = set()
    for rel in ("detection_v3_16_development/selection_manifest.json",
                "detection_v3_16_1/selection_manifest.json"):
        payload = json.loads((base / rel).read_text(encoding="utf-8"))
        for row in payload["pairs"]:
            pages.add(str(row["page"]))
            pages.add(str(row["distractor_page"]))
    return pages


@dataclass(frozen=True)
class NaturalPair:
    pair_id: str
    case_id: str
    page: str
    claim: str
    supports_id: str
    refutes_id: str
    supports_evidence: str
    refutes_evidence: str
    character_ratio: float
    token_jaccard: float


def build_natural_pairs(rows: Sequence[Mapping[str, object]]) -> list[NaturalPair]:
    by_case: dict[str, list[dict]] = {}
    for row in rows:
        by_case.setdefault(str(row["case_id"]), []).append(dict(row))
    pairs: list[NaturalPair] = []
    for cid in sorted(by_case):
        by_claim: dict[str, list[dict]] = {}
        for row in by_case[cid]:
            by_claim.setdefault(str(row["claim"]), []).append(row)
        for claim in sorted(by_claim):
            vv = by_claim[claim]
            if len(vv) != 2:
                continue
            labs = {str(v["label"]) for v in vv}
            if labs != {"SUPPORTS", "REFUTES"}:
                continue
            s = next(v for v in vv if str(v["label"]) == "SUPPORTS")
            r = next(v for v in vv if str(v["label"]) == "REFUTES")
            cr = character_ratio(str(s["evidence"]), str(r["evidence"]))
            tj = token_jaccard(str(s["evidence"]), str(r["evidence"]))
            pairs.append(NaturalPair(
                pair_id=f"{cid}:{hashlib.sha256(claim.encode()).hexdigest()[:12]}",
                case_id=cid, page=str(s["page"]), claim=claim,
                supports_id=str(s["unique_id"]), refutes_id=str(r["unique_id"]),
                supports_evidence=str(s["evidence"]), refutes_evidence=str(r["evidence"]),
                character_ratio=cr, token_jaccard=tj,
            ))
    return pairs


def eligible_pairs(rows: Sequence[Mapping[str, object]]) -> list[NaturalPair]:
    excluded = load_frozen_excluded_pages()
    by_page: dict[str, list[NaturalPair]] = {}
    for pair in build_natural_pairs(rows):
        if pair.page in excluded:
            continue
        by_page.setdefault(pair.page, []).append(pair)
    out: list[NaturalPair] = []
    for page in sorted(by_page):
        best = sorted(
            by_page[page],
            key=lambda p: (-p.character_ratio, -p.token_jaccard, p.case_id),
        )[0]
        if best.character_ratio < 0.93 or best.token_jaccard < 0.85:
            continue
        if "\ufffd" in best.claim or "\ufffd" in best.supports_evidence or "\ufffd" in best.refutes_evidence:
            continue
        if not (5 <= len(best.claim.split()) <= 40):
            continue
        if not (10 <= len(best.supports_evidence.split()) <= 120
                and 10 <= len(best.refutes_evidence.split()) <= 120):
            continue
        out.append(best)
    out.sort(key=lambda p: hpair(p.page))
    return out


@dataclass(frozen=True)
class Distractor:
    distractor_id: str
    distractor_page: str
    evidence: str


def assign_distractors(selected: Sequence[NaturalPair], rows: Sequence[Mapping[str, object]]) -> dict[str, Distractor]:
    excluded = load_frozen_excluded_pages()
    used_pages = {p.page for p in selected}
    # candidate distractor sentences: one row per page, deterministic
    by_page: dict[str, list[dict]] = {}
    for row in rows:
        page = str(row["page"])
        if page in excluded or page in used_pages:
            continue
        by_page.setdefault(page, []).append(dict(row))
    candidates: list[dict] = []
    for page in sorted(by_page):
        best = sorted(by_page[page], key=lambda r: (str(r["unique_id"]),))[0]
        candidates.append(best)
    candidates.sort(key=lambda r: hpair("distractor:" + str(r["unique_id"])))
    used_distractors: set[str] = set()
    out: dict[str, Distractor] = {}
    for pair in selected:
        chosen = None
        for cand in candidates:
            if cand["unique_id"] in used_distractors:
                continue
            if token_jaccard(pair.claim, str(cand["evidence"])) > 0.05:
                continue
            if "\ufffd" in str(cand["evidence"]):
                continue
            chosen = cand
            break
        if chosen is None:
            raise ValueError(f"no distractor available for pair {pair.pair_id}")
        used_distractors.add(str(chosen["unique_id"]))
        out[pair.pair_id] = Distractor(
            distractor_id=str(chosen["unique_id"]),
            distractor_page=str(chosen["page"]),
            evidence=str(chosen["evidence"]),
        )
    return out


# --- composites and evidence views ----------------------------------------- #

@dataclass(frozen=True)
class Composite:
    pair_id: str
    stage: int
    item_id: str          # f"{pair_id}:support" or f"{pair_id}:refute"
    cqid: str
    claim: str
    gold_label: str       # "SUPPORTS" | "REFUTES"
    gold_yes: bool        # gold answer in yes/no space (yes=SUPPORTS)
    evidence: str         # item's own evidence (decision-relevant)
    evidence_opp: str     # paired counter-evidence (decision-relevant, opposite)
    para1: str            # paraphrase variant 1 of evidence (artifact, offline)
    para1_opp: str        # paraphrase variant 1 of the paired counter-evidence (artifact, offline)
    para2: str            # paraphrase variant 2 of evidence (artifact, offline)
    distractor: str       # non-decision-relevant third unit
    distractor_para: str  # paraphrase of distractor (artifact, offline)
    source_ids: tuple[str, str]  # (own unique_id, opp unique_id)


def build_composites(pairs: Sequence[NaturalPair], distractors: Mapping[str, Distractor],
                     artifacts: Mapping[str, Mapping[str, str]],
                     stage_override: int | None = None) -> list[Composite]:
    out: list[Composite] = []
    for idx, pair in enumerate(pairs):
        stage = stage_override if stage_override is not None else (1 if idx < N_STAGE1_PAIRS else 2)
        dist = distractors[pair.pair_id]
        para_s1 = artifacts.get(pair.supports_id, {}).get("para1") or ""
        para_s2 = artifacts.get(pair.supports_id, {}).get("para2") or ""
        para_r1 = artifacts.get(pair.refutes_id, {}).get("para1") or ""
        para_r2 = artifacts.get(pair.refutes_id, {}).get("para2") or ""
        out.append(Composite(
            pair_id=pair.pair_id, stage=stage, item_id=f"{pair.pair_id}:support",
            cqid=cqid_for(f"{pair.pair_id}:support"), claim=pair.claim,
            gold_label="SUPPORTS", gold_yes=True,
            evidence=pair.supports_evidence, evidence_opp=pair.refutes_evidence,
            para1=para_s1, para1_opp=para_r1, para2=para_s2,
            distractor=dist.evidence, distractor_para=artifacts.get(dist.distractor_id, {}).get("para1") or "",
            source_ids=(pair.supports_id, pair.refutes_id),
        ))
        out.append(Composite(
            pair_id=pair.pair_id, stage=stage, item_id=f"{pair.pair_id}:refute",
            cqid=cqid_for(f"{pair.pair_id}:refute"), claim=pair.claim,
            gold_label="REFUTES", gold_yes=False,
            evidence=pair.refutes_evidence, evidence_opp=pair.supports_evidence,
            para1=para_r1, para1_opp=para_s1, para2=para_r2,
            distractor=dist.evidence, distractor_para=artifacts.get(dist.distractor_id, {}).get("para1") or "",
            source_ids=(pair.refutes_id, pair.supports_id),
        ))
    return out


def unit_texts(comp: Composite, condition: str) -> dict[str, str]:
    """Map evidence id -> text for the given condition (3 units)."""
    if condition == "original":
        return {"E01": comp.evidence, "E02": comp.para1, "E03": comp.distractor}
    if condition == "paraphrase":
        return {"E01": comp.para1, "E02": comp.para2, "E03": comp.distractor_para}
    if condition == "reverse":
        return {"E01": comp.evidence_opp, "E02": comp.para1_opp, "E03": comp.distractor}
    if condition == "synthetic_reverse":
        return {
            "E01": REVERSE_PREFIX + comp.evidence,
            "E02": REVERSE_PREFIX + comp.para1,
            "E03": REVERSE_PREFIX + comp.distractor,
        }
    if condition == "remove":
        return {}
    raise ValueError(f"unknown condition: {condition}")


def build_view(comp: Composite, agent_index: int, condition: str) -> v10.EvidenceView:
    partition = v10.PARTITION_TABLE[agent_index]
    texts = unit_texts(comp, condition)
    items: list[tuple[str, str]] = []
    for eid in ("E01", "E02", "E03"):
        if eid not in partition:
            continue
        text = texts.get(eid)
        if text is None:
            continue  # E02 in reverse condition is not shown (keeps 2 units, one decisive)
        items.append((eid, text))
    return v10.EvidenceView(condition=condition, items=tuple(items))


def build_messages(comp: Composite, view: v10.EvidenceView, *, agent_id: str,
                   persona: str, repair: bool = False) -> list[dict[str, str]]:
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
        "evidence_packet": [
            {"evidence_id": eid, "text": text} for eid, text in view.items
        ],
    }
    user = (
        "Answer the yes/no question under the task-local evidence. yes means the "
        "evidence SUPPORTS the claim; no means the evidence REFUTES the claim. "
        "answer must be exactly 'yes' or 'no'. Confidence is the probability that "
        "your answer is correct. cited_evidence_ids must be a unique list drawn "
        f"only from the packet.\n\nagent_id must be exactly: {agent_id}\n"
        "Required keys, with no others: agent_id, answer, confidence, "
        f"cited_evidence_ids.\n\nTask payload:\n"
        f"{json.dumps(task_payload, ensure_ascii=False, indent=2)}"
    )
    if repair:
        user += REPAIR_SUFFIX
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def run_one_agent_call(client, comp: Composite, view, *, agent_index: int) -> dict:
    agent_id, persona = v10.AGENT_PERSONAS[agent_index]
    attempts: list[dict] = []
    decision = None
    final_error = None
    repair = False
    for _ in range(MAX_ATTEMPTS):
        try:
            messages = build_messages(
                comp, view, agent_id=agent_id, persona=persona, repair=repair,
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
            "cache_key": result.cache_key, "usage": dict(result.usage),
            "latency_seconds": result.latency_seconds,
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
        "cqid": comp.cqid,
        "pair_id": comp.pair_id,
        "item_id": comp.item_id,
        "stage": comp.stage,
        "agent_id": agent_id,
        "agent_index": agent_index,
        "condition": view.condition,
        "partition": sorted(view.allowed_evidence_ids),
        "success": decision is not None,
        "first_pass_valid": decision is not None and len(attempts) == 1,
        "attempts": attempts,
        "decision": decision,
        "final_error": final_error,
    }


# --- paraphrase artifact generation (offline; cached) ----------------------- #

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


def generate_paraphrase_variants(text: str, client, *, seed_base: int) -> tuple[str | None, str | None]:
    prompt = PARAPHRASE_PROMPT.format(text=text)
    src_tokens = max(1, len(text.split()))
    variants: list[str | None] = []
    for k in (0, 1):
        try:
            result = client.call([{"role": "user", "content": prompt}], seed=seed_base + k)
            variants.append(parse_paraphrase_response(result.content, src_tokens))
        except (KeyError, OSError, RuntimeError, TypeError, ValueError):
            variants.append(None)
    return variants[0], variants[1]


def build_paraphrase_manifest(items: Sequence[Mapping[str, str]], client, *,
                              seed_base: int = PARAPHRASE_SEED) -> tuple[dict, dict]:
    manifest: dict[str, dict] = {}
    stats = {"n_items": len(items), "n_ok_para1": 0, "n_ok_para2": 0, "n_both_ok": 0}
    for idx, item in enumerate(items):
        uid = str(item["unique_id"])
        text = str(item["evidence"])
        p1, p2 = generate_paraphrase_variants(text, client, seed_base=seed_base)
        if p1:
            stats["n_ok_para1"] += 1
        if p2:
            stats["n_ok_para2"] += 1
        if p1 and p2:
            stats["n_both_ok"] += 1
        manifest[uid] = {
            "unique_id": uid,
            "source_text": text,
            "para1": p1 or "",
            "para2": p2 or "",
            "usable": bool(p1 and p2),
        }
        if (idx + 1) % 50 == 0 or idx == len(items) - 1:
            print(f"[para-gen] {idx+1}/{len(items)} ok1={stats['n_ok_para1']} ok2={stats['n_ok_para2']} "
                  f"both={stats['n_both_ok']}", flush=True)
    stats["unusable_fraction"] = 1.0 - stats["n_both_ok"] / max(1, stats["n_items"])
    return manifest, stats
