#!/bin/bash
# 启动 Score-4 升分战役（A/B/C/D/E 并发，后台 tmux）
set -u
ROOT=/home/gaoym/when-consensus-lies-publish-20260911
CS="$ROOT/consensus_stress"
SESS=wcl-score4
[ -n "${OPENAPI_CENTER_API_KEY:-}" ] || { echo "OPENAPI_CENTER_API_KEY not set"; exit 1; }
tmux kill-session -t "$SESS" 2>/dev/null || true
tmux new-session -d -s "$SESS" -n A "bash $CS/round6/run_agent.sh A $CS/round6/prompts/A_prompt.md"
tmux new-window -t "$SESS" -n B "bash $CS/round6/run_agent.sh B $CS/round6/prompts/B_prompt.md"
tmux new-window -t "$SESS" -n C "bash $CS/round6/run_agent.sh C $CS/round6/prompts/C_prompt.md"
tmux new-window -t "$SESS" -n D "bash $CS/round6/run_agent.sh D $CS/round6/prompts/D_prompt.md"
tmux new-window -t "$SESS" -n E "bash $CS/round6/run_agent.sh E $CS/round6/prompts/E_prompt.md"
tmux setenv -t "$SESS" OPENAPI_CENTER_API_KEY "$OPENAPI_CENTER_API_KEY"
sleep 3
echo "=== sessions ==="; tmux ls 2>/dev/null
echo "=== windows ==="; tmux list-windows -t "$SESS" 2>/dev/null
