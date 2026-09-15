# When Consensus Lies: Stress-Testing Multi-Agent Agreement with Counter-Evidence

**Target venue:** NAACL (main). **Status:** integrated draft v5 (round-7 integration, Agent W5,
2026-09-15) on top of v4 (gpt-6-astra revision, 2026-09-14). All frozen round-3/4/5/6 numbers and
95% CIs are unchanged from v4; every round-7 addition is labeled *post-hoc / exploratory* and is
traceable to `consensus_stress/round7/{audit,ind_ce,ind_ce_strict,stress_profile,lambda_features}/`
(provenance tags `[W1]`–`[W4]` point to the exact decision/result files; see the accompanying
`paper_delta_v4_to_v5.md` for the full traceability table). **Figures:** two round-7 diagnostic
figures are referenced (Section 8); final rendering pending. **Citations:** `[CITE]` placeholders
pending completion.

---

## Title candidates (round-7 decision aid, per NAACL plan §19)

1. **When Consensus Lies: Stress-Testing Multi-Agent Agreement with Counter-Evidence** — *recommended.*
   Matches the revision's final framing: the paper contributes an empirical paired-consensus
   phenomenon plus a pre-outcome stress-test protocol (CST-Bench), and it foregrounds the protocol
   rather than a standalone "signal," which is the more defensible claim after the round-7
   paired-prediction and independent-counter-evidence stress tests.
2. **When Consensus Lies: Counter-Evidence Responsiveness as a Pre-Outcome Signal of Consensus Error**
   — the v4 title. Still accurate: the pre-outcome ranking result (AUROC 0.943/0.896) is a central
   finding; it is retained as a candidate because the empirical claim is unchanged.
3. **Counter-Evidence Responsiveness Predicts Errors in Multi-Agent Consensus** — concise variant;
   acceptable only if "predicts" is read as pre-outcome ranking, not causal prediction.

The final title should be decided with the main editor after the three-contribution structure is
locked; the body below uses candidate 1 as the working title.

---

## Abstract

Multi-agent LLM panels are widely used for fact verification, but consensus is not evidence of
correctness: panels can converge on an incorrect answer with high agreement. We identify and
rigorously test a pre-outcome empirical regularity—*consensus items that fail to respond to
decision-relevant counter-evidence are substantially more likely to be wrong*—and contribute a
stress-test protocol (CST-Bench) that measures this regularity before gold labels are observed.
On a frozen 300-pair, 600-item VitaminC natural-pair protocol, the label-free score
RS_q = −BF_q (paraphrase stability + natural counter-evidence responsiveness) ranks consensus
errors with AUROC 0.943 [0.924, 0.960] and Risk@80 0.846 [0.638, 0.981] for Qwen3.5-4B panels
(567 HC items) and AUROC 0.896 [0.873, 0.916] and Risk@80 0.422 [0.274, 0.591] for Ling-3.0-tiny
panels (574 HC items); a frozen cross-model procedure transfer reaches AUROC 0.723 [0.682, 0.765],
and a single-point 100-item GPT-class validation reaches 0.969 [0.935, 0.995]. The main score
requires **10 probe calls after 5 consensus-formation calls** per item; the remaining 10 calls of
the full protocol are auxiliary diagnostics that never enter the score.

Two round-7 stress tests bound the interpretation. First, a paired-prediction diagnostic
(reverse-condition-free, post-hoc) reconstructs the reverse axis exactly (Spearman 0.998 vs
BF_reverse; AUROC 0.931/0.869) and ~98.7%/97.0% of RS_q's ranking power from the two
original-condition answers alone: the error-ranking signal is a *natural-pair property*.
Second, an independent-counter-evidence control—counter-evidence generated from the claim alone,
textually independent of the natural mirror, compared against a matched placebo—shows that panels
flip significantly more under decision-relevant independent counter-evidence than under the
placebo (strict variant Δ_CE = +0.212 [+0.116, +0.310]; label-coupled variant Δ_CE = +0.293
[+0.206, +0.368]), so *selective average responsiveness to decision-relevant counter-evidence is
not purely a mirror artifact*; the placebo baseline is not clean in either variant (0.514/0.544),
and the strict independent score carries no error-ranking increment over the natural-pair signal
(paired ΔAUROC −0.349 [−0.714, −0.091] vs S_natural; ρ ≈ 0.03). The signal is specific to
natural counter-evidence: a negation-prefix control (BoolQ) reverses direction (AUROC 0.449).
Responsiveness is therefore reported as a descriptive, pre-outcome behavioral regularity under
the natural-pair protocol—not as a latent trait, a causal mechanism, or an independently
deployable counter-evidence-generation pipeline. Claims are bounded to two small open-weight
models, one GPT-class single point, and one dataset.

## 1 Introduction

### 1.1 Consensus is not reliability

Multi-agent LLM panels—several personas sampled from one or more models that read shared evidence
and vote—are a common recipe for fact verification and reasoning [CITE]. A panel that converges on
one answer with high agreement appears trustworthy: it has examined the same evidence, reasoned
through different personas, and still reached the same conclusion. Agreement, however, is an
*internal* property of the panel; by itself, it does not establish that the evidence supports the
answer. A panel can be unanimous and wrong. Confidence scoring does not resolve this failure mode:
on our frozen benchmark, vote agreement and several confidence variants rank consensus errors only
slightly above chance (AUROC 0.58–0.73 on Qwen3.5-4B panels), and their paired AUROC differences
from our proposed score have confidence intervals that exclude zero (e.g., +0.360 [0.305, 0.412]
versus vote agreement; +0.315 [0.271, 0.360] versus an internal symmetric risk score).

Existing consensus- and uncertainty-oriented methods inspect agreement, confidence, or sampling
consistency—all properties of the panel's own outputs. Less attention is paid to a different
question: does a formed consensus respond appropriately when it is confronted with
*decision-relevant counter-evidence*—evidence that supports the opposite verdict? We ask a
narrower, pre-outcome question: once a consensus has formed, can we rank *which* consensuses face
elevated error risk using only evidence-level behavior, before the answer is labeled? We focus on
one behavior: whether the panel changes its answer when its evidence packet is replaced with
counter-evidence.

### 1.2 What we measure, and the mirror-equivalence caveat

We use the VitaminC natural-pair construction [CITE]. Each pair (i, j) shares a claim and a
distractor but has opposite gold labels, and the two evidence packets constitute one another's
natural counter-evidence. The frozen protocol records each agent under the original evidence, a
meaning-preserving paraphrase, and the swapped natural counter-evidence; the pre-registered score
is RS_q = −BF_q, a label-free composite of *paraphrase stability* (the agent retains its answer
under rewording, with its own original answer as the expectation) and *counter-evidence
responsiveness* (the agent changes its answer to the flip of its original answer under the natural
evidence swap). Features are frozen without labels; outcomes are merged only afterward.

One property of this construction bounds every interpretive claim and is stated once here and
again, with the round-7 quantification, in §3.5 and §4.6. Because the reverse-view prompt for item
i is byte-identical to the original-view prompt for its mirror item j (verified on 3,000/3,000
rebuilt prompt pairs; answers agree on 99.97% of Qwen and 99.63% of Ling agent calls [W1]),
BF_reverse is a deterministic re-encoding of the panel's original answer, its mirror-item answer,
and the frozen paired gold: at the single-call level, an originally correct agent is counted
faithful exactly when it answers the mirror item correctly, and an originally wrong agent exactly
when it answers the mirror item incorrectly. The reverse axis therefore measures a *pre-outcome
behavioral regularity of natural pairs*—not an independently sampled probe of a latent trait.
A paired-prediction diagnostic (§4.6) confirms the consequence: the reverse axis—and ~98.7%/97.0%
of RS_q's ranking power—can be reconstructed without any reverse-condition call. The
independent-counter-evidence experiment (§4.7) separately tests whether the model's *average*
responsiveness is specific to decision-relevant counter-evidence beyond the mirror's byte identity.

### 1.3 Contributions

**C1 — Empirical phenomenon.** Under the frozen natural-pair protocol, wrong consensus is
disproportionately associated with insufficient response to decision-relevant counter-evidence:
reverse-axis responsiveness separates correct from wrong consensus (Qwen HC 0.843 vs 0.095;
Ling HC 0.703 vs 0.029), and RS_q ranks consensus errors before labels are merged with
AUROC 0.943 [0.924, 0.960] (Qwen) and 0.896 [0.873, 0.916] (Ling), with Risk@80 0.846 [0.638,
0.981] and 0.422 [0.274, 0.591]. The phenomenon replicates across two model families and, as a
single point, a GPT-class relay model.

**C2 — Evaluation protocol (CST-Bench).** A pre-outcome stress-test protocol that measures
counter-evidence responsiveness before gold labels are observed, with explicit call accounting:
**5 consensus-formation calls + 10 main probe calls + 10 auxiliary diagnostic calls per item**
(the main score requires 10 probe calls after consensus formation), an outcome firewall that
merges labels only after features are frozen, a deterministic frozen cohort, preregistered gates,
and pair-grouped bootstrap 95% CIs.

**C3 — Empirical validation.** A preregistered, frozen evaluation with label-stratified metrics,
placebo/permutation/reducibility controls, matched-budget adapted baselines, and cross-model
procedure transfer—plus round-7 stress tests that bound the mechanism: a paired-prediction
reconstruction diagnostic (S_pair), independent counter-evidence controls with matched placebos
(Δ_CE > 0 in both a label-coupled and a strict claim-only construction), multi-axis pressure
profiles, and continuous-λ stress curves. These tests show where the signal is *not* an artifact
(the average flip-rate effect is not purely a mirror consequence) and where it remains a
natural-pair property (the error-ranking signal is substantially reconstructible from paired
answers, and independent counter-evidence does not yet yield an incremental ranking signal).

### 1.4 Scope of claims

The evidence base is the frozen VitaminC natural-pair protocol (600 items), two small open-weight
models (Qwen3.5-4B primary, Ling-3.0-tiny secondary), and one GPT-class single point (100 items,
relay). The central claim is a *pre-outcome behavioral regularity under natural-pair
construction*: consensus items that do not respond to the paired counter-evidence are
substantially more likely to be wrong, and this can be ranked before labels are known. The
regularity is descriptive and predictive; it is not a latent cognitive trait, and the reverse axis
does not independently measure evidence sensitivity beyond the paired structure. The paper
additionally establishes that panels respond selectively to *decision-relevant* counter-evidence
on average (independent of the mirror's byte identity), while the strict independent control does
not establish an independently deployable error-ranking signal (§4.7). Cross-dataset generality is
not claimed: the BoolQ negation-prefix control reverses the signal (AUROC 0.449), and a FEVER
replication is blocked at construction because no natural pairs exist in that data (§4.12).

## 2 Related Work

We position counter-evidence responsiveness within four clusters of prior work: (a) sampling
consistency and hallucination detection, (b) selective prediction and error prediction,
(c) faithfulness and counterfactual evaluation of model behavior, and (d) multi-agent reliability,
metamorphic testing, and consensus. Citations follow a dated literature audit (2026-09-12;
`phase1/novelty_map.md`) combining live arXiv/Crossref retrieval with model knowledge. Entries
whose bibliographic details were not live-verified are marked [CITE]; we do not claim exhaustiveness.

### 2.1 Sampling Consistency and Hallucination Detection

Self-consistency (Wang et al., 2022; arXiv:2203.11171) samples multiple reasoning paths for the
same input and selects a majority vote, showing that cross-sample agreement can improve performance
and provide a reliability signal. SelfCheckGPT (Manakul et al., 2023; arXiv:2303.08896) [CITE]
performs zero-resource, black-box hallucination detection by testing whether independently sampled
answers are consistent with the original response, without an external fact base. Semantic entropy
(Farquhar et al., 2024) [CITE] clusters sampled answers by meaning and uses entropy over semantic
clusters as an uncertainty estimate. Calibrated Language Models Must Hallucinate (Kadavath et al.,
2023; arXiv:2311.14648) [CITE] likewise shows that a model's cross-sample agreement predicts answer
correctness. The common signal is derived from repeated samples of the *same* input: the evidence
remains fixed, and the unit of analysis is a single model's sampling distribution. None of these
methods evaluates how an already-formed multi-agent panel changes its answer when its evidence
packet is replaced with natural counter-evidence. In our benchmark, matched-budget adaptations of
this family serve as external baselines (Sections 3.1 and 4.4).

### 2.2 Selective Prediction and Error Prediction

Selective prediction (El-Yaniv and Wiener, 2019; arXiv:1902.00080) allows a model to abstain,
trading coverage for error rate; risk-coverage curves and their area (AURC) are standard
evaluations. Conformal prediction sets provide coverage guarantees for set-valued predictions
(Sadinle et al., 2019; arXiv:1906.00073). Error prediction has also been studied through training
dynamics (arXiv:2205.13551) [CITE] and, most commonly, calibrated confidence, such as temperature
scaling or isotonic calibration to error probability. These methods use a single model's output
statistics for a single prediction on an unchanged input: none introduces a controlled evidence
intervention, and none targets a consensus formed by multiple agents. In our evaluation, the only
label-using comparators in this family are calibrated strictly out-of-fold.

### 2.3 Faithfulness and Counterfactual Evaluation of Model Behavior

ERASER (DeYoung et al., 2020) evaluates rationale faithfulness through sufficiency and
comprehensiveness: removing the rationale must change the model's score, for a single model.
Counterfactual tests of attribution methods (arXiv:2408.11252) ask whether attribution tracks model
behavior under counterfactual inputs. Measuring Faithfulness in Chain-of-Thought Reasoning (Lanham
et al., 2023) perturbs reasoning steps and measures changes in the answer. Precision Is Not
Faithfulness (arXiv:2606.09376) measures coverage-aware faithfulness of grounded-generation claims
against gold evidence. Citation-faithfulness detection extends this approach to citations
(CiteCheck, arXiv:2502.11054; agentic scientific synthesis, arXiv:2607.08328). These works
establish controlled perturbation as a valid probe of model behavior, and our expected-response
oracle is methodologically indebted to them. However, their object is a single model's explanation,
rationale, reasoning trace, or citation rather than a multi-agent consensus answer; their purpose is
descriptive faithfulness measurement rather than pre-outcome error ranking; and many variants
require gold rationales or labels.

### 2.4 Multi-Agent Reliability, Metamorphic Testing, and Consensus

METAL (arXiv:2312.06056) applies metamorphic relations to LLM qualities by transforming an input
and checking an expected output property without gold labels. It is the closest methodological
ancestor of our oracle, but it is invariance-oriented and targets single-model quality attributes
rather than consensus error prediction. CheckList (Ribeiro et al., 2020) operationalizes behavioral
testing of NLP models through invariance, directional-expectation, and minimum-functionality tests.
It is the closest conceptual ancestor of an "expected response," but likewise targets single-model
capabilities rather than pre-outcome consensus risk. NLI stress testing (Naik et al., 2018) applies
controlled sentence perturbations with labels present. REST (arXiv:2507.10541) stress-tests
reasoning models by packing multiple problems into one prompt, varying task load rather than
evidence. Evidence-State Reliability Under Controlled Degradation (arXiv:2608.21559) degrades
evidence in multi-stage LLM pipelines and evaluates pipeline evidence-state reliability; its unit is
the pipeline evidence state rather than the appropriateness of a consensus response, and it defines
no expected-response oracle and predicts no errors. Multi-agent debate work asks whether
deliberation among agents improves answers or justifies its cost ("Talk Isn't Always Cheap",
arXiv:2509.05396 [CITE]; Demystifying Multi-Agent Debate [CITE]). Debate is a procedure for
*forming* an answer, whereas our intervention probes an *already-formed* consensus.

### 2.5 Positioning

We propose counter-evidence responsiveness as a pre-outcome, evidence-level signal: an
already-formed multi-agent consensus is at elevated error risk when the panel does not change its
answer after its evidence packet is replaced with natural counter-evidence. Within our dated
2026-09-12 audit, we found no live hit and no dated prior work covering the joint combination of
(i) an already-formed multi-agent consensus as the object, (ii) a natural counter-evidence swap
with a label-free, decision-relevance-aware expected-response oracle as the probe, and (iii)
pre-outcome error prediction as the use. We state this as an audit result, not an exhaustiveness
claim. The contribution is deliberately bounded: a behavioral signal and a reproducible benchmark
(CST-Bench), not a "stress-testing framework," a latent "faithfulness trait," or a causal account
of why consensus errors occur.

## 3 Method

### 3.1 Task and Estimand

Each item presents a claim C and an evidence packet. Five agents independently answer a binary
verification question ("Does the provided evidence support the claim?", yes = SUPPORTS, no =
REFUTES). Data come from the official VitaminC test set and are restricted to *natural pairs*: two
rows sharing the same `case_id`, claim, and page/revision, with exactly one SUPPORTS and one
REFUTES label. Selection is frozen and deterministic (protocol `cs-paper-vitaminc-2026-09-13`,
preregistered before any model call): one pair per page (highest character ratio, then token
Jaccard); contrast gates character_ratio ≥ 0.85 and token Jaccard ≥ 0.70; no U+FFFD characters;
claim length 5–40 tokens and evidence length 10–120 tokens; ordering by sha256(SALT + page); and
page- and pair-disjointness from earlier pilots. This yields 300 pairs = 600 items, label-symmetric
by construction (300 SUPPORTS + 300 REFUTES). Each pair produces two composite items sharing the
claim: the S-item (gold SUPPORTS; own evidence = supports evidence, natural counter-evidence =
refutes evidence) and the R-item (gold REFUTES; symmetric). A deterministic,
non-decision-relevant distractor is shared by both items.

The formed consensus is the majority answer of the five original-condition agents; high consensus
(HC) denotes agreement ≥ 0.8 (at least 4 of 5 agents share the majority). The estimand is
consensus_wrong = 1[majority answer ≠ sealed gold] on the HC subset, and the task is *pre-outcome
risk ranking*: rank HC items by predicted risk before labels are merged. We report AUROC of the
risk score against consensus_wrong on HC with pair-grouped bootstrap 95% CIs (2,000 replicates),
and Risk@80, the error-rate reduction when the lowest-risk 80% of HC items are retained, with the
same uncertainty treatment. Comparator risk scores (mean confidence, disagreement, frozen prior
scores, and matched-budget adaptations of the sampling-consistency family) are evaluated on the
same HC subset under the benchmark's matched-call accounting; the only label-using comparators are
calibrated strictly out-of-fold. All directions and gates were frozen before any model call; no
post-hoc sign flip or metric repair is permitted.

### 3.2 Panel and Environment

Five frozen personas (`AGENT_PERSONAS`), each paired with a frozen 2-of-3 partition table
(`PARTITION_TABLE`), form the panel. Every agent sees a fixed two of the three packet units in each
condition, and every view of every non-remove condition contains at least one decision-relevant
unit. Calls use temperature 0 with deterministic per-(agent, condition) seeds, max_tokens=160,
prompt-only JSON (no response_format, no reasoning_effort), up to two retries with a frozen repair
suffix, and content-addressed caching. The primary model is local Qwen3.5-4B; Ling-3.0-tiny is a
preregistered secondary model evaluated under the identical protocol.

Evidence identities. Each item has own evidence E, two meaning-preserving paraphrases
para_1(E), para_2(E), paired natural counter-evidence E_opp (the mirror item's evidence), and a
shared distractor D with token Jaccard ≤ 0.05 against the claim. The five frozen conditions are:
original [E, para_1(E), D]; paraphrase [para_1(E), para_2(E), para(D)]; natural reverse
[E_opp, para_1(E_opp), D]; synthetic reverse (negated units; secondary only); and remove (empty
packet).

Expected-response oracle (label-free, frozen offline, decision-relevance-aware). The relevance
rules are: own evidence (R1), its paraphrases (R2), and paired counter-evidence (R3) are
decision-relevant; a negated unit is relevant if and only if its base is relevant (R4); the
distractor is not decision-relevant (R5); and an empty packet yields no forced response (R6). The
expected response under transformation T is defined solely by transformation semantics: paraphrase
⇒ keep (Y* = Y_0, the agent's own original-condition answer); natural reverse ⇒ flip (Y* =
flip(Y_0)); remove ⇒ no forced response (descriptive only). An agent call is scored if and only if
its view contains at least one decision-relevant unit with a defined expected response. Under the
frozen 2-of-3 partition, all non-remove views are scored. Per-agent, per-condition faithfulness is
f_cond(i,a) = 1[Y(i,cond,a) = Y*(cond)]. Offline audits (decision relevance, ≥ 24/30; paraphrase
meaning preservation, ≥ 80%) precede any agent call, with frozen fallback triggers.

Cross-model contract adaptation (preregistered before any Ling call; protocol
`cs-paper-ling-adapted-20260913-round4`). On the same 600 items with identical evidence, oracle,
conditions, formula, direction, and gates, one transport detail differs: the JSON contract no
longer requests or validates a model-reported `agent_id`; instead, the task dispatcher binds agent
identity server-side to the frozen `agent_index`, persona, and partition, and the record stores
both. This is a provenance change only: it was registered before outcomes were observed, applied
uniformly, and does not enter the oracle, BF_q, RS_q, consensus, agreement, or any gate.

### 3.3 CST-Bench Protocol and Call Accounting

The full protocol consumes **25 calls per item**, organized into three parts:

| Part | Conditions | Calls/item | Role |
|---|---|---|---|
| Consensus formation | original | 5 (5 agents × 1) | Forms the panel consensus and defines the flip expectation Y_0 |
| **Main probe** | paraphrase, natural reverse | **10 (5 agents × 2)** | **The only calls entering the risk score RS_q** |
| Auxiliary diagnostics | synthetic reverse, remove | 10 (5 agents × 2) | Controls/robustness only; never enter RS_q |

The main score therefore requires **10 probe calls after the 5 consensus-formation calls** per
item; the auxiliary diagnostics are reported for controls (e.g., synthetic-reverse dilution,
removal-axis signature, §4.5, §4.8) but are not part of the method's cost. Total experimental cost
is reported separately: 25 calls/item for the full protocol (15 score-relevant: 5 consensus + 10
probe; plus 10 diagnostics). This accounting replaces any description of the main method as a
"25-call score"; RS_q is a 10-probe-call score computed on top of a 5-call consensus.

### 3.4 Risk Score: RS_q = −BF_q

The frozen composite score is

$$BF_q = \frac{1}{5}\sum_{a=1}^{5} \frac{f_{\mathrm{para}}(i,a) + f_{\mathrm{rev}}(i,a)}{2},$$

the mean across the five agents of per-agent faithfulness averaged over the paraphrase and
natural-reverse conditions, and

$$RS_q = -BF_q,$$

so lower expected-response fidelity under natural counter-evidence (higher RS_q) predicts greater
risk that the formed consensus is wrong. Synthetic reverse is reported per condition only and never
enters BF_q (frozen). The direction "higher RS_q = riskier" was fixed before any model call, after
a round-2 sign-consistency correction, and was not selected post hoc.

### 3.5 Mirror Equivalence: What the Reverse Axis Measures

The natural-reverse view of item i is byte-identical to the original view of mirror item j (same
claim, persona, partition, evidence texts, distractor, and seed). A round-7 audit rebuilt all
prompts from the frozen manifests and confirmed byte-level identity on 3,000/3,000 prompt pairs;
temperature-0 inference then gives the View Identity Y(i, reverse, a) = Y(j, original, a),
verified on 99.97% (Qwen) and 99.63% (Ling) of agent calls, with residual mismatches attributable
to parse-repair paths [W1]. Consequently, BF_reverse is a deterministic re-encoding of three
ordinary quantities—the panel's original answers, its mirror-item answers, and the frozen paired
gold labels—rather than a measurement of a latent trait. At the single-call level, an originally
correct agent is counted faithful exactly when it answers the mirror item correctly, whereas an
originally wrong agent is counted faithful exactly when it answers the mirror item incorrectly
(f_rev = m_j(a) if correct, 1 − m_j(a) if wrong). At the consensus level on HC (agreement ≥ 0.8),
BF_reverse on a correct consensus coincides with mirror-item accuracy, whereas on a wrong consensus
it coincides with its complement, 1 − mirror accuracy. Empirically, this yields the collapse from
0.844 (correct, Qwen) / 0.703 (correct, Ling) to 0.095 (wrong, Qwen) / 0.029 (wrong, Ling).

The consequence is quantified by a paired-prediction diagnostic [W1] (§4.6). Define
S_pair_flip(i) = mean_a 1[ŷ_j(a) == flip(ŷ_i(a))], using only the two original-condition answers
of the pair (no reverse-condition call, no labels). By the View Identity this is a
reverse-call-free implementation of BF_reverse: the two scores are equal on 99.82% (Qwen) and
98.43% (Ling) of HC items (Spearman 0.998 [0.993, 1.000] / 0.998 [0.994, 1.000]; paired AUROC
difference −0.0000 [−0.0002, 0.0000] / −0.0002 [−0.0009, 0.0003]), and S_pair reconstructs
~98.7% (Qwen) / ~97.0% (Ling) of RS_q's ranking power. The paraphrase axis is the only component
not subject to this reduction: it is the same item under meaning-preserving rewording (Y* = Y_0)
and measures paraphrase stability independently of label alignment, contributing a small but
statistically significant increment (RS_q − S_pair: +0.0122 [0.0022, 0.0228] / +0.0272 [0.0137,
0.0422]).

The reverse axis is therefore described strictly as *counter-evidence responsiveness*—a
descriptive, pre-outcome-computable behavioral regularity under the natural-pair protocol—and the
paper makes no causal claim that counter-evidence causes consensus error, that responsiveness
causes correctness, or that the score measures a latent "faithfulness" or "rigidity" trait.
Whether responsiveness is specific to *decision-relevant* counter-evidence (beyond the mirror's
byte identity) is tested separately by the independent-counter-evidence experiment (§4.7).

### 3.6 Outcome Firewall and Controls

Outcome firewall. Gold labels are merged only after all pre-outcome features are frozen. Before
merging, forbidden inputs to any score are the gold label, the gold binary, per-agent correctness,
and consensus_wrong. Dataset labels are used offline only to construct the balanced design and
artifact texts; they are never sent to agents or used in probing or scoring. Both protocols were
registered before their model calls, and all gates, directions, and fallbacks were fixed in those
registrations. A round-7 leakage audit traced the full path—prompt construction → evidence
generation → scoring → model selection → threshold selection—and found no path by which labels
enter pre-outcome computation or selection: the prompt builder and feature extractor contain no
label tokens, and the score files are label-free before merge [W1].

Placebo control. The paraphrase axis is the same item under meaning-preserving rewording and
therefore serves as a stability placebo: agent-level paraphrase flip rates of 0.038 (Qwen) and
0.061 (Ling) are far below the preregistered 0.30 threshold, indicating that the reverse-axis
asymmetry is not explained by general prompt instability.

Permutation control. The observed primary AUROC exceeds the 95th percentile of 1,000 per-item
preserve/flip-swap permutations that randomize the sign of each BF component per item (Qwen 0.943
> 0.596; Ling 0.896 > 0.564). Thus, the directional association between low responsiveness and
error is not reproduced when component signs are scrambled.

Reducibility control. RS_q is not a re-expression of agreement or confidence:
|Spearman(RS_q, agreement)| < 0.9 and |Spearman(RS_q, mean_confidence)| < 0.9 (Qwen −0.004 /
−0.161; Ling −0.148 / −0.050), and AUROC on the agreement = 0.8 stratum is 0.844 (Qwen), above
chance. This reducibility check is distinct from the mirror reduction in Section 3.5, which
concerns BF_reverse versus mirror-item accuracy.

Frozen gates. The preregistered within-model gate requires, jointly: pipeline validity ≥ 0.95;
primary AUROC CI lower bound > 0.5 with point estimate ≥ 0.60; macro-label and worst-label AUROC
CI lower bounds > 0.5; the placebo threshold above; the permutation gate above; the reducibility
thresholds above; and, for the formal Risk@80 phase, a paired Risk@80 CI excluding zero in the
favorable direction. No gate is re-run or retuned after outcomes; a failing gate is reported as a
failure.

## 4 Experiments and Results

We evaluate counter-evidence responsiveness as a *pre-outcome* error signal for multi-agent
consensus. All protocols were frozen before any model call; all risk scores are outcome-independent
(no label fields are used before label merge); and every reported interval is a 95% pair-grouped
bootstrap interval (2,000 replicates), computed with a fixed seed base (`20260913`) and
per-statistic offsets. Paired comparisons are computed on the high-consensus (HC) intersection. All
frozen numbers below are reproduced from the frozen analysis artifacts listed in the repository;
round-7 additions are labeled post-hoc. No figure is included in the frozen results; round-7
diagnostic figures are listed in Section 8.

### 4.1 Setup

**Cohort.** The main cohort is a fresh, frozen sample of 300 natural contrastive pairs (600 items)
from VitaminC. It is label-symmetric by construction: each pair contains one SUPPORTS item and one
REFUTES item (300 + 300), with the same evidence view, prompt template, and oracle; the items
differ only in the mirrored evidence conclusion. Items are page- and pair-disjoint from earlier
rounds (150 round-2 pairs; the frozen V3.16/V3.16.1 pages). Eligibility requires
`character_ratio >= 0.85` and `token_jaccard >= 0.70` (one pair per page), with contrast medians of
0.95 / 0.84. The pipeline produced 900/900 usable paraphrase artifacts, 15,000/15,000 agent records
with 14,999 valid (99.99%; one reverse call failed after retry), 30/30 meaning-preserving
paraphrases, 30/30 decision-relevant audit items, and pre-outcome features frozen on all 600 items
before label merge.

**High-consensus populations.** HC is defined as five-agent agreement `>= 0.8` and is fixed before
evaluation. Qwen3.5-4B has 567 HC items (94.5% of 600; 298 pairs), including 65 wrong items
(11.5%). Ling-3.0-tiny has 574 HC items (299 pairs), including 119 wrong items (20.7%). The models
therefore have different failure distributions.

**Models.** Qwen3.5-4B is the primary model, and Ling-3.0-tiny is the secondary model.
gpt-6-astra (a relayed GPT-class model) provides a single-point validation of 100 items. No Qwen
calls were rerun for any analysis; all later rounds reuse the frozen Qwen records.

**Metrics.** The primary metric is AUROC of the risk score for the HC error indicator
(`wrong | HC`). Risk@80 is the relative error reduction obtained by retaining the lowest-risk 80%
of HC items (operating point 0.8). Paired differences are computed on the HC intersection. The risk
form is `RS_q = -BF_q` (higher = riskier), where `BF_q = (bf_paraphrase + bf_reverse)/2` is
expected-response faithfulness averaged over the five agents. Here, `bf_paraphrase` is paraphrase
fidelity (`1 - para_flip_rate`), and `bf_reverse` is natural-reversal fidelity (the proportion of
agents that flip to the oracle's expected opposite under natural counter-evidence).

**Controls.** (i) *Placebo:* the paraphrase-flip rate must remain below 0.30 so that
meaning-preserving paraphrases are not themselves adversarial; the observed rates are 0.038 (Qwen)
and 0.061 (Ling). (ii) *Permutation:* the observed AUROC must exceed the 95th percentile of the
permuted-null distribution; Qwen achieves 0.943 > 0.596, and Ling achieves 0.896 > 0.564.
(iii) *Reducibility:* absolute Spearman correlations with agreement and confidence must remain
below 0.9, and AUROC at an agreement-0.8 split must exceed 0.5 (Qwen: -0.004 / -0.161; 0.844;
Ling: -0.148 / -0.050). Section 4.9 analyzes reducibility against the strongest internal baseline
in detail.

### 4.2 Main results (Qwen3.5-4B)

**Gate set (8/8 PASS).** The frozen paper-scale gate set passes all eight checks (Table 1). The
primary gate is CI-level: the lower bound of AUROC(RS_q, wrong | HC) must exceed 0.5, with a point
estimate >= 0.60.

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

**Against internal baselines.** RS_q ranks consensus errors with AUROC 0.943 [0.924, 0.960] and
reduces retained error by 84.6% at 80% coverage (Risk@80 0.846 [0.638, 0.981]). It significantly
outperforms the frozen internal baselines—R_sym (0.3·reverse_inertia + 0.7·intervention_disagreement),
R_PI (the frozen BoolQ provenance–intervention score), disagreement, and mean confidence—with
CI-confirmed paired AUROC differences. The strict Risk@80 gate (CI lower bound > 0) also passes
(Table 2). A label-blind fitted logistic model over {paraphrase, reverse} achieves 0.941 [0.922,
0.959], tying the frozen composite (paired diff +0.002 [-0.002, +0.007] includes 0). This indicates
that the signal comes from the concept—expected-response faithfulness with a
decision-relevance-aware oracle—rather than from additional fitting. Isotonic calibration reduces
ECE from 0.057 to 0.013 (reported; AUROC unchanged by design). The paper-scale result maintains or
exceeds the round-2 baseline (AUROC 0.906 [0.865, 0.944] -> 0.943; Risk@80 0.654 -> 0.846).

**Table 2: Phase-4 comparison on Qwen HC items (n = 567). Paired diffs are RS_q minus the
baseline; positive favors RS_q.**

| Representation | AUROC [95% CI] | Risk@80 [95% CI] | Paired AUROC diff [95% CI] | Paired Risk@80 diff [95% CI] |
|---|---|---|---|---|
| RS_q = -BF_q | **0.943 [0.924, 0.960]** | **0.846 [0.638, 0.981]** | — | — |
| logistic OOF {para, rev} | 0.941 [0.922, 0.959] | — | +0.002 [-0.002, +0.007] (tie) | — |
| R_sym (frozen) | 0.892 [0.861, 0.921] | 0.499 [0.273, 0.770] | +0.051 [+0.029, +0.075] | +0.347 [+0.152, +0.502] |
| R_PI (frozen) | 0.628 [0.586, 0.670] | -0.001 [-0.235, 0.271] (n.s.) | +0.315 [+0.271, +0.360] | +0.847 [+0.677, +0.984] |
| disagreement | 0.583 [0.536, 0.630] | 0.095 [-0.076, 0.388] (n.s.) | +0.360 [+0.306, +0.413] | +0.751 (point; CI n.r.) |
| confidence | 0.272 [0.226, 0.321] | -0.232 [-0.511, 0.039] (n.s.) | +0.671 [+0.620, +0.723] | +1.078 (point; CI n.r.) |

*Note: for the last two rows, the frozen Phase-4 protocol reported paired Risk@80 differences as
point estimates only; CIs are not reported in the artifact ("n.r."). Confidence is anti-predictive
(AUROC < 0.5).*

**Label-symmetric design, asymmetric error behavior.** The construction is label-symmetric (300
SUPPORTS + 300 REFUTES items), but model behavior is not: Qwen makes errors on 7/283 SUPPORTS items
(2.5%) versus 58/284 REFUTES items (20.4%), or 8.3x more often on REFUTES; REFUTES accounts for
89.2% of the HC error mass. The label-symmetric design is intended precisely to expose this
asymmetry: the risk signal is not an artifact of a single label. We therefore report per-label and
matched diagnostics in Section 4.10 rather than collapsing both labels into a single claim.

### 4.3 Cross-model: Ling-3.0-tiny

**Procedure transfer with a frozen score.** The complete frozen Round-3 cohort (300 pairs / 600
items) was rerun with Ling-3.0-tiny under the same frozen evidence, oracle, conditions, BF_q, and
RS_q. The only protocol adaptation concerned response transport: Ling no longer self-reports
`agent_id`, so the task dispatcher binds the frozen agent index/persona/partition server-side,
while the parser validates `answer`, `confidence`, and `cited_evidence_ids`; a frozen JSON exemplar
appears in every prompt. Calls were 15,000/15,000 valid (100%; first-pass 14,992/15,000 = 99.95%),
with 3,000/3,000 valid calls in every condition.

**Ling within-model gate: 8/8 PASS** (Table 3). On Ling's own 574 HC items, the unchanged RS_q
procedure ranks Ling's 119 errors with AUROC 0.896 [0.873, 0.916].

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

**Score transfer.** The frozen Qwen item-level RS_q, applied to Ling's own errors, achieves AUROC
0.723 [0.682, 0.765] and Risk@80 0.296 [0.148, 0.439], with both CI lower bounds above 0.5
(Table 4). Ling's own procedure score is significantly better (paired AUROC diff -0.173 [-0.217,
-0.130]; Risk@80 diff -0.126 [-0.226, -0.062]). Item-level Spearman correlation between Qwen and
Ling RS_q is only 0.496 on the 574 HC items. Outcome overlap is limited: across all 600 items, the
models share the consensus on 511, are both wrong on 57, Qwen-only wrong on 19, and Ling-only wrong
on 62. The procedure and the aggregate signal transfer; item-level ranking does not.

**Table 4: Frozen score transfer to Ling errors (574 HC items).**

| Quantity | AUROC [95% CI] | Risk@80 [95% CI] |
|---|---|---|
| Frozen Qwen item-level RS_q on Ling errors | 0.723 [0.682, 0.765] | 0.296 [0.148, 0.439] |
| Ling's own unchanged RS_q procedure | 0.896 [0.873, 0.916] | 0.422 [0.274, 0.591] |
| Paired diff (Qwen-transfer - Ling-own) | -0.173 [-0.217, -0.130] | -0.126 [-0.226, -0.062] |

**Mechanism fidelity.** On Ling HC items, mean natural-evidence reversal fidelity is 0.703 for
correct consensus and 0.029 for wrong consensus; the correct-minus-wrong difference is 0.674
[0.629, 0.719], with the CI excluding zero. Wrong Ling consensus is therefore substantially more
rigid under natural evidence reversal than correct consensus, replicating the central Qwen
mechanism in a different model family. This supports cross-family transfer on this frozen VitaminC
natural-pair protocol for Qwen3.5-4B and Ling-3.0-tiny only; it does not establish universal
transfer, superiority over all reliability baselines, or zero-shot generalization to arbitrary
datasets.

### 4.4 External baselines / leaderboard

We compared RS_q with 11 methods on the same frozen VitaminC main split under a matched per-item
call/token budget. All external baselines are **matched-budget adapted proxies**—binary/answer-match
variants, including Self-consistency as 1 − modal frequency, an answer-match SelfCheckGPT-style
variant without its NLI/self-check pipeline, and a binary semantic-entropy variant without
bidirectional-entailment clustering—and are not presented as implementations of the original
published methods. The three binary sampling-consistency variants share one 25-sample
temperature-0.7 answer distribution and produce identical features; they are therefore reported as
a single merged row. The "single-agent intervention" row is our own ablation (5 personas → 1
persona), labeled external only for ranking and narration.

RS_q ranks first on both models under the leaderboard's stated rule (AUROC point estimate, then
Risk@80, then calls/item), with the best AUROC point (Qwen 0.943 [0.924, 0.960]; Ling 0.896 [0.875,
0.917]). No baseline is significantly better than RS_q: for every baseline, the paired AUROC
difference CI (RS_q − baseline) is either entirely above 0 (RS_q significantly better) or includes
0 (the single-agent intervention); none has an upper bound below 0 (Tables 5–6). RS_q is not
the best Risk@80 point in every comparison: on Qwen, the reversal-only(5) probe has a slightly
higher Risk@80 point (0.884 vs 0.846), and that probe is analyzed separately in Section 4.5.

**Table 5: Leaderboard, Qwen3.5-4B (567 HC items; 65 wrong). Paired diffs are RS_q minus baseline.
Calls/item counts use the accounting of §3.3: main score = 10 probe calls (+5 consensus); total
protocol = 25.**

| Method | Calls/item | AUROC [95% CI] | Risk@80 [95% CI] | Paired AUROC diff [95% CI] | Paired Risk@80 diff [95% CI] |
|---|---|---|---|---|---|
| CST RS_q (proposed) | 10 probe / 25 protocol | 0.943 [0.924, 0.960] | 0.846 [0.651, 0.981] | — | — |
| Reversal-only probe (5 calls) | 5 / 10 | 0.931 [0.913, 0.948] | 0.884 [0.556, 0.981] | +0.012 [0.002, 0.023] | -0.039 [-0.038, 0.134] |
| Single-agent intervention | 25 / 25 | 0.925 [0.900, 0.948] | 0.769 [0.514, 0.942] | +0.018 [-0.001, 0.039] | +0.077 [0.000, 0.210] |
| R_sym (internal) | 25 / 25 | 0.892 [0.864, 0.916] | 0.499 [0.281, 0.754] | +0.051 [0.029, 0.075] | +0.347 [0.154, 0.502] |
| Frozen mean confidence | 5 / 5 | 0.728 [0.676, 0.775] | 0.268 [-0.004, 0.445] | +0.215 [0.165, 0.270] | +0.578 [0.464, 0.774] |
| Sampling-consistency family (3 identical variants) | 25 / 25 | 0.645 [0.575, 0.712] | 0.249 [0.063, 0.485] | +0.297 [0.229, 0.374] | +0.597 [0.401, 0.749] |
| Raw sampled confidence | 25 / 25 | 0.628 [0.558, 0.693] | 0.095 [-0.148, 0.316] | +0.314 [0.248, 0.383] | +0.751 [0.598, 0.910] |
| R_PI (internal) | 25 / 25 | 0.628 [0.584, 0.673] | -0.001 [-0.246, 0.257] | +0.315 [0.271, 0.359] | +0.847 [0.684, 0.978] |
| Isotonic confidence | 25 / 25 | 0.585 [0.513, 0.651] | 0.037 [-0.202, 0.276] | +0.358 [0.288, 0.432] | +0.809 [0.634, 0.963] |
| Vote agreement | 5 / 5 | 0.583 [0.530, 0.638] | 0.095 [-0.071, 0.382] | +0.360 [0.305, 0.412] | +0.751 [0.532, 0.844] |
| Temperature confidence | 25 / 25 | 0.580 [0.503, 0.652] | 0.076 [-0.181, 0.325] | +0.363 [0.284, 0.443] | +0.770 [0.597, 0.928] |

**Table 6: Leaderboard, Ling-3.0-tiny (574 HC items; 119 wrong). Paired diffs are RS_q minus
baseline.**

| Method | Calls/item | AUROC [95% CI] | Risk@80 [95% CI] | Paired AUROC diff [95% CI] | Paired Risk@80 diff [95% CI] |
|---|---|---|---|---|---|
| CST RS_q (proposed) | 10 probe / 25 protocol | 0.896 [0.875, 0.917] | 0.422 [0.272, 0.583] | — | — |
| Single-agent intervention | 25 / 25 | 0.883 [0.860, 0.905] | 0.412 [0.239, 0.556] | +0.014 [-0.003, 0.030] | +0.011 [-0.021, 0.085] |
| Reversal-only probe (5 calls) | 5 / 10 | 0.869 [0.847, 0.891] | 0.348 [0.184, 0.526] | +0.027 [0.013, 0.042] | +0.074 [0.031, 0.125] |
| R_sym (internal) | 25 / 25 | 0.818 [0.787, 0.847] | 0.212 [0.033, 0.366] | +0.078 [0.053, 0.104] | +0.210 [0.155, 0.309] |
| Frozen mean confidence | 5 / 5 | 0.611 [0.568, 0.655] | 0.128 [-0.051, 0.230] | +0.285 [0.236, 0.330] | +0.294 [0.253, 0.430] |
| Raw sampled confidence | 25 / 25 | 0.587 [0.543, 0.632] | 0.075 [-0.073, 0.224] | +0.309 [0.260, 0.358] | +0.347 [0.273, 0.439] |
| Temperature confidence | 25 / 25 | 0.585 [0.541, 0.629] | 0.075 [-0.079, 0.212] | +0.312 [0.263, 0.362] | +0.347 [0.260, 0.438] |
| R_PI (internal) | 25 / 25 | 0.577 [0.553, 0.602] | -0.103 [-0.269, 0.050] | +0.319 [0.292, 0.347] | +0.525 [0.448, 0.608] |
| Isotonic confidence | 25 / 25 | 0.568 [0.523, 0.614] | 0.075 [-0.072, 0.217] | +0.329 [0.278, 0.378] | +0.347 [0.277, 0.444] |
| Sampling-consistency family (3 identical variants) | 25 / 25 | 0.562 [0.527, 0.601] | 0.086 [-0.046, 0.252] | +0.334 [0.292, 0.372] | +0.336 [0.231, 0.406] |
| Vote agreement | 5 / 5 | 0.544 [0.512, 0.579] | 0.054 [-0.072, 0.219] | +0.353 [0.322, 0.385] | +0.368 [0.273, 0.431] |

**Single-agent intervention.** At a matched 25-call budget, a single-agent intervention (5 personas
→ 1 persona, our own ablation) achieves AUROC 0.925 [0.900, 0.948] on Qwen and 0.883 [0.860,
0.905] on Ling. Its paired AUROC difference from RS_q is not significant for either model: +0.018
[-0.001, 0.039] (Qwen) and +0.014 [-0.003, 0.030] (Ling), with both CIs including 0. For Risk@80,
the Qwen difference CI lower bound is exactly 0.000 ([0.000, 0.210]), while the Ling CI includes 0
([-0.021, 0.085]). RS_q is therefore point-best but statistically tied with this ablation on AUROC.
This is consistent with the axis decomposition (Section 4.9): most of the signal comes from the
natural-reversal axis, which the single-agent intervention still exposes. RS_q's robust,
CI-confirmed advantages are over the internal R_sym/R_PI and the proxy families; the
reversal-only(5) probe is analyzed separately in Section 4.5.

### 4.5 Cost and call accounting: how many calls buy how much reliability

Using only the frozen records (zero new model calls), we vary the number of marginal stress calls
added to the already-formed five-agent consensus (total = marginal + 5 consensus calls).
Reversal-only probes use 1, 2, 5, or 10 marginal calls; risk is defined as 1 − mean natural-reversal
fidelity over the first K agents, and the 10-call version additionally includes the
synthetic-reverse condition. Reversal+paraphrase probes use 2, 4, or 10 marginal calls; risk is
defined as 1 − mean fidelity over (paraphrase + reverse) / 2, with K = 5 recovering the frozen
BF_q score function. Missing or invalid calls are treated as missing responses. Table 7 reports
AUROC and Risk@80; Table 8 reports paired differences relative to the full RS_q (10 probe calls /
25 protocol calls per item; positive = RS_q better).

**Table 7: AUROC and Risk@80 by per-item calls (pair-grouped 95% CI). Calls/item is marginal
probe / total protocol; RS_q uses its 10 probe calls.**

| Method | Calls/item (probe / protocol) | Qwen AUROC [95% CI] | Qwen Risk@80 [95% CI] | Ling AUROC [95% CI] | Ling Risk@80 [95% CI] |
|---|---|---|---|---|---|
| CST RS_q (proposed) | 10 / 25 | 0.943 [0.924, 0.960] | 0.846 [0.651, 0.981] | 0.896 [0.875, 0.917] | 0.422 [0.272, 0.583] |
| Reversal-only probe (1 call) | 1 / 6 | 0.873 [0.827, 0.918] | 0.750 [0.462, 0.923] | 0.851 [0.826, 0.873] | 0.296 [0.148, 0.484] |
| Reversal-only probe (2 calls) | 2 / 7 | 0.895 [0.846, 0.937] | 0.807 [0.537, 0.943] | 0.866 [0.842, 0.887] | 0.338 [0.179, 0.518] |
| Reversal-only probe (5 calls) | 5 / 10 | 0.931 [0.913, 0.948] | 0.884 [0.556, 0.981] | 0.869 [0.847, 0.891] | 0.348 [0.184, 0.526] |
| Reversal-family probe (10 calls) | 10 / 15 | 0.832 [0.796, 0.867] | 0.480 [0.295, 0.676] | 0.753 [0.729, 0.776] | 0.201 [0.054, 0.355] |
| Reversal+paraphrase (2 calls) | 2 / 7 | 0.873 [0.824, 0.918] | 0.673 [0.435, 0.904] | 0.859 [0.834, 0.882] | 0.369 [0.193, 0.490] |
| Reversal+paraphrase (4 calls) | 4 / 9 | 0.898 [0.847, 0.941] | 0.807 [0.526, 0.942] | 0.878 [0.856, 0.899] | 0.412 [0.231, 0.545] |
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

1. **The 5-call cost story is not statistically supported.** The pre-registered adoption rule
   required reversal-only(5) to be no worse than RS_q on paired AUROC (CI lower bound <= 0) before
   adopting the 5-call story. The paired AUROC difference CI excludes 0 for both models—Qwen +0.012
   [0.002, 0.023]; Ling +0.027 [0.013, 0.042] (RS_q better)—so a "5 calls ≈ 10 calls" equivalence
   is not claimed. The Qwen gap is small, and Qwen reversal-only(5) is not worse on Risk@80 (paired
   diff -0.039 [-0.038, 0.134], CI including 0; point estimates 0.884 vs 0.846). The AUROC result
   is nevertheless significant for both models, and we report this negative result.
2. **The cheapest score-identical point is 10 probe calls/item.** Reversal+paraphrase(10) is
   score-identical to RS_q by construction: BF_q uses exactly the 10 scored paraphrase+reverse
   calls. The paired differences are 0.000 [0.000, 0.000] for AUROC and Risk@80 on both models,
   with identical AUROC point estimates (0.943 / 0.896). Any reduced-cost claim should therefore be
   stated as "10 probe calls/item (15 calls total including consensus formation)," not fewer.
3. **Adding synthetic reversal dilutes the signal.** The 10-call reversal-family probe (natural +
   synthetic reverse) is *worse* than the 5-call natural-only probe on both models (Qwen 0.832
   [0.796, 0.867] vs 0.931; Ling 0.753 [0.729, 0.776] vs 0.869), with large, significant paired
   differences relative to RS_q (0.111 [0.081, 0.139] / 0.144 [0.124, 0.164]). More calls therefore
   do not monotonically improve reliability; the natural counter-evidence axis is the informative
   component, and the auxiliary synthetic-reverse/remove diagnostics do not enter the score.
4. **Token accounting.** Reversal-only(5) costs 2,154 / 2,176 tokens/item (prompt + completion),
   compared with 10,196 / 10,354 for the full 25-call protocol on Qwen / Ling. The cheap probe is
   therefore materially less expensive, even though it is not statistically equivalent in AUROC.

### 4.6 Paired-prediction reconstruction (S_pair diagnostic; post-hoc [W1])

The central methodological question—how much of the observed signal is mechanically attributable to
the pair structure—is answered directly with a reverse-condition-free diagnostic on the frozen
records (zero new model calls; post-hoc label). Under the label convention gold SUPPORTS→yes,
REFUTES→no and the reverse oracle flip(y_0), the natural-pair construction makes "mirror answer ==
flip(original answer)" a label-consistent paired statistic. Define, using only the two
original-condition panel answers (all 600 items, not restricted to HC):

- s_pair_flip(i) = mean_a 1[ŷ_j(a) == flip(ŷ_i(a))] (mirror answer == flip of original answer;
  equals BF_reverse(i) by the View Identity),
- s_pair_same(i) = mean_a 1[ŷ_j(a) == ŷ_i(a)] (agent-level mirror agreement; informationally
  equivalent under binary answers),
- s_pair_panel(i) = 1[consensus_j == consensus_i] (panel-level).

None of these touches the reverse-condition records or any label.

**Table 9: S_pair reconstruction (HC; risk direction = higher more risk; pair-grouped 95% CI).**

| Feature | Qwen AUROC [CI] | Ling AUROC [CI] |
|---|---:|---:|
| **RS_q** (reference) | **0.943 [0.924, 0.960]** | **0.896 [0.873, 0.917]** |
| **BF_reverse** (risk direction, reference) | **0.931 [0.913, 0.948]** | **0.869 [0.846, 0.891]** |
| **S_pair_flip** (risk direction) | **0.931 [0.912, 0.948]** | **0.869 [0.846, 0.891]** |
| **S_pair_same** (risk direction) | **0.931 [0.912, 0.948]** | **0.869 [0.846, 0.891]** |
| S_pair_panel (risk direction) | 0.893 [0.847, 0.932] | 0.863 [0.838, 0.884] |

**Table 10: Paired differences and correlations (pair-grouped 95% CI).**

| Quantity | Qwen [CI] | Ling [CI] |
|---|---:|---:|
| S_pair_flip − BF_reverse (AUROC) | -0.0000 [-0.0002, 0.0000] | -0.0002 [-0.0009, 0.0003] |
| RS_q − S_pair_flip (AUROC) | +0.0122 [0.0022, 0.0228] | +0.0272 [0.0137, 0.0422] |
| RS_q − S_pair_panel (AUROC) | +0.0501 [0.0214, 0.0824] | +0.0338 [0.0184, 0.0498] |
| Spearman(S_pair_flip, BF_reverse) | 0.998 [0.993, 1.000] | 0.998 [0.994, 1.000] |
| Per-item equality s_pair_flip == bf_reverse (HC) | 99.82% | 98.43% |

**Mirror-item reconstruction.** Using only the mirror item's full calls (whose reverse-condition
calls are exactly item i's original-condition calls), RS_q(j) predicts item i's error with AUROC
0.909 [0.886, 0.932] (Qwen) and 0.827 [0.795, 0.856] (Ling)—96.4% / 92.2% of the item's own RS_q
ranking power. Wrong(i) does not imply wrong(j) (both-wrong: 5/567 Qwen, 0/574 Ling); the
reconstruction comes from the reverse axis being a deterministic function of paired original
answers, not from mirror-item co-error.

**Reading.** S_pair exactly reconstructs the reverse axis (per-item equality ≥ 98.4%, Spearman
0.998, paired AUROC difference ~0.000), and it reconstructs ~98.7% (Qwen) / ~97.0% (Ling) of RS_q's
ranking power. The only residual is the small paraphrase-axis increment (RS_q − S_pair_flip
+0.0122 [+0.0022, +0.0228] / +0.0272 [+0.0137, +0.0422], CI-excluding-zero but small; the
paraphrase axis alone has AUROC only 0.60 / 0.58). The ranking power of the main score is therefore
a property of the natural-pair structure: the reverse condition provides no measurement independent
of the paired construction. This diagnostic is post-hoc; it does not alter any frozen gate, and
S_pair is defined only on natural-pair benchmarks. It is the reason the paper claims a *pre-outcome
behavioral regularity under natural-pair construction*, and it motivates the independent-
counter-evidence experiment, which tests the average-responsiveness question without the mirror.

### 4.7 Independent counter-evidence: natural vs independent vs placebo (W2/W2b)

The S_pair diagnostic shows the *ranking* signal is a natural-pair property; it does not by itself
show whether the model's *average flip-rate response* is specific to decision-relevant
counter-evidence or merely to the mirror's byte identity. To test this, two preregistered
independent-counter-evidence protocols were run with gpt-6-astra (relay) panels, comparing three
evidence types: **natural** (the byte-identical mirror E_j), **independent** (E_ind, generated to
support the opposite conclusion without copying the mirror), and **placebo** (decision-irrelevant
evidence). The quantity of interest is Δ_CE = P(flip | E_counter) − P(flip | E_placebo): a
selective-response increment above an irrelevant-perturbation baseline.

**W2 (label-coupled, 98 items / 50 pairs).** E_ind was generated by gpt-6-astra (200 sentences, 2
per item; decision-relevance audit 0.90; token Jaccard vs the mirror median 0.23 / p90 0.42 / max
0.68; no verbatim copy). Three-condition formal run: 1,500/1,500 valid calls (first-pass 0.991).
Flip rates are item×agent label-blind (n = 498 per condition):

| condition | P(flip) | 95% CI |
|---|---|---:|
| natural | 0.8253 | [0.7289, 0.9140] |
| ind | 0.8373 | [0.7827, 0.8873] |
| placebo | 0.5442 | [0.4990, 0.5944] |

- **Δ_CE = +0.2932 [+0.2056, +0.3682]** (pair-grouped bootstrap 2,000; G3 PASS, CI excludes 0).
- Δ_NI (ind − natural) = +0.0120 [−0.0581, +0.0789] (≈ 0); Δ_NP (natural − placebo) = +0.2811
  [+0.1449, +0.4008].
- Placebo ceiling: P(flip|placebo) = 0.5442 > 0.30 — the 0.30 gate was copied from the round-6
  paraphrase placebo and is not directly transferable to this "decision-irrelevant replacement"
  operationalization; the honest reading is a selective increment above a non-clean baseline, not
  all-or-nothing responsiveness.
- Round-6 replication diagnostic: our P(flip|natural) = 0.8253 vs frozen rev_flip_rate 0.8246
  (abs diff 0.0007, gate ≤ 0.15: True).

On the HC subset (n = 96, wrong = 8), S_natural AUROC 0.9624 [0.9253, 0.9908], S_ind 0.9830
[0.9537, 1.0000], S_combined 1.0000 [1.0000, 1.0000]; S_placebo is weak and anti-correlated in the
risk direction (0.3111 [0.1848, 0.4341]). Paired AUROC: S_ind − S_natural +0.0206 [−0.0187,
+0.0646] (CI includes 0); S_combined − S_natural +0.0376 [+0.0104, +0.0747] (CI excludes 0);
S_ind − S_placebo +0.6719 [+0.5526, +0.7963]. OOF logistic increment of S_ind over S_natural:
+0.0447 [+0.0146, +0.0842] (CI excludes 0). ρ(S_natural, S_ind) = 0.5664 [0.3557, 0.6945] —
the two axes share a responsiveness factor but are not the same signal. All HC statistics carry a
small-sample caveat (8 wrong items; exploratory).

**W2b (strict claim-only, 50 items / 25 pairs).** To remove any dependence on item polarity or the
mirror text, counter-evidence was generated from the claim alone: both directions in a single
label-blind call, with the counter-evidence assigned offline to oppose each item's gold; a matched
topic-relevant placebo was generated in the same call. Formal run: 50 items, valid 0.998.
Independence and leakage audits pass: token Jaccard vs the mirror median 0.185 / max 0.467; char
ratio max 0.549; LCS max 0.565; generation inputs are 30/30 claim-only templates; inference-prompt
leakage audit sha-matches 1.0 on 299 rebuilt prompts (packet = claim + single evidence unit);
placebo irrelevance 0.80; direction-compliance 0.783 overall (marginal; 0.80 on the assigned
counter-evidence segments). Headline flip rates (label-blind):

| quantity | estimate | 95% CI |
|---|---:|---:|
| P(flip | ind_strict) | 0.7258 | [0.6466, 0.8115] |
| P(flip | placebo_matched) | 0.5141 | [0.4600, 0.5772] |
| **Δ_CE (ind_strict − placebo)** | **+0.2118** | **[+0.1160, +0.3097]** |
| P(flip | natural, reused) | 0.8434 | [0.7177, 0.9478] (diagnostic) |

On the HC subset (n = 46–47 across scores; wrong = 3), S_ind_strict AUROC 0.624 [0.286,
0.856] (CI includes 0.5); S_natural 0.973 [0.912, 1.000]; RS_q 0.943 [0.860, 1.000]. Paired AUROC:
S_ind_strict − S_natural −0.349 [−0.714, −0.091]; S_ind_strict − RS_q −0.318 [−0.670, −0.106]
(both significantly negative). ρ(S_natural, S_ind_strict) = 0.033 [−0.044, 0.478] (≈ 0); OOF
**W2 strict (claim-only TARGET_SPEC, 100 items / 50 pairs).** A second, larger claim-only construction with the same offline gold assignment (formal run: 1,500 logical calls, valid 0.9593, completed 2026-09-15 06:47 after relay recovery; no protocol re-tuning) reproduces the behavioral result: Δ_CE = +0.0988 [+0.0300, +0.1681] (G3 PASS), with P(flip) natural 0.8253 / ind_strict 0.6567 / placebo 0.5579; the placebo baseline is again not clean (0.558 > 0.30) and the strict evidence flips significantly less than the natural mirror (Δ_NI = −0.1686 [−0.2689, −0.0611]). The predictive axis again fails to replicate: S_ind_strict HC AUROC 0.699 [0.465, 0.869] (CI includes 0.5, n = 72), paired ΔAUROC vs S_natural −0.257 [−0.500, −0.088], OOF increment +0.027 [0.000, 0.058] (CI touches 0), ρ(S_natural, S_ind_strict) 0.322 [0.128, 0.538]. See `ind_ce/analysis/ind_ce_strict_results.md`.

**Reading.** The independent-counter-evidence protocols partition the claim into two levels.
*Behavioral axis (established):* panels flip significantly more under decision-relevant
independent counter-evidence than under a matched placebo (Δ_CE = +0.212 in the 50-item strict run; +0.099 in the
100-item strict run; +0.293 label-coupled; all CIs exclude 0), and about as often as under the natural mirror in the label-coupled variant (Δ_NI = +0.012 [−0.058, +0.079] ≈ 0); the claim-only variants flip less than the mirror (e.g., Δ_NI = −0.169 [−0.269, −0.061] in the 100-item run).
Selective average responsiveness to decision-relevant counter-evidence is therefore not purely a
consequence of the byte-identical mirror construction. *Predictive axis (not established):* the
strict independent score carries no error-ranking increment over the natural-pair signal—its HC
AUROC includes chance (3 wrong items), its paired AUROC differences are significantly negative, and
it is nearly uncorrelated with the natural-pair score (ρ ≈ 0.03). The error-ranking contribution
therefore remains a *natural-pair consensus-fragility phenomenon*: the real paired sentence, which
is stronger and direction-cleaner than LLM-generated evidence, accounts for the predictive value.
All three protocols leave the placebo baseline non-clean (0.51–0.56), so the behavioral claim is a
selective increment over an irrelevant-perturbation baseline, not all-or-nothing responsiveness.
These are preregistered controls, reported with their audit boundaries; small HC samples (8 and 3
wrong items) keep the predictive-axis estimates wide.

### 4.8 Multi-axis stress profiles and λ curves (post-hoc [W3][W4])

Two additional stress axes exist in the frozen records—evidence removal (empty packet) and a
continuous stress-strength parameter λ—alongside the paraphrase and synthetic-reverse axes. A
round-7 post-hoc analysis (zero new calls) asks whether these axes add predictive information to
RS_q and whether they separate "correct but rigid" panels from truly wrong ones.

**Full-cohort reversal/removal signature.** The phase-3 finding that wrong consensus is *more rigid
under reversal* and *less stable under removal* replicates on the full 600-item cohort for both
models: correct vs wrong reversal flip rates differ by +0.748 [+0.685, +0.808] (Qwen HC) and
+0.674 [+0.629, +0.715] (Ling HC), while removal flip rates differ in the opposite direction
(−0.306 [−0.366, −0.240] Qwen HC; −0.249 [−0.291, −0.206] Ling HC). As risk representations, the
reversal axis dominates (AUROC 0.931/0.869) and the removal axis is a weaker, direction-opposite
axis (0.646 [0.608, 0.684] / 0.614 [0.587, 0.641]).

**No multi-axis increment.** No fixed-weight combination of {reversal, removal, paraphrase}
significantly exceeds RS_q in AUROC: Qwen best combination risk_z3 ΔAUROC = −0.012 [−0.027,
−0.000]; risk_rev_rem_para −0.022 [−0.038, −0.006]; Ling combinations are all significantly
negative (risk_rev_rem_para −0.024 [−0.038, −0.011]). Adding the removal axis to RS_q directly
makes the score significantly worse (risk_rsq_rem: Qwen −0.052 [−0.084, −0.021]; Ling −0.048
[−0.075, −0.025])—the removal axis contributes noise, not information, after the reversal axis. A
3-axis OOF logistic regression ties RS_q (Qwen −0.001 [−0.006, +0.004]; Ling −0.005 [−0.013,
+0.002], CIs include 0), indicating the three-axis feature set is near the ceiling already reached
by RS_q, not that the weights are suboptimal. Risk@80 shows no increment either.

**False-positive boundary (stated once).** The reversal-rigidity axis has a known false-positive
rate: among *correct* HC panels, `consensus-rigid` (rev_flip_rate ≤ 0.4) accounts for 13.9%
(Qwen 70/502) and 27.3% (Ling 124/455); `fully-rigid` (rev_flip_rate = 0) accounts for 9.2% and
22.4%. Neither the discrete removal axis (separation AUROC 0.501 [0.441, 0.557] Qwen, chance; 0.461
[0.434, 0.487] Ling, below chance; 0.500 for fully-rigid in both models) nor the paraphrase axis
(0.583 [0.521, 0.646] / 0.604 [0.567, 0.642], small partial separation) resolves these
false positives. RS_q is therefore a *ranking signal with a known false-positive rate*, not a
claim that only wrong consensus stays rigid. The multi-axis profile is reported as a diagnostic
figure (Figure 1), and the 3-axis OOF tie is reported as negative evidence that more axes do not
help.

**Continuous λ curves are a mechanism visualization, not a new feature.** On the frozen phase-3
subset (Qwen, 120 pairs / 240 items; HC 225 items, 22 wrong), per-item λ-stress curves
(stress-area, breakpoint, robustness radius) were reconstructed and verified against the frozen
phase-3 gate (reversal stress-area AUROC 0.948 [0.925, 0.969]). Relative to the binary reverse axis
(rev_flip_rate), the stress-area residual increment is 0.476 [0.429, 0.653] (point ≤ 0.5, CI
contains 0.5; paired diff +0.003 [−0.001, +0.009]) and breakpoint/radius paired diffs are
significantly negative (−0.022 [−0.038, −0.009]); relative to RS_q, the stress-area residual is
0.561 [0.494, 0.664] (CI contains 0.5) with paired diff −0.017 [−0.032, −0.002] (RS_q dominates).
The curve's interior shape (λ ∈ [0.2, 0.8]) carries no independent information (increment 0.533
[0.466, 0.602], CI contains 0.5). Mechanistically, 78% (159/203) of correct consensus reach
rev_flip_rate = 1.0 under natural counter-evidence while wrong consensus are all ≤ 0.2; the
continuous curve is a smoothed, monotone view of the binary flip endpoint. The λ curves are
therefore reported as an interpretability figure (Figure 2), not as a feature contribution; no
claim is made about Ling λ behavior, for which no λ records exist (not evaluable).

### 4.9 Reducibility: is RS_q a new signal or a re-weighted baseline?

To determine whether RS_q/BF_q is "just R_sym with different weights plus a paraphrase axis," we
conducted a label-free reducibility audit (zero new model calls; pair-grouped bootstrap, 2,000
replicates). Algebraically, the scores share only the natural-reversal flip axis (RS_q weight −0.5
via BF_q; R_sym weight −0.3 via reverse_inertia) and use different second axes (RS_q: paraphrase
faithfulness; R_sym: intervention_disagreement). "Just re-weighted" is therefore not literally
accurate; empirically the scores overlap substantially but are not strictly reducible (Table 11).

**Table 11: Reducibility of RS_q versus R_sym.**

| Quantity | Qwen [95% CI] | Ling [95% CI] |
|---|---|---|
| Spearman(RS_q, R_sym) | 0.822 [0.787, 0.845] | 0.859 [0.822, 0.886] |
| Incremental AUROC of RS_q residualized on R_sym | 0.874 [0.784, 0.931] | 0.787 [0.743, 0.831] |
| Paired AUROC diff RS_q - R_sym | +0.051 [0.028, 0.075] | +0.078 [0.053, 0.106] |

RS_q is strongly positively correlated with R_sym (0.82 / 0.86), but the two scores are far from
isomorphic. Residualizing RS_q on R_sym leaves a significant, moderate incremental AUROC (0.874
[0.784, 0.931] on Qwen; 0.787 [0.743, 0.831] on Ling; CI lower bounds well above 0.5), and the
paired AUROC advantage over R_sym is confirmed by the CIs for both models (+0.051 / +0.078).
Correlations with R_PI, intervention disagreement, vote agreement, and confidence are weak
(|rho| <= 0.35).

**Axis decomposition.** RS_q's signal is concentrated in the natural-reversal axis (Table 12). The
reverse axis alone reaches 0.931 [0.913, 0.947] on Qwen and 0.869 [0.846, 0.891] on Ling, compared
with RS_q's 0.943 / 0.896, whereas the paraphrase axis alone is near chance (0.599 [0.548, 0.652] /
0.581 [0.542, 0.621]). The paraphrase axis nevertheless contributes a small but statistically
significant increment (paired AUROC diff of RS_q over the reverse axis: 0.012 [0.002, 0.022] /
0.027 [0.013, 0.042], with both CIs excluding 0); its residual incremental AUROC is only 0.284
[0.194, 0.378] / 0.317 [0.257, 0.384], below 0.5 and direction-unstable. R_sym (0.892 [0.861,
0.921] / 0.818 [0.787, 0.847]) is *lower* than the reverse axis alone because its
intervention-disagreement component (weight 0.7; itself AUROC only about 0.536 / 0.475) reduces the
score. RS_q's advantage over R_sym therefore reflects adding the paraphrase axis and removing
intervention_disagreement.

**Table 12: Axis decomposition (pair-grouped 95% CI).**

| Quantity | Qwen [95% CI] | Ling [95% CI] |
|---|---|---|
| RS_q AUROC | 0.943 [0.924, 0.960] | 0.896 [0.875, 0.917] |
| Reverse axis (-rev_flip_rate) AUROC | 0.931 [0.913, 0.947] | 0.869 [0.846, 0.891] |
| Paraphrase axis (-bf_paraphrase) AUROC | 0.599 [0.548, 0.652] | 0.581 [0.542, 0.621] |
| Paired diff RS_q - reverse axis | 0.012 [0.002, 0.022] | 0.027 [0.013, 0.042] |
| Paired diff RS_q - paraphrase axis | 0.344 [0.295, 0.393] | 0.316 [0.282, 0.349] |
| Residual incremental AUROC of RS_q over reverse axis | 0.284 [0.194, 0.378] | 0.317 [0.257, 0.384] |
| Residual incremental AUROC of RS_q over paraphrase axis | 0.921 [0.901, 0.941] | 0.855 [0.828, 0.880] |

RS_q is *partially reducible* to the natural-reversal axis that R_sym already captures at weight
0.3; it is not an independent new heuristic. Errors are correlated with near-duplicate natural
pairs, and the natural counter-evidence axis can pre-outcome-predict consensus errors; RS_q's
relative gain over R_sym is the small paraphrase-axis increment (paired AUROC +0.05 / +0.08, both
significant). Combined with §4.6, the mechanism statement is: *the predictive value lives in the
natural-pair reversal structure, with a small paraphrase-axis increment*.

### 4.10 Label balance: SUPPORTS vs REFUTES

Because a label-symmetric construction does not imply symmetric error rates (Qwen: 2.5% on
SUPPORTS vs 20.4% on REFUTES; Ling: 4.4% vs 38.1%; an 8.3–8.7x ratio), we report per-label
AUROC/Risk@80 as the primary view (Table 13). The pooled estimate is interpreted as
REFUTES-dominated by error composition: REFUTES accounts for 89.2% / 89.1% of the HC error mass and
89.3% / 88.9% of the pooled AUROC concordant mass on Qwen / Ling.

**Table 13: Per-label AUROC / Risk@80 (label-internal Risk@80).**

| Model | Label | n | Wrong (rate) | AUROC [95% CI] | Risk@80 [95% CI] (label-internal) |
|---|---|---|---|---|---|
| Qwen | SUPPORTS | 283 | 7 (2.5%) | 0.917 [0.819, 0.999] | 0.642 [0.165, 1.000] |
| Qwen | REFUTES | 284 | 58 (20.4%) | 0.986 [0.973, 0.995] | 0.871 [0.687, 0.976] |
| Qwen | pooled | 567 | 65 (11.5%) | 0.943 [0.924, 0.960] | 0.846 [0.638, 0.981] |
| Ling | SUPPORTS | 296 | 13 (4.4%) | 0.881 [0.834, 0.928] | 0.807 [0.283, 0.904] |
| Ling | REFUTES | 278 | 106 (38.1%) | 0.957 [0.934, 0.977] | 0.338 [0.253, 0.432] |
| Ling | pooled | 574 | 119 (20.7%) | 0.896 [0.873, 0.916] | 0.422 [0.274, 0.591] |

The signal holds within both labels: both per-label AUROCs are significantly above chance in both
models (SUPPORTS 0.917 [0.819, 0.999] Qwen; 0.881 [0.834, 0.928] Ling). Post-hoc error-count-matched
pooling keeps pooled AUROC near 0.92 / 0.875. The pooled metric should be read as REFUTES-carried,
with label-stratified numbers as the primary view.

### 4.11 Large-model single point (gpt-6-astra)

As a single-point check with a larger GPT-class model, we ran the frozen protocol on the first 50
pairs (100 items × 5 agents × 5 conditions = 2,500 logical calls) through a relayed endpoint
(`https://openapi.center/v1`). The recorded model id matches `gpt-6-astra` in all 2,483 successful
records. Transport reliability was imperfect: 17/2,500 records (0.7%) are transport failures (HTTP
200 × 1,511; 429 × 826; 502 × 115; 400 × 125; 929 transport retries), while there were 0 parse
failures (no contract adaptation or JSON-exemplar escalation was needed). Two items lack complete
five-agent `original` answers and are excluded by the pre-existing Round-3 feature rule, which
requires all five originals to define consensus/agreement. This exclusion is label-free and does
not select on outcomes, leaving 98 items with complete features, of which 96 are HC with 8 wrong
(error rate 0.0833; 7 REFUTES + 1 SUPPORTS).

All within-model gates pass (Table 14): AUROC(RS_q, wrong | HC) = 0.969 [0.935, 0.995] (n = 96),
Risk@80 = 1.000 [0.836, 1.000], with all 8 wrong HC items in the highest-risk 20%; placebo
paraphrase flip is 0.0394; permutation is 0.9695 > 0.8942; and mechanism fidelity (correct minus
wrong natural-reversal fidelity) is 0.832 [0.745, 0.928] (correct n = 88, wrong n = 8). Frozen
Qwen/Ling RS_q scores transfer to gpt-6-astra's own errors at the aggregate level (Table 15), with
Qwen's score transferring more strongly than Ling's, consistent with item-level Spearman (Qwen
0.6787 vs Ling 0.3656).

**Table 14: gpt-6-astra within-model gates (n = 96 HC).**

| Gate | Observed | Verdict |
|---|---|---|
| G1 pipeline validity (>= 0.95) | 0.9932 (2,483/2,500) | PASS |
| G2 primary AUROC(RS_q, wrong\|HC) | 0.969 [0.935, 0.995] | PASS (CI lb 0.935 > 0.5) |
| G3 placebo (paraphrase flip) | 0.0394 | PASS |
| G4 permutation | 0.9695 > 0.8942 | PASS |
| G5 mechanism fidelity (correct-wrong bf_reverse) | 0.832 [0.745, 0.928] | PASS |
| Risk@80 (secondary) | 1.000 [0.836, 1.000] | all 8 wrong in highest-risk 20% |

**Table 15: Frozen score transfer to gpt-6-astra errors (n = 96; secondary evidence).**

| Source score | AUROC [95% CI] | Risk@80 [95% CI] | Spearman(src RS_q, gpt RS_q) |
|---|---|---|---|
| Qwen3.5-4B (round 3) | 0.838 [0.693, 0.950] | 0.684 [-0.120, 1.000] | 0.6787 |
| Ling-3.0-tiny (round 4) | 0.737 [0.568, 0.862] | 0.211 [-0.440, 0.844] | 0.3656 |

This is a 100-item single point, not a full-cohort estimate. The wrong-HC count is small (n = 8),
so the CIs are wide-tailed and support only the pre-registered CI-level gate (lower bound > 0.5)
and the direction of the mechanism. The model is a relay GPT-class model accessed through a
third-party proxy; its per-call model identity is recorded and matches `gpt-6-astra` in every
successful record, but the deployment is not a local first-party environment. No per-item ranking
equivalence across models or full-cohort large-model estimate is claimed.

### 4.12 Negative results / specificity

**BoolQ (specificity negative).** On a fresh balanced 50-yes/50-no BoolQ cohort (100 items; HC
85/100, 23 wrong, 27%), the frozen RS_q procedure yields AUROC 0.449 [0.308, 0.579]—direction-
reversed (below 0.5)—so the cross-dataset gate fails (G2/G3/G4/G6). The label subgroups diverge
(no: 0.073 [0.005, 0.169] vs yes: 0.745 [0.579, 0.889]), reproducing the answer-prior confound in
risk orientation. Risk@80 is 0.239 [-0.467, 0.348] (n.s.); permutation fails (0.449 < 0.612); and
RS_q is significantly *worse* than R_PI on BoolQ (paired diff -0.097 [-0.182, -0.009]). Placebo is
clean (0.052), and the pipeline is 100% valid. The diagnosis is that BoolQ lacks natural
counter-evidence, so the frozen oracle's reverse axis is a synthetic negation prefix, and the
synthetic-reversal axis is weak/non-separating. This is a **specificity result**, not a
contradiction: the risk signature is specifically "unresponsive to genuine natural evidence
reversal," rather than "unresponsive to any perturbation." No parser, oracle, or gate was changed;
the negative result is retained.

**FEVER (blocked at construction).** FEVER validation lacks the two-evidence contrast structure
required by the frozen oracle: verification found 0 same-claim pairs with both SUPPORTS and
REFUTES verdicts, and an offline semantic audit of 60 near-duplicate candidate pairs (162
judgments) passed 57/60 on "E_S supports C_S" but only 4/60 on "E_R refutes C_S." Thus, the paired
REFUTES evidence is almost always the same as, or near-identical to, the SUPPORTS evidence, with
only 1/60 pairs passing both. Running the protocol on these pairs would not implement the oracle as
specified. No agent calls were made on FEVER and no result is claimed; cross-dataset evaluation was
instead conducted on the balanced BoolQ split above.

## 5 Discussion

### 5.1 The regularity: natural-pair consensus fragility

The central empirical finding is a behavioral regularity computable before any outcome is
observed. Under the frozen VitaminC natural-pair protocol, a multi-agent panel that has already
reached high consensus (agreement ≥ 0.8) changes its answer when its evidence packet is replaced
with the natural counter-evidence—the evidence of the paired mirror item—when the consensus is
correct, and tends not to change it when the consensus is wrong. Reverse-axis responsiveness
(BF_reverse) separates these populations sharply: 0.844 (Qwen, derived) and 0.703 (Ling, reported)
on correct-consensus items, versus 0.095 and 0.029 on wrong-consensus items; on wrong-consensus
items, 90.5% (Qwen) and 97.1% (Ling) of agent calls retain the wrong answer under the natural
counter-evidence. This is the phenomenon that RS_q operationalizes, and it is pre-outcome: the
score is a function of frozen, label-free features and ranks errors with AUROC 0.943 [0.924, 0.960]
(Qwen) and 0.896 [0.873, 0.916] (Ling), with Risk@80 reductions of 0.846 [0.638, 0.981] and 0.422
[0.274, 0.591].

The round-7 stress tests make the interpretation precise rather than weakening the result.
First, the reverse axis is a deterministic re-encoding of paired answers: BF_reverse(i) is
identical to BF_reverse(j) on 99.65% / 97.39% of HC pairs (Spearman 0.996 / 0.995 [W1]), and
S_pair—using only the two original-condition answers—reconstructs the reverse axis exactly and
~98.7% / ~97.0% of RS_q's ranking power (§4.6). The ranking signal is therefore a *natural-pair
property*: it is produced by the alignment between the mirror gold and the panel's behavior under
the paired construction, not by an independent probe of a separately measurable trait. Second, the
independent-counter-evidence protocols (§4.7) show that the *average flip-rate response* is
selective to decision-relevant counter-evidence: panels flip significantly more under
independently generated, decision-relevant counter-evidence than under a matched placebo
(Δ_CE = +0.212 strict / +0.293 label-coupled, CIs exclude 0), with the label-coupled variant
flipping about as often as under the natural mirror (Δ_NI ≈ 0) while the claim-only variants
flip less (Δ_NI = −0.169 in the 100-item run). The mirror-equivalence objection is therefore answered on the
behavioral axis—responsiveness to decision-relevant evidence is not merely a reaction to the
mirror's byte identity—while the error-ranking contribution remains explicitly tied to the
natural-pair construction, where the strict independent variant provides no incremental ranking
power.

The regularity also has a second, weaker measurable axis: paraphrase stability. The paraphrase
condition tests the same item under meaning-preserving rewording against the agent's own original
answer and is not subject to the mirror reduction; paraphrase flip rates are low (0.038 Qwen;
0.061 Ling), so the reverse-axis asymmetry is not explained by general prompt instability.
Paraphrase faithfulness contributes a small but statistically significant increment over the
reverse axis alone (residual-increment AUROC 0.921 [0.901, 0.941] Qwen; 0.855 [0.828, 0.880] Ling;
paired AUROC increments 0.012 [0.002, 0.022] and 0.027 [0.013, 0.042]).

### 5.2 What transfers, and what does not

Two aspects transfer across model families. First, the *procedure*: the frozen Qwen item-level
RS_q, applied directly to Ling's own errors, achieves AUROC 0.723 [0.682, 0.765]—above chance by
CI, although below Ling's own within-model score (0.896; paired difference −0.173 [−0.217,
−0.130]). Second, the *aggregate signal*: the same within-model gate structure (permutation,
placebo, mechanism fidelity, primary AUROC) passes for Qwen3.5-4B and Ling-3.0-tiny on the full
600-item cohort and, as a single point, for a GPT-class relay model (gpt-6-astra) on a 100-item
subset (HC n = 96, 8 wrong; within-model AUROC 0.969 [0.935, 0.995]; frozen Qwen and Ling RS_q
transfer to its errors with AUROC 0.838 [0.693, 0.950] and 0.737 [0.568, 0.862]).

Item-level ranking does *not* transfer. Item-level Spearman correlation between Qwen and Ling RS_q
is only 0.496 on 574 shared HC items, and the correlations between each frozen score and the
gpt-6-astra score are 0.68 (Qwen) and 0.37 (Ling). The protocol exhibits partial cross-model
transfer, while item-level risk ranking remains substantially model-dependent—shared but
model-dependent behavioral structure. A risk score learned on one model family should be
recalibrated or re-validated for each family; the benchmark's value is to make that validation
inexpensive and standardized.

### 5.3 Selectivity to decision-relevant counter-evidence

The BoolQ result is an honest negative that supports the "natural counter-evidence" account:
BoolQ's reverse axis is a negation-prefix reversal rather than a natural evidence swap, and on
BoolQ the signal reverses direction (AUROC 0.449 [0.308, 0.579], permutation failing at 0.449 <
0.612). An axis that does not represent a genuine evidence-level contradiction does not produce the
regularity. The independent-counter-evidence protocols sharpen this account at the average-response
level: with evidence that genuinely contradicts the claim—generated independently of the mirror—the
flip-rate response significantly exceeds a matched
irrelevant placebo (Δ_CE > 0) and matches the natural mirror in the label-coupled variant
(Δ_NI ≈ 0; the claim-only variants flip less, Δ_NI = −0.169 in the 100-item run). Two qualifications keep this claim precise. The placebo baseline is
not clean (P(flip|placebo) ≈ 0.51–0.56): panels also change their answers on roughly half of
topic-relevant neutral replacements, so the effect is a *selective increment* of decision-relevant
counter-evidence over an irrelevant-perturbation baseline, not all-or-nothing responsiveness. And
the selectivity is established at the level of average flip rates; the strict independent score
does not rank consensus errors beyond the natural-pair signal (negative paired increments, ρ ≈
0.03, §4.7). The mechanism is therefore best stated as: *under the natural-pair construction,
error-prone consensus is disproportionately rigid to decision-relevant counter-evidence, and this
rigidity is selective—it is not explained by general perturbation instability and not purely an
artifact of the mirror's byte identity.*

### 5.4 Deployment angle

The pre-outcome nature of RS_q makes it directly applicable to selective routing or abstention: a
panel that has reached consensus but has a high risk score can be routed to additional
verification, an adjudicator, or abstention before its answer is released. The deployment story is
conditional on obtaining counter-evidence: the benchmark supplies it through natural pairs, whereas
a deployed system must *retrieve or generate* decision-relevant counter-evidence
((C, E) → retrieve/generate counter-evidence → stress test → risk estimate → selective routing).
The paper evaluates the value of the stress-test signal conditional on obtaining counter-evidence;
it does not claim to solve end-to-end counter-evidence retrieval. The strict independent-control
result bounds what a claim-only generation module can currently achieve: it produces evidence that
elicits a selective average flip response, but it does not yet provide an incremental error-ranking
signal over the natural-pair score, so a deployed generator should be validated as a ranking module
rather than assumed to substitute for the natural pair.

Two cost facts constrain the deployment claim. The main score requires 10 probe calls after the 5
consensus-formation calls per item (15 score-relevant calls total); the 10 auxiliary diagnostic
calls of the full protocol are not needed for scoring. A cheaper 5-call reversal-only probe
reaches AUROC 0.931 [0.913, 0.948] (Qwen) and 0.869 [0.847, 0.891] (Ling) but is statistically
significantly worse than RS_q in paired AUROC difference (Qwen +0.012 [0.002, 0.023]; Ling +0.027
[0.013, 0.042]); under the pre-registered decision rule, "5 calls ≈ 10 calls" is not claimed. The
statistically lossless cheaper point is the 10-call probe itself (score-identical by construction,
paired difference 0.000 [0.000, 0.000]). Token accounting from frozen records makes the trade-off
concrete: mean total tokens/item are 10,196 (Qwen) and 10,354 (Ling) for the full 25-call protocol,
versus 2,154 and 2,176 for the 5-call reversal probe—roughly a fifth of the tokens at a small but
significant AUROC cost. Adding synthetic-reverse calls dilutes the signal (Qwen 0.832; Ling
0.753), reinforcing that the natural-reverse axis is the core carrier and that additional calls are
not monotonically beneficial.

## 6 Limitations

The following boundaries bound the positive results; failed and blocked records from the project
history are preserved in the repository and are not relabeled.

1. **The error-ranking signal is a natural-pair property.** BF_reverse is a deterministic,
   label-aligned re-encoding of the original answer, the mirror-item answer, and the frozen paired
   gold (View Identity verified on 99.97% / 99.63% of agent calls; 3,000/3,000 prompts byte-identical
   [W1]). A paired-prediction diagnostic reconstructs the reverse axis exactly and ~98.7% / ~97.0%
   of RS_q's ranking power from the two original-condition answers alone (§4.6). The claim is
   therefore *descriptive and predictive under natural-pair construction*, not a measurement of a
   latent rigidity trait. The paraphrase axis is the only component not subject to this reduction,
   and it alone discriminates only weakly (per-axis AUROC 0.599/0.581).
2. **Independent counter-evidence: behavioral selectivity, no independent ranking signal.** The
   strict claim-only controls (50 items Δ_CE +0.212; 100 items Δ_CE +0.099) and the
   label-coupled control (98 items, +0.293) all show Δ_CE > 0
   with CIs excluding 0, but the placebo baseline is not clean (P(flip|placebo) = 0.514 / 0.544), so
   the behavioral claim is a selective increment, not all-or-nothing responsiveness. The strict
   independent score carries no error-ranking increment over the natural-pair signal: HC AUROC 0.624
   [0.286, 0.856] (3 wrong items), paired ΔAUROC −0.349 [−0.714, −0.091] vs S_natural and −0.318
   [−0.670, −0.106] vs RS_q, ρ ≈ 0.03, OOF increment +0.004 [−0.074, 0.047]. The label-coupled HC
   estimate (8 wrong items) shows a positive OOF increment (+0.0447 [+0.0146, +0.0842]) but a paired
   AUROC increment with CI including 0; both estimates are small-sample and exploratory.
   Direction-compliance in the strict generation audit was marginal (0.783 overall; 0.80 on the
   assigned counter-evidence segments). An independently deployable counter-evidence-generation +
   ranking pipeline is future work.
3. **A single positive dataset, plus a single GPT-class point.** The positive evidence comes from
   one dataset (VitaminC natural pairs, 600 items, label-symmetric by construction). The large-model
   evidence is a single point: 100 items (98 with complete features; HC n = 96, 8 wrong consensus
   items), run through a third-party relay (openapi.center) for a GPT-class model (gpt-6-astra),
   with 2,483/2,500 valid calls (0 parse failures; 17 transport failures). The within-model AUROC
   0.969 [0.935, 0.995] and the transfer AUROCs (0.838/0.737) rest on only 8 wrong items, so the CIs
   are wide and the point is indicative rather than a full-cohort estimate. Cross-dataset generality
   is not claimed; the BoolQ negation-prefix control reverses the signal (AUROC 0.449), and FEVER
   has no natural pairs to evaluate.
4. **Label asymmetry.** Construction is label-symmetric, but error rates are not: Qwen errors on
   7/283 SUPPORTS HC items (2.5% [1.2%, 5.0%]) versus 58/284 REFUTES items (20.4% [16.1%, 25.5%]);
   Ling errors on 13/296 (4.4% [2.6%, 7.4%]) versus 106/278 (38.1% [32.6%, 44.0%]). About 89% of
   pooled errors are REFUTES, and the pooled AUROC (0.943/0.896) is a REFUTES-dominated composite;
   per-label AUROCs are both above chance in both models, and per-label numbers are the primary view.
5. **Multi-axis and λ results are post-hoc and bounded.** No fixed-weight multi-axis combination
   exceeds RS_q (OOF 3-axis logistic ties: Qwen −0.001 [−0.006, +0.004]; Ling −0.005 [−0.013,
   +0.002]), and the removal axis does not resolve the reversal axis's false positives
   (consensus-rigid among correct panels: 13.9% Qwen / 27.3% Ling; removal separation at chance or
   below). λ-curve reducibility is evaluated only on the Qwen phase-3 subset (120 pairs; 22 wrong);
   Ling λ behavior is not evaluable (no λ records).
6. **Ling contract adaptation (preregistered).** Ling-3.0-tiny did not self-report `agent_id`; the
   dispatcher binds the frozen agent index/persona/partition server-side, and the parser validates
   the answer, confidence, and cited evidence IDs with a frozen JSON exemplar in every prompt. This
   adaptation was preregistered before the Ling run, changes no evidence, oracle, condition, or
   score field, and the run achieved 15,000/15,000 valid calls. It is a response-format
   accommodation whose effect cannot be fully separated from model behavior.
7. **Cost/benefit is real but small.** The 5-call reversal probe is cheaper (about one fifth of the
   tokens) but statistically significantly worse than RS_q in paired AUROC (Qwen +0.012 [0.002,
   0.023]; Ling +0.027 [0.013, 0.042]); the magnitude of the gap is small. The 10-call probe is
   lossless by construction (identical item-level scores), so the honest cost summary is "10 probe
   calls are lossless; 5 calls are cheaper but slightly weaker," not "5 calls ≈ 10 calls."
8. **No causal identification; adapted baselines; no multiplicity correction.** The evidence is
   correlational and pre-outcome; no claim is made that counter-evidence causes error or that
   responsiveness causes correctness. External baselines (Self-consistency, SelfCheckGPT, binary
   semantic entropy, calibrated confidence) are matched-budget adapted proxies—binary/answer-match
   variants without the original pipelines—not reproductions of the cited papers' numbers. Paired
   pair-grouped bootstrap CIs are the primary inference; no formal family-wise correction is applied
   across the leaderboard.

## 7 Conclusion

We identify and test a pre-outcome empirical regularity in multi-agent consensus: consensus items
that fail to respond appropriately to decision-relevant counter-evidence are substantially more
likely to be incorrect. The paper contributes (C1) the phenomenon itself—wrong consensus is
disproportionately rigid to natural counter-evidence (correct vs wrong reversal fidelity 0.844/0.703
vs 0.095/0.029; RS_q AUROC 0.943 [0.924, 0.960] Qwen and 0.896 [0.873, 0.916] Ling, Risk@80 0.846
[0.638, 0.981] and 0.422 [0.274, 0.591]); (C2) CST-Bench, a pre-outcome stress-test protocol with
explicit call accounting (5 consensus-formation + 10 main probe + 10 auxiliary diagnostic calls;
the main score requires 10 probe calls after consensus formation), an outcome firewall, frozen
cohort, preregistered gates, and pair-grouped bootstrap evaluation; and (C3) a rigorous validation
with label-stratified metrics, placebo/permutation/reducibility controls, matched-budget adapted
baselines, cross-model procedure transfer (Qwen→Ling AUROC 0.723 [0.682, 0.765]), a GPT-class
single point (0.969 [0.935, 0.995]), and round-7 stress tests.

The stress tests sharpen, rather than dissolve, the contribution. A paired-prediction diagnostic
shows the ranking signal is a natural-pair property (S_pair reconstructs ~98.7%/97.0% of RS_q's
ranking power from the two original-condition answers alone), so the paper reports responsiveness
as a descriptive, pre-outcome behavioral regularity under natural-pair construction—not as a
latent trait or a causal mechanism. Independent-counter-evidence controls show that selective
average responsiveness to decision-relevant counter-evidence is not purely a mirror artifact
(Δ_CE = +0.212 strict [+0.116, +0.310]; +0.293 label-coupled [+0.206, +0.368]), while the strict
independent variant does not establish an independently deployable error-ranking signal—the natural
pair itself carries the predictive value. Multi-axis and λ-curve analyses confirm that RS_q is near
the ceiling of the available feature set (OOF 3-axis tie) and that the continuous stress curve is a
mechanism visualization rather than an additional signal, with a known false-positive rate of the
rigidity axis (13.9%/27.3% of correct panels are consensus-rigid). The practical takeaway is
operational and conditional: selective routing or abstention can use a cheap, outcome-blind
responsiveness probe—10 probe calls/item as the lossless point, 5 calls/item as a slightly weaker
but substantially cheaper alternative—once decision-relevant counter-evidence is obtained; the
paper does not claim to solve end-to-end counter-evidence retrieval, and claims remain bounded to
two small open-weight models, one GPT-class single point, and one dataset.

## 8 Figures (round-7 diagnostic; final rendering pending)

- **Figure 1 — Multi-axis pressure profile (post-hoc [W3]).**
  Two-panel scatter (Qwen, Ling; HC subset) of reversal rigidity (1 − rev_flip_rate) versus
  removal instability (rem_flip_rate), colored by consensus correctness; rigid regions marked.
  Shows the reproducible reverse signature (wrong: rigid to reversal, unstable to removal) and the
  overlapping correct-rigid population.
  Source: `consensus_stress/round7/stress_profile/figures/axis_profile_scatter.png`.
- **Figure 2 — Continuous λ stress curves (post-hoc [W4]).**
  Qwen phase-3 subset: mean agent flip probability versus λ (fraction of units stressed) for
  correct-rigid vs wrong-rigid panels, on the removal and reversal axes. Mechanism visualization
  only; the curves are reducible to the binary flip endpoint (no predictive increment).
  Source: `consensus_stress/round7/stress_profile/figures/lambda_separation.png`.

## 9 Round-7 provenance

All round-7 statements in this draft are traceable to:

| Topic | Artifact |
|---|---|
| Mirror equivalence, leakage audit, S_pair diagnostic | `round7/audit/{mirror_audit,s_pair_diagnostic,leakage_audit}.md` + `SUMMARY.md` |
| Independent counter-evidence (label-coupled) | `round7/ind_ce/analysis/ind_ce_results.md` + `decision.md` + `SUMMARY.md` |
| Strict independent counter-evidence (claim-only) | `round7/ind_ce_strict/decision.md` + `SUMMARY.md` |
| Multi-axis profiles, false-positive decomposition | `round7/stress_profile/stress_profile_analysis.md` + `decision.md` + `SUMMARY.md` |
| λ-curve reducibility | `round7/lambda_features/lambda_features_analysis.md` + `decision.md` + `SUMMARY.md` |

All frozen round-3/4/5/6 numbers are unchanged from draft v4; round-7 additions are labeled
post-hoc/exploratory where they are not preregistered protocol results (W2 and W2b protocols were
preregistered before their calls; the S_pair, multi-axis, and λ analyses are post-hoc on frozen
records). No number was added without a CI or an explicit point estimate from the listed artifacts;
no new claim was introduced beyond the workstream decisions (W1–W4 + W2b).
