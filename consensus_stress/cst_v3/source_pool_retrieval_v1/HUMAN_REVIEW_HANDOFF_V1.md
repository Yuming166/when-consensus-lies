# CST V3 human-review handoff v1

This handoff is for two independent human reviewers. Codex has not filled any substantive review field.

## Reviewer packet

Use `FOUR_CONDITION_FULL_INPUTS_V1.csv` for the complete input text and `ATTEMPT_SOURCE_RECORDS_V1.jsonl` for every retrieved candidate and provenance field. The source snapshot labels are provenance metadata, not final V3 target states.

For each item, review the complete `A + append` input, not an isolated sentence. Record:

- A relation: support/refute/insufficient/unresolved;
- AA target;
- neutral target;
- support target;
- counter target;
- whether neutral is proposition-neutral;
- whether support/counter are directional;
- conflict and insufficient reason;
- time/source/entity/unit/scope confounds;
- final status and rationale.

## Important asymmetry

If A already supports the proposition, support is normally a maintenance condition and counter is the directional reversal. If A refutes the proposition, counter is normally maintenance and support is the directional reversal. Do not score support as a required flip for A-support items.

## Current material failures

The provisional manifest has no complete four-condition rows:

- 17 items: `SUPPORT_MATERIAL_NOT_RETRIEVED`;
- 17 items: `COUNTER_MATERIAL_NOT_RETRIEVED`.

Reviewers must preserve these failures. They must not fill missing material, treat A as its own append, or select replacements after seeing any model output.
