#!/bin/bash
# run_agent.sh <workstream_name> <prompt_file>
# Model fallback: gpt-6-astra -> gpt-5.6-sol -> gpt-5.5 -> server default (DeepSeek V4 flash)
set -u
NAME="$1"; PROMPT_FILE="$2"
ROOT=/home/gaoym/when-consensus-lies-publish-20260911
LOG="$ROOT/consensus_stress/round6/run_logs/$NAME.log"
ST="$ROOT/consensus_stress/round6/run_logs/$NAME.status"
mkdir -p "$(dirname "$LOG")"
cd "$ROOT"
log(){ echo "[$(date '+%F %T')] $*" >> "$LOG"; }
probe(){ # $1=model ; 0=ok
  timeout 45 codex exec --skip-git-repo-check -c model_provider=astra -m "$1" \
    -c model_reasoning_effort=low \
    -c model_catalog_json=/home/gaoym/.codex/astra-model-catalog.json \
    -c model_context_window=1050000 -c model_auto_compact_token_limit=940000 \
    "Reply with exactly: OK" >/dev/null 2>&1
}
run_agent(){ # $1=model | 'default'
  if [ "$1" = "default" ]; then
    codex exec "$PROMPT" >> "$LOG" 2>&1
  else
    OPENAPI_CENTER_API_KEY="${OPENAPI_CENTER_API_KEY:-}" codex exec --skip-git-repo-check \
      -c model_provider=astra -m "$1" -c model_reasoning_effort=high \
      -c model_catalog_json=/home/gaoym/.codex/astra-model-catalog.json \
      -c model_context_window=1050000 -c model_auto_compact_token_limit=940000 \
      "$PROMPT" >> "$LOG" 2>&1
  fi
}
PROMPT="$(cat "$PROMPT_FILE")"
CHOSEN=""
for m in gpt-6-astra gpt-5.6-sol gpt-5.5; do
  log "probe $m ..."
  if probe "$m"; then CHOSEN="$m"; log "probe OK -> $m"; break; fi
  log "probe FAIL $m"
done
if [ -z "$CHOSEN" ]; then CHOSEN="default"; log "all relay probes failed -> server default (deepseek)"; fi
echo "model=$CHOSEN start=$(date '+%F %T')" > "$ST"
log "run agent $NAME with model=$CHOSEN"
run_agent "$CHOSEN"
RC=$?
if [ "$CHOSEN" != "default" ] && [ "$RC" -ne 0 ]; then
  log "relay run failed rc=$RC; fallback to default"
  echo "model=default-fallback start=$(date '+%F %T')" > "$ST"
  run_agent default
  RC=$?
fi
echo "finish=$(date '+%F %T') rc=$RC" >> "$ST"
log "agent $NAME finished rc=$RC"
exit $RC
