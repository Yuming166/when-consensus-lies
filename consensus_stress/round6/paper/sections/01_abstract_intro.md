# When Consensus Lies: Counter-Evidence Responsiveness

## Candidate titles

1. **When Consensus Lies: Counter-Evidence Responsiveness as a Pre-Outcome Signal of Consensus Error**
2. **When Consensus Lies: Do Panels Change Their Answer under Natural Counter-Evidence?**
3. **When Consensus Lies: Ranking Multi-Agent Consensus Errors from Responses to Natural Counter-Evidence**

---

## Abstract

Multi-agent LLM panels are increasingly used for fact verification, yet consensus among agents is not evidence of correctness: panels can converge on a wrong answer with high agreement. We study whether the error risk of an already-formed consensus can be ranked *before the outcome is known*, from a single evidence-level behavior — whether the panel changes its answer after its evidence packet is swapped to the natural counter-evidence. On a frozen 300-pair, 600-item VitaminC natural-pair protocol, we compute RS_q = −BF_q, a label-free composite of paraphrase stability and counter-evidence responsiveness. RS_q ranks consensus errors with AUROC 0.943 [0.924, 0.960] and Risk@80 0.846 [0.638, 0.981] (Qwen3.5-4B panels) and AUROC 0.896 [0.873, 0.916] and Risk@80 0.422 [0.274, 0.591] (Ling-3.0-tiny panels); a frozen cross-model procedure transfer reaches AUROC 0.723 [0.682, 0.765], and a single-point 100-item GPT-class validation reaches 0.969 [0.935, 0.995]. The signal is specific to natural counter-evidence: a negation-prefix control (BoolQ) reverses direction (AUROC 0.449). On this frozen protocol the reversal axis is a deterministic re-encoding of mirror-item behavior, so we report responsiveness as a descriptive, pre-outcome behavior — not a latent trait and not a causal explanation. Our claims are deliberately bounded: two small open models plus one GPT-class single point, and one dataset.

---

## 1 Introduction

### 1.1 Motivation: consensus is not reliability

Multi-agent LLM panels — several personas sampled from one or more models that read shared evidence and vote — are a common recipe for fact verification and reasoning [CITE]. A panel that converges on one answer with high agreement looks trustworthy: it has seen the same evidence, argued from different personas, and still landed in the same place. But agreement is an *internal* property of the panel; it says nothing, by itself, about whether the evidence actually supports the answer. A panel can be unanimous and wrong. This is not a failure mode that confidence scoring fixes: on our frozen benchmark, vote agreement and several confidence variants rank consensus errors only slightly better than chance (AUROC 0.58–0.73 on Qwen3.5-4B panels), and their paired AUROC differences against our proposed score have confidence intervals that exclude zero (e.g., +0.360 [0.305, 0.412] vs. vote agreement; +0.315 [0.271, 0.360] vs. an internal symmetric risk score).

We therefore ask a narrower, pre-outcome question: once a consensus has formed, can we rank *which* consensuses are at elevated error risk using only evidence-level behavior, before the answer is labeled? We focus on one behavior in particular: whether the panel changes its answer when its evidence packet is swapped to the *natural* counter-evidence — the evidence that would support the opposite verdict.

### 1.2 What we measure, and the mirror-equivalence caveat

We use the VitaminC natural-pair construction [CITE]: each pair (i, j) shares a claim and a distractor but carries opposite gold labels, and the two evidence packets are the natural counter-evidence of one another. The frozen protocol (600 items; five agents per item, temperature 0) records each agent under the original evidence, a meaning-preserving paraphrase of it, and the swapped natural counter-evidence. The pre-registered score is RS_q = −BF_q, where BF_q averages two label-free components: *paraphrase stability* (the agent keeps its answer under rewording, where the expected answer is the agent's own original answer) and *counter-evidence responsiveness* (the agent's answer changes to the flip of its original answer under the natural evidence swap). Features are frozen without labels; outcomes are merged only afterward.

We state the central interpretive caveat up front, because it bounds everything in this paper. On this frozen protocol, the reverse-view prompt for item i is byte-identical to the original-view prompt for the mirror item j (the claim, persona, partition, evidence texts, distractor, and seed all coincide; empirically, answers agree on 99.97% of Qwen and 99.63% of Ling agent calls). Consequently, BF_reverse is a deterministic re-encoding of the panel's original answer, its mirror-item answer, and the frozen paired gold: conditional on an agent being correct on the original item, BF_reverse is *identically* the agent's correctness on the mirror item; on wrong items it is the complement. In plain terms, on the reversal axis we are measuring whether the panel's mirror-item answer aligns with the flip of its original answer. That is a real, pre-outcome-computable behavioral regularity, but it is not an independent probe of a latent "responsiveness" trait, and it is not causal: the data cannot separate "non-responsive to counter-evidence" from "the mirror gold aligns with the wrong answer". We report the behavior and its predictive ranking; we do not claim a mechanism.

### 1.3 Why pre-outcome ranking matters

A label-free score computed before outcomes are known has a concrete use: selective routing and abstention. Downstream systems can flag high-risk consensus items for human review, additional evidence collection, or abstention, without waiting for a gold label. Cost matters for such routing: the 10-call reversal-plus-paraphrase score is numerically identical to RS_q (paired Δ = 0.000 [0.000, 0.000] on both models), so the full ranking requires no more than the panel's own original and mirror-condition calls. The outcome firewall of the frozen protocol (labels merged only after feature freezing) is exactly the setting in which such a score would be deployed.

### 1.4 Contributions

- **A pre-outcome, label-free risk score.** We define counter-evidence responsiveness operationally (BF_reverse as the fraction of agent calls that change answer to the flip of the original answer under natural evidence swap), combine it with paraphrase stability into the frozen composite RS_q = −BF_q, and show it ranks consensus errors with AUROC 0.943 [0.924, 0.960] and Risk@80 0.846 [0.638, 0.981] (Qwen3.5-4B, 567 HC items) and AUROC 0.896 [0.873, 0.916] and Risk@80 0.422 [0.274, 0.591] (Ling-3.0-tiny, 574 HC items), with paired AUROC differences over agreement- and confidence-based baselines whose CIs exclude zero.
- **Bounded cross-model and cross-size evidence.** A frozen procedure transfer (Qwen item-level RS_q applied to Ling errors) reaches AUROC 0.723 [0.682, 0.765] — above chance but significantly below Ling's own 0.896, so item-level ranking is partly model-specific. A single-point, 100-item GPT-class validation reaches AUROC 0.969 [0.935, 0.995] (within-model HC n=96, wrong n=8). Per-label consistency holds for Qwen (SUPPORTS 0.917 / REFUTES 0.986).
- **Specificity to natural counter-evidence.** The signal reverses direction on a negation-prefix control (BoolQ AUROC 0.449), showing it tracks natural counter-evidence rather than arbitrary perturbation; a FEVER replication was blocked at construction because no natural pairs exist in the data, and we report this boundary rather than a proxy result.
- **Controls and reducibility.** Paraphrase placebo flip rates are low (0.038 Qwen / 0.061 Ling), so reverse-axis asymmetry is not general prompt instability; permutation controls are passed (0.943 > 95th pct 0.596; 0.896 > 0.564); and RS_q is not a re-expression of agreement (Spearman −0.004) or confidence (−0.161) on Qwen.
- **An honest measurement-level interpretation.** We state the mirror-equivalence reduction explicitly: BF_reverse is a label-aligned re-encoding of the panel's original and mirror answers with the frozen paired gold; on correct consensus it coincides with mirror-item accuracy and on wrong consensus it is its complement. The contribution is a descriptive, pre-outcome behavioral regularity and its ranking performance — with no causal, trait, or framework claim.

### 1.5 Scope and claims

This paper does **not** claim: (i) a "consensus stress testing framework" with causal stress curves or breakpoints as mechanism evidence; (ii) "expected-response faithfulness" as a latent trait; (iii) "evidence insensitivity" or rigidity as an explanation of *why* a consensus is wrong; (iv) causal identification — that counter-evidence causes error, or that responsiveness causes correctness; (v) universal transfer, zero-shot generalization, or superiority over every reliability baseline; (vi) results on arbitrary perturbations or on datasets beyond the frozen VitaminC natural-pair protocol; or (vii) any result for FEVER or other blocked datasets. The empirical basis is two small open models (Qwen3.5-4B, Ling-3.0-tiny) plus one GPT-class single point, on one dataset, with one specificity negative. Anticipating reviewers: yes, at its core this is a flip/stay measurement — on this protocol, precisely a label-aligned re-encoding of mirror-item behavior — and we treat that as the finding, not something to explain away; yes, there is only one dataset, and we surface the FEVER construction block instead of papering over it; yes, the models are small, and we label the GPT-class result a preliminary single point rather than a generalization claim.

---

## Writing notes (5 lines)

1. Adopted the frozen honest positioning verbatim: counter-evidence responsiveness as a pre-outcome, evidence-level signal; dropped "framework / latent trait / evidence insensitivity / causal" wording throughout.
2. Used prompt-authoritative CIs for all headline numbers (Qwen Risk@80 [0.638, 0.981], Ling AUROC [0.873, 0.916]); verified gpt-6-astra and 10-call identity numbers against round6/large_model and round6/cost_curve before citing.
3. Stated the mirror-equivalence caveat once, prominently (abstract + §1.2), and preempted "is this just flip-rate?" by embracing the reduction as the finding.
4. Bounded generality explicitly: two small models + one GPT-class single point, one dataset; BoolQ as specificity negative, FEVER as construction block; no universal/zero-shot/mechanism claims.
5. No invented citations (external refs marked [CITE]); text-only, no figures; all non-headline numbers (placebo, permutation, reducibility, baselines) trace to the read round3/round4/leaderboard files.
