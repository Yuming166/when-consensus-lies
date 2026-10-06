# Three-world request reconstruction

This directory reconstructs the historical request objects for the exact Qwen3.5-4B and DeepSeek V4.1 Flash queues in this release. It carries no complete FinQA passages, saved answers, raw response payloads, reasoning, API credentials, or model checkpoints.

Supply the original FinQA TRAIN JSON with byte SHA-256:

`49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6`

Run an audit without exporting financial text:

```bash
python src/rebuild_interventions.py \
  --train /absolute/path/to/FinQA/dataset/train.json \
  --report /tmp/pecr_rebuild_audit.json \
  --hashes-out /tmp/pecr_rebuilt_request_hashes.jsonl
```

The program decodes only `id`, `qa.question`, `pre_text`, `post_text`, and `table`. It skips other JSON values lexically, including `qa.answer` and `qa.program`. It applies the saved cell edits and source-bound text-span patches, rebuilds each prompt using the recorded profile, and compares the canonical request-object hash with the saved hash. The acceptance audit matched **9,888 / 9,888** historical request hashes: 5,097 Qwen requests over 1,699 items and 4,791 DeepSeek requests over 1,597 items. The DeepSeek item IDs are a subset of the Qwen cohort. No model or network calls are made.

To prepare requests for a later external model call, write them to a new private directory outside this release:

```bash
python src/rebuild_interventions.py \
  --train /absolute/path/to/FinQA/dataset/train.json \
  --report /tmp/pecr_rebuild_export_audit.json \
  --export-private /absolute/private/path/pecr_model_inputs \
  --track both
```

The exported `inputs_<track>_<world>.jsonl` files contain full financial evidence and request payloads. Keep them private. The script sets restrictive permissions, refuses existing destinations and refuses output inside the release. It does not submit requests. The caller must separately choose an endpoint and credentials. The DeepSeek profile records only the provider-reported alias; its exact backend checkpoint is unknown. The local Qwen checkpoint hash was not preserved, so matching the request does not guarantee matching historical outputs.

## Files

- `edit_spec.jsonl`: 1,699 frozen rows with source IDs, source groups, direction status, per-world expected hashes, table-cell updates, and compact character-span patches for changed pre/post text. Original evidence passages and full edited sentences are not included.
- `schema.json`: machine-readable schema for each edit-spec row.
- `original_text_hashes.jsonl`: original input hashes binding each row to the supplied FinQA source.
- `prompt_templates.json`: exact prompt template and track-specific request-object fields.
- `saved_request_hashes.jsonl`: ID/world/track/model/status and canonical request hashes from the saved calls; no answer values or raw response text.
- `world_coverage.jsonl`: all 1,699 rows with per-world call status for both model tracks; non-attempted DeepSeek rows are explicitly `NOT_REQUESTED`.
- `source_hashes.json`: project-relative lineage hashes for construction, prompts, collectors, and saved request-hash manifests. Private source contents are not redistributed.
- `rebuilt_request_hashes.jsonl`: acceptance output for every expected historical request.
- `REBUILD_AUDIT.json`: aggregate reconstruction acceptance, source-field allow-list, and claim limits.
- `FinQA_LICENSE.txt`: upstream license notice.

This establishes local reconstruction of the saved request objects, not exact HTTP wire bytes, future model behavior, semantic validity of every intervention, or causal effectiveness.
