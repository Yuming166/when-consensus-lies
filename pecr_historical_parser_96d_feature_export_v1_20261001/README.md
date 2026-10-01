# Historical parser and 96-D feature export (V1, 2026-10-01)

This is a read-only provenance export. It does **not** change any frozen manifest,
ledger, label, score, or old analysis.

## Contents

1. **Historical parser sources**
   - `parser/paired_qwen_v2/run_paired_qwen_v2.py`: historical two-world strict parser.
   - `parser/holdout_v3/run_holdout_qwen.py`: historical 565-item holdout parser source. No holdout data is included.
   - `parser/bidirectional_v1/prepare_bidirectional.py`: historical three-world strict parser/snapshot builder.
   - `parser/bidirectional_v1/test_parser.py`: synthetic parser checks.
2. **96-D graph-feature source**
   - `features_96/source/feature_builder.py` defines 96 named graph features and the historical 4,096-dimensional hashed text block.
   - `features_96/source/prepare_prelabel.py` records how the historical feature snapshot and row map were generated.
   - `features_96/source/audit_collection.py` records the historical collection/hash-chain audit.
   - `features_96/tests/test_synthetic.py` is the historical synthetic test.
3. **Real feature and ID snapshot**
   - `features_96/snapshot/features_prelabel.npz`: `X=(2241,4192)` and `graph=(2241,96)`.
   - `features_96/snapshot/feature_row_map.jsonl`: one row map record for each of 2,241 unique item IDs across 453 source groups.
   - `features_96/snapshot/feature_schema_96.json`: the ordered 96 graph-feature names.
   - `features_96/snapshot/SNAPSHOT_AUDIT.json`: generated shape, finiteness, ID alignment, and content-boundary audit.

## Interpretation boundary

The exported feature file has 4,192 total columns because the historical method
also used a 4,096-column hashed text block. The specifically named, structured
graph block is exactly 96 dimensions. The 96 feature names are in
`feature_schema_96.json`.

No raw financial report text, raw model response, raw ledger, frozen 565-item
holdout payload, model checkpoint, or credential is exported here. Source files
may retain historical endpoint/model constants, but were scanned for no bearer
token or API key.

See `manifest/EXPORT_MANIFEST.json` and `manifest/SHA256SUMS.txt` for exact
source paths and hashes.
