# ConvFinQA v0.11 freeze status (2026-09-22)

- Status: **FROZEN_PRE_MODEL_CALL_NO_MODEL_CALLS**
- Model/API calls: **0**
- Primary one-per-conversation manifests: train **1344**, dev **198**
- Source-file sensitivity manifests: train **754**, dev **114**
- Public prompt inputs and internal gold ledgers are written as separate artifacts.
- Train/dev source-file disjoint: **True**
- Primary contract is frozen before any ConvFinQA model call.

The primary unit is one eligible executable program turn per conversation, selected by earliest turn index then stable ID. One-per-source-file is retained as a sensitivity analysis because it yields only 114 dev items. Private test labels are unavailable and are not used.
