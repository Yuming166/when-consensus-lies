# PECR benchmark release V1 — 2026-10-02

Self-contained generation-aligned **historical-response risk benchmark**, with
an executable offline **three-world intervention reconstruction**. The two uses
and their evidence limits are defined in [DATA_CARD.md](DATA_CARD.md).

The aligned benchmark tracks are current Qwen (2,142 items / 452 groups) and
DeepSeek native G (2,050 / 448), each with six fixed methods and five folds.
DeepSeek shared-Qwen G remains a separate historical/source-comparison track.
All old sources, labels, scores, paper versions and primary outputs remain intact.
See [acceptance/FINAL_REPORT.md](acceptance/FINAL_REPORT.md) for actual checks and
complete fit accounting, including the retained first-pass export failure.

## Fresh numerical environment and reusable entry

Use Python 3.13.13 on Linux to reproduce the verified environment. From this
directory, create a new venv outside the release; no corpus, model weights, API,
ledger, FinQA gold, or old sibling directory is needed for numerical execution.
Dependencies are pinned including transitive packages.

```bash
python3 -m venv /tmp/pecr_new_environment
/tmp/pecr_new_environment/bin/python -m pip install -r environment/requirements.lock
PYTHONDONTWRITEBYTECODE=1 /tmp/pecr_new_environment/bin/python -I src/benchmark.py validate
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  /tmp/pecr_new_environment/bin/python -I src/benchmark.py retrain --outdir /tmp/pecr_new_refit
sha256sum -c SHA256SUMS.txt
```

Outputs must be new. The unified final entry runs **90 fixed fits**: the two
aligned tracks plus the historical shared-G track, six methods × five folds
each. The native/shared origin comparison reuses predictions and requires zero
additional fits. It saves row-level prediction differences, parameter/software
receipts, metrics, paired intervals, tables and hashes. It never searches seeds,
parameters or samples, and never replaces references when values differ.

To render tables again from the same saved result set, without fitting:

```bash
PYTHONDONTWRITEBYTECODE=1 /tmp/pecr_new_environment/bin/python -I src/benchmark.py tables \
  --results acceptance/clean_refit_final/RESULTS.json --outdir /tmp/pecr_new_tables
```

Both default paths and explicit `--root /absolute/path/to/moved_release` are
supported. All input dependencies resolve inside the chosen release.
Private-source audit/rebuild scripts have a different access scope and are
not imported by numerical validation or refitting.

## Reconstruction for a later model

See [intervention/README.md](intervention/README.md) for source SHA, actual saved
profiles, canonical hash definition and a private three-world payload export
command. This script needs a user-supplied FinQA TRAIN file and decodes approved
text fields only, without dataset gold/programs or holdout access.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/rebuild_worlds.py \
  --train /absolute/path/to/FinQA/dataset/train.json \
  --report /tmp/pecr_new_rebuild_receipt.json
```

Default execution checks hashes only. The optional private input exporter writes
outside this release and sends no requests. A newly called model requires a new
version of aligned responses, labels, G96, validity audit and strict queue;
historical numerical rows are not labels for changed answers.

## Files and complete coverage

| Relative path | Contents |
|---|---|
| `cohorts/qwen_generation_aligned/` | Same-generation label-blind features, labels, edit manifest, folds and schema |
| `cohorts/deepseek_generation_aligned/` | Native original G96, fixed DeepSeek target/Raw/Curve/folds |
| `cohorts/deepseek_shared_qwen/` | Historical shared-Qwen G primary, retained as source track |
| `reference/` | Explicit reference IDs/y/groups/folds/OOF, original source hashes and receipts |
| `coverage/attempted_frame.jsonl` and `.csv` | Full 2,241-item frame for Qwen and shared track, every world/status/unit/label reason |
| `coverage/native_attempted_frame.jsonl` and `.csv` | Full native-track frame; G96 `not_computed` outside its fixed strict cohort |
| `coverage/COVERAGE.md`, `NATIVE_COVERAGE.md` | Mutually exclusive partitions and support/coverage |
| `intervention/` | Frozen edits, prompt templates, input/request hashes, full-world coverage and reconstruction acceptance |
| `protocol/` | Complete effective HGB parameters and fixed post-hoc release specifications |
| `environment/` | Fresh environment proof and full pinned dependency list |
| `acceptance/clean_refit_final/` | Final clean 90-fit OOF, complete metrics/intervals/differences and automatic tables |
| `acceptance/failed_export_pass_v1/` | First 70-fit run retained with explicit report-generation failure |
| `acceptance/clean_refit_existing_v2/` | Repaired 70-fit existing-suite pass; all old predictions/points/intervals exact |
| `reports/`, `audit/` | Independent provenance, native completion, portability checks and source preservation |

Qwen's **83 requested non-strict items** are retained individually:
52 feature-valid/unknown-label, 7 feature-invalid/known-label and
24 feature-invalid/unknown-label. The 16 unrequested construction exclusions are
separate. DeepSeek has 175 requested non-strict items plus 16 unrequested.
Unknown collection status is never filled with success.

Generation-aligned labels and response-aware G96 are mandatory for the two
aligned tracks. The shared-G historical track is explicitly an exception and
must not be presented as DeepSeek-native original features. Historical per-row
label freeze hashes that never existed remain unavailable; audit-added binding
is marked post-hoc. Full details are in the data card and provenance reports.
