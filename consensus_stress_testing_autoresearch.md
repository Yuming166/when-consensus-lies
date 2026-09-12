# AutoResearch Plan --- Consensus Stress Testing

## 0. Research Objective

### North-star goal

Upgrade the current **When Consensus Lies** study from a fixed
intervention-based risk score into a more general and experimentally
grounded framework for **outcome-blind stress testing of multi-agent
consensus**.

The target research question is:

> **When multiple agents agree, can we stress-test the evidence
> supporting their consensus before the ground-truth label is revealed,
> and determine whether the collective response is appropriately
> evidence-responsive?**

The desired final result is not merely a better scalar than RPI/Rsym.
The goal is to establish a new research object:

\[ `\text{Multi-agent consensus}`{=tex} `\rightarrow`{=tex}
`\text{controlled evidence stress}`{=tex} `\rightarrow`{=tex}
`\text{collective behavioral response}`{=tex} `\rightarrow`{=tex}
`\text{pre-outcome reliability estimate}`{=tex} \]

and, if empirically justified, extend this into:

\[ `\text{Active Consensus Stress Testing}`{=tex} \]

where a limited intervention budget is used to select the most
informative next probe.

### Target empirical outcome

The new method should ideally:

1.  Work on the existing BoolQ and VitaminC experimental infrastructure.
2.  Improve on the current RPI/Rsym baselines under the same label-blind
    evaluation protocol.
3.  Preserve positive selective-prediction results at the preregistered
    operating point.
4.  Replicate across model families rather than being specific to Qwen.
5.  Show positive results on at least one additional task/domain.
6.  Demonstrate that the improvement comes from the new conceptual
    object, not merely from adding more interventions or a more flexible
    post-hoc score.
7.  If Active Probing is pursued, demonstrate improved
    reliability-per-inference-budget over fixed probing.
8.  Maintain strict outcome firewalls: ground-truth labels, correctness,
    and derived outcome variables must never influence probing or score
    construction.

------------------------------------------------------------------------

# 1. Current Baseline and Starting Point

The existing study already establishes the following experimental
infrastructure:

-   Environment-controlled evidence identities and provenance roots.
-   Fixed evidence views for five agents.
-   Original multi-agent consensus with high-consensus subset defined by
    agreement \>= 0.8.
-   Paired evidence interventions.
-   Observable outputs only: answer, confidence, cited evidence IDs.
-   Labels revealed only after routing.
-   Pre-outcome risk ranking and selective routing.
-   RPI and Rsym as frozen baseline scores.
-   BoolQ provenance-disjoint replication.
-   VitaminC label-symmetric cross-family evaluation.
-   S&P500 replay as an external stress program.

The current intervention set is:

-   `remove`
-   `reverse`
-   `substitute`

The existing paper explicitly treats these individual ingredients as
established tools; its claimed distinction is their use for pre-outcome
error risk of a fixed multi-agent consensus under environment-assigned
evidence conditions.

The current results therefore serve as **baselines, not targets to be
protected at all costs**.

Important existing findings to preserve as reference points:

-   BoolQ V12.1: RPI AUROC = 0.705 \[0.620, 0.781\].
-   BoolQ V12.1: Risk@80 error reduced from 0.220 to 0.133.
-   BoolQ V12.1: complete intervention inertia AUROC = 0.791; flip
    inertia AUROC = 0.807; shared-source fraction alone ≈ chance.
-   VitaminC V3.16.1: both Qwen and Ling passed all preregistered
    model-level gates.
-   Cross-model item-level risk correlation remained modest, motivating
    stronger study of what exactly transfers.

These numbers must remain unchanged as historical baselines. Do not
modify baseline definitions merely to make the new method look better.

------------------------------------------------------------------------

# 2. Research Philosophy

## 2.1 Search for a new phenomenon, not a new heuristic

Do NOT optimize:

> "Find a weighted combination of existing intervention features that
> maximizes AUROC."

Instead ask:

> "What observable property of a consensus makes it trustworthy or
> untrustworthy under controlled evidence stress?"

The primary conceptual candidates are:

1.  **Expected-response faithfulness**
2.  **Consensus stress testing**
3.  **Consensus stress curves**
4.  **Robustness--responsiveness separation**
5.  **Consensus breakpoint / robustness radius**
6.  **Active consensus probing**

The agents should be allowed to reject these ideas if literature or
experiments show that they are already established or empirically weak.

## 2.2 Do not equate invariance with reliability

A key hypothesis is:

\[ `\text{invariance}`{=tex} `\neq `{=tex}`\text{reliability}`{=tex} \]

An agent should remain invariant under semantics-preserving changes, but
should respond when evidence undergoes a meaningful semantic change.

Therefore the desired property is:

\[ `\text{appropriate response}`{=tex} \]

rather than simply:

\[ `\text{answer flip}`{=tex} \]

## 2.3 Do not claim causal identification

Evidence interventions measure observable behavioral dependence. They do
not establish unique internal causal mechanisms.

The research should use language such as:

-   behavioral responsiveness
-   intervention sensitivity
-   expected-response consistency
-   evidence responsiveness
-   stress-test behavior

and avoid unsupported claims such as:

-   causal identification of internal reasoning
-   proof that the model "used" a particular evidence sentence
    internally

------------------------------------------------------------------------

# 3. Research Phases

## Phase 0 --- Research Audit

### Objective

Freeze a machine-readable description of the current study before
changing anything.

### Tasks

-   Extract all current baselines.
-   Record all existing experiment versions.
-   Record all positive, inconclusive, invalidated, and failed results.
-   Identify every feature currently allowed to enter RPI/Rsym.
-   Identify all outcome-derived variables and ensure they are
    firewalled.
-   Reproduce the current main baseline if possible.

### Deliverables

``` text
research_state.md
baseline_manifest.json
baseline_results.json
known_failures.md
outcome_firewall.md
```

### Gate 0

Proceed only if:

-   Baseline results can be reproduced or discrepancies are documented.
-   Existing invalidated metrics remain invalidated.
-   No outcome leakage exists.
-   Baseline code/configuration is versioned and frozen.

------------------------------------------------------------------------

# Phase 1 --- Parallel Literature and Novelty Audit

## Objective

Determine whether the candidate concepts are genuinely underexplored.

### Parallel agent allocation

Run independent agents across:

1.  LLM faithfulness
2.  Counterfactual reasoning
3.  Evidence intervention
4.  Multi-agent consensus
5.  Multi-agent calibration
6.  Selective prediction
7.  Active learning
8.  Active testing
9.  Robustness / adversarial evaluation
10. Causal inference / counterfactual evaluation
11. Human decision-making / social choice
12. LLM safety / hallucination detection

### Required output for every candidate paper

Each agent must record:

``` text
paper
year
venue
intervention unit
intervention type
single-model or multi-agent
consensus before intervention?
evidence controlled by environment?
paired original/intervention design?
labels hidden during intervention?
predicts future error?
selective routing?
adaptive intervention selection?
stress curve?
expected-response evaluation?
```

### Required attack questions

For each proposed contribution:

1.  Has someone already defined the same problem?
2.  Has someone already measured the same object under a different name?
3.  Is the novelty merely the combination of known components?
4.  Can the contribution be reduced to a known faithfulness metric?
5.  Is a multi-agent formulation genuinely necessary?
6.  Does the method predict unrevealed future consensus error?
7.  Is active probing genuinely new in this setting?
8.  What is the closest competing paper?
9.  What experiment would make our claim false?

### Deliverable

``` text
novelty_map.md
closest_work_table.csv
claim_attack.md
```

### Gate 1

A candidate survives only if at least one of the following appears
genuinely differentiated:

-   consensus-level expected-response evaluation
-   stress-response trajectory/curve
-   consensus robustness--responsiveness characterization
-   active intervention selection for consensus reliability

If no candidate survives, return to Phase 1 rather than polishing the
old RPI framework.

------------------------------------------------------------------------

# Phase 2 --- Concept Discovery and Kill Tests

## Objective

Test whether the new conceptual object exists empirically before
building a complex method.

### Candidate concepts

#### C1. Expected-response faithfulness

For intervention (T):

\[ e `\rightarrow `{=tex}T(e) \]

define an expected behavioral response:

\[ Y\^\*(T) \]

and compare it with the observed response:

\[ Y(T) \]

Measure:

\[ BR(T)=`\mathbb{1}`{=tex}\[Y(T)=Y\^\*(T)\] \]

at agent and consensus levels.

#### C2. Consensus Stress Testing

Instead of treating interventions as isolated ablations, treat them as
probes of an already-formed consensus:

\[ C_0 `\rightarrow `{=tex}C_1
`\rightarrow `{=tex}`\cdots `{=tex}`\rightarrow `{=tex}C_k \]

#### C3. Consensus Stress Curve

Introduce a perturbation-strength parameter:

\[ `\lambda `{=tex}`\in [0,1]`{=tex}\]

and measure:

\[ A_q(`\lambda`{=tex}) =
`\text{consensus agreement after stress level }`{=tex}`\lambda`{=tex} \]

Potential derived quantities:

-   stress-response area
-   consensus breakpoint
-   robustness radius
-   response elasticity

#### C4. Robustness--Responsiveness Map

Separate:

-   robustness to semantics-preserving perturbations
-   responsiveness to semantics-changing perturbations

Potential behavioral categories:

                    High responsiveness   Low responsiveness
  ----------------- --------------------- ----------------------
  High robustness   Reliable              Evidence-insensitive
  Low robustness    Brittle               Unstable

#### C5. Active Consensus Probing

Under intervention budget (B):

\[ T\^\*=`\arg`{=tex}`\max`{=tex}\_T I(T;R`\mid `{=tex}X) \]

where (R) is latent future consensus reliability and (X) is the
currently observed response state.

The exact acquisition objective can be changed during research, but it
must be label-blind during deployment.

------------------------------------------------------------------------

## Phase 2 experimental design

Start small.

Use:

-   BoolQ
-   VitaminC
-   current five-agent infrastructure
-   existing evidence graph
-   existing parser
-   existing model configurations where possible

Do not begin with expensive new models.

### Intervention families

At minimum compare:

1.  semantic-preserving transformation
2.  semantic-changing transformation
3.  evidence removal
4.  provenance-preserving vs provenance-changing transformations where
    feasible

The existing remove/reverse/substitute interventions may be reused as
implementation mechanisms.

### Critical null test

A semantic-preserving intervention should generally preserve the answer.

A semantic-changing intervention should induce the expected directional
response when the changed evidence is decision-relevant.

The important measurement is therefore:

\[ `\text{Observed response}`{=tex}
`\quad`{=tex}`\text{vs.}`{=tex}`\quad`{=tex}
`\text{Expected response}`{=tex} \]

not merely flip rate.

### Gate 2

A candidate advances only if:

-   it reveals a reproducible behavioral distinction between correct and
    false consensus;
-   it is not reducible to ordinary confidence or vote agreement;
-   it produces a meaningful effect on at least one existing benchmark;
-   the phenomenon survives basic null/placebo controls.

If the effect does not exist, kill the concept.

------------------------------------------------------------------------

# Phase 3 --- Build the Consensus Stress Benchmark

## Objective

Turn the observed phenomenon into a systematic benchmark/protocol.

### Required benchmark axes

#### Axis A --- semantic preservation

Expected:

\[ C(T(e)) `\approx `{=tex}C(e) \]

#### Axis B --- semantic reversal

Expected:

\[ C(T(e)) `\text{ moves toward the opposite decision}`{=tex} \]

when the intervention is decision-relevant.

#### Axis C --- evidence weakening/removal

Expected behavior may be:

-   unchanged if redundant evidence remains sufficient;
-   reduced confidence;
-   increased disagreement;
-   changed answer;

depending on evidence redundancy.

The benchmark must not hard-code one response for every removal case.

#### Axis D --- provenance manipulation

Where possible, separate:

-   same semantic content, different provenance;
-   different semantic content, same topic;
-   correlated vs independent evidence roots.

### Important principle

The benchmark should distinguish:

> "the model changed"

from:

> "the model changed appropriately."

------------------------------------------------------------------------

# 4.1 Expected-response oracle design

This is a high-risk methodological component.

Do not use the gold label to define the expected response.

Instead define expected response from the transformation itself.

Examples:

### Semantics-preserving

\[ Y\^\*=Y_0 \]

### Explicit polarity reversal

\[ Y\^\*=`\operatorname{flip}`{=tex}(Y_0) \]

### Weak perturbation

Expected response may be probabilistic or indeterminate.

For these cases, use an explicitly declared **no-forced-response**
category.

### Required control

Include transformations whose expected response is:

\[ `\text{no deterministic change}`{=tex} \]

to avoid turning all invariance into failure.

------------------------------------------------------------------------

# Phase 4 --- Reliability Modeling

## Objective

Test whether stress-response information predicts future consensus
error.

### Baselines

At minimum:

-   majority agreement
-   mean confidence
-   confidence dispersion
-   vote disagreement
-   source overlap
-   RPI
-   Rsym
-   individual intervention features
-   stress-response features

### Candidate new representations

#### 1. Behavioral Faithfulness

\[ BF_q =
`\text{fraction of interventions with expected response}`{=tex} \]

#### 2. Stress Area

\[ SA_q = `\int`{=tex}\_0\^1 A_q(`\lambda`{=tex})d`\lambda`{=tex} \]

#### 3. Breakpoint

\[ `\lambda`{=tex}\_q\^\* =
`\inf`{=tex}{`\lambda`{=tex}:A_q(`\lambda`{=tex})\<`\tau`{=tex}} \]

#### 4. Robustness--Responsiveness pair

\[ RR_q=(Robustness_q, Responsiveness_q) \]

#### 5. Response diversity

Measure whether agents exhibit coherent collective response or
heterogeneous/random response.

### Modeling principle

Start with simple interpretable models:

-   logistic regression
-   isotonic calibration
-   monotonic regression
-   shallow tree

Only introduce neural models if simple models cannot express the
phenomenon.

### Primary endpoints

-   AUROC
-   AUPRC
-   Risk@80
-   risk-coverage curve
-   calibration
-   bootstrap confidence intervals

### Gate 4

The new representation must outperform existing baselines under a frozen
evaluation protocol.

A positive AUROC alone is insufficient.

At the preregistered operating point:

\[ `\text{Risk@80}`{=tex}*{new} \< `\text{Risk@80}`{=tex}*{baseline} \]

must be tested with uncertainty.

------------------------------------------------------------------------

# Phase 5 --- Active Consensus Probing

## Objective

Determine whether reliability can be estimated efficiently with fewer
interventions.

### Setup

Each question has an intervention budget:

\[ B`\in`{=tex}{1,2,3,`\ldots`{=tex}} \]

Candidate strategies:

1.  random probe
2.  fixed remove → reverse → substitute
3.  strongest-single-probe
4.  greedy information gain
5.  uncertainty reduction
6.  learned acquisition policy

### Required comparison

For equal model-call budget compare:

\[ `\text{accuracy/risk quality per intervention}`{=tex} \]

rather than only absolute AUROC.

### Possible acquisition objective

Given current observation state (X_t):

\[ T\_{t+1} = `\arg`{=tex}`\max`{=tex}\_T `\mathbb{E}`{=tex}\[
`\text{risk-information gain}`{=tex} `\mid `{=tex}X_t,T\] \]

Do not use ground-truth labels in selecting (T) at test time.

### Key result to seek

A compelling result would look qualitatively like:

``` text
0 probes   -> weak baseline
1 probe    -> large reliability gain
2 probes   -> most of the gain
3+ probes  -> diminishing returns
full probe -> marginal additional benefit
```

The exact numbers are not predetermined.

### Gate 5

Active probing becomes a core contribution only if it provides a
statistically defensible improvement in reliability-per-budget over
fixed probing.

Otherwise retain it as an analysis or future direction.

------------------------------------------------------------------------

# Phase 6 --- Cross-Model and Cross-Dataset Validation

## Objective

Demonstrate that the method is not a Qwen/BoolQ artifact.

### Model families

At minimum:

-   Qwen family
-   Ling family
-   one additional materially different model family if compute permits

Ideally vary both:

-   model family
-   model scale

### Dataset progression

#### Existing core

-   BoolQ
-   VitaminC

#### Additional

Choose at least one dataset where evidence and labels can be cleanly
controlled.

Potential candidates:

-   FEVER, if the evidence construction passes the existing audit
-   another fact-verification benchmark
-   an arbitrary QA dataset with externally controlled evidence

### Cross-model protocol

Important distinction:

#### Within-model validity

Does the method predict errors for model M?

#### Cross-model transfer

Does a score/procedure learned or selected on model M work on model N?

#### Mechanism transfer

Does the same behavioral phenomenon appear across models even if
item-level rankings differ?

Do not conflate these.

### Target positive result

The strongest realistic claim is:

> The stress-testing procedure and its aggregate reliability signal
> transfer across model families, while item-level risk ranking may
> remain model-dependent.

This is more defensible than demanding perfect item-level correlation.

### Gate 6

A final method should have:

-   positive results on original data;
-   positive results on at least one additional model family;
-   positive results on at least one additional dataset/domain;
-   no dependence on post-hoc model-specific relabeling.

If cross-model results fail, diagnose whether the failure is:

1.  model behavior;
2.  evidence construction;
3.  expected-response definition;
4.  calibration;
5.  sample adequacy;
6.  genuine lack of transfer.

Do not silently change the method to rescue one model.

------------------------------------------------------------------------

# Phase 7 --- Adversarial Validation and Failure Analysis

## Objective

Try to destroy the final method.

### Attack 1 --- confidence baseline

Can confidence alone reproduce the result?

### Attack 2 --- disagreement baseline

Can simple vote disagreement reproduce it?

### Attack 3 --- intervention-count baseline

Does the method merely reward "more changes"?

### Attack 4 --- response-rate baseline

Does raw flip rate explain everything?

### Attack 5 --- evidence-length baseline

Does the score accidentally measure evidence length?

### Attack 6 --- citation-count baseline

Does citation volume explain the result?

### Attack 7 --- provenance leakage

Can source identity accidentally encode labels?

### Attack 8 --- intervention strength confounding

Are stronger interventions simply more predictive because they are more
obviously adversarial?

### Attack 9 --- answer-prior confounding

Does the method behave differently for native YES vs NO labels?

### Attack 10 --- semantic-preserving placebo

Does the method incorrectly flag stable answers as unreliable when the
evidence meaning is unchanged?

### Attack 11 --- model-specific prompt artifact

Does changing persona wording destroy the phenomenon?

### Attack 12 --- randomization

Shuffle intervention assignments and verify that the signal disappears
or weakens appropriately.

### Gate 7

A final method must have an explicit explanation for its major failure
modes.

Negative results should be retained.

------------------------------------------------------------------------

# 5. Multi-Agent AutoResearch Architecture

## 5.1 Agent roles

Use parallel agents with intentionally different objectives.

### Explorer agents

Search for:

-   new concepts
-   related literature
-   new benchmarks
-   alternative mathematical formulations

### Killer agents

Attempt to invalidate:

-   novelty
-   metric validity
-   expected-response assumptions
-   cross-model claims

### Experimental agents

Implement and run small experiments.

### Statistical agents

Check:

-   confidence intervals
-   bootstrap procedures
-   multiple comparisons
-   calibration
-   power
-   leakage

### Reproducibility agents

Check:

-   seeds
-   configs
-   data splits
-   cached outputs
-   parser failures
-   deterministic behavior

### Synthesis agent

Only after independent reports are produced, synthesize them into the
next experiment plan.

------------------------------------------------------------------------

# 5.2 Agent independence rule

Agents should not all see the same hypothesis first.

For major research decisions:

``` text
5–10 independent proposals
        ↓
blind-ish aggregation
        ↓
killer review
        ↓
small experiment
        ↓
decision
```

This reduces confirmation bias from the original research direction.

------------------------------------------------------------------------

# 6. Experiment Registry

Every experiment must record:

``` yaml
experiment_id:
parent_experiment:
date:
hypothesis:
research_question:
dataset:
model:
agent_configuration:
evidence_version:
intervention_version:
random_seed:
training_data:
selection_data:
test_data:
allowed_inputs:
forbidden_inputs:
primary_metric:
secondary_metrics:
budget:
status:
result:
confidence_interval:
decision:
reason:
```

Possible statuses:

-   `PROPOSED`
-   `RUNNING`
-   `PASS`
-   `FAIL`
-   `INCONCLUSIVE`
-   `INVALIDATED`
-   `SUPERSEDED`

Never delete failed experiments.

------------------------------------------------------------------------

# 7. Anti-Cherry-Picking Rules

These are mandatory.

## Rule 1

Do not change the primary metric after seeing the result.

## Rule 2

Do not change the test split because the current split is inconvenient.

## Rule 3

Do not add a model only because it produces a positive result.

## Rule 4

Do not drop a model only because it produces a negative result.

## Rule 5

Do not tune intervention weights on the test set.

## Rule 6

Do not use labels, correctness, or future outcomes to select probes.

## Rule 7

Do not redefine "expected response" after observing the model response.

## Rule 8

If a preregistered gate fails, record the failure and design a new
cohort rather than silently repairing the original cohort.

## Rule 9

Any new method that uses more inference calls must be compared at
matched compute budget.

## Rule 10

A positive result is not accepted unless an independent agent attempts
to reproduce or falsify it.

------------------------------------------------------------------------

# 8. Decision Tree

``` text
Literature novelty?
    │
    ├── NO → abandon / reformulate
    │
    └── YES
         ↓
Does the stress-response phenomenon exist?
    │
    ├── NO → abandon concept
    │
    └── YES
         ↓
Does it predict future consensus error?
    │
    ├── NO → retain as behavioral analysis only
    │
    └── YES
         ↓
Does it beat RPI/Rsym/confidence/disagreement?
    │
    ├── NO → diagnose / simplify / reformulate
    │
    └── YES
         ↓
Does it survive semantic-preserving placebo controls?
    │
    ├── NO → invalidate
    │
    └── YES
         ↓
Does it transfer across model families?
    │
    ├── NO → restrict claim or redesign
    │
    └── YES
         ↓
Does active probing beat fixed probing under equal budget?
    │
    ├── NO → keep stress testing, drop active-probing claim
    │
    └── YES
         ↓
Strong final method
```

------------------------------------------------------------------------

# 9. Target Final Research Contribution

The preferred final contribution hierarchy is:

## Contribution 1 --- New research object

**Consensus Stress Testing**

A protocol for evaluating whether an already-formed multi-agent
consensus remains appropriately responsive to controlled transformations
of its supporting evidence.

## Contribution 2 --- New measurement

**Expected-response behavioral faithfulness**

Distinguish:

\[ `\text{answer changed}`{=tex} \]

from:

\[ `\text{answer changed appropriately}`{=tex}. \]

## Contribution 3 --- New representation

**Consensus Stress Profile**

Characterize consensus using its response trajectory rather than a
single intervention outcome.

Potential components:

-   semantic-preserving robustness
-   semantic-changing responsiveness
-   stress area
-   breakpoint
-   response diversity

## Contribution 4 --- Optional method

**Active Consensus Probing**

Select interventions adaptively under a fixed inference budget.

## Contribution 5 --- Empirical validation

Demonstrate positive reliability gains:

-   on the original BoolQ/VitaminC infrastructure;
-   across model families;
-   on at least one additional dataset/domain;
-   with strict outcome-blind evaluation.

------------------------------------------------------------------------

# 10. Preferred Final Paper Story

The strongest eventual paper should NOT read:

> "We introduce three new interventions and combine them into a better
> risk score."

Instead it should read approximately:

> **Agreement is not itself evidence that a multi-agent decision is
> responsive to the evidence supporting it. We introduce outcome-blind
> Consensus Stress Testing, which probes an already-formed consensus
> with controlled evidence transformations and evaluates whether the
> collective behavioral response matches the transformation's expected
> semantic effect. This produces a consensus stress profile that
> separates robust evidence-responsive agreement from
> evidence-insensitive or brittle agreement. We further study active
> probing under a fixed inference budget and show that a small number of
> targeted probes can identify a substantial fraction of unreliable
> consensus decisions. Across BoolQ, VitaminC, and cross-model
> evaluations, the resulting pre-outcome signal improves selective
> reliability over agreement, confidence, provenance overlap, and the
> existing RPI/Rsym baselines.**

This paragraph is a **target hypothesis**, not a result. It must only
appear in the final paper if the experiments actually support it.

------------------------------------------------------------------------

# 11. Minimum Viable Success

The project is considered successful if all of the following hold:

### Scientific

-   A clearly defined new phenomenon is identified.
-   It is distinguishable from ordinary confidence/disagreement.
-   It is not reducible to simple intervention flip rate.
-   It has a principled expected-response interpretation.

### Empirical

-   Positive result on the existing core benchmark.
-   Positive result on at least two model families.
-   Positive result on at least one additional dataset/domain.
-   Statistically defensible improvement in risk ranking and/or Risk@80.

### Methodological

-   Outcome-blind test-time procedure.
-   No test-label tuning.
-   Semantic-preserving controls.
-   Matched-budget comparisons.
-   Strong failure analysis.

### Reproducibility

-   Versioned configs.
-   Saved intervention artifacts.
-   Saved raw model outputs.
-   Experiment registry.
-   Reproducible evaluation scripts.

------------------------------------------------------------------------

# 12. Stretch Goal

If the core method is strong, pursue:

\[ `\boxed{
\text{Active Consensus Stress Testing}
}`{=tex} \]

with:

\[ `\text{probe selection}`{=tex} `\rightarrow`{=tex}
`\text{response}`{=tex} `\rightarrow`{=tex}
`\text{posterior reliability}`{=tex} `\rightarrow`{=tex}
`\text{next probe}`{=tex} \]

and demonstrate:

\[ `\text{same reliability}`{=tex}
`\quad`{=tex}`\text{with fewer model calls}`{=tex}. \]

The strongest possible result would therefore not simply be:

> "our score has higher AUROC."

It would be:

> **"A consensus can be actively stress-tested before its correctness is
> known, and a small, adaptively chosen set of evidence probes provides
> substantially more reliability information per inference than static
> probing."**

That is the highest-value research direction in this roadmap.

------------------------------------------------------------------------

# 13. Immediate Next Actions

## Step A

Freeze the current RPI/Rsym implementation and baseline results.

## Step B

Launch parallel literature agents to attack:

-   Consensus Stress Testing
-   Expected-response faithfulness
-   Stress curves
-   Robustness--responsiveness
-   Active Consensus Probing

## Step C

Launch independent "killer" agents whose only task is to find existing
work that makes each concept non-novel.

## Step D

Run a small BoolQ/VitaminC pilot with:

-   semantics-preserving transformations;
-   semantics-changing transformations;
-   existing remove/reverse/substitute conditions.

## Step E

Measure:

\[ `\text{expected response accuracy}`{=tex} \]

at:

-   agent level;
-   consensus level;
-   correct consensus;
-   false consensus.

## Step F

Only if the phenomenon is strong, build the full stress curve.

## Step G

Only if the stress curve predicts future error, build active probing.

## Step H

Only after the method is frozen, run the expensive cross-model
evaluation.

------------------------------------------------------------------------

# 14. Research Principle

The autoresearch system should optimize for:

\[ `\boxed{
\text{Scientific novelty}
+
\text{falsifiability}
+
\text{cross-model validity}
+
\text{compute efficiency}
}`{=tex} \]

not:

\[ `\boxed{
\text{maximum benchmark score}
}`{=tex} \]

The system is allowed---and encouraged---to conclude:

> **The proposed idea is not novel enough.**

or:

> **The phenomenon exists but does not predict reliability.**

or:

> **The method works on Qwen but does not transfer.**

Such outcomes are research results, not failures of the autoresearch
process.
