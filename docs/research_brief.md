# Research Brief

## Reliable Multi-Agent Decisions under Distribution Shift
### Outcome-Firewalled Evidence-Response Audits, Selective Risk Transfer, and As-of Financial Replay

**Researcher:** [Your Name]

**Repository snapshot audited:** `codex/naacl-symmetric` at commit
`0195b6773e16ea35d592caf1141c1fe4d9a830e1` (September 5, 2026), extended by the
curated data/docs in this repository.

## 1. Executive summary

I study a reliability problem that appears whenever several language-model agents
agree: **when does agreement represent independent support, and when is it only
false consensus caused by shared evidence, stale evidence, or behaviorally
irrelevant citations?**

The current project does not treat the LLM as a stock-price predictor or ask it to
expose hidden chain-of-thought. Instead, the evaluation environment assigns each
agent an auditable evidence view, keeps source identities and availability times
outside the model, and applies paired `remove`, `reverse`, and `substitute`
interventions. The resulting observable response behavior is converted into a
pre-outcome risk score for an already formed consensus. The label is revealed only
after response records, risk scores, and retained/abstained items have been
frozen.

The main methodological contribution is therefore not a new intervention,
citation validator, debate algorithm, or universal truth score. It is a concrete
**consensus-error estimand plus an integrity protocol**: can observable evidence
responses rank wrong high-consensus decisions before the outcome is known, and when
does that signal remain valid under model and domain shift?

## 2. What has been completed

### A. A preregistered, environment-controlled reliability protocol

For each item, five fixed personas receive controlled evidence views:

- literal evidence user;
- skeptical auditor;
- consistency checker;
- counterfactual reasoner; and
- minimal judge.

Each agent returns only an answer, confidence, and evidence IDs. The environment
rejects invented or out-of-packet citations and records the provenance graph

```text
source root -> evidence item -> agent view -> cited evidence -> decision
```

The original consensus is selected first. Only consensus items with at least 80%
agreement enter the primary risk-ranking analysis. Labels/outcomes are kept in a
separate ledger and are inaccessible until the pre-outcome routes are frozen.
This prevents outcome leakage and separates error ranking from answer repair.

Two frozen score instantiations are kept separate:

```text
R_PI  = 0.1 * complete_intervention_inertia
      + 0.3 * answer_flip_inertia
      + 0.6 * shared_source_fraction

R_sym = 0.3 * reverse_inertia
      + 0.7 * intervention_disagreement
```

`R_PI` is the original BoolQ protocol. `R_sym` is a separately registered,
label-symmetric VitaminC protocol selected on Qwen development data and then held
fixed for both Qwen and Ling formal evaluation.

### B. Synthetic stress-testing before real LLM calls

The synthetic harness creates controlled false-consensus mechanisms including
shared corruption, stale evidence, partial corruption, and evidence inertia. It
supports hidden/aliased provenance, noisy source-quality estimates, variable agent
counts, corruption strength, and mechanism-held-out evaluation.

The fixed conditional-provenance score ranked held-out consensus errors strongly in
Synthetic V3. An independently preregistered V4 learned a monotonic router with
better calibration than several baselines, but it did not beat the fixed V3
structural prior on the main selective-risk endpoint and drifted when
evidence-inertia was completely held out. This negative result motivated retaining
explicit provenance/intervention structure rather than assuming that a learned
router will extrapolate to unseen failure mechanisms.

### C. Real-LLM confirmation on BoolQ

A provenance-disjoint Qwen3.5-4B replication (V12.1) used 358 questions and 7,160
calls. Among 300 high-consensus questions, 66 consensus decisions were wrong.
The frozen `R_PI` score achieved:

- AUROC: **0.705**, 95% CI **[0.620, 0.781]**;
- retained error at 80% coverage: **0.220 -> 0.133**;
- error reduction: **0.087**, 95% CI **[0.046, 0.098]**.

The behavioral intervention coordinates carried the useful signal; citation
sharing alone was approximately at chance. The result is a bounded confirmation of
pre-outcome error ranking on this protocol, not label-invariant reliability.

### D. Fresh label-symmetric cross-family replication

The earlier label-asymmetric experiments showed that aggregate success can hide
opposite behavior across native labels. Instead of reweighting those outcomes
post hoc, V3.16 froze a balanced natural-contrastive construction: one SUPPORTS
and one REFUTES item per VitaminC page pair. V3.16.1 then preregistered all
remaining 289 natural pairs (578 balanced items), used the identical frozen
`R_sym`, and ran 11,560 calls per model across five personas and four conditions.

Both Qwen3.5-4B and Ling-3.0-tiny passed all registered model-level gates in the
fresh cohort:

| Model | Overall AUROC | Macro-label AUROC | Worst-label AUROC | Risk@80 error reduction |
|---|---:|---:|---:|---:|
| Qwen3.5-4B | 0.839 [0.802, 0.873] | 0.840 [0.802, 0.875] | 0.807 [0.750, 0.857] | +0.057 [0.038, 0.075] |
| Ling-3.0-tiny | 0.727 [0.689, 0.764] | 0.738 [0.689, 0.784] | 0.607 [0.515, 0.692] | +0.042 [0.026, 0.055] |

The two models share 526 high-consensus items, but their item-level risk scores
have Spearman correlation only **0.294**. The correct interpretation is therefore
**aggregate behavioral-signal transfer across model families**, not universal or
item-level-stable transfer. The preceding V3.16 cohort is retained as a formal
adequacy boundary: Ling had only 17 SUPPORTS errors, below the preregistered
minimum of 20, so favorable intervals were not used to manufacture a pass.

### E. As-of S&P 500 replay and protocol-failure analysis

The project also instantiates the same reliability question in a sequential,
real-world setting. The as-of environment contains 29 standardized features from
seven provenance roots, a five-trading-day direction target, and 500 decision dates
(350 train / 150 test). Five LLM roles answer each date's question; V1 and V2 each
contain 2,500 actual model calls on the identical manifest.

The result is an important external-validity boundary:

- V1 AMIR-style routing had the best calibration in its reported table
  (risk ECE **0.055** versus **0.174** for majority), but its AURC difference was
  **-0.0874 [-0.1994, +0.0736]**, so the confirmatory routing endpoint failed.
- A preregistered prompt-only repair increased valid responses from **68.2% to
  75.6%** on the same dates and yielded a paired sign-test result of approximately
  **7 x 10^-9**.
- V2 still failed the primary AURC criterion: **+0.0317 [-0.0886, +0.1805]**.
  In V2, the router's calibration advantage also did not replicate; the router
  risk ECE was **0.184** versus **0.135** for majority.

Thus, the financial replay does not support an alpha, predictability, or routing-
superiority claim. It shows that as-of provenance, calibration, and output-contract
validity must be evaluated separately, and that a seemingly harmless abstention
policy can create fail-closed coverage bias.

## 3. What the project contributes scientifically

1. **A precise unit of analysis:** the error risk of an already formed,
   high-consensus multi-agent decision, rather than explanation quality or debate
   quality.
2. **An outcome-firewalled protocol:** evidence identities, availability, paired
   interventions, frozen risk scores, and adequacy gates are fixed before outcome
   access.
3. **A measurable transfer boundary:** the aggregate signal transfers from Qwen to
   Ling on a fresh balanced natural-pair cohort, while modest item-level
   correlation limits stronger generalization claims.
4. **A reusable negative-result discipline:** invalid outcome-contaminated metrics,
   failed gates, parser/contract failures, and non-confirmatory financial routing
   results remain visible rather than being pooled away.
5. **A protocol-level deployment finding:** role instructions and output schemas
   interact. An agent can abstain for a sensible reason while the downstream
   contract rejects that abstention, silently changing the population seen by a
   router.

## 4. Limitations and explicit non-claims

- The intervention test is operational, not a causal identification of the
  model's internal evidence use.
- The five personas within a deployment are not independent models.
- The V3.16.1 transfer is directional from Qwen development to Qwen/Ling formal
  evaluation; it is not bidirectional generalization.
- Seventy target pages had appeared previously as distractors, so the fresh cohort
  is not a fully unseen-page replication.
- The financial replay has only 150 test dates per version and no stronger-model
  replication.
- Abstention defers risky cases; it does not repair them.
- No result establishes universal factuality, citation sufficiency, live-retrieval
  robustness, S&P 500 alpha, or prospective trading performance.

## 5. Why this is a strong fit with Prof. Huan Zhang

The most promising connection is **not** "LLMs for stock prediction." It is that
we treat "should this multi-agent consensus be trusted" as an **empirically
measurable, outcome-firewalled quantity**, and we are equally interested in
*when that measurement stops working* -- a verification-minded question posed at
the decision level rather than the weight level.

Concrete intersections with your work on neural-network verification and
certified robustness (alpha-beta-CROWN), adversarial robustness, and LLM safety:

- **Decision-level robustness to evidence manipulation.** The `remove` /
  `reverse` / `substitute` interventions are a controlled stress test of whether
  an agent's decision responds to evidence changes; the synthetic harness varies
  corruption mechanisms and holds out entire mechanisms at evaluation time. This
  is a robustness/verification mindset applied to multi-agent decisions, not
  only to a single model's weights.
- **Rigorous, falsifiable safety evaluation.** Every formal experiment is
  preregistered with frozen endpoints, outcome firewalls, and adequacy gates;
  failures are preserved rather than pooled away. The protocol culture matches
  the standard expected in safety and robustness evaluation.
- **Abstention as a safety behavior.** A core finding is that a sensible
  abstention can be silently rejected by an output contract (73.6% of V1 S&P 500
  failures), changing the population a router sees. "When should an LLM agent
  system refuse to decide, and how do we preserve that refusal" is a concrete
  safety problem for multi-agent systems.
- **Transfer of a reliability signal under shift.** The signal replicates
  aggregate cross-family gates (Qwen -> Ling) but has only 0.294 item-level
  Spearman correlation -- a crisp domain-adaptation / generalization problem
  with an existing experimental infrastructure.

I would frame the conversation around **verifying or rigorously bounding when a
reliability signal transfers**, and around **safe abstention as a first-class
design principle** for LLM agent systems, rather than around extending the
financial application for its own sake.
## 6. Proposed next project

### Shift-Aware Provenance Risk Transfer

**Goal:** determine when an outcome-independent reliability score trained or
selected in one domain/model remains calibrated in a new domain/model, and detect
when transfer should be rejected.

A possible program is:

1. Represent each consensus by intervention behavior, provenance structure,
   confidence, and measurable source/target shift features.
2. Separate invariant reliability components from model- or domain-specific
   calibration components.
3. Adapt calibration using target-unlabeled response data only; labels remain
   sealed until final evaluation.
4. Add a transfer-uncertainty gate that abstains when the target falls outside the
   supported reliability regime.
5. Evaluate on held-out model families, held-out corruption mechanisms, new QA
   datasets, and as-of S&P 500 time windows.

The main hypotheses would be:

- a frozen structural risk score transfers better than a freely learned router
  under mechanism shift;
- target-unlabeled calibration can improve risk control without changing the
  pre-outcome ranking; and
- a shift-aware abstention rule can improve safety even when a universal routing
  gain is not identifiable.

Primary metrics would include AUROC/AURC, Risk@80, worst-label performance,
Brier/ECE, cross-model rank correlation, achieved coverage, and the cost of
rejecting valid consensus. The emphasis would remain on selective reliability
under distribution shift, with finance serving as a demanding sequential testbed
rather than as a performance claim.

## 7. Suggested contact positioning

Lead with **reliability verification + safety-aware abstention for LLM agent
systems**, then use the cross-family transfer boundary and the S&P 500 replay as
evidence that the problem is difficult and real. Do not lead with "I built a
profitable trading agent," "causal faithfulness," or "a new universal truth
detector."

A concise ask is:

> I would like to explore whether the weak item-level transfer of an otherwise
> successful reliability signal can be formalized as a domain-adaptation and
> selective-prediction problem, with target-label-free calibration and explicit
> abstention under support mismatch. I would also welcome your perspective on
> making the intervention-inertia signal a verifiable property of LLM-agent
> decisions, in the spirit of certified-robustness work.