# AutoResearch Generation 2 --- Astra6 Hindsight Target Replication & Decomposition

**Date:** 2026-09-18\
**Project:** `when-consensus-lies`\
**Parent workspace:** `consensus_stress/autoresearch_astra_credit/`\
**Research LLM:** PRIVATE RELAY `gpt-6-astra` ONLY\
**DEV:** LOCKED\
**PROSPECTIVE (807 dates):** SEALED

## 0. Immutable Generation-1 record

Do not edit or retroactively pass Generation 1.

Frozen facts: - Algorithmic credit distillability: mean Spearman ≈
0.0525 vs frozen threshold \>=0.20 → `DROP_ALGORITHMIC_PSEUDOLABEL`. -
Astra6 teacher: 300 requested, 300 recorded, 299 valid, 1 transport
failure; all successful model returns were `gpt-6-astra`; zero
fallback. - 99/100 complete triplets. - Mean pairwise credit Spearman
0.6709 (threshold 0.30). - Top-credit agreement 0.8620 (threshold
0.40). - Mean entropy 0.8904 (requirement \<1.37). - Because
completeness required \>=100 complete triplets, frozen verdict remains
`DROP-ASTRA-PSEUDOLABEL`. - No TRAIN-CV candidate passed the incremental
gate. - DEV was not evaluated. - Prospective calls = 0; 807 dates remain
untouched.

Generation-2 motivation is narrower: Astra6 hindsight credit showed
strong numerical repeatability on 99 complete units, but Gen-1 failed
its procedural completeness gate. This motivates an **independent
replication and decomposition**, not retroactive rescue.

## 1. Central question

\[
`\boxed{\text{What part, if any, of Astra6 hindsight judgment is predictable before the future outcome and useful beyond B6?}}`{=tex}
\]

Test the complete chain:

\[
`\text{stability}`{=tex}`\to`{=tex}`\text{pre-outcome distillability}`{=tex}`\to`{=tex}`\text{increment beyond B6}`{=tex}`\to`{=tex}`\text{direction/market controls}`{=tex}.
\]

A stable hindsight target that cannot be predicted from pre-outcome
information is not useful for inference-time reliability estimation.

## 2. Hypotheses

### H2.1 Independent stability replication

Astra6 hindsight credit is reproducibly stable on a new TRAIN-only
replication sample.

### H2.2 Component-specific distillability

For \[ q\^{Astra}=\[q\_{para},q\_{remove},q\_{agree},q\_{contradict}\],
\] one or more components may be pre-outcome-distillable even if the
whole vector is not.

### H2.3 Nontrivial teacher residual

Fit a TRAIN-only, cross-fitted simple hindsight explanation \[
`\hat `{=tex}q\^{simple}=f(C,D,Conf,X\_{market}) \] and define \[
e^{Astra}=q^{Astra}-`\hat `{=tex}q\^{simple}. \] Then test whether
pre-outcome (X,T) predicts (e\^{Astra}).

### H2.4 Outcome-path support

Use (R\_{t,1:10}), not only binary correctness, to construct
training-only soft resolution/support targets.

### H2.5 Conditional credit

Diagnostic value may depend on market state: \[ q_k=q_k(X_t,T\_{t,a}).
\]

### H2.6 Residual-over-B6 utility

If a target is distillable, use it only to model what B6 misses: \[
logit(r^{new})=logit(r^{B6})+`\delta`{=tex}\_`\theta`{=tex}(X,T,`\hat `{=tex}q).
\]

## 3. Execution order

Execute strictly:

``` text
G2-A Independent teacher replication
→ G2-B Credit decomposition
→ G2-C Simple hindsight explanation + OOF residual
→ G2-D Pre-outcome distillability
→ G2-E TRAIN-only incremental residual models
→ G2-F Red-team controls
→ G2-G Decision whether DEV may unlock
```

Do not jump directly to model search.

## 4. G2-A --- independent replication

Create a preregistered TRAIN-only pool: - pool size: 120 units; -
target: 100 complete triplets; - 3 independent Astra6 generations per
unit.

Prefer units not used in Gen-1 stability analysis if feasible. If
overlap is unavoidable, report exact overlap and non-overlap metrics.

Selection is frozen before observing new teacher outputs.

### Transport rule

For 429/5xx/network failures: 1. preserve every failure; 2. never switch
model; 3. use frozen retry policy; 4. mark incomplete after retry
exhaustion; 5. continue through the preregistered pool until 100
complete triplets or pool exhaustion.

No selection based on teacher score, correctness, outcome, or observed
stability.

Recommended retry policy: max 3 attempts per requested generation,
exponential backoff, same Astra6 model and same semantic prompt.

### Replication metrics

Report requested units, attempts, successful transports, schema-valid
calls, complete triplets, pairwise credit Spearman, top-credit
agreement, entropy, and per-component stability.

Frozen replication thresholds: \[
`\rho`{=tex}*{pairwise}`\ge0.30`{=tex},`\quad `{=tex}A*{top}`\ge0.40`{=tex},`\quad `{=tex}H\<1.37,`\quad `{=tex}N\_{complete}`\ge100`{=tex}.
\]

Verdict: - `ASTRA_STABILITY_REPLICATED` -
`ASTRA_STABILITY_NOT_REPLICATED` - `ASTRA_REPLICATION_INCOMPLETE`

## 5. G2-B --- credit decomposition

Analyze separately: \[ q\_{para},q\_{remove},q\_{agree},q\_{contradict}.
\]

For each report: - mean/SD/entropy; - run-to-run Spearman; - rank
stability; - correlation with correctness; - confidence/probability; -
original direction; - agree/contradict/removal/paraphrase flips; -
market features; - B6 score and B6 error.

Do not rely on one averaged credit metric.

## 6. G2-C --- explain teacher with simple hindsight variables

Fit date-grouped, cross-fitted models for each teacher component using
nested feature sets:

-   S0 constant
-   S1 correctness only
-   S2 correctness + original direction
-   S3 + confidence/probability
-   S4 + direction-response features
-   S5 + market-only features
-   S6 + full observable B6 trajectory

Correctness is allowed only to analyze/construct TRAIN hindsight
targets. It is forbidden in the later foresight student.

Report cross-fitted (R\^2), Spearman, MAE and component-wise results.

Choose the strongest simple explanation using a frozen TRAIN-CV rule.

Construct OOF residual: \[
e\_{t,a,k}=q\_{t,a,k}-`\hat `{=tex}q\^{simple,OOF}\_{t,a,k}. \]

Never use in-sample residuals as pseudo-labels.

## 7. G2-D --- pre-outcome distillability

For each raw component (q_k), residual (e_k), and any preregistered
path/regime target, compare:

-   D0 market only
-   D1 direction only
-   D2 raw B6 trajectory only
-   D3 market + B6 trajectory
-   D4 market + B6 + agent identity

All inputs are pre-outcome. Use date-grouped TRAIN-only CV.

Primary metrics: - Spearman - MAE - top-credit accuracy where
meaningful - Pearson secondary

### Conditional diagnostics

Report: \[ `\rho`{=tex}(`\hat `{=tex}q,q),`\quad`{=tex}
`\rho`{=tex}(`\hat `{=tex}q,q`\mid `{=tex}C=1),`\quad`{=tex}
`\rho`{=tex}(`\hat `{=tex}q,q`\mid `{=tex}C=0). \]

Also report descriptive strata by agent, original UP/DOWN, high/low VIX,
and response pattern.

### Direction-control gate

For each component: \[
`\Delta`{=tex}\_{full-dir}=`\rho`{=tex}(D3)-`\rho`{=tex}(D1). \]

A target is not independently behaviorally distillable if direction-only
reproduces it.

Recommended component gate: \[ `\rho`{=tex}(D3)`\ge0.20`{=tex} \] plus
positive Full-vs-Direction delta with bootstrap support and no
single-agent domination.

Possible target verdicts: - `DISTILLABLE_FULL` -
`DISTILLABLE_DIRECTION` - `STABLE_NOT_DISTILLABLE` - `UNSTABLE` -
`COMPONENT_SPECIFIC`

Do not change Gen-1 thresholds retroactively.

## 8. G2-E --- incremental utility beyond B6

Only targets passing G2-D may enter.

First train a foresight target predictor: \[
`\hat `{=tex}q=h\_`\phi`{=tex}(X,T). \]

Then: \[
logit(r^{new})=logit(r^{B6})+`\delta`{=tex}\_`\theta`{=tex}(X,T,`\hat `{=tex}q).
\]

At inference, true hindsight (q), correctness, future return and future
path are forbidden.

Keep candidate set small: - C0 B6 - C1 B6 + predicted Astra component
credit - C2 B6 + predicted Astra residual credit - C3 B6 + predicted
outcome-path target, only if it passed - C4 B6 + at most two
independently passing auxiliary targets

No kitchen-sink model.

Use simple residual heads first: regularized logistic interactions,
GBDT, then small MLP only if justified. Do not fine-tune Ling or Astra.

## 9. TRAIN-only incremental evaluation

Use date-grouped CV and report: - AUROC - AUPRC - Brier - ECE - paired
delta vs B6 - fold consistency - 1,000 date-level bootstrap replicates

Also run block-bootstrap and non-overlapping-date robustness because
10-day outcomes overlap.

## 10. Red-team controls

Every survivor must face: - shuffled pseudo-label - direction-only
pseudo-label predictor - market-only predictor - agent-ID-only -
confidence-only - shuffled trajectory - label-permutation diagnostic -
remove Astra target → B6 - teacher-run sensitivity - mean-teacher vs
individual-run target

A gain that vanishes across teacher runs is fragile.

## 11. Generation-2 Astra6 Explorer wave

After G2-A through G2-D, launch 12 independent Astra6 Explorers. They
initially do not see one another.

Prompt:

> Generation 1 found algorithmic credit non-distillable (mean Spearman
> ≈0.0525). Astra6 hindsight credit was numerically stable on 99
> complete triplets (pairwise Spearman 0.6709, top-credit agreement
> 0.8620), but failed the frozen completeness gate because one transport
> failure left 99 rather than 100 complete units. Generation 2 has
> produced component-level, direction-controlled,
> correctness-conditional, residualized distillability analyses. Propose
> exactly one falsifiable transformation or use of the Astra hindsight
> target that could isolate information that is both
> pre-outcome-distillable and incrementally useful beyond B6. Do not
> propose belief recovery and do not merely change the classifier. State
> the mechanism, mathematical target, cheapest TRAIN-only falsification,
> direction/leakage controls, and explicit abandonment condition.

Priority areas may include component-specific credit, teacher residual,
outcome-resolution weighting, path support, regime-conditioned credit,
hard-case credit, pairwise intervention credit, B6 meta-reliability,
selective credit, and disagreement-specific credit.

## 12. Debate and adjudication

For every survivor use fresh Astra6 contexts: - Advocate - Skeptic -
Methodologist - Adjudicator

Adjudicator returns: - `ADVANCE` - `TARGETED_ABLATION` - `KILL`

Critics must explicitly test direction, correctness leakage, market
state, repeated search, teacher instability, lucky folds, cross-fitting
errors, and simpler baselines.

## 13. DEV unlock gate

DEV remains locked unless at least one candidate satisfies all: 1. Astra
target independently replicated if Astra-derived; 2. target
pre-outcome-distillable; 3. Full adds beyond direction-only; 4. target
survives correctness/simple-target residual analysis or has a clearly
documented alternative interpretation; 5. TRAIN-CV improves over B6; 6.
shuffled pseudo-label does not reproduce; 7. market-only does not
reproduce; 8. not isolated to one fold/agent; 9. no leakage; 10. fresh
Astra6 adjudicator says `ADVANCE`.

If none passes: \> `GENERATION_2_COMPLETE_NO_DEV`

If unlocked, freeze \<=2 candidates, hyperparameters, target predictors,
prompts, seeds, code commit, protocol hash and metrics, then evaluate
DEV once. No tuning after DEV.

## 14. Prospective rule

Generation 2 does **not** unlock the 807 prospective dates
automatically.

Even a positive DEV result proceeds to a later finalist/prospective
protocol.

Prospective remains `SEALED`.

## 15. Generation-2 primary verdict

Return exactly one: - `ASTRA_TARGET_NOT_REPLICATED` -
`STABLE_NOT_DISTILLABLE` - `DISTILLABLE_BUT_REDUNDANT` -
`DISTILLABLE_NOT_USEFUL` - `TRAIN_INCREMENT_FOUND` -
`DEV_INCREMENT_FOUND` - `PARTIAL_ANOMALY`

Do not claim `DISCOVERED`, `PROVEN`, `GENERALIZES`, `SUPERIOR`,
`DEPLOYMENT_READY`, or `ALPHA`.

## 16. Required directory

``` text
generation_2/
├── 00_protocol/
├── 01_replication/
├── 02_decomposition/
├── 03_teacher_residual/
├── 04_distillability/
├── 05_explorers/
├── 06_candidates/
├── 07_train_cv/
├── 08_red_team/
├── 09_debate/
├── 10_dev/
└── 11_synthesis/
```

Maintain `G2_EXPERIMENT_LEDGER.jsonl` with every tested
hypothesis/model, not only winners.

## 17. Astra6-only hard rule

Every successful new LLM call must satisfy the preregistered Astra6
identity check. On 429, timeout, malformed response, or network error:
record failure and retry under frozen policy; never fallback.

If any successful call returns Luna or another model: \>
`MODEL_IDENTITY_VIOLATION`

Stop Generation 2 and audit.

Keep secrets in environment variables only.

## 18. Workspace isolation

Continue using the isolated worktree. Do not modify dirty `main`,
overwrite Generation-1 artifacts, interfere with older S&P500 processes,
or commit unrelated changes.

## 19. Immediate execution instruction

Start Generation 2, but initially execute **only through G2-D**:

1.  freeze/hash this protocol;
2.  preserve Gen-1 verdict;
3.  construct preregistered 120-unit replication pool;
4.  obtain up to 100 complete Astra6 triplets under frozen retry rules;
5.  compute replication stability;
6.  decompose credit;
7.  build cross-fitted simple hindsight explanations;
8.  construct OOF teacher residuals;
9.  run component-level/residual pre-outcome distillability;
10. run direction-only and correctness-conditional diagnostics;
11. write interim synthesis.

**Do not run G2-E candidate models until G2-D is complete and the frozen
gate authorizes continuation.**

## 20. Interim independent Astra6 synthesis

Use a fresh Astra6 context and ask:

> Generation 1 is immutable and failed the Astra pseudo-label
> completeness gate at 99/100 despite strong numerical stability.
> Generation 2 independently replicated or failed to replicate that
> stability and decomposed the hindsight target into
> intervention-specific components, simple hindsight explanations, OOF
> residual targets, pre-outcome distillability, correctness-conditional
> diagnostics, and direction-only controls. Determine whether any target
> contains evidence of pre-outcome-predictable information not
> adequately explained by direction, correctness, confidence, agent
> identity, or market-only features. Do not recommend a method merely
> because a correlation is positive. Identify the narrowest surviving
> hypothesis and the cheapest decisive next experiment.

Required JSON:

``` json
{
  "replication_verdict": "...",
  "distillability_verdict": "...",
  "surviving_target": "...",
  "main_alternative_explanation": "...",
  "next_stage_authorized": true,
  "next_experiment": "...",
  "unsafe_claims": []
}
```

## 21. Final principle

Do not rescue Generation 1. Do not rescue pseudo-labeling.

Generation 2 asks **why a highly repeatable hindsight teacher either can
or cannot be converted into foresight information**.

The desired information path is:

\[ `\boxed{
Y_{future}
\rightarrow q^{hindsight}
\rightarrow \widehat q(X,T)
\rightarrow \Delta Reliability_{>B6}
}`{=tex} \]

Test every arrow separately.

If an arrow fails, preserve the failure and make that exact bottleneck
the object of the next research generation.
