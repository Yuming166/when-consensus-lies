# AutoResearch: Behavioral Belief Attribution from Consensus Stress Tests

## Project
**Working title:** Behavioral Belief Attribution for Multi-Agent LLM Reliability

**Repository:** `when-consensus-lies`

**Primary working directory:** `consensus_stress/`

**Target venue:** NAACL Main / ARR

**Research mode:** Multi-agent parallel autoresearch with Astra6

---

# 0. Executive Goal

The existing Consensus Stress Testing (CST) framework asks:

> Can controlled evidence interventions reveal whether a multi-agent consensus is reliable before the outcome is known?

This autoresearch phase asks a stronger question:

> Can the same intervention responses reveal which individual agents should be trusted?

The goal is NOT merely to add a more complicated classifier on top of CST.

The goal is to test whether controlled interventions expose a latent, agent-specific reliability state that cannot be recovered from:

- majority agreement,
- answer identity,
- self-reported confidence,
- raw agent output,
- persona identity,
- or simple consensus-level CST scores alone.

The desired research progression is:

CST interventions
    ↓
Agent-specific behavioral trajectories
    ↓
Latent belief / reliability attribution
    ↓
Agent-level trust estimates
    ↓
Consensus reliability + trustworthy aggregation

A particularly important downstream test is:

> When the panel disagrees, can behavioral stress responses identify a correct minority agent?

If successful, this extension should transform CST from a consensus-level risk score into a framework for **behavioral belief attribution and trustworthy multi-agent aggregation**.

---

# 1. Scientific Motivation

## 1.1 Current CST

For item i and agent a, the current framework observes responses under controlled evidence conditions:

    original
    paraphrase
    natural pair
    independent agree
    independent contradict
    placebo
    auxiliary interventions

Conceptually:

    T_{i,a} = {
        y_orig,
        y_para,
        y_nat,
        y_ind_agree,
        y_ind_contra,
        ...
    }

The primary CST score currently aggregates selected behavioral responses across agents.

However, aggregation discards agent-level structure.

Two panels may have identical original votes:

    [YES, YES, YES, YES, YES]

while exhibiting very different intervention trajectories.

Likewise, in a disagreement panel:

    [YES, YES, YES, NO, NO]

the two minority agents may be behaviorally more reliable than the majority.

This information is currently underused.

---

# 2. Central Research Question

## RQ1 — Agent-level identifiability

Do intervention trajectories contain information about individual agent correctness beyond the original answer and confidence?

Formally:

    P(correct_{i,a} | T_{i,a}, Q_i, E_i)

should outperform:

    P(correct_{i,a} | answer_{i,a})

and strong conventional uncertainty baselines.

---

## RQ2 — Latent belief strength

Can intervention responses reveal latent belief strength that is not captured by discrete answers or self-reported confidence?

For example, two agents may both answer YES:

    Agent A: latent support ≈ 0.52
    Agent B: latent support ≈ 0.95

but respond differently to controlled evidence stress.

We ask whether behavioral trajectories recover this distinction.

---

## RQ3 — Trustworthy agent identification

Given a panel of agents, can we estimate:

    r_{i,a} = P(agent a is reliable on item i | pre-outcome observations)

and identify the most trustworthy agent:

    a* = argmax_a r_{i,a}

without observing the ground-truth outcome at inference time?

---

## RQ4 — Correct minority identification

In disagreement cases, can the inferred reliability model identify cases where the correct answer is held by a minority?

This is a particularly important falsifiable downstream test.

Evaluate:

    majority vote

versus:

    reliability-weighted aggregation.

---

## RQ5 — Hindsight-to-foresight belief attribution

Can a posterior/hindsight model that observes the revealed outcome produce useful structured reliability pseudo-labels, which can then be distilled into a pre-outcome model?

Conceptual inspiration:

    hindsight attribution
        ↓
    structured pseudo-label
        ↓
    foresight reliability inference

The deployment model MUST NOT observe the outcome.

---

# 3. Critical Scientific Constraint

Do NOT assume that an LLM-generated "trustworthiness" score is ground truth.

A teacher saying:

    "Agent 3 is the most trustworthy"

is NOT sufficient evidence.

Pseudo-labels must be anchored as strongly as possible in observable and verifiable behavior.

Distinguish:

### Directly observable

- original answer
- answer correctness after outcome reveal
- paraphrase stability
- natural-pair response
- independent-AGREE response
- independent-CONTRADICT response
- intervention flip patterns
- confidence if explicitly elicited
- panel agreement
- persona
- evidence condition
- response consistency

### Latent / inferred

- belief strength
- evidence sensitivity
- susceptibility to directional evidence
- agent reliability
- trustworthiness
- responsibility for panel error

The paper MUST NOT present latent pseudo-labels as factual psychological states.

Use terminology such as:

- inferred behavioral reliability
- latent reliability attribution
- behavioral belief state

Avoid anthropomorphic claims about internal beliefs unless carefully qualified.

---

# 4. Proposed Representation

For each agent:

    z_{i,a} = (
        b_{i,a},
        s_{i,a},
        u_{i,a},
        r_{i,a}
    )

where:

### b — inferred belief strength

How strongly the observable behavior supports the original decision.

### s — semantic stability

Resistance to meaning-preserving perturbations.

Primarily informed by paraphrase controls.

### u — directional responsiveness

How systematically the agent updates under evidence that agrees with or contradicts its current decision.

### r — behavioral reliability

Estimated probability that this agent's current decision should be trusted.

Do NOT assume these four dimensions are statistically identifiable.

One purpose of autoresearch is to determine whether they can actually be separated.

---

# 5. Proposed Hindsight → Foresight Architecture

## 5.1 Posterior / Hindsight Attributor

During offline training only, allow a strong teacher to observe:

    Q_i
    E_i
    ground truth y_i
    original panel responses
    intervention trajectories T_{i,1...A}

The teacher outputs a structured attribution.

Example schema:

{
  "agent_id": "A3",
  "original_correct": true,
  "paraphrase_stable": true,
  "directionally_responsive": true,
  "behavioral_consistency": 0.84,
  "inferred_belief_strength": 0.78,
  "posterior_reliability": 0.86,
  "evidence_for_attribution": [...]
}

IMPORTANT:

The teacher should separate:

    deterministic fields

from:

    inferred fields.

Deterministic fields should be computed programmatically whenever possible, not generated by the LLM.

---

## 5.2 Foresight / Prior Attributor

The deployment model receives:

    Q_i
    E_i
    original responses
    intervention trajectories

but NOT:

    y_i

and predicts:

    r_hat_{i,1...A}

Optionally:

    z_hat_{i,1...A}.

The model should approximate posterior reliability attribution without outcome access.

---

# 6. Minimal Models Before LLM Modeling

Do NOT jump directly to an LLM judge.

First determine whether the signal exists using simple models.

Required models:

M0 — answer-only baseline

M1 — persona + answer

M2 — self-reported confidence

M3 — raw consensus features

M4 — original CST aggregate features

M5 — agent-level intervention features

M6 — simple logistic regression / monotonic model

M7 — lightweight tree-based model if appropriate

Only if M5/M6 show meaningful signal should the project proceed to:

M8 — LLM belief attributor

M9 — hindsight-distilled foresight attributor

This ordering is mandatory.

---

# 7. Primary Hypotheses

## H1 — Agent-level signal

Agent-level CST trajectories predict individual correctness beyond answer/confidence baselines.

Primary metric:

    AUROC(agent correctness)

Secondary:

    AUPRC
    ECE
    Brier score

---

## H2 — Intervention increment

Adding intervention trajectories improves prediction over:

    original answer + confidence + persona

Use paired bootstrap confidence intervals.

---

## H3 — Correct-agent ranking

Within each panel, reliability scores rank correct agents above incorrect agents.

Metrics:

    pairwise ranking accuracy
    MRR of correct agents
    NDCG where appropriate
    top-1 trustworthy-agent accuracy

---

## H4 — Minority recovery

Among disagreement panels where the majority is wrong:

    reliability-weighted aggregation

should recover the correct answer more frequently than:

    majority vote
    confidence-weighted vote

This is one of the strongest possible downstream results.

---

## H5 — Foresight distillation

A pre-outcome attributor trained from structured hindsight attribution retains meaningful reliability signal without observing outcomes.

Compare:

    hindsight teacher
    foresight student
    direct supervised correctness predictor
    heuristic CST

---

# 8. Null / Falsification Hypotheses

Actively attempt to falsify the proposed story.

## F1 — Persona prior

Reliability prediction may simply learn:

    persona → accuracy.

Test leave-persona-out generalization.

---

## F2 — Answer prior

Prediction may simply learn:

    YES vs NO.

Report label-stratified metrics and worst-label AUROC.

---

## F3 — Confidence leakage

Agent-level reliability may be almost completely explained by confidence.

Compare:

    confidence

versus:

    confidence + CST trajectory.

---

## F4 — Natural-pair direction leakage

Agent reliability may simply re-encode the already known natural-pair direction signal.

Compare:

    direction-only

versus:

    full trajectory.

Perform direction-matched evaluations where possible.

---

## F5 — Teacher tautology

The hindsight teacher may simply rank agents according to whether their original answer equals ground truth.

This would make pseudo-labeling scientifically trivial.

Test whether teacher attribution adds anything beyond:

    correctness + deterministic behavioral features.

If not, DROP the teacher-based framing.

---

## F6 — Judge self-preference

If the same model family generates responses and judges reliability, the judge may prefer stylistically similar outputs.

Cross-family judging is mandatory.

---

## F7 — Intervention-count artifact

More calls may mechanically produce more information.

Compare equal-budget baselines.

---

## F8 — No stable agent identity

If personas do not produce persistent agent-specific behavioral tendencies across items, the concept of "which agent is most trustworthy" may not be meaningful beyond item-specific reliability.

Explicitly test:

    persistent agent reliability

versus:

    item-conditioned reliability.

Do not conflate them.

---

# 9. Multi-Agent Astra6 Work Plan

Run the following workstreams in parallel.

Each agent MUST produce:

1. a concise report,
2. reproducible code,
3. machine-readable results,
4. failure analysis,
5. recommendation: CONTINUE / MODIFY / DROP.

Do not allow agents to modify the same result files concurrently.

---

## Agent Group A — Data Archaeology

### Goal

Determine exactly what data already exists.

Tasks:

- inspect `consensus_stress/`
- map all experiment artifacts
- identify item IDs shared across intervention runs
- identify agent/persona IDs
- identify original answers
- identify intervention responses
- identify ground truth
- identify confidence fields
- identify evidence metadata
- determine which intervention conditions are available per item
- quantify missingness

Output:

    autoresearch_belief/data_inventory.md
    autoresearch_belief/data_schema.json
    autoresearch_belief/item_coverage.csv

No new LLM calls.

---

## Agent Group B — Agent-Level Dataset Builder

Construct one row per:

    (item, agent)

Target:

    original_correct ∈ {0,1}

Candidate features:

    original_answer
    consensus_answer
    consensus_strength
    persona
    confidence
    paraphrase_flip
    natural_flip
    independent_agree_flip
    independent_contradict_flip
    placebo_flip
    number_of_flips
    directional_asymmetry
    semantic_stability
    response_entropy
    intervention consistency

Create strict pre-outcome feature masks.

Outcome must NEVER enter feature construction.

Output:

    agent_level_dataset.parquet
    feature_dictionary.md
    leakage_audit.md

---

## Agent Group C — Simple Predictability Probe

Run the cheapest decisive experiment.

Question:

> Can agent-level behavioral trajectories predict individual correctness?

Models:

    answer prior
    confidence
    consensus features
    CST aggregate
    logistic regression on trajectory
    simple monotonic model

Evaluation:

    grouped split by item

NEVER randomly split individual agent rows across train/test.

Report:

    AUROC
    AUPRC
    Brier
    ECE
    bootstrap CI

Also:

    label-stratified
    persona-stratified
    model-family-stratified

Primary decision:

If intervention trajectories do NOT outperform strong non-intervention baselines, flag the entire extension as likely DROP.

---

## Agent Group D — Agent Ranking

Evaluate whether scores rank agents within the SAME item.

Important subset:

    panels containing both correct and incorrect agents.

Metrics:

    pairwise ranking accuracy
    MRR(correct agent)
    top-1 correct-agent rate
    calibration of r_hat

Exclude unanimous-correct and unanimous-wrong panels from ranking analyses where ranking is undefined.

---

## Agent Group E — Minority Recovery

Construct disagreement subsets:

    majority correct
    majority wrong
    tie / near tie
    correct minority exists

Compare:

    majority vote
    confidence-weighted vote
    CST-weighted vote
    learned reliability-weighted vote
    oracle reliability

Key metric:

    accuracy on majority-wrong disagreement cases

Also report:

    overall accuracy

to prevent cherry-picking.

This experiment has high scientific priority.

---

## Agent Group F — Latent Belief Feasibility

Investigate whether intervention trajectories support something richer than correctness prediction.

Questions:

1. Are paraphrase stability and directional responsiveness statistically separable?
2. Do multiple behavioral dimensions emerge?
3. Does a low-dimensional latent representation improve held-out correctness prediction?
4. Are inferred dimensions stable across model families?

Use:

    PCA / factor analysis where appropriate
    clustering
    correlation analysis
    simple latent-variable models

Do NOT overinterpret latent components.

Output:

    latent_structure_report.md

---

## Agent Group G — Hindsight Teacher Design

Design a structured posterior attribution protocol.

Use Astra6 as teacher initially.

Teacher sees outcome.

Generate pseudo-labels only for a modest pilot subset first.

Suggested:

    100–300 items

balanced across:

    correct consensus
    wrong consensus
    disagreement
    majority-wrong cases

Teacher must output structured JSON.

Run at least:

    2 independent teacher samples

for pseudo-label stability.

Measure:

    inter-run agreement
    correlation with deterministic features
    dependence on correctness
    dependence on confidence
    persona bias

Do NOT scale until stability is demonstrated.

---

## Agent Group H — Foresight Belief Attributor

Only start if Group G passes.

Input excludes ground truth.

Compare three versions:

### H1
Structured feature predictor.

### H2
LLM prompted foresight attributor.

### H3
Distilled / fine-tuned foresight model if justified.

Evaluate against:

    actual agent correctness

not merely teacher agreement.

Teacher agreement is secondary.

---

## Agent Group I — Direction Confound Audit

This group is adversarial.

Goal:

Determine whether the new agent-level reliability model is simply another encoding of:

    natural-pair direction.

Run:

    direction-only baseline
    direction + confidence
    full behavioral model
    direction-matched subsets
    independent-evidence subsets

If full model loses its advantage after direction control:

    MODIFY the contribution claim.

Do not hide this result.

---

## Agent Group J — Cross-Family Generalization

Train / derive attribution on one model family.

Test on another where possible.

Examples:

    Qwen → Ling
    Ling → Qwen

Questions:

- Does agent-level reliability transfer?
- Does feature importance transfer?
- Does pseudo-label structure transfer?
- Does ranking performance transfer?

Aggregate transfer is sufficient for an initial positive result.

Do not require item-level latent-state identity across families.

---

## Agent Group K — Literature & Novelty Audit

Search current literature on:

- LLM belief modeling
- behavioral belief elicitation
- multi-agent reliability
- agent trust estimation
- social world models
- hindsight attribution
- pseudo-labeling latent states
- minority-agent selection
- debate judge reliability
- confidence calibration
- selective prediction
- agent routing
- theory of mind for LLM agents
- intervention-based uncertainty estimation

Explicitly compare against:

**Building Social World Models with Large Language Models**

Determine:

1. what exactly can be borrowed conceptually;
2. what would be derivative;
3. what is novel in CST-based behavioral belief attribution;
4. whether "belief attribution" terminology is already overloaded.

Output:

    novelty_landscape.md
    closest_work_table.csv

---

## Agent Group L — Reviewer / Red-Team

Assume the submission claims:

> Controlled interventions reveal which LLM agents should be trusted.

Attack this claim.

Try to show:

- pseudo-label circularity
- answer leakage
- label leakage
- persona leakage
- benchmark artifacts
- natural-pair direction confounding
- judge bias
- insufficient disagreement cases
- unreliable "belief" semantics
- triviality relative to confidence
- failure under cross-family transfer

Produce:

    reviewer_attack.md

and rank concerns by severity.

---

# 10. Stage Gates

## Gate 1 — Signal Exists

Proceed only if agent-level trajectory features show a meaningful increment over strong baselines.

Desired evidence:

    ΔAUROC > 0

with bootstrap CI preferably excluding zero on at least one major dataset/model family.

More importantly:

    improved selective/ranking behavior.

If not:

    DROP or radically reformulate.

---

## Gate 2 — Ranking Works

Proceed to "which agent should be trusted" claims only if the model can rank correct vs incorrect agents within mixed-correctness panels.

Consensus-level AUROC is insufficient.

---

## Gate 3 — Minority Recovery

Strong result if:

    reliability weighting > majority vote

on majority-wrong disagreement cases,

without materially degrading overall accuracy.

If this fails, retain agent reliability as analysis only.

---

## Gate 4 — Pseudo-Labels Add Value

The hindsight teacher must add useful structure beyond deterministic correctness labels.

If:

    teacher reliability ≈ function(original correctness)

then DROP the social-world-model-style pseudo-labeling component.

Use direct supervision instead.

---

## Gate 5 — Foresight Works

The pre-outcome model must predict actual correctness/reliability.

High teacher-student agreement alone is NOT sufficient.

---

# 11. Evaluation Hierarchy

Prioritize:

### Level 1 — Agent correctness prediction

    AUROC
    AUPRC
    Brier
    ECE

### Level 2 — Within-panel ranking

    pairwise ranking
    MRR
    top-1 correct agent

### Level 3 — Decision utility

    majority-wrong recovery
    reliability-weighted accuracy
    selective risk

### Level 4 — Transfer

    cross-model-family
    cross-dataset

### Level 5 — Interpretability

    latent belief attribution
    behavioral dimensions

Do NOT lead with interpretability if Levels 1–3 fail.

---

# 12. Required Baselines

At minimum:

    Majority vote
    Vote entropy
    Consensus strength
    Answer prior
    Persona prior
    Self-reported confidence
    Confidence-weighted voting
    Paraphrase stability only
    Natural response only
    Direction-only
    Existing CST score
    Agent-level trajectory model

If computationally feasible:

    semantic consistency
    self-consistency
    judge-based reliability without interventions

The last baseline is particularly important:

> Does an LLM judge already identify the trustworthy agent from the original responses alone?

If yes, CST must demonstrate incremental value.

---

# 13. Statistical Protocol

Use item-grouped splits.

Never place agents from the same item in both train and test.

Use:

    bootstrap by item

not by individual agent row.

Report:

    point estimate
    95% CI

For model comparisons:

    paired bootstrap differences.

Pre-register primary metrics before expensive LLM experiments.

Do not repeatedly optimize thresholds on test.

---

# 14. Leakage Rules

At inference time, prohibited features include:

    ground truth
    correctness indicator
    gold-derived outcome metadata
    hindsight teacher explanation
    future intervention outcomes not available under the declared protocol

Maintain explicit feature manifests:

    PRE_OUTCOME_ALLOWED
    TRAIN_ONLY
    EVALUATION_ONLY

Every experiment must pass a leakage audit.

---

# 15. Recommended Initial Pilot

Before spending substantial Astra6 calls:

### Pilot P1

Use existing data only.

No new LLM calls.

Build:

    agent-level trajectory dataset

and test:

    confidence
    natural response
    paraphrase response
    direction
    full trajectory

against:

    agent correctness.

---

### Pilot P2

Evaluate within-panel ranking.

Subset:

    at least one correct
    at least one incorrect agent.

Question:

> Can CST behavior identify the correct agent?

---

### Pilot P3

Evaluate majority-wrong disagreement cases.

Question:

> Can CST-derived reliability recover the correct minority?

---

Only if P1–P3 are promising:

### Pilot P4

Spend Astra6 calls on hindsight belief attribution.

---

# 16. Potential Main Method If Successful

A future method section could be:

## Behavioral Belief Attribution

For agent a on item i:

    T_{i,a} =
    [f_para,
     f_nat,
     f_agree,
     f_contra,
     confidence,
     response consistency,
     ...]

Infer:

    r_hat_{i,a}
        =
    g_theta(T_{i,a}, Q_i, E_i)

Then aggregate:

    score_i(y)
        =
    Σ_a r_hat_{i,a} · 1[y_hat_{i,a}=y]

and:

    y_hat_i
        =
    argmax_y score_i(y)

Consensus risk can additionally be derived from:

    R_i =
    h(r_hat_{i,1}, ..., r_hat_{i,A},
      original votes)

This yields two outputs:

    consensus reliability
    agent reliability

from the same behavioral probing framework.

---

# 17. Desired Scientific Story

The strongest possible story is NOT:

> We added another LLM to CST.

It is:

> A discrete agent answer reveals little about the strength and reliability of the underlying decision. Controlled evidence interventions expose a behavioral trajectory. We show that these trajectories contain agent-specific reliability information, allowing a pre-outcome model to identify trustworthy agents and, in disagreement cases, sometimes recover correct minority judgments.

Conceptual progression:

    Answer
      ↓
    Consensus
      ↓
    Stress Response
      ↓
    Behavioral Trajectory
      ↓
    Agent Reliability
      ↓
    Trustworthy Aggregation

---

# 18. Claims That Require Strong Evidence

Do NOT claim:

    "We recover agents' true beliefs."

Prefer:

    "We infer behaviorally grounded latent reliability states."

Do NOT claim:

    "The most trustworthy agent is identified"

unless within-panel ranking is validated against actual outcomes.

Do NOT claim:

    "Pseudo-labels reveal ground-truth beliefs."

They are teacher-generated attribution targets.

Do NOT claim:

    "CST corrects false consensus"

unless downstream aggregation actually improves decisions.

Do NOT claim:

    "Agent reliability is persistent"

unless cross-item identity effects are demonstrated.

---

# 19. Success Criteria for NAACL-Main-Level Extension

Strong outcome:

1. Agent-level CST trajectories significantly predict correctness beyond confidence and answer priors.
2. The model ranks correct agents within mixed panels.
3. It identifies correct minority agents substantially better than conventional aggregation.
4. Results replicate across at least two model families.
5. Direction-only baselines do not fully explain the gain.
6. Hindsight-to-foresight attribution adds value or is honestly dropped.
7. The final method remains pre-outcome at deployment.
8. Negative mechanism findings are reported transparently.

Exceptional outcome:

    behavioral stress testing identifies a correct minority
    even when majority agreement and confidence favor the wrong answer.

This would substantially strengthen the paper.

---

# 20. Failure Outcomes Are Valuable

Possible outcomes:

### Outcome A — Full success

Behavioral trajectories support agent reliability inference and trustworthy aggregation.

→ Integrate as major paper contribution.

### Outcome B — Agent correctness works, belief modeling does not

Simple behavioral features predict agent correctness, but latent pseudo-labels add no value.

→ DROP belief-model complexity.
→ Keep agent-level CST reliability.

### Outcome C — Direction explains everything

Agent-level prediction collapses after controlling natural-pair direction.

→ Do not claim latent reliability.
→ Use result to sharpen CST mechanism interpretation.

### Outcome D — No agent-level signal

Consensus-level CST works but individual attribution does not.

→ Keep original paper.
→ Report internally as a falsified extension.

All four outcomes are scientifically acceptable.

---

# 21. Final Astra6 Synthesis Task

After all parallel agents finish, assign one independent Astra6 synthesis agent.

It must NOT merely summarize reports.

It must adjudicate:

1. Is there genuine agent-level information?
2. Does it survive confidence and direction controls?
3. Can correct agents be ranked within panels?
4. Can correct minority agents be recovered?
5. Does hindsight pseudo-labeling add information?
6. Is "belief attribution" scientifically justified?
7. Does this materially strengthen the NAACL paper?
8. Which components should be kept, modified, or dropped?

Final verdict must be exactly one of:

    INTEGRATE
    INTEGRATE-LIGHT
    KEEP-AS-SECONDARY
    DROP

Required final files:

    autoresearch_belief/FINAL_SYNTHESIS.md
    autoresearch_belief/FINAL_DECISION.md
    autoresearch_belief/PAPER_SAFE_CLAIMS.md
    autoresearch_belief/PAPER_UNSAFE_CLAIMS.md
    autoresearch_belief/NEXT_EXPERIMENTS.md

---

# 22. Execution Priority

Run in this order:

PARALLEL WAVE 1:
    A Data Archaeology
    K Literature Audit
    L Reviewer Red-Team

PARALLEL WAVE 2:
    B Dataset Builder
    C Predictability
    D Ranking
    E Minority Recovery
    F Latent Structure
    I Direction Audit

GATE REVIEW

If positive:

PARALLEL WAVE 3:
    G Hindsight Teacher
    J Cross-Family Generalization

Then:

    H Foresight Attributor

Finally:

    Independent Synthesis Agent

Do not spend substantial LLM budget before Wave 2 establishes that the agent-level behavioral signal exists.

---

# 23. One-Sentence North Star

> Can we use how an agent changes its mind under controlled evidence stress to infer whether that agent—not merely the consensus—should be trusted before the outcome is known?
