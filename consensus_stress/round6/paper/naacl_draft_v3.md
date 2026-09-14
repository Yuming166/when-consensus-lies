# When Consensus Lies: Counter-Evidence Responsiveness as a Pre-Outcome Signal of Consensus Error

**Target venue:** NAACL (main). **Status:** integrated draft v3, generated 2026-09-14.
**Figures:** not yet included (pending). **Citations:** external references are marked `[CITE]`
and must be completed before submission; every experimental number carries a 95% CI and traces
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

---

## 2 Related Work

We position counter-evidence responsiveness against four clusters of prior work: (a) sampling-consistency and hallucination detection, (b) selective prediction and error prediction, (c) faithfulness and counterfactual evaluation of model behavior, and (d) multi-agent reliability, metamorphic testing, and consensus. Citations follow a dated literature audit (2026-09-12; `phase1/novelty_map.md`) that combines live arXiv/Crossref retrieval with model knowledge; entries whose bibliographic details were not live-verified are marked [CITE], and we do not claim exhaustiveness.

### 2.1 Sampling Consistency and Hallucination Detection

Self-consistency (Wang et al., 2022; arXiv:2203.11171) samples multiple reasoning paths for the same input and takes a majority vote, showing that agreement across samples is both a performance booster and a usable reliability signal. SelfCheckGPT (Manakul et al., 2023; arXiv:2303.08896) [CITE] performs zero-resource, black-box hallucination detection by checking whether independently sampled answers are consistent with the original response, without an external fact base. Semantic entropy (Farquhar et al., 2024) [CITE] clusters sampled answers by meaning and uses the entropy over semantic clusters as an uncertainty estimate. Calibrated Language Models Must Hallucinate (Kadavath et al., 2023; arXiv:2311.14648) [CITE] similarly shows that a model's agreement with itself across samples predicts whether its answer is correct. The shared thread is that the signal is derived from repeated samples of the *same* input; the evidence never changes, and the unit of analysis is a single model's sampling distribution. None of these methods evaluates how an already-formed multi-agent panel changes its answer when its evidence packet is swapped to the natural counter-evidence. In our benchmark, matched-budget adaptations of this family serve as external baselines (Sections 3.1 and 3.5).

### 2.2 Selective Prediction and Error Prediction

Selective prediction (El-Yaniv and Wiener, 2019; arXiv:1902.00080) lets a model abstain and trades coverage for error rate; risk-coverage curves and their area (AURC) are the standard evaluation. Conformal prediction sets provide coverage guarantees for set-valued predictions (Sadinle et al., 2019; arXiv:1906.00073). Error prediction has also been approached from training dynamics (arXiv:2205.13551) [CITE] and, most commonly, from calibrated confidence (e.g., temperature scaling or isotonic calibration to error probability). These methods operate on a single model's own output statistics for a single prediction on the same input: none introduces a controlled evidence intervention, and none targets a consensus formed by multiple agents. In our evaluation, the only label-using comparators in this family are calibrated strictly out-of-fold.

### 2.3 Faithfulness and Counterfactual Evaluation of Model Behavior

ERASER (DeYoung et al., 2020) evaluates whether extracted rationales are faithful via sufficiency and comprehensiveness: removing the rationale must change the model's score, for a single model. Counterfactual tests of attribution methods (arXiv:2408.11252) ask whether attribution tracks model behavior under counterfactual inputs. Measuring Faithfulness in Chain-of-Thought Reasoning (Lanham et al., 2023) perturbs reasoning steps and measures answer changes. Precision Is Not Faithfulness (arXiv:2606.09376) measures coverage-aware faithfulness of grounded generation claims against gold evidence. Citation-faithfulness detection extends the same idea to citations (CiteCheck, arXiv:2502.11054; agentic scientific synthesis, arXiv:2607.08328). These works establish controlled perturbation as a valid way to probe model behavior, and our expected-response oracle is methodologically indebted to them; but the object is a single model's explanation, rationale, reasoning trace, or citation rather than the answer of a multi-agent consensus, the purpose is descriptive faithfulness measurement rather than pre-outcome error ranking, and many variants require gold rationales or labels.

### 2.4 Multi-Agent Reliability, Metamorphic Testing, and Consensus

METAL (arXiv:2312.06056) applies metamorphic relations to LLM qualities: transform an input and check the expected output property without gold labels. This is the closest methodological ancestor of our oracle, but it is invariance-oriented and applied to single-model quality attributes, not to consensus error prediction. CheckList (Ribeiro et al., 2020) operationalizes behavioral testing of NLP models with invariance, directional-expectation, and minimum-functionality tests; it is the closest conceptual ancestor of an "expected response", but again for single-model capabilities rather than pre-outcome consensus risk. NLI stress testing (Naik et al., 2018) applies controlled sentence perturbations with labels present. REST (arXiv:2507.10541) stress-tests reasoning models by packing multiple problems into one prompt, varying task load rather than evidence. Evidence-State Reliability Under Controlled Degradation (arXiv:2608.21559) degrades evidence in multi-stage LLM pipelines and evaluates pipeline evidence-state reliability; the unit is the pipeline evidence state rather than the appropriateness of a consensus's response, and it defines no expected-response oracle and predicts no errors. Multi-agent debate work asks whether deliberation among agents improves answers or is worth its cost ("Talk Isn't Always Cheap", arXiv:2509.05396 [CITE]; Demystifying Multi-Agent Debate [CITE]); debate is a procedure for *forming* an answer, whereas our intervention is a probe applied to an *already-formed* consensus.

### 2.5 Positioning

We propose counter-evidence responsiveness as a pre-outcome, evidence-level signal: an already-formed multi-agent consensus is at elevated error risk when the panel does not change its answer after its evidence packet is swapped to the natural counter-evidence. Within our dated 2026-09-12 audit, we found no live hit, and no dated prior work, for the joint combination of (i) an already-formed multi-agent consensus as the object, (ii) a natural counter-evidence swap with a label-free, decision-relevance-aware expected-response oracle as the probe, and (iii) pre-outcome error prediction as the use; we state this as an audit result, not an exhaustiveness claim. The contribution is deliberately bounded: a behavioral signal plus a reproducible benchmark (CST-Bench), not a "stress-testing framework", not a latent "faithfulness trait", and not a causal account of why consensus errors occur.

## 3 Method

### 3.1 Task and Estimand

Each item presents a claim $C$ and an evidence packet; five agents independently answer a binary verification question ("Does the provided evidence support the claim?", yes = SUPPORTS, no = REFUTES). Data come from the official VitaminC test set, restricted to *natural pairs*: two rows sharing the same `case_id`, claim, and page/revision, with exactly one SUPPORTS and one REFUTES label. Selection is frozen and deterministic (protocol `cs-paper-vitaminc-2026-09-13`, preregistered before any model call): one pair per page (highest character ratio, then token Jaccard); contrast gates character_ratio $\geq 0.85$ and token Jaccard $\geq 0.70$; no U+FFFD characters; claim length 5-40 tokens and evidence length 10-120 tokens; ordering by sha256(SALT + page); page- and pair-disjoint from earlier pilots. This yields 300 pairs = 600 items that are label-symmetric by construction (300 SUPPORTS + 300 REFUTES). Each pair produces two composite items sharing the claim: the S-item (gold SUPPORTS; own evidence = supports evidence, natural counter-evidence = refutes evidence) and the R-item (gold REFUTES; symmetric). A deterministic, non-decision-relevant distractor is shared by both items.

The formed consensus is the majority answer of the five original-condition agents; high consensus (HC) is agreement $\geq 0.8$ (at least 4 of 5 agents share the majority). The estimand is $\mathrm{consensus\_wrong} = \mathbb{1}[\text{majority answer} \neq \text{sealed gold}]$ on the HC subset, and the task is *pre-outcome risk ranking*: rank HC items by predicted risk before labels are merged. We report AUROC of the risk score against $\mathrm{consensus\_wrong}$ on HC with pair-grouped bootstrap 95% CIs (2,000 replicates), and Risk@80, the error-rate reduction when the lowest-risk 80% of HC items are retained, with the same uncertainty treatment. Comparator risk scores (mean confidence, disagreement, frozen prior scores, and matched-budget adaptations of the sampling-consistency family) are evaluated on the same HC subset under the benchmark's matched-call accounting; the only label-using comparators are calibrated strictly out-of-fold. All directions and gates were frozen before any model call; no post-hoc sign flip or metric repair is permitted.

### 3.2 Panel and Environment

Five frozen personas (`AGENT_PERSONAS`), each with a frozen 2-of-3 partition table (`PARTITION_TABLE`), form the panel: every agent sees a fixed two of the three packet units in each condition, and every view of every non-remove condition contains at least one decision-relevant unit. Calls use temperature 0 with deterministic per-(agent, condition) seeds, `max_tokens=160`, prompt-only JSON (no `response_format`, no `reasoning_effort`), up to two retries with a frozen repair suffix, and content-addressed caching. The primary model is local Qwen3.5-4B; Ling-3.0-tiny is a preregistered secondary model on the identical protocol.

Evidence identities. Each item has an own evidence $E$, two meaning-preserving paraphrases $\mathrm{para}_1(E), \mathrm{para}_2(E)$, the paired natural counter-evidence $E_{\mathrm{opp}}$ (the mirror item's evidence), and a shared distractor $D$ with token Jaccard $\leq 0.05$ against the claim. The five frozen conditions are: original $[E, \mathrm{para}_1(E), D]$; paraphrase $[\mathrm{para}_1(E), \mathrm{para}_2(E), \mathrm{para}(D)]$; natural reverse $[E_{\mathrm{opp}}, \mathrm{para}_1(E_{\mathrm{opp}}), D]$; synthetic reverse (negated units; secondary only); and remove (empty packet).

Expected-response oracle (label-free, frozen offline, decision-relevance-aware). Relevance rules: own evidence (R1), its paraphrases (R2), and the paired counter-evidence (R3) are decision-relevant; a negated unit is relevant iff its base is (R4); the distractor is not decision-relevant (R5); an empty packet yields no forced response (R6). The expected response under transformation $T$ is defined from transformation semantics alone: paraphrase $\Rightarrow$ keep ($Y^* = Y_0$, the agent's own original-condition answer), natural reverse $\Rightarrow$ flip ($Y^* = \mathrm{flip}(Y_0)$), remove $\Rightarrow$ no forced response (descriptive only). An agent call is scored iff its view contains at least one decision-relevant unit with a defined expected response; under the frozen 2-of-3 partition, all non-remove views are scored. Per-agent, per-condition faithfulness is $f_{\mathrm{cond}}(i,a) = \mathbb{1}[Y(i,\mathrm{cond},a) = Y^*(\mathrm{cond})]$. Offline audits (decision relevance, $\geq 24/30$; paraphrase meaning preservation, $\geq 80\%$) precede any agent call, with frozen fallback triggers.

Cross-model contract adaptation (preregistered before any Ling call; protocol `cs-paper-ling-adapted-20260913-round4`). On the same 600 items with identical evidence, oracle, conditions, formula, direction, and gates, one transport detail differs: the JSON contract no longer requests or validates a model-reported `agent_id`; instead, the task dispatcher binds agent identity server-side to the frozen `agent_index`, persona, and partition, and the record stores both. This is a provenance change only: it was registered before outcomes were observed, it is applied uniformly, and it does not enter the oracle, $BF_q$, $RS_q$, consensus, agreement, or any gate.

### 3.3 Risk Score: $RS_q = -BF_q$

The frozen composite score is

$$BF_q = \frac{1}{5}\sum_{a=1}^{5} \frac{f_{\mathrm{para}}(i,a) + f_{\mathrm{rev}}(i,a)}{2},$$

the mean over the five agents of per-agent faithfulness averaged over the paraphrase and natural-reverse conditions, and

$$RS_q = -BF_q,$$

so that lower expected-response fidelity under natural counter-evidence (higher $RS_q$) predicts higher risk that the formed consensus is wrong. Synthetic reverse is reported per-condition only and never enters $BF_q$ (frozen). The direction "higher $RS_q$ = riskier" was fixed before any model call, after a round-2 sign-consistency correction, and is not post-hoc.

### 3.4 Mirror-Equivalence Caveat

We state the central interpretive caveat once. Because the natural-reverse view of item $i$ is byte-identical to the original view of the mirror item $j$ (same claim, persona, partition, evidence texts, distractor, and seed), temperature-0 inference gives the View Identity $Y(i,\mathrm{reverse},a) = Y(j,\mathrm{original},a)$, empirically verified on 99.97% (Qwen) and 99.63% (Ling) of calls, with residual mismatches attributable to parse-repair paths. Consequently, $BF_{\mathrm{reverse}}$ is a deterministic re-encoding of three ordinary quantities -- the panel's original answers, its mirror-item answers, and the frozen paired gold labels -- rather than a measurement of a latent trait. At the single-call level, an originally correct agent is counted faithful exactly when it answers the mirror item correctly, while an originally wrong agent is counted faithful exactly when it answers the mirror item incorrectly ($f_{\mathrm{rev}} = m_j(a)$ if correct, $1 - m_j(a)$ if wrong). At the consensus level on HC (agreement $\geq 0.8$), on a correct consensus $BF_{\mathrm{reverse}}$ coincides with mirror-item accuracy (the majority, weight $\geq 0.8$, is originally correct), while on a wrong consensus it coincides with its complement, $1 - \text{mirror accuracy}$ (the majority, weight $\geq 0.8$, is originally wrong). Empirically this is the collapse from 0.844 (correct, Qwen) / 0.703 (correct, Ling) to 0.095 (wrong, Qwen) / 0.029 (wrong, Ling). We therefore describe the reverse axis strictly as counter-evidence responsiveness -- a descriptive, pre-outcome-computable behavioral regularity on this protocol -- and make no causal claim that counter-evidence causes consensus error, that responsiveness causes correctness, or that the score measures a latent "faithfulness" or "rigidity" trait. The paraphrase axis is not subject to this reduction (it is the same item under meaning-preserving rewording, $Y^* = Y_0$) and measures stability under paraphrase independently of label alignment.

### 3.5 Cost Variants

The full protocol consumes 25 calls per item (5 agents x 5 conditions); $RS_q$ is defined on those 25 calls. Two reduced-cost variants are computed from the same frozen records (zero new calls; protocol `cs-round6-cost-curve-20260914`), always on top of the already-formed 5-agent consensus, whose original answers define the flip expectation:

- Reversal-only with $K$ calls, $K \in \{1,2,5\}$: $\mathrm{risk} = 1 - \frac{1}{K}\sum_{a < K} f_{\mathrm{rev}}(i,a)$; marginal cost $K$ calls/item (total $K+5$). Reversal-only(5) reaches AUROC 0.931 (Qwen) and 0.869 (Ling) on HC, but it is statistically below $RS_q$ on paired AUROC (Qwen $\Delta = +0.012$ [0.002, 0.023]; Ling $\Delta = +0.027$ [0.013, 0.042]); we therefore do not claim a "5 calls $\approx$ 25 calls" equivalence.
- Reversal + paraphrase with $2K$ calls, $K \in \{1,2,5\}$: $\mathrm{risk} = 1 - \frac{1}{K}\sum_{a < K}\frac{f_{\mathrm{para}}(i,a) + f_{\mathrm{rev}}(i,a)}{2}$; marginal cost $2K$ calls/item (total $2K+5$). $K = 5$ is exactly the frozen $BF_q$ score function, using the 10 scored calls.

Empirically, the 10-call point is lossless: reversal+paraphrase(10) has pair-grouped differences $\Delta = 0.000$ [0.000, 0.000] versus $RS_q$ on both AUROC and Risk@80 for both models, because $RS_q = -BF_q$ depends only on the 10 scored paraphrase+reverse calls; the other 15 calls (original, synthetic reverse, remove) do not enter the score. The supported low-cost point is therefore 10 scored calls/item (plus the 5 original consensus calls), not fewer: the 5-call reversal-only probe loses statistically significant AUROC on both models, and adding synthetic-reverse calls (the 10-call reversal family) dilutes the signal rather than improving it. Token accounting from the frozen records reflects the same ordering (Qwen mean total tokens/item: 2,154 for reversal-only(5) vs. 10,196 for $RS_q$; Ling: 2,176 vs. 10,354).

### 3.6 Outcome Firewall and Controls

Outcome firewall. Gold labels are merged only after all pre-outcome features are frozen; before merging, forbidden inputs to any score are the gold label, the gold binary, per-agent correctness, and $\mathrm{consensus\_wrong}$. Dataset labels are used offline only to construct the balanced design and artifact texts; they are never sent to agents and never used in probing or scoring. Both protocols were registered before their model calls, and all gates, directions, and fallbacks were fixed in those registrations.

Placebo control. The paraphrase axis is the same item under meaning-preserving rewording, so it acts as a stability placebo: agent-level paraphrase flip rates of 0.038 (Qwen) and 0.061 (Ling) are far below the preregistered 0.30 threshold, indicating that the reverse-axis asymmetry is not explained by general prompt instability.

Permutation control. The observed primary AUROC exceeds the 95th percentile of 1,000 per-item preserve/flip-swap permutations that randomize the sign of each $BF$ component per item (Qwen 0.943 > 0.596; Ling 0.896 > 0.564); the directional association between low responsiveness and error is not reproduced when component signs are scrambled.

Reducibility control. $RS_q$ is not a re-expression of agreement or confidence: $|\mathrm{Spearman}(RS_q, \mathrm{agreement})| < 0.9$ and $|\mathrm{Spearman}(RS_q, \mathrm{mean\_confidence})| < 0.9$ (Qwen $-0.004$ / $-0.161$; Ling $-0.148$ / $-0.050$), and AUROC on the agreement $= 0.8$ stratum is 0.844 (Qwen), above chance. This reducibility check is separate from the mirror reduction in Section 3.4, which concerns $BF_{\mathrm{reverse}}$ versus mirror-item accuracy.

Frozen gates. The preregistered within-model gate requires, jointly: pipeline validity $\geq 0.95$; primary AUROC CI lower bound $> 0.5$ with point estimate $\geq 0.60$; macro-label and worst-label AUROC CI lower bounds $> 0.5$; the placebo threshold above; the permutation gate above; the reducibility thresholds above; and, for the formal Risk@80 phase, a paired Risk@80 CI excluding zero in the favorable direction. No gate is re-run or retuned after outcomes; a failing gate is reported as a failure.

---

## 4 Experiments and Results

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

---

# Section 5 — Discussion

## 5.1 What the regularity is (and is not)

The central empirical finding of this paper is a behavioral regularity that is computable
before any outcome is observed. On the frozen VitaminC natural-pair protocol, a multi-agent
panel that has already reached high consensus (agreement >= 0.8) tends to change its answer
when its evidence packet is swapped to the natural counter-evidence — the evidence of the
paired mirror item — if the consensus is correct, and tends not to change it if the consensus
is wrong. Reverse-axis responsiveness (BF_reverse) separates these two populations sharply:
0.844 (Qwen3.5-4B, derived) and 0.703 (Ling-3.0-tiny, reported) on correct consensus versus
0.095 and 0.029 on wrong consensus; on wrong-consensus items, 90.5% (Qwen) and 97.1% (Ling)
of agent calls stay with the wrong answer when presented with the natural counter-evidence.

We are deliberately precise about what this regularity is *not*. The mirror-equivalence
analysis (R1) shows that BF_reverse is a deterministic, label-aligned re-encoding of three
ordinary quantities: the agent's answer on the original item, the agent's answer on the
mirror item, and the frozen paired gold. Conditional on an agent being correct on the
original item, BF_reverse is *identical* to the agent's accuracy on the mirror item; on
wrong consensus the two quantities are complements. The 0.703-to-0.029 collapse is therefore
produced by the alignment of the mirror gold with the panel's (wrong) answer — staying is
simultaneously "still wrong" and "mirror-correct" — not by a separately measurable
"rigidity" or "evidence insensitivity" trait. We do not claim such a trait, and we have
dropped the earlier "expected-response faithfulness" framing in favor of the operational
term *counter-evidence responsiveness*. What remains is still nontrivial and still
pre-outcome: the *directional association* between low responsiveness to natural
counter-evidence and consensus error, which ranks errors with AUROC 0.943 [0.924, 0.960]
(Qwen) and 0.896 [0.873, 0.916] (Ling) for RS_q = -BF_q, with Risk@80 reductions of 0.846
[0.638, 0.981] and 0.422 [0.274, 0.591]. The ranking facts are unchanged by the reframing;
only the interpretation is narrowed.

The regularity also has a measurable second axis: paraphrase stability. The paraphrase
condition is not subject to the mirror reduction, because it tests the same item under
meaning-preserving rewording against the agent's own original answer, not a mirror prompt.
Paraphrase flip rates are low (0.038 Qwen; 0.061 Ling) — the reverse-axis asymmetry is not
explained by general prompt instability — and paraphrase faithfulness contributes a small but
statistically significant increment over the reverse axis alone (residual-increment AUROC
0.921 [0.901, 0.941] Qwen; 0.855 [0.828, 0.880] Ling; paired AUROC increments of the full
RS_q over the reverse axis 0.012 [0.002, 0.022] and 0.027 [0.013, 0.042]).

## 5.2 What transfers, and what does not

Two things transfer across model families. First, the *procedure*: the frozen Qwen item-level
RS_q, applied directly to Ling's own errors, achieves AUROC 0.723 [0.682, 0.765] — above
chance by CI, though below Ling's own within-model score (0.896; paired difference -0.173
[-0.217, -0.130]). Second, the *aggregate signal*: the same within-model gate structure
(permutation, placebo, mechanism-fidelity, primary AUROC) passes for Qwen3.5-4B and
Ling-3.0-tiny on the full 600-item cohort and, as a single point, for a GPT-class relay model
(gpt-6-astra) on a 100-item subset (HC n=96, 8 wrong; within-model AUROC 0.969 [0.935, 0.995];
frozen Qwen and Ling RS_q transfer to its errors with AUROC 0.838 [0.693, 0.950] and 0.737
[0.568, 0.862]).

What does *not* transfer is item-level ranking. Item-level Spearman correlation between Qwen
and Ling RS_q is only 0.496 on 574 shared HC items, and the correlations between each frozen
score and the gpt-6-astra score are 0.68 (Qwen) and 0.37 (Ling). We therefore claim
procedure-level and aggregate-signal transfer, never per-item ordering equivalence across
models. A risk score learned on one model family should be recalibrated or re-validated
per family; the benchmark's value is in making that validation cheap and standardized.

## 5.3 Why specificity to natural counter-evidence matters

The BoolQ result is an honest negative that we treat as evidence *for* the "natural
counter-evidence" interpretation. BoolQ's reverse axis is a negation-prefix reversal rather
than a natural evidence swap, and on BoolQ the signal reverses direction: AUROC 0.449
[0.308, 0.579], with permutation control failing (0.449 < 0.612) and the round-1 answer-prior
confound reappearing in risk orientation. The contrast is informative: a perturbation axis
that is not a genuine evidence-level contradiction does not produce the regularity. This
supports reading the effect as responsiveness to *meaning-level counter-evidence* rather
than to arbitrary input perturbation, and it bounds the mechanism to datasets that actually
supply such pairs (e.g., VitaminC's SUPPORTS/REFUTES mirror items), with no claim of
transfer to synthetic perturbations or other datasets.

## 5.4 Deployment angle

The pre-outcome nature of RS_q makes it directly usable for selective routing or abstention:
a panel whose consensus is reached but whose risk score is high can be routed to additional
verification, an adjudicator, or abstention before the answer is released. Two cost facts
constrain that deployment claim. First, the full RS_q is 25 calls/item (5 agents x 5
conditions). Second, a cheaper 5-call probe (natural-reverse condition only, on top of the
already-formed consensus; 10 calls/item in total including the 5 original consensus calls)
reaches AUROC 0.931 [0.913, 0.948] (Qwen) and 0.869 [0.847, 0.891] (Ling), but is
statistically significantly worse than the full RS_q in paired AUROC difference (Qwen +0.012
[0.002, 0.023]; Ling +0.027 [0.013, 0.042]). Per our pre-registered decision rule, we do
*not* claim "5 calls ~= 25 calls." The statistically lossless cheap point is 10 calls/item
(reversal + paraphrase, 15 calls/item total), whose item-level scores are identical to RS_q
(paired difference 0.000 [0.000, 0.000]). Token accounting from frozen records makes the
trade-off concrete: mean total tokens/item are 10,196 (Qwen) and 10,354 (Ling) for the full
RS_q versus 2,154 and 2,176 for the 5-call reversal probe — roughly a fifth of the tokens at
a small, significant AUROC cost. Adding a synthetic-reverse condition instead (10-call
reversal family) *dilutes* the signal (Qwen 0.832; Ling 0.753), reinforcing that the
natural-reverse axis is the core carrier and that more calls are not monotonically better.

# Section 6 — Limitations

We state our limitations explicitly and concretely. Failure and blocked records from the
project history are preserved in the repository and not relabeled; the boundaries below
are the ones we ask reviewers to weigh against the positive results.

1. **Mirror-equivalence restricts the mechanism claim to a descriptive regularity.**
   BF_reverse is a label-aligned re-encoding of the original answer, the mirror-item answer,
   and the frozen paired gold; it is not an independent probe of a latent rigidity trait.
   The View Identity holds empirically on 99.97% (Qwen) and 99.63% (Ling) of agent calls,
   with the residual attributable to parse-repair paths. Consequently, our claim is
   *descriptive* (wrong consensus panels do not change their answer under natural
   counter-evidence) and *predictive* (this pre-outcome behavior ranks errors), not
   mechanistic. The paraphrase axis is the only component not subject to this reduction, and
   it alone discriminates only weakly (per-axis AUROC 0.599/0.581).

2. **A single positive dataset, plus a single GPT-class point.** The positive evidence is
   one dataset (VitaminC natural pairs, 600 items, label-symmetric by construction). The
   large-model evidence is a single point: 100 items (98 with complete features; HC n=96,
   8 wrong consensus items), run through a *third-party relay* (openapi.center) for a
   GPT-class model (gpt-6-astra), with 2,483/2,500 valid calls (0 parse failures; 17
   transport failures). The within-model AUROC 0.969 [0.935, 0.995] and the transfer AUROCs
   (0.838/0.737) rest on only 8 wrong items, so the CIs are wide and the point is
   indicative, not a full-cohort estimate. We do not claim cross-dataset generality or a
   frontier-model full-cohort result.

3. **Small, open-weight research models for the full-cohort results.** The two full-cohort
   runs use Qwen3.5-4B and Ling-3.0-tiny. We have no full-cohort result on a frontier
   closed-weight model, and we do not assume the aggregate signal or the item-level ranking
   behavior holds at frontier scale. The gpt-6-astra single point is a bounded validation of
   procedure transfer only.

4. **Label asymmetry: construction is symmetric, error rates are not.** The benchmark is
   label-symmetric (300 SUPPORTS + 300 REFUTES items, shared evidence views and prompt
   templates), but model error rates are strongly asymmetric: Qwen errors on 7/283 SUPPORTS
   HC items (2.5% [1.2%, 5.0%]) versus 58/284 REFUTES items (20.4% [16.1%, 25.5%]); Ling
   13/296 (4.4% [2.6%, 7.4%]) versus 106/278 (38.1% [32.6%, 44.0%]). About 89% of pooled
   errors are REFUTES, and about 89% of the pooled AUROC concordant mass is carried by
   REFUTES-wrong items; the pooled AUROC (0.943/0.896) is therefore a REFUTES-dominated
   composite. We bound this with per-label AUROCs (both labels significantly above chance in
   both models; SUPPORTS 0.917 [0.819, 0.999] Qwen and 0.881 [0.834, 0.928] Ling) and a
   post-hoc error-count-matched pooling that keeps pooled AUROC near 0.92/0.875, and we do
   not claim SUPPORTS is *significantly* harder than REFUTES where the difference CI includes
   zero (Qwen). But the pooled metric should be read as REFUTES-carried, and label-stratified
   numbers are the primary view.

5. **Ling contract adaptation (preregistered).** Ling-3.0-tiny did not self-report
   `agent_id`; the dispatcher binds the frozen agent index/persona/partition server-side,
   and the parser validates answer, confidence, and cited evidence IDs with a frozen JSON
   exemplar in every prompt (previous transport attempts failed on placeholder IDs and were
   recorded as failures). This adaptation was preregistered before the Ling run, changes no
   evidence, oracle, condition, or score field, and the run achieved 15,000/15,000 valid
   calls. It is nonetheless a response-format accommodation whose effect cannot be fully
   separated from model behavior.

6. **Cost/benefit is real but small.** The 5-call probe is cheaper (about one fifth of the
   tokens) but statistically significantly worse than the full 25-call RS_q in paired AUROC
   (Qwen +0.012 [0.002, 0.023]; Ling +0.027 [0.013, 0.042]); the gap is small in magnitude.
   The 10-call score is lossless by construction (identical item-level scores), so the
   honest cost story is "10 calls are lossless; 5 calls are cheaper but slightly weaker," not
   "5 calls are equivalent."

7. **No causal identification.** We do not establish that counter-evidence *causes* the
   error, nor that responsiveness *causes* correctness. The evidence is correlational,
   pre-outcome, and specific to the frozen protocol; we explicitly refrain from causal
   wording throughout.

8. **External baselines are adapted proxies under matched budget, not original-implementation
   reruns.** Self-consistency, SelfCheckGPT, and binary semantic entropy are implemented as
   binary answer-match variants (mode frequency, answer-match probability, yes/no cluster
   entropy) without the original pipelines (e.g., no NLI/self-verification for SelfCheckGPT,
   no bidirectional entailment clustering for semantic entropy); calibrated confidence is a
   pair-grouped 5-fold out-of-fold isotonic/temperature calibration; all external rows are
   scored at a matched 25 calls/item budget. These are fair *budget-matched proxies*, not
   reproductions of the cited papers' numbers, and the leaderboard marks them as such.

9. **No multiplicity correction on the leaderboard.** We compare RS_q against multiple
   baselines and report pair-grouped bootstrap CIs as the primary inference; we do not apply
   a formal family-wise correction across the leaderboard. The main claims hold at the
   individual CI level, but a formal correction is appropriate future work.

In addition, we preserve prior failures rather than repairing them away: a BoolQ
worst-label polarity reversal (native-`no` AUROC 0.120; verdict
`PASS_CROSS_FAMILY_AGGREGATE_ONLY`), the failed S&P500 LLM replay routing endpoint (twice),
Synthetic V4 learned-router drift, and the Ling V3.15 JSON-contract failures are all on
record and inform the boundaries above.

# Section 7 — Conclusion

We proposed counter-evidence responsiveness as a pre-outcome error signal for multi-agent
consensus: on the frozen VitaminC natural-pair protocol, a high-consensus panel that does
not change its answer when its evidence is swapped to the natural counter-evidence is at
elevated risk of being wrong. The combined risk score RS_q = -BF_q ranks consensus errors
before labels are merged with AUROC 0.943 [0.924, 0.960] (Qwen3.5-4B) and 0.896 [0.873,
0.916] (Ling-3.0-tiny), and the procedure and aggregate signal transfer across model
families and, as a single point, to a GPT-class relay model, while item-level ranking does
not. The mirror-equivalence analysis bounds the claim: the reverse axis is a label-aligned
re-encoding of ordinary answers, so the contribution is a descriptive, pre-outcome
regularity plus a benchmark (CST-Bench) and a frozen, reproducible evaluation — not a latent
mechanism and not a new standalone heuristic. We report label-stratified results because the
pooled signal is REFUTES-carried, we keep the honest BoolQ negative as a specificity
boundary, and we do not claim causal identification, cross-dataset generality, or frontier
full-cohort validation. The practical takeaway is modest and operational: selective routing
or abstention on consensus answers can be driven by a cheap, outcome-blind responsiveness
probe, with 10 calls/item as the lossless point and 5 calls/item as a slightly weaker but
far cheaper alternative.

# Appendix A — Reviewer Q&A

## A.1 (R1) "Your BF_reverse is just mirror-item accuracy."

Yes — for the reverse axis. We accept this, and it is now formalized rather than defended.
At the single-call level, with the View Identity (the reverse view of item *i* is
byte-identical to the original view of the mirror item *j*), for an originally-correct agent
BF_reverse is *identically* the agent's mirror-item accuracy; for an originally-wrong agent
it is its complement. At the consensus level, on correct consensus BF_reverse approximately
equals mirror-item accuracy (majority weight >= 0.8); on wrong consensus it approximately
equals its complement. The numerical claim "BF_reverse == mirror-item accuracy" is therefore
exact for originally-correct agents and consensus-correct items, and inverted for the group
that dominates wrong consensus. This is why the earlier "expected-response faithfulness"
label was dropped.

What survives the reduction, and what we actually claim:

- **Pre-outcome ranking.** RS_q = -BF_q ranks consensus errors before labels are merged
  (AUROC 0.943 [0.924, 0.960] Qwen; 0.896 [0.873, 0.916] Ling), and the directional
  association is not reproduced under a per-item sign-permutation control (observed ranking
  exceeds the 95th percentile of 1000 permutations). Whether the score is "mirror-item
  accuracy re-encoded" does not change that it is computable before the outcome and ranks
  errors.
- **Paraphrase stability.** The paraphrase axis is *not* subject to the mirror reduction
  (same item, meaning-preserving rewording, expected = y0). Paraphrase flips are rare
  (0.038/0.061), and the axis adds a small but significant increment over the reverse axis.
- **Cost.** The signal is cheaply computable on top of an already-formed consensus (a 5-call
  natural-reverse probe reaches AUROC 0.931/0.869; the 10-call reversal+paraphrase score is
  identical to RS_q).

We therefore agree that the reverse axis adds no new *measurement* beyond two ordinary
answers and the frozen gold; the contribution is the pre-outcome use of that re-encoding for
selective prediction, its stability across models, and the benchmark that makes it
reproducible.

## A.2 (R2) "A single agent gets the same result, so consensus is unnecessary."

We do not dispute the headline comparison. The single-agent intervention (one persona, five
temperature-0.7 replicates across the same five conditions, 25 calls/item) reaches AUROC
0.925 [0.900, 0.948] on Qwen HC, and the paired AUROC difference against RS_q (0.943) is
0.018 with a 95% CI of [-0.001, 0.039] — the CI includes zero, so we cannot claim RS_q is
significantly better on this metric. We therefore make no "consensus is necessary for signal
strength" claim.

Three things qualify the conclusion a reviewer might draw:

- **It is not cheaper.** The single-agent intervention uses 25 calls/item — the same budget
  as RS_q (5 personas x 5 conditions, temperature 0). "A single agent suffices" here does
  not translate into fewer calls; it is a different allocation of the same budget.
- **Consensus is the deployment object, not the signal source.** The risk signal is defined
  relative to an already-formed panel answer: the oracle expectation is the *flip of the
  panel majority answer*, and the probe is run on top of a formed consensus. In the
  deployment scenario we argue for (selective routing / abstention of high-consensus
  answers), the consensus already exists; the question is whether to trust it. We do not
  claim the signal originates in the aggregation.
- **The consensus object also changes what the regularity means.** On the frozen protocol,
  the regularity is about whether a *panel* changes its answer under natural counter-evidence;
  the mirror-equivalence analysis shows this is a property of panel answer / gold alignment
  on the mirror item. A single sampled agent's answer does not carry the same consensus-level
  semantics, and the item-level ranking is model- and instance-dependent rather than a stable
  cross-agent property we would claim.

In short: consensus is the unit we route on, and a single agent can score about as well
under a matched budget; we do not argue otherwise.

## A.3 (R3) "RS_q is just R_sym reweighted + a paraphrase axis."

Substantially overlapping — but not strictly reducible, and we no longer claim a new
standalone heuristic. The algebra is not "just reweighting": RS_q = -(bf_paraphrase +
rev_flip_rate)/2 shares only the natural-reverse flip axis with R_sym = 0.3*(1 -
rev_flip_rate) + 0.7*intervention_disagreement, and with different effective weights (-0.5
versus -0.3); the second axes differ entirely (paraphrase faithfulness versus intervention
disagreement). Empirically the two are strongly but not perfectly correlated: Spearman 0.822
[0.787, 0.845] (Qwen) and 0.859 [0.822, 0.886] (Ling). RS_q retains a significant but
moderate increment over R_sym: residual-increment AUROC 0.874 [0.784, 0.931] (Qwen) and 0.787
[0.743, 0.831] (Ling), with paired AUROC differences of +0.051 [0.028, 0.075] and +0.078
[0.053, 0.106]. Most of RS_q's signal is carried by the shared reverse axis (reverse-axis-only
AUROC 0.931/0.869 versus 0.943/0.896), and the increment comes from the paraphrase axis plus
the removal of intervention_disagreement (which alone is near chance, 0.536/0.475). We agree
with the spirit of the reduction and have positioned the main contribution accordingly: a
benchmark (CST-Bench) with a frozen, reproducible protocol; a clean aggregate signal on the
natural-reverse axis; and an honest, bounded increment from paraphrase stability — rather
than a claim that RS_q is a new mechanism or a fundamentally new heuristic.

### A.4 "Only one positive dataset?"

Yes, that is accurate. The positive evidence is VitaminC natural pairs (600 items,
label-symmetric), and BoolQ is an honest negative (direction reversed, AUROC 0.449). The
mechanism requires natural counter-evidence pairs — true, meaning-level opposing evidence for
the same claim — which is a property of datasets like VitaminC (SUPPORTS/REFUTES mirror
items) and not of arbitrary perturbation axes. We therefore deliberately bound the claim to
this benchmark and do not claim cross-dataset generality; the contribution is framed as the
benchmark plus the frozen evaluation and a bounded signal, not as a dataset-agnostic law.
Evaluating other natural-pair corpora (e.g., evidence-veracity datasets with genuine
contradicting evidence) is future work.

### A.5 "Why not zero-shot / a GPT-4 full cohort?"

Three honest reasons. (i) We make no zero-shot claim and the relay run is explicitly a
single-point validation, not a full-cohort estimate; the available GPT-class model at our
third-party relay was gpt-6-astra, whose identity we verify in every successful record —
we did not use GPT-4. (ii) Scale and reliability: the 100-item run required 2,500 logical
calls, 929 transport retries, and 17 transport failures over roughly 92 minutes and ~5.5M
prompt tokens; a full 600-item cohort through the same relay would be ~6x that (roughly
9-10 hours and ~33M prompt tokens) against observed 429/502/400 rate limits. (iii) Marginal
value: item-level ranking does not transfer across models (Spearman 0.496 Qwen-Ling;
0.68/0.37 to gpt-6-astra), so a frontier full cohort would primarily add a within-model
AUROC estimate for one relay model. A full frontier-model cohort under the same frozen
protocol is future work; we state the single-point boundary rather than extrapolate.

### A.6 "Are the baselines fair?"

Under a matched-budget reading, yes, with an explicit caveat. Every external baseline is
scored at a matched 25 calls/item budget, the same as RS_q, on the same frozen high-consensus
population, with pair-grouped CIs. However, the external rows are *adapted proxies*, not
original-implementation reruns: Self-consistency is implemented as 1 - mode frequency of 25
temperature-0.7 binary samples; SelfCheckGPT as answer-match probability without the original
NLI/self-verification pipeline; binary semantic entropy as normalized entropy over yes/no
clusters without bidirectional-entailment clustering; calibrated confidence as pair-grouped
5-fold out-of-fold isotonic/temperature calibration. We do not present these as reproductions
of the cited papers, and the leaderboard and README mark them as adapted proxies. The
internal baselines (R_sym, R_PI, vote agreement, frozen confidence) are exact frozen
formulas from this project. Fairness, in other words, is in the budget and the population —
not in the claim that we reran external authors' code.

# Claims We Explicitly Do Not Make

- No causal claim: we do not say that counter-evidence causes consensus error, or that
  responsiveness causes correctness. "Responsive / non-responsive" is descriptive of frozen
  protocol behavior.
- No latent-trait claim: BF_reverse is a label-aligned re-encoding of ordinary answers and
  the frozen gold, not a measurement of "rigidity," "evidence insensitivity," or any other
  latent faithfulness trait.
- No new-heuristic claim: RS_q is not a new standalone heuristic; it substantially overlaps
  R_sym on the natural-reverse axis and adds only a modest, significant increment via the
  paraphrase axis.
- No item-level transfer claim: per-item risk ranking is model-dependent (Spearman 0.496
  Qwen-Ling; 0.68/0.37 to the gpt single point); only procedure and aggregate-signal
  transfer are claimed.
- No frontier or zero-shot claim: no full-cohort result on a frontier closed-weight model;
  the gpt-6-astra result is a 100-item single point (8 wrong HC items, wide CIs, third-party
  relay) and does not support zero-shot or universal generalization.
- No cross-dataset generality claim: the positive evidence is one dataset (VitaminC natural
  pairs); BoolQ (AUROC 0.449, direction reversed) is an honest negative that bounds the
  mechanism to natural counter-evidence.
- No "5 calls ~= 25 calls" equivalence claim: the 5-call probe is statistically significantly
  worse in paired AUROC (small gap); the lossless cheap point is 10 calls/item.
- No label-symmetry claim about errors: construction is label-symmetric, error rates are not
  (SUPPORTS 2.5-4.4% versus REFUTES 20.4-38.1%); the pooled metric is REFUTES-carried and
  label-stratified numbers are primary.
- No reproduction claim for external baselines: Self-consistency, SelfCheckGPT, binary
  semantic entropy, and calibrated confidence are matched-budget adapted proxies, not
  original-implementation reruns.
- No post-hoc rescuing of frozen endpoints: all post-hoc analyses (matched-coverage,
  error-count-matched pooling, label-difference diagnostics) are labeled as such and do not
  alter frozen gate verdicts; failed records (S&P500 replay, Synthetic V4 drift, BoolQ
  label reversal, Ling V3.15 contract failures) remain on record.
- No downstream-superiority claim: no universal factuality, live-retrieval robustness,
  prospective trading performance, or alpha/predictability claim is established by any
  result reported here.
