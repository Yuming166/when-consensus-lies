# 4 Main Experiments

This section evaluates CST-Bench as a reliability-measurement instrument.

The central probe is a fixed, gold-opposing natural pair.

For a correct consensus, the paired item argues against the consensus.

For a wrong consensus, the paired item is aligned with the gold-correct direction.

The analysis therefore separates two types of evidence:

1. **PREDICTIVE evidence**, which asks whether the resulting score ranks wrong consensus decisions above correct ones.
2. **MECHANISM evidence**, which asks whether the response depends on the direction and construction of the presented evidence.

These categories are not interchangeable.

A score can rank outcomes well without identifying the behavioral process that produces the ranking.

Conversely, a mechanism probe can reveal direction-sensitive updating without yielding a validated predictor.

The experiments do not establish general rigidity to counter-evidence.

In particular, independent claim-only counter-evidence is treated as a mechanism probe, not as an independently validated predictor.

No causal, mediation, general-rigidity, or independent-CE predictor claim is made.

## 4.1 Experimental setup

The primary evaluation uses a frozen VitaminC manifest containing 300 natural pairs, or 600 items.

The model panels are Qwen3.5-4B and Ling-3.0-tiny.

Each consensus is formed from five panel calls.

The high-confidence (HC) subset uses the preregistered agreement threshold.

Gold labels are merged only after feature computation is frozen.

This ordering prevents the outcome labels from entering score construction.

For query model \(q\), the risk score is

\[
\mathrm{RS}_q=-\mathrm{BF}_q,
\]

where \(\mathrm{BF}_q\) is computed from paraphrase stability and responsiveness to the natural counter-evidence probe.

Higher \(\mathrm{RS}_q\) therefore denotes greater estimated risk.

The score is evaluated against whether an HC consensus is wrong.

The evaluation target is consequently conditional on the HC subset.

It is not an estimate of the unconditional error rate.

All reported confidence intervals are 95% pair-grouped bootstrap intervals where provided.

The natural-pair evaluation is the primary PREDICTIVE analysis.

Flip rates, placebo comparisons, and direction-by-construction contrasts are interpreted separately as MECHANISM analyses.

## 4.2 Predictive evidence: within-panel ranking

The natural-pair score separates wrong from correct HC consensus decisions in both replicated panels.

For Qwen3.5-4B, \(\mathrm{RS}_q\) obtains AUROC \(0.943\) with a 95% interval of \([0.924,0.960]\).

This estimate uses 567 HC items, including 65 wrong items.

Its Risk@80 is \(0.846\), with interval \([0.638,0.981]\).

For Ling-3.0-tiny, the corresponding AUROC is \(0.896\), with interval \([0.873,0.916]\).

The Ling evaluation contains 574 HC items.

Its Risk@80 is \(0.422\).

A single-point gpt-6-astra evaluation obtains AUROC \(0.969\), with interval \([0.935,0.995]\).

That evaluation contains 96 HC items, including 8 wrong items.

| Query model | HC items | Wrong HC items | AUROC (wrong \(\mid\) HC) | Risk@80 |
|---|---:|---:|---:|---:|
| Qwen3.5-4B | 567 | 65 | 0.943 [0.924, 0.960] | 0.846 [0.638, 0.981] |
| Ling-3.0-tiny | 574 | — | 0.896 [0.873, 0.916] | 0.422 |
| gpt-6-astra | 96 | 8 | 0.969 [0.935, 0.995] | — |

**Table 1: Predictive performance of the natural-pair risk score.**

These results are PREDICTIVE evidence for the frozen VitaminC protocol.

They show that the score ranks wrong HC decisions above correct HC decisions within the reported cohorts.

They do not show that the score measures a model-general property of counter-evidence processing.

The gpt-6-astra result is especially uncertain as a population estimate because only 8 wrong HC items are included.

The Qwen3.5-4B result includes 65 wrong items.

The larger number of evaluated HC items does not remove the dependence on the frozen cohort or on the natural-pair construction.

The Ling-3.0-tiny result likewise remains specific to its panel and evaluation procedure.

An answer-prior control is substantially weaker.

Using only \(1[\mathrm{consensus=yes}]\) gives AUROC \(0.671\) for Qwen3.5-4B.

The same control gives AUROC \(0.634\) for Ling-3.0-tiny.

The natural-pair probe scores obtain AUROC \(0.943\) and \(0.896\), respectively.

A label-only baseline gives AUROC \(0.51\).

These comparisons do not prove that the probe is free of every answer-prior effect.

They do show that the reported ranking is not reproduced by the label-only baseline.

The appropriate conclusion is therefore comparative rather than absolute:

the natural-pair score provides stronger within-panel predictive ranking than the tested answer-prior controls.

## 4.3 Mechanism evidence: natural-mirror flip asymmetry

The fixed natural-pair probe produces a pronounced asymmetry in behavioral updating.

Across the aggregate consensus analysis, the natural mirror flips \(0.902\) of correct consensus decisions.

It flips \(0.075\) of wrong consensus decisions.

The corresponding Qwen3.5-4B rates are \(0.843\) for correct decisions and \(0.095\) for wrong decisions.

The corresponding Ling-3.0-tiny rates are \(0.703\) and \(0.029\).

| Panel or aggregate | Consensus correct | Consensus wrong |
|---|---:|---:|
| Aggregate consensus | 0.902 | 0.075 |
| Qwen3.5-4B | 0.843 | 0.095 |
| Ling-3.0-tiny | 0.703 | 0.029 |

**Table 2: Flip rates under the fixed gold-opposing natural-pair probe.**

The direction of the probe is essential to this interpretation.

For a correct consensus, the natural mirror argues against the current answer.

For a wrong consensus, it agrees with the gold-correct direction.

The asymmetry is therefore consistent with direction-gated responsiveness in this construction.

This is MECHANISM evidence.

It is not an additional estimate of predictive AUROC.

It does not establish a general inability to use counter-evidence.

It also does not establish that evidence direction causes the observed score or mediates the relationship between consensus status and response.

A clean neutral paraphrase placebo flips \(0.038\) of cases.

A matched content placebo flips between \(0.51\) and \(0.56\).

Within the matched content placebo, the rates are \(0.92\) for yes-answerers and \(0.09\) for no-answerers.

The contrast indicates that content matching alone does not make the two response directions behaviorally equivalent.

It motivates treating evidence direction as a design variable.

It also cautions against interpreting every content-matched response as evidence for the same mechanism.

## 4.4 Natural-pair reconstruction

The natural-pair structure also permits a score, \(S_{\mathrm{pair}}\), constructed from the two original answers.

This construction does not require a reverse call.

It also does not use outcome labels in the score itself.

\(S_{\mathrm{pair}}\) reconstructs the reverse axis with Spearman correlation \(0.998\).

It retains approximately \(98.7\%\) of the reported ranking power for Qwen3.5-4B.

It retains approximately \(97.0\%\) for Ling-3.0-tiny.

| Quantity | Qwen3.5-4B | Ling-3.0-tiny |
|---|---:|---:|
| Spearman(\(S_{\mathrm{pair}}\), reverse axis) | 0.998 | 0.998 |
| Ranking power recovered | \(\sim 98.7\%\) | \(\sim 97.0\%\) |

**Table 3: Reconstruction of the reverse axis from the original natural pair.**

This result is a paired-prediction diagnostic.

It shows that the ranking signal can be recovered from the natural-pair structure without an additional reverse call or labels.

It is therefore relevant to PREDICTIVE score construction.

It is not MECHANISM evidence.

In particular, reconstruction does not show that the signal is independent of the fixed natural-pair construction.

It does not establish that the same reconstruction holds for independently authored evidence.

It does not identify why the paired answers produce the observed ranking.

The bounded interpretation is that the natural-pair design contains a mechanically recoverable ranking axis.

## 4.5 Transfer across model panels

A procedure fixed using Qwen3.5-4B transfers to Ling-3.0-tiny with AUROC \(0.723\), with interval \([0.682,0.765]\).

Ling-3.0-tiny's own procedure obtains AUROC \(0.896\), with interval \([0.873,0.916]\).

The paired AUROC difference between the transferred and within-panel procedures is \(-0.173\), with interval \([-0.217,-0.130]\).

At the item level, Qwen3.5-4B and Ling-3.0-tiny scores have Spearman correlation \(0.496\) over 574 HC items.

| Evaluation | AUROC | Risk@80 | Item-level association |
|---|---:|---:|---:|
| Qwen procedure transferred to Ling | 0.723 [0.682, 0.765] | — | — |
| Ling's own procedure | 0.896 [0.873, 0.916] | — | — |
| Qwen transfer minus Ling own | -0.173 [-0.217, -0.130] | — | — |
| Qwen--Ling score association | — | — | Spearman 0.496 |

**Table 4: Cross-panel procedure transfer.**

The transfer result is PREDICTIVE evidence.

It indicates that a procedure fixed on Qwen3.5-4B retains ranking ability when applied to Ling-3.0-tiny.

The transferred AUROC is lower than Ling's within-panel AUROC.

The difference is consistent with panel-specific calibration or response structure.

The item-level correlation of \(0.496\) is neither negligible nor near-perfect.

Thus, an aggregate component of the signal transfers, but item-level risk scores are not invariant across the two panels.

This result does not establish transfer to other models, domains, prompting regimes, or evidence formats.

## 4.6 Direction \(\times\) evidence-construction analysis

The Round10 analysis crosses evidence direction with evidence construction.

The design distinguishes evidence agreeing with the initial consensus from evidence contradicting it.

It also distinguishes natural evidence from independent counter-evidence.

The analysis contains 16 items and 178 logical calls: 16 generation + 2 audit + 160 inference. Inference validity was 145/160; generation parsing was valid for 10/16 items, while 6/16 were format-invalid but recorded, loose-extracted, and audited. The direction audit found 10/16 clean agree sentences and 10/16 clean contradict sentences. Across the \(2\times2\) design, the CONTRADICT-minus-AGREE direction contrast is \(+0.44\), with interval \([0.24,0.65]\).

| Contrast | Direction contrast |
|---|---:|
| Overall CONTRADICT minus AGREE | +0.44 [0.24, 0.65] |
| Wrong items | +0.5062 [0.2438, 0.7625] |
| Correct items | +0.3688 [0.1312, 0.6500] |
| Consensus=yes | +0.3727 [0.1731, 0.6200] |
| Consensus=no | +0.5800 [0.1500, 0.8667] |

**Table 5: Direction contrasts in the Round10 analysis.**

The overall contrast is mechanism-oriented descriptive evidence for direction-sensitive behavior under the tested protocol.

The within-stratum estimates are descriptive source results; their small cells and the parser/direction audits below limit interpretation.

The overall contrast should not be read as a causal effect.

It is not a mediation estimate.

It does not establish that construction has no role.

For wrong consensuses, the as-assigned independent-CONTRADICT cell flips \(35/37\) cases. After direction auditing, the clean subset is \(30/32\) across 7 clean items.

The post-hoc Probe1 extension gives an as-assigned total of \(44/46\); it adds 2 items / 9 agent rows, uses a post-hoc direction decomposition, and relies on one batched direction audit. It is not a fully audited clean result, an AUROC result, or a generalization test.

The natural mirror for wrong consensuses is consensus-agreeing.

It flips only \(0.075\) of those cases.

These comparisons support a direction-sensitive interpretation within the tested design.

They do not validate independent counter-evidence as a separate predictor.

The direction-clean construction comparison contains only \(n=3\) items.

The small cell limits precision and makes construction-specific conclusions fragile.

The direction-clean analysis therefore cannot rule out a small construction effect.

The direction-clean comparison also does not establish general equivalence between natural and independent evidence.

The as-assigned independent-CE analysis contains direction-label noise.

Five of eight wrong-item AGREE sentences were audited as actually contradicting the evidence.

This observation is important for interpretation.

An as-assigned construction contrast can confound evidence construction with evidence direction.

The clean analysis addresses that issue descriptively, but its small cell prevents a strong general conclusion.

## 4.7 Independent counter-evidence is not an independent predictor

Independent claim-only counter-evidence is included to probe the behavioral account.

It is not included as a second validated reliability predictor.

Its role is to test whether direction-sensitive updating persists when the evidence construction is varied.

Accordingly, independent CE belongs to the MECHANISM analysis.

It should not be treated as an independent predictive signal.

The natural-pair score is evaluated as the CST-Bench reliability signal.

Independent CE tests whether the response pattern is compatible with direction-gated updating beyond the original natural-pair presentation.

This distinction prevents a mechanism result from being double-counted as predictive evidence.

It also prevents the independent-CE probe from being interpreted as a separate validated risk model.

The available independent-CE result does not establish independent predictive power.

Nor does it establish that independent claim-only evidence is a generally reliable counter-evidence format.

The clean direction analysis is informative about the tested response pattern, but its small cells constrain the inference.

No causal or mediation claim follows from the contrast.

## 4.8 Additional scope checks

The auxiliary checks place boundaries on how broadly the VitaminC result should be interpreted.

On BoolQ, the reported AUROC is \(0.449\) \([0.308,0.579]\) when reversed.

This does not provide positive evidence for the same predictive behavior outside the primary VitaminC evaluation.

FEVER provides no usable natural pairs.

Its Jaccard value is \(1.000\), so that result does not constitute a usable natural-pair validation.

The S&P500 as-of sequential analysis is null.

These checks do not invalidate the VitaminC findings.

They do show that the protocol's behavior is not established uniformly across the auxiliary settings.

They also reinforce the need to distinguish a result on the frozen primary cohort from a claim about general reliability measurement.

The current evidence supports reporting the VitaminC analysis as a bounded evaluation.

It does not support presenting CST-Bench as validated across all domains or temporal settings.

## 4.9 Summary and scope

On the frozen VitaminC cohort, the gold-opposing natural-pair probe yields AUROC \(0.943\) \([0.924,0.960]\) for Qwen3.5-4B.

It yields AUROC \(0.896\) \([0.873,0.916]\) for Ling-3.0-tiny.

The single-point gpt-6-astra evaluation yields AUROC \(0.969\) \([0.935,0.995]\).

The natural-mirror flip rates are asymmetric between correct and wrong consensus decisions.

The aggregate rates are \(0.902\) for correct decisions and \(0.075\) for wrong decisions.

The panel-specific rates show the same qualitative ordering.

The natural-pair reconstruction has Spearman correlation \(0.998\) with the reverse axis.

It retains approximately \(98.7\%\) and \(97.0\%\) of the reported ranking power for Qwen3.5-4B and Ling-3.0-tiny.

A single cross-panel portability check applying the Qwen-fixed procedure to Ling obtains AUROC \(0.723\) \([0.682,0.765]\).

The item-level score association is Spearman \(0.496\).

These are PREDICTIVE results for the frozen protocol; they are not evidence of model-independent or out-of-domain generalization.

The Round10 analysis supplies MECHANISM evidence for direction-sensitive behavior.

Its overall CONTRADICT-minus-AGREE direction contrast is \(+0.44\) \([0.24,0.65]\).

The as-assigned independent-CONTRADICT cell flips \(35/37\) wrong-consensus cases. After direction auditing, the clean subset is \(30/32\) across 7 clean items.

The post-hoc Probe1 extension gives an as-assigned total of \(44/46\); it adds 2 items / 9 agent rows, uses a post-hoc direction decomposition, and relies on one batched direction audit. It is not a fully audited clean result, an AUROC result, or a generalization test.

Those results do not establish general rigidity to counter-evidence.

They do not establish causal mediation.

They do not establish a general construction-independent mechanism.

They do not establish independent-CE prediction or a financial-prediction claim.

The result is best characterized as a reliability-measurement protocol under the frozen VitaminC natural-pair design, paired with a direction-gated behavioral regularity.

Its validity is constrained by the natural-pair construction.

It is also constrained by the tested domains and panels.

The small wrong-item and direction-clean cells impose additional uncertainty.

The auxiliary checks further limit generalization beyond the frozen VitaminC setting.
