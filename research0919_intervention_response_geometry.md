# AutoResearch 0919 --- Intervention Response Geometry

## Discovering Reliability Structure Without Latent-State or Hindsight-Credit Compression

**Project:** `when-consensus-lies`\
**Recommended workspace:**
`consensus_stress/autoresearch_response_geometry/`\
**Research mode:** falsification-driven autoresearch\
**LLM research assistant:** private `gpt-6-astra` only when LLM calls
are required\
**Starting scientific state:** B6 survives; B8 and hindsight-credit
increment fail\
**DEV:** LOCKED at start\
**Prospective:** 807 dates SEALED at start\
**Primary objective:** determine whether reliability information resides
in relational geometry among controlled intervention responses rather
than in a compressed latent state or hindsight pseudo-label.

------------------------------------------------------------------------

# 0. Motivation

The current evidence establishes three distinct facts.

### A. Raw behavioral trajectory contains predictive signal

On the bounded S&P500 pilot:

\[ AUROC(B6)=0.6320. \]

B6 directly uses observable intervention-response trajectories.

### B. Learned low-dimensional behavioral state did not improve on B6

\[ AUROC(B8)=0.6177, \]

\[ `\Delta `{=tex}AUROC(B8-B6)=-0.0143, \]

with 95% CI:

\[ \[-0.0560,+0.0287\]. \]

Verdict:

> `KEEP_B6_NO_ESCALATION`

### C. Hindsight credit can be stable and partially distillable, yet still be useless beyond B6

Astra6 hindsight credit independently replicated strongly:

-   pairwise Spearman: 0.7576;
-   top-credit agreement: 0.8700;
-   entropy: 0.7638.

Two components were pre-outcome-distillable:

\[ q\_{para}: `\rho=0.3699`{=tex} \]

\[ q\_{removal}: `\rho=0.3882`{=tex}. \]

But G2-E found no incremental reliability value beyond B6:

-   M1: +0.0000228 AUROC;
-   M2: -0.0000076;
-   M3: -0.0000913;
-   M4: -0.0002968.

Shuffle control:

\[ `\Delta `{=tex}AUROC=+0.0001674, \]

larger than every candidate.

Verdict:

> `DISTILLABLE_NOT_USEFUL`

Therefore the next research question must **not** be "how can we rescue
pseudo-label distillation?"

Instead:

\[ `\boxed{
\text{Does reliability reside in structured relations among intervention responses themselves?}
}`{=tex} \]

------------------------------------------------------------------------

# 1. Central Hypothesis

Let an agent's observable intervention trajectory be:

\[ T_a= {R_a(I_0),R_a(I_1),...,R_a(I_K)}. \]

Previous attempts assumed useful compression:

\[ T_a`\rightarrow `{=tex}z_a`\rightarrow `{=tex}C_a \]

or:

\[ T_a`\rightarrow `{=tex}`\hat `{=tex}q_a`\rightarrow `{=tex}C_a. \]

Both failed to improve B6.

The new hypothesis is:

\[ `\boxed{
C_a=f(\mathcal G(T_a))
}`{=tex} \]

where (`\mathcal `{=tex}G(T_a)) is the **relational geometry** of
intervention responses: pairwise transitions, directional derivatives,
asymmetries, curvature, agent-relative position, and panel-relative
response structure.

The hypothesis is explicitly **not** that (`\mathcal `{=tex}G) recovers
an internal belief.

It is an observable behavioral reliability signature.

------------------------------------------------------------------------

# 2. Scientific Question

Test:

> Are there reproducible intervention-response relations that predict
> agent correctness beyond the existing B6 raw-trajectory baseline and
> survive direction, confidence, market-state, agent-ID, and generic
> nonlinear-feature controls?

The strongest useful result is:

\[ `\boxed{
B6+\mathcal G(T)>B6
}`{=tex} \]

on frozen TRAIN-CV, followed by one-time DEV and eventually untouched
prospective replication.

------------------------------------------------------------------------

# 3. Non-Negotiable Boundaries

Do not:

-   revive B8 as the main hypothesis;
-   revive Astra hindsight pseudo-labels as the main hypothesis;
-   call the representation latent belief;
-   claim causal cognition;
-   optimize market alpha/PnL;
-   inspect prospective outcomes during method discovery;
-   repeatedly tune against DEV;
-   choose hard subsets using realized correctness;
-   search arbitrary high-capacity architectures until one wins;
-   silently exclude failures;
-   overwrite previous negative results.

Previous failures are part of the evidence and must remain visible.

------------------------------------------------------------------------

# 4. Research Strategy

Use four populations:

1.  **Explorers** --- independently propose structural hypotheses.
2.  **Builders** --- implement the smallest falsifiable version.
3.  **Critics** --- attempt to explain results with simpler controls.
4.  **Synthesizers** --- identify surviving mechanisms across proposals.

The process should search over **scientific structures**, not classifier
brands.

Maximum four research generations.

------------------------------------------------------------------------

# 5. Generation 0 --- Freeze Existing Data and Baselines

Before new search:

1.  hash all existing TRAIN/DEV manifests;
2.  freeze B6 implementation and predictions;
3.  freeze B7 direction-only baseline;
4.  freeze market-only/confidence-only/agent-ID baselines;
5.  record all previous B8 and hindsight-credit results;
6.  verify prospective pool remains untouched;
7.  create a new experiment ledger.

Create:

``` text
00_freeze/
  DATA_MANIFEST.json
  BASELINE_MANIFEST.json
  PRIOR_RESULTS.md
  PROTOCOL_HASH.json
```

------------------------------------------------------------------------

# 6. Representation of a Response

For each date (t), agent (a), intervention (k), retain observable fields
such as:

\[ R\_{t,a,k}= (d\_{t,a,k},p\_{t,a,k},c\_{t,a,k}) \]

where:

-   (d): UP/DOWN decision;
-   (p): probability of UP;
-   (c): confidence.

Use only fields already authorized by the frozen response schema.

No future outcome enters feature construction.

------------------------------------------------------------------------

# 7. Geometry Family G1 --- Intervention Derivatives

Define changes relative to original response:

\[ `\Delta `{=tex}p_k=p_k-p_0 \]

\[ `\Delta `{=tex}c_k=c_k-c_0 \]

and discrete decision flips:

\[ F_k=`\mathbb 1`{=tex}\[d_k`\neq `{=tex}d_0\]. \]

Candidate relations include:

-   paraphrase sensitivity;
-   removal sensitivity;
-   agree sensitivity;
-   contradict sensitivity;
-   signed versus absolute changes.

These are primitive geometry, not yet a new method.

------------------------------------------------------------------------

# 8. Geometry Family G2 --- Directional Asymmetry

Test relations such as:

\[ A\_{AC}=`\Delta `{=tex}p\_{agree}-`\Delta `{=tex}p\_{contradict} \]

or sign-aware versions aligned to the original decision.

Question:

> Does a reliable agent respond differently to supporting versus
> opposing interventions in a reproducible way?

Control carefully for direction-only information.

------------------------------------------------------------------------

# 9. Geometry Family G3 --- Behavioral Curvature

Treat intervention responses as finite perturbations around the original
state.

Construct second-order quantities such as:

\[ K\_{P,R}=`\Delta `{=tex}p\_{remove}-`\Delta `{=tex}p\_{para} \]

\[ K\_{A,C}=`\Delta `{=tex}p\_{contradict}-`\Delta `{=tex}p\_{agree}. \]

Also test normalized versions:

\[ `\tilde `{=tex}K=`\frac{K}{\epsilon+\sum_k|\Delta p_k|}`{=tex}. \]

Interpretation must remain descriptive:

> nonlinear response structure across interventions.

Do not call it Hessian/internal curvature unless mathematically
justified.

------------------------------------------------------------------------

# 10. Geometry Family G4 --- Pairwise Response Distances

For interventions (i,j):

\[ D\_{ij}=\|\|R(I_i)-R(I_j)\|\|. \]

Use small, interpretable distance functions over
direction/probability/confidence.

Examples:

-   original ↔ paraphrase;
-   original ↔ removal;
-   agree ↔ contradict;
-   paraphrase ↔ removal.

Test whether the **pattern of distances**, rather than a compressed
scalar, carries reliability information.

------------------------------------------------------------------------

# 11. Geometry Family G5 --- Transition Motifs

Discretize only with TRAIN-frozen thresholds.

Examples:

``` text
stable → stable
stable → flip
high-confidence → low-confidence
agree-stable / contradict-responsive
paraphrase-stable / removal-sensitive
globally-rigid
globally-volatile
```

A motif must be defined pre-outcome.

Do not name motifs "good/bad agent" before testing correctness
association.

Test motif frequencies and correctness conditional on market/agent
controls.

------------------------------------------------------------------------

# 12. Geometry Family G6 --- Panel-Relative Geometry

Reliability may depend on how an agent responds relative to peers.

For each feature (g\_{t,a}), construct:

\[ g\^{rel}*{t,a} = g*{t,a} - median\_{b`\neq `{=tex}a}(g\_{t,b}). \]

Also test:

-   rank within panel;
-   deviation from panel median;
-   disagreement with panel response direction;
-   intervention-specific uniqueness;
-   response convergence/divergence after intervention.

This is especially important for minority recovery.

------------------------------------------------------------------------

# 13. Geometry Family G7 --- Cross-Agent Coupling

For each intervention, define panel response dispersion:

\[ V_k=Var_a(p\_{a,k}) \]

and pairwise convergence:

\[ C_k= `\frac{1}{|E|}`{=tex} `\sum`{=tex}*{a\<b} \|p*{a,k}-p\_{b,k}\|.
\]

Then examine changes:

\[ `\Delta `{=tex}V_k=V_k-V_0. \]

Question:

> Does an intervention expose whether consensus is robust, brittle, or
> supported by heterogeneous agent responses?

This connects agent-level geometry back to consensus-level CST.

------------------------------------------------------------------------

# 14. Geometry Family G8 --- Minimal Response Graph

A response graph is permitted only as a compact mathematical
representation.

Nodes:

\[ I_0,I\_{para},I\_{remove},I\_{agree},I\_{contradict}. \]

Node attributes: - direction; - probability; - confidence.

Edges encode observed transition differences.

Do **not** immediately use a GNN.

First test explicit graph statistics:

-   edge magnitudes;
-   signed edge asymmetry;
-   path differences;
-   triangle consistency;
-   cycle inconsistency;
-   node sensitivity.

The previous Graph-CST failure concerned citation/support graph
degeneracy and does not validate this graph automatically.

------------------------------------------------------------------------

# 15. Explorer Wave

Launch 16 independent Astra6 Explorers.

Each receives:

-   frozen B6/B8 results;
-   G2-D positive distillability;
-   G2-E `DISTILLABLE_NOT_USEFUL`;
-   prior direction-dominant CST mechanism;
-   prohibition on latent-belief framing;
-   prospective/DEV lock status.

Prompt:

> Propose exactly one falsifiable structural hypothesis explaining why
> the raw intervention-response trajectory predicts reliability while
> both low-dimensional behavioral-state compression and hindsight-credit
> distillation fail to improve it. The proposal must exploit relations
> among intervention responses rather than merely changing the
> classifier. Give a mathematical feature/structure, a mechanism-level
> intuition, the cheapest TRAIN-only falsification, required controls,
> and an explicit kill condition. It must be testable without future
> outcomes at inference.

Explorers do not initially see one another.

------------------------------------------------------------------------

# 16. Proposal Taxonomy

Cluster Explorer proposals by mechanism, not wording.

Expected clusters:

-   directional asymmetry;
-   perturbation curvature;
-   intervention pair geometry;
-   response motifs;
-   panel-relative reliability;
-   cross-agent coupling;
-   graph consistency;
-   hard-case conditional geometry.

Retain diversity.

Do not choose 12 variants of the same idea.

------------------------------------------------------------------------

# 17. Generation-1 Candidate Budget

Advance at most 8 structurally distinct hypotheses.

Each Builder must implement the **smallest interpretable version**.

Allowed initial predictive heads:

-   regularized logistic regression;
-   shallow tree/GBDT;
-   simple GAM if available.

Do not begin with neural networks.

------------------------------------------------------------------------

# 18. Baseline Hierarchy

Every candidate must compare against:

### B0

Constant / prevalence.

### B-market

Frozen market-only features.

### B-conf

Original confidence/probability.

### B-agent

Agent identity.

### B7

Direction-only.

### B6

Frozen raw trajectory baseline.

### B6 + random nonlinear summary

Matched-dimensional random projection/control.

### B6 + candidate geometry

Primary test.

The scientific question is the final comparison.

------------------------------------------------------------------------

# 19. Incremental Formulation

Prefer residualization over B6:

\[ logit(r\^{new}) = logit(r\^{B6}) +
`\delta`{=tex}\_`\theta`{=tex}(`\mathcal `{=tex}G(T)). \]

This directly tests:

\[ I(`\mathcal `{=tex}G(T);C`\mid `{=tex}B6) \]

operationally through out-of-fold incremental predictive value.

Do not claim formal conditional mutual information unless estimated
separately.

------------------------------------------------------------------------

# 20. TRAIN-Only Search

All method discovery occurs using TRAIN only.

Use date-grouped temporal folds.

Because the target is next-10-day movement, account for overlapping
labels with purging/embargo or equivalent temporal separation.

All preprocessing, motif thresholds, scaling, feature selection, and
model fitting occur within the training side of each fold.

------------------------------------------------------------------------

# 21. Primary Metrics

For correctness prediction:

-   AUROC;
-   AUPRC;
-   Brier;
-   ECE.

Primary incremental endpoint:

\[ `\Delta `{=tex}AUROC= AUROC(B6+`\mathcal `{=tex}G)-AUROC(B6). \]

Also require calibration not to materially deteriorate.

Use paired date-level bootstrap.

Use block bootstrap/non-overlapping robustness.

------------------------------------------------------------------------

# 22. Ranking and Panel Metrics

Secondary metrics:

-   within-panel ranking;
-   top-1 trusted-agent correctness;
-   majority-wrong minority recovery;
-   wrong-consensus identification;
-   selective Risk@80 if well-defined.

These are especially relevant if full-set AUROC gain is modest but panel
decision utility is meaningful.

Do not promote a secondary metric to primary after seeing results.

------------------------------------------------------------------------

# 23. Hard-Case Analysis

Define hard cases before seeing correctness.

Allowed definitions include:

-   B6 near 0.5;
-   small B6 within-panel margin;
-   high intervention dispersion;
-   high original confidence with large response instability;
-   panel disagreement.

Hard-case analysis is diagnostic.

A method cannot advance solely because of a post-hoc hard-case win.

------------------------------------------------------------------------

# 24. Mandatory Controls

Every candidate faces:

1.  direction-only;
2.  market-only;
3.  confidence-only;
4.  agent-ID-only;
5.  shuffled geometry;
6.  random matched-dimensional geometry;
7.  feature permutation;
8.  label permutation;
9.  fold sensitivity;
10. temporal-block robustness.

For panel-relative candidates additionally:

11. shuffled agent identities within date;
12. shuffled peer assignment where meaningful.

------------------------------------------------------------------------

# 25. Incremental Gate

A candidate may advance only if:

-   TRAIN-CV (`\Delta `{=tex}AUROC\>0);
-   effect sign is reasonably stable across folds;
-   paired bootstrap supports the direction;
-   calibration does not materially worsen;
-   direction-only does not reproduce;
-   matched random geometry does not reproduce;
-   shuffled geometry does not reproduce;
-   no single agent dominates;
-   no leakage/audit failure.

Preferred strong gate:

\[ 95%CI(`\Delta `{=tex}AUROC)\>0. \]

Candidates with positive point estimate but uncertain CI may be marked
`ANOMALY`, not `PASS`.

------------------------------------------------------------------------

# 26. Cross-Pollination

After Generation 1, allow Astra6 Synthesizers to combine at most
**three** surviving mechanisms.

Examples:

\[ `\text{directional asymmetry}`{=tex} +
`\text{panel-relative position}`{=tex} \]

or:

\[ `\text{curvature}`{=tex} + `\text{motif}`{=tex} \]

Do not combine failed mechanisms.

Do not build a kitchen-sink feature set.

Every combined candidate must have an ablation showing each parent
contributes.

------------------------------------------------------------------------

# 27. Generation 2 --- Structural Competition

At most 5 candidates enter Generation 2.

Require:

-   frozen feature definitions;
-   frozen model family;
-   nested ablations;
-   matched complexity controls;
-   TRAIN-only temporal CV.

Ask:

> Which structural relation survives when simpler explanations are
> removed?

------------------------------------------------------------------------

# 28. Astra6 Debate

For every Generation-2 survivor use fresh contexts:

### Advocate

Explain why the geometry captures a meaningful reliability relation.

### Skeptic

Try to reduce it to direction, confidence, market regime, agent
identity, or generic nonlinearity.

### Methodologist

Audit temporal leakage, overlapping labels, preprocessing, feature
selection, multiple testing, and bootstrap.

### Reviewer

Assess whether the result is a genuine reliability-method contribution.

### Adjudicator

Return:

``` json
{
  "decision": "ADVANCE|TARGETED_ABLATION|KILL",
  "mechanism": "...",
  "strongest_alternative": "...",
  "increment_beyond_B6": "...",
  "control_status": "...",
  "remaining_risk": "...",
  "dev_unlock": false
}
```

------------------------------------------------------------------------

# 29. Multiple-Testing Discipline

Maintain:

``` text
EXPERIMENT_LEDGER.jsonl
```

for every hypothesis.

Log:

-   hypothesis ID;
-   generation;
-   parent mechanisms;
-   exact feature definition;
-   model;
-   hyperparameters;
-   folds;
-   seed;
-   metrics;
-   CIs;
-   controls;
-   verdict.

Report the total number of tested hypotheses in final synthesis.

Do not report only winners.

------------------------------------------------------------------------

# 30. DEV Unlock

DEV may unlock only after one or at most two finalists satisfy all
frozen TRAIN gates and survive debate.

Before access freeze:

-   exact geometry;
-   preprocessing;
-   model;
-   hyperparameters;
-   seed policy;
-   metrics;
-   bootstrap;
-   panel metrics;
-   hard-case definitions;
-   failure criteria;
-   code commit;
-   protocol hash.

Create:

``` text
DEV_UNLOCK_CERTIFICATE.json
```

No tuning after DEV.

------------------------------------------------------------------------

# 31. One-Time DEV

Evaluate frozen finalist(s) once.

Primary:

\[ `\Delta `{=tex}AUROC\_{geometry-B6}. \]

Also report:

-   AUPRC;
-   Brier;
-   ECE;
-   paired date bootstrap;
-   block bootstrap;
-   non-overlapping robustness;
-   panel ranking;
-   minority recovery.

Possible verdicts:

-   `DEV_GEOMETRY_INCREMENT`
-   `DEV_PARTIAL_ANOMALY`
-   `DEV_NO_INCREMENT`

If no increment, do not tune on DEV.

------------------------------------------------------------------------

# 32. Prospective Protection

The 807 untouched prospective dates are the final confirmatory asset.

Do not touch them during geometry discovery.

Prospective may unlock only after a successful frozen DEV finalist and a
new prospective preregistration.

Freeze one primary method.

No broad finalist tournament on prospective.

------------------------------------------------------------------------

# 33. Prospective Preregistration

Create:

``` text
PROSPECTIVE_PREREGISTRATION.md
PROSPECTIVE_UNLOCK_CERTIFICATE.json
```

Freeze:

-   one geometry method;
-   frozen B6 baseline;
-   temporal range;
-   all feature definitions;
-   all parameters;
-   primary/secondary metrics;
-   block-bootstrap method;
-   panel analysis;
-   failure criteria;
-   code commit/hash.

A fresh Astra6 Skeptic + Methodologist must approve before outcome
access.

------------------------------------------------------------------------

# 34. Prospective Success

Strong confirmation requires:

\[ `\boxed{
B6+\mathcal G(T)>B6
}`{=tex} \]

on untouched prospective dates with:

-   positive paired AUROC delta;
-   calibration not materially worse;
-   temporal-dependence robustness;
-   direction/random/shuffle controls unable to explain;
-   no leakage;
-   consistent structural interpretation.

Only then may the final project use a strong geometry contribution
claim.

------------------------------------------------------------------------

# 35. Cross-Domain Validation

If and only if a compact geometry mechanism survives S&P500 prospective
confirmation, test whether the **same frozen structural principle**
transfers to existing BoolQ/VitaminC agent trajectories where
compatible.

Do not redesign it separately per dataset.

The valuable question is:

\[ `\boxed{
\text{Is the same intervention-response relation predictive across domains?}
}`{=tex} \]

Cross-domain transfer would substantially strengthen the paper.

------------------------------------------------------------------------

# 36. Connection to Consensus CST

If a geometry mechanism survives, test whether it explains or
complements consensus-level CST.

Possible hierarchy:

\[ `\text{agent response geometry}`{=tex} `\rightarrow`{=tex}
`\text{agent reliability}`{=tex} `\rightarrow`{=tex}
`\text{panel reliability}`{=tex} `\rightarrow`{=tex}
`\text{consensus stress score}`{=tex}. \]

Do not assume this hierarchy is true.

Test whether agent-level geometry adds to existing consensus CST score.

------------------------------------------------------------------------

# 37. Potential Paper Contribution if Successful

A successful result could support:

> Controlled interventions reveal reliability through structured
> behavioral response relations. These relations can provide information
> beyond raw confidence and direction, without requiring recovery of
> latent beliefs or outcome-conditioned pseudo-labels.

A stronger cross-domain result could support:

> Reliability is expressed in intervention-response geometry: observable
> relations among an agent's responses to controlled evidence
> perturbations provide a reusable behavioral signature of decision
> reliability.

Only use these after the corresponding evidence exists.

------------------------------------------------------------------------

# 38. Negative Result if Geometry Fails

If no geometry candidate improves B6 after controls, conclude:

> The current bounded pilot supports predictive value in the raw
> intervention trajectory but does not identify a stable
> lower-dimensional or relational summary with incremental value beyond
> that trajectory.

This is a legitimate boundary.

Do not continue unlimited feature search.

------------------------------------------------------------------------

# 39. Stopping Rules

Stop the research line if:

-   no Generation-1 geometry family produces a credible TRAIN anomaly;
-   all Generation-2 survivors are explained by B6/random/direction
    controls;
-   DEV fails after a frozen finalist;
-   prospective fails.

At each failure, preserve artifacts and write the exact failed arrow.

------------------------------------------------------------------------

# 40. Required Directory

``` text
consensus_stress/autoresearch_response_geometry/
├── 00_freeze/
├── 01_explorers/
├── 02_generation1/
├── 03_controls/
├── 04_crosspollination/
├── 05_generation2/
├── 06_debate/
├── 07_dev/
├── 08_prospective/
├── 09_crossdomain/
└── 10_synthesis/
```

------------------------------------------------------------------------

# 41. Required Final Artifacts

At minimum:

``` text
RUN_STATUS.json
EXPERIMENT_LEDGER.jsonl
EXPLORER_HYPOTHESES.md
GEOMETRY_CANDIDATES.md
TRAIN_RESULTS.md
CONTROL_RESULTS.md
TEMPORAL_ROBUSTNESS.md
DEBATE_SYNTHESIS.md
DEV_RESULTS.md              # only if unlocked
PROSPECTIVE_RESULTS.md      # only if unlocked
CROSSDOMAIN_RESULTS.md      # only if authorized
PAPER_SAFE_CLAIMS.md
PAPER_UNSAFE_CLAIMS.md
FINAL_DECISION.md
NEXT_EXPERIMENTS.md
```

------------------------------------------------------------------------

# 42. Final Verdict Taxonomy

Return one:

-   `NO_GEOMETRY_SIGNAL`
-   `GEOMETRY_REDUNDANT_WITH_B6`
-   `TRAIN_GEOMETRY_INCREMENT`
-   `DEV_GEOMETRY_INCREMENT`
-   `PROSPECTIVE_GEOMETRY_CONFIRMED`
-   `CROSSDOMAIN_GEOMETRY_SUPPORTED`
-   `PARTIAL_ANOMALY`
-   `AUDIT_FAIL`

Do not use `DISCOVERED` merely for TRAIN/DEV evidence.

------------------------------------------------------------------------

# 43. First Execution Batch

Execute now only through the first structural tournament:

1.  freeze and hash prior state;
2.  verify prospective remains untouched;
3.  launch 16 independent Astra6 Explorers;
4.  cluster proposals by mechanism;
5.  select \<=8 structurally distinct hypotheses;
6.  implement minimal interpretable versions;
7.  run TRAIN-only temporal CV;
8.  compare each to B6 plus all mandatory controls;
9.  run paired date bootstrap;
10. run block/non-overlap robustness for promising candidates;
11. convene Astra6 Advocate/Skeptic/Methodologist on survivors;
12. write an interim synthesis.

Do **not** unlock DEV in the same execution batch unless the full frozen
TRAIN gate, audits, and adjudication have completed and a formal
`DEV_UNLOCK_CERTIFICATE.json` is produced.

------------------------------------------------------------------------

# 44. Explorer Prompt

Use this exact scientific framing:

> We have a multi-agent reliability dataset with controlled intervention
> responses. The raw response trajectory B6 predicts correctness, but a
> learned low-dimensional behavioral state B8 failed to improve B6.
> Separately, an outcome-conditioned Astra6 teacher produced stable
> hindsight intervention credits, and paraphrase/removal credits were
> pre-outcome-distillable, but adding their predicted values produced
> essentially zero increment beyond B6 and failed shuffle controls.
> Therefore do not propose latent-belief recovery, hindsight
> pseudo-label rescue, or merely a new classifier. Propose exactly one
> falsifiable hypothesis in which reliability is expressed through a
> structural relation among observable intervention responses. Define
> the relation mathematically, explain why B6 may contain it while prior
> compression loses it, specify the cheapest TRAIN-only test, identify
> direction/confidence/market/agent-ID/random-feature controls, and
> state a clear kill condition.

------------------------------------------------------------------------

# 45. Final Research Principle

The project should now test a different ontology of reliability.

Not:

\[ `\text{agent has hidden scalar trustworthiness}`{=tex}. \]

Not:

\[ `\text{teacher reveals a hidden belief}`{=tex}. \]

Instead:

\[ `\boxed{
\text{reliability may be a property of how behavior changes under controlled perturbations}
}`{=tex} \]

The intervention trajectory is the observable object.

The scientific task is to determine whether its **relations**---not an
invented latent state---form a reproducible reliability signature.

If they do, demonstrate this incrementally, prospectively, and across
domains.

If they do not, preserve that result and stop.
