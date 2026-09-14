### 4.5 Cost: how many calls buy how much reliability

Using only the frozen records (zero new model calls), we vary the number of marginal stress calls added to the already-formed five-agent consensus (total = marginal + 5 original calls). Reversal-only probes use 1, 2, 5, or 10 marginal calls; risk is defined as 1 - mean natural-reversal fidelity over the first K agents, and the 10-call version additionally includes the synthetic-reverse condition. Reversal+paraphrase probes use 2, 4, or 10 marginal calls; risk is defined as 1 - mean fidelity over (paraphrase + reverse) / 2, with K = 5 recovering the frozen BF_q score function. Missing or invalid calls are treated as missing responses. Table 7 reports AUROC and Risk@80; Table 8 reports paired differences relative to the full RS_q (25 calls/item; positive = RS_q better).

**Table 7: AUROC and Risk@80 by per-item calls (pair-grouped 95% CI).**

| Method | Calls/item (marginal / total) | Qwen AUROC [95% CI] | Qwen Risk@80 [95% CI] | Ling AUROC [95% CI] | Ling Risk@80 [95% CI] |
|---|---|---|---|---|---|
| CST RS_q (proposed) | 25 / 25 | 0.943 [0.924, 0.960] | 0.846 [0.651, 0.981] | 0.896 [0.875, 0.917] | 0.422 [0.272, 0.583] |
| Reversal-only probe (1 call) | 1 / 2 | 0.873 [0.827, 0.918] | 0.750 [0.462, 0.923] | 0.851 [0.826, 0.873] | 0.296 [0.148, 0.484] |
| Reversal-only probe (2 calls) | 2 / 4 | 0.895 [0.846, 0.937] | 0.807 [0.537, 0.943] | 0.866 [0.842, 0.887] | 0.338 [0.179, 0.518] |
| Reversal-only probe (5 calls) | 5 / 10 | 0.931 [0.913, 0.948] | 0.884 [0.556, 0.981] | 0.869 [0.847, 0.891] | 0.348 [0.184, 0.526] |
| Reversal-family probe (10 calls) | 10 / 20 | 0.832 [0.796, 0.867] | 0.480 [0.295, 0.676] | 0.753 [0.729, 0.776] | 0.201 [0.054, 0.355] |
| Reversal+paraphrase (2 calls) | 2 / 4 | 0.873 [0.824, 0.918] | 0.673 [0.435, 0.904] | 0.859 [0.834, 0.882] | 0.369 [0.193, 0.490] |
| Reversal+paraphrase (4 calls) | 4 / 6 | 0.898 [0.847, 0.941] | 0.807 [0.526, 0.942] | 0.878 [0.856, 0.899] | 0.412 [0.231, 0.545] |
| Reversal+paraphrase (10 calls) | 10 / 15 | 0.943 [0.924, 0.960] | 0.846 [0.640, 0.981] | 0.896 [0.876, 0.918] | 0.422 [0.268, 0.587] |

**Table 8: Paired differences vs RS_q (RS_q - method, on the HC intersection).**

| Method | Qwen AUROC diff [95% CI] | Qwen Risk@80 diff [95% CI] | Ling AUROC diff [95% CI] | Ling Risk@80 diff [95% CI] |
|---|---|---|---|---|
| Reversal-only probe (1 call) | 0.069 [0.035, 0.109] | 0.096 [0.019, 0.251] | 0.046 [0.029, 0.064] | 0.126 [0.062, 0.167] |
| Reversal-only probe (2 calls) | 0.048 [0.017, 0.086] | 0.039 [0.000, 0.154] | 0.031 [0.016, 0.046] | 0.084 [0.031, 0.128] |
| Reversal-only probe (5 calls) | 0.012 [0.002, 0.023] | -0.039 [-0.038, 0.134] | 0.027 [0.013, 0.042] | 0.074 [0.031, 0.125] |
| Reversal-family probe (10 calls) | 0.111 [0.081, 0.139] | 0.366 [0.229, 0.487] | 0.144 [0.124, 0.164] | 0.221 [0.156, 0.296] |
| Reversal+paraphrase (2 calls) | 0.070 [0.033, 0.111] | 0.173 [0.039, 0.273] | 0.037 [0.023, 0.055] | 0.053 [0.032, 0.126] |
| Reversal+paraphrase (4 calls) | 0.045 [0.013, 0.082] | 0.039 [0.019, 0.173] | 0.019 [0.010, 0.027] | 0.011 [0.010, 0.075] |
| Reversal+paraphrase (10 calls) | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

**Findings.**

1. **The 5-call cost story is not statistically supported.** The pre-registered adoption rule required reversal-only(5) to be no worse than RS_q on paired AUROC (CI lower bound <= 0) before adopting the 5-call story. The paired AUROC difference CI excludes 0 for both models—Qwen +0.012 [0.002, 0.023]; Ling +0.027 [0.013, 0.042] (RS_q better)—so we cannot claim that "5 calls ≈ 25 calls." The Qwen gap is small, and Qwen reversal-only(5) is not worse on Risk@80 (paired diff -0.039 [-0.038, 0.134], CI including 0; point estimates 0.884 vs 0.846). However, the AUROC result is significant for both models, and we report this negative result.
2. **The cheapest score-identical point is 10 calls/item.** Reversal+paraphrase(10) is score-identical to RS_q by construction: BF_q uses exactly the 10 scored paraphrase+reverse calls. The paired differences are 0.000 [0.000, 0.000] for AUROC and Risk@80 on both models, with identical AUROC point estimates (0.943 / 0.896). Any reduced-cost claim should therefore be stated as "10 calls/item," not 5.
3. **Adding synthetic reversal dilutes the signal.** The 10-call reversal-family probe (natural + synthetic reverse) is *worse* than the 5-call natural-only probe on both models (Qwen 0.832 [0.796, 0.867] vs 0.931; Ling 0.753 [0.729, 0.776] vs 0.869), with large, significant paired differences relative to RS_q (0.111 [0.081, 0.139] / 0.144 [0.124, 0.164]). More calls therefore do not monotonically improve reliability; the natural counter-evidence axis is the informative component.
4. **Token accounting.** Reversal-only(5) costs 2,154 / 2,176 tokens/item (prompt + completion), compared with 10,196 / 10,354 for RS_q(25) on Qwen / Ling. The cheap probe is therefore materially less expensive, even though it is not statistically equivalent in AUROC.

### 4.6 Reducibility: is RS_q a new signal or a re-weighted baseline?

To determine whether RS_q/BF_q is "just R_sym with different weights plus a paraphrase axis," we conducted a label-free reducibility audit (zero new model calls; pair-grouped bootstrap, 2,000 replicates). Algebraically, the scores share only the natural-reversal flip axis (RS_q weight -0.5 via BF_q; R_sym weight -0.3 via reverse_inertia) and use different second axes (RS_q: paraphrase faithfulness; R_sym: intervention_disagreement). Thus, "just re-weighted" is not literally accurate. Empirically, the scores overlap substantially but are not strictly reducible (Table 9).

**Table 9: Reducibility of RS_q versus R_sym.**

| Quantity | Qwen [95% CI] | Ling [95% CI] |
|---|---|---|
| Spearman(RS_q, R_sym) | 0.822 [0.787, 0.845] | 0.859 [0.822, 0.886] |
| Incremental AUROC of RS_q residualized on R_sym | 0.874 [0.784, 0.931] | 0.787 [0.743, 0.831] |
| Paired AUROC diff RS_q - R_sym | +0.051 [0.028, 0.075] | +0.078 [0.053, 0.106] |

RS_q is strongly positively correlated with R_sym (0.82 / 0.86), but the two scores are far from isomorphic. Residualizing RS_q on R_sym leaves a significant, moderate incremental AUROC (0.874 [0.784, 0.931] on Qwen; 0.787 [0.743, 0.831] on Ling; CI lower bounds well above 0.5), and the paired AUROC advantage over R_sym is confirmed by the CIs for both models (+0.051 / +0.078). Correlations with R_PI, intervention disagreement, vote agreement, and confidence are weak (|rho| <= 0.35).

**Axis decomposition.** RS_q's signal is concentrated in the natural-reversal axis (Table 10). The reverse axis alone reaches 0.931 [0.913, 0.947] on Qwen and 0.869 [0.846, 0.891] on Ling, compared with RS_q's 0.943 / 0.896, whereas the paraphrase axis alone is near chance (0.599 [0.548, 0.652] / 0.581 [0.542, 0.621]). The paraphrase axis nevertheless contributes a small but statistically significant increment (paired AUROC diff of RS_q over the reverse axis: 0.012 [0.002, 0.022] / 0.027 [0.013, 0.042], with both CIs excluding 0). Its residual incremental AUROC is only 0.284 [0.194, 0.378] / 0.317 [0.257, 0.384], below 0.5 and direction-unstable. Notably, R_sym (0.892 [0.861, 0.921] / 0.818 [0.787, 0.847]) is *lower* than the reverse axis alone because its intervention-disagreement component (weight 0.7; itself AUROC only about 0.536 / 0.475) reduces the score. RS_q's advantage over R_sym therefore reflects adding the paraphrase axis and removing intervention_disagreement.

**Table 10: Axis decomposition (pair-grouped 95% CI).**

| Quantity | Qwen [95% CI] | Ling [95% CI] |
|---|---|---|
| RS_q AUROC | 0.943 [0.924, 0.960] | 0.896 [0.875, 0.917] |
| Reverse axis (-rev_flip_rate) AUROC | 0.931 [0.913, 0.947] | 0.869 [0.846, 0.891] |
| Paraphrase axis (-bf_paraphrase) AUROC | 0.599 [0.548, 0.652] | 0.581 [0.542, 0.621] |
| Paired diff RS_q - reverse axis | 0.012 [0.002, 0.022] | 0.027 [0.013, 0.042] |
| Paired diff RS_q - paraphrase axis | 0.344 [0.295, 0.393] | 0.316 [0.282, 0.349] |
| Residual incremental AUROC of RS_q over reverse axis | 0.284 [0.194, 0.378] | 0.317 [0.257, 0.384] |
| Residual incremental AUROC of RS_q over paraphrase axis | 0.921 [0.901, 0.941] | 0.855 [0.828, 0.880] |

**Honest conclusion.** RS_q is *partially reducible* to the natural-reversal axis that R_sym already captures at weight 0.3; it is **not** an independent new heuristic. We therefore frame the mechanism as follows: *errors are correlated with near-duplicate natural pairs, and the natural counter-evidence axis can pre-outcome-predict consensus errors*. RS_q's relative gain over R_sym is the small paraphrase-axis increment (paired AUROC +0.05 / +0.08, both significant). We do not claim a fundamentally new signal beyond the reversal axis plus this small paraphrase increment.

### 4.7 Label balance: SUPPORTS vs REFUTES

Because a label-symmetric construction does not imply symmetric error rates (Qwen: 2.5% on SUPPORTS vs 20.4% on REFUTES; Ling: 4.4% vs 38.1%; an 8.3-8.7x ratio), we report per-label AUROC/Risk@80 as the primary view (Table 11). The pooled estimate is interpreted as REFUTES-dominated by error composition: REFUTES accounts for 89.2% / 89.1% of the HC error mass and 89.3% / 88.9% of the pooled AUROC concordant mass on Qwen / Ling.

**Table 11: Per-label AUROC / Risk@80 (label-internal Risk@80).**

| Model | Label | n | Wrong (rate) | AUROC [95% CI] | Risk@80 [95% CI] (label-internal) |
|---|---|---|---|---|---|
| Qwen | SUPPORTS | 283 | 7 (2.5%) | 0.917 [0.819, 0.999] | 0.642 [0.165, 1.000] |
| Qwen | REFUTES | 284 | 58 (20.4%) | 0.986 [0.973, 0.995] | 0.871 [0.687, 0.976] |
| Qwen | pooled | 567 | 65 (11.5%) | 0.943 [0.924, 0.960] | 0.846 [0.638, 0.981] |
| Ling | SUPPORTS | 296 | 13 (4.4%) | 0.881 [0.834, 0.928] | 0.807 [0.283, 0.904] |
| Ling | REFUTES | 278 | 106 (38.1%) | 0.957 [0.934, 0.977] | 0.338 [0.253, 0.432] |
| Ling | pooled | 574 | 119 (20.7%) | 0.896 [0.873, 0.916] | 0.422 [0.274, 0.591] |

The signal holds within both labels: per-label AUROC is significantly above 0.5 in every cell (Mann-Whitney one-sided p < 1e-5 for both SUPPORTS cells). The SUPPORTS result is not driven by a single error: leave-one-error-out (jackknife) SUPPORTS AUROC ranges over [0.903, 0.944] on Qwen and [0.872, 0.886] on Ling, with every value above 0.8. Qwen's 7 SUPPORTS errors all fall in the highest-risk 27% of that label (5/7 in the top 11%), and Ling's 13 errors average the 89.4th risk percentile. Because Qwen has only 7 SUPPORTS positives, we gate and report the worst label at the CI level (both CI lower bounds > 0.5: 0.819 / 0.834). We do not claim that SUPPORTS is significantly harder than REFUTES for Qwen because the per-label AUROC difference CI includes 0 (-0.069 [-0.169, +0.007]); for Ling, the difference CI excludes 0 (-0.076 [-0.133, -0.021]).

**Error-rate-matched diagnostic (post-hoc sensitivity, not a gate).** Equalizing the two labels' error counts—by matching SUPPORTS up to the REFUTES error count (58 / 106 per label) or reducing both to the SUPPORTS count (7 / 13)—keeps pooled AUROC at about 0.92 on Qwen and 0.875 on Ling (matched-up: 0.919 [0.903, 0.935] / 0.875 [0.863, 0.887]; matched-down: 0.920 [0.868, 0.958] / 0.875 [0.842, 0.909]), with CI lower bounds >= 0.84. The pooled 0.943 is partly elevated by the near-perfect rankability of the 58 REFUTES errors (per-label 0.986). Nevertheless, the ordering signal is strong within each label and is not an artifact of label imbalance.

### 4.8 Large-model single point (gpt-6-astra)

As a single-point check with a larger GPT-class model, we ran the frozen protocol on the first 50 pairs (100 items x 5 agents x 5 conditions = 2,500 logical calls) through a relayed endpoint (`https://openapi.center/v1`). The recorded model id matches `gpt-6-astra` in all 2,483 successful records. Transport reliability was imperfect: 17/2,500 records (0.7%) are transport failures (HTTP 200 x 1,511; 429 x 826; 502 x 115; 400 x 125; 929 transport retries), while there were **0 parse failures** (no contract adaptation or JSON-exemplar escalation was needed). Two items lack complete five-agent `original` answers and are excluded by the pre-existing Round-3 feature rule, which requires all five originals to define consensus/agreement. This exclusion is label-free and does not select on outcomes, leaving 98 items with complete features, of which 96 are HC with 8 wrong (error rate 0.0833; 7 REFUTES + 1 SUPPORTS).

All within-model gates pass (Table 12): AUROC(RS_q, wrong | HC) = 0.969 [0.935, 0.995] (n = 96), Risk@80 = 1.000 [0.836, 1.000], with all 8 wrong HC items in the highest-risk 20%; placebo paraphrase flip is 0.0394; permutation is 0.9695 > 0.8942; and mechanism fidelity (correct minus wrong natural-reversal fidelity) is 0.832 [0.745, 0.928] (correct n = 88, wrong n = 8). Frozen Qwen/Ling RS_q scores transfer to gpt-6-astra's own errors at the aggregate level (Table 13), with Qwen's score transferring more strongly than Ling's, consistent with item-level Spearman (Qwen 0.6787 vs Ling 0.3656).

**Table 12: gpt-6-astra within-model gates (n = 96 HC).**

| Gate | Observed | Verdict |
|---|---|---|
| G1 pipeline validity (>= 0.95) | 0.9932 (2,483/2,500) | PASS |
| G2 primary AUROC(RS_q, wrong\|HC) | 0.969 [0.935, 0.995] | PASS (CI lb 0.935 > 0.5) |
| G3 placebo (paraphrase flip) | 0.0394 | PASS |
| G4 permutation | 0.9695 > 0.8942 | PASS |
| G5 mechanism fidelity (correct-wrong bf_reverse) | 0.832 [0.745, 0.928] | PASS |
| Risk@80 (secondary) | 1.000 [0.836, 1.000] | all 8 wrong in highest-risk 20% |

**Table 13: Frozen score transfer to gpt-6-astra errors (n = 96; secondary evidence).**

| Source score | AUROC [95% CI] | Risk@80 [95% CI] | Spearman(src RS_q, gpt RS_q) |
|---|---|---|---|
| Qwen3.5-4B (round 3) | 0.838 [0.693, 0.950] | 0.684 [-0.120, 1.000] | 0.6787 |
| Ling-3.0-tiny (round 4) | 0.737 [0.568, 0.862] | 0.211 [-0.440, 0.844] | 0.3656 |

**Honest boundaries.** This is a 100-item single point, not a full-cohort estimate. The wrong-HC count is small (n = 8), so the CIs are wide-tailed and support only the pre-registered CI-level gate (lower bound > 0.5) and the direction of the mechanism. The model is a relay GPT-class model accessed through a third-party proxy; its per-call model identity is recorded and matches `gpt-6-astra` in every successful record, but the deployment is not a local first-party environment. We claim neither per-item ranking equivalence across models nor a full-cohort large-model estimate.

### 4.9 Negative results / specificity

**BoolQ (specificity negative).** On a fresh balanced 50-yes/50-no BoolQ cohort (100 items; HC 85/100, 23 wrong, 27%), the frozen RS_q procedure yields AUROC 0.449 [0.308, 0.579]—*direction-reversed* (below 0.5)—so the cross-dataset gate fails (G2/G3/G4/G6). The label subgroups diverge (no: 0.073 [0.005, 0.169] vs yes: 0.745 [0.579, 0.889]), reproducing the answer-prior confound in risk orientation. Risk@80 is 0.239 [-0.467, 0.348] (n.s.); permutation fails (0.449 < 0.612); and RS_q is significantly *worse* than R_PI on BoolQ (paired diff -0.097 [-0.182, -0.009]). Placebo is clean (0.052), and the pipeline is 100% valid. The diagnosis is that BoolQ lacks natural counter-evidence, so the frozen oracle's reverse axis is a synthetic negation prefix, and the synthetic-reversal axis is weak/non-separating. This is a **specificity result**, not a contradiction: it supports the causal interpretation that the risk signature is specifically "unresponsive to genuine natural evidence reversal," rather than "unresponsive to any perturbation." No parser, oracle, or gate was changed; the negative result is retained.

**FEVER (blocked at construction).** FEVER validation lacks the two-evidence contrast structure required by the frozen oracle: verification found 0 same-claim pairs with both SUPPORTS and REFUTES verdicts, and an offline semantic audit of 60 near-duplicate candidate pairs (162 judgments) passed 57/60 on "E_S supports C_S" but only 4/60 on "E_R refutes C_S." Thus, the paired REFUTES evidence is almost always the same as, or near-identical to, the SUPPORTS evidence, with only 1/60 pairs passing both. Running the protocol on these pairs would not implement the oracle as specified. Therefore, **no agent calls were made on FEVER and no result is claimed**; cross-dataset evaluation was instead conducted on the balanced BoolQ split above.
