# Round 4 Optional Phase 5 Pilot — Matched-Budget Active Probe Selection (offline)

Status: **FROZED before analysis**. This pilot is executed only after the Round-4
cross-model main line completed and passed. It uses no new model calls and is exploratory;
it cannot alter or rescue any Phase-6 gate.

## Data and budget

- Frozen Round-3 Qwen preoutcome features on the full 600-item cohort; evaluate on the
  567 Qwen HC items.
- Each policy uses exactly **one stress condition × 5 agents per item** (the same per-item
  call budget). No original-condition calls are recounted because both policies require the
  same original consensus anchor.
- Labels are merged only after both policy scores are fully constructed.

## Policies (label-blind)

### Active(1 probe)

Use the Phase-3-informed reversal axis for every item:

`risk_active = 1 - bf_reverse`.

The probe choice is based on the prior Phase-3 stress-axis finding, not current labels.

### Fixed(full-condition rotation)

Deterministically assign one of the four stress conditions to each item using
`sha256("round4-fixed-rotation:" + item_id) % 4`, with order
`paraphrase, reverse, synthetic_reverse, remove`. This uses the full condition set across
the cohort while matching the one-condition-per-item call budget.

Score the assigned condition as:

- paraphrase: `1 - bf_paraphrase`
- reverse: `1 - bf_reverse`
- synthetic_reverse: `1 - bf_synthetic_reverse`
- remove: `1 - rem_flip_rate`

The hash assignment is independent of labels and outcomes.

## Endpoints

On the identical Qwen HC support, report:

1. AUROC for each policy with pair-grouped bootstrap CI.
2. Risk@80 error reduction for each policy with pair-grouped CI.
3. Paired AUROC difference `active - fixed` and paired Risk@80 difference with CIs.

Primary exploratory gate: paired AUROC difference CI lower bound > 0. Secondary: paired
Risk@80 difference CI lower bound > 0. Item-level condition counts are reported.
