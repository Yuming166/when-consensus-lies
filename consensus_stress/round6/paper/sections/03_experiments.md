## 4. Experiments and Results

We evaluate counter-evidence responsiveness as a *pre-outcome* error signal for multi-agent consensus. All protocols were frozen before any model call; all risk scores are outcome-independent (no label fields are used before the label merge); and every reported interval is a 95% pair-grouped bootstrap interval (2,000 replicates) computed with a fixed seed base (`20260913`) and per-statistic offsets, with paired comparisons computed on the high-consensus (HC) intersection. All numbers below are reproduced from the frozen analysis artifacts listed in the repository; no figure is included.

### 4.1 Setup

**Cohort.** The main cohort is a fresh, frozen sample of 300 natural contrastive pairs (600 items) from VitaminC, label-symmetric by construction: each pair yields one SUPPORTS item and one REFUTES item (300 + 300) that share the same evidence view, prompt template, and oracle, and differ only in the mirrored evidence conclusion. Items are page- and pair-disjoint from earlier rounds (150 round-2 pairs; the frozen V3.16/V3.16.1 pages). Eligibility requires `character_ratio >= 0.85` and `token_jaccard >= 0.70` (one pair per page), with contrast medians of 0.95 / 0.84. The pipeline produced 900/900 usable paraphrase artifacts, 15,000/15,000 agent records with 14,999 valid (99.99%; one reverse call failed after retry), 30/30 meaning-preserving paraphrases, 30/30 decision-relevant audit items, and pre-outcome features frozen on all 600 items before label merge.

**High-consensus populations.** HC is defined as five-agent agreement `>= 0.8` and is fixed before evaluation. Qwen3.5-4B: 567 HC items (94.5% of 600; 298 pairs), 65 wrong (11.5%). Ling-3.0-tiny: 574 HC items (299 pairs), 119 wrong (20.7%). The two models therefore do not share a failure distribution.

**Models.** Qwen3.5-4B is the primary model; Ling-3.0-tiny is the secondary model; gpt-6-astra (a relayed GPT-class model) provides a single-point validation of 100 items. No Qwen calls were rerun for any analysis; all later rounds reuse the frozen Qwen records.

**Metrics.** The primary metric is AUROC of the risk score on the HC error indicator (`wrong | HC`). Risk@80 is the relative error reduction when retaining the lowest-risk 80% of HC items (operating point 0.8). Paired differences are computed on the HC intersection. Risk form: `RS_q = -BF_q` (higher = riskier), where `BF_q = (bf_paraphrase + bf_reverse)/2` is the expected-response faithfulness averaged over the five agents: `bf_paraphrase` is paraphrase fidelity (`1 - para_flip_rate`) and `bf_reverse` is natural-reversal fidelity (the agent flips to the oracle's expected opposite under natural counter-evidence).

**Controls.** (i) *Placebo:* the paraphrase-flip rate must stay below 0.30 so that meaning-preserving paraphrases are not themselves adversarial; observed 0.038 (Qwen) and 0.061 (Ling). (ii) *Permutation:* the observed AUROC must exceed the 95th percentile of the permuted-null distribution; Qwen 0.943 > 0.596, Ling 0.896 > 0.564. (iii) *Reducibility:* Spearman correlations against agreement/confidence must stay below 0.9 in absolute value, and the AUROC at an agreement-0.8 split must exceed 0.5 (Qwen: -0.004 / -0.161; 0.844; Ling: -0.148 / -0.050). Section 4.6 analyzes reducibility against the strongest internal baseline in detail.

### 4.2 Main results (Qwen3.5-4B)

**Gate set (8/8 PASS).** The frozen paper-scale gate set passes on all eight checks (Table 1). The primary gate is CI-level: the lower bound of AUROC(RS_q, wrong | HC) must exceed 0.5 with point estimate >= 0.60.

**Table 1: Frozen gate set, Qwen3.5-4B, VitaminC paper-scale cohort (567 HC items).**

| Gate | Frozen criterion | Observed | Verdict |
|---|---|---|---|
| G1 Pipeline validity | valid rate >= 0.95 | 0.9999 (14,999/15,000) | PASS |
| G2 Primary AUROC (CI) | CI lb > 0.5 | 0.943 [0.924, 0.960] | PASS |
| G2 Primary AUROC (point) | point >= 0.60 | 0.943 | PASS |
| G3 Macro-label AUROC | CI lb > 0.5 | 0.952 [0.904, 0.995] | PASS |
| G4 Worst-label (SUPPORTS) AUROC | CI lb > 0.5 | 0.917 [0.819, 0.999] | PASS |
| G5 Placebo (paraphrase flip) | <= 0.30 | 0.038 | PASS |
| G6 Permutation | observed > 95th pct | 0.943 > 0.596 | PASS |
| G7 Reducibility | \|Spearman\| < 0.9; AUROC(agr=0.8) > 0.5 | -0.004 / -0.161; 0.844 | PASS |

**Against internal baselines.** RS_q ranks consensus errors with AUROC 0.943 [0.924, 0.960] and cuts retained error by 84.6% at 80% coverage (Risk@80 0.846 [0.638, 0.981]). It significantly outperforms the frozen internal baselines—R_sym (0.3·reverse_inertia + 0.7·intervention_disagreement), R_PI (the frozen BoolQ provenance–intervention score), disagreement, and mean confidence—with CI-confirmed paired AUROC differences, and a strict Risk@80 gate (CI lower bound > 0) passes (Table 2). A label-blind fitted logistic over {paraphrase, reverse} (0.941 [0.922, 0.959]) ties the frozen composite (paired diff +0.002 [-0.002, +0.007] includes 0), indicating that the concept—expected-response faithfulness with decision-relevance-aware oracle—rather than extra fitting carries the signal. Isotonic calibration reduces ECE from 0.057 to 0.013 (reported; AUROC unchanged by design). The paper-scale result maintains or exceeds the round-2 baseline (AUROC 0.906 [0.865, 0.944] -> 0.943; Risk@80 0.654 -> 0.846).

**Table 2: Phase-4 comparison on Qwen HC items (n = 567). Paired diffs are RS_q minus the baseline; positive favors RS_q.**

| Representation | AUROC [95% CI] | Risk@80 [95% CI] | Paired AUROC diff [95% CI] | Paired Risk@80 diff [95% CI] |
|---|---|---|---|---|
| RS_q = -BF_q | **0.943 [0.924, 0.960]** | **0.846 [0.638, 0.981]** | — | — |
| logistic OOF {para, rev} | 0.941 [0.922, 0.959] | — | +0.002 [-0.002, +0.007] (tie) | — |
| R_sym (frozen) | 0.892 [0.861, 0.921] | 0.499 [0.273, 0.770] | +0.051 [+0.029, +0.075] | +0.347 [+0.152, +0.502] |
| R_PI (frozen) | 0.628 [0.586, 0.670] | -0.001 [-0.235, 0.271] (n.s.) | +0.315 [+0.271, +0.360] | +0.847 [+0.677, +0.984] |
| disagreement | 0.583 [0.536, 0.630] | 0.095 [-0.076, 0.388] (n.s.) | +0.360 [+0.306, +0.413] | +0.751 (point; CI n.r.) |
| confidence | 0.272 [0.226, 0.321] | -0.232 [-0.511, 0.039] (n.s.) | +0.671 [+0.620, +0.723] | +1.078 (point; CI n.r.) |

*Note: for the last two rows the frozen Phase-4 protocol reported paired Risk@80 differences as point estimates only; CIs are not reported in the artifact ("n.r."). Confidence is anti-predictive (AUROC < 0.5).*

**Label-symmetric design, asymmetric error behavior.** The construction is label-symmetric (300 SUPPORTS + 300 REFUTES items), but model behavior is not: Qwen errors on 7/283 SUPPORTS items (2.5%) versus 58/284 REFUTES items (20.4%), i.e., 8.3x more often on REFUTES, and REFUTES carries 89.2% of the HC error mass. The label-symmetric design exists precisely to expose this asymmetry: the risk signal is not an artifact of one label, and we report per-label and matched diagnostics in Section 4.7 rather than collapsing the two labels into a single claim.

### 4.3 Cross-model: Ling-3.0-tiny

**Procedure transfer with a frozen score.** The complete frozen Round-3 cohort (300 pairs / 600 items) was re-run with Ling-3.0-tiny under the same frozen evidence, oracle, conditions, `BF_q`, and `RS_q`. The only protocol adaptation was response transport: Ling no longer self-reports `agent_id`, so the task dispatcher binds the frozen agent index/persona/partition server-side and the parser validates `answer`, `confidence`, and `cited_evidence_ids`; a frozen JSON exemplar is present in every prompt. Calls were 15,000/15,000 valid (100%; first-pass 14,992/15,000 = 99.95%), with 3,000/3,000 valid calls in every condition.

**Ling within-model gate: 8/8 PASS** (Table 3). On Ling's own 574 HC items, the unchanged RS_q procedure ranks Ling's 119 errors with AUROC 0.896 [0.873, 0.916].

**Table 3: Ling within-model gate set (574 HC items).**

| Gate | Observed | Verdict |
|---|---|---|
| Pipeline validity (>= 0.95) | 1.000 (15,000/15,000; first-pass 0.9995) | PASS |
| Primary AUROC(RS_q, wrong\|HC): CI lb > 0.5, point >= 0.60 | 0.896 [0.873, 0.916] | PASS |
| Macro-label AUROC | 0.919 [0.895, 0.944] | PASS |
| Worst label (SUPPORTS) | 0.881 [0.834, 0.928] | PASS |
| Placebo (paraphrase flip) | 0.061 | PASS |
| Permutation | 0.896 > 0.564 | PASS |
| Reducibility | Spearman -0.148 (agreement) / -0.050 (confidence) | PASS |
| Risk@80 (descriptive) | 0.422 [0.274, 0.591] (CI excludes 0) | PASS |

**Score transfer.** The frozen Qwen item-level RS_q, applied to Ling's own errors, achieves AUROC 0.723 [0.682, 0.765] and Risk@80 0.296 [0.148, 0.439], with both CI lower bounds above 0.5 (Table 4). Ling's own procedure score is significantly better (paired AUROC diff -0.173 [-0.217, -0.130]; Risk@80 diff -0.126 [-0.226, -0.062]), and item-level Spearman between Qwen and Ling RS_q is only 0.496 on the 574 HC items. Outcome overlap is limited: across all 600 items the models share the consensus on 511, are both wrong on 57, Qwen-only wrong on 19, Ling-only wrong on 70, and both correct on 454. The supported claim is therefore bounded: **the stress-testing procedure and the aggregate reliability signal transfer across model families, while item-level risk ordering is partly model-dependent.**

**Table 4: Cross-model procedure/score transfer on Ling HC items.**

| Signal | AUROC [95% CI] | Risk@80 [95% CI] |
|---|---|---|
| Frozen Qwen item-level RS_q on Ling errors | 0.723 [0.682, 0.765] | 0.296 [0.148, 0.439] |
| Ling's own unchanged RS_q procedure | 0.896 [0.873, 0.916] | 0.422 [0.274, 0.591] |
| Paired diff (Qwen-transfer - Ling-own) | -0.173 [-0.217, -0.130] | -0.126 [-0.226, -0.062] |

**Mechanism fidelity.** On Ling HC items, mean natural-evidence reversal fidelity is 0.703 for correct consensus versus 0.029 for wrong consensus; the correct-minus-wrong difference is 0.674 [0.629, 0.719], CI excluding zero. Wrong Ling consensus is therefore much more rigid under natural evidence reversal than correct consensus, replicating the central Qwen mechanism in a different model family. Claim boundary: this supports cross-family transfer on this frozen VitaminC natural-pair protocol for Qwen3.5-4B and Ling-3.0-tiny only; it does not claim universal transfer, superiority over all reliability baselines, or zero-shot generalization to arbitrary datasets.

### 4.4 External baselines / leaderboard

We compared RS_q against 11 methods on the same frozen VitaminC main split under a matched per-item call/token budget (5-25 calls/item; RS_q uses 25 calls/item at 10,196/10,354 tokens/item on Qwen/Ling, while the cheapest baselines use 5 calls/item). All external baselines are **adapted proxies**—binary/answer-match variants (e.g., Self-consistency as 1 - modal frequency, an answer-match SelfCheckGPT-style variant without its NLI/self-check pipeline, and a binary semantic-entropy variant without bidirectional-entailment clustering)—and must not be read as implementations of the original published methods. The three binary sampling-consistency variants share one 25-sample temperature-0.7 answer distribution and produce identical features, so they are reported as a single merged row. The "single-agent intervention" row is our own ablation (5 personas -> 1 persona) that is labeled external only for ranking/narration.

RS_q ranks #1 on both models by the leaderboard's stated rule (AUROC point estimate, then Risk@80, then calls/item), with the best AUROC point (Qwen 0.943 [0.924, 0.960]; Ling 0.896 [0.875, 0.917]). **No baseline is significantly better than RS_q**: for every baseline the paired AUROC difference CI (RS_q - baseline) is either entirely above 0 (RS_q significantly better) or includes 0 (not significantly different, i.e., the single-agent intervention); none has an upper bound below 0 (Tables 5-6). We do not claim the best Risk@80 point everywhere: on Qwen the reversal-only(5) probe has a slightly higher Risk@80 point (0.884 vs 0.846), and we treat that probe separately in Section 4.5.

**Table 5: Leaderboard, Qwen3.5-4B (567 HC items; 65 wrong). Paired diffs are RS_q minus baseline.**

| Method | Calls/item | AUROC [95% CI] | Risk@80 [95% CI] | Paired AUROC diff [95% CI] | Paired Risk@80 diff [95% CI] |
|---|---|---|---|---|---|
| CST RS_q (proposed) | 25 | 0.943 [0.924, 0.960] | 0.846 [0.651, 0.981] | — | — |
| Reversal-only probe (5 calls) | 5 | 0.931 [0.913, 0.948] | 0.884 [0.556, 0.981] | +0.012 [0.002, 0.023] | -0.039 [-0.038, 0.134] |
| Single-agent intervention | 25 | 0.925 [0.900, 0.948] | 0.769 [0.514, 0.942] | +0.018 [-0.001, 0.039] | +0.077 [0.000, 0.210] |
| R_sym (internal) | 25 | 0.892 [0.864, 0.916] | 0.499 [0.281, 0.754] | +0.051 [0.029, 0.075] | +0.347 [0.154, 0.502] |
| Frozen mean confidence | 5 | 0.728 [0.676, 0.775] | 0.268 [-0.004, 0.445] | +0.215 [0.165, 0.270] | +0.578 [0.464, 0.774] |
| Sampling-consistency family (3 identical variants) | 25 | 0.645 [0.575, 0.712] | 0.249 [0.063, 0.485] | +0.297 [0.229, 0.374] | +0.597 [0.401, 0.749] |
| Raw sampled confidence | 25 | 0.628 [0.558, 0.693] | 0.095 [-0.148, 0.316] | +0.314 [0.248, 0.383] | +0.751 [0.598, 0.910] |
| R_PI (internal) | 25 | 0.628 [0.584, 0.673] | -0.001 [-0.246, 0.257] | +0.315 [0.271, 0.359] | +0.847 [0.684, 0.978] |
| Isotonic confidence | 25 | 0.585 [0.513, 0.651] | 0.037 [-0.202, 0.276] | +0.358 [0.288, 0.432] | +0.809 [0.634, 0.963] |
| Vote agreement | 5 | 0.583 [0.530, 0.638] | 0.095 [-0.071, 0.382] | +0.360 [0.305, 0.412] | +0.751 [0.532, 0.844] |
| Temperature confidence | 25 | 0.580 [0.503, 0.652] | 0.076 [-0.181, 0.325] | +0.363 [0.284, 0.443] | +0.770 [0.597, 0.928] |

**Table 6: Leaderboard, Ling-3.0-tiny (574 HC items; 119 wrong). Paired diffs are RS_q minus baseline.**

| Method | Calls/item | AUROC [95% CI] | Risk@80 [95% CI] | Paired AUROC diff [95% CI] | Paired Risk@80 diff [95% CI] |
|---|---|---|---|---|---|
| CST RS_q (proposed) | 25 | 0.896 [0.875, 0.917] | 0.422 [0.272, 0.583] | — | — |
| Single-agent intervention | 25 | 0.883 [0.860, 0.905] | 0.412 [0.239, 0.556] | +0.014 [-0.003, 0.030] | +0.011 [-0.021, 0.085] |
| Reversal-only probe (5 calls) | 5 | 0.869 [0.847, 0.891] | 0.348 [0.184, 0.526] | +0.027 [0.013, 0.042] | +0.074 [0.031, 0.125] |
| R_sym (internal) | 25 | 0.818 [0.787, 0.847] | 0.212 [0.033, 0.366] | +0.078 [0.053, 0.104] | +0.210 [0.155, 0.309] |
| Frozen mean confidence | 5 | 0.611 [0.568, 0.655] | 0.128 [-0.051, 0.230] | +0.285 [0.236, 0.330] | +0.294 [0.253, 0.430] |
| Raw sampled confidence | 25 | 0.587 [0.543, 0.632] | 0.075 [-0.073, 0.224] | +0.309 [0.260, 0.358] | +0.347 [0.273, 0.439] |
| Temperature confidence | 25 | 0.585 [0.541, 0.629] | 0.075 [-0.079, 0.212] | +0.312 [0.263, 0.362] | +0.347 [0.260, 0.438] |
| R_PI (internal) | 25 | 0.577 [0.553, 0.602] | -0.103 [-0.269, 0.050] | +0.319 [0.292, 0.347] | +0.525 [0.448, 0.608] |
| Isotonic confidence | 25 | 0.568 [0.523, 0.614] | 0.075 [-0.072, 0.217] | +0.329 [0.278, 0.378] | +0.347 [0.277, 0.444] |
| Sampling-consistency family (3 identical variants) | 25 | 0.562 [0.527, 0.601] | 0.086 [-0.046, 0.252] | +0.334 [0.292, 0.372] | +0.336 [0.231, 0.406] |
| Vote agreement | 5 | 0.544 [0.512, 0.579] | 0.054 [-0.072, 0.219] | +0.353 [0.322, 0.385] | +0.368 [0.273, 0.431] |

**Honest statement on the single-agent intervention.** At the same 25-call budget, a single-agent intervention (5 personas -> 1 persona, our own ablation) reaches AUROC 0.925 [0.900, 0.948] on Qwen and 0.883 [0.860, 0.905] on Ling. Its paired AUROC difference versus RS_q is **not significant on either model**: +0.018 [-0.001, 0.039] (Qwen) and +0.014 [-0.003, 0.030] (Ling), both CIs including 0; on Risk@80 the Qwen difference CI lower bound sits at exactly 0.000 ([0.000, 0.210]) and the Ling CI includes 0 ([-0.021, 0.085]). We therefore do not claim that RS_q separates from this ablation on AUROC; the leaderboard shows RS_q point-best but statistically tied with it. This is consistent with the mechanism analysis (Section 4.6): most signal comes from the natural-reversal axis, which the single-agent intervention still exposes, so a large gap would not be expected. RS_q's robust, CI-confirmed advantages are over the internal R_sym/R_PI and the proxy families; the reversal-only(5) probe is treated separately in Section 4.5.

### 4.5 Cost: how many calls buy how much reliability

Using only the frozen records (zero new model calls), we vary the number of marginal stress calls on top of the already-formed five-agent consensus (total = marginal + 5 original calls): reversal-only probes with 1, 2, 5, and 10 marginal calls (risk = 1 - mean natural-reversal fidelity over the first K agents; the 10-call version adds the synthetic-reverse condition) and reversal+paraphrase probes with 2, 4, and 10 marginal calls (risk = 1 - mean over (paraphrase + reverse) fidelity / 2; K = 5 equals the frozen BF_q score function). Missing/invalid calls are treated as missing responses. Table 7 reports AUROC and Risk@80; Table 8 reports paired differences versus the full RS_q (25 calls/item; positive = RS_q better).

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

1. **The 5-call cost story is not statistically supported.** The pre-registered adoption rule was to adopt the 5-call story only if reversal-only(5) is not statistically worse than RS_q on paired AUROC (CI lower bound <= 0). The paired AUROC difference CI excludes 0 on both models—Qwen +0.012 [0.002, 0.023]; Ling +0.027 [0.013, 0.042] (RS_q better)—so "5 calls ≈ 25 calls" cannot be claimed. The gap is small on Qwen, and on Risk@80 Qwen's reversal-only(5) is not worse (paired diff -0.039 [-0.038, 0.134], CI including 0, point 0.884 vs 0.846), but the AUROC result is significant on both models and we report the negative.
2. **The cheapest score-identical point is 10 calls/item.** Reversal+paraphrase(10) is score-identical to RS_q by construction (BF_q uses exactly the 10 scored paraphrase+reverse calls), with paired differences of 0.000 [0.000, 0.000] on AUROC and Risk@80 for both models and identical AUROC point estimates (0.943 / 0.896). If a reduced-cost claim is made, it should be "10 calls/item", not 5.
3. **Adding synthetic reversal dilutes the signal.** The 10-call reversal-family probe (natural + synthetic reverse) is *worse* than the 5-call natural-only probe on both models (Qwen 0.832 [0.796, 0.867] vs 0.931; Ling 0.753 [0.729, 0.776] vs 0.869), with large significant paired differences versus RS_q (0.111 [0.081, 0.139] / 0.144 [0.124, 0.164]). More calls do not monotonically buy reliability; the natural counter-evidence axis is the informative component.
4. **Token accounting.** Reversal-only(5) costs 2,154 / 2,176 tokens/item (prompt + completion) versus 10,196 / 10,354 for RS_q(25) on Qwen / Ling, so the cheap probe is real in cost terms even though it is not statistically equivalent in AUROC.

### 4.6 Reducibility: is RS_q a new signal or a re-weighted baseline?

To answer whether RS_q/BF_q is "just R_sym with different weights plus a paraphrase axis", we ran a label-free reducibility audit (zero new model calls; pair-grouped bootstrap, 2,000 replicates). Algebraically the two scores share only the natural-reversal flip axis (RS_q weight -0.5 via BF_q; R_sym weight -0.3 via reverse_inertia) and use different second axes (RS_q: paraphrase faithfulness; R_sym: intervention_disagreement), so "just re-weighted" is not literally accurate. Empirically they are substantially overlapping but not strictly reducible (Table 9).

**Table 9: Reducibility of RS_q versus R_sym.**

| Quantity | Qwen [95% CI] | Ling [95% CI] |
|---|---|---|
| Spearman(RS_q, R_sym) | 0.822 [0.787, 0.845] | 0.859 [0.822, 0.886] |
| Incremental AUROC of RS_q residualized on R_sym | 0.874 [0.784, 0.931] | 0.787 [0.743, 0.831] |
| Paired AUROC diff RS_q - R_sym | +0.051 [0.028, 0.075] | +0.078 [0.053, 0.106] |

RS_q is strongly positively correlated with R_sym (0.82 / 0.86) but far from isomorphic; residualizing RS_q on R_sym leaves significant, moderate incremental AUROC (0.874 [0.784, 0.931] on Qwen; 0.787 [0.743, 0.831] on Ling, CI lower bounds well above 0.5), and the paired AUROC advantage over R_sym is CI-confirmed on both models (+0.051 / +0.078). Correlations with R_PI, intervention disagreement, vote agreement, and confidence are weak (|rho| <= 0.35).

**Axis decomposition.** RS_q's signal is almost entirely carried by the natural-reversal axis (Table 10): the reverse axis alone reaches 0.931 [0.913, 0.947] on Qwen and 0.869 [0.846, 0.891] on Ling, versus RS_q's 0.943 / 0.896, while the paraphrase axis alone is near chance (0.599 [0.548, 0.652] / 0.581 [0.542, 0.621]). The paraphrase axis adds a small but statistically significant increment (paired AUROC diff of RS_q over the reverse axis: 0.012 [0.002, 0.022] / 0.027 [0.013, 0.042], both CIs excluding 0; residual incremental AUROC of RS_q over the reverse axis is only 0.284 [0.194, 0.378] / 0.317 [0.257, 0.384], below 0.5 and direction-unstable). Notably, R_sym (0.892 [0.861, 0.921] / 0.818 [0.787, 0.847]) is *lower* than the reverse axis alone, because its intervention-disagreement component (weight 0.7; itself AUROC only about 0.536 / 0.475) drags the score down; RS_q's advantage over R_sym therefore comes from adding the paraphrase axis and dropping intervention_disagreement.

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

**Honest conclusion.** RS_q is *partially reducible* to the natural-reversal axis that R_sym already captures at weight 0.3, and it does **not** constitute an independent new heuristic. We therefore frame the mechanism as: *errors are correlated with near-duplicate natural pairs, and the natural counter-evidence axis can pre-outcome-predict consensus errors*; RS_q's relative gain over R_sym is the small paraphrase-axis increment (paired AUROC +0.05 / +0.08, both significant). We do not claim a fundamentally new signal beyond the reversal axis plus a small paraphrase increment.

### 4.7 Label balance: SUPPORTS vs REFUTES

Because the label-symmetric construction does not imply symmetric error rates (Qwen: 2.5% on SUPPORTS vs 20.4% on REFUTES; Ling: 4.4% vs 38.1%; an 8.3-8.7x ratio), we report per-label AUROC/Risk@80 as the primary view (Table 11), with the pooled estimate presented as REFUTES-dominated by error composition (REFUTES carries 89.2% / 89.1% of the HC error mass and 89.3% / 88.9% of the pooled AUROC concordant mass on Qwen / Ling).

**Table 11: Per-label AUROC / Risk@80 (label-internal Risk@80).**

| Model | Label | n | Wrong (rate) | AUROC [95% CI] | Risk@80 [95% CI] (label-internal) |
|---|---|---|---|---|---|
| Qwen | SUPPORTS | 283 | 7 (2.5%) | 0.917 [0.819, 0.999] | 0.642 [0.165, 1.000] |
| Qwen | REFUTES | 284 | 58 (20.4%) | 0.986 [0.973, 0.995] | 0.871 [0.687, 0.976] |
| Qwen | pooled | 567 | 65 (11.5%) | 0.943 [0.924, 0.960] | 0.846 [0.638, 0.981] |
| Ling | SUPPORTS | 296 | 13 (4.4%) | 0.881 [0.834, 0.928] | 0.807 [0.283, 0.904] |
| Ling | REFUTES | 278 | 106 (38.1%) | 0.957 [0.934, 0.977] | 0.338 [0.253, 0.432] |
| Ling | pooled | 574 | 119 (20.7%) | 0.896 [0.873, 0.916] | 0.422 [0.274, 0.591] |

The signal holds within both labels: per-label AUROC is significantly above 0.5 in every cell (Mann-Whitney one-sided p < 1e-5 for both SUPPORTS cells). The SUPPORTS result is not driven by one error: leave-one-error-out (jackknife) SUPPORTS AUROC ranges over [0.903, 0.944] on Qwen and [0.872, 0.886] on Ling, with every value above 0.8; Qwen's 7 SUPPORTS errors all fall in the highest-risk 27% of that label (5/7 in the top 11%), and Ling's 13 errors average the 89.4th risk percentile. Because Qwen has only 7 SUPPORTS positives, we gate and report the worst label at the CI level (both CI lower bounds > 0.5: 0.819 / 0.834) and do not claim SUPPORTS is significantly harder than REFUTES for Qwen—the per-label AUROC difference CI includes 0 (-0.069 [-0.169, +0.007]); for Ling the difference CI excludes 0 (-0.076 [-0.133, -0.021]).

**Error-rate-matched diagnostic (post-hoc sensitivity, not a gate).** Forcing the two labels to equal error counts—matching SUPPORTS up to the REFUTES error count (58 / 106 per label) or both down to the SUPPORTS count (7 / 13)—keeps pooled AUROC at about 0.92 on Qwen and 0.875 on Ling (matched-up: 0.919 [0.903, 0.935] / 0.875 [0.863, 0.887]; matched-down: 0.920 [0.868, 0.958] / 0.875 [0.842, 0.909]), with CI lower bounds >= 0.84. The pooled 0.943 is partly elevated by the near-perfect rankability of the 58 REFUTES errors (per-label 0.986), but the ordering signal is present and strong within each label and is not an artifact of label imbalance.

### 4.8 Large-model single point (gpt-6-astra)

As a single-point check with a larger GPT-class model, we ran the frozen protocol on the first 50 pairs (100 items x 5 agents x 5 conditions = 2,500 logical calls) through a relayed endpoint (`https://openapi.center/v1`); the recorded model id matches `gpt-6-astra` in all 2,483 successful records. Transport reliability was imperfect: 17/2,500 records (0.7%) are transport failures (HTTP 200 x 1,511; 429 x 826; 502 x 115; 400 x 125; 929 transport retries) and **0 parse failures** (no contract adaptation or JSON-exemplar escalation was needed). Two items lack complete five-agent `original` answers and are excluded by the pre-existing Round-3 feature rule (all five originals are required to define consensus/agreement); this exclusion is label-free and not post-hoc selection on outcomes, leaving 98 items with complete features, of which 96 are HC with 8 wrong (error rate 0.0833; 7 REFUTES + 1 SUPPORTS).

Within-model gates all pass (Table 12): AUROC(RS_q, wrong | HC) = 0.969 [0.935, 0.995] (n = 96), Risk@80 = 1.000 [0.836, 1.000] with all 8 wrong HC items in the highest-risk 20%, placebo paraphrase flip 0.0394, permutation 0.9695 > 0.8942, and mechanism fidelity (correct minus wrong natural-reversal fidelity) 0.832 [0.745, 0.928] (correct n = 88, wrong n = 8). Frozen Qwen/Ling RS_q scores transfer to gpt-6-astra's own errors at the aggregate level (Table 13), with Qwen's score transferring more strongly than Ling's, consistent with item-level Spearman (Qwen 0.6787 vs Ling 0.3656).

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

**Honest boundaries.** This is a 100-item single point, not a full-cohort estimate; the wrong-HC count is small (n = 8), so CIs are wide-tailed and support only the pre-registered CI-level gate (lower bound > 0.5) and the mechanism direction. The model is a relay GPT-class model through a third-party proxy; per-call model identity is recorded and matches `gpt-6-astra` in every successful record, but the deployment is not a local first-party environment. We claim no per-item ranking equivalence across models and no full-cohort large-model estimate.

### 4.9 Negative results / specificity

**BoolQ (specificity negative).** On a fresh balanced 50-yes/50-no BoolQ cohort (100 items; HC 85/100, 23 wrong, 27%), the frozen RS_q procedure produces AUROC 0.449 [0.308, 0.579]—*direction-reversed* (below 0.5)—so the cross-dataset gate fails (G2/G3/G4/G6). Label subgroups diverge (no: 0.073 [0.005, 0.169] vs yes: 0.745 [0.579, 0.889]), reproducing the answer-prior confound in risk orientation; Risk@80 is 0.239 [-0.467, 0.348] (n.s.); permutation fails (0.449 < 0.612); and RS_q is significantly *worse* than R_PI on BoolQ (paired diff -0.097 [-0.182, -0.009]). Placebo is clean (0.052) and the pipeline is 100% valid. The diagnosis is that BoolQ has no natural counter-evidence, so the frozen oracle's reverse axis is a synthetic negation prefix—and the synthetic-reversal axis is weak/non-separating. This is a **specificity result**, not a contradiction: it supports the causal reading that the risk signature is specifically "unresponsive to genuine natural evidence reversal", not "unresponsive to any perturbation". No parser, oracle, or gate was changed; the negative is retained.

**FEVER (blocked at construction).** FEVER validation lacks the two-evidence contrast structure the frozen oracle requires: verification found 0 same-claim pairs with both SUPPORTS and REFUTES verdicts, and an offline semantic audit of 60 near-duplicate candidate pairs (162 judgments) passed 57/60 on "E_S supports C_S" but only 4/60 on "E_R refutes C_S"—the paired REFUTES evidence is almost always the same (or near-identical) sentence as the SUPPORTS evidence—with only 1/60 pairs passing both. Running the protocol on such pairs would not implement the oracle as specified, so **no agent calls were made on FEVER and no result is claimed**; cross-dataset evaluation was instead run on the balanced BoolQ split above.

### Summary

1. On 567/574 high-consensus VitaminC items, counter-evidence responsiveness (RS_q = -BF_q) ranks consensus errors with AUROC 0.943 [0.924, 0.960] (Qwen) / 0.896 [0.873, 0.916] (Ling), passing all 8/8 frozen gates on both models and beating confidence, disagreement, R_PI, and R_sym with CI-confirmed paired differences.
2. The signal transfers across model families as a procedure (Ling own-score 0.896; frozen Qwen-score transfer 0.723 [0.682, 0.765]) and to a GPT-class single point (gpt-6-astra 0.969 [0.935, 0.995]; Qwen transfer 0.838 [0.693, 0.950]), while item-level ordering is partly model-dependent (Qwen-Ling Spearman 0.496).
3. Five calls is not statistically equivalent to the 25-call RS_q (paired AUROC CI excludes 0 on both models); the cheapest score-identical point is 10 calls/item (reversal+paraphrase, diff 0.000 [0.000, 0.000]), and adding synthetic reversal dilutes signal.
4. The natural-reversal axis alone reaches AUROC 0.931 / 0.869 and carries most of RS_q's signal; the paraphrase axis adds a small significant increment, and RS_q is substantially overlapping with—but not strictly reducible to—R_sym (Spearman 0.822/0.859; incremental AUROC 0.874/0.787).
5. Boundaries are explicit: small models, one dataset, SUPPORTS error asymmetry (2.5% vs 20.4%) reported with per-label and matched diagnostics, small wrong-N (8) in the gpt single point, and a specificity negative on BoolQ (AUROC 0.449, direction-reversed) with FEVER blocked at construction.
