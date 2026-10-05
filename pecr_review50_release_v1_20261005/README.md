# PECR 50-item construction review: recovered forms and auditable sampling

**Status: forms available; completed historical judgments and adjudication not recovered.** The original packet and its exact 50-item sample are verified. The earlier “50/50 VALID” is project-lead reported only. Publishing blank forms does not close the semantic-construction-quality evidence gap.

## Start here

- [Reviewer 1 form](forms/REVIEWER1_REVIEW.csv)
- [Reviewer 2 form](forms/REVIEWER2_REVIEW.csv)
- [Adjudication form](forms/ADJUDICATION.csv)
- [Original recovered blank form](historical/BLANK_ADJUDICATION_FORM.csv)
- [Original reviewer instructions in Chinese](historical/REVIEWER_INSTRUCTIONS_ZH.md)
- [Fixed sample and edit metadata](SAMPLE_MANIFEST.jsonl)
- [Recovery and exact sampling receipt](RECOVERY_AND_SAMPLING.json)

The new forms are a separately versioned re-review instrument. They retain the original 50 IDs and order, separate positive/negative financial coherence and direction, and add failure-type and independence records. All judgments, dates and reviewer fields are intentionally blank. Completed 20-item forms found elsewhere had no sampled ID overlap and are not substituted for this review.

## Exact sampling rule

Frame: all **2,241 attempted items / 453 source groups**, including construction exclusions. Do not filter to requested, strict, correct/incorrect, or interesting-response items.

1. Retain original item order within each source group.
2. Initialize Python `random.Random(20260928)`.
3. Iterate lexicographically sorted group keys, selecting one item per group with that RNG's `choice`.
4. Shuffle the resulting 453-item list with the same RNG; take the first 50.

This exactly reproduces the historical packet's 50 IDs and their order from the published attempted-frame edit specifications. This is group-balanced sampling, not a uniform item sample; do not generalize the raw valid fraction as an unbiased item-level corpus estimate. The seed/IDs are historical; this recovery/publication was performed on 2026-10-05 and does not create a historical review completion date.

```bash
python pecr_review50_release_v1_20261005/src/verify.py
```

## Material access and blinding

Reviewers must see the question, pre/post text, all three tables, edited cell and saved operand metadata. They must not see model answers, confidence, correctness labels, gold numeric results, risk scores, or holdout items. The saved program direction is exposed: this is response/label-blind, **not direction-blind**. Judge direction appropriateness independently rather than accepting the program direction as truth.

Financial text/tables are not duplicated in this public supplement. A local private HTML/JSONL handoff can be produced from the hash-verified original packet:

```bash
python pecr_review50_release_v1_20261005/src/prepare_private_packet.py \
  --historical-packet /private/path/blind_review_packet.jsonl \
  --outdir /absolute/new/private/review50_materials
```

The output must be outside the repository. No network/model calls occur. Alternatively, obtain the exact FinQA TRAIN source and use the existing benchmark's offline three-world reconstruction entry; keep instantiated financial material private. The public form alone is not sufficient evidence for judging financial coherence.

## Fixed rubric and disposition

- Per check: `YES`, `NO`, `UNCERTAIN`.
- Overall: `VALID` only when both edits satisfy all checks; `INVALID` if a documented construction contradiction/error exists; otherwise `UNCERTAIN`.
- Failure types (semicolon-separated): `EDIT_LOCATION`, `FINANCIAL_IDENTITY`, `CROSS_TEXT_CONTRADICTION`, `UNIT_OR_SCALE`, `PERIOD_OR_ENTITY`, `DIRECTION`, `INSUFFICIENT_CONTEXT`, `OTHER`.
- Supply a concrete cell/text reference and rationale for every verdict. For `OTHER`, explain it. Retain all 50 rows; blank is pending, not uncertain or valid.
- Two reviewers complete forms independently, without sharing intermediate verdicts. Preserve raw submissions and their hashes before comparison. Report all three categories, missingness, failure-type counts and raw agreement; disagreements go to a named adjudicator with a recorded rationale. An adjudicator must not see model labels/performance.
- Report disagreement and uncertainty rather than silently excluding them. No automatic “VALID” fill, no replacement sampling, and no post-outcome rubric tuning.

A reviewer who has already inspected the sampled model responses/labels must disclose that exposure and cannot be described as independently blinded for those cases. Codex has prepared and checked the instrument, not supplied independent human judgments.

## Current support

| Sampled | Distinct groups | Completed recovered | New completed | Pending |
|---:|---:|---:|---:|---:|
| 50 | 50 | 0 | 0 | 50 |

VALID/INVALID/UNCERTAIN counts and adjudication agreement are currently **unavailable**, not 50/0/0. Existing limitations must remain until actual review records support a revision. This supplement does not modify the frozen benchmark, labels, scores, or manuscript.
