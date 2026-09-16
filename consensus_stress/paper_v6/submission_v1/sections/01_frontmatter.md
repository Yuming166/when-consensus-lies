# CST-Bench: Measuring Consensus Reliability with Direction-Gated Natural-Pair Stress Tests

## Abstract

Consensus does not guarantee correctness. We study whether an outcome-blind, label-free scoring
procedure applied to an offline gold-conditioned natural-pair resource can measure the reliability
of consensus decisions by probing whether panels update toward decision-relevant counter-evidence. CST-Bench uses five consensus calls, ten main-probe calls, and
ten auxiliary calls with frozen gates, an outcome firewall, preregistration, and pair-grouped
confidence intervals. The natural-pair resource is constructed offline with gold-conditioned
direction, while scoring is label-free and outcome-blind once the resource is fixed. The probe
argues against the item's gold answer; its power is therefore the evidence direction, not near-duplicate
overlap. On VitaminC
natural pairs (300 pairs / 600 items), the probe flips 0.902 of correct consensus decisions and
0.075 of wrong decisions. RS_q = −BF_q reaches AUROC 0.943 [0.924, 0.960] for Qwen (567 HC, 65
wrong), 0.896 [0.873, 0.916] for Ling (574 HC), and 0.969 [0.935, 0.995] in a single-point
evaluation (96 HC, 8 wrong). The result is bounded: BoolQ reverses direction, FEVER has no usable
natural pairs, and S&P500 yields a null as-of sequential stress-test result. Answer-prior and
placebo controls provide negative evidence against the tested answer-prior and placebo alternatives. Independent claim-only
counter-evidence is a mechanism probe, not an independent predictor. CST-Bench is thus a
reliability-measurement protocol evaluated under the frozen VitaminC natural-pair design, not evidence
for general counter-evidence rigidity or a causal account of model failure.

---

## 1 Introduction

### 1.1 Motivation: multi-agent consensus is unreliable

Multi-agent LLM panels—several personas sampled from one or more models that read shared evidence
and vote—are a common recipe for fact verification and reasoning \citep{du-etal-2024-multiagent-debate}. Consensus can improve
decision procedures, but agreement is not correctness: a panel may converge on the wrong answer,
and the convergence can obscure uncertainty that matters before the outcome is known. The practical
question is not whether consensus is ever wrong (it is) but whether the reliability of an
already-formed consensus decision can be measured without waiting for, or peeking at, the outcome.

This paper studies a narrower, measurable form of that question: whether a probe can rank which
consensus decisions are unreliable when scoring is *outcome-blind and label-free* conditional on an
offline gold-conditioned natural-pair construction, and how far such a probe generalizes. The setting is a collection of natural item pairs whose content provides evidence in a
known direction. On the VitaminC collection—300 pairs / 600 items with a frozen manifest—panels
built from Qwen3.5-4B and Ling-3.0-tiny respond to a fixed probe selected to oppose the item's gold
answer. The probe changes correct consensus decisions more often than wrong ones: the natural-mirror
flip rates are 0.902 for correct consensus (Qwen 0.843, Ling 0.703) and 0.075 for wrong consensus
(Qwen 0.095, Ling 0.029). These results motivate a measurement instrument, not a claim that
language models are generally rigid to counter-evidence.

Standard reliability signals are weak here. Confidence calibration and sampling consistency are
computed on repeated samples of the *same* input and do not intervene on the evidence; they are
also typically defined for a single model rather than an already-formed multi-agent panel. A
stress-test probe that replaces the evidence packet with natural counter-evidence targets exactly
the object of interest—whether an existing consensus decision changes when its evidential
underpinning is challenged—and it can be run before any outcome is known. CST-Bench formalizes
this idea as an outcome-blind, label-free scoring protocol on a fixed gold-conditioned resource
rather than as a post-hoc diagnostic.

### 1.2 Research question

> Can a stress-test protocol—whose scoring is outcome-blind and label-free conditional on a fixed,
> offline gold-conditioned natural-pair resource—expose which consensus decisions are unreliable when
> panels are probed with decision-relevant counter-evidence, and how far does this generalize?

The paper separates predictive measurement from mechanism evidence. CST-Bench measures reliability
with a direction-gated probe: the natural pair is selected because it argues against the item's
gold answer. The probe's power is its **direction**, not near-duplicate overlap. Accordingly, the
paper does not claim a general "rigidity to counter-evidence" mechanism, an
independent-counter-evidence predictor, a causal or mediation effect, or an explanation of why
language models fail.

The score is RS_q = −BF_q (paraphrase stability + natural counter-evidence responsiveness),
outcome-blind and label-free once the fixed resource is constructed. On the evaluated VitaminC items, the primary score RS_q obtains AUROC 0.943
[0.924, 0.960] for Qwen (567 HC, 65 wrong), 0.896 [0.873, 0.916] for Ling (574 HC), and 0.969
[0.935, 0.995] for the gpt-6-astra single-point evaluation (96 HC, 8 wrong). These results support
the instrument on this benchmark; they do not establish universal transfer or a general mechanism.

Accordingly, the reported AUROCs are conditional on the frozen VitaminC resource and its gold-conditioned offline construction; outcome-blindness applies only after freezing, the Qwen-to-Ling result is a single transfer check, and \(S_{\mathrm{ind}}\) and Round10 provide neither independent predictive nor causal evidence.

### 1.3 Why a pre-outcome stress-test probe

Once its resource is fixed, a pre-outcome scoring test should withhold labels, distinguish evidence
direction from superficial similarity, and follow a controlled procedure. CST-Bench addresses these requirements with five
consensus calls, ten main-probe calls, and ten auxiliary calls; frozen gates; an outcome firewall;
preregistration; and pair-grouped confidence intervals (Section 3).

The fixed natural-pair probe argues against the item's gold answer, so its signal is direction, not
overlap. Two pieces of evidence make this precise. First, a score formed only from the two original
answers, S_pair, reconstructs the reverse-axis ranking with Spearman 0.998 and recovers
~98.7% (Qwen) / ~97.0% (Ling) of the RS_q ranking: the ranking is a *natural-pair property*.
Second, a clean neutral paraphrase placebo flips only 0.038, while a content-level matched placebo
flips 0.51–0.56 and is direction-asymmetric (0.92 among yes-answerers, 0.09 among no-answerers).
Content change alone therefore does not provide a clean interpretation of the signal; the direction
of the evidence change must be controlled.

The regularity is **axis-native** rather than universal. On BoolQ, where the reverse operation is a
negation-prefix rather than natural counter-evidence, RS_q has AUROC 0.449 [0.308, 0.579]: the
direction is reversed and permutation fails. On FEVER, evidence overlap has Jaccard 1.000, leaving
no usable natural pairs and making the probe vacuous. On S&P500, an as-of sequential stress test is
null; no alpha claim is made. The graph study is dropped.

Answer-prior controls bound the probe further. The answer prior 1[consensus=yes] alone has AUROC
0.671 / 0.634 (Qwen / Ling), far below the probe (0.943 / 0.896), and the probe is not a label
artifact (label AUROC 0.51). The tested answer-prior comparator did not match the probe in this evaluation; this comparison does
not establish causal mediation or rule out every label-related interaction.

### 1.4 Contributions

**C1 — A direction-gated empirical regularity.** A fixed gold-opposing natural-pair probe separates
correct from wrong consensus decisions before outcomes are used: panels update toward the evidence
direction at ~0.90 for correct consensus and ~0.08 for wrong consensus (natural-mirror flip 0.902
vs 0.075; Qwen 0.843/0.095, Ling 0.703/0.029). RS_q ranks consensus errors from outcome-blind, label-free features once the resource is fixed, at AUROC 0.943 [0.924, 0.960] (Qwen), 0.896 [0.873, 0.916] (Ling), and 0.969
[0.935, 0.995] (gpt-6-astra single point). These are predictive measurements on the evaluated
data, not evidence for a general rigidity mechanism.

**C2 — CST-Bench as a reliability-measurement protocol.** CST-Bench uses five consensus calls, ten
main-probe calls, and ten auxiliary calls with frozen gates, an outcome firewall, preregistration,
and pair-grouped confidence intervals, producing an outcome-blind, label-free score RS_q = −BF_q after offline resource construction.
A single cross-panel portability check applying the Qwen-fixed procedure to Ling yields AUROC
0.723 [0.682, 0.765]; item-level Spearman(Qwen RS_q, Ling RS_q) = 0.496 (medium, not perfect).
This is not evidence of model-independent or out-of-domain generalization.

**C3 — Boundaries, controls, and honest negatives.** The observed signal is direction-gated and axis-native:
BoolQ reverses direction (AUROC 0.449 [0.308, 0.579]), FEVER is vacuous (no usable natural pairs,
overlap Jaccard 1.000), and S&P500 is null. Answer-prior (0.671/0.634 ≪ 0.94) and placebo controls
(paraphrase 0.038 clean; content placebo 0.51–0.56 and direction-asymmetric at 0.92 vs 0.09)
constrain label-only and paraphrase explanations. Independent claim-only counter-evidence is a
mechanism probe, not an independent predictor; the protocol-specific strict results are reported
with their cohort and version rather than pooled across runs. E_sel is dropped (Round9) as a reparameterization of S_natural + answer-prior.

Round10 provides mechanism-oriented descriptive evidence, not an additional predictor. In a 2×2 study (16 items / 178
calls), the direction contrast—opposing versus agreeing with the consensus—is +0.44 [0.24, 0.65].
The as-assigned independent-CONTRADICT cell flips wrong consensus at 0.946 (35/37); after direction auditing, the clean subset is 30/32 across 7 clean items.
The post-hoc two-item/9-row Probe1 extension gives an as-assigned total of 44/46 and is not a fully audited clean result. Within the direction-stratified comparison,
the natural mirror was numerically similar to the direction-clean independent condition; this does not establish
equivalence. The direction-clean construction comparison has n=3 items, so a small overlap effect is not ruled out. These results
are reported as a direction-sensitive interpretation with an explicit, unresolved small-n boundary—not
as an additional reliability predictor.

### 1.5 Scope of claims

The evidence base is the frozen VitaminC natural-pair protocol (300 pairs / 600 items), two small
open-weight panels (Qwen3.5-4B primary, Ling-3.0-tiny secondary), and one gpt-6-astra single point
(96 HC items). The central claim is a pre-outcome behavioral regularity under natural-pair
construction: consensus items that do not update toward gold-opposing evidence are substantially
more likely to be wrong, and this can be ranked before labels are observed. The regularity is
descriptive and predictive; it is not a latent cognitive trait, and it does not support a
mechanism claim about why some panels are wrong. Cross-dataset generality is explicitly not
claimed: BoolQ reverses the signal, FEVER has no usable natural pairs, and S&P500 is null. The
paper evaluates a reliability-measurement protocol under the frozen VitaminC natural-pair design
and reports a direction-gated behavioral regularity, not an explanation of consensus failure.

### 1.6 Related-work preview

Section 2 positions CST-Bench within four clusters: (a) sampling consistency and hallucination
detection (e.g., self-consistency, semantic entropy), where the signal derives from repeated
samples of the *same* input and no evidence intervention is applied; (b) selective prediction and
error prediction, which use a single model's output statistics on an unchanged input and do not
target an already-formed multi-agent consensus; (c) faithfulness and counterfactual evaluation,
which establish controlled perturbation as a valid probe but target single-model rationales or
reasoning traces rather than consensus answers; and (d) multi-agent reliability, metamorphic
testing, and consensus, which stress single-model qualities or form answers through debate rather
than probing an already-formed consensus. The distinguishing combination here is (i) an
already-formed multi-agent consensus as the object, (ii) a gold-conditioned natural-pair
probe whose scoring is label-free after the resource is fixed, and (iii) pre-outcome reliability measurement as the use. Citation
details are left to Section 2 and follow the dated literature audit (2026-09-12;
`consensus_stress/phase1/novelty_map.md`); no exhaustiveness claim is made.

### 1.7 Paper roadmap

Section 3 (method) describes the VitaminC natural pairs, panel construction, the CST-Bench call
accounting (5 + 10 + 10), the gold-opposing natural-pair probe, frozen gates, outcome firewall,
preregistration, pair-grouped CIs, and the formal definitions of RS_q / BF_q / S_natural with the
direction-gated interpretation. Section 4 (main experiments) reports VitaminC within-model results
(Qwen / Ling / gpt-6-astra), the Qwen → Ling procedure transfer, the S_pair natural-pair property,
the Round10 direction-gated analysis, and flip-rate asymmetry tables. Section 5 (boundaries and
negative results) reports the BoolQ / FEVER / S&P500 axis-native boundaries, the
mechanism-versus-prediction separation, the answer-prior and placebo asymmetry controls,
independent claim-only CE as a mechanism probe, the E_sel drop, the graph-study drop, and
limitations. Sections 2 (related work) and 6 (conclusion) position CST-Bench against consistency-based,
selective-prediction, faithfulness, and multi-agent reliability work and summarize the bounded
claims.

---
