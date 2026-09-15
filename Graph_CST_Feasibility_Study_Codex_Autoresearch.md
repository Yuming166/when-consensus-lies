# Graph-CST Feasibility Study — Codex Autoresearch Instruction

## 0. Mission

We currently have a strong but deliberately simple consensus stress-testing protocol (CST) for identifying unreliable multi-agent LLM consensus before outcome labels are used.

The next research question is:

> Can an explicit Evidence–Belief–Agent–Consensus graph reveal structural properties of consensus that are not captured by ordinary agreement strength and CST stress-response features, while remaining transferable across models and datasets?

This is a **feasibility study**, not a request to immediately build a GNN or a large learned system.

The goal is to determine whether graph structure provides a genuine incremental scientific signal.

The final decision must be one of:

- **PROMOTE** — graph structure provides a robust, nontrivial, transferable increment beyond CST.
- **MODIFY** — some graph signal exists, but the current representation or belief-inference procedure needs revision.
- **DROP** — graph features are redundant with CST/consensus, unstable, non-transferable, or dependent on unreliable inferred beliefs.

Do not force a positive result.

---

# 1. Hard Research Principles

### 1.1 Frozen-data-first

Start with the existing frozen data and existing records.

Do NOT immediately make new LLM calls.

First determine what graph structure can already be constructed from:

- agent outputs,
- evidence/source records,
- consensus labels,
- existing intervention records,
- existing natural/independent/placebo probe records.

Default:

- **0 new LLM calls**
- only use existing data.

Only request new calls if a required graph component genuinely cannot be constructed from frozen data.

If new calls are necessary:

- maximum **20 items**
- maximum **250 logical calls**
- use the cheapest viable model/protocol
- do not expand the dataset merely to obtain a positive result.

---

# 2. Scientific Question

The central hypothesis is:

> Two panels can have identical answer consensus but very different underlying support structures.

For example:

Panel A:

- 5/5 agents answer YES
- all agents rely on the same evidence
- inferred beliefs are nearly identical
- the consensus graph is highly centralized/redundant.

Panel B:

- 5/5 agents answer YES
- agents rely on different evidence
- inferred beliefs form multiple independent clusters
- support is structurally distributed.

Both have identical vote agreement, but Panel B may be more reliable.

The graph representation should therefore separate:

1. **Answer agreement**
2. **Belief similarity/diversity**
3. **Evidence overlap/redundancy**
4. **Independent support**
5. **Graph centralization**
6. **Response of the graph to CST interventions**

Do not assume that these quantities predict correctness. Test them.

---

# 3. Proposed Graph

Construct a heterogeneous:

> Evidence–Belief–Agent–Consensus Graph

with four main node types.

### 3.1 Evidence nodes

Each distinct evidence/source unit becomes an evidence node:

`E_j`

Possible metadata:

- source ID
- source text
- source type
- evidence direction
- intervention condition
- semantic embedding if already available
- source reuse count.

Do not introduce outcome labels into graph construction.

---

### 3.2 Belief nodes

For each agent, infer a small set of explicit, testable propositions:

`B_{i,k}`

These should represent what the agent appears to believe, NOT a chain-of-thought reconstruction.

Examples:

- “Person X held position Y in year Z.”
- “Event A occurred before event B.”
- “Source S supports proposition P.”

Beliefs must be:

- explicit,
- short,
- falsifiable,
- behaviorally testable,
- independent of the final gold label where possible.

Do NOT ask for hidden chain-of-thought.

Do NOT treat a verbal explanation as ground-truth cognition.

The belief layer is only useful if it can later predict observable behavior.

---

### 3.3 Agent nodes

One node per agent:

`A_i`

Edges:

- Agent → Evidence
- Agent → Belief
- Agent → Consensus.

Possible edge weights:

- evidence usage
- evidence attribution
- belief confidence, if explicitly available
- answer polarity.

---

### 3.4 Consensus node

One consensus node:

`C`

Connect:

`A_i → C`

with the agent's selected answer.

The consensus node represents the final majority decision.

---

# 4. Graph Features

Implement simple interpretable graph statistics first.

Do NOT train a GNN at this stage.

The initial feature family should include:

## 4.1 Consensus features

- vote count
- consensus strength
- vote entropy
- answer margin.

These form the baseline.

---

## 4.2 Evidence overlap

For each pair of agents:

- evidence-set Jaccard similarity
- evidence cosine similarity if embeddings already exist
- shared-source count
- unique-source count.

Aggregate:

- mean pairwise overlap
- maximum overlap
- overlap variance.

---

## 4.3 Evidence redundancy

Measure:

- fraction of evidence reused by multiple agents
- number of unique evidence units
- effective number of independent sources
- source concentration / entropy
- Gini-style concentration if useful.

Potential simple measure:

`effective_support = 1 / sum_j p_j^2`

where `p_j` is the fraction of agents relying on evidence source `j`.

Do not overinterpret this as statistical independence. Call it something like:

> effective support diversity

unless true source independence is established.

---

## 4.4 Graph centralization

Measure whether consensus depends on a small number of shared nodes/edges.

Possible features:

- maximum evidence degree
- degree entropy
- degree concentration
- betweenness concentration
- fraction of all agent–evidence edges touching the top-k evidence nodes
- evidence centralization.

Hypothesis:

> high centralization may indicate correlated support rather than independent agreement.

Again, this is a hypothesis, not a conclusion.

---

# 5. Belief-Graph Features

If usable belief nodes can be obtained from frozen outputs, construct:

### 5.1 Belief similarity

Between agents:

- lexical similarity
- embedding cosine similarity
- proposition overlap.

Aggregate:

- mean belief similarity
- maximum similarity
- variance.

### 5.2 Belief diversity

Possible measures:

- number of distinct belief clusters
- entropy of belief clusters
- average inter-agent belief distance
- within-agent vs between-agent similarity.

### 5.3 Belief–answer consistency

Check whether inferred beliefs consistently support the agent's final answer.

Do NOT score correctness here.

The purpose is to measure internal structural consistency.

---

# 6. Structural Decomposition

The most important comparison is:

### Level 1 — Answer graph

Only:

- agent answers
- consensus strength
- vote entropy.

### Level 2 — Evidence graph

Add:

- evidence overlap
- evidence diversity
- evidence concentration
- effective support diversity.

### Level 3 — Belief graph

Add:

- belief similarity
- belief diversity
- belief clustering
- belief–answer consistency.

### Level 4 — Dynamic graph

Compare graph structure before and after CST interventions.

For each intervention:

`G_0 → G_k`

Measure:

- edge Jaccard
- node retention
- evidence replacement
- belief-cluster changes
- agent–evidence redistribution
- consensus changes.

The key question:

> Does a structurally fragile consensus exhibit a characteristic graph response before the final label is known?

---

# 7. Nested Predictive Test

Do NOT immediately build a complex neural predictor.

Construct:

### M0 — Consensus only

Features:

- consensus strength
- vote entropy
- vote margin.

### M1 — Conventional uncertainty

Add:

- confidence features if available
- disagreement
- semantic disagreement
- self-consistency proxies.

### M2 — Consensus + CST

Add the existing CST stress score(s), especially the strongest frozen natural-pair stress signal.

### M3 — Consensus + CST + Graph

Add:

- evidence overlap
- effective support diversity
- centralization
- belief diversity
- graph-response features.

Compare:

- AUROC
- AUPRC
- AURC
- Risk@80
- Risk@90
- ECE.

Primary metric:

> Risk@80 / AURC

because the intended use is selective risk estimation, not ordinary classification.

AUROC remains useful but must not be the only result.

---

# 8. Incremental-Value Test

The central quantity is:

`ΔAUROC = AUROC(M3) - AUROC(M2)`

Also compute:

`ΔAURC`

`ΔRisk@80`

`ΔRisk@90`

Use paired bootstrap confidence intervals.

A graph method should NOT be promoted merely because M3 has a higher point estimate.

Strong evidence requires:

- reproducible improvement,
- nontrivial effect size,
- preferably CI excluding zero,
- improvement across more than one dataset/model split,
- no dependence on outcome leakage.

---

# 9. Matched-Consensus Analysis

This analysis is especially important.

Select panels with the same consensus strength.

For example:

> compare 5/5 YES wrong panels against 5/5 YES correct panels.

Then ask:

Do graph features differ even when answer agreement is identical?

Repeat for:

- 5/5 YES
- 5/5 NO
- 4/5
- other available consensus levels.

This tests whether graph structure captures something beyond simple agreement.

If graph features do not distinguish matched-consensus panels, that is strong evidence against the graph hypothesis.

---

# 10. Cross-Model / Cross-Dataset Transfer

Do not optimize graph features only on one dataset.

At minimum evaluate:

### Dataset transfer

Train/calibrate feature combination on:

`BoolQ → VitaminC`

and if feasible:

`VitaminC → BoolQ`

### Model transfer

Evaluate:

`Qwen → Ling`

without retuning graph feature definitions.

The graph representation should remain conceptually identical.

This is critical because the project's scientific value is not just fitting one benchmark.

A feature that works only on one generator should be treated skeptically.

---

# 11. Important Anti-Leakage Rules

These are mandatory.

### Rule 1

Do not use the final gold label to construct graph features.

### Rule 2

Do not use:

- “correct”
- “wrong”
- gold answer
- post-hoc error category

 during graph construction.

### Rule 3

If evidence direction is derived from a benchmark label, mark that graph feature as:

> label-coupled diagnostic

and do NOT include it in the main pre-outcome predictor.

### Rule 4

Do not use intervention outcomes to construct the original pre-outcome graph.

Intervention-response features belong to a separate dynamic-analysis condition.

### Rule 5

If beliefs are generated using an instruction containing the gold answer, discard that belief representation from the pre-outcome analysis.

### Rule 6

Do not infer hidden chain-of-thought.

---

# 12. Belief Inference: Only If Necessary

The belief layer is potentially the most interesting part, but also the most dangerous.

Do NOT assume that extracted “beliefs” represent actual internal beliefs.

If existing agent outputs already contain enough explicit propositions, use them.

Otherwise run a tiny pilot.

Maximum:

- 20 items
- 2–5 beliefs per agent
- no hidden CoT
- no gold labels shown to the belief extractor.

Then test:

> Can inferred beliefs predict how the original agent behaves on a novel proposition?

The principle is:

> infer belief → make behavioral prediction → test prediction

NOT:

> infer belief → produce explanation → assume it is true.

---

# 13. Behavioral Validation of Beliefs

For each inferred belief:

1. Convert it into a short behavioral probe.
2. Ask the original agent a novel question testing that belief.
3. Compare predicted answer vs actual answer.

Possible metric:

`belief_behavior_accuracy`

Also compute:

- consistency across probes
- cross-context transfer
- contradiction rate.

If belief extraction cannot predict behavior substantially above trivial baselines, DROP the belief layer.

This is a hard gate.

---

# 14. Optional Dynamic Graph Analysis

If the existing CST intervention records allow it, analyze:

`G_original`

versus:

`G_paraphrase`

`G_natural_counter`

`G_independent_counter`

`G_placebo`

Possible measures:

- graph edit distance
- evidence-node replacement
- edge Jaccard
- agent clustering changes
- belief clustering changes
- centralization change
- effective support change.

Then ask:

> Is an unreliable consensus structurally less stable under controlled perturbations?

Do not assume that “more graph change” means “more unreliable.”

Test the direction empirically.

---

# 15. Minimal Statistical Models

Start with:

1. Logistic regression
2. Isotonic calibration
3. Simple monotonic combination if appropriate.

Avoid:

- GNN
- transformer over graphs
- large MLP
- end-to-end supervised graph classifier

unless simple models clearly establish a robust graph signal first.

The point of this phase is scientific attribution, not leaderboard optimization.

---

# 16. Main Scientific Tests

The study should answer these questions in order:

### Q1

Does graph structure differ between correct and wrong consensus after controlling for agreement strength?

### Q2

Does evidence independence/diversity add information beyond consensus?

### Q3

Does belief diversity add information beyond evidence structure?

### Q4

Does graph structure add information beyond CST?

### Q5

Does the graph representation transfer across models?

### Q6

Does it transfer across datasets?

### Q7

Can inferred beliefs be behaviorally validated?

If Q7 fails, the belief layer must not be used as a major paper contribution.

---

# 17. Decision Criteria

## PROMOTE

Promote graph structure if most of the following hold:

- M3 improves over M2 meaningfully.
- ΔAURC is favorable.
- Risk@80/90 improves.
- improvement is statistically credible.
- matched-consensus analysis shows structural differences.
- Qwen→Ling transfer is reasonable.
- BoolQ→VitaminC transfer is reasonable.
- graph features remain interpretable.
- belief inference, if used, passes behavioral validation.

Then consider a paper-level contribution such as:

> Consensus Independence Graphs

or

> Evidence–Belief Structure for Consensus Reliability

The graph should remain a transparent representation rather than a black-box GNN.

---

## MODIFY

Choose MODIFY if:

- evidence structure helps but belief structure does not;
- graph features help only on one dataset;
- dynamic graph response is useful but static graph structure is not;
- one graph statistic is strong but the full graph is redundant;
- belief extraction works only after a narrower proposition representation.

Then retain only the validated component.

---

## DROP

Choose DROP if:

- M3 ≈ M2;
- graph features are almost deterministic functions of consensus/CST;
- matched-consensus differences disappear;
- transfer fails badly;
- inferred beliefs do not predict behavior;
- gains depend on label-coupled features;
- results are unstable across bootstrap splits.

Do not manufacture complexity to rescue the hypothesis.

A clean negative result is valuable.

---

# 18. Suggested Directory

Write all outputs under:

`consensus_stress/graph_cst/`

Recommended structure:

```text
consensus_stress/graph_cst/
├── protocol.md
├── README.md
├── scripts/
│   ├── build_graph.py
│   ├── extract_features.py
│   ├── matched_consensus.py
│   ├── fit_nested_models.py
│   ├── transfer_eval.py
│   └── belief_validation.py
├── results/
│   ├── graph_features.jsonl
│   ├── nested_model_results.json
│   ├── matched_consensus_results.json
│   ├── transfer_results.json
│   └── belief_validation_results.json
├── figures/
│   ├── graph_structure_vs_consensus.pdf
│   ├── incremental_value.pdf
│   └── transfer.pdf
└── decision.md
```

Only create files that are actually needed.

---

# 19. Required Final Report

At the end, write:

`consensus_stress/graph_cst/decision.md`

It must contain:

## A. What was tested

Exactly which graph representation and features were evaluated.

## B. Frozen-data coverage

Number of:

- items
- agents
- evidence units
- belief propositions
- interventions.

## C. Main results

A table:

| Model | AUROC | AUPRC | AURC | Risk@80 | Risk@90 | ECE |
|---|---:|---:|---:|---:|---:|---:|
| M0 | | | | | | |
| M1 | | | | | | |
| M2 | | | | | | |
| M3 | | | | | | |

## D. Incremental value

Report:

- ΔAUROC
- ΔAURC
- ΔRisk@80
- bootstrap CIs.

## E. Matched-consensus result

Explicitly state whether graph structure separates correct/wrong panels with equal agreement.

## F. Transfer

Report:

- BoolQ→VitaminC
- VitaminC→BoolQ if feasible
- Qwen→Ling.

## G. Belief validation

If performed:

- behavioral prediction accuracy
- baseline accuracy
- consistency
- failure cases.

## H. Leakage audit

Explicitly document every feature that is:

- pre-outcome
- label-coupled
- post-outcome.

## I. Decision

Exactly one:

`PROMOTE`

`MODIFY`

`DROP`

with a concise scientific justification.

---

# 20. Interpretation Guardrails

Do NOT write:

- “graphs explain why LLMs hallucinate”
- “agents have true internal beliefs”
- “evidence independence guarantees correctness”
- “graph structure causes reliability”
- “we discovered the mechanism of false consensus”

unless the experiments genuinely establish such claims.

Prefer:

- “structural correlate”
- “behaviorally validated belief representation”
- “incremental predictive signal”
- “evidence-support topology”
- “consensus structural diversity”
- “graph-based reliability feature.”

---

# 21. Relationship to the Existing CST Paper

The graph study should be positioned as an extension of the existing CST protocol.

Current CST:

> perturb evidence → observe behavioral response → estimate consensus risk.

Graph extension:

> represent who relies on what → quantify support topology → test whether structural diversity adds risk information beyond behavioral stress response.

This is potentially more interesting than simply adding another stress-test condition.

The key scientific question is:

> Does consensus reliability depend not only on whether agents agree, but on whether their agreement is structurally independent?

If yes, this can become a meaningful second layer of the paper.

If no, keep CST simple.

---

# 22. Final Instruction to Codex

Work conservatively.

Do not chase positive results.

Do not expand the dataset unnecessarily.

Do not build a GNN before simple feature-level evidence exists.

Do not treat generated explanations as genuine beliefs.

Do not use gold labels in graph construction.

Do not modify the main paper during this study.

Do not modify frozen historical results.

Every new result must be reproducible from a script and recorded with:

- dataset/version
- model
- item IDs
- random seed
- number of calls
- validity rate
- feature definitions
- leakage status.

The final objective is NOT:

> “make the method more complicated.”

The objective is:

> determine whether graph structure captures a scientifically distinct and transferable dimension of consensus reliability beyond agreement strength and CST.

If the answer is no, stop and report DROP.
