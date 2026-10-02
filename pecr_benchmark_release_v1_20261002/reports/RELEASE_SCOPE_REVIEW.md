# Independent release scope review

PASS for the documented benchmark scope, executable input reconstruction,
future-generation policy interfaces, unknown-status preservation, and notice
attribution. This is a scope review, not final numerical acceptance. At this
review snapshot the four added native methods have real OOF and a recorded
20 completed fits; the final clean 90-fit run has not started. A complete release
success must be stated only after that separate gate and final assembly pass.

The review added only this report and `audit/release_scope_review.json`. It did
not fit an estimator, call a model, export a private payload, decode TRAIN/gold or
holdout, read a raw response ledger, or edit existing intervention files. The
original eleven-file intervention seal still matches.

## Two executable scopes and their claim boundaries

The numerical entry is self-contained for saved historical-response error ranking.
Qwen's aligned exported support is 2,142/452 with 1,699 errors and 443 correct;
DeepSeek's aligned support is 2,050/448 with 1,257 errors and 793 correct. The
shared-Qwen DeepSeek track has the same target queue but remains an explicitly
historical feature-origin comparison. Response-aware G is not a pure structural
baseline; Graph-only uses one answer, while Raw/Curve use three. The data card
correctly avoids equal-call, causal, untouched-confirmation, new-model
performance, official FinQA score, and review-score guarantees.

The intervention entry reconstructs actual original/positive/negative model
inputs. The expected and observed canonical request hashes independently agree
for every one of the 13,350 released comparisons, with no duplicate or missing
keys. Both origins cover 2,225 requested IDs and three worlds. This supports the
complete **saved intervention input reconstruction** claim. It does not establish
HTTP wire identity, semantic validity of edits, future response correctness, or
new-model effectiveness. The frozen program-conditioned edit/direction descriptors
are reused without rebuilding or executing programs.

`src/rebuild_worlds.py` defaults to hash-only auditing. Its explicit
`--write-local-inputs /absolute/new/private/directory --profile qwen|deepseek
--model NEW_MODEL` mode creates locally usable requests without sending them.
The command is documented, confines financial evidence to a new directory outside
the release, refuses existing paths, and separates optional new-model
configuration from saved-profile exact checks. This review did not execute that
private export. The source has no network/model client or subprocess import.
The retained exact profiles correctly use Qwen 384 tokens and DeepSeek 8,192 with
`reasoning_effort=low`, despite the older DeepSeek collector docstring.

## Future-generation dependencies and interfaces

The previously missing pure dependencies are now bundled under `src/frozen/`:
byte-identical G96 and Decimal label policy, plus an AST-exact projection of
`parse_num`, `norm_unit`, and `parse_resp`. Their source hashes match the frozen
export. The numerical entry remains separate from future label/data access.
`intervention/NEW_GENERATION_PROTOCOL.md` supplies the required staged interface;
no new-generation responses or labels were created by adding these dependencies.

All 23 synthetic checks passed. The crucial contracts are explicit:

- `label_one` returns `(correct, reason)`. Save `error=1-correct` only for known
  labels; malformed answers remain unknown. The Decimal comparison retains its
  frozen tolerance and does not rescale percentages or convert units.
- Original raw `answer_value` type, `unit`, and `confidence` feed labeling/G.
  Parser-normalized floats/units feed Raw17/Curve33; they are not substituted into
  the original-response feature record.
- The historical parser can return NaN/Inf. A separate finite numerical/matrix
  gate must mark `nonfinite_numeric` invalid; a parser return alone is not strict
  eligibility. The frozen functions were not silently changed.
- G96 is built using `_safe`/`_graph`, returns float32, and persists those exact
  values as float64. The hashed-text `FrozenFeatureBuilder.transform` is outside
  this benchmark. Supporting evidence is validated but does not affect G96.
  Original-only field restrictions and genuine response failures remain visible.
- New responses require new generation-bound labels, G96, parse coverage, strict
  queue and group folds. Neither historical labels nor response-aware G can fill
  changed-answer rows. The future strict queue is not locked to old cohort sizes.

There is no remaining indispensable small-code dependency missing from the input
reconstruction or frozen policy contract. An external model caller and separately
versioned response ingestion/label execution are intentionally outside this
release; the data card says so. Input reconstruction and pure helpers must not be
represented as an already executed new-model end-to-end benchmark.

## Coverage and phase history

The existing two-track full coverage contains 2,241 unique IDs per track. Qwen
partitions are 2,142 strict, 52 valid/unlabeled, 7 invalid/labeled, 24
invalid/unlabeled and 16 unrequested. DeepSeek shared partitions are 2,050, 54,
79, 42 and 16 respectively. Every source-recorded collection status is still
unknown; offline parse success and HTTP 200 do not rewrite it as success.
The intervention frame also keeps all 16 exclusions as unknown for every
origin/world. Empty/unequal units remain diagnostic rather than a new primary
filter.

`reports/AS_BEFORE_SCOPE_MAP.md` correctly maps the preserved earlier 70-fit scope
and incomplete-native inventory to their historical phase. The aligned registry
is defined by `protocol/ALIGNED_TRACK_SPEC.json` and the completed native suite,
with the final manifest/refit/coverage registry to follow. The new six-method native
OOF exists and is finite for all 2,050 rows; runtime records 20 completed fits.
It is a post-hoc suite completion, not a recovered historical reference.

The final 90-fit acceptance and linked final registry/coverage/report paths were
pending at this snapshot. The root's final report must supply their actual
outcomes before publishing the package. Statements in README/data card about
final exact clean refitting must be treated as intended final-release text until
that gate passes; this scope report does not retroactively certify it.

## Attribution and license scope

The locally retained FinQA notice is MIT with copyright 2021 Zhiyu Chen, matching
the [official upstream LICENSE](https://raw.githubusercontent.com/czyssrs/FinQA/main/LICENSE)
checked during this review. The new project notice identifies 2026 PECR benchmark
contributors. Both notices are retained; the data card limits the release license
to supplied code/derived artifacts and keeps separately acquired evidence under
its upstream terms. This is appropriate factual attribution for this package.
The notice is not a legal guarantee or independent certification of all copyright
ownership or underlying financial-evidence rights. No financial bodies are
bundled or relicensed by the reconstruction workflow.

Machine-readable facts, policy tests, reviewed input hashes and the pending final
acceptance gates are in `audit/release_scope_review.json`.
