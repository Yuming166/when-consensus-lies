#!/bin/bash
# Loop: wait for gpt-6-astra healthy (2 consecutive OKs), run strict inference, repeat
# until strict valid_rate >= 0.95 or max passes reached.
cd /home/gaoym/when-consensus-lies-publish-20260911/consensus_stress/round7/ind_ce
for pass in $(seq 1 15); do
  okcount=0
  for i in $(seq 1 240); do
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
    echo "$(date '+%F %T') pass=$pass probe=$OK" >> strict_watch.log
    if [ "$OK" = "OK" ]; then okcount=$((okcount+1)); else okcount=0; fi
    if [ $okcount -ge 2 ]; then break; fi
    sleep 20
  done
  echo "$(date '+%F %T') pass=$pass launching strict inference" >> strict_watch.log
  python3 scripts/run_three_conditions_strict.py >> strict_inf2.log 2>&1
  RATE=$(python3 -c "import json; s=json.load(open('run_summary_strict_formal.json')); print(s['valid_rate'])")
  echo "$(date '+%F %T') pass=$pass valid_rate=$RATE" >> strict_watch.log
  OKB=$(python3 - <<'PY'
import json
s=json.load(open('run_summary_strict_formal.json'))
print("PASS" if s["valid_rate"] >= 0.95 else "CONTINUE")
PY
)
  if [ "$OKB" = "PASS" ]; then echo "$(date '+%F %T') strict valid_rate>=0.95 achieved" >> strict_watch.log; exit 0; fi
  sleep 20
done
echo "$(date '+%F %T') watch_loop exhausted" >> strict_watch.log
