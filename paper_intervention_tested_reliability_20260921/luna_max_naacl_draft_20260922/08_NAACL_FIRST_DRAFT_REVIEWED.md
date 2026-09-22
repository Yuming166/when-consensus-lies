# Intervention-Tested Reliability: From Directional Consensus Stress Tests to Executable Counterfactual Diagnostics

## Abstract

Reliability evaluation can be more informative when, in settings with an independently specified intervention consequence, it tests whether a system responds in the expected direction or magnitude rather than treating any output change or high confidence as evidence of reliability. We call this property **expected-response fidelity** and distinguish it from generic sensitivity, which records only whether an output changes. We develop and bound this idea through Consensus Stress Testing (CST), a bounded S&P portability test, and Program-Executable Counterfactual Reliability (PECR). On frozen VitaminC cohorts, the direction-sensitive score \(RS_q=-BF_q\) ranked incorrect high-consensus decisions with AUROC \(0.943\,[0.924,0.960]\), confirmed at \(0.912\,[0.848,0.973]\) on 50 pairs. Round10 narrowed the interpretation: consensus-opposing independent evidence changed wrong consensus in \(35/37=0.946\) cases, with direction contrast \(+0.44\,[0.24,0.65]\). The S&P branch marks a portability boundary: on 469 DEV units, B6 reached \(0.6320\,[0.5546,0.7051]\), B8 reached \(0.6177\,[0.5430,0.6950]\), and B8–B6 was \(-0.0143\,[-0.0560,0.0287]\). PECR uses a gold executable FinQA program to transform a uniquely mapped operand and score transformed-gold fidelity. On 126 source-deduplicated items from 182 structurally eligible rows in the 883-row official DEV split, full CEF/S2 AUROC was \(0.9008/0.8317\) for Qwen3.5-4B and \(0.8477/0.8379\) for Ling-3.0-tiny; S2 uses three rather than five calls per item. On 198 ConvFinQA DEV items, a Qwen TRAIN-fit response-rich student estimated the two unobserved stronger-probe fidelity outcomes, with head AUROCs \(\operatorname{AUROC}(p_{-2},F_{-2})=0.8754\) and \(\operatorname{AUROC}(p_{+2},F_{+2})=0.8407\), and raised Qwen S2 from \(0.6508\) to \(0.7474\) (\(\Delta=+0.0966\), item-bootstrap 95% CI \([+0.0183,+0.1740]\)) with three deployment calls per item. These results support a bounded diagnostic principle, not universal reasoning reliability, hidden-state recovery, causal competence, or an AUROC upper-bound interpretation of full CEF.

## 1. Introduction

A reliability measure is most useful before the outcome is observed, when a system or decision-maker must still decide whether to trust an answer. Yet a model can be highly confident, agree with other responses, or react strongly to a perturbation while remaining wrong. Confidence- and agreement-based reliability signals are therefore useful but incomplete [CITATION NEEDED]. We study a complementary question: can a controlled intervention on the evidence reveal whether an original answer is likely to be correct without using the eventual correctness label?

The central distinction is between **generic sensitivity** and **expected-response fidelity**. Let \(x\) denote the original evidence, \(r_0\) the model’s original response, and \(T_k(x)\) an intervention producing response \(r_k\). A generic sensitivity score records only whether \(r_k\neq r_0\). This treats an appropriate revision, an irrelevant flip, and a response to a malformed perturbation as instances of the same behavior. Expected-response fidelity instead asks whether \(r_k\) matches the response independently implied by the intervention semantics, including its expected direction or magnitude when that consequence is known. The intervention must therefore be outcome-blind and semantically controlled: its construction cannot depend on whether the original answer is correct, and its expected consequence must be specified independently of the model’s response.

We develop this principle through three connected evidence lines. First, Consensus Stress Testing (CST) applies outcome-blind evidence interventions to high-consensus decisions. On frozen VitaminC natural-pair cohorts, the direction-sensitive score \(RS_q=-BF_q\) ranked incorrect high-consensus decisions beyond confidence, agreement, and frozen provenance comparisons. The paper-scale AUROC was \(0.943\,[0.924,0.960]\), and a separate 50-pair confirmation reached \(0.912\,[0.848,0.973]\). Thus, an intervention response can carry correctness information even when the original decision has strong consensus.

CST also establishes an interpretation boundary. An initial account could treat incorrect consensus as direction-free rigidity: perhaps wrong groups simply resist any new evidence. Round10 provides evidence against that explanation within the frozen contrast. Consensus-opposing independent evidence changed wrong consensus in \(35/37=0.946\) cases, while the reported direction contrast was \(+0.44\,[0.24,0.65]\). Consensus-agreeing or no-new-information evidence rarely produced the same change. The surviving result is narrower: a directionless flip rate is under-specified. What matters is whether the system responds in the direction implied by the intervention. CST therefore provides evidence for directional response fidelity, not hidden group-state recovery or a causal account of group reasoning.

Second, we test the portability of behavioral intervention signals in a bounded S&P 500 branch. The setting passed a structural-hardness gate, with static AUROCs of \(0.6040\) for Ling-3.0-tiny and \(0.5569\) for the frozen Hy model condition. In the finalized comparison on 469 DEV units, the simpler B6 raw-trajectory feature reached \(0.6320\,[0.5546,0.7051]\), while the B8 behavioral-state candidate reached \(0.6177\,[0.5430,0.6950]\). The difference, B8–B6, was \(-0.0143\,[-0.0560,0.0287]\), leading to the operational decision `KEEP_B6_NO_ESCALATION`. This negative branch is important because it prevents a general portability claim: measurable behavioral sensitivity is not automatically a transferable reliability predictor. It does not show that financial forecasting is impossible; it shows that response magnitude alone need not provide stable incremental correctness information when intervention semantics are difficult to identify.

This boundary motivates a more controlled setting. Program-Executable Counterfactual Reliability (PECR) uses a gold executable program from FinQA [CITATION NEEDED]. For a structurally eligible item, the method transforms a uniquely mapped operand, reruns the gold program, and computes the transformed gold answer from the frozen gold program independently of the model response. The model is then evaluated in a transformed world whose expected answer is externally specified. Full Counterfactual Execution Fidelity (CEF) aggregates transformed-gold execution success across the valid probes, while the sparse score S2 averages the two frozen \(k=-1,+1\) probes. Both scores measure transformed-gold fidelity. They are not measurements of latent reasoning, causal competence, or absolute counterfactual ability.

The eligibility boundary is substantive. The official FinQA DEV split contains 883 rows, but the executable construction reduced this to 182 structurally eligible rows and 126 source-deduplicated evaluation items. The terminal-operation counts were add \(8\), divide \(105\), multiply \(5\), and subtract \(8\). On these 126 items, Qwen3.5-4B reached full CEF AUROC \(0.9008\,[0.8411,0.9517]\) and S2 AUROC \(0.8317\,[0.7555,0.9020]\). Ling-3.0-tiny reached \(0.8477\,[0.7619,0.9256]\) and \(0.8379\,[0.7504,0.9182]\), respectively. The corresponding confidence-based AUROCs were near chance, \(0.5181\) and \(0.5412\). These results support an item-level diagnostic association with original correctness even though they do not establish strong absolute counterfactual competence.

The sparse score also provides a concrete cost–information tradeoff. Full CEF uses five calls per item: the original call plus four counterfactual probes. S2 uses three calls: the original call plus the two fixed \(k=-1,+1\) probes. Under this protocol, the reduction is 40% in total calls and 50% in counterfactual calls. On 200-item TRAIN controls, S2 retained \(0.8079\,[0.6920,0.9081]\) of Qwen’s full-CEF gain and \(0.8122\,[0.6573,0.9420]\) of Ling’s. These are secondary retention ratios computed against the same-cohort confidence-based AUROC, not equivalence claims. On official DEV, the full-CEF–S2 gaps were \(0.0691\) for Qwen and \(0.0098\) for Ling, illustrating that a lower-cost diagnostic can preserve substantial ranking information while still losing some reference-score resolution.

We further examine whether the executable diagnostic transfers across financial reasoning formats. On 198 ConvFinQA DEV items [CITATION NEEDED], Qwen’s S2 and full-CEF AUROCs were \(0.6508\,[0.5707,0.7353]\) and \(0.6870\,[0.5954,0.7822]\). Ling’s corresponding values were \(0.8275\,[0.6525,0.9983]\) and \(0.8251\,[0.6456,0.9988]\). The reported global and within-operation permutation tests both gave \(p=0.0002\). The Ling estimate requires important qualification: only \(9/198\) items were originally correct, schema validity was \(79.1\%\), and numeric validity was \(57.7\%\). We therefore treat this result as a cross-task PECR replication with explicit validity and sample-composition limits, not as a universal transfer claim.

The strongest new result concerns missing-probe imputation. On frozen ConvFinQA Qwen DEV, a Qwen TRAIN-fit response-rich student estimated the two unobserved stronger-probe fidelity outcomes. The head AUROCs for predicting those fidelity labels were \(\operatorname{AUROC}(p_{-2},F_{-2})=0.8754\) and \(\operatorname{AUROC}(p_{+2},F_{+2})=0.8407\). Replacing those unexecuted probes with the imputed values raised Qwen’s S2 from \(0.6508\) to \(0.7474\), a difference of \(+0.0966\). The item-bootstrap 95% CI was \([+0.0183,+0.1740]\), and the source-group CI was \([+0.0190,+0.1736]\), with only three deployment calls per item. This is a result about imputing a missing diagnostic, not about improving the model’s underlying task accuracy. It should not be described as surpassing a teacher, and full discrete CEF is a reference score rather than an AUROC upper bound.

Taken together, the paper makes a bounded argument. First, reliability evaluation should score expected behavior under a controlled intervention rather than generic output change alone. Second, CST demonstrates this distinction in evidence interventions: the useful signal is directional, while the S&P branch shows that behavioral sensitivity does not automatically transfer across domains. Third, PECR instantiates the principle in a setting where a gold program independently determines the transformed answer, yielding a cross-model sparse diagnostic and a lower-call missing-probe extension. The evidence remains limited to two model families, structurally eligible financial-reasoning items, and the reported intervention protocols. We do not claim universal reasoning reliability, hidden-state recovery, causal competence, or broad portability beyond settings in which the expected response can be independently specified.


## 2. Intervention-Tested Reliability Framework

### 2.1 Outcome-blind interventions

We define reliability evaluation around controlled interventions rather than around a single unperturbed response. Let \(x\) denote an original evidence context, question, prompt, or structured decision instance, and let \(f\) denote a model or panel. The original decision is

\[
d=f(x).
\]

Let \(C\in\{0,1\}\) indicate whether \(d\) is correct under the externally defined outcome or gold answer. The correctness label is used only after the intervention responses and their derived features have been frozen; it is not exposed while the intervention responses are generated.

For an intervention indexed by \(k\), let

\[
x^{(k)}=T_k(x), \qquad r_k=f\bigl(x^{(k)}\bigr).
\]

The transformation \(T_k\) is specified independently of the model response and is logged before outcome information is merged. The index \(k\) can identify an evidence stress direction, a replacement condition, an operand transformation, or a null control. The resulting response pattern is used to construct a diagnostic score \(q(x)\), which is evaluated by how well it ranks the original correctness target \(C\).

This definition makes intervention-tested reliability a behavioral, task-scoped property. It does not assert universal reasoning reliability, recovery of a hidden state, or correctness under interventions that were not specified and tested.

### 2.2 Behavioral sensitivity and expected-response fidelity

The weakest intervention observable is behavioral sensitivity: whether the response changes at all. We define

\[
B_k=\mathbf{1}[r_k\neq d].
\]

For structured or numerical outputs, the comparison may use the task's frozen response representation, but the semantic question remains whether the model moved. \(B_k\) therefore answers:

> Did the system respond differently after the intervention?

It does not answer whether the response was warranted. A response can change because of relevant evidence, an irrelevant distractor, a formatting change, or a malformed input.

Expected-response fidelity adds a pre-specified criterion for what the response should do. Let \(\mathcal{E}_k\) be a predicate that encodes the expected consequence of intervention \(T_k\), fixed independently of \(C\) and of the model response. We define

\[
F_k=\mathbf{1}\!\left[\mathcal{E}_k(d,r_k,T_k)=1\right].
\]

When the expected response is an independently computable target \(y_k^\star\), this becomes

\[
F_k=\mathbf{1}\!\left[\kappa(r_k)=\kappa(y_k^\star)\right],
\]

where \(\kappa\) is the frozen answer or decision canonicalization function.

For a scalar response coordinate \(v(\cdot)\), an expected directional change can be represented by \(s_k\in\{-1,+1\}\):

\[
F_k^{\mathrm{dir}}
=
\mathbf{1}\!\left[
\operatorname{sign}\!\left(v(r_k)-v(d)\right)=s_k
\right].
\]

If the intervention specifies an expected change \(\Delta_k^\star\), the corresponding magnitude error is

\[
e_k^{\mathrm{mag}}
=
\left|
\left(v(r_k)-v(d)\right)-\Delta_k^\star
\right|.
\]

A binary magnitude-fidelity criterion can be obtained from a tolerance fixed before outcome merging. The important distinction is that fidelity is evaluated against an independently specified consequence; it is not inferred from the fact that the response changed.

Thus, the framework forms a hierarchy:

\[
\text{response change }(B_k)
\;\longrightarrow\;
\text{direction or magnitude agreement }(F_k^{\mathrm{dir}})
\;\longrightarrow\;
\text{exact executable agreement }(F_k).
\]

This is an organizing principle for empirical diagnostics, not a claim that every stronger definition is uniformly better on every benchmark.

### 2.3 Reliability as response to an expected consequence

An intervention-tested reliability score combines response features across a fixed intervention family:

\[
q(x)=\Phi\left(\{B_k,F_k\}_{k\in\mathcal{K}}\right),
\]

where \(\Phi\) is fixed before evaluating the original correctness label. The score is useful when higher or lower values rank \(C\) more effectively than a baseline such as confidence alone. The score is not interpreted as a calibrated probability unless separately established.

The framework distinguishes two non-executable cases from the executable PECR case below.

**Consensus stress testing.** In CST, \(d\) is an initial consensus decision and \(r_k\) is the consensus after controlled evidence stress. Independent counter-evidence supplies an expected direction relative to the initial consensus. The resulting diagnostic tests whether the consensus responds in the expected direction, rather than merely whether it changes. This is a behavioral test of response direction; it does not require or imply recovery of a hidden group state.

**Generic sensitivity testing.** In the bounded S&P branch, \(B_k\) is the primary observable. The analysis therefore tests whether sensitivity at one intervention transfers as a reliability predictor at another, rather than assuming that any measurable response is informative. The frozen branch retains the \(B_6\) diagnostic and does not escalate to \(B_8\) solely on the basis of sensitivity.

**Executable counterfactual testing.** PECR supplies an independently computed transformed answer. It therefore instantiates expected-response fidelity with an exact transformed-gold criterion rather than with output movement alone.

## 3. Program-Executable Counterfactual Reliability

### 3.1 Transformed executable worlds

Program-Executable Counterfactual Reliability (PECR) applies the framework to numerical reasoning items for which a frozen gold program can be executed after a controlled operand transformation.

For an eligible item, let \(x\) be the original model input, \(P\) the executable gold program, and

\[
d=f(x)
\]

the original model answer. The construction trace selects one uniquely mapped operand \(a\). A frozen transformation rule changes only this operand and creates four transformed executable worlds,

\[
x^{(-2)},\quad x^{(-1)},\quad x^{(+1)},\quad x^{(+2)}.
\]

The evidence or report text and the model-facing prompt are regenerated deterministically from each transformed input. The gold program is executed independently on every valid world:

\[
y_k^{\mathrm{CF}}=P\!\left(x^{(k)}\right),
\qquad
k\in\{-2,-1,+1,+2\}.
\]

The model is then queried on the transformed prompt and returns

\[
r_k=f\!\left(x^{(k)}\right).
\]

The world-level executable fidelity indicator is

\[
F_k
=
\mathbf{1}\!\left[
\kappa(r_k)=\kappa\!\left(y_k^{\mathrm{CF}}\right)
\right].
\]

Here, the transformed gold is determined by the input transformation and the executable program, not by inspecting the model response. The original correctness target \(C\) is merged only after the model calls, transformed answers, and reliability features have been frozen.

PECR is consequently narrower than free-form semantic perturbation. It measures whether a model produces the independently computed answer for a finite set of transformed executable worlds. It is a behavioral diagnostic of transformed-gold fidelity, not a measurement of latent reasoning, causal competence, or absolute counterfactual competence.

### 3.2 Structural eligibility

The construction is output-blind and fails closed. An item is structurally eligible only when the frozen trace establishes all of the following:

- all program operations are supported by the frozen operator set;
- the intervention operand has a unique mapping to the input;
- the original program execution is deterministic and consistent with the gold answer under the frozen numeric rules;
- all required transformed worlds are deterministic and valid;
- count-like values remain integer-valued under the transformations;
- no transformed divisor is near zero;
- intermediate values and final results remain within the frozen numeric bounds;
- the transformation does not introduce a unit or surface-generation ambiguity that erases the intended change.

Invalid worlds are excluded during eligibility construction rather than silently converted into failures. Invalid model responses, including missing answers, malformed schemas, and non-finite values, are scored as invalid and are not repaired into favorable outcomes.

The official FinQA DEV cohort makes the coverage restriction explicit. The initial 883 rows yield 182 structurally eligible rows, and source deduplication produces 126 evaluation items. The final source-deduplicated operation counts are:

\[
\text{add}=8,\qquad
\text{divide}=105,\qquad
\text{multiply}=5,\qquad
\text{subtract}=8.
\]

All PECR claims are therefore scoped to the eligible, source-deduplicated cohort rather than to all FinQA items.

### 3.3 Full CEF and sparse S2

For an item with all four valid transformed worlds, full Counterfactual Execution Fidelity (CEF) is

\[
\operatorname{CEF}(x)
=
\frac{
F_{-2}+F_{-1}+F_{+1}+F_{+2}
}{4}.
\]

Although the original response \(d\) is not included in this average, it is still required to establish original correctness and to construct response-derived features. Full CEF therefore requires one original call and four counterfactual calls, or five calls per item.

The frozen sparse score \(S2\) uses the two fixed mild probes:

\[
S2(x)
=
\frac{F_{-1}+F_{+1}}{2}.
\]

S2 uses the original call and the \(-1\) and \(+1\) calls, for three calls per item. Relative to full CEF, this is a planned 40% reduction in total calls and a 50% reduction in counterfactual calls.

Both scores are reliability diagnostics for ranking the original correctness target \(C\). They are not substitutes for the original answer scorer, and transformed-world success does not establish that the model used the intended internal calculation.

### 3.4 Response-rich missing-probe imputation

Full CEF observes the outcomes of the stronger \(-2\) and \(+2\) probes, whereas S2 does not. We therefore introduce a response-rich missing-probe estimator that predicts the two unexecuted fidelity outcomes from the response pattern already available under the S2 budget.

Let

\[
z=\phi\!\left(d,r_{-1},r_{+1}\right)
\]

denote a frozen response-rich feature vector derived only from the original response and the two mild-probe responses, together with their deterministic response-processing records. The stronger-probe responses are not part of \(z\).

Two binary heads are fitted on training items for which the full probe outcomes are available:

\[
p_{-2}
=
h_{-2}(z)
\approx
\Pr(F_{-2}=1\mid z),
\]

\[
p_{+2}
=
h_{+2}(z)
\approx
\Pr(F_{+2}=1\mid z).
\]

The frozen implementation uses two response-rich gradient-boosted decision-tree heads. The heads are trained against the executable fidelity labels \(F_{-2}\) and \(F_{+2}\), rather than against the original correctness label. For the ConvFinQA confirmation, the heads are fit once on 1,344 Qwen TRAIN items and evaluated on the frozen 198-item DEV cohort.

The imputed PECR score is

\[
\widehat{\operatorname{CEF}}(x)
=
\frac{
F_{-1}+F_{+1}+p_{-2}+p_{+2}
}{4}.
\]

The estimator is a plug-in hybrid: it replaces the two missing binary outcomes with head outputs trained to estimate their fidelity conditional on the observed response-rich feature vector $z$. Because the deployed heads condition on $z$ rather than explicitly on the observed values of $F_{-1}$ and $F_{+1}$, the displayed score should not be read as an exact conditional expectation without an additional conditional-independence assumption. The fitted heads provide plug-in estimates of the two missing probe outcomes. At deployment, the system therefore makes only the original, \(-1\), and \(+1\) calls needed by S2, constructs \(z\), and estimates \(p_{-2}\) and \(p_{+2}\) without querying either stronger world. The unexecuted probe responses are used only as training labels or as a frozen reference for evaluation, not as inference-time inputs.

The imputed score is continuous, whereas full CEF takes values in

\[
\{0,\;0.25,\;0.5,\;0.75,\;1\}.
\]

Consequently, the imputed score can change the ranking of items by resolving ties in the discrete reference. Full CEF is therefore treated as a full-probe reference diagnostic, not as an AUROC upper bound. The imputation method is not described as surpassing a teacher.

### 3.5 Evaluation protocol and scope

For FinQA, PECR is evaluated with Qwen3.5-4B and Ling-3.0-tiny on the source-deduplicated eligible DEV cohort. For ConvFinQA, the same executable construction is applied to 198 DEV items, with the original target defined as normalized current-turn executable numeric correctness.

All original and transformed answers use the frozen answer and unit canonicalization rules. Missing, malformed, schema-invalid, or non-finite outputs fail closed. Each reliability score is evaluated by its AUROC for ranking the original correctness label \(C\). Uncertainty intervals are obtained with item-level bootstrap procedures; source-group cluster bootstrap is used as a sensitivity analysis for imputation deltas. Global and within-operation permutation procedures provide null controls for the PECR rankings.

The ConvFinQA imputation mapping is fit on Qwen TRAIN and, when applied to Ling, is used without refitting, recalibration, threshold selection, or feature selection. This is a zero-shot transfer condition, not statistically confirmed cross-model distillation. The Ling cohort is additionally reported with its validity limitations: only \(9/198\) original answers are correct, schema validity is \(79.1\%\), and numeric validity is \(57.7\%\).

For within-operation permutation strata, operation labels use the repaired executable-trace projection. The repair changed \(11/126\) operation projections but did not change model-facing inputs, transformed gold answers, prompts, or primary CEF/AUROC values; no model calls were rerun.


## 4. Experimental Protocol

### 4.1 Intervention-tested reliability

We evaluate reliability as fidelity to the expected consequence of an intervention rather than as response magnitude alone. A model response can change without changing in the appropriate direction, and a high confidence value need not identify a correct answer. Our protocols therefore specify the intervention consequence before evaluating whether the resulting response ranks correct and incorrect original answers.

The eventual original-answer correctness label is used only for evaluation. It is not used to construct the CST response score, select PECR probes, or deploy the missing-probe student. We report AUROC as the primary ranking metric and retain the frozen 95% intervals supplied by each analysis.

### 4.2 CST: directional response fidelity

Consensus Stress Testing (CST) uses frozen VitaminC cohorts [CITATION NEEDED] to test whether a controlled evidence intervention produces an expected directional response. We define the high-consensus subset by original agreement \(\ge 0.8\). For item \(q\), \(BF_q\) is the mean of the frozen paraphrase and reverse-intervention behavioral-faithfulness fractions, where each fraction counts interventions satisfying the preregistered expected-response predicate; the risk score is \(RS_q=-BF_q\), so larger values indicate lower expected-response faithfulness. The score is computed without using the eventual item label. The primary evaluation asks whether \(RS_q\) ranks incorrect decisions among high-consensus cases.

We use two frozen cohorts: a 50-pair confirmation cohort and a paper-scale cohort containing 300 natural pairs, or 600 items. The confirmation analysis includes placebo and permutation controls and passed the label-symmetric gate. A finalized Round10 \(2\times2\) analysis separately tests whether response direction relative to the initial decision explains the observed effect, rather than a direction-free rigidity or generic evidence-construction account.

### 4.3 S&P 500 portability boundary

The S&P 500 branch is a bounded portability test rather than a second positive benchmark. It includes linguistic interventions and market-native changes to sequential inputs. Unlike a program transformation, these interventions do not provide a uniquely executable transformed answer, so a behavioral change is not automatically aligned with a correctness-relevant consequence.

The final comparison uses 469 complete DEV units. B6 is the simpler raw-trajectory feature, while B8 is the richer behavioral-state candidate. The frozen stopping rule was `KEEP_B6_NO_ESCALATION`; teacher expansion and untouched prospective evaluation were not authorized after this comparison.

### 4.4 PECR construction and FinQA evaluation

PECR is evaluated first on FinQA [CITATION NEEDED]. A row is structurally eligible when its gold executable program contains a uniquely mapped operand that can be transformed and re-executed to produce a transformed gold answer computed from the frozen gold program independently of the model response. For each probe, the model response is compared with that transformed answer, yielding a binary transformed-gold fidelity outcome. Full CEF averages four counterfactual probe outcomes; S2 averages two fixed mild-probe outcomes.

The official DEV population contains 883 rows. The output-blind eligibility procedure produced 182 structurally eligible rows, followed by deterministic one-item-per-source-file selection of 126 source-deduplicated evaluation items. The terminal-operation composition is:

| Operation | Count |
|---|---:|
| add | 8 |
| divide | 105 |
| multiply | 5 |
| subtract | 8 |

The target remains original answer correctness. Thus, CEF and S2 measure fidelity to independently transformed gold answers; they are not measures of latent reasoning recovery, causal competence, or absolute counterfactual competence.

For ConvFinQA [CITATION NEEDED], we use the same executable transformation principle, with normalized current-turn executable numeric correctness as the primary target. The frozen DEV cohort contains 198 items and 990 item-world evaluations.

### 4.5 Sparse scoring and missing-probe imputation

Full CEF uses one original call and four counterfactual calls, for five calls per item. S2 uses one original call and two mild counterfactual calls, for three calls per item. For missing-probe imputation, the observed mild probes are denoted \(-1\) and \(+1\), while the stronger unexecuted probes are \(-2\) and \(+2\). A Qwen TRAIN-fit response-rich student fits two binary heads,

\[
\hat p_{-2}=h_{-2}(z)\approx P(F_{-2}=1\mid z), \qquad
\hat p_{+2}=h_{+2}(z)\approx P(F_{+2}=1\mid z),
\]

where \(F_j\) is the transformed-gold fidelity outcome for probe \(j\). The imputed score is

\[
\widehat{\mathrm{CEF}}
=
\frac{F_{-1}+F_{+1}+\hat p_{-2}+\hat p_{+2}}{4}.
\]

The student is fit once on 1,344 Qwen ConvFinQA TRAIN items and evaluated on the already executed 198-item DEV cohort. The \(-2\) and \(+2\) probes are never queried at deployment, so the imputed score uses the same three calls per item as S2.

## 5. Results

### 5.1 CST motivation: direction matters

The directional CST score ranked incorrect high-consensus decisions in both frozen VitaminC cohorts. On the paper-scale cohort, \(RS_q\) achieved AUROC \(0.943\) with 95% CI \([0.924, 0.960]\). The independent 50-pair confirmation achieved AUROC \(0.912\), 95% CI \([0.848, 0.973]\).

The Round10 mechanism analysis does not support a direction-free interpretation in which any response to additional evidence is equally informative. Consensus-opposing independent evidence changed the wrong consensus in \(35/37=0.946\) cases, with a direction contrast of \(+0.44\), 95% CI \([0.24, 0.65]\). The surviving interpretation is therefore conditional: response direction relative to the initial decision showed the clearest signal in this frozen contrast, relative to the tested generic evidence-construction and overlap contrasts. A raw change or flip indicator would merge interventions that agree with the current decision with interventions that oppose it and would discard this distinction.

CST consequently provides a bounded motivation for intervention-tested reliability. It shows that expected directional response can rank errors in the frozen evidence-intervention setting; it does not establish recovery of a hidden group state, a universal consensus law, or a causal account of why a panel changes.

### 5.2 S&P 500: a portability boundary

The S&P branch demonstrates that measurable behavioral sensitivity does not automatically become a transferable correctness signal. The bounded hardness analysis gave static AUROC \(0.6040\) for Ling and \(0.5569\) for Hy. Wrong-majority dates were common, with \(161/166\) dates having a wrong majority and \(14/87\) dates having all five panel answers wrong.

On the 469 complete DEV units, the simpler B6 feature achieved AUROC \(0.6320\), 95% CI \([0.5546, 0.7051]\). The B8 behavioral-state candidate achieved AUROC \(0.6177\), 95% CI \([0.5430, 0.6950]\). The paired difference was

\[
\mathrm{B8}-\mathrm{B6}=-0.0143,
\qquad
95\%~\mathrm{CI}=[-0.0560, 0.0287].
\]

The frozen decision was `KEEP_B6_NO_ESCALATION`. Thus, the richer behavioral representation did not establish a stable incremental correctness signal over the simpler baseline. This negative boundary is important for the paper thesis: repeatable behavioral change, response geometry, or local sensitivity is not sufficient when the expected semantic consequence of an intervention is under-specified.

### 5.3 FinQA PECR

The official FinQA result is restricted to the 126 source-deduplicated eligible items, not the complete 883-row DEV population. Qwen3.5-4B and Ling-3.0-tiny produced the following frozen results:

| Model | Original accuracy | Confidence AUROC | S2 AUROC | Full CEF AUROC | Full–S2 gap |
|---|---:|---:|---:|---:|---:|
| Qwen3.5-4B | \(43/126=34.13\%\) | 0.5181 | \(0.8317\ [0.7555,0.9020]\) | \(0.9008\ [0.8411,0.9517]\) | \(0.0691\ [0.0211,0.1238]\) |
| Ling-3.0-tiny | \(29/126=23.02\%\) | 0.5412 | \(0.8379\ [0.7504,0.9182]\) | \(0.8477\ [0.7619,0.9256]\) | \(0.0098\ [-0.0145,0.0470]\) |

Full CEF and S2 both ranked original answer correctness for the two evaluated model families, while raw confidence was near chance in this cohort: \(0.5181\) for Qwen3.5-4B and \(0.5412\) for Ling-3.0-tiny. The result supports executable transformed-gold fidelity as a correctness diagnostic on this eligible FinQA subset. It does not establish broad FinQA coverage or latent reasoning fidelity.

### 5.4 Sparse-cost comparison

The sparse design reduces the planned call budget from five calls per item for full CEF to three calls per item for S2. This is a 40% reduction in total calls and a 50% reduction in counterfactual calls.

On 200 same-item TRAIN controls, the direct scores and gain-retention ratios were. We define the secondary retention ratio as

\[
R_{\mathrm{ret}}=\frac{\operatorname{AUROC}(S2)-\operatorname{AUROC}(\mathrm{Conf})}{\operatorname{AUROC}(\mathrm{Full\ CEF})-\operatorname{AUROC}(\mathrm{Conf})},
\]

where $\mathrm{Conf}$ is the same-cohort confidence-based AUROC. This ratio is descriptive and is not an equivalence or superiority test.


| Model | Full CEF AUROC | S2 AUROC | Direct gap | Retention of full-CEF gain |
|---|---:|---:|---:|---:|
| Qwen3.5-4B | 0.8729 | 0.8007 | 0.0722 | \(0.8079\ [0.6920,0.9081]\) |
| Ling-3.0-tiny | 0.8559 | 0.7857 | 0.0702 | \(0.8122\ [0.6573,0.9420]\) |

These ratios are secondary endpoints rather than equivalence claims. They indicate that two executable probes retain a substantial fraction of the full-CEF gain in both evaluated models while using fewer calls. On official DEV, the full–S2 gaps were \(0.0691\ [0.0211,0.1238]\) for Qwen3.5-4B and \(0.0098\ [-0.0145,0.0470]\) for Ling-3.0-tiny.

### 5.5 ConvFinQA cross-task replication

The cross-task evaluation tests whether the PECR signal persists when the current turn depends on conversational context. The Qwen cohort contained 34 original-correct positives, 988/990 schema-valid worlds (99.8%), and numeric validity of 0.9455. The Ling cohort contained only 9 original-correct positives, 783/990 schema-valid worlds (79.1%), and numeric validity of 0.5768 (57.7%).

| Model | Original-correct positives | Schema-valid worlds | Numeric-valid worlds | S2 AUROC | Full CEF AUROC | Global / within-operation \(p\) |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5-4B | 34/198 | \(988/990=99.8\%\) | 0.9455 | \(0.6508\ [0.5707,0.7353]\) | \(0.6870\ [0.5954,0.7822]\) | 0.0002 / 0.0002 |
| Ling-3.0-tiny | 9/198 | \(783/990=79.1\%\) | 0.5768 | \(0.8275\ [0.6525,0.9983]\) | \(0.8251\ [0.6456,0.9988]\) | 0.0002 / 0.0002 |

For Qwen3.5-4B, both S2 and full CEF retained positive discrimination of normalized current-turn executable numeric correctness. The core signal also replicated for Ling-3.0-tiny, but this estimate is secondary: only \(9/198\) original answers were correct, and the schema and numeric-validity rates were substantially lower than Qwen’s. The paired full-CEF-minus-S2 difference for Ling was \(-0.0024\), 95% CI \([-0.0083,0.0023]\). Accordingly, the cross-task result supports bounded replication within executable financial reasoning, not arbitrary reasoning-task generalization.

### 5.6 Qwen missing-probe confirmation

The missing-probe student was trained on 1,344 Qwen ConvFinQA TRAIN items and evaluated once on the frozen 198-item DEV cohort. The two heads were individually discriminative for the outcomes of the stronger probes:

\[
\mathrm{AUROC}(p_{-2},F_{-2})=0.8754,
\qquad
\mathrm{AUROC}(p_{+2},F_{+2})=0.8407.
\]

Using the predicted stronger-probe outcomes in the continuous imputed score improved the sparse diagnostic from S2 AUROC \(0.6508\) to \(0.7474\):

\[
\Delta_{\widehat{\mathrm{CEF}}-\mathrm{S2}}=+0.0966,
\]

with item-bootstrap 95% CI \([+0.0183,+0.1740]\). The post-hoc source-group cluster-bootstrap interval was \([+0.0190,+0.1736]\). The improvement passes the frozen practical threshold of \(+0.02\), while deployment remains at three calls per item.

The full CEF score on this cohort was \(0.6870\). It is retained as a full discrete diagnostic reference, not as an AUROC upper bound. Because full CEF takes values in \(\{0,0.25,0.5,0.75,1\}\), the continuous imputed score can resolve ties and produce a different ranking. Thus, the \(0.7474\) result should be interpreted as an improvement over S2, not as surpassing a teacher or violating an upper-bound comparison.

Applying the frozen Qwen TRAIN-fit mapping to Ling without refitting yielded a suggestive point estimate: Ling S2 increased from \(0.8275\) to \(0.8536\), a delta of \(+0.0262\). However, the item-bootstrap 95% CI was \([-0.0539,+0.1436]\), and the source-group interval was \([-0.0476,+0.1453]\). The Ling missing-head positive counts were only 6 for \(-2\) and 8 for \(+2\); no Ling refit, calibration, feature selection, or threshold selection was performed. We therefore treat this result as suggestive zero-shot transfer only, not statistically confirmed cross-model imputation.

Taken together, the results support a conditional progression from generic response, to directional expected response in CST, to executable expected response in PECR. The positive PECR and missing-probe results are bounded to the evaluated financial-reasoning cohorts and observed answer-correctness targets.


## 6. Related Work

### 6.1 Confidence, calibration, and selective prediction

Reliability evaluation for language models commonly uses self-reported confidence, token probabilities, calibration curves, and selective prediction or abstention policies [CITATION NEEDED]. Calibration asks whether a reported probability corresponds to empirical correctness frequency, while selective prediction uses an uncertainty score to control risk under abstention [CITATION NEEDED]. These approaches evaluate the original response and its associated uncertainty. Intervention-tested reliability adds a different question: after a controlled change in the evidence, does the system respond in the expected direction or magnitude?

This distinction makes confidence a complementary baseline rather than an alternative definition of reliability. On the eligible FinQA DEV cohort, confidence AUROC was `0.5181` for Qwen3.5-4B and `0.5412` for Ling-3.0-tiny. These near-chance values motivate comparison with behavioral probes in this cohort, but they do not establish that confidence or calibration methods are generally ineffective.

### 6.2 Agreement and self-consistency

Agreement-based methods use repeated samples, vote margins, panel consensus, entropy, or semantic dispersion to estimate uncertainty [CITATION NEEDED]. Self-consistency methods similarly treat repeated agreement across stochastic reasoning paths as evidence of reliability [CITATION NEEDED]. These signals measure variability or agreement in the same underlying world; they do not, by themselves, specify how a response should change when relevant evidence is added or an operand is transformed.

CST begins from this agreement-based setting but tests a further property: whether a high-consensus answer moves appropriately when presented with independent, consensus-opposing evidence. PECR applies the same principle at the item level using executable numerical transformations rather than repeated sampling. The goal is not to replace agreement or self-consistency, but to add an expected-response axis that can be evaluated under a matched call budget.

### 6.3 Intervention, robustness, and metamorphic evaluation

Robustness and stress-testing work evaluates systems under perturbations, distribution shifts, adversarial inputs, or evidence removal [CITATION NEEDED]. Metamorphic testing evaluates whether outputs remain invariant or change according to a specified relation after an input transformation [CITATION NEEDED]. PECR is closely related to this relation-preserving testing tradition. It should therefore be viewed as a program-backed instance of intervention evaluation, not as a wholly separate testing paradigm.

The difference is the reliability target and the source of the expected outcome. PECR uses a gold executable program to transform a uniquely mapped operand and construct transformed gold answers from the frozen gold program independently of the model response. CEF and S2 then measure fidelity to those transformed answers as a diagnostic of correctness on the original item. This differs from evaluating only post-perturbation task accuracy or measuring arbitrary output sensitivity. CST provides a natural-language analogue in which the expected response is directional rather than numerically executable.

### 6.4 Counterfactual reasoning and process verification

Counterfactual reasoning and causal evaluation study how systems answer under alternative premises, changed facts, or hypothetical worlds [CITATION NEEDED]. Process and reasoning-verification work instead examines intermediate traces, proofs, tool calls, or other observable accounts of how an answer was produced [CITATION NEEDED]. PECR intersects with both traditions while making a narrower claim. Its transformed worlds are generated from executable arithmetic programs, but the resulting score is not a measure of general counterfactual competence or causal understanding. Likewise, the gold program is a construction and scoring instrument; it is not evidence that the model internally followed the same program.

### 6.5 Positioning

The paper studies a complementary reliability signal: observable response fidelity under an executable, outcome-blind intervention. CST demonstrates the signal through directional changes in consensus decisions. PECR makes the expected response explicit through transformed gold and evaluates it with sparse and full probe budgets. The contribution is therefore not a replacement for confidence, calibration, agreement, or self-consistency. It is a method for testing whether those signals are accompanied by behavior that tracks the known semantics of an intervention.

## 7. Discussion

### 7.1 Expected response is more informative than change alone

A raw output change is ambiguous. A model may change for an irrelevant reason, while a model may appropriately remain stable under an intervention whose expected answer is invariant. Conversely, no change in response to relevant evidence may indicate a problem, but only when the expected direction of change is known. Intervention-tested reliability resolves this ambiguity by scoring the relation between the intervention and the response, rather than merely measuring response magnitude.

CST illustrates this distinction at the level of consensus decisions. On frozen VitaminC cohorts, the direction-sensitive score `RS_q = -BF_q` ranked incorrect high-consensus decisions with AUROC `0.943 [0.924, 0.960]`; the 50-pair confirmation achieved `0.912 [0.848, 0.973]`. The accompanying Round10 analysis is important for interpreting the signal. Consensus-opposing independent evidence changed the wrong consensus in `35/37 = 0.946` cases, with a direction contrast of `+0.44 [0.24, 0.65]`. Thus the result is not adequately described as detecting direction-free rigidity. It indicates that the direction of behavioral change carries information. It does not recover a hidden group state or establish a cognitive mechanism inside the model.

The bounded S&P branch provides a useful negative boundary. Measurable behavioral sensitivity was not automatically a transferable reliability predictor: static AUROC was `0.6040` for Ling and `0.5569` for Hy. On `469` DEV units, B6 achieved `0.6320 [0.5546, 0.7051]`, B8 achieved `0.6177 [0.5430, 0.6950]`, and B8–B6 was `-0.0143 [-0.0560, 0.0287]`. This supported retaining B6 without escalation. The result cautions against treating generic sensitivity as sufficient. A useful intervention must carry an interpretable expectation about how the answer should respond.

### 7.2 PECR makes the expectation executable

PECR instantiates this principle for structurally eligible numerical reasoning items. A gold executable program identifies a uniquely mapped operand, transforms it into several counterfactual worlds, and independently produces transformed gold answers. The model is then evaluated on whether its responses follow those executable transformations. CEF and S2 therefore measure transformed-gold fidelity. They are not measures of latent reasoning, causal competence, or absolute counterfactual ability.

The official FinQA DEV result shows the value of this diagnostic on the frozen eligible cohort. Qwen3.5-4B achieved full CEF AUROC `0.9008 [0.8411, 0.9517]` and S2 AUROC `0.8317 [0.7555, 0.9020]`. Ling-3.0-tiny achieved `0.8477 [0.7619, 0.9256]` and `0.8379 [0.7504, 0.9182]`, respectively. These scores are associations with original correctness on the selected cohort, not claims that either model has broad counterfactual reasoning ability.

The same evaluation recipe was applied to `198` ConvFinQA DEV items. Qwen achieved S2/full CEF AUROCs of `0.6508 [0.5707, 0.7353]` and `0.6870 [0.5954, 0.7822]`. Ling achieved `0.8275 [0.6525, 0.9983]` and `0.8251 [0.6456, 0.9988]`. Global and within-operation permutation values were `p = 0.0002` for both models. The Ling estimates require particular caution: only `9/198` items were originally correct, schema validity was `79.1%`, and numeric validity was `57.7%`. These results support replication of the executable diagnostic within a related benchmark family, but not a task-general reliability claim.

### 7.3 The three-budget PECR ladder

The method separates the cost of observing interventions from the cost of modeling their likely outcomes:

| Layer | Deployment observations | Learned or unobserved component | Calls/item | Role |
|---|---|---|---:|---|
| Confidence baseline | Original response | None | 1 | One-call uncertainty baseline |
| S2 | Original, `-1`, `+1` | None | 3 | Fixed sparse diagnostic |
| Imputed PECR | Original, `-1`, `+1` | Estimates of `p_-2` and `p_+2` | 3 | Response-rich sparse diagnostic |
| Full discrete CEF | Original, `-2`, `-1`, `+1`, `+2` | None | 5 | Full-probe reference |

Relative to full CEF, S2 uses three rather than five calls per item, corresponding to planned reductions of `40%` in total calls and `50%` in counterfactual calls. On 200-item TRAIN controls, S2 retained `0.8079 [0.6920, 0.9081]` of Qwen’s full-CEF gain and `0.8122 [0.6573, 0.9420]` of Ling’s. These retention ratios are secondary summaries rather than equivalence claims; direct AUROC values and paired differences remain the primary comparisons.

The missing-probe result shows how the same three-call deployment budget can support a learned response-rich diagnostic. On frozen ConvFinQA Qwen DEV, a Qwen TRAIN-fit student predicted the outcomes of two unexecuted stronger probes with AUROCs `0.8754` for `p_-2` and `0.8407` for `p_+2`. The resulting imputed score improved S2 from `0.6508` to `0.7474`, a difference of `+0.0966` with item-bootstrap 95% CI `[+0.0183, +0.1740]` and source-group CI `[+0.0190, +0.1736]`. Deployment still required only three calls per item.

This result should be interpreted as budget-preserving imputation, not as evidence that the imputed system surpasses the full-probe system. Full discrete CEF is a discrete reference diagnostic, not an AUROC upper bound. The learned estimates and the discrete pass pattern are different scores with different information structures.

Zero-shot transfer to Ling is secondary and suggestive: the Qwen-trained imputation produced `0.8536` versus Ling S2 `0.8275`, a point difference of `+0.0262`, but the item-bootstrap interval was `[-0.0539, +0.1436]` and the source-group interval was `[-0.0476, +0.1453]`. No Ling refit, recalibration, threshold selection, or feature selection was performed.

### 7.4 Relation to matched-budget baselines

The available baseline evidence is consistent with, but does not prove, the value of intervention-tested behavior. On a fresh 40-item source-file-disjoint TRAIN cohort, S2 had the highest observed AUROC among the primary tested black-box baselines for both models: `0.8110` for Qwen and `0.9583` for Ling, compared with repeated-sampling agreement values of `0.6027` and `0.6618`. The cohort was small and operation-skewed (`add=7`, `divide=28`, `subtract=5`), so these values should be read as a fresh-cohort comparison rather than a definitive ranking.

Self-verification did not exceed S2 on this cohort, but the Qwen paired interval includes zero. Semantic consistency was exploratory because the execution used three observed calls per item although the frozen table specified two. Accordingly, the paper presents PECR as complementary to confidence, agreement, and self-consistency, while avoiding a claim of separation from every baseline under every model and budget.

## 8. Limitations

First, PECR applies only where a reliable executable representation is available. On official FinQA DEV, the output-blind construction reduced `883` rows to `182` structurally eligible rows and then to `126` source-deduplicated evaluation items. The operation distribution was highly skewed: `add 8`, `divide 105`, `multiply 5`, and `subtract 8`. The claim is therefore about an identifiable arithmetic subset, not the full dataset distribution.

Second, model and benchmark coverage remains limited. The main results use Qwen3.5-4B and Ling-3.0-tiny, and the ConvFinQA replication remains within the broader FinQA-style benchmark family. The S&P branch is a useful portability boundary, not a second executable benchmark. Larger model families, additional executable tasks, and more balanced operation coverage are natural next tests.

Third, PECR depends on gold executable programs and transformed gold answers. This provides strong, auditable supervision but restricts portability and changes the interpretation of the score. High CEF or S2 indicates transformed-gold fidelity on eligible items; it does not show that the model internally executed the gold program, recovered a hidden state, understood a causal relation, or possesses general counterfactual competence.

Fourth, sparse compression is lossy, and the retention ratios have wide intervals. Full CEF uses five calls per item while S2 uses three, and the imputed variant additionally depends on a TRAIN-fit response model. The Qwen missing-probe result is the strongest current evidence for this compression strategy; the Ling transfer remains uncertain because of the low positive count and validity caveats.

Finally, baseline coverage is still bounded. The fresh comparison cohort contains only 40 items, and the semantic-consistency implementation was not strictly matched to its planned call count. Future work should evaluate confidence, token-level uncertainty, repeated sampling, self-verification, and semantic consistency under a single preregistered budget and on larger, multi-operation cohorts.

## 9. Conclusion

This paper introduces intervention-tested reliability as a complementary way to evaluate whether a system responds appropriately to controlled changes in its evidence. CST shows that the direction of a consensus response to independent evidence can predict incorrect high-consensus decisions, while the S&P boundary shows that generic behavioral sensitivity is not sufficient without an interpretable expected response.

PECR makes that expectation executable for eligible numerical reasoning items. Its transformed-gold fidelity scores associate with original correctness on frozen FinQA and ConvFinQA cohorts, and its three-call sparse variants provide a practical cost ladder. Most notably, missing-probe imputation improved Qwen ConvFinQA S2 from `0.6508` to `0.7474` without increasing the three-call deployment budget. These findings support a narrow positive claim: executable interventions can provide an item-level reliability diagnostic beyond the tested confidence and agreement baselines in the reported cohorts. They do not establish universal reasoning reliability, hidden-state recovery, or causal competence. Broader validation should focus on additional executable benchmarks, balanced cohorts, and strictly matched uncertainty baselines.

## Appendix A. Reproducibility Plan

Appendix A specifies the following reproducibility materials; any unavailable row-level artifact will be labeled as unavailable rather than reconstructed:

1. **Evidence ledger and freeze chronology.** An artifact registry will identify experiment IDs, freeze dates, cohort definitions, allowed claims, and the exact main-table entries supported by each artifact. Discovery, confirmation, sparse replication, cross-model evaluation, compression controls, and official DEV validation will remain distinct. The principal anchors are `cs-pilot-vitaminc-conf-20260913`, `cs-paper-vitaminc-20260913`, and `round10-2x2-20260915` for CST; `sp500-f0-hardness-20260918` and `sp500-wave3-b678-20260918` for the S&P boundary; `pecr-v0.7-larger-teacher-control` and `pecr-v0.8-official-dev-one-shot` for FinQA; and `29_final_evidence_freeze_20260922`, `27_convfinqa_stage2_qwen_missing_probe_20260922`, and `28_convfinqa_stage3_ling_replication_20260922` for the ConvFinQA confirmation.

2. **PECR construction specification.** Document supported operations, deterministic numeric rules, operand-selection and uniqueness checks, the `-2,-1,+1,+2` world schemas, exclusion rules, surface-quantization checks, and fail-closed invalid-output categories.

3. **Eligibility and structural composition.** Include the complete `883 → 182 → 126` attrition table, operation counts, rejection reasons, and descriptive comparisons for official DEV, ineligible rows, eligible-before-deduplication rows, the selected cohort, and eligible-but-not-selected rows. These comparisons will not be presented as a no-bias guarantee.

4. **Scoring and budget accounting.** Specify original-answer correctness, transformed-gold matching, CEF and S2 aggregation, invalid handling, bootstrap units, global and within-operation permutation procedures, prompt templates, endpoint identity checks, and the three- versus five-call accounting. The imputation appendix will document the Qwen TRAIN fit, held-out ConvFinQA deployment, feature availability, and the absence of Ling refitting or tuning.

5. **CST and S&P boundary analyses.** Move secondary calibration, risk-at-coverage, placebo, label-symmetry, and historical permutation details to the appendix while retaining the Round10 direction contrast in the main paper. Report finalized S&P intervention families and the stop-escalation decision without inserting unavailable subgroup values.

6. **Metadata and analyzer-repair disclosure.** The offline deterministic repair changed the `program_ops` projection for `11/126` records, while model-facing world inputs, transformed gold, and prompts were unchanged and no model calls were rerun. Separately, the v0.10 analyzer repair materialized the two confidence fields already declared by the frozen feature contract and made the direction-sign calculation explicit; the feature-list hash remained unchanged, no forbidden outcome-derived feature appeared, and no model calls were added. The 41-feature omission check and group-bootstrap audit are post-hoc integrity/sensitivity analyses, not replacements for the frozen endpoints. The raw pre-repair manifest was not persisted; the reconstructed before-projection hash is therefore reconstructed metadata rather than a persisted raw artifact. The recorded hashes are: before-projection `655751001f203d70283ea585b2e2d210889761665fd99054789c8717c638c7f4`, final projection `ea744f23eb989e02db9678e902a7d342b425954ac9722d7b658eadd9545cc7a2`, cohort `6d249216f4da6b9bdcfc291ff2ae57ff8a1a516c1515b1d0e4877cd585b16735`, world-input `b7d52a26b27be8cbd6bc71992ba5cd8603cce9f88f0d5005289c682ae1e47b10`, world-gold `08f98e22a8fd4f3a13996fe9f362bfa9b3bcc7b4d9fe8bc0121269e87787abff`, and prompt `3f83f924f2d1ec639840c54843e0385d03536b8e34653ff99eb968f1ef6ddd82`.

7. **Artifact and non-overwrite statement.** Document that the consolidation workspace contains drafts, specifications, and offline code only, with no raw model-output copies and no modifications to historical experiment directories. Any unavailable row-level artifacts will be labeled as missing rather than reconstructed.
