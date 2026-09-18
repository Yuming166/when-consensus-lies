# AutoResearch 0918-SP500

# Counterfactual Behavioral State Distillation for Pre-Outcome Agent Reliability

**Date:** 2026-09-18\
**Project:** `when-consensus-lies`\
**Proposed workspace:**
`consensus_stress/autoresearch_sp500_behavioral_state/`\
**Status:** New external-domain stress test following
`autoresearch_distill`\
**Primary verdict space:**
`ADVANCE-METHOD / ADVANCE-BEHAVIORAL-ONLY / REFRAME / DROP`

------------------------------------------------------------------------

## 0. Executive Objective

The previous belief-distillation autoresearch completed a frozen,
auditable train/dev/prospective loop and ended with:

> `REFRAME-BEHAVIORAL-STATE`

The strongest finalist, M07 Hybrid, produced a small prospective
improvement on Qwen but no replicated same-family improvement on Ling.
Explicit pairwise belief distillation failed. Deterministic behavioral
trajectory baseline B5 was already very strong, creating substantial
ceiling effects.

This follow-up must **not** continue tuning the existing BoolQ/VitaminC
formulation.

Instead, test a harder temporally resolved domain in which:

1.  outcomes are genuinely unknown at inference time and revealed later;
2.  individual agent error is common;
3.  wrong-majority and false-consensus panels occur naturally;
4.  agent reliability can vary with market regime;
5.  interventions can operate on temporally valid information;
6.  hindsight supervision can be defined naturally using future realized
    outcomes.

The domain is S&P 500 10-trading-day direction forecasting.

The central scientific question is:

> **Can counterfactual response patterns reveal a predictive behavioral
> state that tells us when an agent should be trusted before the future
> market outcome is known?**

The secondary question is:

> **Can future outcomes provide useful hindsight auxiliary supervision
> for that behavioral state without being available at inference time?**

This project is **not** primarily a trading-alpha project.

Primary endpoints are reliability prediction, calibration,
false-consensus detection, and wrong-majority recovery.

------------------------------------------------------------------------

# 1. Core Hypotheses

## H1 --- Harder-domain hypothesis

The previous benchmark may have become too easy for deterministic
behavioral reliability models.

Test whether S&P 500 forecasting yields:

-   lower individual accuracy;
-   lower B5 reliability AUROC;
-   more disagreement;
-   more 5/5 wrong consensus;
-   more 3/2 and 4/1 wrong-majority panels;
-   greater headroom for learned behavioral-state models.

This hypothesis must be tested before expensive method development.

------------------------------------------------------------------------

## H2 --- Behavioral-state hypothesis

An agent's responses across controlled information interventions contain
a latent predictive structure:

\[ z\_{t,a} = f\_`\theta`{=tex}(X_t, T\_{t,a}) \]

where:

-   \(t\) = forecast date;
-   \(a\) = agent;
-   (X_t) = all temporally valid information available at date (t);
-   (T\_{t,a}) = agent intervention-response trajectory;
-   (z\_{t,a}) = learned behavioral state.

A useful (z\_{t,a}) should predict:

1.  held-out intervention responses;
2.  actual future correctness;
3.  relative reliability within the panel.

------------------------------------------------------------------------

## H3 --- Hindsight-distillation hypothesis

After the future outcome is revealed, an outcome-conditioned teacher can
provide auxiliary supervision:

\[ q\_`\phi`{=tex}(z\_{t,a}`\mid `{=tex}X_t,T\_{t,a},R\_{t,10}) \]

A foresight student must operate without future information:

\[ p\_`\theta`{=tex}(z\_{t,a}`\mid `{=tex}X_t,T\_{t,a}) \]

The question is whether teacher supervision adds prospective value
beyond:

-   raw trajectories;
-   deterministic CST features;
-   true correctness supervision;
-   market-state features;
-   direction-only features.

------------------------------------------------------------------------

## H4 --- Regime-conditioned reliability hypothesis

Agent reliability is not necessarily static.

Model:

\[ r\_{t,a}=g\_`\psi`{=tex}(m_t,z\_{t,a}) \]

where:

\[ m_t = MarketEncoder(X_t) \]

is the market state.

A technical agent may be more useful in one regime and less useful in
another. This is an empirical hypothesis, not an assumption.

------------------------------------------------------------------------

## H5 --- Adaptive probing hypothesis

If behavioral state is useful, not every intervention should be
necessary.

An active selector may choose the next intervention that maximally
reduces reliability uncertainty.

This is a **late-stage extension only**. Do not implement before the
fixed-probe method passes.

------------------------------------------------------------------------

# 2. Non-Claims

Do not claim:

-   recovered true internal belief;
-   ground-truth belief labels;
-   causal understanding of agent cognition;
-   profitable trading strategy;
-   alpha;
-   deployable financial advice;
-   universal market predictability;
-   universal agent competence;
-   teacher posterior as truth;
-   robustness merely because a result appears on one temporal split.

Preferred terminology:

-   behavioral state;
-   counterfactual response profile;
-   item/date-conditioned reliability;
-   outcome-conditioned hindsight auxiliary supervision;
-   foresight reliability estimation;
-   regime-conditioned behavioral reliability.

------------------------------------------------------------------------

# 3. Forecast Target

For forecast date (t), define the primary outcome using the S&P 500
closing level:

\[ R\_{t,10}=`\frac{P_{t+10}}{P_t}`{=tex}-1 \]

Primary binary label:

\[ y_t=`\mathbf{1}`{=tex}\[R\_{t,10}\>0\] \]

where (t+10) means 10 trading days later.

Store both:

-   binary direction (y_t);
-   continuous realized return (R\_{t,10}).

Do not discard the continuous outcome.

Optional robustness horizons, only after the primary protocol is frozen:

-   5 trading days;
-   20 trading days.

The 10-day horizon is primary.

------------------------------------------------------------------------

# 4. Temporal Validity Is Non-Negotiable

Every input must satisfy:

\[ timestamp(input)`\leq `{=tex}t \]

No future information may appear in:

-   price features;
-   macro releases;
-   VIX;
-   yields;
-   credit spreads;
-   news;
-   sentiment;
-   summaries;
-   intervention evidence;
-   teacher-independent student features.

For revised macroeconomic series, use vintage/as-released values where
feasible. If unavailable, explicitly document the limitation and exclude
variables whose revisions create unacceptable leakage.

All news/event summaries must be generated only from documents published
by forecast cutoff time.

No retrospective market descriptions.

Forbidden examples:

-   "The market later fell because..."
-   "Ahead of the selloff..."
-   future-return-derived indicators;
-   revised data not available at time (t), unless explicitly audited
    and justified.

------------------------------------------------------------------------

# 5. Forecast Cutoff

Choose one frozen daily cutoff.

Recommended:

> Forecast after U.S. market close on trading day (t), using information
> available up to the close.

Then predict close-to-close direction from (P_t) to (P\_{t+10}).

This avoids ambiguity about intraday availability.

If a different cutoff is selected, freeze it before data generation.

------------------------------------------------------------------------

# 6. Temporal Splitting

Random train/test splitting is prohibited.

Use walk-forward temporal evaluation.

Minimum structure:

\[ TRAIN `\rightarrow `{=tex}EMBARGO `\rightarrow `{=tex}DEV \]

and later:

\[ TRAIN+DEV `\rightarrow `{=tex}EMBARGO
`\rightarrow `{=tex}PROSPECTIVE_TEST \]

Because 10-day labels overlap, the embargo must be at least the forecast
horizon.

Recommended minimum:

-   10 trading-day embargo.

Prefer a slightly more conservative gap if data volume permits.

No date whose outcome window overlaps a later evaluation partition may
leak into training labels.

------------------------------------------------------------------------

# 7. Stage 0 --- Feasibility Before Method Search

Before any large Astra6 teacher generation or model tournament,
construct a 300--500-date pilot.

Use exactly the same 5-agent protocol intended for the later study.

Measure:

### Agent-level

-   accuracy;
-   balanced accuracy;
-   Brier score if probabilistic predictions are elicited;
-   confidence calibration.

### Panel-level

-   5/5 consensus rate;
-   5/5 wrong-consensus count;
-   4/1 disagreement rate;
-   4/1 wrong-majority count;
-   3/2 disagreement rate;
-   3/2 wrong-majority count;
-   majority-vote accuracy.

### Existing reliability baseline

Reconstruct the closest SP500 analogue of B5.

Measure:

-   agent correctness AUROC;
-   AUPRC;
-   Brier;
-   ECE;
-   within-panel ranking;
-   wrong-majority recovery.

### Feasibility Gate F0

Proceed to full method development if at least one is true:

1.  B5 AUROC is materially below the previous \~0.93--0.95 ceiling;
2.  wrong-majority panels are sufficiently common for meaningful
    evaluation;
3.  5/5 wrong consensus occurs often enough for false-consensus
    analysis;
4.  behavioral interventions show non-degenerate response variance.

Strong preferred condition:

> at least 50 wrong-majority panels can realistically be accumulated in
> the full experiment.

If none holds:

> `DROP-SP500-AS-HARDER-BENCHMARK`

Do not spend a large teacher-call budget.

------------------------------------------------------------------------

# 8. Five-Agent Information Design

Avoid five cosmetically different personas seeing identical information.

The preferred design uses **heterogeneous but controlled information
views**.

## A1 --- Price / Technical

May receive:

-   recent S&P 500 returns;
-   momentum;
-   moving-average ratios;
-   realized volatility;
-   drawdown;
-   volume/market breadth if temporally valid.

------------------------------------------------------------------------

## A2 --- Macro / Rates

May receive:

-   Treasury yields;
-   yield-curve measures;
-   credit spread;
-   recent macro releases;
-   monetary-policy information available by (t).

------------------------------------------------------------------------

## A3 --- Risk / Sentiment

May receive:

-   VIX;
-   volatility term information if available;
-   sentiment indicators;
-   Google Trends if timestamp-valid;
-   risk-appetite proxies.

------------------------------------------------------------------------

## A4 --- News / Events

May receive:

-   temporally valid event/news summaries;
-   major earnings/macro/geopolitical market-relevant events available
    by (t).

Do not use hindsight summaries.

------------------------------------------------------------------------

## A5 --- Integrated

Receives a controlled mixture across sources.

The integrated agent must not simply receive unrestricted extra
information. Freeze its packet budget so comparisons remain
interpretable.

------------------------------------------------------------------------

# 9. Evidence Packet Control

Every agent/date record must store:

-   exact raw input sources;
-   timestamps;
-   normalized evidence units;
-   source category;
-   packet composition;
-   token count;
-   generated summary if applicable;
-   checksum/hash;
-   forecast cutoff.

The intervention generator must operate on these explicit evidence
units.

Do not intervene on hidden model reasoning.

------------------------------------------------------------------------

# 10. Agent Output Schema

Every original and intervention call must return structured output.

Recommended schema:

``` json
{
  "direction": "UP",
  "prob_up": 0.61,
  "confidence": 0.67,
  "key_evidence_ids": ["E02", "E05"],
  "short_justification": "..."
}
```

Requirements:

-   `direction` must be UP or DOWN;
-   `prob_up` in \[0,1\];
-   confidence in \[0,1\];
-   justification short;
-   no hidden CoT requested;
-   evidence references must correspond to supplied evidence IDs.

Use hard direction for primary correctness.

Treat self-reported probabilities/confidence as baselines/features, not
calibrated truth.

------------------------------------------------------------------------

# 11. Intervention Family

The intervention set must separate semantic stability, source
dependence, and directional responsiveness.

## I0 --- Original

Unmodified temporally valid evidence.

------------------------------------------------------------------------

## I1 --- Paraphrase Placebo

Preserve facts and direction while changing wording/order.

Purpose:

-   semantic stability;
-   presentation sensitivity.

------------------------------------------------------------------------

## I2 --- Source Mask

Remove one source family.

Examples:

-   macro mask;
-   sentiment mask;
-   news mask;
-   technical mask.

Only apply masks relevant to the agent's packet.

Purpose:

-   source dependence;
-   information fragility.

------------------------------------------------------------------------

## I3 --- Evidence Unit Removal

Remove one evidence unit while preserving all others.

Purpose:

-   local sensitivity.

------------------------------------------------------------------------

## I4 --- Real Agreeing Evidence

Add an independent, timestamp-valid evidence unit that points in the
same direction as the agent's current forecast.

Direction is defined relative to the **current agent prediction**, not
future truth.

------------------------------------------------------------------------

## I5 --- Real Contradicting Evidence

Add an independent, timestamp-valid evidence unit that points against
the current agent forecast.

Again:

> direction is relative to the current forecast, not realized future
> outcome.

This is critical to avoid the previous natural-pair direction confound.

------------------------------------------------------------------------

## I6 --- Source Substitution

Replace one evidence representation with a semantically equivalent or
closely matched alternative source/representation where feasible.

Purpose:

-   source-specific sensitivity.

------------------------------------------------------------------------

# 12. Intervention Validity Audit

Every agreeing/contradicting evidence intervention must pass:

1.  timestamp validity;
2.  factual validity;
3.  independence check;
4.  direction annotation;
5.  no future outcome leakage.

Use a mixture of:

-   deterministic checks;
-   independent LLM validation;
-   manual audit on a stratified sample.

Store:

``` text
intervention_validity.json
```

Do not assume generated counterevidence is valid because the generator
says so.

------------------------------------------------------------------------

# 13. Behavioral Trajectory

For date (t), agent (a):

\[ T\_{t,a}= { O\^{orig}, O\^{para}, O\^{mask}, O\^{remove}, O\^{agree},
O\^{contradict}, O\^{swap} } \]

Derive deterministic features including:

-   original direction;
-   original probability;
-   paraphrase flip;
-   probability shift under paraphrase;
-   source-mask flip;
-   removal flip;
-   agree flip;
-   contradict flip;
-   probability movement toward intervention direction;
-   confidence shift;
-   source sensitivity;
-   directional selectivity;
-   response entropy.

Do not assume a single scalar is sufficient.

------------------------------------------------------------------------

# 14. Directional Response Profile

Explicitly construct:

\[ `\alpha`{=tex}\_{t,a}=ResponseStrength(CONTRADICT) \]

\[ `\beta`{=tex}\_{t,a}=ResponseStrength(AGREE) \]

and a simple diagnostic:

\[ D\_{t,a}=`\alpha`{=tex}*{t,a}-`\beta`{=tex}*{t,a} \]

The exact response-strength definition must be frozen before prospective
evaluation.

Candidate definitions:

-   hard flip;
-   change in `prob_up`;
-   signed movement relative to intervention direction.

Compare all learned models against a direction-only baseline.

------------------------------------------------------------------------

# 15. Proposed Main Method

# Counterfactual Behavioral State Distillation (CBSD)

CBSD has four core components.

## Component A --- Market State Encoder

\[ m_t=f_m(X_t) \]

Inputs may include structured market features and controlled text/event
representations.

Keep this encoder modest.

The project is not a competition to build the largest market forecaster.

------------------------------------------------------------------------

## Component B --- Behavioral State Encoder

\[ z\_{t,a}=f_b(T\_{t,a},X\_{t,a}) \]

The representation should capture how the agent responds to controlled
information changes.

------------------------------------------------------------------------

## Component C --- Regime-Conditioned Reliability Head

\[ `\hat `{=tex}r\_{t,a} = `\sigma`{=tex}( g(m_t,z\_{t,a}) ) \]

where:

\[
`\hat `{=tex}r\_{t,a}`\approx `{=tex}P(C\_{t,a}=1`\mid `{=tex}X_t,T\_{t,a})
\]

and:

\[ C\_{t,a} = `\mathbf 1`{=tex}\[`\hat `{=tex}y\_{t,a}=y_t\] \]

------------------------------------------------------------------------

## Component D --- Hindsight Auxiliary Teacher

Teacher sees future realized outcome during TRAIN/DEV only:

\[ q\_`\phi`{=tex}(z\^H\_{t,a}`\mid `{=tex}X_t,T\_{t,a},R\_{t,10}) \]

Student never sees (R\_{t,10}) at inference:

\[ p\_`\theta`{=tex}(z\^F\_{t,a}`\mid `{=tex}X_t,T\_{t,a}) \]

Teacher supervision is auxiliary, not ground truth.

------------------------------------------------------------------------

# 16. Masked Intervention Modeling

This is the primary self-supervised behavioral-state objective.

Given intervention responses:

\[ T\_{t,a}=(T_1,`\ldots`{=tex},T_K) \]

mask one or more responses and predict them:

\[ p\_`\theta`{=tex}(T_k`\mid `{=tex}T\_{`\setminus `{=tex}k},X_t) \]

Loss:

\[ `\mathcal `{=tex}L\_{BR} = -`\sum`{=tex}*k
`\log `{=tex}p*`\theta`{=tex}(T_k`\mid `{=tex}T\_{`\setminus `{=tex}k},X_t)
\]

For probabilistic outputs, also predict:

-   direction;
-   probability shift;
-   confidence shift.

This objective provides a direct falsifiable test:

> Does the representation contain enough behavioral structure to predict
> unseen agent responses?

------------------------------------------------------------------------

# 17. Held-Out Intervention Prediction

Run leave-one-intervention-out evaluation.

Examples:

-   Original + Para + Agree → predict Contradict;
-   Original + Contradict + Para → predict Mask;
-   Original + Mask + Contradict → predict Agree.

Metrics:

-   direction-response accuracy;
-   response AUROC where appropriate;
-   probability MAE;
-   Brier score.

### Gate B0

If learned state cannot predict held-out intervention behavior above
simple trajectory baselines:

> do not call it a latent behavioral state.

Use `trajectory representation` instead.

------------------------------------------------------------------------

# 18. True Correctness Objective

Use actual future outcome during training:

\[ `\mathcal `{=tex}L_C = BCE( `\hat `{=tex}r\_{t,a}, C\_{t,a} ) \]

This is the primary supervised reliability target.

Pseudo-labels must not replace available true correctness labels without
a specific ablation.

------------------------------------------------------------------------

# 19. Hindsight Distillation Objective

Teacher produces structured posterior targets rather than a single
invented "belief score."

Recommended teacher fields:

``` json
{
  "posterior_correctness": 0.0,
  "behavioral_consistency": 0.0,
  "counterevidence_responsiveness": 0.0,
  "source_fragility": 0.0,
  "uncertainty": 0.0,
  "teacher_confidence": 0.0
}
```

Whenever a field is directly computable from observed responses, compute
it programmatically instead of asking the teacher.

Distillation loss:

\[ `\mathcal `{=tex}L_D =
KL(q\_`\phi`{=tex}(z^H)`\Vert `{=tex}p\_`\theta`{=tex}(z^F)) \]

or field-wise soft-target losses.

Teacher rationale must not become student input.

------------------------------------------------------------------------

# 20. Temporal Consistency Objective

Behavioral state may vary smoothly when market conditions are similar.

Optional objective:

\[ `\mathcal `{=tex}L_T = w\_{t,t'} \|z\_{t,a}-z\_{t',a}\|\^2 \]

where (w\_{t,t'}) is high only when market states are similar.

Do not enforce smoothness blindly across regime shifts.

Compare:

-   no temporal regularization;
-   adjacent-date regularization;
-   market-similarity-weighted regularization.

This component is optional until the simpler model works.

------------------------------------------------------------------------

# 21. Full Candidate Objective

Primary candidate:

\[ `\mathcal `{=tex}L = `\mathcal `{=tex}L_C +
`\lambda`{=tex}*{BR}`\mathcal `{=tex}L*{BR} +
`\lambda`{=tex}\_D`\mathcal `{=tex}L_D +
`\lambda`{=tex}\_T`\mathcal `{=tex}L_T \]

Use a small preregistered hyperparameter grid.

Example:

\[ `\lambda`{=tex}\_{BR}`\in`{=tex}{0.1,0.3,1.0} \]

\[ `\lambda`{=tex}\_D`\in`{=tex}{0,0.1,0.3} \]

\[ `\lambda`{=tex}\_T`\in`{=tex}{0,0.05,0.1} \]

Do not perform massive search.

The prospective test must never be used for tuning.

------------------------------------------------------------------------

# 22. Aggregation

Given reliability estimates:

\[ r\_{t,1},`\ldots`{=tex},r\_{t,5} \]

construct normalized weights:

\[ w\_{t,a} = `\frac{\exp(r_{t,a}/\tau)}`{=tex}
{`\sum`{=tex}*j`\exp`{=tex}(r*{t,j}/`\tau`{=tex})} \]

Then aggregate original agent probabilities:

\[ P_t(UP) = `\sum`{=tex}*a w*{t,a}P\_{t,a}(UP) \]

Primary aggregated direction:

\[ `\hat `{=tex}y_t=`\mathbf1`{=tex}\[P_t(UP)\>0.5\] \]

Freeze temperature using DEV only.

Also report a temperature-free weighted-score variant if feasible.

------------------------------------------------------------------------

# 23. Required Baselines

## B0 --- Market class prior

## B1 --- Majority vote

## B2 --- Mean agent probability

## B3 --- Confidence-weighted vote

## B4 --- Historical rolling agent accuracy

Uses only past resolved outcomes.

## B5 --- Market-feature-only reliability model

No intervention trajectory.

## B6 --- Raw deterministic CST trajectory model

SP500 analogue of existing B5.

## B7 --- Direction-only model

Uses agree/contradict response features.

## B8 --- Behavioral-state model without teacher

Masked intervention modeling + correctness.

## B9 --- Behavioral-state + hindsight teacher

Main CBSD candidate.

## B10 --- Hindsight pseudo-label only

Negative/control baseline.

## B11 --- Direct Astra judge

Pre-outcome judge with original panel only.

## B12 --- Direct Astra judge + trajectories

Tests whether simply exposing CST responses to a strong LLM is
sufficient.

------------------------------------------------------------------------

# 24. Four-Way Core Ablation

Before expanding the method, run:

### A --- Majority

\[ Vote(A_1,`\ldots`{=tex},A_5) \]

### B --- Raw trajectory

\[ T`\rightarrow `{=tex}r \]

### C --- Behavioral state

\[ T `\xrightarrow{masked\ intervention}`{=tex} z `\rightarrow `{=tex}r
\]

### D --- Behavioral state + hindsight distillation

\[ T `\rightarrow `{=tex}z + q\_`\phi`{=tex}(z`\mid `{=tex}R\_{t,10})
`\rightarrow `{=tex}r \]

The key desired ordering is:

\[ B\<C\<D \]

Interpretation:

-   if (B\<C): behavioral-state modeling works;
-   if (C\<D): hindsight auxiliary distillation adds value;
-   if (B=C=D): stop method expansion.

------------------------------------------------------------------------

# 25. Parallel AutoResearch Agents

Use independent agents with isolated output directories.

## R01 --- Temporal Data Auditor

Tasks:

-   inspect all feature timestamps;
-   detect look-ahead;
-   detect revised-data risks;
-   verify 10-day label construction;
-   verify embargo;
-   verify overlapping-label handling.

Output:

`R01_temporal_audit.md`

------------------------------------------------------------------------

## R02 --- Hardness Auditor

Tasks:

-   quantify agent accuracy;
-   disagreement distribution;
-   wrong-majority counts;
-   false-consensus counts;
-   B6 ceiling;
-   class balance.

Decision:

`HARD_ENOUGH / BORDERLINE / TOO_EASY / TOO_NOISY`

------------------------------------------------------------------------

## R03 --- Intervention Designer

Design and validate:

-   paraphrase;
-   mask;
-   remove;
-   agree;
-   contradict;
-   source substitution.

Must explicitly separate direction relative to current prediction from
future truth.

------------------------------------------------------------------------

## R04 --- Counterevidence Validity Auditor

Independently audit generated interventions.

Measure:

-   timestamp validity;
-   factual validity;
-   directional validity;
-   independence;
-   leakage.

------------------------------------------------------------------------

## R05 --- Deterministic Baseline Builder

Implement B0--B7.

No teacher calls.

------------------------------------------------------------------------

## R06 --- Masked Behavioral Modeling

Implement B8.

Primary question:

> Can partial trajectories predict held-out intervention responses?

------------------------------------------------------------------------

## R07 --- Hindsight Teacher Designer

Design structured outcome-conditioned auxiliary targets.

Must not output "true belief."

Run stability pilot before scaling.

------------------------------------------------------------------------

## R08 --- Teacher Stability Auditor

Repeat teacher generation.

Measure:

-   field stability;
-   ranking stability;
-   relationship to correctness;
-   relationship to future return magnitude;
-   relationship to deterministic trajectory features.

------------------------------------------------------------------------

## R09 --- CBSD Main Method

Implement B9.

Compare:

-   correctness only;
-   -   behavioral reconstruction;
-   -   teacher;
-   full objective.

------------------------------------------------------------------------

## R10 --- Regime-Conditioned Reliability

Test:

\[ r\_{t,a}=g(m_t,z\_{t,a}) \]

versus:

\[ r\_{t,a}=g(z\_{t,a}) \]

Do not overfit regime labels.

Prefer continuous market-state representations over arbitrary bull/bear
categories.

------------------------------------------------------------------------

## R11 --- Temporal Consistency

Test optional temporal regularization.

Must demonstrate benefit on DEV before prospective advancement.

------------------------------------------------------------------------

## R12 --- Aggregation / Minority Recovery

Evaluate whether reliability weighting improves:

-   wrong-majority recovery;
-   false-consensus abstention;
-   overall panel accuracy.

------------------------------------------------------------------------

## R13 --- Direct Astra Judge Baseline

Compare:

-   original only;
-   original + confidence;
-   original + trajectories.

Use frozen prompts.

------------------------------------------------------------------------

## R14 --- Cross-Regime Auditor

Evaluate performance by predeclared descriptive strata, e.g.:

-   high/low volatility;
-   positive/negative recent momentum;
-   high/low credit stress.

Do not cherry-pick favorable regimes.

------------------------------------------------------------------------

## R15 --- Leakage / Permutation Red Team

Run:

-   shuffled future labels;
-   shuffled teacher targets;
-   shuffled trajectories;
-   shuffled agent IDs;
-   shifted timestamps;
-   market-feature-only controls;
-   direction-only controls.

Any suspicious persistence of performance must be investigated.

------------------------------------------------------------------------

## R16 --- Independent Final Synthesizer

Must not develop any method.

Receives all frozen results and issues final verdict.

------------------------------------------------------------------------

# 26. Teacher Stability Gate

Before generating full teacher targets:

Use at least 100--150 TRAIN/DEV date-agent/panel units, stratified
across:

-   correct/incorrect;
-   consensus/disagreement;
-   wrong-majority;
-   volatility states;
-   Qwen/Ling if both are used.

Run at least 3 independent teacher generations.

Gate passes only if:

1.  structured targets have nontrivial stability;
2.  teacher outputs are not almost deterministic restatements of
    correctness;
3.  useful fields retain variance conditional on correctness;
4.  no timestamp leakage is found.

If failed:

> remove teacher from main method and continue behavioral-state-only.

------------------------------------------------------------------------

# 27. Model Families

At minimum use two agent model families if feasible.

Preferred continuity:

-   Qwen family;
-   Ling family.

Astra6 may be used for:

-   intervention validation;
-   hindsight teacher;
-   direct judge baseline;
-   method design;
-   independent synthesis.

Do not require Astra6 as the only forecasting agent.

Cross-family evaluation is valuable but secondary to strict temporal
validity.

------------------------------------------------------------------------

# 28. Prospective Evaluation

Once all method choices are frozen:

1.  hash protocol;
2.  hash configs;
3.  record Git commit;
4.  freeze prompts;
5.  freeze model versions;
6.  freeze hyperparameters;
7.  run PROSPECTIVE_TEST once;
8.  reveal outcomes only according to protocol;
9.  perform no post-test tuning.

Target:

-   = 200 forecast dates;

-   preferably enough to yield \>= 50 wrong-majority panels across the
    full evaluation design.

If 200 dates do not yield enough hard panels, extend the prospective
period under the already frozen protocol rather than selectively
sampling based on outcomes.

------------------------------------------------------------------------

# 29. Primary Metrics

## Agent correctness

-   AUROC;
-   AUPRC;
-   Brier;
-   ECE.

## Within-panel ranking

-   pairwise correct-vs-incorrect ranking;
-   top-1 correct-agent rate;
-   MRR where meaningful.

## Panel decision

-   majority accuracy;
-   reliability-weighted accuracy;
-   wrong-majority recovery;
-   number corrected;
-   number broken;
-   net corrections.

## False consensus

Among 5/5 panels:

-   wrong-consensus detection AUROC;
-   Risk@coverage;
-   selective risk.

## Behavioral-state validity

-   held-out intervention response accuracy;
-   probability MAE/Brier;
-   leave-one-intervention-out performance.

------------------------------------------------------------------------

# 30. Secondary Financial Metrics

Only after primary reliability analysis.

Optional:

-   sign strategy accuracy;
-   cumulative return of a simple fixed-rule strategy;
-   Sharpe;
-   drawdown.

These must be explicitly secondary.

If reported:

-   include transaction-cost assumptions;
-   avoid optimizing trading rules on prospective test;
-   do not claim alpha without appropriate financial baselines and
    statistical controls.

A strong reliability paper does not require profitable trading.

------------------------------------------------------------------------

# 31. Statistical Protocol

Bootstrap by forecast date, not by individual agent row.

Use:

-   paired date bootstrap;
-   95% confidence intervals;
-   exact counts for small wrong-majority subsets.

For overlapping 10-day outcomes, also run a dependence-aware robustness
analysis, e.g.:

-   block bootstrap;
-   non-overlapping-date subsample.

Do not treat adjacent dates as independent observations.

------------------------------------------------------------------------

# 32. Hard-Case Analysis

Predefine a hard subset using **pre-outcome quantities only**.

Candidate criteria:

-   3/2 disagreement;
-   4/1 disagreement;
-   small B6 reliability margin;
-   high agent confidence despite disagreement;
-   high behavioral ambiguity.

Never define the hard set using whether the future prediction turned out
wrong.

Then test whether B8/B9 improve most where deterministic CST is
uncertain.

This directly tests the ceiling-effect hypothesis without outcome-based
selection.

------------------------------------------------------------------------

# 33. False-Consensus Challenge

Analyze:

\[ 5/5 correct \]

versus:

\[ 5/5 wrong \]

Primary question:

> Can behavioral stress responses identify unreliable unanimous
> forecasts before the 10-day outcome is known?

Compare:

-   confidence;
-   market uncertainty;
-   B6 raw CST;
-   B7 direction-only;
-   B8 behavioral state;
-   B9 CBSD.

This is the closest financial analogue of the original
`When Consensus Lies` question.

------------------------------------------------------------------------

# 34. Wrong-Majority Challenge

For:

\[ 3:2 `\text{ or }`{=tex} 4:1 \]

where majority is later revealed wrong, evaluate whether pre-outcome
reliability weighting places more weight on the correct minority.

Report:

-   number of eligible panels;
-   B1 majority baseline;
-   B3 confidence weighting;
-   B4 historical accuracy;
-   B6 raw CST;
-   B8 behavioral state;
-   B9 CBSD;
-   direct judge.

Do not make a strong minority-recovery claim from tiny (n).

------------------------------------------------------------------------

# 35. Active Behavioral Stress Testing

# OPTIONAL --- only after B8/B9 pass

If fixed-probe behavioral state works, add an adaptive selector.

At step (k), choose:

\[ I\^\* = `\arg`{=tex}`\max`{=tex}\_I `\mathbb `{=tex}E\[
H(r\_{t,a}`\mid `{=tex}O\_{1:k}) -
H(r\_{t,a}`\mid `{=tex}O\_{1:k},O_I)\] \]

Compare equal call budgets:

-   random probe;
-   fixed probe order;
-   heuristic direction-first;
-   learned information-gain selector.

Budgets:

-   B=1;
-   B=2;
-   B=3.

Metrics:

-   reliability AUROC per call;
-   wrong-majority recovery per call;
-   false-consensus detection per call.

Do not implement this unless the fixed behavioral-state representation
has already passed.

------------------------------------------------------------------------

# 36. Stage Gates

## G0 --- Temporal Integrity

PASS only if no material future leakage is found.

Failure:

`STOP`

------------------------------------------------------------------------

## G1 --- Hardness

PASS if the new domain provides meaningful additional headroom/hard
cases.

Failure:

`DROP-SP500-AS-HARDER-BENCHMARK`

------------------------------------------------------------------------

## G2 --- Intervention Validity

PASS if agree/contradict/mask interventions are temporally valid and
behaviorally non-degenerate.

Failure:

`REDESIGN-INTERVENTIONS`

------------------------------------------------------------------------

## G3 --- Behavioral-State Validity

PASS if masked/held-out intervention prediction beats simple baselines.

Failure:

`KEEP-RAW-TRAJECTORY`

------------------------------------------------------------------------

## G4 --- Reliability Gain

PASS if B8 improves prospectively over B6 on at least one meaningful
reliability endpoint with paired uncertainty supporting the effect.

Failure:

`NO-BEHAVIORAL-STATE-GAIN`

------------------------------------------------------------------------

## G5 --- Hindsight Increment

PASS if B9 improves over B8 prospectively.

This is the critical test of the original distillation idea.

Failure:

`DROP-HINDSIGHT-DISTILLATION`

This does not invalidate behavioral-state modeling.

------------------------------------------------------------------------

## G6 --- Downstream Utility

Strong PASS if learned reliability improves either:

-   wrong-majority recovery;
-   false-consensus selective risk;

without unacceptable degradation in overall panel accuracy/calibration.

------------------------------------------------------------------------

## G7 --- Cross-Family / Temporal Robustness

Strongest result requires evidence across:

-   more than one model family;
-   more than one temporal evaluation window or walk-forward fold.

A single positive split is insufficient for a universal claim.

------------------------------------------------------------------------

# 37. Stop Rules

Stop escalating complexity if:

1.  S&P500 is not actually harder in the needed way;
2.  intervention responses are mostly noise;
3.  held-out intervention prediction fails;
4.  B8 does not beat raw trajectory B6;
5.  teacher targets add no value beyond B8;
6.  gains vanish under direction-only control;
7.  results depend on leakage-prone features;
8.  only trading PnL improves while reliability metrics do not;
9.  prospective gains disappear under block/non-overlap robustness;
10. gains appear only after prospective-test tuning.

Negative results must be preserved.

------------------------------------------------------------------------

# 38. Required Ablation Matrix

For every finalist:

  ---------------------------------------------------------------------------------
  Variant       Market          Raw   Direction       Masked   Hindsight   Temporal
                 state   trajectory               behavioral     teacher       reg.
                                                    pretrain             
  --------- ---------- ------------ ----------- ------------ ----------- ----------
  B5                 ✓                                                   

  B6          optional            ✓    implicit                          

  B7          optional                        ✓                          

  B8                 ✓            ✓           ✓            ✓             

  B9                 ✓            ✓           ✓            ✓           ✓ 

  B9+T               ✓            ✓           ✓            ✓           ✓          ✓
  ---------------------------------------------------------------------------------

Also run:

-   shuffled teacher;
-   shuffled trajectory;
-   shuffled agent ID;
-   no confidence;
-   no market state;
-   no direction;
-   no text/news;
-   structured-data-only if applicable.

------------------------------------------------------------------------

# 39. Required Final Tables

## Table 1 --- Domain Hardness

Columns:

-   model family;
-   individual accuracy;
-   majority accuracy;
-   5/5 rate;
-   5/5 wrong count;
-   4/1 wrong count;
-   3/2 wrong count;
-   B6 AUROC.

------------------------------------------------------------------------

## Table 2 --- Behavioral-State Validity

Columns:

-   method;
-   held-out intervention accuracy;
-   response Brier;
-   probability MAE.

------------------------------------------------------------------------

## Table 3 --- Agent Reliability

Columns:

-   AUROC;
-   AUPRC;
-   Brier;
-   ECE;
-   paired delta vs B6;
-   paired delta vs B8.

------------------------------------------------------------------------

## Table 4 --- False Consensus

Columns:

-   method;
-   N unanimous;
-   N wrong;
-   AUROC;
-   Risk@80;
-   AURC if appropriate.

------------------------------------------------------------------------

## Table 5 --- Wrong-Majority Recovery

Columns:

-   method;
-   N eligible;
-   recovered;
-   broken;
-   net corrected;
-   recovery rate.

------------------------------------------------------------------------

## Table 6 --- Ablations

Include:

-   no market state;
-   no direction;
-   no masked modeling;
-   no teacher;
-   shuffled teacher;
-   no temporal regularization.

------------------------------------------------------------------------

# 40. Required Figures

## Figure A --- Method Overview

Flow:

``` text
As-of-time market evidence
        ↓
Five heterogeneous agents
        ↓
Controlled counterfactual interventions
        ↓
Agent response trajectories
        ↓
Behavioral State Encoder
        ↓
Regime-conditioned reliability
        ↓
Reliability-weighted panel decision
```

Training-only branch:

``` text
Future 10-day outcome
        ↓
Hindsight auxiliary teacher
        ↓
Behavioral-state distillation
```

Clearly mark future outcome as **TRAINING ONLY / NOT AVAILABLE AT
INFERENCE**.

------------------------------------------------------------------------

## Figure B --- Behavioral Response Profile

Show one example date with:

-   five original forecasts;
-   responses to agree/contradict/mask;
-   inferred reliability;
-   later realized outcome.

Do not expose or imply hidden CoT.

------------------------------------------------------------------------

## Figure C --- Hardness Comparison

Compare previous benchmark vs SP500 on:

-   B5/B6 reliability ceiling;
-   disagreement rate;
-   wrong-majority rate;
-   false-consensus count.

Use only directly comparable quantities.

------------------------------------------------------------------------

## Figure D --- Core Ablation

Show:

\[ B6 `\rightarrow `{=tex}B8 `\rightarrow `{=tex}B9 \]

with paired prospective deltas.

------------------------------------------------------------------------

# 41. Directory Structure

Create:

``` text
consensus_stress/autoresearch_sp500_behavioral_state/
├── 00_protocol/
│   ├── FROZEN_PROTOCOL.md
│   ├── protocol_hash.json
│   ├── temporal_split.json
│   └── feature_availability.md
├── 01_data/
│   ├── forecast_dates.csv
│   ├── evidence_manifest.jsonl
│   ├── outcome_manifest.csv
│   └── leakage_audit.json
├── 02_feasibility/
│   ├── hardness_report.md
│   ├── panel_statistics.json
│   └── decision.md
├── 03_interventions/
│   ├── intervention_spec.md
│   ├── validity_results.json
│   └── audit.md
├── 04_trajectories/
│   ├── trajectory_schema.md
│   └── derived_features.parquet
├── 05_baselines/
├── 06_behavioral_state/
├── 07_hindsight_teacher/
├── 08_cbsd/
├── 09_ablation/
├── 10_cross_family/
├── 11_hard_cases/
├── 12_prospective/
├── 13_red_team/
└── 14_synthesis/
```

------------------------------------------------------------------------

# 42. Reproducibility Requirements

Every experiment must record:

-   Git commit;
-   model name/version;
-   prompts;
-   temperature;
-   seeds;
-   forecast cutoff;
-   data timestamps;
-   input hashes;
-   output hashes;
-   train/dev/test date ranges;
-   embargo;
-   intervention version;
-   teacher version;
-   hyperparameters.

Do not modify frozen artifacts in place.

------------------------------------------------------------------------

# 43. Resource Policy

Use local computation for:

-   market feature engineering;
-   label construction;
-   timestamp validation;
-   deterministic interventions where possible;
-   metrics;
-   bootstrap;
-   model training when lightweight;
-   permutation tests.

Use Astra6 strategically for:

-   intervention design;
-   independent counterevidence validation;
-   hindsight teacher;
-   direct judge baseline;
-   red-team reasoning;
-   final synthesis.

Before large-scale calls:

1.  estimate cost;
2.  run feasibility;
3.  run intervention validity pilot;
4.  run teacher stability pilot;
5.  pass relevant gates.

------------------------------------------------------------------------

# 44. Recommended Execution Waves

## Wave 0 --- Data and Leakage

R01 + data builder.

No model research until temporal integrity passes.

------------------------------------------------------------------------

## Wave 1 --- Hardness Pilot

R02 + R05.

300--500 dates.

Decision:

> Is SP500 actually a better test bed?

------------------------------------------------------------------------

## Wave 2 --- Intervention Pilot

R03 + R04.

Validate behavioral variance and counterevidence direction.

------------------------------------------------------------------------

## Wave 3 --- Behavioral State

R06 + R10.

No teacher yet.

Primary test:

\[ B6 `\overset{?}{<}`{=tex} B8 \]

------------------------------------------------------------------------

## Wave 4 --- Hindsight Distillation

R07 + R08 + R09.

Primary test:

\[ B8 `\overset{?}{<}`{=tex} B9 \]

------------------------------------------------------------------------

## Wave 5 --- Utility and Baselines

R12 + R13 + R14.

Focus:

-   false consensus;
-   wrong-majority recovery;
-   direct judge comparison.

------------------------------------------------------------------------

## Wave 6 --- Red Team

R15.

No candidate advances without passing leakage/permutation controls.

------------------------------------------------------------------------

## Wave 7 --- Prospective Test

Freeze once.

Run once.

No tuning afterward.

------------------------------------------------------------------------

## Wave 8 --- Independent Synthesis

R16.

------------------------------------------------------------------------

# 45. Final Synthesis Questions

The independent synthesis agent must answer:

1.  Was SP500 meaningfully harder than the previous benchmark?
2.  Did the domain reduce the deterministic reliability ceiling?
3.  Were wrong-majority and false-consensus panels sufficiently
    frequent?
4.  Were interventions temporally valid?
5.  Did controlled trajectories contain predictive reliability signal?
6.  Could partial trajectories predict held-out intervention responses?
7.  Did masked behavioral modeling improve over raw trajectory B6?
8.  Did market-state conditioning help?
9.  Did hindsight auxiliary supervision improve over
    behavioral-state-only B8?
10. Did the teacher add information beyond future correctness
    restatement?
11. Did gains survive direction-only controls?
12. Did gains survive permutation tests?
13. Did gains survive dependence-aware temporal statistics?
14. Did reliability weighting recover wrong-majority cases?
15. Did it detect false unanimous consensus?
16. Did results replicate across model families?
17. Did results replicate across temporal windows?
18. Is `behavioral state` terminology empirically justified?
19. Is `distillation` justified as a contribution?
20. Should active probing be attempted?

------------------------------------------------------------------------

# 46. Final Verdict

The final synthesis must return exactly one:

## `ADVANCE-METHOD`

Requirements:

-   B8 \> B6 prospectively;
-   B9 \> B8 prospectively;
-   gains survive controls;
-   meaningful downstream utility;
-   no material leakage.

Interpretation:

> Counterfactual behavioral-state modeling works, and hindsight outcome
> supervision provides additional pre-outcome reliability value.

------------------------------------------------------------------------

## `ADVANCE-BEHAVIORAL-ONLY`

Requirements:

-   B8 \> B6;
-   B9 does not reliably beat B8.

Interpretation:

> Behavioral-state modeling works, but hindsight distillation does not
> add robust value.

------------------------------------------------------------------------

## `REFRAME`

Use when:

-   some predictive effects exist;
-   interpretation or generality is narrower than planned.

------------------------------------------------------------------------

## `DROP`

Use when:

-   harder domain does not create meaningful headroom;
-   behavioral state fails;
-   effects are explained by leakage/direction/trivial baselines;
-   prospective evidence is negative.

------------------------------------------------------------------------

# 47. Paper-Safe Success Claim

If the strongest outcome occurs, preferred wording is approximately:

> We model agent reliability through counterfactual behavioral states
> derived from controlled, temporally valid evidence interventions. On a
> temporally resolved market forecasting task, these states predict
> held-out behavioral responses and future agent correctness.
> Outcome-conditioned hindsight supervision is used only during training
> and, when supported by prospective evaluation, provides auxiliary
> information for outcome-blind reliability estimation.

Do not use stronger wording unless directly justified.

------------------------------------------------------------------------

# 48. The Most Important Experiment

The project should ultimately be able to produce cases of the following
form:

``` text
Forecast date: t
Future 10-day outcome: hidden

Agents:
A1: UP
A2: UP
A3: UP
A4: DOWN
A5: DOWN

Raw majority: UP

Behavioral stress:
A1: unstable under paraphrase and weak contradict response
A2: source-fragile
A3: follows agreeing evidence but ignores contradicting evidence
A4: stable and selectively responsive to valid counterevidence
A5: stable and selectively responsive to valid counterevidence

Pre-outcome reliability model:
weight(A4,A5) > weight(A1,A2,A3)

System prediction:
DOWN

Ten trading days later:
realized outcome = DOWN
```

One anecdote proves nothing.

But if this pattern occurs reproducibly across a frozen temporal test
set, with paired statistical evidence and no future leakage, it directly
supports the scientific thesis:

> **Controlled counterfactual behavior can reveal when a minority agent
> should be trusted over an apparently confident majority.**

------------------------------------------------------------------------

# 49. Minimal First Run

Do not immediately execute the entire project.

First run only:

### Step 1

Construct 300--500 temporally valid forecast dates.

### Step 2

Run 5 agents on original evidence.

### Step 3

Measure:

-   individual accuracy;
-   majority accuracy;
-   disagreement;
-   wrong-majority count;
-   5/5 wrong count.

### Step 4

Run a minimal intervention set:

-   Original;
-   Paraphrase;
-   Mask;
-   Agree;
-   Contradict.

### Step 5

Build B6 raw trajectory baseline.

### Step 6

Build B8 masked behavioral-state model without any teacher.

### Step 7

Compare:

\[ B6 `\overset{?}{<}`{=tex} B8 \]

Only if positive or strongly suggestive:

### Step 8

Generate hindsight teacher targets.

### Step 9

Build B9.

### Step 10

Compare:

\[ B8 `\overset{?}{<}`{=tex} B9 \]

This staged execution is mandatory to avoid spending a large model-call
budget on a domain or representation that does not provide useful
headroom.

------------------------------------------------------------------------

# 50. North-Star Scientific Chain

The desired evidence chain is:

\[ `\text{Hard temporally resolved task}`{=tex} \]

\[ `\Downarrow`{=tex} \]

\[ `\text{Natural agent disagreement and false consensus}`{=tex} \]

\[ `\Downarrow`{=tex} \]

\[ `\text{Controlled as-of-time counterfactual interventions}`{=tex} \]

\[ `\Downarrow`{=tex} \]

\[ `\text{Predictive behavioral response state}`{=tex} \]

\[ `\Downarrow`{=tex} \]

\[ `\text{Regime-conditioned agent reliability}`{=tex} \]

\[ `\Downarrow`{=tex} \]

\[ `\text{Outcome-conditioned training signal}`{=tex} \]

\[ `\Downarrow`{=tex} \]

\[ `\text{Outcome-blind prospective reliability}`{=tex} \]

\[ `\Downarrow`{=tex} \]

\[
`\boxed{\text{False-consensus detection + trustworthy-minority recovery}}`{=tex}
\]

The goal is not to force this chain to succeed.

The goal is to test every arrow independently and preserve whichever
parts survive.
