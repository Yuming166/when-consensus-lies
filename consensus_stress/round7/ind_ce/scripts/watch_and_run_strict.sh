#!/bin/bash
# Watch for gpt-6-astra recovery, then launch strict inference. Log to strict_watch.log
cd /home/gaoym/when-consensus-lies-publish-20260911/consensus_stress/round7/ind_ce
for i in $(seq 1 120); do
  OK=$(python3 - <<'PY'
import os, re, json, urllib.request, urllib.error
KEY = os.environ.get('OPENAPI_CENTER_API_KEY')
if not KEY:
    KEY = re.search(r'experimental_bearer_token\s*=\s*"([^"]+)"', open('/home/gaoym/.codex/private.config.toml').read()).group(1)
payload={"model":"gpt-6-astra","messages":[{"role":"user","content":"Reply with exactly: OK"}],"temperature":0.0,"max_tokens":16,"seed":9}
req=urllib.request.Request("https://openapi.center/v1/chat/completions", data=json.dumps(payload).encode(),
    headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
try:
    with urllib.request.urlopen(req, timeout=40) as r:
        print("OK")
except Exception:
    print("ERR")
PY
)
  echo "$(date '+%F %T') probe=$OK" >> strict_watch.log
  if [ "$OK" = "OK" ]; then
    echo "$(date '+%F %T') gpt-6-astra recovered; launching strict inference" >> strict_watch.log
    python3 scripts/run_three_conditions_strict.py >> strict_inf.log 2>&1
    echo "$(date '+%F %T') strict inference finished rc=$?" >> strict_watch.log
    exit 0
  fi
  sleep 30
done
echo "$(date '+%F %T') gpt-6-astra did not recover within watch window" >> strict_watch.log
