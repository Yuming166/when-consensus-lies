# Round-7 W2 — Independent Counter-Evidence vs Natural vs Placebo (results)

Protocol: `cs-paper-ind-ce-20260914-round7-w2` (preregistered; cohort = first 100 items / 50 pairs of round3 selection_manifest).

Cohort analyzed: n=98 items, 50 pairs; HC (agreement>=0.8): n=96, wrong=8 (8.3%).

## 1. Three-condition flip rates (label-blind)

| condition | P(flip) | 95% CI | n (item x agent) |
|---|---|---|---|
| natural | 0.8253 | [0.7289, 0.9140] | 498 |
| ind | 0.6567 | [0.5957, 0.7183] | 469 |
| placebo | 0.5579 | [0.5114, 0.6082] | 466 |

**Delta_CE = P(flip|ind) - P(flip|placebo) = +0.0988 [+0.0300, +0.1681]** (pair-grouped bootstrap 2000, seed 20260914).
Delta_NI = P(flip|ind) - P(flip|natural) = -0.1686 [-0.2689, -0.0611].
Delta_NP = P(flip|natural) - P(flip|placebo) = +0.2674 [+0.1307, +0.3895].

Round-6 replication: our P(flip|natural)=0.8253 vs round-6 rev_flip_rate=0.8246 (abs diff 0.0007, gate<=0.15: True).

## 2. Gates

- **G3_delta_CE_gt_0**: {"point": 0.0988, "ci_lb": 0.03, "pass": true}
- **G4_placebo_le_0.30**: {"rate": 0.5579, "pass": false}

## 3. AUROC / Risk@80 on HC (risk direction: higher = riskier; pair-grouped 2000, seed 20260914+1/2)

| score | AUROC [CI] | Risk@80 reduction [CI] |
|---|---|---|
| S_natural | 0.9624 [0.9253, 0.9908] | 1.0000 [0.5263, 1.0000] |
| S_ind | 0.6985 [0.4653, 0.8694] | -0.0105 [-1.0211, 0.7639] |
| S_combined | 0.9582 [0.8824, 1.0000] | 0.7474 [0.4667, 1.0000] |
| S_placebo | 0.3286 [0.1917, 0.4518] | -0.2632 [-1.1654, 0.4770] |
| S_pair_panel_gpt | 0.9540 [0.9207, 0.9837] | 1.0000 [0.4629, 1.0000] |
| S_pair_flip_gpt | 0.9598 [0.9277, 0.9839] | 1.0000 [0.6321, 1.0000] |
| S_pair_same_gpt | 0.0402 [0.0161, 0.0723] | -0.2533 [-1.1203, 0.4699] |
| S_pair_panel_qwen | 0.7443 [0.5677, 0.9326] | 0.5263 [-0.1053, 1.0000] |

### Paired AUROC differences

- S_ind_minus_S_natural: -0.2567 [-0.5000, -0.0875] (n=72)
- S_combined_minus_S_natural: +0.0030 [-0.0766, +0.0536] (n=72)
- S_ind_minus_S_placebo: +0.2990 [+0.1161, +0.5229] (n=55)
- S_pair_panel_minus_S_ind: -0.2746 [-0.5574, -0.0797] (n=70)
- S_pair_panel_minus_S_natural: +0.0057 [-0.0118, +0.0250] (n=94)

## 4. rho(S_natural, S_ind) = 0.3223 [0.1276, 0.5377] (n=73)

## 5. OOF logistic increment (S_ind over S_natural)
- model A=S_natural: OOF AUROC 0.9448; model B=[S_natural, S_ind]: OOF AUROC 0.9716; diff +0.0269 [+0.0000, +0.0581] (HC n=72, wrong=5, pairs=42).

## 6. Interpretation

- E_ind construction: see `run_summary_audit.json` and `audit_sample.jsonl` (decision-relevance + independence gates).
- Delta_CE > 0 with CI excluding 0: True.
- Placebo clean (P(flip|placebo)<=0.30): False.
- S_ind increment over S_natural: see OOF logistic above (small-HC caveat).
