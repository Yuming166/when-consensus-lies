# AutoResearch 0918
# Hindsight-to-Foresight Belief Distillation for Agent Reliability

## Status

Follow-up to:

    research0917.md
    consensus_stress/autoresearch_belief/

Previous decision:

    INTEGRATE-LIGHT

Previous autoresearch established:

- deterministic intervention-response trajectories contain agent-level reliability signal;
- agent-level prediction improves over the consensus-level baseline on Qwen and Ling;
- within-panel agent ranking is feasible;
- minority recovery shows positive signal;
- the small Astra subset does not provide stable replication;
- a hindsight Astra6 teacher can produce reasonably stable structured rankings;
- the first direct pre-outcome Astra6 foresight pilot FAILED to demonstrate useful agent-reliability prediction;
- the 20-item foresight pilot obtained AUROC ≈ 0.3339.

Therefore:

DO NOT tune the existing 20-item foresight prompt.

DO NOT treat hindsight teacher output as belief ground truth.

DO NOT claim that latent internal beliefs have been recovered.

This phase asks whether the negative foresight result reflects:

1. a bad pseudo-label target;
2. a bad distillation objective;
3. an unsuitable representation;
4. insufficient data;
5. teacher noise;
6. failure to exploit within-panel relational structure;

or whether hindsight-to-foresight belief distillation is fundamentally unsupported by the current CST signal.

---

# 0. North-Star Question

> Can outcome-aware hindsight attribution provide auxiliary supervision that improves pre-outcome identification of trustworthy agents beyond deterministic CST trajectory features?

Formal view:

Let:

    X_{i,a}

denote all information available before the outcome is revealed.

This may include:

    question
    presented evidence packet
    agent/persona identity
    original answer
    consensus state
    self-reported confidence if available
    deterministic CST intervention responses
    behavioral trajectory features

Let:

    y_i

be the revealed outcome.

A hindsight teacher models:

    q_phi(z_{i,a} | X_{i,a}, y_i)

while a foresight student must model:

    p_theta(z_{i,a} | X_{i,a})

without observing y_i.

The scientific question is whether:

    q_phi -> p_theta

distillation improves prediction of independently verifiable downstream outcomes.

---

# 1. Ground-Truth Evaluation Targets

Pseudo-labels are NEVER the primary evaluation target.

All methods must ultimately be evaluated against observable outcomes.

## T1 — Agent correctness

    c_{i,a} = 1[agent a's original answer == y_i]

Primary metrics:

    AUROC
    AUPRC
    Brier score
    ECE

---

## T2 — Within-panel agent ranking

For panels containing both correct and incorrect agents:

    correct agents > incorrect agents

Metrics:

    pairwise ranking accuracy
    MRR
    top-1 correct-agent rate
    NDCG if appropriate

---

## T3 — Majority-wrong minority recovery

For panels where:

    majority answer != y_i

and at least one minority agent is correct:

evaluate whether reliability-weighted aggregation recovers y_i.

Metrics:

    minority recovery accuracy
    panel accuracy
    delta over majority vote
    delta over confidence weighting
    delta over deterministic M5 weighting

This is the highest-value downstream endpoint.

---

# 2. Frozen Evaluation Before Method Search

This section is mandatory.

Before any method tournament begins:

1. create frozen train/dev/test splits;
2. group strictly by item;
3. prevent agents from the same item crossing splits;
4. freeze evaluation code;
5. freeze baseline implementations;
6. write split hashes to disk;
7. prohibit all tournament agents from modifying the test split.

Recommended:

    TRAIN
    DEV
    PROSPECTIVE_TEST

The prospective test set must not be inspected during method development.

Target prospective test size:

    >= 200 items

where feasible.

Additionally target:

    >= 50 majority-wrong disagreement panels

for the primary minority-recovery analysis.

If the current corpus cannot supply these numbers:

    report the actual maximum available
    do not fabricate or oversample duplicates
    consider generating a new frozen prospective batch only under a preregistered protocol

Output:

    consensus_stress/autoresearch_distill/
        frozen_protocol.md
        split_manifest.json
        split_hashes.json
        evaluation_spec.md

---

# 3. Allowed Information

Define three explicit information classes.

## PRE_OUTCOME_ALLOWED

May be used by student:

    question
    evidence packet presented to agent
    persona / agent identifier
    original response
    panel responses
    consensus answer
    consensus strength
    confidence if elicited before outcome
    paraphrase response
    natural-pair response
    remove response
    independent intervention response ONLY if declared available in the inference protocol
    deterministic behavioral features derived from these

---

## HINDSIGHT_TEACHER_ONLY

May be used only during pseudo-label generation:

    ground truth y_i
    original correctness
    post-outcome correctness comparisons

---

## EVALUATION_ONLY

May not be used for pseudo-label construction unless explicitly declared:

    held-out test correctness
    test-set aggregate statistics
    prospective-test labels during method selection

Every method must write:

    feature_manifest.json

and pass an automatic leakage audit.

---

# 4. Important Terminology

Do NOT call the teacher target:

    true belief
    ground-truth belief
    internal belief state

Preferred terms:

    hindsight attribution
    posterior reliability attribution
    behavioral reliability pseudo-label
    latent behavioral state
    inferred reliability state

The project may use "belief distillation" as a working name, but final paper terminology must depend on empirical identifiability.

---

# 5. Existing Baselines to Freeze

Before new methods, reproduce:

## B0 — Answer prior

## B1 — Persona + answer

## B2 — Confidence

## B3 — Consensus-level features

## B4 — Existing M4

## B5 — Existing deterministic M5 trajectory model

The previous result suggests approximately:

    Qwen M5 - M4 AUROC ≈ +0.0212
    Ling M5 - M4 AUROC ≈ +0.0178

Reproduce these under the new frozen split.

Do NOT compare new methods only against M4.

The primary baseline for this phase is:

    B5 = deterministic M5 trajectory model

A distillation method succeeds only if it adds value beyond B5.

---

# 6. Central Hypothesis

The weak direct Astra foresight result may occur because the previous setup asked an LLM to infer an underspecified scalar:

    "Which agent is trustworthy?"

Instead, hindsight information may be more distillable when represented as:

    soft posterior distributions
    pairwise preferences
    listwise rankings
    structured behavioral attributes
    contrastive relationships
    counterfactual response predictions

Therefore this phase performs a controlled method tournament.

---

# 7. Shared Teacher Input

For item i, hindsight teacher receives:

    Q_i
    evidence packets
    panel original responses
    deterministic CST trajectories
    relevant observable behavioral features
    revealed outcome y_i

The teacher MUST NOT receive hidden chain-of-thought.

If short rationales/citations are part of recorded outputs, treat them as optional observable features and run an ablation.

Teacher outputs must be structured JSON.

No free-form pseudo-label should enter training directly.

---

# 8. Shared Student Input

The student receives the SAME information as the teacher except:

    y_i is removed
    correctness indicators are removed
    hindsight explanations are removed

Therefore:

    Teacher: q_phi(z | X, y)

    Student: p_theta(z | X)

This information asymmetry must remain explicit throughout all experiments.

---

# 9. Parallel Method Tournament

Run the following Astra6 research agents in parallel.

Each agent owns a separate directory.

No agent may overwrite another agent's artifacts.

Each method agent must produce:

    METHOD.md
    implementation/
    dev_results.json
    ablations.json
    failure_analysis.md
    decision.md

Decision must be one of:

    ADVANCE
    MODIFY
    DROP

---

# Agent M1 — Hard Reliability Pseudo-Labels

## Goal

Establish the simplest pseudo-label baseline.

Teacher outputs:

    trustworthy / untrustworthy

or:

    most_trustworthy_agent

Student learns these hard labels.

Evaluate against actual correctness, not teacher agreement.

Purpose:

Determine whether naive pseudo-label distillation works at all.

Expected risk:

Teacher label may collapse to revealed correctness.

This is a baseline, not the preferred method.

---

# Agent M2 — Soft Posterior Reliability

Teacher outputs:

    p_teacher(correct_or_reliable | X, y)

for every agent.

Example:

    A1 0.11
    A2 0.28
    A3 0.82
    A4 0.67
    A5 0.19

Require:

    probabilities in [0,1]

Student predicts:

    p_student(r | X)

Candidate objectives:

    KL divergence
    soft binary cross entropy
    temperature-scaled distillation

Search a small frozen temperature grid.

Do not tune temperatures on test.

Question:

> Are soft targets more distillable than hard trust labels?

---

# Agent M3 — Pairwise Reliability Distillation

## High-priority method

Avoid absolute trust scores.

For each within-panel pair:

    (A_a, A_b)

teacher predicts:

    A_a > A_b
    A_a = A_b
    A_a < A_b

in behavioral reliability.

Construct pairwise pseudo-label probabilities:

    p(A_a more reliable than A_b)

Train student with pairwise ranking loss.

Possible objectives:

    Bradley-Terry
    logistic pairwise loss
    margin ranking loss

Primary downstream metric:

    within-panel ranking

Secondary:

    agent correctness AUROC

Key question:

> Is relative trust easier to distill than absolute trust?

---

# Agent M4 — Listwise Panel Distillation

Treat the entire panel jointly.

Teacher outputs a distribution:

    pi_teacher(A1...A5)

such that:

    sum pi = 1.

Example:

    [0.08, 0.12, 0.51, 0.20, 0.09]

Student predicts:

    pi_student(A1...A5)

Possible objectives:

    listwise cross entropy
    KL divergence
    Plackett-Luce-style ranking

Evaluate:

    top-1 correct-agent rate
    MRR
    minority recovery

This explicitly models the fact that reliability is relational within a panel.

---

# Agent M5 — Structured Behavioral-State Distillation

Teacher does NOT directly output one trust score.

Teacher outputs structured attributes:

    semantic_stability
    directional_responsiveness
    counterevidence_sensitivity
    behavioral_consistency
    inferred_commitment_strength
    posterior_reliability

Each field:

    probability or bounded scalar

Whenever a field is deterministically computable:

    compute it programmatically

and do NOT ask teacher to hallucinate it.

Train student multi-task:

    L =
      lambda_s L_stability
    + lambda_d L_direction
    + lambda_c L_consistency
    + lambda_b L_commitment
    + lambda_r L_reliability

Run ablations:

    no reliability head
    no belief-strength head
    deterministic attributes only
    inferred attributes only

Question:

> Does intermediate behavioral supervision make reliability more distillable?

---

# Agent M6 — Contrastive Reliability Representation

Learn representation:

    h_{i,a} = encoder(X_{i,a})

Use hindsight information to construct training relationships.

Within the same item:

    correct agent = positive
    incorrect agent = negative

or teacher-defined high/low reliability pairs.

Objectives:

    supervised contrastive loss
    triplet loss
    InfoNCE-style loss

Then train a lightweight reliability head on h.

Critical evaluation:

Does representation generalize across items and model families?

---

# Agent M7 — Hybrid True-Label + Pseudo-Label Training

## Highest-priority method

Because actual agent correctness is available during training, do not unnecessarily replace real supervision with pseudo-labels.

Train:

    L_total =
        L_correctness
      + lambda_1 L_teacher
      + lambda_2 L_ranking
      + lambda_3 L_behavior

where:

    L_correctness = true agent correctness supervision
    L_teacher = soft teacher attribution
    L_ranking = within-panel ranking
    L_behavior = auxiliary intervention-response prediction

Search a SMALL preregistered lambda grid.

Example:

    lambda ∈ {0, 0.1, 0.3, 1.0}

No large hyperparameter search.

Critical comparison:

    true labels only
    pseudo-labels only
    hybrid

The key scientific question:

> Does hindsight attribution provide useful auxiliary structure beyond direct correctness supervision?

---

# Agent M8 — Confidence-Weighted Pseudo-Labels

Teacher pseudo-label quality may vary substantially.

Estimate teacher confidence using:

    repeated teacher samples
    inter-run agreement
    entropy
    consistency with observable behavioral features

Define:

    w_i,a ∈ [0,1]

Train:

    L =
    Σ w_i,a L_pseudo(i,a)

Compare:

    all pseudo-labels
    high-confidence only
    confidence-weighted
    deterministic filtering

Question:

> Does filtering noisy hindsight supervision make foresight distillation viable?

---

# Agent M9 — Multi-Teacher Consensus

Generate hindsight attribution using multiple independent teacher samples and, if feasible, multiple model families.

Construct:

    mean posterior
    median posterior
    consensus ranking
    disagreement entropy

Only distill high-agreement cases in one condition.

Compare:

    single teacher
    self-consistency teacher
    ensemble teacher

Important:

Do not interpret teacher agreement as truth.

Evaluate only against real downstream correctness.

---

# Agent M10 — Counterfactual Response Distillation

## High-priority alternative

Do NOT teach reliability directly.

Instead teach:

> How would this agent respond to another intervention?

For a held-out intervention I*:

    p(flip under I* | observed trajectory)

Teacher may use hindsight context during training, but target response itself should be observable whenever possible.

Examples:

    observe original + paraphrase + natural
    predict independent-CONTRADICT response

or:

    observe original + natural
    predict paraphrase/remove response

Train a behavioral-state representation.

Then use:

    representation -> agent correctness

with true labels.

This tests whether the student can learn a genuine predictive behavioral state rather than imitate teacher trust scores.

---

# Agent M11 — Leave-One-Intervention-Out State Modeling

For each intervention type:

    hold it out

and predict its response from remaining interventions.

Examples:

    para -> held out
    natural -> held out
    remove -> held out
    independent agree -> held out
    independent contradict -> held out

Metrics:

    response AUROC
    accuracy
    Brier

Then test whether held-out-response predictive representations improve:

    agent correctness
    ranking
    minority recovery

This is a falsification test for "latent behavioral state."

If trajectories cannot predict future/held-out behavior:

    do not claim latent-state recovery.

---

# Agent M12 — Direction-Explicit Reliability Model

Current CST evidence indicates direction is a dominant mechanism.

Model this explicitly.

Construct features such as:

    response_to_AGREE
    response_to_CONTRADICT
    response_to_PARAPHRASE
    response_to_REMOVE

Estimate a directional response profile:

    alpha = P(flip | CONTRADICT)
    beta  = P(flip | AGREE)

and derived features such as:

    directional_selectivity = alpha - beta

Do not assume this exact formula is optimal.

Compare:

    direction-only
    raw trajectory
    structured directional profile
    direction + teacher distillation

Question:

> Does teacher supervision add anything after the known direction signal is modeled explicitly?

This is mandatory.

---

# Agent M13 — Panel-Context Relational Model

Agent reliability may depend on other agents.

Instead of:

    r_a = g(X_a)

model:

    r_a = g(X_a, X_{-a})

Possible lightweight architectures:

    set encoder
    permutation-invariant pooling
    small attention-based panel encoder

Do not build an unnecessarily large architecture.

Compare:

    independent agent scoring

versus:

    panel-conditioned scoring.

Important downstream test:

    majority-wrong panels.

---

# Agent M14 — Teacher Target Search

Treat pseudo-label DESIGN as the research variable.

Compare teacher targets:

T1:
    absolute reliability

T2:
    probability of correctness

T3:
    pairwise trust

T4:
    panel ranking

T5:
    directional responsiveness

T6:
    belief/commitment strength

T7:
    expected response to counterevidence

For each target measure:

    teacher stability
    correlation with correctness
    correlation with M5
    student distillability
    downstream gain

Primary question:

> Which hindsight target is actually recoverable from pre-outcome information?

This agent should produce a target-selection matrix.

---

# Agent M15 — Direct LLM Judge Baseline

Important reviewer baseline.

Give a foresight LLM:

    original question
    evidence
    original agent outputs

without CST intervention trajectories.

Ask it to rank agents.

Then provide CST trajectories.

Compare:

    Judge(original only)
    Judge(original + confidence)
    Judge(original + CST)

This answers:

> Does behavioral intervention information actually help an LLM judge?

Do not tune the failed 20-item prompt endlessly.

Use a frozen prompt family and sufficient held-out evaluation.

---

# Agent M16 — Adversarial Distillation Auditor

This agent tries to destroy the result.

Test:

    answer prior leakage
    persona leakage
    natural-pair direction leakage
    teacher correctness tautology
    panel composition leakage
    benchmark label metadata leakage
    model-family leakage
    duplicated items
    train/test item contamination
    confidence leakage
    pseudo-label memorization

Run shuffled-label controls.

Run:

    pseudo-label permutation
    teacher-output permutation
    trajectory permutation within label
    persona permutation

If a supposedly sophisticated model survives nonsensical pseudo-labels:

    investigate leakage immediately.

Output:

    adversarial_audit.md

---

# 10. Teacher Pseudo-Label Schema

Use a common schema where applicable.

Example:

{
  "item_id": "...",
  "agent_id": "...",

  "posterior": {
    "correctness_probability": 0.0,
    "reliability_probability": 0.0,
    "commitment_strength": 0.0,
    "directional_responsiveness": 0.0
  },

  "pairwise_preferences": {
    "A1": 0.0,
    "A2": 0.0,
    "A3": 0.0,
    "A4": 0.0
  },

  "teacher_confidence": 0.0,

  "observable_support": {
    "paraphrase_stable": true,
    "natural_response": "...",
    "directional_pattern": "..."
  }
}

Do not include unrestricted chain-of-thought.

Short evidence references or concise justifications may be stored separately for analysis but must not automatically become student input.

---

# 11. Teacher Stability Study

Before scaling pseudo-label generation:

Sample:

    >= 100 items if possible

stratified across:

    consensus correct
    consensus wrong
    disagreement
    majority wrong
    Qwen
    Ling

Run:

    >= 3 independent teacher generations

Measure:

    score correlation
    pairwise ranking agreement
    top-1 agreement
    entropy
    calibration against actual correctness

If teacher stability is poor:

    prioritize M8/M9 filtering
    do not scale naive pseudo-label generation

---

# 12. Student Families

Do not assume the student must itself be an LLM.

Compare:

## S1 — Logistic / linear

## S2 — Tree-based lightweight model

## S3 — Small MLP

## S4 — Pairwise ranking model

## S5 — Panel relational model

## S6 — LLM prompted foresight model

## S7 — Fine-tuned/open-weight student if justified

A simple student beating an LLM judge is a valid and potentially interesting result.

Complexity is not the goal.

---

# 13. Model Selection Rules

All tournament agents may inspect:

    TRAIN
    DEV

They may NOT inspect:

    PROSPECTIVE_TEST labels.

Select finalists using a composite DEV criterion.

Suggested hierarchy:

1. within-panel pairwise ranking;
2. agent correctness AUROC;
3. minority recovery;
4. calibration;
5. complexity/cost.

Do NOT construct an arbitrary scalar leaderboard unless necessary.

Prefer Pareto selection.

Advance approximately:

    top 3–5 qualitatively distinct methods

to prospective evaluation.

---

# 14. Wave Structure

## WAVE 0 — Freeze

Single protocol agent:

    split data
    freeze hashes
    reproduce B0–B5
    run leakage checks

No method development before completion.

---

## WAVE 1 — Teacher / Target Exploration

Parallel:

    M1 Hard labels
    M2 Soft posterior
    M3 Pairwise
    M4 Listwise
    M5 Structured state
    M8 Confidence weighting
    M9 Multi-teacher
    M14 Target search

Goal:

Identify pseudo-label targets that are:

    stable
    nontrivial
    distillable

---

## WAVE 2 — Representation / Learning

Parallel:

    M6 Contrastive
    M7 Hybrid
    M10 Counterfactual response
    M11 Held-out intervention
    M12 Direction-explicit
    M13 Relational model
    M15 Direct judge baseline

Goal:

Determine how to convert teacher/behavioral information into pre-outcome reliability.

---

## WAVE 3 — Adversarial Audit

Run M16 against all advancing methods.

Methods failing leakage/permutation controls are eliminated.

---

## WAVE 4 — Prospective Evaluation

Select only 3–5 finalists.

Unlock PROSPECTIVE_TEST labels once.

No further tuning after this point.

Evaluate:

    actual correctness
    ranking
    minority recovery
    calibration
    cross-family transfer

---

## WAVE 5 — Independent Astra6 Synthesis

Assign a fresh Astra6 agent that did NOT develop any candidate method.

It receives:

    frozen protocol
    all method reports
    dev results
    prospective results
    adversarial audit

It must adjudicate the scientific evidence.

---

# 15. Key Ablation Matrix

Every finalist should be evaluated under:

    Original only

    Original + Confidence

    Original + CST

    Original + CST + Direction

    Original + CST + Teacher

    Original + CST + Direction + Teacher

    Full method

This is necessary to answer:

> What exactly does pseudo-label distillation add?

---

# 16. Pairwise Distillation Experiment

Because "absolute reliability" lacks a natural continuous ground truth, pairwise ranking receives special priority.

For mixed-correctness panel:

    A_correct
    A_wrong

true evaluation relation is:

    A_correct > A_wrong

Teacher may provide a softer relation:

    P(A_correct > A_wrong | X, y)

Student predicts:

    P(A_a > A_b | X)

without y.

Use:

    item-grouped training

and evaluate all valid correct/incorrect pairs.

Important comparison:

    deterministic pairwise M5

versus:

    teacher-distilled pairwise model.

If pairwise works while scalar trust does not:

    prefer pairwise framing.

---

# 17. Hybrid Objective Experiment

Recommended main candidate:

    L =
        L_true_correctness
      + lambda_pair L_teacher_pair
      + lambda_state L_behavior_state
      + lambda_cf L_counterfactual

where:

    L_true_correctness

uses actual TRAIN correctness only.

Teacher supervision is auxiliary.

Test:

A:
    true correctness only

B:
    pseudo-label only

C:
    true + soft teacher

D:
    true + pairwise teacher

E:
    true + behavioral-state

F:
    true + pairwise + behavioral-state

G:
    full hybrid

This experiment determines whether teacher pseudo-labels genuinely add information.

---

# 18. Cross-Family Transfer

At minimum attempt:

    Train Qwen -> Test Ling
    Train Ling -> Test Qwen

If pseudo-labels are model-specific:

    report this.

If behavioral representation transfers:

    emphasize this.

Also compare:

    teacher trained/generated on one family
    student evaluated on another

where scientifically valid.

Do not force a universal-transfer claim.

---

# 19. Majority-Wrong Challenge Set

Create a dedicated frozen subset:

    majority answer wrong
    at least one correct minority agent
    all required pre-outcome features available

Target:

    >= 50 panels

preferably more.

For each method compute:

    recovery accuracy
    confidence interval
    number corrected
    number newly broken

Important metric:

    net correction

defined as:

    wrong-majority panels corrected
    minus
    originally recoverable panels damaged

Also report overall panel accuracy separately.

Do not optimize only on the challenge set.

---

# 20. Prospective Test

Target:

    >= 200 held-out items

Prefer:

    balanced model families
    sufficient mixed-correctness panels
    sufficient wrong-consensus/disagreement cases

All pseudo-label generation and student training must be complete before test labels are opened.

Record:

    git commit
    config hash
    model versions
    prompts
    random seeds
    dataset hashes

before evaluation.

---

# 21. Success Gates

## GATE A — Teacher quality

PASS if at least one hindsight target is:

    reasonably stable across teacher runs

AND:

    related to actual correctness/ranking

AND:

    not reducible entirely to trivial deterministic fields.

---

## GATE B — Distillability

PASS if a foresight student predicts actual held-out agent correctness/ranking meaningfully above trivial baselines.

Teacher agreement alone does not count.

---

## GATE C — Increment Beyond M5

Critical gate.

PASS if at least one distillation method improves over deterministic M5 on prospective data in a meaningful endpoint.

Prefer:

    paired bootstrap CI supporting positive increment

on:

    agent ranking
    or minority recovery

AUROC-only marginal gains are weaker evidence.

---

## GATE D — Direction Control

PASS if the gain is not fully eliminated by a direction-only baseline.

If direction explains most of the gain:

    MODIFY claim.

---

## GATE E — Minority Utility

Strong PASS if:

    distilled reliability

improves majority-wrong recovery over:

    majority vote
    confidence weighting
    deterministic M5

without unacceptable degradation elsewhere.

---

# 22. Stop Conditions

Stop belief-distillation development if, after the tournament:

1. no method beats deterministic M5 prospectively;
2. teacher pseudo-labels are unstable;
3. gains disappear under direction control;
4. pseudo-label permutation performs similarly;
5. teacher supervision only reproduces correctness labels;
6. minority recovery does not improve;
7. apparent gains rely on test-set tuning.

Then final decision:

    DROP-DISTILLATION

This is an acceptable scientific outcome.

Do NOT continue prompt tuning indefinitely.

---

# 23. Possible Final Outcomes

## Outcome A — Strong success

Pairwise/structured/hybrid distillation improves:

    agent ranking
    minority recovery
    prospective correctness

beyond M5.

Decision:

    INTEGRATE-MAJOR

Potential paper contribution:

> Hindsight-supervised behavioral attribution can be distilled into pre-outcome agent reliability estimates.

---

## Outcome B — Limited success

Small agent-level gain, no robust minority gain.

Decision:

    INTEGRATE-LIGHT

Use as secondary extension.

---

## Outcome C — Behavioral state works, trust pseudo-labels fail

Held-out intervention prediction succeeds, but teacher trust distillation does not.

Decision:

    REFRAME

Potential contribution:

> CST trajectories support predictive behavioral-state modeling, but not validated latent belief recovery.

This is scientifically interesting.

---

## Outcome D — Pairwise works, scalar belief fails

Decision:

    REFRAME-PAIRWISE

Use:

    comparative agent reliability

instead of:

    latent belief score.

This may be preferable conceptually.

---

## Outcome E — Full failure

No prospective improvement beyond deterministic M5.

Decision:

    DROP-DISTILLATION

Keep the previous INTEGRATE-LIGHT behavioral reliability result.

---

# 24. Required Statistical Reporting

For all main comparisons:

    point estimate
    95% item-bootstrap CI
    paired bootstrap delta

For AUROC:

    bootstrap by item

For ranking:

    bootstrap by panel/item

For minority recovery:

    exact counts
    proportion
    bootstrap CI where meaningful

Never bootstrap individual agent rows independently when they belong to the same panel.

---

# 25. Required Final Tables

## Table 1 — Teacher Target Quality

Columns:

    Target
    Stability
    Correctness correlation
    Direction correlation
    Distillability
    Verdict

---

## Table 2 — Agent Reliability

Rows:

    Confidence
    M4
    M5
    Direct LLM Judge
    Hard Distill
    Soft Distill
    Pairwise
    Listwise
    Structured
    Contrastive
    Hybrid
    Best Final

Columns:

    AUROC
    AUPRC
    Brier
    ECE

---

## Table 3 — Within-Panel Ranking

Columns:

    Pairwise Accuracy
    MRR
    Top-1 Correct
    CI

---

## Table 4 — Majority-Wrong Recovery

Columns:

    Method
    N panels
    Recovered
    Broken
    Net Corrected
    Recovery Accuracy

---

## Table 5 — Ablations

Rows:

    -confidence
    -direction
    -teacher
    -behavioral state
    -pairwise objective
    shuffled teacher
    shuffled trajectory

---

# 26. Required Final Figures

If results warrant figures:

## Figure A

Hindsight-to-Foresight Distillation:

    CST trajectories
         ↓
    Hindsight posterior q(z|X,y)
         ↓
    structured / pairwise pseudo-labels
         ↓
    Foresight prior p(z|X)
         ↓
    agent reliability

Clearly mark:

    outcome visible only during training.

---

## Figure B

Within-panel reliability example:

    majority wrong
    minority correct

show:

    votes
    behavioral trajectories
    inferred reliability
    weighted decision

Do not imply internal belief access.

---

## Figure C

Teacher target vs student distillability.

Possible scatter:

    teacher stability
        vs
    prospective student gain.

This may reveal that the most interpretable target is not the most distillable target.

---

# 27. Paper-Safe Claims

Potentially safe IF supported:

> Controlled intervention trajectories contain agent-specific reliability information.

> Hindsight attribution can provide auxiliary supervision for pre-outcome reliability estimation.

> Relative agent reliability is more readily recoverable than an absolute latent belief score.

> Behavioral reliability weighting can recover some cases where the majority decision is incorrect.

> The useful signal is item-conditioned and behavioral rather than evidence of persistent agent competence.

---

# 28. Claims to Avoid

Do NOT say:

> We recover the agent's true belief.

Do NOT say:

> The teacher provides ground-truth beliefs.

Do NOT say:

> The student learns human-like theory of mind.

Do NOT say:

> The model identifies the objectively most trustworthy agent.

Prefer:

> predicts which agent's current judgment is more likely to be correct.

Do NOT say:

> Distillation corrects false consensus

unless prospective downstream results support it.

---

# 29. Novelty Criterion

The contribution is NOT:

> using pseudo-labels.

The contribution, if successful, is the combination:

    controlled behavioral intervention
        +
    hindsight posterior attribution
        +
    pre-outcome distillation
        +
    within-panel reliability estimation
        +
    minority recovery

The central scientific finding should be:

> What information about agent reliability is recoverable from behavioral stress responses before outcomes are known?

---

# 30. Resource Policy

Use Astra6 aggressively for:

    teacher target generation
    independent method design
    prompt variants within frozen families
    reviewer/red-team analysis
    synthesis

Do NOT waste Astra6 calls on:

    recomputing deterministic features
    simple baselines
    bootstrap
    data joins
    leakage checks
    metrics

Use local computation for those.

Before large teacher generation:

    estimate call budget
    run stability pilot
    pass Gate A

---

# 31. Git / Reproducibility

Create:

    consensus_stress/autoresearch_distill/

Suggested structure:

    00_protocol/
    01_data/
    02_baselines/
    03_teacher_targets/
    04_methods/
        M01_hard/
        M02_soft/
        M03_pairwise/
        M04_listwise/
        M05_structured/
        M06_contrastive/
        M07_hybrid/
        M08_weighted/
        M09_multiteacher/
        M10_counterfactual/
        M11_heldout/
        M12_direction/
        M13_relational/
        M14_target_search/
        M15_judge/
        M16_audit/
    05_finalists/
    06_prospective/
    07_synthesis/

Every result must include:

    config
    code
    seed
    input manifest
    output JSON/CSV
    README

Do not push intermediate secrets, credentials, caches, or large model artifacts.

---

# 32. Final Independent Synthesis

A fresh Astra6 synthesis agent must answer:

1. Did hindsight supervision provide information beyond deterministic CST trajectories?
2. Which pseudo-label target was most stable?
3. Which target was most distillable?
4. Did scalar reliability work?
5. Did pairwise reliability work?
6. Did structured behavioral-state learning work?
7. Did held-out intervention prediction work?
8. Did gains survive direction control?
9. Did gains transfer across Qwen/Ling?
10. Did any method improve majority-wrong recovery?
11. Did pseudo-labels add value beyond true-label training?
12. Is "belief" terminology justified?
13. Should this become a main CST contribution?

Final verdict must be exactly one:

    INTEGRATE-MAJOR
    INTEGRATE-LIGHT
    REFRAME-PAIRWISE
    REFRAME-BEHAVIORAL-STATE
    DROP-DISTILLATION

Required outputs:

    FINAL_SYNTHESIS.md
    FINAL_DECISION.md
    METHOD_WINNER.md
    TEACHER_TARGET_ANALYSIS.md
    PROSPECTIVE_RESULTS.md
    MINORITY_RECOVERY.md
    DIRECTION_AUDIT.md
    PAPER_SAFE_CLAIMS.md
    PAPER_UNSAFE_CLAIMS.md
    NEXT_EXPERIMENTS.md

---

# 33. Final Decision Rule

The goal is NOT to find a method that looks good on DEV.

The goal is to answer:

> Is there a reproducible path from outcome-aware hindsight attribution to outcome-blind agent reliability?

The strongest evidence would be:

    hindsight teacher
        ↓
    pairwise / structured supervision
        ↓
    foresight student
        ↓
    prospective agent ranking
        ↓
    correct minority recovery

with improvement over:

    deterministic M5
    confidence
    direction-only
    direct LLM judge

If this chain survives frozen prospective evaluation and adversarial audit:

    integrate it.

Otherwise:

    preserve the negative result and retain deterministic behavioral reliability.

---

# 34. North-Star Success Case

The most valuable result is not a higher teacher-student agreement score.

It is a case where:

    3 agents vote NO
    2 agents vote YES
    ground truth is hidden

and the pre-outcome model, using behavioral stress responses, assigns greater reliability to the two YES agents and selects YES.

Later:

    ground truth = YES.

Repeated across a sufficiently large frozen test set, this would establish that behavioral reliability inference can identify when a minority judgment deserves greater weight than raw consensus.

That is the target.
