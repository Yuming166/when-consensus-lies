#!/usr/bin/env bash
set -euo pipefail
BASE=/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call
V1=$BASE/pecr_crossmodel_deepseek_v1_20261001
V2=$BASE/pecr_crossmodel_deepseek_v2_complete_20261001
MAN=$BASE/pecr_bidirectional_development_v1_20260928/data/construction_manifest_dev_train.jsonl
V32=$BASE/pecr_trd_delta_method_development_v3_20260926/v3_2
cd "$V2"
python3 src/assemble_v2.py
python3 src/make_deepseek_labels_v2.py
python3 "$BASE/pecr_bidirectional_transformer_development_v1_20260928/src/prepare_bidirectional.py" \
  --manifest "$MAN" --ledger data/merged_ledger_v2.jsonl \
  --labels data/labels_deepseek_v2.csv \
  --feature-npz "$V32/data/features_prelabel.npz" \
  --row-map "$V32/data/feature_row_map.jsonl" \
  --outdir data/parsed_deepseek_v2
python3 "$BASE/pecr_curve_feature_development_v2_audit_20260928/src/run_curve_hgb_audited.py" \
  --features data/parsed_deepseek_v2/labeled_features.jsonl \
  --outdir results/within_deepseek_v2
python3 "$V1/src/run_transfer.py" results/transfer_v2 data/parsed_deepseek_v2/labeled_features.jsonl
echo ANALYSIS_V2_DONE
