#!/usr/bin/env python3
"""Round-7 W2 shared relay client: OpenAI-compatible chat via private relay.
Content-addressed cache + transport retry + HTTP/token stats. Key in-memory only.
Mirrors Round-6 RelayChatClient, parameterized for temperature/max_tokens/seed.
"""
from __future__ import annotations
import hashlib, json, os, re, time
from dataclasses import dataclass, field
from pathlib import Path
import urllib.error, urllib.request

RELAY_BASE = "https://openapi.center/v1"
DEFAULT_MODEL = "gpt-6-astra"
FALLBACK_MODELS = ("gpt-5.6-sol", "gpt-5.5")
MAX_TRANSPORT_ATTEMPTS = 3
BACKOFF = (2.0, 4.0, 8.0)
MAX_RESPONSE_BYTES = 1_000_000


def load_key() -> str:
    k = os.environ.get("OPENAPI_CENTER_API_KEY")
    if k:
        return k
    cfg = Path.home() / ".codex" / "private.config.toml"
    m = re.search(r'experimental_bearer_token\s*=\s*"([^"]+)"', cfg.read_text(encoding="utf-8"))
    if not m:
        raise RuntimeError("no relay key (env OPENAPI_CENTER_API_KEY or private.config.toml)")
    return m.group(1)


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass
class ChatResult:
    content: str
    model: str
    usage: dict
    http_status: int
    latency_seconds: float
    cache_hit: bool
    cache_key: str
    attempt_http: list = field(default_factory=list)


class RelayChatClient:
    def __init__(self, cache_dir: Path, model: str = DEFAULT_MODEL, timeout: float = 180.0,
                 key: str | None = None) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = model
        self.timeout = timeout
        self.key = key if key is not None else load_key()
        self.endpoint = RELAY_BASE + "/chat/completions"
        self.stats = {"http": {}, "transport_retries": 0, "cache_hits": 0, "errors": 0,
                      "models_seen": {}}

    def _post(self, payload) -> tuple[str, str, dict, int, float]:
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
            return (detail[:500], payload["model"], {}, e.code, time.monotonic() - started)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise RuntimeError(f"transport: {e}") from e
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("response exceeded 1MB")
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        return (content, str(data.get("model", payload["model"])), dict(data.get("usage") or {}),
                status, time.monotonic() - started)

    def call(self, messages, *, seed: int, model: str | None = None,
             temperature: float = 0.0, max_tokens: int = 160) -> ChatResult:
        model = model or self.model
        payload = {"model": model, "messages": list(messages),
                   "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
        material = {"endpoint": self.endpoint, "request": payload}
        key = hashlib.sha256(canonical_json(material).encode()).hexdigest()
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            cached = json.loads(path.read_text(encoding="utf-8"))
            self.stats["cache_hits"] += 1
            return ChatResult(content=str(cached["content"]), model=str(cached["model"]),
                              usage=dict(cached.get("usage") or {}),
                              http_status=int(cached.get("http_status", 200)),
                              latency_seconds=0.0, cache_hit=True, cache_key=key)
        last_err: str | None = None
        attempt_http: list = []
        for attempt in range(MAX_TRANSPORT_ATTEMPTS):
            try:
                content, resp_model, usage, status, lat = self._post(payload)
                attempt_http.append(status)
                self.stats["http"][status] = self.stats["http"].get(status, 0) + 1
                if status == 200:
                    self.stats["models_seen"][resp_model] = self.stats["models_seen"].get(resp_model, 0) + 1
                    out = {"content": content, "model": resp_model, "usage": dict(usage),
                           "http_status": status, "latency_seconds": lat, "cache_hit": False,
                           "cache_key": key}
                    self.cache_dir.joinpath(f"{key}.json").write_text(
                        json.dumps(out, ensure_ascii=False, sort_keys=True), encoding="utf-8")
                    return ChatResult(content=content, model=resp_model, usage=dict(usage),
                                      http_status=status, latency_seconds=lat, cache_hit=False,
                                      cache_key=key, attempt_http=attempt_http)
                last_err = f"http {status}: {content[:200]}"
                # Relay reports transient upstream failures as HTTP 400 "Upstream request failed";
                # treat those as retryable (documented adaptation), other 400s as permanent.
                if status == 400 and "upstream" not in content.casefold():
                    raise RuntimeError(f"HTTP {status}: {content[:300]}")
                if status not in (429, 400, 500, 502, 503, 504):
                    raise RuntimeError(f"HTTP {status}: {content[:300]}")
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                self.stats["errors"] += 1
            if attempt < MAX_TRANSPORT_ATTEMPTS - 1:
                time.sleep(BACKOFF[min(attempt, len(BACKOFF) - 1)])
                self.stats["transport_retries"] += 1
        raise RuntimeError(f"transport failed after {MAX_TRANSPORT_ATTEMPTS} attempts: {last_err}")

    def probe_models(self) -> dict:
        req = urllib.request.Request(RELAY_BASE + "/models", method="GET")
        req.add_header("Authorization", "Bearer " + self.key)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return {"status": r.status, "models_available": sorted(d["id"] for d in data.get("data", []))}


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
