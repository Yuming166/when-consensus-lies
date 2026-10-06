# PECR two-track benchmark data card

## Intended use

This release supports two related tasks: offline ranking of saved original FinQA answers by numerical error risk, and reconstruction of the historical three-world inputs so a user can send them to a model through an external client. It contains separate Qwen3.5-4B and DeepSeek V4.1 Flash tracks. Labels, responses, features, strict cohorts, and results are track-specific; do not pool them as a common target.

“Re-callable” here means the original, positive, and negative request objects can be rebuilt and checked against the historical request hashes. The package does not contain a model API client, credentials, model weights, or a fixed provider checkpoint. It cannot guarantee that a later call to a mutable model alias reproduces historical answers.

## Population and observed coverage

The benchmark uses previously explored, program-conditioned FinQA TRAIN questions, not an untouched new-question test set. The released two-track cohort contains all 1,699 Qwen attempts and all 1,597 DeepSeek attempts. DeepSeek's attempted IDs are a subset of the Qwen cohort. The strict offline risk queues contain 1,597 Qwen rows (413 groups; 1,258 errors and 339 correct answers) and 1,537 DeepSeek rows (407 groups; 837 errors and 700 correct answers). Their 1,537 shared strict items have 449 model-specific label disagreements; therefore cross-track labels and AUROCs are not pooled or treated as paired model performance.

The intervention package preserves every observed model/world status and reconstructs the request objects for 5,097 Qwen and 4,791 DeepSeek model/world slots. The accompanying `coverage/construction_frame_2241.csv` retains the wider frame: 2,225 requested construction candidates plus 16 items that were never requested. Re-callable inputs are provided only for the actual reviewed/model-attempted Qwen 1,699-item cohort and the DeepSeek 1,597-item subset; other construction candidates remain coverage records, not completed or attempted interventions.

## Construction review

The supplied review record reports `Valid` for all 1,699 constructed items. The user reported that one reviewer (`reviewer1`) completed the review on 2026-10-06; the reviewer/date attribution is user-reported, and the supplied CSV's reviewer/date cells are blank. This is a single-rater review; no second independent review or documented blinding procedure is claimed.

Of the 1,699 items, 1,655 have inherited frozen direction status and 44 remain `REQUIRES_HUMAN_REDERIVATION`. The 44 direction-pending items are outside both strict risk-prediction cohorts. Their historical inputs can still be reconstructed; their direction should not be described as independently revalidated.

## Three-world reconstruction

Provide the exact FinQA TRAIN JSON with SHA-256 `49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6`. The reconstruction script decodes only `id`, `qa.question`, `pre_text`, `post_text`, and `table`; gold answers and programs are skipped without being decoded. It restores the frozen edits from `intervention/edit_spec.jsonl` (described by `intervention/schema.json`), builds requests from `intervention/prompt_templates.json`, and checks the saved request hashes. The local audit verified **9,888 / 9,888** request hashes: 5,097 for Qwen and 4,791 for DeepSeek. This check makes no API call and does not read labels, OOF predictions, or holdout data.

The public package does not include complete financial records or instantiated prompts. It contains table-cell updates and compact text-span patches, which include the short source-derived fragments needed to restore dependent textual changes. The optional exporter writes full requests using the supplied FinQA source into a new private directory outside the release. Keep that export local. The package contains no model answers, raw response ledger, chain-of-thought, credentials, or checkpoints.

The Qwen track records `Qwen3.5-4B` from its collection specification; the local runtime checkpoint hash was not captured in the reconstruction audit. The DeepSeek track records the provider-reported alias `deepseek-v4.1-flash`; the exact backend checkpoint is unknown. Request-object reconstruction is verified for the saved model/configuration profiles, but exact model-output replay is not established.

## Labels and features

`error=1` denotes an incorrect saved original answer under the inherited numeric answer-comparison policy; `error=0` denotes correct. Labels were generated using FinQA TRAIN `qa.answer` in a separate stage and are distributed separately from features. No gold values or programs are included. Unknown labels stay blank and are excluded from strict fitting. These labels are not official FinQA program-execution scores.

Strict feature archives contain G96, Raw17, Curve33, and Arithmetic44. Feature order is fixed in `schemas/feature_schema.json`; duplicate historical aliases are preserved positionally. The methods use the same items, labels, groups, folds, and fixed HGB settings within each track. Paired source-group bootstrap intervals condition on the saved OOF predictions and omit training variance and earlier method-selection history.

These OOF results are development estimates on previously explored TRAIN data. They do not establish new-question independent confirmation, causal mechanism, or generalization to all model families.

## Privacy, licenses, and redistribution

The release retains the FinQA MIT license notice. It contains item IDs, source groups, hashes, numerical feature matrices, labels, OOF scores, request profiles, and compact intervention patches. It excludes full financial passages, complete table evidence, instantiated requests, raw model answers, reasoning, API credentials, and model checkpoints. The short edit fragments are source-derived; redistributors should retain the license notice and verify applicable upstream and model-provider terms before hosting or using them.

`audit/source_hashes.json` uses project-relative source names and contains no workstation absolute paths. The intervention source manifest hashes the private construction and response artifacts without redistributing them. The earlier intervention package's reconstruction evidence is not used as proof for this release; the current tracks were independently rebuilt and checked against their own saved request hashes.
