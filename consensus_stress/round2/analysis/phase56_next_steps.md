# Phase 5 / 6 — Next-Step Plans (not executed this round)

## Phase 5 — Active Consensus Probing (not executed)
Goal: use a limited intervention budget to select the most informative next probe
(which condition / which unit) instead of fixed probing of all conditions.
- Preregistration required: probe-selection rule (e.g., uncertainty-driven / disagreement-driven),
  budget in calls, and a frozen comparison protocol (active vs fixed-probing at matched call budget).
- The fixed-probing results of this round provide the calibration anchor (e.g., reverse-condition
  faithfulness is the strongest single axis; paraphrase is near-degenerate).
- No active-probing calls were made this round; no claims are made.

## Phase 6 — Cross-Model / Cross-Dataset Validation (not executed)
- Cross-model: run the SAME frozen protocol on a second local model (e.g., Ling-3.0-tiny at
  http://127.0.0.1:31520) with the protocol re-frozen before its calls; report per-model and
  cross-model rank correlation. No second-model calls were made this round.
- Cross-dataset: a fresh cohort on another label-symmetric verification set or a balanced
  BoolQ construction (round-1 lesson: BoolQ needs a label-symmetric design) under the same
  frozen oracle.
- These are required before any claim of generalization; currently the result is
  Qwen3.5-4B/VitaminC-only.

## Safety / discipline reminders for future rounds
- Pre-register the direction-consistent numeric gate from the start (AUROC of a risk score
  whose higher = riskier, or equivalently the sign-corrected AUROC of the faithfulness score).
- Use CI-level worst-label gates at full scale (V3.16.1 style), not point-level.
- Keep the decision-relevance audit and no-forced-response oracle as this round defined them.
