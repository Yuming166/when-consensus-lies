# PECR final evidence freeze — 2026-09-22

## Status

`EVIDENCE_FROZEN_NO_NEW_MODEL_CALLS`

The ConvFinQA cross-task confirmatory phase is complete. The workspace now freezes the evidence boundary for writing. No new model calls, benchmark additions, probe reselection, architecture search, Ling TRAIN-fit distillation, or threshold tuning are part of this freeze.

## Main claims

1. **Cross-task PECR core signal.** Frozen S2 and full CEF retain positive discrimination of current-turn executable correctness on Qwen3.5-4B and Ling-3.0-tiny ConvFinQA DEV cohorts. This is bounded to executable financial reasoning and does not establish universal reliability.
2. **Qwen missing-probe distillation.** A Qwen TRAIN-fit response-rich student predicts the two unexecuted stronger-probe outcomes and improves S2 on frozen ConvFinQA DEV without increasing deployment calls: S2 `0.6508`, student `0.7474`, delta `+0.0966`, item-bootstrap CI `[0.0183, 0.1740]`; post-hoc source-group CI `[0.0190, 0.1736]`.
3. **Ling zero-shot transfer.** The frozen Qwen-to-Ling mapping is positive at the point estimate (`0.8275 -> 0.8536`, `+0.0262`) but both item and group bootstrap intervals cross zero. It is `suggestive practical-only`, not confirmed cross-model distillation.

## Mandatory caveats

- Full discrete CEF is a reference diagnostic, not an AUROC upper bound for the continuous imputed score.
- Ling has only `9/198` original-correct positives, `79.1%` schema-valid worlds, and `57.7%` numeric-valid worlds.
- The FinQA and ConvFinQA claims are cross-task within the executable financial-reasoning family, not arbitrary reasoning-task generalization.
- The 41-feature omission check and group-bootstrap audit are post-hoc integrity/sensitivity analyses; they do not replace the frozen endpoints.

## Audit trail

The v0.10 analyzer repair was implementation-only. The frozen contract already declared the two original-confidence fields; the repair materialized them and made the direction-sign calculation explicit. The feature-list hash remained unchanged, no forbidden outcome-derived feature appeared, and zero model calls were added.

See `FINAL_EVIDENCE_FREEZE.json` for artifact hashes and exact values.
