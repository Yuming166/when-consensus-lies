# Round-7 W2 — Independent Counter-Evidence vs Natural vs Placebo (results)

Protocol: `cs-paper-ind-ce-20260914-round7-w2` (preregistered; cohort = first 100 items / 50 pairs of round3 selection_manifest).

Cohort analyzed: n=98 items, 50 pairs; HC (agreement>=0.8): n=96, wrong=8 (8.3%).

## 1. Three-condition flip rates (label-blind)

| condition | P(flip) | 95% CI | n (item x agent) |
|---|---|---|---|
| natural | 0.8253 | [0.7289, 0.9140] | 498 |
| ind | 0.8373 | [0.7827, 0.8873] | 498 |
| placebo | 0.5442 | [0.4990, 0.5944] | 498 |

**Delta_CE = P(flip|ind) - P(flip|placebo) = +0.2932 [+0.2056, +0.3682]** (pair-grouped bootstrap 2000, seed 20260914).
Delta_NI = P(flip|ind) - P(flip|natural) = +0.0120 [-0.0581, +0.0789].
Delta_NP = P(flip|natural) - P(flip|placebo) = +0.2811 [+0.1449, +0.4008].

Round-6 replication: our P(flip|natural)=0.8253 vs round-6 rev_flip_rate=0.8246 (abs diff 0.0007, gate<=0.15: True).

## 2. Gates

- **G3_delta_CE_gt_0**: {"point": 0.2932, "ci_lb": 0.2056, "pass": true}
- **G4_placebo_le_0.30**: {"rate": 0.5442, "pass": false}

## 3. AUROC / Risk@80 on HC (risk direction: higher = riskier; pair-grouped 2000, seed 20260914+1/2)

| score | AUROC [CI] | Risk@80 reduction [CI] |
|---|---|---|
| S_natural | 0.9624 [0.9253, 0.9908] | 1.0000 [0.5263, 1.0000] |
| S_ind | 0.9830 [0.9537, 1.0000] | 1.0000 [1.0000, 1.0000] |
| S_combined | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] |
| S_placebo | 0.3111 [0.1848, 0.4341] | -0.2632 [-1.0800, 0.5263] |
| S_pair_panel_gpt | 0.9540 [0.9207, 0.9837] | 1.0000 [0.4629, 1.0000] |
| S_pair_flip_gpt | 0.9598 [0.9277, 0.9839] | 1.0000 [0.6321, 1.0000] |
| S_pair_same_gpt | 0.0402 [0.0161, 0.0723] | -0.2533 [-1.1203, 0.4699] |
| S_pair_panel_qwen | 0.7443 [0.5677, 0.9326] | 0.5263 [-0.1053, 1.0000] |

### Paired AUROC differences

- S_ind_minus_S_natural: +0.0206 [-0.0187, +0.0646] (n=96)
- S_combined_minus_S_natural: +0.0376 [+0.0104, +0.0747] (n=96)
- S_ind_minus_S_placebo: +0.6719 [+0.5526, +0.7963] (n=96)
- S_pair_panel_minus_S_ind: +0.0279 [-0.0128, +0.0714] (n=94)
- S_pair_panel_minus_S_natural: +0.0057 [-0.0118, +0.0250] (n=94)

## 4. rho(S_natural, S_ind) = 0.5664 [0.3557, 0.6945] (n=98)

## 5. OOF logistic increment (S_ind over S_natural)
- model A=S_natural: OOF AUROC 0.9553; model B=[S_natural, S_ind]: OOF AUROC 1.0; diff +0.0447 [+0.0146, +0.0842] (HC n=96, wrong=8, pairs=50).

## 6. Interpretation

- E_ind construction: see `run_summary_audit.json` and `audit_sample.jsonl` (decision-relevance + independence gates).
- Delta_CE > 0 with CI excluding 0: True.
- Placebo clean (P(flip|placebo)<=0.30): False.
- S_ind increment over S_natural: see OOF logistic above (small-HC caveat).
