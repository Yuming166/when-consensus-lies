#!/usr/bin/env bash
# Round-7 W1 P0 audit: reproduce all three evidence JSONs (zero model calls, read-only).
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
for s in mirror_audit.py s_pair_diagnostic.py leakage_audit.py; do
  echo "== $s =="
  "$PY" "$s"
done
echo "ALL DONE -> consensus_stress/round7/audit/{mirror_audit,s_pair_results,leakage_audit_evidence}.json"
