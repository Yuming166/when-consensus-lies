# 3 Method

## 3.1 CST-Bench

CST-Bench is an outcome-blind, label-free scoring protocol on an offline gold-conditioned natural-pair resource for measuring whether a consensus panel updates toward decision-relevant counter-evidence. Its primary output is a risk score computed before outcome labels are merged. The protocol is not intended to measure a general property of “rigidity to counter-evidence.” Instead, it uses a fixed natural-pair probe whose evidence is assigned to argue against the item’s gold label. The defining feature of this probe is therefore its direction, not near-duplicate overlap.

### 3.1.1 Panel and consensus

Each panel contains five frozen agents. The evidence packet is distributed using a frozen assignment table, with each agent receiving a fixed view of the packet. Every non-remove view contains decision-relevant evidence. Inference uses deterministic decoding and frozen per-agent and per-condition settings. Requests and outputs are cached and content-addressed; failed generations are handled using the preregistered repair procedure.

Consensus is formed from the five original-condition calls. The consensus answer is the majority answer, and high consensus (HC) denotes agreement by at least 0.8 of the panel, equivalently at least 4/5 agents. The later evaluation outcome is

\[
\mathrm{consensus\_wrong}_i
=
\mathbf{1}
[
\mathrm{consensus}_i
\ne
\mathrm{gold}_i
].
\]

This outcome is unavailable when the stress-test features are computed. Evaluation therefore asks whether a score available before labels can rank items by subsequent consensus error.

### 3.1.2 Main probes

For each agent, the main probe suite contains two conditions.

**Natural mirror.** The original evidence is replaced by the evidence from the paired item. The pair is constructed so that this evidence argues against the item’s gold label. Relative to the original response, the expected behavior is therefore a directionally appropriate flip: a correct original answer should be opposed by the mirror evidence, whereas a wrong original answer is aligned with it.

**Paraphrase placebo.** The evidence is reworded while preserving its meaning. The expected behavior is answer stability. This condition tests whether the panel changes in response to content-preserving reformulation rather than to decision-relevant evidence.

The natural mirror is not interpreted as a generic test of counter-evidence responsiveness. Its interpretation is gated by the fixed relation between the paired evidence and the item’s gold label. In particular, the protocol does not treat natural-pair similarity or overlap as the scientific target.

### 3.1.3 Auxiliary diagnostics

The protocol retains auxiliary conditions for auditing and interpretation, but these calls do not enter the primary score.

A content-level matched placebo uses topic-matched but decision-irrelevant content. It is not assumed to be neutral: the observed flip rate is 0.51--0.56 and is direction-asymmetric, with rates of 0.92 for yes-answerers and 0.09 for no-answerers. We therefore report this condition as a diagnostic rather than as a clean placebo.

An independent claim-only counter-evidence (CE) condition generates counter-evidence from the claim alone, in both directions, and assigns the direction offline to oppose the gold label. This condition is a mechanism probe: it tests whether directionally aligned counter-evidence can induce the expected response without the natural-pair construction. It is not treated as an independent predictor. The larger cached strict TARGET_SPEC analysis (cohort HC n=96, wrong=8; \(S_{\mathrm{ind}}\) scored n=72 over 42 pairs; OOF n=72 with wrong=5) gave \(S_{\mathrm{ind}}\) AUROC 0.699 (CI includes 0.5) and OOF increment +0.027 [0.000,0.058]. The separate strict 25-pair analysis (cohort HC n=47, wrong=3; metric/OOF n=46 over 25 pairs) gave \(S_{\mathrm{ind}}\) AUROC 0.624 [0.286,0.856] and OOF increment +0.004 [-0.074,0.047]. An earlier W2 v1 protocol gave AUROC 0.983 with OOF increment +0.045 [0.015,0.084] on HC n=96. These are protocol-specific mechanism results, not a pooled range and not a deployment claim.

### 3.1.4 Call accounting

Each item uses 5 consensus calls, 10 main-probe calls, and 10 auxiliary-diagnostic calls:

| Call group | Conditions | Calls per item | Used in \(RS_q\) |
|---|---|---:|:---:|
| Consensus formation | Original | 5 | Yes |
| Main probe | Paraphrase and natural mirror | 10 | Yes |
| Auxiliary diagnostics | Synthetic reverse and remove | 10 | No |
| **Total** | — | **25** | — |

The primary score uses the original consensus calls and the two main-probe conditions only. Auxiliary diagnostics are excluded from \(RS_q\), so they cannot alter the primary ranking.

## 3.2 Outcome firewall and preregistered protocol

### 3.2.1 Outcome firewall

Gold labels are merged only after all pre-outcome features have been computed, frozen, and hashed. The gold label, per-agent correctness, the binary `consensus_wrong` outcome, and any equivalent label-derived quantity are forbidden inputs to score computation.

Labels may be used offline to construct the frozen balanced design and to assign the direction of the natural-pair and independent-CE artifacts. They are not provided to the agents and are not available to the pre-outcome scoring procedure. This distinction separates construction metadata from features available at prediction time.

The leakage audit covers prompt construction, evidence generation, scoring, model selection, and threshold selection. The intended data flow has no path from evaluation outcomes to the label-free features or their preregistered selection.

### 3.2.2 Frozen gates and preregistration

Protocols, cohort definitions, manifests, probe construction, and evaluation rules are frozen before model calls. The preregistered gates include pipeline validity, primary and label-stratified AUROC criteria, placebo stability, permutation comparison, and checks against reducing \(RS_q\) to agreement or mean confidence. The formal Risk@80 analysis additionally requires a paired Risk@80 confidence interval that excludes zero.

These gates are not tuned after outcomes are observed. A failed gate is reported as a failure rather than used to revise the protocol.

The frozen protocol identifiers and manifests record deterministic cohort construction and SHA256 hashes. The independent-CE and direction-gated analyses use their corresponding preregistered specifications.

### 3.2.3 Uncertainty

Confidence intervals are computed with pair-grouped bootstrap resampling. The two members of a natural pair are resampled together, rather than treating paired items as independent. This procedure is used for AUROC, Risk@80, flip-rate differences, and paired AUROC differences.

## 3.3 Formal definitions

Let \(i\) index an item, \(a\) index one of the five agents, and \(c\) index a probe condition. Let \(Y(i,c,a)\) denote the parsed binary answer under condition \(c\). Let \(Y_0(i,a)\) denote the answer under the original condition.

For each condition, the frozen expected-response oracle specifies the behavior tested by the protocol. The paraphrase expectation is answer preservation,

\[
Y^*(i,\mathrm{para},a)=Y_0(i,a),
\]

whereas the natural-mirror expectation is a flip,

\[
Y^*(i,\mathrm{natural},a)=\mathrm{flip}(Y_0(i,a)).
\]

Define per-agent fidelity to these expected responses as

\[
f_c(i,a)
=
\mathbf{1}
[
Y(i,c,a)=Y^*(i,c,a)
].
\]

The baseline fidelity is

\[
BF_q(i)
=
\frac{1}{5}
\sum_a
\frac{
f_{\mathrm{para}}(i,a)
+
f_{\mathrm{natural}}(i,a)
}{2},
\]

and the primary risk score is

\[
RS_q(i)=-BF_q(i).
\]

Higher \(RS_q\) therefore denotes lower fidelity to the preregistered probe expectations and higher measured stress-test risk. The score is computed without the evaluation outcome.

For interpretation of the natural condition, define the observed response flip

\[
\mathrm{flip}(i,a,c)
=
\mathbf{1}
[
Y(i,c,a)\ne Y_0(i,a)
].
\]

The label-free natural-counter-evidence responsiveness score is

\[
S_{\mathrm{natural}}(i)
=
\frac{1}{5}
\sum_a
\mathrm{flip}(i,a,\mathrm{natural}).
\]

The independent-CE diagnostic is defined analogously:

\[
S_{\mathrm{ind}}(i)
=
\frac{1}{5}
\sum_a
\mathrm{flip}(i,a,\mathrm{independent\ CE}).
\]

\(S_{\mathrm{ind}}\) is reported as a mechanism diagnostic and is not promoted to an independent predictive feature.

### 3.3.1 Direction-gated interpretation

The natural mirror argues against the item’s gold label. Consequently, for a correct consensus it opposes the panel’s answer, while for a wrong consensus it agrees with the panel’s wrong answer. A high natural-mirror flip rate can therefore be interpreted only together with this fixed direction relation.

The observed natural-mirror flip rate is 0.902 for correct consensus and 0.075 for wrong consensus. The corresponding Qwen values are 0.843 and 0.095, and the corresponding Ling values are 0.703 and 0.029.

This asymmetry is described as a direction-gated behavioral regularity. It is not evidence for a general causal mechanism of counter-evidence processing, and it does not support a claim that the panels are rigid to counter-evidence in general.

The direction-gated analysis further uses the Round10 \(2\times2\) experiment, which contains 16 generation + 2 audit + 160 inference calls (178 logical calls). Inference validity was 145/160; generation parsing was valid for 10/16 items, while 6/16 were format-invalid but recorded, loose-extracted, and audited. The direction audit found 10/16 clean agree sentences and 10/16 clean contradict sentences. The CONTRADICT-minus-AGREE direction contrast is \(+0.44\) with a 95% interval of \([0.24,0.65]\). In the as-assigned independent-CONTRADICT condition, the wrong consensus flips in 0.946 of cases (35/37). After direction auditing, the clean subset is 30/32 across 7 clean items. The post-hoc Probe1 extension yields an as-assigned total of 44/46; it adds 2 items / 9 agent rows and is not a fully audited clean result. Within the direction-stratified comparison, the natural mirror was numerically similar to the direction-clean independent-CE condition; this does not establish equivalence. The direction-clean construction comparison has \(n=3\) items, so a small independent-overlap effect is not ruled out.

For the natural-pair design, \(S_{\mathrm{pair}}\), computed from the two original answers, reconstructs the reverse axis with Spearman correlation 0.998 and recovers approximately 98.7%/97.0% of the \(RS_q\) ranking. This is treated as a property of the natural-pair construction, not as evidence for a broader behavioral mechanism.

## 3.4 Dataset designs

### 3.4.1 VitaminC natural pairs

The primary design uses the frozen VitaminC natural-pair manifest containing 300 pairs and 600 items. Each pair contains one SUPPORTS item and one REFUTES item sharing the relevant claim context. The evidence from one member supplies the natural counter-evidence for the other.

Qwen3.5-4B and Ling-3.0-tiny are evaluated with five-agent panels. gpt-6-astra is evaluated as a single point.

Within the HC subset, \(RS_q\) yields AUROC 0.943 \([0.924,0.960]\) for Qwen, based on 567 HC items with 65 wrong; Ling yields 0.896 \([0.873,0.916]\), based on 574 HC items. Risk@80 is 0.846 \([0.638,0.981]\) for Qwen and 0.422 for Ling. The gpt-6-astra single-point AUROC is 0.969 \([0.935,0.995]\), based on 96 HC items with 8 wrong.

### 3.4.2 BoolQ

BoolQ supplies an axis-native negative design because it does not provide the VitaminC-style natural evidence swap. Its reverse construction uses a negation-prefix operation rather than a natural counter-evidence pair.

Under this design, \(RS_q\) obtains AUROC 0.449 \([0.308,0.579]\), with the direction reversed, and the permutation gate fails. BoolQ is therefore retained as a boundary condition on the natural-pair protocol rather than folded into the VitaminC claim.

### 3.4.3 FEVER

FEVER does not provide a usable natural-pair construction for this probe: its evidence-overlap Jaccard is 1.000. The natural-pair test is consequently vacuous for this dataset, and the protocol does not treat the absence of a usable contrast as evidence for or against the CST-Bench measurement claim.

### 3.4.4 S&P500

The S&P500 analysis is an as-of sequential stress test. It is reported as a null result and is not used to claim alpha, market predictability, or an explanation of market behavior.

## 3.5 Scope of the measurement claim

CST-Bench is a reliability-measurement protocol evaluated for pre-outcome risk ranking under the frozen VitaminC natural-pair design, paired with a direction-gated behavioral regularity. Its central evidence is that a fixed gold-opposing natural-pair probe distinguishes correct from wrong consensus decisions in the VitaminC design. The protocol does not claim a general property of counter-evidence processing, a causal or mediation mechanism, or an explanation of why language models fail.

The independent claim-only CE condition is a mechanism probe rather than an independent predictor. The answer-prior and placebo analyses test whether the primary result can be reduced to answer frequency or an uncontrolled direction artifact. The BoolQ reversal, FEVER construction failure, and S&P500 null delimit where the natural-pair measurement claim does and does not apply.
