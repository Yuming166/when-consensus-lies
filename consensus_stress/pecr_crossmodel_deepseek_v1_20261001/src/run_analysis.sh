#!/usr/bin/env bash
# DeepSeek cross-model analysis driver. Run AFTER collection completes.
set -euo pipefail
D=/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_crossmodel_deepseek_v1_20261001
V=/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call
MAN=$V/pecr_bidirectional_development_v1_20260928/data/construction_manifest_dev_train.jsonl
V32=$V/pecr_trd_delta_method_development_v3_20260926/v3_2

cd $D
python3 src/run_deepseek_collection.py --manifest $MAN --outdir data/full_dev --phase assemble
python3 src/make_deepseek_labels.py
python3 $V/pecr_bidirectional_transformer_development_v1_20260928/src/prepare_bidirectional.py \
  --manifest $MAN --ledger data/full_dev/raw_ledger_full_dev.jsonl \
  --labels data/labels_deepseek.csv \
  --feature-npz $V32/data/features_prelabel.npz \
  --row-map $V32/data/feature_row_map.jsonl \
  --outdir data/parsed_deepseek
python3 $V/pecr_curve_feature_development_v2_audit_20260928/src/run_curve_hgb_audited.py \
  --features data/parsed_deepseek/labeled_features.jsonl \
  --outdir results/within_deepseek
python3 src/run_transfer.py results/transfer data/parsed_deepseek/labeled_features.jsonl
echo ANALYSIS_DONE
