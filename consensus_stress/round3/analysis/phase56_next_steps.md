# Phase 5 / 6 — Next Steps (round 3)

## Phase 5 — Active consensus probing (not executed this round)
- Budget and gates did not allow an active-probing experiment after the paper-scale
  cohort, Phase 3 (9,600 calls) and Phase 6 runs.
- Design (preregistered template ready): uncertainty/stress-driven probe selection at a
  matched call budget vs fixed probing, using the Phase-3 finding that the reversal axis
  is the informative probe (synthetic reversal and removal are weak/opposite).

## Phase 6 — Cross-model (Ling-3.0-tiny) — FAILED at pipeline; next round
- Diagnosis: strict per-call JSON contract (agent_id field) not satisfiable by the tiny
  model (valid 31%). Next-round options (freeze BEFORE calls):
  1. Pre-register a model-capability parse accommodation: drop the agent_id integrity
     requirement for the second model and bind agent identity to the task-assignment
     agent_index (recorded server-side), keeping answer/confidence/citations checks.
  2. Add a frozen JSON exemplar to the prompt for the second model only.
  3. Choose a second model that satisfies the strict contract.
  The oracle, cohort, conditions, BF_q, and gates stay unchanged.

## Phase 6 — Cross-dataset — honest negatives retained
- FEVER: BLOCKED at construction (no natural same-claim counter-evidence; audit 1/60).
  A future design would need a dataset with genuine two-evidence contrast (e.g., a
  contrastive QA/fact-verification set built for it).
- Balanced BoolQ: FAIL (direction reversed, label subgroups opposite) — specificity
  boundary: the mechanism is specifically natural counter-evidence responsiveness, not
  any perturbation. Good for the paper's causal interpretation.

## Open questions for the paper
- Does the mechanism transfer to a contract-capable second model (Ling-3.5-class or a
  small instruction-tuned model with reliable JSON output)?
- Can stress area / breakpoint replace BF_q as the primary feature (they agree: 0.948 vs
  0.943) with a single protocol that measures both in one pass?
