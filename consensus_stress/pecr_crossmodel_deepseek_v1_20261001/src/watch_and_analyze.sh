#!/usr/bin/env bash
# Wait for collection to finish, then run the frozen analysis chain.
D=/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_crossmodel_deepseek_v1_20261001
while pgrep -f "run_deepseek_collection.py.*phase collect" >/dev/null; do sleep 30; done
# ensure all slot files exist before assembling
n=$(ls $D/data/full_dev/responses | wc -l)
echo "collect process exited; slot files=$n" >> $D/data/analysis.log
if [ "$n" -eq 6675 ]; then
  bash $D/src/run_analysis.sh >> $D/data/analysis.log 2>&1
  echo "ANALYSIS_CHAIN_EXIT=$?" >> $D/data/analysis.log
else
  echo "INCOMPLETE_COLLECTION n=$n -- analysis NOT run" >> $D/data/analysis.log
fi
