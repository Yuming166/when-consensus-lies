# AutoResearch Guide — FinQA + ConvFinQA Financial Reliability Exploration with Astra6

## 1. Scope and motivation

FinQA has 8,281 QA examples with gold reasoning programs and supporting facts over financial reports. ConvFinQA has 3,892 conversations and 14,115 questions, with official train/dev/test conversation splits of 3,037/421/434. These are medium-sized rather than huge datasets: large enough for controlled intervention studies, but small enough to run several thousand to tens of thousands of LLM calls with careful auditing.

The research question is:

> Can controlled perturbations of program-relevant financial evidence reveal answer-reliability information beyond the model's original response/confidence, and if so, can that signal be distilled into a compact low-query reliability estimator?

Do not search for a student architecture before establishing a teacher signal.

## 2. Experimental boundaries

- Use official TRAIN only for method discovery.
- Keep official DEV locked during exploration.
- Keep TEST sealed.
- Do not select examples by correctness after generation.
- Do not tune intervention wording using labels.
- Preserve failed calls and parse failures.
- Verify every private research-agent call returns `gpt-6-astra`; abort on fallback.
- Base answering model: Qwen3.5-4B primary; Ling-3.0-tiny only as a later replication if Qwen establishes signal.
- Do not require or store hidden chain-of-thought. Store final answer, confidence/probability, evidence IDs, structured operation/program outputs if explicitly requested, and intervention responses.

## 3. Recommended scale

### FinQA first pass
Freeze 2,000 TRAIN examples.

Per example:
1. original
2. relevant supporting-fact removal
3. relevant operand perturbation
4. irrelevant numeric perturbation
5. paraphrase placebo

Expected calls:
\[
2000\times5=10,000
\]

If signal exists, expand to 4,000 TRAIN examples and richer interventions.

### ConvFinQA first pass
Freeze 1,000 TRAIN conversations. Select up to 3 eligible target turns per conversation using dependency metadata only.

Per target turn:
1. original
2. current relevant evidence removal
3. dependent previous-turn perturbation
4. non-dependent previous-turn perturbation
5. paraphrase/history placebo

Expected calls: roughly 12,500–15,000.

## 4. FinQA intervention families

### F1 Supporting-fact removal
Remove one gold supporting fact while leaving the rest unchanged.

### F2 Supporting-fact paraphrase
Paraphrase a gold supporting fact without changing numerical content.

### F3 Relevant operand perturbation
Replace one number used by the gold program with a realistic alternative.

### F4 Irrelevant numeric perturbation
Modify a number not used by the gold program.

### F5 Program-step counterfactual
Perturb an operand/intermediate quantity associated with a specific gold program step.

### F6 Evidence swap
Replace a relevant row/sentence with a matched irrelevant row/sentence from the same report.

### F7 Formatting placebo
Change formatting only.

Gold annotations may be used offline to construct interventions, but gold answer/correctness must never enter the reliability predictor.

## 5. ConvFinQA intervention families

### C1 Current-turn supporting evidence removal
Remove evidence needed for the current turn.

### C2 Previous dependent-turn perturbation
Change an earlier answer/fact on which the current turn depends.

### C3 Previous-turn paraphrase
Semantics-preserving control.

### C4 Dependency-break intervention
Replace a required earlier fact/answer with an incompatible but plausible alternative.

### C5 Non-dependent turn perturbation
Perturb an earlier turn that the current answer does not depend on.

### C6 Current operand perturbation
Perturb a numerical operand used at the current step.

### C7 History truncation
Remove varying amounts of prior history.

## 6. Structured record

For every call, log:

```json
{
  "dataset": "FinQA_or_ConvFinQA",
  "example_id": "...",
  "conversation_id": null,
  "turn_id": null,
  "model": "...",
  "intervention_family": "...",
  "intervention_id": "...",
  "original_answer": "...",
  "intervened_answer": "...",
  "original_confidence": 0.0,
  "intervened_confidence": 0.0,
  "answer_changed": false,
  "direction_changed": false,
  "gold_relevance": "relevant_or_irrelevant_or_placebo",
  "program_step": null,
  "evidence_ids": [],
  "parse_valid": true,
  "failure_reason": null
}
```

## 7. Baseline competence audit

Before any reliability modeling, record:
- original accuracy
- confidence distribution
- error rate by program length
- error rate by operator type
- table/text/mixed evidence
- dependency depth for ConvFinQA
- parse-valid rate

If accuracy is >95% or <20%, add a second model family or adjust difficulty using only pre-answer metadata. Do not rebalance by correctness.

## 8. Behavioral fingerprint Z

Construct outcome-blind features such as:
- relevant-removal flip rate
- irrelevant-removal flip rate
- paraphrase instability
- relevant operand sensitivity
- irrelevant numeric sensitivity
- confidence drop under relevant removal
- confidence shift under placebo
- relevant-vs-irrelevant response gap
- program-step sensitivity
- ConvFinQA dependency-sensitive vs non-dependent response gap

Do not include gold answer/correctness in Z.

## 9. Stage A — Signal existence

Compare:

\[
B_0=f(O)
\]

versus:

\[
B_1=f(O,Z)
\]

Use a small frozen model set:
- regularized logistic
- shallow GBDT
- small MLP

Metrics:
- AUROC
- AUPRC
- Brier
- ECE
- Risk@80
- AURC

Bootstrap:
- FinQA: example-level
- ConvFinQA: conversation-level

Mandatory controls:
- shuffled Z
- confidence-only
- placebo-only
- operation-family metadata
- program length / dependency depth
- relevant/irrelevant label swap

Preferred Stage A gate:

\[
95\%CI(\Delta AUROC)>0
\]

plus no major Brier/ECE collapse, and real Z must outperform shuffled/null controls.

If FAIL: do not train a student.

## 10. Stage B — Relevant-vs-irrelevant contrast

Define:
\[
Z_{rel},\quad Z_{irr}
\]

Compare:
\[
O+Z_{rel}
\]
vs.
\[
O+Z_{irr}
\]
and
\[
O+Z_{rel}+Z_{irr}.
\]

A strong result requires program-relevant perturbations to provide incremental value beyond nuisance sensitivity.

## 11. FinQA program-aware analysis

Analyze by:
- program length
- operator type
- number of operands
- table vs text
- single-step vs multi-step
- arithmetic vs comparison

Questions:
1. Does signal increase with reasoning depth?
2. Do incorrect answers respond differently to relevant perturbations?
3. Does irrelevant sensitivity characterize unreliable answers?
4. Is response direction aligned with the gold program?

Treat any gold-program-dependent feature as oracle analysis unless it is available at deployment.

## 12. ConvFinQA dependency analysis

For each turn compute:
- dependency depth
- number of prerequisite turns
- previous-answer sensitivity
- irrelevant-history sensitivity
- propagation after earlier-turn perturbation

Key test:
\[
\text{dependency-aligned response}\rightarrow\text{current-turn correctness}
\]

Compare against:
- random earlier-turn perturbation
- non-dependent-turn perturbation
- history-length controls

Optionally test whether a reliability score at turn \(t\) predicts downstream errors at \(t+1,t+2\).

## 13. Cross-dataset transfer

Only if both datasets show positive TRAIN-only signal.

Train a frozen reliability estimator on FinQA and evaluate only semantically matched features on ConvFinQA, and vice versa where meaningful.

Do not force transfer across incompatible feature definitions.

## 14. Distillation — conditional only

Do not run unless Stage A passes.

Teacher:
\[
r_T=P(C=1\mid O,Z)
\]

Student inputs:
- original response
- optionally 1–2 selected probes

Test query budgets:
\[
q\in\{0,1,2\}
\]

Primary metric:
\[
Retention(q)=\frac{AUROC(S_q)-AUROC(O)}{AUROC(T)-AUROC(O)}
\]

Student success requires retaining actual reliability utility, not merely correlating with teacher scores.

## 15. Active probe selection

Only after fixed-probe distillation works.

Learn:
\[
\pi(k\mid O,R_{observed})
\]

Candidate probes:
- relevant removal
- relevant operand perturbation
- irrelevant control
- paraphrase
- dependency perturbation for ConvFinQA

Goal: recover most teacher gain in 1–2 extra calls.

## 16. Mandatory null controls

1. relevant vs irrelevant evidence
2. paraphrase placebo
3. shuffled fingerprint
4. operation-family metadata
5. input-length baseline
6. confidence-only
7. magnitude-matched random numeric perturbation
8. same-report irrelevant donor
9. ConvFinQA dependent vs non-dependent previous-turn perturbation

A reliability claim must survive these controls.

## 17. Astra6 research roles

Use separate Astra6 roles:
- Dataset Auditor
- Intervention Designer
- Leakage Auditor
- Measurement Skeptic
- Statistician
- Failure Analyst
- Adjudicator

Astra6 is for protocol design, critique, and synthesis—not as an outcome-conditioned pseudo-label oracle in the main method.

## 18. Search discipline

Before generation, freeze:
- sampled IDs
- model version
- prompts
- parser
- intervention families
- feature definitions
- metrics
- bootstrap plan
- gate thresholds
- null controls

Do not:
- search until positive
- add interventions after seeing results
- choose only wrong examples
- unlock DEV during exploration
- select the best subgroup post hoc

## 19. Verdict labels

Use one per dataset:

```text
SIGNAL_NOT_ESTABLISHED
BEHAVIORAL_RELIABILITY_SIGNAL_ESTABLISHED
RELEVANCE_SPECIFIC_SIGNAL_ESTABLISHED
GENERIC_SENSITIVITY_ONLY
DISTILLATION_READY
DISTILLATION_SUCCESS
DISTILLATION_FAILED
```

## 20. DEV unlock

Official DEV may be used once only after:
- TRAIN Stage A passes
- intervention protocol frozen
- controls pass
- final reliability estimator frozen
- hyperparameters frozen
- adjudicator approves

No tuning after DEV. TEST remains sealed.

## 21. Output tree

```text
consensus_stress/autoresearch_financial_qa/
├── 00_protocol/
│   ├── PROTOCOL.md
│   ├── DATASET_AUDIT.md
│   ├── SPLIT_MANIFEST.json
│   ├── INTERVENTION_MANIFEST.json
│   └── HASHES.json
├── finqa/
│   ├── 01_baseline/
│   ├── 02_interventions/
│   ├── 03_signal/
│   ├── 04_relevance_controls/
│   ├── 05_program_analysis/
│   └── FINAL_DECISION.json
├── convfinqa/
│   ├── 01_baseline/
│   ├── 02_interventions/
│   ├── 03_signal/
│   ├── 04_dependency_analysis/
│   └── FINAL_DECISION.json
├── cross_dataset/
├── distillation/
├── EXPERIMENT_LEDGER.jsonl
├── PAPER_SAFE_CLAIMS.md
├── PAPER_UNSAFE_CLAIMS.md
└── NEXT_EXPERIMENTS.md
```

## 22. Recommended first execution

### Batch A — FinQA Qwen
Freeze 2,000 TRAIN examples.

Run:
- original
- relevant removal
- relevant operand perturbation
- irrelevant numeric perturbation
- paraphrase

Expected 10,000 calls.

Run only Stage A + Stage B first.

### Batch B — ConvFinQA Qwen
Freeze 1,000 TRAIN conversations, up to 3 dependency-eligible turns per conversation.

Run:
- original
- current relevant removal
- dependent previous-turn perturbation
- non-dependent previous-turn control
- paraphrase/history placebo

Expected roughly 12,500–15,000 calls.

## 23. Final scientific interpretation

Strong positive result:

> In deterministic and conversational financial reasoning tasks, controlled perturbations of program-relevant evidence reveal reliability information beyond the model's original response/confidence, while matched irrelevant and placebo perturbations do not. A compact student can preserve part of this diagnostic signal with a small probe budget.

Strong negative result:

> Even with gold programs and supporting evidence enabling precise finance-domain interventions, intervention response does not predict correctness beyond original-response baselines. This would imply that the previous S&P500 failures are not solely due to stochastic market outcomes.

## 24. Core instruction to Astra6

> Do not optimize for a positive result. First determine whether controlled finance-domain interventions contain correctness information under identifiable, deterministic reasoning tasks. Preserve negative results and null controls. Do not train a student until the full intervention teacher demonstrates stable incremental reliability value. Treat gold programs as offline construction metadata, never as hidden deployment-time supervision. Keep official DEV and TEST sealed until TRAIN gates are complete.
