#!/bin/bash
set -u
ROOT=/home/gaoym/when-consensus-lies-publish-20260911
CS="$ROOT/consensus_stress"
SESS=wcl-rev7
[ -n "${OPENAPI_CENTER_API_KEY:-}" ] || { echo "OPENAPI_CENTER_API_KEY not set"; exit 1; }
tmux kill-session -t "$SESS" 2>/dev/null || true
tmux new-session -d -s "$SESS" -n W1 "bash $CS/round7/run_agent.sh W1 $CS/round7/prompts/W1_audit.md"
tmux new-window -t "$SESS" -n W2 "bash $CS/round7/run_agent.sh W2 $CS/round7/prompts/W2_ind_ce.md"
tmux new-window -t "$SESS" -n W3 "bash $CS/round7/run_agent.sh W3 $CS/round7/prompts/W3_stress_profile.md"
tmux new-window -t "$SESS" -n W4 "bash $CS/round7/run_agent.sh W4 $CS/round7/prompts/W4_lambda_features.md"
tmux setenv -t "$SESS" OPENAPI_CENTER_API_KEY "$OPENAPI_CENTER_API_KEY"
sleep 3
tmux ls; tmux list-windows -t "$SESS"
