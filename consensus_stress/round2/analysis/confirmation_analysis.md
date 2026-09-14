# Confirmation Cohort — Corrected Direction-Consistent Gate (VitaminC, Qwen3.5-4B)

Protocol: `cs-pilot-vitaminc-conf-2026-09-13` (confirmation_preregistration.md, frozen before
any confirmation agent call). Date: 2026-09-13. Model: Qwen3.5-4B @ 127.0.0.1:31518.

## 1. Integrity

- 50 fresh VitaminC natural pairs (100 items, 50 SUPPORTS + 50 REFUTES), disjoint from the
  pilot's 100 pairs and from frozen V3.16/V3.16.1 pages; contrast gates pass.
- Relevance audit 29/30 (96.7%) decision-relevant (1 flagged: Belinelli gold-noise item);
  selection stands per frozen rule.
- Paraphrase artifacts 150/150 usable; audit 20/20 meaning-preserving.
- Agent calls 2500/2500 valid (100%), first-pass 99.96%.
- Outcome firewall intact (no label fields in records/features before merge).

## 2. Population

- 94/100 high-consensus; wrong HC = 13 (13.8%): SUPPORTS 2/48, REFUTES 11/46.

## 3. Corrected gate results (risk orientation RS_q = -BF_q; higher = riskier)

| gate (frozen) | result | pass |
|---|---|---|
| pipeline >= 0.95 | 1.00 | YES |
| primary AUROC(RS_q, wrong\|HC) CI lb > 0.5, point >= 0.60 | 0.912 [0.848, 0.973] | YES |
| macro CI lb > 0.5 | 0.912 macro; CI [0.759, 0.972] | YES |
| worst-label point > 0.5 | SUPPORTS 0.788 [0.565, 0.957]; REFUTES 0.968 [0.913, 1.0] | YES |
| C1 placebo (paraphrase flip <= 0.30) | 0.050 | YES |
| C2 permutation (risk orientation) | obs 0.912 > 95th pct 0.699 | YES |
| reducibility | Spearman(RS,agreement) -0.39; Spearman(RS,conf) -0.21; AUROC at agr==0.8 = 0.70 (n=9) | YES |

## 4. Baselines and paired diffs vs RS_q

| score | AUROC [95% CI] | paired diff vs RS_q [CI] |
|---|---|---|
| RS_q = -BF_q | 0.912 [0.848, 0.973] | — |
| R_sym (frozen) | 0.846 | +0.066 [+0.005, +0.150] |
| R_PI (frozen) | 0.605 | +0.307 [+0.209, +0.416] |
| mean confidence | 0.300 | +0.612 [+0.455, +0.768] |
| agreement | 0.377 | +0.535 [+0.402, +0.705] |

All paired-diff CIs exclude 0 (RS_q significantly exceeds every baseline).

## 5. Agent-level expected-response accuracy

| condition | accuracy |
|---|---|
| paraphrase | 0.950 |
| reverse (natural swap) | 0.732 |
| synthetic_reverse | 0.436 |

Consistent with the pilot: stable under preservation, responsive to natural reversal,
weakly responsive to the synthetic negation prefix.

## 6. Verdict

All 7 frozen corrected gates pass. Combined with the pilot cohort (AUROC(-BF_q, wrong) =
0.901 [0.847, 0.946] in the same frozen substantive direction), Gate 2 of round 2 is declared
PASS with two independent pre-registered cohorts. The failure of the pilot's as-written
numeric gate was a preregistration sign defect (documented in gate2_decision_pilot.md), not
an absence of signal; no sign was flipped post-hoc — the substantive direction was frozen
before any round-2 agent call.
