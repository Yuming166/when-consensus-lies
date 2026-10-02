# Generation and numeric binding acceptance

PASS for source/row binding, with explicit shared-Qwen DeepSeek feature provenance. No TRAIN/gold/holdout access, model/API call or fit was performed in this acceptance task.
This post-hoc audit binds saved artifacts; it does not independently recheck numeric-gold correctness or invent historical per-row freeze receipts.

## Qwen corrected primary
Every current-label answer hash and original response record/response hash matches generation_map and the corrected feature frame. Curve/Raw exactly reconstruct from their saved three responses and edit operands. Corrected G96 matches the current frame, whose audited builder reads the same current original fields; old responses/G are not substituted.
Support2142/452 includes1699 errors and443 correct. All2225 requested items remain visible;83 requested outside strict split52 valid-unlabeled,7 invalid-labeled and24 invalid-unlabeled, plus16 unrequested exclusions.

## DeepSeek shared primary
The existing DeepSeek label generator/receipt targets V2 merged original parsed_json.answer_value. The same source file supplies all three response worlds. Each exported strict numeric world matches those source fields after the historical parser normalization; the same saved labels bind OOF by existing real training row order.
DeepSeek per-response label hashes were not embedded in the original label CSV; their binding is added now from the saved source recipe/file/ID provenance, not falsely dated as a historical freeze. No gold was read to certify label correctness here.
Primary G96 is historical shared_Qwen, copied exactly from the saved Qwen snapshot, including saved fallback fields. It is deliberately cross-model and not target-native. Per-row origin includes the actual old label-input snapshot hash rather than substituting the actual old model answer for its default field.
Support2050/448 includes1257 errors and793 correct. The175 requested outside strict split54 valid-unlabeled,79 invalid-labeled and42 invalid-unlabeled, plus16 unrequested.

## Native availability
Existing target-native DeepSeek scores cover native Raw and native Full Curve only; shared Raw/Curve are their paired reference variants. These four saved variants have the same2050 IDs/labels/folds, and shared scores match primary OOF exactly.
Native graph-only and all three native family-removal variants do not exist. Thus native six-method coverage is incomplete; no missing method was trained, fabricated or marked successful.
A saved DeepSeek shared-G graph-only score exists in the earlier audited OOF with matching y/group support. It remains a shared-G source artifact and cannot fill a native-method cell.

## Traceability
audit/generation_binding_audit.json records source-relative paths and all inspected source hashes. coverage/ID_HASHES.json defines ordered ID hash semantics. coverage/attempted_frame JSONL/CSV contains two full2241 cohorts and per-world statuses/units, missing labels and feature-source boundary.
Raw ledgers, financial text, narrative answers, reasoning and credentials are not exported. Missing collection batches/finished timestamps remain unknown. Recorded request/response hashes retain source-recorded semantics; separately derived field hashes are explicitly labeled.
The portable release can refit from numeric artifacts; rerunning this private-source binding check requires the source tree and does not require dataset gold.
Source and numeric provenance consistency is not independent generalization, a causal mechanism, an ARR score or an acceptance guarantee.
