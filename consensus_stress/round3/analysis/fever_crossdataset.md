# Phase 6 — Cross-Dataset FEVER: BLOCKED at construction (data-structure mismatch)

Protocol: `cs-paper-vitaminc-2026-09-13` section 10. FEVER validation cannot provide
same-claim SUPPORTS/REFUTES natural pairs (verified: 0 same-claim pairs with both
verdicts). A near-duplicate claim-pair construction was attempted with an offline
semantic audit (Qwen judge, frozen prompt): J1 "E_S supports C_S" AND J2 "E_R refutes C_S".

## Audit result (162 judgments on 60 candidate pairs)

- J1 pass: 57/60 (E_S supports C_S) — near-duplicate SUPPORTS claims are mostly valid.
- J2 pass: 4/60 (E_R refutes C_S) — the paired REFUTES claim's evidence is almost always
  the SAME (or near-identical) sentence as E_S, so it cannot serve as natural
  counter-evidence for C_S. Only 1/60 candidate pairs passed both.
- Conclusion: FEVER validation lacks the two-evidence contrast structure that the frozen
  oracle's "reverse = natural counter-evidence swap" requires. Running the protocol on
  such pairs would not implement the oracle as specified.

## Decision

- FEVER cross-dataset: **BLOCKED at construction** (structural mismatch, empirically
  verified). No agent calls were made on FEVER; no result is claimed.
- Cross-dataset was instead run on balanced BoolQ (the instruction's second option) —
  see boolq_crossdataset.md. The BoolQ run is also a specificity boundary (synthetic
  reversal only), reported honestly.
