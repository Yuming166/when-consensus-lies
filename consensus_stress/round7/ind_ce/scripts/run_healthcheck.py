#!/usr/bin/env python3
"""Round-7 W2 capability gate: GET /v1/models + 3x minimal PONG chat (max_tokens 16)."""
import json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))
from relay_client import RelayChatClient, write_json

def main() -> int:
    client = RelayChatClient(HERE / "cache", model="gpt-6-astra")
    models = client.probe_models()
    probes = []
    for n in range(3):
        t0 = time.monotonic()
        try:
            r = client.call([{"role": "user", "content": "Reply with exactly: OK"}],
                            seed=20_260_914, temperature=0.0, max_tokens=16)
            probes.append({"n": n + 1, "ok": r.http_status == 200 and r.content.strip() == "OK",
                           "status": r.http_status, "model": r.model,
                           "latency_seconds": round(time.monotonic() - t0, 2)})
        except Exception as e:
            probes.append({"n": n + 1, "ok": False, "error": f"{type(e).__name__}: {e}"})
    summary = {"protocol": "cs-paper-ind-ce-20260914-round7-w2", "stage": "healthcheck",
               "relay_base": "https://openapi.center/v1",
               "models_endpoint": {"status": models["status"], "models_available": models["models_available"]},
               "primary_model": "gpt-6-astra",
               "minimal_chat": {"payload": "temperature 0, max_tokens 16", "probes": probes,
                                "consecutive_3_ok": all(p["ok"] for p in probes)},
               "timestamp": time.strftime("%Y-%m-%dT%H:%M%z")}
    write_json(HERE / "run_summary_healthcheck.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
