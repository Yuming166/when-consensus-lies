# PECR: generation-aligned historical risk and intervention reconstruction

This release has two distinct uses. **The historical-response risk benchmark**
trains an offline error ranker for saved original model answers. **The
reconstructable intervention benchmark** supplies frozen edit specifications,
prompt templates and executable local reconstruction of the original, positive
and negative model inputs. The second use is supported by actual input hash
verification, rather than inferred from numerical features or OOF predictions.
No new model responses were collected for this release.

## Data, targets and tracks

The source is a fixed FinQA TRAIN candidate frame of 2,241 unique item IDs from
453 source groups, with 2,225 requested items and 16 construction exclusions.
Source groups follow the saved source-document grouping rule, not error labels
or predictions. The two model cohorts overlap; their groups and items are not
independent samples. No 565-item holdout is included or accessed.

| Track | Role | Strict items | Groups | Error / correct | Original-response G96 |
|---|---|---:|---:|---:|---|
| `qwen_generation_aligned` | Aligned benchmark | 2,142 | 452 | 1,699 / 443 | Current three-world Qwen original |
| `deepseek_generation_aligned` | Aligned benchmark | 2,050 | 448 | 1,257 / 793 | Same DeepSeek merged three-world original |
| `deepseek_shared_qwen` | Historical feature-origin track | 2,050 | 448 | 1,257 / 793 | Historical Qwen snapshot; explicitly cross-model |

Each aligned track contains Graph-only, Raw three-world, Full Curve and the three
fixed family-removal variants. DeepSeek native Raw and Curve were already saved;
native Graph-only and the three removal variants were added as a **fixed post-hoc
suite completion**. Existing shared-G results, labels, OOF and manuscripts remain
unchanged. The archival shared Graph-only reference was verified by actual clean
refitting, not assumed to be identical merely because its parameters matched.

`error=1` means the saved original answer fails the frozen project numerical
comparison against FinQA TRAIN `qa.answer`. This is not the official FinQA program
execution score. The frozen Decimal rule uses
`abs(pred-gold) <= max(0.0001, 0.0001*abs(gold))`; percentages are not rescaled,
units are not converted, and unsupported numeric formats remain unknown.
The release uses existing labels; its acceptance stage did not decode dataset
gold. Qwen's earlier correction accessed `qa.answer` for the 2,225 requested IDs
only. Historical DeepSeek label generation had its own 2,241 dev-TRAIN-ID scope;
this is documented separately, not retroactively narrowed.

Current Qwen label-answer hashes, original record hashes and feature inputs are
joined per ID. DeepSeek's original labels did not contain per-response target
hashes: their binding is traced through the saved label-generation recipe,
label-file hash and merged source ledger. Per-ID hashes added by this audit are
explicitly post-hoc; no historical freeze date is invented. This is a source
binding audit, not an independent gold correctness audit.

## Representation and split contract

G96 contains original **input and response** information, including answer,
unit and confidence. Graph-only is not a pure structural baseline and uses one
answer; Raw and Curve use three. Comparisons with Graph-only are not equal-call
budget comparisons. Shared-Qwen G also retains its historical default response
fields and is not generation-aligned with the DeepSeek target.

Raw17 consists of the frozen raw response, confidence, unit and direction
features. Curve33 has Raw17 as its exact first 17 columns. The complete matrices
have 96 / 113 / 129 / 124 / 125 / 121 columns in method order. Each schema names
columns by both position and historical name: `answer_number_count` occurs at
indices 4 and 35 and must not be deduplicated. Family removals use the exact
published masks; their names do not imply that every input or direction signal
has been removed. Labels are separate from label-blind numerical features.

All strict methods use identical IDs, labels and five source-group folds.
GroupKFold uses five splits with no shuffling. Existing DeepSeek folds were
reconstructed post-hoc, and Qwen's corrected cohort received new post-hoc folds.
No group spans test folds. OOF predictions cover every strict row. Classification
parameters, all effective defaults, software versions and one-thread execution
are recorded. Strict matrices are finite and do not share writable memory.

## Full-frame coverage and missingness

Every attempted item is retained, including the 83 Qwen requested items outside
strict: 52 feature-valid with unknown label, 7 feature-invalid with known label,
and 24 feature-invalid with unknown label. The 16 unrequested construction
exclusions are separate. DeepSeek has 175 requested non-strict items:
54 valid/unlabeled, 79 invalid/labeled and 42 invalid/unlabeled, plus the same 16
construction exclusions. Native G96 was built only for the fixed 2,050 strict
DeepSeek rows; outside this queue it remains `not_computed`, never filled with
shared-Qwen G.

Per-world offline parser outcomes, recorded status, unit combinations, label
missingness and construction reasons remain visible in the coverage files.
Recorded status not retained in source records stays unknown even when an
offline parser succeeds. HTTP success is not answer validity. Empty or unequal
units are not silently excluded from the main queue. The optional unit-compatible
definition is three normalized units all nonempty and equal, with no conversion.

## Three-world reconstruction and later model use

The package bundles no financial passages. Supply the exact upstream FinQA
TRAIN file, identified by SHA256 in `intervention/README.md`. The lexical loader
decodes only `id`, `qa.question`, `pre_text`, `post_text`, and `table`; it skips
gold answers and programs. Saved edits and directions are fixed descriptors
from the original program-conditioned construction; candidate selection,
program execution, and semantic validity are not re-established by rebuilding.

For both saved model profiles, all 2,225 originals and their positive/negative
inputs reproduce the recorded canonical request hashes: **13,350 / 13,350**.
Both original and asymmetric historical edit formatters are retained. Sixteen
unrequested exclusions remain unknown and generate no requests.

The executable can return input payloads in memory or, when explicitly requested,
write them to a new private directory outside the release. It performs no
network requests. Actual new-model execution, response parsing and newly aligned
labels/G96/strict queues must be versioned independently. Historical labels or
response-aware G96 cannot be reused as targets/features for changed original
answers. This release establishes input reconstruction capability, not tested
effectiveness for a newly called model or an end-to-end hosted evaluation API.

## Evaluation and limits

Tables and confidence intervals are generated from saved OOF. Intervals use
paired source-group percentile bootstrap, B=2,000 and seed=20260928, with
single-class draws counted and skipped without retries. They are conditional on
the OOF predictions, do not measure training variance, and are not adjusted for
multiple comparisons or development selection. These are development/post-hoc
findings, not untouched confirmation, causal mechanism evidence, cross-dataset
generalization, or a guarantee of a paper review score. Full Curve remains the
specified method even when a removal variant has a higher point estimate.

Exact refitting was checked in a fresh venv with independently installed packages
and a moved package with no old sibling directories. The Python/Linux environment
and pinned transitive dependencies are recorded; exact identity on other
platforms or versions is not established. Prediction differences are saved if
they arise, without changing seeds, samples or old references.

## Contents, attribution and privacy

The package contains numerical model answers, labels, schemas, manifests, OOF,
code, hashes and coverage diagnostics. It excludes raw ledgers, reasoning,
financial bodies, API credentials and model checkpoints. Original source-relative
paths are provenance references, not runtime dependencies for numerical refits.
FinQA's locally verified upstream MIT notice is retained as
`intervention/FinQA_LICENSE.txt`. The release's MIT license applies to the code
and derived artifacts supplied here; separately acquired evidence retains its
upstream terms. No upload or automatic repository push was performed.
