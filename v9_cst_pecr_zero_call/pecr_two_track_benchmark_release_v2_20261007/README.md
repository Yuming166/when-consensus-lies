# PECR two-track benchmark: risk prediction and intervention reconstruction

This release contains two model-specific FinQA tracks, Qwen3.5-4B and DeepSeek V4.1 Flash. It supports both offline prediction of saved original-answer error risk and executable reconstruction of the exact historical original/positive/negative request objects for every attempted item in these tracks.

The numerical benchmark includes fixed features, separate existing labels, source-group folds, reference OOF scores, complete observed-attempt coverage, fixed HGB settings, and a clean refit entry point. The intervention package contains text-free source hashes, compact edit patches, saved request hashes, request profiles, and a local reconstruction/export script. It makes no model or network calls.

## Offline benchmark

Use Python 3.13 and install `environment/requirements.lock`. From this directory:

```bash
python -m pip install -r environment/requirements.lock
python src/validate_release.py
python src/retrain.py --outdir outputs/refit
```

The refit trains six fixed HGB feature views on the saved folds and checks their OOF scores against the released reference. It reads no external data. Output paths must be new.

## Rebuild the three-world requests

Supply the exact FinQA TRAIN JSON used by the experiment (SHA-256 is checked by the script). The audit-only command reconstructs all 1,699 Qwen and 1,597 DeepSeek items, then compares 9,888 canonical request hashes with the saved calls:

```bash
python src/rebuild_interventions.py \
  --train /absolute/path/to/FinQA/dataset/train.json \
  --report /tmp/pecr_rebuild_audit.json
```

To export request payloads for later calls, choose a new private directory outside this release:

```bash
python src/rebuild_interventions.py \
  --train /absolute/path/to/FinQA/dataset/train.json \
  --report /tmp/pecr_rebuild_audit_export.json \
  --export-private /absolute/private/path/pecr_inputs \
  --track both
```

The export contains the financial evidence supplied by the user and is written with restrictive local permissions. It is never included in this package or sent to a model. An external caller must submit the exported requests. This package reconstructs historical request objects; it does not pin provider checkpoints or guarantee identical future model outputs.

See [DATA_CARD.md](DATA_CARD.md) for benchmark scope, review, model identity, and redistribution limits.
