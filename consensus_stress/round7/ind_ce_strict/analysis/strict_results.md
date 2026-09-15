# Round-7 W2b STRICT — Independent Counter-Evidence (claim-only) vs Matched Placebo (results)

Protocol: `cs-paper-ind-ce-strict-20260915-round7-w2b` (preregistered; cohort = first 50 items / 25 pairs).

Cohort analyzed: n=49 items, 25 pairs; HC (agreement>=0.8): n=47, wrong=3 (6.4%).

## 1. Flip rates (label-blind; item x agent pairs, pair-grouped bootstrap 2000)

| condition | P(flip) | 95% CI | n |
|---|---|---|---|
| ind_strict | 0.7258 | [0.6466, 0.8115] | 248 |
| natural | 0.8434 | [0.7177, 0.9478] | 249 |
| pm | 0.5141 | [0.46, 0.5772] | 249 |

**Delta_CE = P(flip|ind_strict) - P(flip|pm) = +0.2118 [0.116, 0.3097]**
Delta_ind-natural = -0.1176 [-0.2539, 0.035]
Delta_natural-pm = 0.3293 [0.1767, 0.452]

## 2. Gates

- **G3_delta_CE_gt_0**: {"ci_lb": 0.116, "pass": true, "point": 0.2118}
- **G4_placebo_le_0.30**: {"pass": false, "rate": 0.5141}
- **G5_diag_|ind-natural|**: {"abs_diff": 0.1176}

## 3. AUROC / Risk@80 on HC (risk direction: higher = riskier; pair-grouped 2000)

| score | AUROC [CI] | Risk@80 reduction [CI] |
|---|---|---|
| R_S_ind_strict | 0.6240 [0.2857, 0.8556] | -0.2778 [-1.5556, 1.0000] |
| R_S_natural | 0.9735 [0.9118, 1.0000] | 1.0000 [0.5648, 1.0000] |
| R_S_pm | 0.3864 [0.1413, 0.6354] | -0.2703 [-1.9640, 1.0000] |
| RS_q | 0.9432 [0.8596, 1.0000] | 1.0000 [-0.2051, 1.0000] |
| R_S_combined_natural_ind | 0.9574 [0.8581, 1.0000] | 1.0000 [0.0980, 1.0000] |

### Paired AUROC differences

- combined_minus_natural: -0.0155 [-0.1413, 0.0833] (n=46)
- ind_minus_RS_q: -0.3178 [-0.6705, -0.1061] (n=46)
- ind_minus_natural: -0.3488 [-0.7143, -0.0909] (n=46)
- ind_minus_pm: 0.2481 [0.1023, 0.4565] (n=46)

## 4. rho(S_natural, S_ind_strict) = 0.0327 [-0.0442, 0.4785] (n=48)

## 5. OOF logistic increment (diagnostic)

- ind_over_RS_q: model_a AUROC 0.3217, model_b AUROC 0.4806, diff 0.1589 [-0.6848, 0.2093] (n=46)
- ind_over_natural: model_a AUROC 0.9496, model_b AUROC 0.9535, diff 0.0039 [-0.0739, 0.0465] (n=46)

## 6. Leakage audit (inference prompts, 299 rebuilt checks)

- pass: True; sha-match rate: 1.0

## 7. Interpretation

- E_ind_strict construction: claim-only dual-direction generation + offline gold assignment (see run_summary_audit.json / audit_sample.jsonl and run_summary_parser_correction.json).
- Delta_CE and gates: see section 2; placebo cleanliness is the key gate.
- S_ind_strict predictive value: AUROC/Risk@80 on HC and paired increments vs S_natural/RS_q.
- Parser correction transparency: run_summary_parser_correction.json.
