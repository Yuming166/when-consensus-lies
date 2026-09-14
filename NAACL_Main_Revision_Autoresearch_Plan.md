# NAACL Main Revision / Autoresearch Plan

## 0. Objective

Current reviewer assessment: **Borderline / Weak Reject (around 3/5), but close to Accept (4/5)**.

The paper already has strong empirical discipline:

- preregistration
- outcome firewall
- frozen cohort
- grouped bootstrap
- label-stratified evaluation
- permutation / placebo controls
- cross-model replication
- cost analysis
- ablations

The main remaining threat is **not lack of experiments**. It is the scientific interpretation of the core reverse-evidence signal.

### Central reviewer concern

The natural-pair construction creates:

\[
(C,E_S) \leftrightarrow (C,E_R)
\]

with opposite labels, while the reverse condition is byte-identical to the paired item's original condition:

\[
\mathrm{reverse}(i)=\mathrm{original}(j)
\]

and:

\[
Y_j=1-Y_i.
\]

Therefore, a skeptical reviewer may argue:

> The predictive power of the reverse-evidence signal is partly mechanically induced by the paired-item construction, rather than reflecting an independently measurable evidence-responsiveness phenomenon.

This must be treated as the **highest-priority methodological issue**.

The goal of this revision is to make the paper defensible against this objection and, if possible, demonstrate that the phenomenon survives removal of the mirror dependency.

---

# 1. First step: audit the current implementation

Before changing code or manuscript:

1. Read the complete `naacl_main.tex`.
2. Inspect all experiment scripts and configuration files.
3. Identify:
   - natural-pair construction
   - original / reverse / placebo conditions
   - consensus formation
   - scoring implementation
   - bootstrap / CI implementation
   - baseline implementations
   - cross-model experiments
   - preregistration / firewall logic
4. Trace every path by which labels could enter:
   - prompt construction
   - evidence generation
   - score computation
   - model selection
   - threshold selection
5. Produce an internal audit documenting:
   - claims directly supported by existing experiments
   - claims that are too strong
   - exact consequences of mirror-equivalence
   - existing controls that address the issue
   - experiments that could genuinely break the dependency.

**Do not fabricate or silently modify results.**

---

# 2. P0: Mirror-equivalence analysis

Formalize the current dependency.

For each item:

\[
i=(C,E_i,Y_i)
\]

and paired item:

\[
j=(C,E_j,Y_j)
\]

where:

\[
Y_j=1-Y_i.
\]

If:

\[
E_i^{reverse}=E_j^{original},
\]

then:

\[
BF_{reverse}(i)
\]

is not an independently sampled evidence intervention. It is closely tied to the model's prediction on the paired item.

Quantify this relationship empirically.

At minimum calculate:

- agreement between reverse prediction and paired original prediction
- exact equivalence rate
- correlation between reverse-derived score and paired-item prediction
- how much predictive performance can be reconstructed from paired-item predictions alone.

Run a simple diagnostic baseline:

\[
S_{pair}(i)=f(\hat Y_i,\hat Y_j)
\]

where `f` is the simplest possible paired-prediction statistic appropriate to the current label convention.

Compare:

\[
S_{pair}
\]

against:

\[
BF_{reverse}
\]

and:

\[
RS_q.
\]

The purpose is not necessarily to invalidate the method. The purpose is to determine how much of the observed signal is mechanically attributable to the pair structure.

---

# 3. P0/P1: Independent counter-evidence experiment

## Highest-value new experiment

If scientifically feasible, construct a counter-evidence packet that is **not the byte-identical natural mirror**.

For each:

\[
(C,E)
\]

construct:

\[
E_{counter}^{ind}
\]

such that:

1. It supports the opposite conclusion.
2. It is decision-relevant.
3. It is not byte-identical to the paired mirror evidence.
4. It does not simply copy the paired evidence.
5. It does not expose the gold label through metadata.
6. It preserves the same claim/context as much as possible.
7. It is created without post-hoc use of the evaluation outcome.
8. Generation and evaluation are separated if an LLM is used.

**Never leak the ground-truth label into the final inference prompt.**

---

# 4. Preferred three-condition experiment

Compare:

### A. Natural counter-evidence

Existing paired mirror:

\[
E_{natural}
\]

### B. Independent counter-evidence

New evidence packet:

\[
E_{ind}
\]

### C. Placebo / irrelevant evidence

Evidence that changes the input but should not provide decision-relevant counter-evidence:

\[
E_{placebo}.
\]

Measure:

\[
P(\mathrm{flip}\mid E_{natural})
\]

\[
P(\mathrm{flip}\mid E_{ind})
\]

\[
P(\mathrm{flip}\mid E_{placebo}).
\]

The most important quantity is:

\[
\Delta_{CE}
=
P(\mathrm{flip}\mid E_{counter})
-
P(\mathrm{flip}\mid E_{placebo}).
\]

The scientific question is:

> Does the model selectively respond to decision-relevant counter-evidence, rather than merely reacting to arbitrary evidence perturbations?

---

# 5. If independent counter-evidence works

Run:

## 5.1 Predictive validity

Compare:

- `BF_reverse`
- independent counter-evidence responsiveness
- combined signal
- placebo responsiveness
- paired-prediction-only baseline

Report:

- AUROC
- AUPRC when appropriate
- bootstrap 95% CI
- paired bootstrap differences.

---

## 5.2 Incremental information

Fit a grouped OOF model such as:

\[
P(\mathrm{error})
=
\sigma(
\beta_0+
\beta_1S_{natural}+
\beta_2S_{ind}
).
\]

Determine whether:

\[
S_{ind}
\]

provides predictive information conditional on the mirror-derived score.

Also compare:

\[
S_{natural}
\]

alone vs.

\[
S_{ind}
\]

alone vs.

\[
[S_{natural},S_{ind}].
\]

---

## 5.3 Natural vs independent correlation

Compute:

\[
\rho(S_{natural},S_{ind}).
\]

Interpret carefully.

High correlation means the phenomenon may be robust but not necessarily that the signals are independent.

Low/moderate correlation plus incremental predictive value is especially valuable.

---

# 6. If independent counter-evidence is NOT feasible

Do not manufacture a synthetic positive result.

Instead:

1. Explicitly formalize the mirror-equivalence limitation.
2. Narrow the claim.
3. Stop describing `BF_reverse` as an independently identified latent trait.
4. Frame the contribution as:
   - an empirical paired-consensus phenomenon
   - a pre-outcome stress-test protocol
   - a predictive regularity under natural-pair construction.
5. Add a clear limitation:
   - the current benchmark does not fully separate evidence responsiveness from paired-item structure.
6. State independent counter-evidence as future work.

Scientific honesty is more important than a superficially stronger result.

---

# 7. Reframe the central contribution

The strongest defensible framing is:

> We identify and rigorously test a pre-outcome empirical regularity in multi-agent consensus: consensus items that fail to respond appropriately to decision-relevant counter-evidence are substantially more likely to be incorrect.

Prefer:

- empirical regularity
- behavioral signal
- counter-evidence responsiveness
- consensus fragility
- pre-outcome risk signal
- selective stress test.

Avoid overclaiming:

- latent rigidity
- faithfulness
- a psychological trait
- universal model behavior
- fully model-agnostic reliability
- causal mechanism.

---

# 8. Three main contributions

Structure the paper around three contributions.

## Contribution 1 — Empirical phenomenon

Wrong consensus is disproportionately associated with insufficient response to decision-relevant counter-evidence.

## Contribution 2 — Evaluation protocol

A pre-outcome stress-test protocol measures counter-evidence responsiveness before gold labels are observed.

## Contribution 3 — Empirical validation

The phenomenon is evaluated with:

- multiple model families
- preregistration
- outcome firewall
- grouped bootstrap
- label-stratified evaluation
- placebo controls
- permutation controls
- cross-model transfer
- budget analysis.

Do not make the simple scoring formula itself carry the entire novelty claim.

---

# 9. Revisit the score and call accounting

The paper currently risks confusing:

- total diagnostic protocol
- actual score computation
- auxiliary controls.

Separate:

### Consensus formation

5 calls.

### Main risk probe

10 calls.

### Auxiliary diagnostics

Additional calls used only for robustness / controls.

If the score itself only needs 10 probe calls after consensus formation, state:

> The main score requires 10 probe calls after initial consensus formation.

Do not define the main method as a 25-call method if 15 of those calls are only diagnostics.

Report total experimental cost separately.

---

# 10. Cross-model interpretation

Current cross-model transfer is useful but imperfect.

If:

\[
AUROC_{\mathrm{Qwen}\rightarrow\mathrm{Ling}}\approx0.72
\]

while:

\[
AUROC_{\mathrm{Ling}\rightarrow\mathrm{Ling}}\approx0.90,
\]

do NOT call the score fully model-agnostic.

Use:

> The protocol exhibits partial cross-model transfer, while item-level risk ranking remains substantially model-dependent.

If Qwen/Ling item-level correlation is around 0.5, present this as evidence for:

> shared but model-dependent behavioral structure.

---

# 11. External baselines

Current external baselines are adapted proxies.

Use terminology such as:

> matched-budget adapted baselines

or:

> protocol-adapted comparison methods.

Clearly distinguish:

- faithful reproduction
- adapted proxy
- diagnostic control.

Do not present adapted implementations as exact reproductions of original methods.

Avoid an overly aggressive leaderboard framing.

The goal is to establish:

> the proposed signal provides useful predictive information under a comparable inference budget.

---

# 12. Confidence baseline

The confidence baseline has poor AUROC.

Do not overinterpret it.

State that:

- it is a frozen diagnostic baseline;
- confidence elicitation may not be calibrated consistently across models;
- poor performance here does not imply confidence is universally useless;
- the proposed method does not depend on confidence failure.

If necessary, move detailed confidence analysis to the appendix.

---

# 13. Deployment realism

The benchmark has access to natural counter-evidence, but deployment does not automatically provide it.

Explicitly distinguish:

## Benchmark

Natural counter-evidence is available through paired evidence.

## Potential deployment

An independent retrieval/evidence-generation module must identify decision-relevant counter-evidence.

Conceptual pipeline:

\[
(C,E)
\rightarrow
\text{retrieve/generate counter-evidence}
\rightarrow
\text{stress test}
\rightarrow
\text{risk estimate}
\rightarrow
\text{selective routing}.
\]

The current paper evaluates the value of the stress-test signal **conditional on obtaining counter-evidence**.

Do not claim to solve end-to-end counter-evidence retrieval.

---

# 14. Strengthen selective routing story

The practical implication should be:

> A pre-outcome stress test can identify a subset of consensus items that warrant additional verification.

Rather than:

> The method makes the model more truthful.

Use:

\[
\text{consensus}
\rightarrow
\text{counter-evidence stress test}
\rightarrow
\text{risk score}
\rightarrow
\begin{cases}
\text{accept}\\
\text{verify / escalate}
\end{cases}
\]

Make risk-at-coverage results central if supported by the existing experiments.

---

# 15. Do not blindly add more models

Priority order:

## P0 — Mandatory

- mirror-equivalence audit
- leakage audit
- paired-prediction-only diagnostic
- independent counter-evidence experiment if feasible
- recompute all affected metrics.

## P1 — Strongly recommended

- natural vs independent vs placebo comparison
- incremental predictive value
- deployment limitation
- claim reframing.

## P2 — Optional

- additional model family
- additional dataset
- additional baseline.

Do not spend substantial compute on P2 before P0/P1 are complete.

---

# 16. Statistical requirements

All new experiments must preserve:

- fixed seeds
- frozen item cohort
- no post-outcome model selection
- grouped bootstrap at natural-pair level
- 95% confidence intervals
- label-stratified evaluation where appropriate
- permutation controls when applicable
- no test-set tuning
- no post-hoc sign selection.

If the new analysis changes a preregistered protocol, explicitly label it:

> exploratory / post-hoc robustness analysis.

Never silently present a new analysis as preregistered.

---

# 17. Manuscript narrative

The introduction should follow:

## Problem

High agreement does not imply correctness.

## Gap

Existing consensus / uncertainty methods often inspect agreement, confidence, or sampling consistency, while less attention is paid to whether a consensus responds appropriately to decision-relevant counter-evidence.

## Idea

Measure counter-evidence responsiveness before labels are known.

## Main finding

Wrong consensus is substantially less responsive to counter-evidence.

## Validation

The phenomenon replicates across model families and survives controls.

## Caveat

Natural-pair construction creates a potential mirror-equivalence artifact, which is explicitly tested / bounded.

---

# 18. Reduce defensive prose

Avoid excessive repeated phrases such as:

- “This does not mean...”
- “We emphasize that...”
- “We do not claim...”
- “A reviewer might think...”

Instead:

1. Make the claim precise.
2. Give the evidence.
3. State the limitation once.
4. Move on.

The manuscript should read as a confident scientific argument, not a pre-written rebuttal.

---

# 19. Possible title direction

Current title:

> When Consensus Lies: Counter-Evidence Responsiveness as a Pre-Outcome Signal of Consensus Error

Potential alternatives if experiments justify them:

> When Consensus Lies: Stress-Testing Multi-Agent Agreement with Counter-Evidence

or:

> Counter-Evidence Responsiveness Predicts Errors in Multi-Agent Consensus

Do not change the title unless the final scientific framing genuinely changes.

---

# 20. Final reviewer-oriented checklist

Before finishing the revision, answer:

1. Can a reviewer reasonably claim that the main result is mechanically caused by mirror pairing?
2. If yes, did we empirically break that dependency?
3. If not, did we honestly narrow the claim?
4. Does the main signal add value beyond simple paired-item prediction consistency?
5. Does the phenomenon replicate across model families?
6. Is the deployment story honest about where counter-evidence comes from?
7. Are external baselines clearly labeled as adapted proxies?
8. Is the main call budget stated correctly?
9. Are all confidence intervals and statistical tests reproducible?
10. Can a skeptical reviewer understand the exact contribution within the first two pages?

---

# 21. Target reviewer impression

The ideal final paper should make a skeptical reviewer conclude:

> The authors identify an interesting pre-outcome behavioral signal for consensus reliability. The signal is simple, but the phenomenon is non-trivial, experimentally replicated, and carefully stress-tested. The authors explicitly recognize the mirror-pair limitation and provide evidence that the effect is not merely a trivial consequence of that construction. They avoid claiming that the signal identifies a latent cognitive trait and instead establish a useful selective-verification signal for multi-agent consensus.

The goal is **not** to maximize the number of experiments.

The goal is to make the core scientific claim difficult to dismiss.

---

# 22. Execution rule for Codex / autoresearch

When implementing this plan:

1. Inspect before modifying.
2. Preserve all existing reproducible results.
3. Never overwrite preregistered results with exploratory results.
4. Never use outcome labels to construct test-time evidence.
5. Never tune thresholds on the final test set.
6. Record every new experiment in the work log.
7. Save raw outputs and derived metrics separately.
8. Update the manuscript only after validating the experiment.
9. If an experiment fails, diagnose and report the failure rather than silently changing the protocol.
10. Prioritize scientific validity over positive results.

## Success criterion

A successful revision is one where the strongest remaining criticism is:

> “The phenomenon is interesting but its generality is limited.”

rather than:

> “The main result may be a mechanical consequence of the benchmark construction.”

That distinction is the primary target of this revision.
