# When Consensus Lies: Counter-Evidence Responsiveness as a Pre-Outcome Signal of Consensus Error

**Target venue:** NAACL (main). **Status:** integrated draft v3, generated 2026-09-14.
**Figures:** not yet included (pending). **Citations:** external references are marked `[CITE]`
and must be completed before submission; every experimental number has a 95% CI and traces
to the frozen round-3/4/5/6 artifacts under `consensus_stress/` (see `round6/paper/sections/`
for per-section provenance notes and `round6/paper/README.md` if added).

*Candidate alternative titles (from drafting):*
1. When Consensus Lies: Counter-Evidence Responsiveness as a Pre-Outcome Signal of Consensus Error
2. When Consensus Lies: Do Panels Change Their Answer under Natural Counter-Evidence?
3. When Consensus Lies: Ranking Multi-Agent Consensus Errors from Responses to Natural Counter-Evidence

---


1. **When Consensus Lies: Counter-Evidence Responsiveness as a Pre-Outcome Signal of Consensus Error**
2. **When Consensus Lies: Do Panels Change Their Answer under Natural Counter-Evidence?**
3. **When Consensus Lies: Ranking Multi-Agent Consensus Errors from Responses to Natural Counter-Evidence**

---

## Abstract

Multi-agent LLM panels are increasingly used for fact verification, but consensus is not evidence of correctness: panels can converge on incorrect answers with high agreement. We study whether the error risk of an already-formed consensus can be ranked *before the outcome is known* using a single evidence-level behavior—whether the panel changes its answer after its evidence packet is replaced with natural counter-evidence. On a frozen 300-pair, 600-item VitaminC natural-pair protocol, we compute RS_q = −BF_q, a label-free composite of paraphrase stability and counter-evidence responsiveness. RS_q ranks consensus errors with AUROC 0.943 [0.924, 0.960] and Risk@80 0.846 [0.638, 0.981] for Qwen3.5-4B panels, and AUROC 0.896 [0.873, 0.916] and Risk@80 0.422 [0.274, 0.591] for Ling-3.0-tiny panels. A frozen cross-model procedure transfer reaches AUROC 0.723 [0.682, 0.765], while a single-point 100-item GPT-class validation reaches 0.969 [0.935, 0.995]. The signal is specific to natural counter-evidence: a negation-prefix control (BoolQ) reverses the direction (AUROC 0.449). On this frozen protocol, the reversal axis is a deterministic re-encoding of mirror-item behavior. We therefore report responsiveness as a descriptive, pre-outcome behavior—not as a latent trait or causal explanation. Our claims are deliberately bounded to two small open models, one GPT-class single point, and one dataset.

## 1 Introduction

### 1.1 Motivation: consensus is not reliability

Multi-agent LLM panels—several personas sampled from one or more models that read shared evidence and vote—are a common recipe for fact verification and reasoning [CITE]. A panel that converges on one answer with high agreement appears trustworthy: it has examined the same evidence, reasoned through different personas, and still reached the same conclusion. Agreement, however, is an *internal* property of the panel; by itself, it does not establish that the evidence supports the answer. A panel can be unanimous and wrong. Confidence scoring does not resolve this failure mode: on our frozen benchmark, vote agreement and several confidence variants rank consensus errors only slightly above chance (AUROC 0.58–0.73 on Qwen3.5-4B panels), and their paired AUROC differences from our proposed score have confidence intervals that exclude zero (e.g., +0.360 [0.305, 0.412] versus vote agreement; +0.315 [0.271, 0.360] versus an internal symmetric risk score).

We therefore ask a narrower, pre-outcome question: once a consensus has formed, can we rank *which* consensuses face elevated error risk using only evidence-level behavior, before the answer is labeled? We focus on one behavior: whether the panel changes its answer when its evidence packet is replaced with the *natural* counter-evidence—the evidence that supports the opposite verdict.

### 1.2 What we measure, and the mirror-equivalence caveat

We use the VitaminC natural-pair construction [CITE]. Each pair (i, j) shares a claim and a distractor but has opposite gold labels, and the two evidence packets constitute one another's natural counter-evidence. The frozen protocol (600 items; five agents per item, temperature 0) records each agent under the original evidence, a meaning-preserving paraphrase, and the swapped natural counter-evidence. The pre-registered score is RS_q = −BF_q, where BF_q averages two label-free components: *paraphrase stability*—the agent retains its answer under rewording, with its original answer as the expected answer—and *counter-evidence responsiveness*—the agent changes its answer to the flip of its original answer under the natural evidence swap. Features are frozen without labels; outcomes are merged only afterward.

We state the central interpretive caveat explicitly because it bounds the paper's claims. On this frozen protocol, the reverse-view prompt for item i is byte-identical to the original-view prompt for mirror item j: the claim, persona, partition, evidence texts, distractor, and seed all coincide. Empirically, answers agree on 99.97% of Qwen and 99.63% of Ling agent calls. Consequently, BF_reverse is a deterministic re-encoding of the panel's original answer, its mirror-item answer, and the frozen paired gold. Conditional on an agent being correct on the original item, BF_reverse is *identically* the agent's correctness on the mirror item; on wrong items, it is the complement. In plain terms, the reversal axis measures whether the panel's mirror-item answer aligns with the flip of its original answer. This is a real, pre-outcome-computable behavioral regularity, but it is not an independent probe of a latent “responsiveness” trait and is not causal: the data cannot distinguish “non-responsive to counter-evidence” from “the mirror gold aligns with the wrong answer.” We report the behavior and its predictive ranking; we do not claim a mechanism.

### 1.3 Why pre-outcome ranking matters

A label-free score computed before outcomes are known has a concrete use in selective routing and abstention. Downstream systems can flag high-risk consensus items for human review, additional evidence collection, or abstention without waiting for a gold label. Routing also makes cost relevant: the 10-call reversal-plus-paraphrase score is numerically identical to RS_q (paired Δ = 0.000 [0.000, 0.000] on both models), so the full ranking requires no more than the panel's own original and mirror-condition calls. The frozen protocol's outcome firewall—labels are merged only after feature freezing—matches the setting in which such a score would be deployed.

### 1.4 Contributions

- **A pre-outcome, label-free risk score.** We define counter-evidence responsiveness operationally as BF_reverse, the fraction of agent calls that change their answer to the flip of the original answer under the natural evidence swap. We combine it with paraphrase stability in the frozen composite RS_q = −BF_q and show that it ranks consensus errors with AUROC 0.943 [0.924, 0.960] and Risk@80 0.846 [0.638, 0.981] (Qwen3.5-4B, 567 HC items), and AUROC 0.896 [0.873, 0.916] and Risk@80 0.422 [0.274, 0.591] (Ling-3.0-tiny, 574 HC items), with paired AUROC differences from agreement- and confidence-based baselines whose CIs exclude zero.
- **Bounded cross-model and cross-size evidence.** A frozen procedure transfer—Qwen item-level RS_q applied to Ling errors—reaches AUROC 0.723 [0.682, 0.765], above chance but significantly below Ling's own 0.896. Thus, item-level ranking is partly model-specific. A single-point, 100-item GPT-class validation reaches AUROC 0.969 [0.935, 0.995] (within-model HC n=96, wrong n=8). Per-label consistency holds for Qwen (SUPPORTS 0.917 / REFUTES 0.986).
- **Specificity to natural counter-evidence.** The signal reverses direction on a negation-prefix control (BoolQ AUROC 0.449), indicating that it tracks natural counter-evidence rather than arbitrary perturbation. A FEVER replication was blocked at construction because no natural pairs exist in the data; we report this boundary rather than a proxy result.
- **Controls and reducibility.** Paraphrase placebo flip rates are low (0.038 Qwen / 0.061 Ling), indicating that reverse-axis asymmetry is not general prompt instability. Permutation controls are passed (0.943 > 95th pct 0.596; 0.896 > 0.564), and RS_q is not a re-expression of agreement (Spearman −0.004) or confidence (−0.161) on Qwen.
- **An honest measurement-level interpretation.** We state the mirror-equivalence reduction explicitly: BF_reverse is a label-aligned re-encoding of the panel's original and mirror answers with the frozen paired gold. On correct consensus it coincides with mirror-item accuracy; on wrong consensus it is its complement. The contribution is a descriptive, pre-outcome behavioral regularity and its ranking performance, without a causal, trait, or framework claim.

### 1.5 Scope and claims

This paper does **not** claim: (i) a “consensus stress testing framework” with causal stress curves or breakpoints as mechanism evidence; (ii) “expected-response faithfulness” as a latent trait; (iii) “evidence insensitivity” or rigidity as an explanation of *why* a consensus is wrong; (iv) causal identification—that counter-evidence causes error, or that responsiveness causes correctness; (v) universal transfer, zero-shot generalization, or superiority over every reliability baseline; (vi) results on arbitrary perturbations or datasets beyond the frozen VitaminC natural-pair protocol; or (vii) any result for FEVER or other blocked datasets. The empirical basis is two small open models (Qwen3.5-4B, Ling-3.0-tiny) plus one GPT-class single point, on one dataset, with one specificity negative. Anticipating reviewer concerns: yes, at its core this is a flip/stay measurement—on this protocol, precisely a label-aligned re-encoding of mirror-item behavior—and we treat that as the finding rather than explain it away; yes, there is only one dataset, and we surface the FEVER construction block instead of papering over it; yes, the models are small, and we label the GPT-class result a preliminary single point rather than a generalization claim.

---

---
