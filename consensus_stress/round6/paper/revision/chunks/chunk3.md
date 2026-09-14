## 4 Experiments and Results

We evaluate counter-evidence responsiveness as a *pre-outcome* error signal for multi-agent consensus. All protocols were frozen before any model call; all risk scores are outcome-independent (no label fields are used before label merge); and every reported interval is a 95% pair-grouped bootstrap interval (2,000 replicates), computed with a fixed seed base (`20260913`) and per-statistic offsets. Paired comparisons are computed on the high-consensus (HC) intersection. All numbers below are reproduced from the frozen analysis artifacts listed in the repository; no figure is included.

### 4.1 Setup

**Cohort.** The main cohort is a fresh, frozen sample of 300 natural contrastive pairs (600 items) from VitaminC. It is label-symmetric by construction: each pair contains one SUPPORTS item and one REFUTES item (300 + 300), with the same evidence view, prompt template, and oracle; the items differ only in the mirrored evidence conclusion. Items are page- and pair-disjoint from earlier rounds (150 round-2 pairs; the frozen V3.16/V3.16.1 pages). Eligibility requires `character_ratio >= 0.85` and `token_jaccard >= 0.70` (one pair per page), with contrast medians of 0.95 / 0.84. The pipeline produced 900/900 usable paraphrase artifacts, 15,000/15,000 agent records with 14,999 valid (99.99%; one reverse call failed after retry), 30/30 meaning-preserving paraphrases, 30/30 decision-relevant audit items, and pre-outcome features frozen on all 600 items before label merge.

**High-consensus populations.** HC is defined as five-agent agreement `>= 0.8` and is fixed before evaluation. Qwen3.5-4B has 567 HC items (94.5% of 600; 298 pairs), including 65 wrong items (11.5%). Ling-3.0-tiny has 574 HC items (299 pairs), including 119 wrong items (20.7%). The models therefore have different failure distributions.

**Models.** Qwen3.5-4B is the primary model, and Ling-3.0-tiny is the secondary model. gpt-6-astra (a relayed GPT-class model) provides a single-point validation of 100 items. No Qwen calls were rerun for any analysis; all later rounds reuse the frozen Qwen records.

**Metrics.** The primary metric is AUROC of the risk score for the HC error indicator (`wrong | HC`). Risk@80 is the relative error reduction obtained by retaining the lowest-risk 80% of HC items (operating point 0.8). Paired differences are computed on the HC intersection. The risk form is `RS_q = -BF_q` (higher = riskier), where `BF_q = (bf_paraphrase + bf_reverse)/2` is expected-response faithfulness averaged over the five agents. Here, `bf_paraphrase` is paraphrase fidelity (`1 - para_flip_rate`), and `bf_reverse` is natural-reversal fidelity (the proportion of agents that flip to the oracle's expected opposite under natural counter-evidence).

**Controls.** (i) *Placebo:* the paraphrase-flip rate must remain below 0.30 so that meaning-preserving paraphrases are not themselves adversarial; the observed rates are 0.038 (Qwen) and 0.061 (Ling). (ii) *Permutation:* the observed AUROC must exceed the 95th percentile of the permuted-null distribution; Qwen achieves 0.943 > 0.596, and Ling achieves 0.896 > 0.564. (iii) *Reducibility:* absolute Spearman correlations with agreement and confidence must remain below 0.9, and AUROC at an agreement-0.8 split must exceed 0.5 (Qwen: -0.004 / -0.161; 0.844; Ling: -0.148 / -0.050). Section 4.6 analyzes reducibility against the strongest internal baseline in detail.

### 4.2 Main results (Qwen3.5-4B)

**Gate set (8/8 PASS).** The frozen paper-scale gate set passes all eight checks (Table 1). The primary gate is CI-level: the lower bound of AUROC(RS_q, wrong | HC) must exceed 0.5, with a point estimate >= 0.60.

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

**Against internal baselines.** RS_q ranks consensus errors with AUROC 0.943 [0.924, 0.960] and reduces retained error by 84.6% at 80% coverage (Risk@80 0.846 [0.638, 0.981]). It significantly outperforms the frozen internal baselines—R_sym (0.3·reverse_inertia + 0.7·intervention_disagreement), R_PI (the frozen BoolQ provenance–intervention score), disagreement, and mean confidence—with CI-confirmed paired AUROC differences. The strict Risk@80 gate (CI lower bound > 0) also passes (Table 2). A label-blind fitted logistic model over {paraphrase, reverse} achieves 0.941 [0.922, 0.959], tying the frozen composite (paired diff +0.002 [-0.002, +0.007] includes 0). This indicates that the signal comes from the concept—expected-response faithfulness with a decision-relevance-aware oracle—rather than from additional fitting. Isotonic calibration reduces ECE from 0.057 to 0.013 (reported; AUROC unchanged by design). The paper-scale result maintains or exceeds the round-2 baseline (AUROC 0.906 [0.865, 0.944] -> 0.943; Risk@80 0.654 -> 0.846).

**Table 2: Phase-4 comparison on Qwen HC items (n = 567). Paired diffs are RS_q minus the baseline; positive favors RS_q.**

| Representation | AUROC [95% CI] | Risk@80 [95% CI] | Paired AUROC diff [95% CI] | Paired Risk@80 diff [95% CI] |
|---|---|---|---|---|
| RS_q = -BF_q | **0.943 [0.924, 0.960]** | **0.846 [0.638, 0.981]** | — | — |
| logistic OOF {para, rev} | 0.941 [0.922, 0.959] | — | +0.002 [-0.002, +0.007] (tie) | — |
| R_sym (frozen) | 0.892 [0.861, 0.921] | 0.499 [0.273, 0.770] | +0.051 [+0.029, +0.075] | +0.347 [+0.152, +0.502] |
| R_PI (frozen) | 0.628 [0.586, 0.670] | -0.001 [-0.235, 0.271] (n.s.) | +0.315 [+0.271, +0.360] | +0.847 [+0.677, +0.984] |
| disagreement | 0.583 [0.536, 0.630] | 0.095 [-0.076, 0.388] (n.s.) | +0.360 [+0.306, +0.413] | +0.751 (point; CI n.r.) |
| confidence | 0.272 [0.226, 0.321] | -0.232 [-0.511, 0.039] (n.s.) | +0.671 [+0.620, +0.723] | +1.078 (point; CI n.r.) |

*Note: for the last two rows, the frozen Phase-4 protocol reported paired Risk@80 differences as point estimates only; CIs are not reported in the artifact ("n.r."). Confidence is anti-predictive (AUROC < 0.5).*

**Label-symmetric design, asymmetric error behavior.** The construction is label-symmetric (300 SUPPORTS + 300 REFUTES items), but model behavior is not: Qwen makes errors on 7/283 SUPPORTS items (2.5%) versus 58/284 REFUTES items (20.4%), or 8.3x more often on REFUTES; REFUTES accounts for 89.2% of the HC error mass. The label-symmetric design is intended precisely to expose this asymmetry: the risk signal is not an artifact of a single label. We therefore report per-label and matched diagnostics in Section 4.7 rather than collapsing both labels into a single claim.

### 4.3 Cross-model: Ling-3.0-tiny

**Procedure transfer with a frozen score.** The complete frozen Round-3 cohort (300 pairs / 600 items) was rerun with Ling-3.0-tiny under the same frozen evidence, oracle, conditions, `BF_q`, and `RS_q`. The only protocol adaptation concerned response transport: Ling no longer self-reports `agent_id`, so the task dispatcher binds the frozen agent index/persona/partition server-side, while the parser validates `answer`, `confidence`, and `cited_evidence_ids`; a frozen JSON exemplar appears in every prompt. Calls were 15,000/15,000 valid (100%; first-pass 14,992/15,000 = 99.95%), with 3,000/3,000 valid calls in every condition.

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

**Score transfer.** The frozen Qwen item-level RS_q, applied to Ling's own errors, achieves AUROC 0.723 [0.682, 0.765] and Risk@80 0.296 [0.148, 0.439], with both CI lower bounds above 0.5 (Table 4). Ling's own procedure score is significantly better (paired AUROC diff -0.173 [-0.217, -0.130]; Risk@80 diff -0.126 [-0.226, -0.062]). Item-level Spearman correlation between Qwen and Ling RS_q is only 0.496 on the 574 HC items. Outcome overlap is limited: across all 600 items, the models share the consensus on 511, are both wrong on 57, Qwen-only wrong on 19, Ling-only wrong on 70, and both correct on 454. The supported claim is therefore bounded: **the stress-testing procedure and aggregate reliability signal transfer across model families, while item-level risk ordering is partly model-dependent.**

**Table 4: Cross-model procedure/score transfer on Ling HC items.**

| Signal | AUROC [95% CI] | Risk@80 [95% CI] |
|---|---|---|
| Frozen Qwen item-level RS_q on Ling errors | 0.723 [0.682, 0.765] | 0.296 [0.148, 0.439] |
| Ling's own unchanged RS_q procedure | 0.896 [0.873, 0.916] | 0.422 [0.274, 0.591] |
| Paired diff (Qwen-transfer - Ling-own) | -0.173 [-0.217, -0.130] | -0.126 [-0.226, -0.062] |

**Mechanism fidelity.** On Ling HC items, mean natural-evidence reversal fidelity is 0.703 for correct consensus and 0.029 for wrong consensus; the correct-minus-wrong difference is 0.674 [0.629, 0.719], with the CI excluding zero. Wrong Ling consensus is therefore substantially more rigid under natural evidence reversal than correct consensus, replicating the central Qwen mechanism in a different model family. Claim boundary: this supports cross-family transfer on this frozen VitaminC natural-pair protocol for Qwen3.5-4B and Ling-3.0-tiny only; it does not claim universal transfer, superiority over all reliability baselines, or zero-shot generalization to arbitrary datasets.

### 4.4 External baselines / leaderboard

We compared RS_q with 11 methods on the same frozen VitaminC main split under a matched per-item call/token budget (5-25 calls/item; RS_q uses 25 calls/item at 10,196/10,354 tokens/item on Qwen/Ling, while the cheapest baselines use 5 calls/item). All external baselines are **adapted proxies**—binary/answer-match variants, including Self-consistency as 1 - modal frequency, an answer-match SelfCheckGPT-style variant without its NLI/self-check pipeline, and a binary semantic-entropy variant without bidirectional-entailment clustering—and should not be interpreted as implementations of the original published methods. The three binary sampling-consistency variants share one 25-sample temperature-0.7 answer distribution and produce identical features; they are therefore reported as a single merged row. The "single-agent intervention" row is our own ablation (5 personas -> 1 persona), labeled external only for ranking and narration.

RS_q ranks #1 on both models under the leaderboard's stated rule (AUROC point estimate, then Risk@80, then calls/item), with the best AUROC point (Qwen 0.943 [0.924, 0.960]; Ling 0.896 [0.875, 0.917]). **No baseline is significantly better than RS_q**: for every baseline, the paired AUROC difference CI (RS_q - baseline) is either entirely above 0 (RS_q significantly better) or includes 0 (not significantly different, i.e., the single-agent intervention); none has an upper bound below 0 (Tables 5-6). We do not claim the best Risk@80 point in every comparison: on Qwen, the reversal-only(5) probe has a slightly higher Risk@80 point (0.884 vs 0.846), and we analyze that probe separately in Section 4.5.

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

**Honest statement on the single-agent intervention.** At the same 25-call budget, a single-agent intervention (5 personas -> 1 persona, our own ablation) achieves AUROC 0.925 [0.900, 0.948] on Qwen and 0.883 [0.860, 0.905] on Ling. Its paired AUROC difference from RS_q is **not significant for either model**: +0.018 [-0.001, 0.039] (Qwen) and +0.014 [-0.003, 0.030] (Ling), with both CIs including 0. For Risk@80, the Qwen difference CI lower bound is exactly 0.000 ([0.000, 0.210]), while the Ling CI includes 0 ([-0.021, 0.085]). We therefore do not claim that RS_q separates from this ablation on AUROC; the leaderboard shows RS_q as point-best but statistically tied with it. This result is consistent with the mechanism analysis (Section 4.6): most of the signal comes from the natural-reversal axis, which the single-agent intervention still exposes, so a large gap is not expected. RS_q's robust, CI-confirmed advantages are over the internal R_sym/R_PI and the proxy families; the reversal-only(5) probe is analyzed separately in Section 4.5.
