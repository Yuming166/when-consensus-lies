# 5 Boundaries, Honest Negatives, and Analysis

This section delimits what CST-Bench is and is not. CST-Bench is a
reliability-measurement instrument: a pre-outcome, label-free stress-test
protocol whose fixed gold-opposing natural-pair probe separates correct from
wrong consensus decisions. It is not a universal test of counter-evidence
handling, not a claim about why panels fail, and not a predictor built from
independent counter-evidence. Every boundary below is reported as a negative
result rather than repaired through reinterpretation; each negative is
explicit, and none is silently dropped.

All numbers in this section are observations from frozen result files; source blocks are attached
locally to the relevant boundary and mechanism paragraphs. The section has two
parts: axis-native boundaries (Section 5.1) and the separation between mechanism
probes and predictors (Section 5.2). Answer-prior and placebo controls are
reported with the main scope checks in Section 4.8, while limitations are
summarized throughout this section and in Section 6.

**Context.** Under the natural mirror—the reverse of an item's own evidence, a
near-duplicate sentence that argues *against* the item's gold—a five-agent
consensus panel flips its answer with probability 0.902 when the consensus is
correct (Qwen 0.843; Ling 0.703) and 0.075 when it is wrong (Qwen 0.095; Ling
0.029). The label-free score RS_q = −BF_q ranks consensus errors with AUROC
0.943 [0.924, 0.960] (Qwen, 567 HC items, 65 wrong), 0.896 [0.873, 0.916]
(Ling, 574 HC items), and 0.969 [0.935, 0.995] (gpt-6-astra single point,
96 HC, 8 wrong). These results motivate the instrument; they do not by
themselves establish axis-invariant behavior. The remainder of this section
shows that the instrument's validity is explicitly bounded.

## 5.1 Axis-native boundaries

The probe's power derives from its direction—it argues against the item's
gold—and from the availability of natural counter-evidence, not from
near-duplicate overlap per se. On axes where these preconditions fail, the
signal reverses, becomes vacuous, or is null. Three axis-native boundaries are
reported: BoolQ (reversal), FEVER (vacuous), and S&P500 (null).

### 5.1.1 BoolQ: direction reversed under negation-prefix reversal

On a frozen balanced BoolQ cohort (100 items, 50 yes / 50 no; pipeline valid
100%), the primary ranking reverses: AUROC(RS_q, wrong | HC) = 0.449
[0.308, 0.579], below 0.5. This is a negative result for the intended ranking
direction, not a weak positive. The permutation check fails in the intended
direction (observed 0.449 < 0.612, the 95th percentile of the permutation
distribution), and Risk@80 is not significant. Every frozen gate that depends
on the intended direction therefore fails on BoolQ.

The construction explains why this axis cannot instantiate the probe. BoolQ
has no natural counter-evidence: the frozen reverse operation is a
negation-prefix transformation, a synthetic reversal that does not supply a
natural evidence-level contrast. Earlier evidence already showed that
synthetic reversal is weak or non-separating even on VitaminC; BoolQ has no
natural counter-evidence at all, so on this axis the probe reduces to a
generic perturbation rather than a decision-relevant reversal.

The label subgroups diverge: AUROC is 0.073 [0.005, 0.169] on the native-no
stratum and 0.745 [0.579, 0.889] on the native-yes stratum. This reproduces,
in risk orientation, the answer-prior confound observed in earlier BoolQ work:
when natural counter-evidence is absent, the score re-associates with the
yes/no structure of the item rather than with error. The placebo flip is clean
(0.052) and the pipeline is fully valid, so the negative is not attributable
to pipeline invalidity; it marks the limit of substituting negation-prefix
reversal for natural counter-evidence. The subgroup divergence is reported as
an observed boundary, not as evidence for a specific causal mechanism.

### 5.1.2 FEVER: vacuous under the pair-construction requirement

FEVER cannot provide the pair structure the probe requires. Verification found
zero same-claim SUPPORTS/REFUTES natural pairs in the validation split—no
same-claim pair in which one verdict is SUPPORTS and the other REFUTES. A
near-duplicate claim-pair construction was attempted with an offline semantic
audit; the paired REFUTES claim's evidence was almost always the same (or
near-identical) sentence as the SUPPORTS evidence, with evidence overlap
Jaccard 1.000. Only 1 of 60 candidate pairs passed both audit judgments.

Because the reverse operation cannot be implemented as a natural
counter-evidence swap, the probe is vacuous for FEVER. No agent calls were made
on FEVER and no result is claimed. This is a structural mismatch in pair
construction—an empirically verified construction boundary—not a behavioral
null estimate.

### 5.1.3 S&P500: null in an as-of sequential setting

The S&P500 analysis is an as-of sequential stress test in a non-pair
sequential setting. The result is null. No alpha claim is made: the analysis
does not establish returns, excess performance, or a deployable financial
predictor, and it does not support any claim of predictability on the
financial axis. The S&P500 boundary is reported to make the axis-native scope
explicit rather than to imply any financial conclusion.

### 5.1.4 Summary: the signal is axis-native

Taken together, the axis-native results are heterogeneous: VitaminC supports
the intended direction (AUROC 0.943/0.896/0.969); BoolQ reverses it (0.449);
FEVER is vacuous under the pairing requirement; and S&P500 is null in a
non-pair sequential setting. The pattern is a specificity result, not a
contradiction of the main finding: it supports the interpretation that the
risk signature is specifically tied to the fixed gold-opposing natural-pair direction,
not to arbitrary perturbations. CST-Bench should be applied
when the task supplies a semantically appropriate natural-pair axis; the
instrument's claims do not generalize to arbitrary axes, and we state that
boundary explicitly.

## 5.2 Mechanism probes versus predictors

Intervention-derived features that reveal stable behavioral differences are
mechanism probes. They become predictors only if they rank errors in an
outcome-independent, out-of-sample-validated way; the two are not
interchangeable. This rule is applied to three candidates below: the
independent claim-only counter-evidence score (retained as a mechanism probe,
not a predictor), the selective-responsiveness score E_sel (dropped), and a
graph-augmented CST framing (dropped).

### 5.2.1 Independent claim-only counter-evidence: a probe, not a predictor

Independent counter-evidence—counter-evidence generated from the claim alone,
textually independent of the natural mirror—shows a descriptive behavioral contrast under the tested protocol:

rates under decision-relevant independent counter-evidence exceed the topic-matched,
decision-irrelevant placebo. However, the corresponding preregistered placebo ceiling (G4)
fails in the W2 v1 and both strict analyses, so these results do not constitute clean
placebo-controlled validation of an independent-CE effect. This makes independent counter-evidence useful as a bounded, mechanism-oriented probe. It is not, however, a validated independent
predictor.

The independent score must be reported by protocol version. The rows below are not a pooled estimate; they are separate analyses with different protocol and cohort definitions. W2 v1 is an exploratory, non-final protocol that predates the stricter TARGET_SPEC and is shown for transparency rather than promoted as the primary independent-prediction endpoint. Under the final strict TARGET_SPEC analyses, no independent predictive increment was established.

| Protocol / cohort | \(S_{\mathrm{ind}}\) AUROC | OOF increment over \(S_{\mathrm{natural}}\) | Interpretation |
|---|---:|---:|---|
| W2 v1 (cohort HC=96/wrong=8; metric n=96, 50 pairs) | 0.983 | +0.045 [0.015, 0.084] | Exploratory, non-final protocol; not predictive validation |
| strict TARGET_SPEC, larger cached (cohort HC=96/wrong=8; \(S_{\mathrm{ind}}\) n=72, 42 pairs; OOF n=72, wrong=5) | 0.699 (CI includes 0.5) | +0.027 [0.000, 0.058] | Strict target; no established independent increment |
| strict TARGET_SPEC, 25-pair (cohort HC=47/wrong=3; \(S_{\mathrm{ind}}\)/OOF n=46, 25 pairs) | 0.624 [0.286, 0.856] | +0.004 [-0.074, 0.047] | CI includes 0.5; no detectable increment |

**Table 6: Protocol-specific independent counter-evidence results; mechanism probe only.**

The ranking standard is deliberately strict. A predictor must rank errors in an
outcome-blind, label-free, out-of-sample-validated manner once the resource is fixed,
and its increment must be distinguishable from the natural-pair score. The final strict
TARGET_SPEC S_ind result does not meet this standard; W2 v1 remains an exploratory
positive diagnostic rather than a validated primary endpoint. We therefore never present S_ind, or any Δ_CE quantity, as an
independent predictor. The only validated pre-outcome ranking signal in this
paper remains the primary natural-pair score RS_q; S_natural is a separate natural-mirror
diagnostic, and independent counter-evidence is presented exclusively as a mechanism probe.

### 5.2.2 E_sel is dropped: a reparameterization

The selective-responsiveness score E_sel was proposed as a new behavioral axis
(Round8 mechanism M-A) and was falsified on frozen data. E_sel is a
deterministic reparameterization of the two existing flip rates
(p_nat, p_placebo), so it cannot reveal a new axis. Its ranking adds nothing
over S_natural: the paired difference E_sel_nat − S_natural is −0.032
[−0.104, +0.004], a CI that touches zero. Its placebo leg is equivalent to the
answer prior in ranking: p_placebo − 1[consensus=yes] = +0.004 [−0.115,
+0.110], with item-level ρ(E_sel_nat, p_placebo) = 0.897.

The falsifiable prediction E_sel_wrong > E_sel_correct was statistically real
on frozen data but did not survive decomposition. Within the consensus-direction-stratified
analysis, the placebo leg is largely answer-prior-like and does not provide a wrong-specific
ranking signal; a residual direction-normalized contrast remains unresolved. E_sel is therefore dropped as a novel
mechanism and as a score; no independent E_sel claim is retained anywhere in the paper. Its
natural-pair component does not add a new contribution.

### 5.2.3 Graph study: dropped

A graph-augmented CST framing was evaluated with three frozen-data probes and
is dropped. The evidence graph is degenerate by construction: effective support
is ≈ 1.0 (1.04/1.02), with only 2 unique cited identifiers per item, so
evidence-overlap, diversity, and concentration features carry almost no
item-level variance. The proposed consensus-opposing retention/flip feature is
a mirror-image re-encoding of the existing direction probe (Pearson vs
S_natural = −0.79; AUROC 0.74 ≤ S_natural 0.83; paired bootstrap unstable at
n=16), and matched-consensus separation (5/5 agreement; wrong-n=5) merely
reproduced the known gold-opposing direction probe. Graph augmentation is
therefore unsupported by the current evidence, and we retain the simpler CST
analysis; this says nothing about graphs in general—only that this
construction, with this evidence-generation regime (a single shared evidence
packet) and this probe set, does not establish an independent contribution.

### 5.2.4 Rule summary

The rule is narrow and is stated as a boundary: intervention-derived probes
are predictors only if they provide an outcome-independent, out-of-fold-
validated ranking. The independent-counter-evidence, E_sel, and graph analyses
do not satisfy that criterion. They are either retained exclusively as probes
(independent counter-evidence) or dropped outright (E_sel; the graph framing),
never relabeled as predictive gains.
