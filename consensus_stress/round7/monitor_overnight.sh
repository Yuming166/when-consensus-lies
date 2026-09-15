#!/bin/bash
# Overnight monitor: wait for W2 + W2b, then launch W5 (paper v5).
set -u
ROOT=/home/gaoym/when-consensus-lies-publish-20260911
CS="$ROOT/consensus_stress"
LOG="$CS/round7/run_logs/monitor.log"
mkdir -p "$CS/round7/run_logs"
W2_ST="$CS/round6/run_logs/W2.status"      # W2 的 wrapper 旧路径 bug
W2B_ST="$CS/round7/run_logs/W2b.status"    # W2b 用修复后的 wrapper
START=$(date +%s)
log(){ echo "[$(date '+%F %T')] $*" >> "$LOG"; }
log "monitor started; waiting for W2 and W2b (cap 10h)"
while true; do
  w2_done=0; w2b_done=0
  [ -f "$W2_ST" ] && grep -q "finish=" "$W2_ST" && w2_done=1
  [ -f "$W2B_ST" ] && grep -q "finish=" "$W2B_ST" && w2_done=1 && w2b_done=1
  if [ "$w2_done" -eq 1 ] && [ "$w2b_done" -eq 1 ]; then log "W2 and W2b finished"; break; fi
  NOW=$(date +%s)
  if [ $((NOW-START)) -gt 36000 ]; then log "10h cap reached; proceeding to W5 with available results"; break; fi
  sleep 120
done
log "launching W5 (paper v5)"
bash "$CS/round7/run_agent.sh" W5 "$CS/round7/prompts/W5_paper.md" >> "$LOG" 2>&1
log "W5 finished rc=$?"
log "monitor done"
