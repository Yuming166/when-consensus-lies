# AutoResearch Wave-4 — Market-Native Counterfactual Reliability Distillation for S&P500

**Status:** Proposed frozen research protocol  
**Primary goal:** Test whether market-native counterfactual response surfaces contain reliability information beyond an agent's original forecast, and only if that signal exists, distill it into a compact low-query student.  
**Core principle:** Do not search for a student architecture before establishing a teacher upper bound.

---

## 0. Research Question

The current S&P500 line has established an important negative boundary:

- Ling-3.0-tiny: original-response baseline is informative, but linguistic intervention responses did not establish stable conditional reliability value.
- Qwen3.5-4B: original-only forecasting improved, but the same linguistic ICVA still failed.
- Hindsight credit, geometry, CRRD teacher, and multiple residual formulations did not establish stable incremental value.

Therefore, Wave-4 must not continue architecture search on the same linguistic intervention representation.

The new question is:

> **Can outcome-blind, market-native counterfactual perturbations reveal a structured response surface that predicts forecast reliability beyond the original judgment, and can this response surface be compressed into a sparse low-query student?**

The intended evidence chain is:

\[
\text{Market-native perturbations}
\rightarrow
\text{Full response surface}
\rightarrow
\text{Reliability increment}
\rightarrow
\text{Structured teacher}
\rightarrow
\text{Sparse distilled student}.
\]

Every arrow must pass an explicit gate. If an upstream gate fails, downstream stages must not run.

---

# 1. Scientific Hypotheses

## H1 — Full Response-Surface Signal

For an original forecast \(O_t\) and a set of market-native interventions \(\mathcal R_t\),

\[
P(C_t=1\mid O_t,\mathcal R_t)
>
P(C_t=1\mid O_t)
\]

where \(C_t\) denotes forecast correctness.

Operationally, test whether adding the full market-native response surface improves AUROC, calibration, and selective reliability over the strongest original-only baseline under strict temporal OOF evaluation.

## H2 — Regime-Conditioned Reliability

The meaning of an intervention response depends on market regime:

\[
P(C_t=1\mid O_t,\mathcal R_t,Z_t^{regime})
>
P(C_t=1\mid O_t,\mathcal R_t)
\]

for at least one preregistered regime-aware model specification.

## H3 — Structured Teacher Advantage

A structured model that respects intervention axis, perturbation magnitude, and response ordering should outperform a capacity-matched flattened baseline:

\[
T_{structured}>B_{flattened,matched}.
\]

## H4 — Sparse Distillation

A low-query student using only a small number of probes should preserve a substantial fraction of the teacher's reliability gain:

\[
Retention(q)=
\frac{AUROC(S_q)-AUROC(O)}
{AUROC(T)-AUROC(O)}.
\]

Target query budgets: \(q\in\{1,2,3\}\).

---

# 2. Non-Negotiable Experimental Boundaries

## 2.1 Preserve previous negative results

Do not overwrite, reinterpret, or retroactively alter earlier Wave-3 / ICVA / CRRD outputs.

Recommended workspace:

```text
consensus_stress/autoresearch_wave4_market_native/
```

## 2.2 DEV remains locked

No method selection, feature selection, architecture choice, threshold tuning, or intervention redesign may use DEV.

## 2.3 Existing prospective set remains sealed

The current 807 prospective dates remain untouched.

Required invariant:

```text
prospective_calls = 0
```

until a final confirmatory protocol is frozen.

## 2.4 No outcome-conditioned intervention construction

Interventions must use only information available as of forecast date \(t\).

Forbidden inputs include future 10-day return, future path, future realized volatility, correctness label, and any feature crossing the information cutoff.

---

# 3. Wave-4 Data Expansion

## 3.1 Increase date count

Target at least:

\[
1000\text{ TRAIN dates}
\]

Preferred total historical cohort:

\[
1500\text{--}2000+\text{ dates}
\]

if data availability permits.

The objective is temporal and regime diversity, not merely more rows.

## 3.2 Prefer temporal breadth over more agents per day

Priority:

1. More historical dates
2. More regime diversity
3. More market-native perturbations
4. More agents only if compute allows

## 3.3 Sampling must be outcome-blind

Do not select dates based on future return magnitude, whether a model was wrong, post-hoc difficulty, or previous ICVA failures.

Allowed stratification variables are pre-outcome only, such as realized volatility, VIX level/z-score, trend strength, drawdown, moving-average state, term structure, put-call/positioning, credit spread state, and rate regime.

## 3.4 Preserve temporal evaluation integrity

Because the main target is a 10-day return label, neighboring dates have overlapping outcomes.

Use:

- expanding temporal folds;
- purging;
- embargo;
- date-grouped evaluation;
- block bootstrap;
- non-overlap robustness subsets.

Freeze the exact embargo before modeling.

---

# 4. Target Definition

Primary target remains:

\[
y_t=\mathbf 1\left[\frac{P_{t+10}-P_t}{P_t}>0\right].
\]

Primary endpoint is forecast reliability/correctness, not trading PnL.

Do not make alpha claims unless a separate trading protocol is preregistered later.

---

# 5. Base Models

## 5.1 Primary model

Use `Qwen3.5-4B` as the primary Wave-4 model.

## 5.2 Secondary family control

Use `Ling-3.0-tiny` only after Qwen market-native signal evaluation.

Do not immediately duplicate the full 2×2 experiment unless Qwen produces interpretable evidence worth replicating.

---

# 6. Financial Evidence Axes

Wave-4 interventions should manipulate **domain-native evidence channels**, not generic linguistic agreement/disagreement.

Freeze a small number of axes before generation.

Recommended initial set:

### Axis A — Trend / Momentum

Examples:
- 1d / 5d / 10d return
- MA ratio
- trend slope
- distance from moving average

### Axis B — Volatility / Risk

Examples:
- realized volatility
- VIX level
- VIX z-score
- VIX change

### Axis C — Positioning / Sentiment

Examples:
- put-call ratio
- positioning proxy
- breadth / flow proxy if available

### Axis D — Macro / Credit Risk

Examples:
- Treasury yield change
- yield-curve state
- credit spread
- risk-premium proxy

Prefer 3–4 axes initially. Do not create a large feature zoo.

---

# 7. Market-Native Counterfactual Construction

## 7.1 Multi-level interventions

For each axis \(k\), define ordered perturbation levels:

\[
\delta\in\{-2,-1,+1,+2\}.
\]

Levels should correspond to realistic historical magnitudes.

The intervention should change one axis while holding other evidence blocks fixed as much as possible.

## 7.2 Prefer historical natural counterfactual donors

For date \(t\), select an earlier historical donor \(j<t\) satisfying:

\[
X^{-k}_j\approx X^{-k}_t
\]

while \(X^k_j\) lies in the desired counterfactual direction/magnitude bucket.

Construct:

\[
X_t^{(k,\delta)}=[X_t^{-k},X_j^k].
\]

This is preferable to asking an LLM to invent hypothetical market evidence.

## 7.3 Donor matching must be time-valid

For TRAIN examples, donors must come only from dates available before the forecast date.

Never use future dates as donors.

## 7.4 Intervention validity audit

For every counterfactual log:

- source date;
- donor date;
- axis changed;
- original value;
- donor value;
- standardized perturbation magnitude;
- unchanged-block distance;
- as-of-time validity;
- intervention direction.

Reject or flag violations using frozen rules only. Do not repair based on correctness.

---

# 8. Full Response Surface

For each date-agent pair, query:

- Original
- \(K\) axes
- \(L\) perturbation levels per axis

Example:

\[
K=3,L=4\Rightarrow 1+3\times4=13
\]

queries per agent-date.

For \(K=4\):

\[
1+4\times4=17.
\]

Store predicted direction, probability, confidence, structured output metadata already in the protocol, and explicit failures.

Do not use hidden chain-of-thought.

---

# 9. Response-Surface Features

For each axis \(k\), compute outcome-blind behavioral descriptors.

## 9.1 Local slope

\[
S_k=\frac{\Delta p}{\Delta x_k}.
\]

Interpret as empirical response sensitivity, not a causal derivative.

## 9.2 Curvature

\[
K_k=p(+2)-2p(0)+p(-2).
\]

## 9.3 Directional asymmetry

\[
A_k=|p(+1)-p(0)|-|p(-1)-p(0)|.
\]

## 9.4 Monotonic consistency

Measure whether ordered perturbation magnitudes induce ordered responses.

Do not assume global monotonicity must hold.

## 9.5 Cross-axis structure

Possible descriptors:

- relative sensitivity across axes;
- rank of most influential axis;
- pairwise sensitivity differences;
- axis-interaction summaries.

Avoid excessive handcrafted compression before testing the raw surface.

---

# 10. Finance-Aware Market Regime Representation

Construct a low-dimensional pre-outcome market-state vector:

\[
Z_t^{regime}
\]

using frozen variables such as:

- trend strength;
- realized volatility;
- VIX z-score;
- drawdown;
- yield / credit state;
- positioning proxy.

Recommended approach:

1. start with continuous variables;
2. optionally derive a small number of regime states;
3. fit any regime encoder on TRAIN only.

Do not cluster using labels.

---

# 11. Stage A — Signal Existence Test

This is the most important stage.

Do not train a student before Stage A passes.

Compare:

### A0 — Original only

\[
B_O=f(O).
\]

### A1 — Original + market

\[
B_{OM}=f(O,M).
\]

### A2 — Original + full response surface

\[
B_{OR}=f(O,\mathcal R).
\]

### A3 — Original + market + full response surface

\[
B_{OMR}=f(O,M,\mathcal R).
\]

Primary gate:

\[
B_{OR}>B_O
\]

and preferably:

\[
B_{OMR}>B_{OM}.
\]

### Stage A model restrictions

Use only a small frozen candidate set:

- Ridge / logistic
- shallow GBDT
- small MLP

No Transformer yet.

No arbitrary feature-subset search.

No post-hoc architecture expansion.

### Stage A PASS criteria

A candidate must satisfy:

1. Positive AUROC increment over matched baseline
2. Positive paired date-bootstrap evidence
3. No severe block-bootstrap contradiction
4. Reasonable fold consistency
5. No major calibration collapse
6. Shuffled-response control does not reproduce gain
7. Market-only / agent-ID controls do not explain effect
8. Common-support analysis agrees

Preferred strong evidence:

\[
95\%\ CI(\Delta AUROC)>0.
\]

If Stage A fails:

```text
STOP_WAVE4_DISTILLATION
```

Do not train teacher/student.

---

# 12. Stage B — Regime-Conditioned Reliability

Only run if Stage A passes or shows a preregistered promising signal.

Compare:

\[
f(O,\mathcal R)
\]

versus

\[
f(O,\mathcal R,Z^{regime}).
\]

Use simple models first:

- regime-conditioned logistic
- shallow mixture-of-experts
- small MLP with regime embedding
- shallow GBDT interaction baseline

Required control: a regime-aware market-only model.

The result must show that regime conditioning helps interpret response behavior rather than merely improving market prediction.

---

# 13. Stage C — Structured Teacher Existence

Only run after response-surface signal exists.

## 13.1 Flattened nonlinear control

Build a capacity-matched baseline:

\[
B_{flat}=MLP(flatten(\mathcal R),O,M)
\]

or a matched shallow GBDT.

## 13.2 Structured teacher

Recommended teacher:

**small axis-aware Transformer / Set Transformer**

Each intervention token:

\[
e_{k,\delta}
=
MLP(axis_k,\delta,p_{k,\delta}-p_0,c_{k,\delta}-c_0,market\ state).
\]

Within-axis aggregation:

\[
h_k=Attn_\delta(e_{k,\delta}).
\]

Across-axis aggregation:

\[
z_T=Attn_k(h_k).
\]

Reliability head:

\[
r_T=\sigma(g[z_T,O,M]).
\]

Keep the network small.

Do not use a generic large Transformer over all raw features.

### Stage C gate

The structured teacher must beat a capacity-matched flattened nonlinear baseline:

\[
T_{structured}>B_{flat}.
\]

If not:

- response-surface signal may still be useful;
- do not claim structured relational advantage;
- do not force a Transformer story.

---

# 14. Stage D — Sparse Student Distillation

Only run if a teacher upper bound exists.

The student receives:

- market state \(M_t\);
- original prediction \(O_t\);
- only \(q\) selected probes.

Test:

\[
q\in\{1,2,3\}.
\]

## 14.1 Student architecture

Start simple:

- small MLP
- small GRU/Transformer only if sequential probe selection is used

Do not begin with a large Transformer.

## 14.2 Distillation targets

Use complementary losses.

### Reliability matching

\[
L_{rel}=(r_S-r_T)^2.
\]

### Embedding matching

\[
L_{emb}=1-\cos(z_S,z_T).
\]

### Ranking preservation

For agents \(a,b\) in the same date:

\[
L_{rank}=\log(1+\exp(-(r_S(a)-r_S(b)))).
\]

Total:

\[
L=L_{correctness}+\lambda_1L_{rel}+\lambda_2L_{emb}+\lambda_3L_{rank}.
\]

All \(\lambda\) values must be frozen using TRAIN-only nested validation.

---

# 15. Stage E — Active Probe Selection

Optional; run only after a fixed-probe student is useful.

The student chooses the next probe:

\[
\pi(k_{next}\mid X,O,R_{observed}).
\]

Sequence:

\[
X\rightarrow O\rightarrow k_1\rightarrow R_{k_1}\rightarrow k_2\rightarrow R_{k_2}\rightarrow r_S.
\]

Goal: recover most of the full-teacher reliability gain with 1–3 probes.

---

# 16. Distillation Success Metric

Define:

\[
Retention(q)=
\frac{AUROC(S_q)-AUROC(O)}
{AUROC(T)-AUROC(O)}.
\]

Report:

- Retention(1)
- Retention(2)
- Retention(3)

Also report AUROC, AUPRC, Brier, ECE, Risk@80, AURC, fold consistency, date bootstrap, and block bootstrap.

Do not call a student successful solely because teacher-student embedding similarity is high. It must preserve reliability utility.

---

# 17. Finance-Specific Inductive Biases

Introduce only as frozen ablations.

## 17.1 Regime conditioning

Same response may have different meaning in different market states.

## 17.2 Temporal smoothness

Optional soft regularizer:

\[
L_{temp}=w_{t,t-1}\|z_t-z_{t-1}\|^2
\]

where \(w\) is high only when pre-outcome market states are similar.

Do not smooth across regime breaks.

## 17.3 Volatility-aware weighting

Optional:

\[
w_t=g(\sigma_t,\text{pre-outcome uncertainty proxy}).
\]

Weights must not use future return magnitude.

## 17.4 Cross-horizon auxiliary tasks

Optional auxiliary predictions:

- 1-day direction
- 5-day direction
- 10-day direction

Each horizon must respect its own temporal leakage boundary.

## 17.5 Soft economic-sign constraints

If an axis has a well-motivated directional prior, use soft ranking constraints rather than hard monotonic laws.

Declare all such priors before evaluation.

---

# 18. Mandatory Baselines

Every relevant stage should include:

1. Market-only
2. Original-only
3. Original + market
4. Response-only
5. Original + raw response surface
6. Flattened nonlinear response model
7. Direction-only / sign-only
8. Confidence-only
9. Agent-ID-only
10. Shuffled response surface
11. Random projection of response surface
12. Feature permutation control

Do not compare only against legacy B6.

---

# 19. Evaluation

Primary:

- AUROC
- AUPRC
- Brier
- ECE

Secondary:

- Risk@80
- AURC
- within-panel ranking
- majority-wrong minority recovery
- calibration slope/intercept if useful

Robustness:

- date-level bootstrap
- block bootstrap
- non-overlap date subset
- regime-stratified evaluation
- per-fold results
- common-support comparisons

---

# 20. Model-Capacity Controls

For any structured teacher, compare with:

- parameter-count-matched MLP
- shallow GBDT
- flattened nonlinear baseline

Report parameter counts and tuning budgets.

Do not give the structured model a larger tuning budget than controls.

---

# 21. Autoresearch Search Discipline

The system must not search until positive.

Use a finite preregistered candidate set.

Recommended maximum:

- Stage A: 3 model classes
- Stage B: 3 regime-aware variants
- Stage C: 2 structured teacher variants
- Stage D: 3 student query budgets
- Stage E: 2 active selector variants

No new candidate family may be introduced after seeing DEV.

All failures remain in the experiment ledger.

---

# 22. Astra6 Role

Astra6 may be used for:

- protocol critique
- intervention validity review
- financial-axis audit
- methodology skepticism
- final synthesis
- paper-safe claim audit

Astra6 must not be used as an outcome-conditioned pseudo-label teacher in the main method.

The main teacher should be trained from ordinary TRAIN correctness supervision after signal existence is established.

---

# 23. Recommended Autoresearch Agent Roles

### Explorer
Propose market-native axes and perturbation construction.

### Financial Methodologist
Check economic plausibility and leakage.

### Statistician
Audit temporal split, bootstrap, calibration, and support.

### Skeptic
Search for simpler explanations.

### Model Auditor
Check parameter/tuning fairness.

### Adjudicator
Issue PASS / FAIL / REFRAME verdicts from frozen criteria.

Do not let the same agent both invent and adjudicate a method without independent review.

---

# 24. Stage-Wise Stop Conditions

## STOP-1 — No market-native signal

If:

\[
O+\mathcal R_{full}\not>O
\]

under robust TRAIN OOF evaluation:

```text
MARKET_NATIVE_SIGNAL_NOT_ESTABLISHED
```

Stop all teacher/student work.

## STOP-2 — No regime increment

If response surface helps but regime conditioning does not:

```text
RESPONSE_SIGNAL_PRESENT_REGIME_INCREMENT_NOT_ESTABLISHED
```

Continue without regime claim.

## STOP-3 — No structured teacher advantage

If:

\[
T_{structured}\not>B_{flat}
\]

then:

```text
STRUCTURED_TEACHER_NOT_ESTABLISHED
```

Do not claim Transformer/relational structure is necessary.

## STOP-4 — Student fails to retain gain

If teacher works but sparse student does not:

```text
TEACHER_SIGNAL_NOT_DISTILLABLE_UNDER_QUERY_BUDGET
```

This is a valid scientific result.

---

# 25. DEV Unlock Gate

DEV may be unlocked only if all are true:

1. Stage A signal exists
2. final intervention construction frozen
3. final market axes frozen
4. final teacher architecture frozen
5. final student architecture/query budget frozen
6. all hyperparameters frozen
7. TRAIN controls completed
8. leakage audits pass
9. experiment ledger complete
10. independent adjudicator signs off

DEV should be evaluated once.

Do not tune after DEV.

---

# 26. Prospective Unlock Gate

The 807 prospective dates remain sealed until:

1. DEV evaluated exactly once
2. final method passed preregistered DEV gate
3. no architecture/threshold changed after DEV
4. weights and preprocessing hashes frozen
5. prospective analysis script frozen
6. `prospective_calls` remained 0 before unlock

---

# 27. Recommended Output Structure

```text
consensus_stress/autoresearch_wave4_market_native/
├── 00_protocol/
│   ├── PROTOCOL.md
│   ├── DATA_MANIFEST.json
│   ├── FEATURE_MANIFEST.json
│   ├── AXIS_MANIFEST.json
│   └── SPLIT_HASHES.json
├── 01_counterfactual_construction/
│   ├── donor_matching.jsonl
│   ├── validity_audit.json
│   └── COUNTERFACTUAL_AUDIT.md
├── 02_response_generation/
│   ├── qwen_responses.jsonl
│   ├── generation_audit.json
│   └── RESPONSE_AUDIT.md
├── 03_stageA_signal/
│   ├── signal_existence.json
│   ├── bootstrap.json
│   └── STAGE_A_RESULTS.md
├── 04_stageB_regime/
├── 05_stageC_teacher/
├── 06_stageD_student/
├── 07_stageE_active/
├── EXPERIMENT_LEDGER.jsonl
├── FINAL_DECISION.json
├── PAPER_SAFE_CLAIMS.md
├── PAPER_UNSAFE_CLAIMS.md
└── NEXT_EXPERIMENTS.md
```

---

# 28. Required Final Decision Labels

Use one of:

```text
MARKET_NATIVE_SIGNAL_NOT_ESTABLISHED
MARKET_NATIVE_SIGNAL_PRESENT
REGIME_CONDITIONING_SUPPORTED
STRUCTURED_TEACHER_SUPPORTED
STRUCTURED_TEACHER_NOT_ESTABLISHED
SPARSE_DISTILLATION_SUPPORTED
TEACHER_SIGNAL_NOT_DISTILLABLE_UNDER_QUERY_BUDGET
DEV_READY
DEV_FAILED
PROSPECTIVE_READY
```

Do not invent softer success labels after seeing results.

---

# 29. Paper-Safe Interpretation if Successful

> Market-native counterfactual perturbations reveal response structure that predicts forecast reliability beyond the original judgment under strict temporal evaluation. A structured teacher captures this response surface, and a sparse student recovers a substantial fraction of the teacher's reliability gain with a limited query budget.

Do not claim:

- true latent belief recovery;
- causal market understanding;
- profitable trading strategy;
- universal financial robustness;
- general deployment reliability.

---

# 30. Paper-Safe Interpretation if Negative

If Stage A fails:

> Under the preregistered market-native perturbation design, the full response surface did not provide stable incremental reliability information beyond the original forecast. We therefore did not proceed to teacher or student distillation.

If Stage C fails:

> The response surface carried reliability information, but the structured teacher did not outperform a capacity-matched flattened nonlinear control.

If Stage D fails:

> The full response surface was informative, but its reliability advantage could not be preserved under the tested sparse-query student budgets.

Each outcome remains scientifically useful and must remain in the ledger.

---

# 31. Recommended First Execution Batch

Do **not** start with the entire 1000+ date cohort and a Transformer.

Run a frozen pilot first.

Suggested:

- 80–120 TRAIN-only dates
- Qwen3.5-4B
- 3 financial axes
- 4 perturbation levels per axis
- 3 agents
- 13 queries per agent-date including original

For 100 dates:

\[
100\times3\times13=3900
\]

model calls.

Pilot goal:

\[
\boxed{
\text{Does the full market-native response surface show conditional reliability value?}
}
\]

Run only Stage A in the pilot.

If Stage A is clearly negative, stop and redesign measurement rather than training a Transformer.

If Stage A is promising, freeze the counterfactual construction and scale to the large Wave-4 cohort.

---

# 32. Preferred Research Sequence

\[
\boxed{
\begin{aligned}
&\text{Wave-4 cohort expansion}\\
\rightarrow&\text{Market-native counterfactual construction}\\
\rightarrow&\text{Qwen full response surface}\\
\rightarrow&\text{Stage A signal existence}\\
\rightarrow&\text{Regime conditioning}\\
\rightarrow&\text{Structured teacher}\\
\rightarrow&\text{Sparse student}\\
\rightarrow&\text{Active probe selector}\\
\rightarrow&\text{DEV}\\
\rightarrow&\text{Prospective}
\end{aligned}}
\]

Most important rule:

\[
\boxed{
\textbf{Never train a distillation student before demonstrating a teacher signal worth distilling.}
}
\]

---

# 33. Core Instruction to the AutoResearch System

> Your job is not to make the hypothesis true. Your job is to determine, under a frozen and auditable protocol, whether market-native counterfactual response behavior contains reliability information beyond the original forecast, whether finance-aware structure adds information beyond generic nonlinear capacity, and whether any such signal can be compressed into a sparse low-query student. Preserve negative results, enforce temporal leakage boundaries, never use DEV or prospective for method selection, and stop immediately when an upstream gate fails.
