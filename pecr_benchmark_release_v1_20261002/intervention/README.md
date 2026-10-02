This directory provides an executable reconstruction of the saved three-world
model inputs, in addition to the numerical benchmark. The release contains no
financial passages, full requests, raw response ledgers, reasoning, or credentials.
Supply the original FinQA TRAIN JSON yourself; its byte SHA-256 must be
`49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6`.
The existing frozen candidate selection is used without reading or executing a
program. Only `id`, `qa.question`, `pre_text`, `post_text`, and `table` are decoded.
The scanner skips all other values lexically, including gold answers and programs.
No holdout is read. No model or network client is included.

From the release directory, run the default audit-only entry point:

```bash
python src/rebuild_worlds.py \
  --train /absolute/path/to/FinQA/dataset/train.json \
  --report /tmp/pecr_world_check_new.json \
  --request-hashes-out /tmp/pecr_world_hashes_new.jsonl
```

Output paths must be new. The script restores original, positive and negative
tables in memory, builds both saved-origin requests, and checks every canonical
request hash. It writes hashes and statuses only. Exact reconstruction was
verified locally for all 13,350 saved requests; see `REBUILD_AUDIT.json` and
`rebuilt_request_hashes.jsonl`.

| Saved origin | Original | Positive | Negative | Total exact matches |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.5-4B | 2,225 | 2,225 | 2,225 | 6,675 |
| deepseek-flash | 2,225 | 2,225 | 2,225 | 6,675 |
| Both origins | 4,450 | 4,450 | 4,450 | 13,350 |

The original text-field canonical hashes also match for all 2,225 requested IDs.
The full edit frame retains 2,241 unique IDs in its original order, across 453
source groups. Sixteen construction exclusions were never requested; their
world reconstruction/request status is `unknown_not_requested_not_reconstructed`.
They are retained in `edit_spec.jsonl` and are not manufactured as successful
requests. There are zero missing requested IDs or mismatched request hashes.

For a later model run, explicitly export the reconstructed inputs to a **new
absolute private directory outside the release**:

```bash
python src/rebuild_worlds.py \
  --train /absolute/path/to/FinQA/dataset/train.json \
  --report /tmp/pecr_local_inputs_audit_new.json \
  --write-local-inputs /absolute/private/new_model_inputs \
  --profile qwen \
  --model YOUR_NEW_MODEL_NAME
```

This optional operation creates three `inputs_<world>.jsonl` files with request
payloads and a `LOCAL_GENERATION.json` specification. Those files contain your
supplied financial evidence; keep them private and outside the public package.
Directory permissions are 0700 and files are 0600. Existing directories and
paths inside the release are refused. This release's acceptance run did not use
this option and did not create a financial-text export. Users can also import
`scan_train_text`, `build_worlds`, and `make_request` to obtain requests in memory.
The script never sends the payloads.

The `--profile` preserves the saved temperature/token configuration and changes
only the model name when `--model` is supplied. Qwen's saved profile is
`temperature=0, max_tokens=384`; DeepSeek's is
`temperature=0, max_tokens=8192, reasoning_effort=low`. The DeepSeek collector's
old docstring mentions 384, but every request in the actual merged complete
ledger uses 8192. The saved-profile exact check always uses the original model
names and configurations, independently of an optional new-model export.
Any new responses require a separately versioned generation map, labels,
original-response G96 features, parse audit, and strict queue. Historical labels
and original-response G are not valid substitutes for new responses.

Files are relative to this directory:

- `edit_spec.jsonl`: full frozen frame and saved operand old/new, cell indices,
  direction, absolute delta, construction status and exclusion flags. These are
  saved descriptors; program execution and candidate selection are not repeated.
- `prompt_templates.json`: exact generic system/user template and two actual
  saved runtime profiles; no instantiated evidence text.
- `original_text_hashes.jsonl`: hashes of selected original evidence fields.
- `saved_request_hashes.jsonl`: ID/world/origin, saved request hash, limited
  non-content source metadata, and private-source path/line references.
- `rebuilt_request_hashes.jsonl`: all expected/observed request hash comparisons.
- `world_coverage.jsonl`: all 2,241 frame rows with both origins' three-world
  reconstruction states, including the 16 unrequested unknown rows.
- `source_hashes.json`: original private source hashes and projection boundaries;
  private paths are provenance references, not dependencies of the public script.
- `REBUILD_AUDIT.json`: complete acceptance coverage and TRAIN access guard.
- `REBUILD_GUARDS.json`: lexical selection and output-path guard checks.
- `SHA256SUMS.txt`: hashes of this intervention delivery and its executable.

The positive formatter is the original V3 `mutate_surface`/`fmt_decimal`, including
currency and percent surface conventions. The negative formatter is the original
bidirectional V1 `fmt_like`, including its six-decimal rule. Both use Decimal
precision 28. Their historical formatting differences are preserved because
reconstruction is verified against actual saved requests. Canonical request
hashing uses UTF-8 JSON with `ensure_ascii=False`, sorted keys, and comma/colon
separators. This is a canonical object hash, not proof of HTTP wire byte identity.

This delivery establishes exact saved input/prompt reconstruction and executable
offline intervention rebuilding. It does not establish semantic validity of the
edits or effectiveness for a new model, and creates no new responses or labels.
