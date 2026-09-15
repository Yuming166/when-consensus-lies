#!/usr/bin/env python3
"""Round-7 W2b G0: relay capability probe (models list + 3 minimal chat calls)."""
from __future__ import annotations
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))
from relay_client import RelayChatClient, write_json

def main() -> int:
    client = RelayChatClient(HERE / "cache", model="gpt-6-astra")
    try:
        models = client.probe_models()
    except Exception as e:
        write_json(HERE / "run_summary_healthcheck.json",
                   {"stage": "healthcheck", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"HEALTHCHECK FAIL: {e}")
        return 1
    probes = []
    ok = True
    for i in range(3):
        try:
            r = client.call([{"role": "user", "content": f"Reply with the single word ok (probe {i})."}],
                            seed=100 + i, model="gpt-6-astra", temperature=0.0, max_tokens=16)
            probes.append({"i": i, "ok": r.http_status == 200 and "ok" in r.content.casefold(),
                           "http_status": r.http_status, "model": r.model, "cache_hit": r.cache_hit})
        except Exception as e:
            probes.append({"i": i, "ok": False, "error": f"{type(e).__name__}: {e}"})
            ok = False
    primary_available = any(p.get("ok") for p in probes) and "gpt-6-astra" in models.get("models_available", [])
    summary = {"stage": "healthcheck", "ok": ok and primary_available,
               "models_available_has_gpt6_astra": "gpt-6-astra" in models.get("models_available", []),
               "models": models, "probes": probes}
    write_json(HERE / "run_summary_healthcheck.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
