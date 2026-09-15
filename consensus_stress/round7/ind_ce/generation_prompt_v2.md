# Generation prompt revision — E_ind batch 2 (V2)

Date: 2026-09-14. Status: documented adaptation (NOT a silent protocol change).
The frozen `preregistration.md` remains byte-identical (hash preserved). This file records the
adopted revision of the E_ind generation prompt after the batch-1 audit.

## Batch-1 audit result (30-item deterministic sample, 60 sentences)
- Decision-relevance rate: 0.7833 (47/60) — below the pre-registered 0.80 gate.
- Independence vs E_j: token_jaccard median 0.1875 / p90 0.4286 / max 0.7917 (all within gates);
  character_ratio median 0.3744 (within 0.75); LCS token ratio max 0.8000 (one sentence > 0.75 gate).
- Diagnosis: for many REFUTE items the model generated same-polarity evidence (agreeing with the
  original evidence) instead of the required OPPOSITE conclusion. The V1 prompt ("Target
  conclusion: the claim is {target}") was followed for SUPPORT items but often ignored for
  REFUTE items.

## Adopted V2 prompt
Replaced `Target conclusion: the claim is {target}` with an explicit statement of the original
evidence's polarity and the required opposite:
- "The original evidence supports the conclusion that the claim is {orig}."
- "Construct NEW evidence that supports the OPPOSITE conclusion: the claim is {target}."
- Added: "DIRECTLY asserts a fact consistent with the claim being {target}",
  "be decision-relevant: a reader should be able to tell from the sentence alone ...",
  "use concrete facts (dates, numbers, names, attributes) rather than vague or hedged wording".
- Independence constraints unchanged (no copying E_i wording; banned meta-words/prefixes;
  output only the sentence).

Full V2 template text is in `scripts/gen_ind_evidence.py` (`USER_TEMPLATE`).
Batch-1 artifacts preserved at `e_ind_artifacts_v1_batch.jsonl`.

## Decision rule going forward
- If batch-2 audit passes all gates (relevance >= 0.80; overlap thresholds) -> proceed to smoke.
- If batch-2 audit still fails -> report honestly and proceed with the marginal gate documented
  (the inference comparison does not depend on the audit pass/fail; audit is an artifact-quality gate).
