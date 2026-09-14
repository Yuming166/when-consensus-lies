"""Rebuild a run summary from a records file (no client state needed)."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "round3"))
import round3_lib as pl

def rebuild(records_path: Path, label: str, model: str, protocol: str) -> dict:
    records = [json.loads(l) for l in records_path.read_text(encoding="utf-8").splitlines() if l]
    http = {}
    cache_hits = 0
    retries = 0
    pt, ct = 0, 0
    first_pass = 0
    for r in records:
        n_attempts = len(r["attempts"])
        if n_attempts > 1:
            retries += n_attempts - 1
        for a in r["attempts"]:
            if a.get("cache_hit"):
                cache_hits += 1
            st = a.get("http_status")
            if st is not None and not a.get("cache_hit"):
                http[str(st)] = http.get(str(st), 0) + 1
            u = a.get("usage") or {}
            pt += u.get("prompt_tokens") or 0
            ct += u.get("completion_tokens") or 0
        if r["first_pass_valid"]:
            first_pass += 1
    return {
        "label": label, "model": model, "protocol": protocol,
        "expected_calls": len(records) * 1 if False else len(records),
        "records": len(records),
        "success": sum(1 for r in records if r["success"]),
        "valid_rate": round(sum(1 for r in records if r["success"]) / max(1, len(records)), 4),
        "first_pass_rate": round(first_pass / max(1, len(records)), 4),
        "http_stats": http, "transport_retries": retries, "cache_hits": cache_hits,
        "token_usage": {"prompt_tokens": pt, "completion_tokens": ct},
        "per_condition": {cond: {"n": sum(1 for r in records if r["condition"] == cond),
                                 "success": sum(1 for r in records if r["condition"] == cond and r["success"])}
                          for cond in pl.CONDITIONS},
    }

if __name__ == "__main__":
    path = Path(sys.argv[1]); label = sys.argv[2]; model = sys.argv[3]
    protocol = "cs-paper-gpt-singlepoint-20260914-round6"
    out = rebuild(path, label, model, protocol)
    print(json.dumps(out, ensure_ascii=False, indent=2))
