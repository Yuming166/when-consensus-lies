#!/usr/bin/env python3
"""Execute the frozen ConvFinQA Stage-3 Ling DEV replication.

No retries, cache, fallback, parallel workers, or outcome-dependent selection.
The raw response artifact is append-only and this runner refuses overwrite.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "CONVFINQA_STAGE3_LING_REPLICATION_CONTRACT.json"
PROMPTS = HERE / "STAGE3_DEV_PROMPTS.jsonl"
GOLD = HERE / "STAGE3_DEV_WORLD_GOLD.jsonl"
RAW = HERE / "STAGE3_LING_DEV_RAW_RECORDS.jsonl"
STATUS = HERE / "STAGE3_LING_DEV_RUN_STATUS.json"
DECISION = HERE / "STAGE3_LING_DEV_EXECUTION_DECISION.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


def strict_output(content: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(content, str) or not content.strip():
        return None, "missing_content"
    try:
        value = json.loads(content)
    except Exception as exc:
        return None, f"invalid_json:{type(exc).__name__}"
    if not isinstance(value, dict) or set(value) != {"answer", "confidence"}:
        return None, "schema_keys_mismatch" if isinstance(value, dict) else "output_not_object"
    confidence = value.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        return None, "confidence_out_of_range"
    answer = value.get("answer")
    if answer is None or isinstance(answer, bool) or not isinstance(answer, (str, int, float)):
        return None, "answer_type_invalid"
    if isinstance(answer, str) and len(answer) > 128:
        return None, "answer_string_too_long"
    return value, None


def request_json(url: str, payload: dict[str, Any], timeout: int) -> tuple[int | None, bytes, str | None, float]:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return int(response.status), response.read(), None, time.monotonic() - started
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read()
        except Exception:
            raw = b""
        return int(exc.code), raw, f"HTTPError:{exc.code}", time.monotonic() - started
    except Exception as exc:
        return None, b"", f"{type(exc).__name__}:{exc}", time.monotonic() - started


def preflight(url: str, expected_model: str, timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            envelope = json.loads(raw.decode("utf-8"))
        models = [x.get("id") for x in envelope.get("data", []) if isinstance(x, dict)]
        return {"http_status": int(response.status), "models": models, "expected_model": expected_model, "identity_pass": int(response.status) == 200 and expected_model in models, "latency_seconds": time.monotonic() - started, "response_sha256": sha_bytes(raw)}
    except Exception as exc:
        return {"http_status": None, "models": [], "expected_model": expected_model, "identity_pass": False, "latency_seconds": time.monotonic() - started, "error": f"{type(exc).__name__}:{exc}"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="unsupported; use a new execution directory")
    args = parser.parse_args()
    if args.force:
        raise SystemExit("--force is intentionally unsupported")
    if RAW.exists():
        raise SystemExit(f"refusing to overwrite existing raw artifact: {RAW}")
    contract = load_json(CONTRACT)
    prompts = load_jsonl(PROMPTS)
    gold = load_jsonl(GOLD)
    if contract.get("status") != "FROZEN_PRE_MODEL_CALL":
        raise SystemExit("contract is not frozen pre-model-call")
    if contract.get("authorization", {}).get("model_calls_authorized") is not True:
        raise SystemExit("model calls are not authorized in the frozen contract")
    if len(prompts) != len(gold) or len(prompts) != int(contract["worlds"]["dev_worlds"]):
        raise SystemExit("prompt/gold/count mismatch")
    prompt_ids = [x["world_id"] for x in prompts]
    gold_ids = [x["world_id"] for x in gold]
    if len(set(prompt_ids)) != len(prompt_ids) or prompt_ids != gold_ids:
        raise SystemExit("prompt/gold ordering mismatch")
    expected_model = contract["model_identity"]["expected_model"]
    endpoint = contract["model_identity"]["endpoint"]
    request_contract = contract["request_contract"]
    timeout = int(request_contract["timeout_seconds"])
    pre = preflight(contract["model_identity"]["models_endpoint"], expected_model, timeout)
    if not pre.get("identity_pass"):
        raise SystemExit(json.dumps({"preflight_failed": pre}, ensure_ascii=False))
    status = {"protocol": contract["protocol"], "contract": contract["contract"], "status": "running", "endpoint": endpoint, "expected_model": expected_model, "expected_worlds": len(prompts), "model_calls": 0, "preflight": pre, "started_utc": now(), "invalid_categories": {}, "returned_models": {}, "retries": 0, "fallback": False, "workers": 1}
    write_json(STATUS, status)
    records: list[dict[str, Any]] = []
    invalid: Counter[str] = Counter()
    returned_models: Counter[str] = Counter()
    identity_drift = False
    for ordinal, prompt in enumerate(prompts):
        seed = 202609222000 + ordinal
        payload = {"model": expected_model, "messages": prompt["messages"], "temperature": request_contract["temperature"], "top_p": request_contract["top_p"], "max_tokens": request_contract["max_tokens"], "seed": seed, "response_format": request_contract["response_format"], "n": request_contract["n"], "stream": request_contract["stream"]}
        payload_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        http_status, raw_body, transport_error, latency = request_json(endpoint, payload, timeout)
        record: dict[str, Any] = {
            "protocol": contract["protocol"], "contract": contract["contract"], "cell_ordinal": ordinal, "world_id": prompt["world_id"], "item_id": prompt["item_id"], "world_label": prompt["world_label"], "prompt_kind": prompt["prompt_kind"], "input_sha256": prompt["input_sha256"], "prompt_hash": prompt["prompt_hash"], "request_seed": seed, "requested_model": expected_model, "returned_model": None, "http_status": http_status, "latency_seconds": latency, "request_payload_sha256": sha_bytes(payload_bytes), "raw_http_body_b64": base64.b64encode(raw_body).decode("ascii"), "raw_http_body_sha256": sha_bytes(raw_body), "raw_response_sha256": None, "answer": None, "confidence": None, "valid": False, "parse_error": None, "transport_error": transport_error, "retry_count": 0, "cache_hit": False, "fallback_used": False, "fresh_conversation": True, "timestamp_utc": now(),
        }
        if transport_error is not None or http_status != 200:
            record["parse_error"] = "transport_failure"
            invalid["transport_failure"] += 1
        else:
            try:
                envelope = json.loads(raw_body.decode("utf-8"))
                returned = envelope.get("model")
                record["returned_model"] = returned
                if returned is not None:
                    returned_models[str(returned)] += 1
                if returned != expected_model:
                    record["parse_error"] = "identity_drift"
                    invalid["identity_drift"] += 1
                    identity_drift = True
                else:
                    content = envelope.get("choices", [{}])[0].get("message", {}).get("content")
                    record["raw_response_sha256"] = None if not isinstance(content, str) else sha_bytes(content.encode("utf-8"))
                    parsed, error = strict_output(content)
                    if error:
                        record["parse_error"] = error
                        invalid[error] += 1
                    else:
                        record["answer"] = parsed["answer"]
                        record["confidence"] = parsed["confidence"]
                        record["valid"] = True
            except Exception as exc:
                record["parse_error"] = f"response_envelope_error:{type(exc).__name__}"
                invalid[record["parse_error"]] += 1
        append_jsonl(RAW, record)
        records.append(record)
        status["model_calls"] = len(records)
        status["invalid_categories"] = dict(invalid)
        status["returned_models"] = dict(returned_models)
        write_json(STATUS, status)
        if len(records) % 25 == 0 or len(records) == len(prompts):
            print(f"completed={len(records)}/{len(prompts)} valid={sum(bool(x.get('valid')) for x in records)}", flush=True)
        if identity_drift:
            break
    complete = len(records) == len(prompts) and not identity_drift
    status.update({"status": "complete" if complete else "aborted_identity_drift" if identity_drift else "incomplete", "finished_utc": now(), "model_calls": len(records), "invalid_categories": dict(invalid), "returned_models": dict(returned_models)})
    write_json(STATUS, status)
    decision = {"protocol": contract["protocol"], "contract": contract["contract"], "status": "STAGE3_EXECUTION_COMPLETE" if complete else "STAGE3_EXECUTION_INCOMPLETE", "all_execution_gates_pass": bool(complete and len(records) == len(gold) and not identity_drift), "model_calls": len(records), "expected_worlds": len(gold), "record_count": len(records), "schema_valid_record_count": sum(bool(x.get("valid")) for x in records), "invalid_categories": dict(invalid), "returned_models": dict(returned_models), "preflight": pre, "hypothesis_result": "NOT_EVALUATED_BY_RUNNER", "stage2_authorized": False, "claim_boundary": contract["claim_boundary"]}
    write_json(DECISION, decision)
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    if not complete:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
