# AutoResearch 0918 --- Astra6-Only Discovery Protocol

## Hindsight Credit Assignment for Behavioral Reliability

**Date:** 2026-09-18\
**Project:** `when-consensus-lies`\
**Workspace:** `consensus_stress/autoresearch_astra_credit/`\
**Research engine:** **PRIVATE ASTRA6 RELAY ONLY**\
**Forbidden research model:** server Luna or any implicit fallback
model\
**Starting point:** Wave-3 verdict `KEEP_B6_NO_ESCALATION`\
**Final verdict:** `DISCOVERED / PARTIAL / REFRAME / FALSIFIED`

## 0. Mission

This is a discovery search, not a confirmation run. The frozen starting
evidence is: the audited intervention-response pipeline works; B6 raw
trajectory remains the strongest retained representation; B8 did not
beat B6; B7 direction-only is strong; teacher/prospective escalation was
stopped; 807 prospective dates remain untouched.

New hypothesis:

> The raw behavioral trajectory may already contain useful information.
> The missing ingredient may be date-conditioned credit assignment:
> learning which intervention responses matter for reliability in the
> current market state.

Model:

\[ r\_{t,a}=`\sigma`{=tex}`\left`{=tex}(w_0\^T x\_{0}+`\sum`{=tex}*k
g*{t,a,k}w_k\^T x\_{t,a,k}ight), `\quad`{=tex} g\_{t,a,k}=g\_
heta(X_t,T\_{t,a},k). \]

Future outcomes may provide **training-only hindsight pseudo-labels**
for (g).

The goal is to search aggressively for a mechanism that survives
falsification, not to manufacture a positive result.

## 1. Research philosophy

Use:

\[ ext{diverse hypotheses} o ext{cheap falsification} o ext{critique} o
ext{cross-pollination} o ext{freeze} o ext{prospective test}. \]

The transferable principles are independent exploration, diversity,
aggressive pruning, machine-checkable evaluation, adversarial critics,
consolidation of surviving ideas, and strict separation of invention
from final validation.

Do not imitate brute-force scale for its own sake. Do not tune
indefinitely on DEV, inspect prospective labels, redefine metrics after
seeing results, selectively report seeds, silently change splits, or
discard failures.

## 2. Astra6-only routing

All LLM-mediated research reasoning must go through the user's private
Astra6 relay: hypothesis generation, method design, interpretation,
critics, synthesis, teacher labels, prompt design, and red-team
reasoning.

Server Luna is forbidden for research decisions.

Local deterministic code is encouraged for feature construction,
regression/classification, attribution, bootstrap, statistics, hashing,
joins, audits, and plotting.

## 3. Model-identity hard gate

Every LLM call must log:

``` json
{
  "requested_model": "...",
  "returned_model": "...",
  "endpoint_alias": "...",
  "request_id": "...",
  "timestamp": "...",
  "prompt_hash": "...",
  "response_hash": "..."
}
```

Before each wave, send a smoke test and verify the returned identity is
an allowed Astra6 identity. Write `model_identity_audit.json`. Abort on
Luna, fallback, missing identity, or inconsistency. **No automatic
fallback.**

If the relay cannot expose reliable identity, return
`IDENTITY_UNVERIFIABLE` and stop.

## 4. Secrets

Use environment variables only:

``` bash
ASTRA6_BASE_URL=...
ASTRA6_API_KEY=...
ASTRA6_MODEL=...
```

Commit only `.env.example`. Never commit credentials, relay secrets,
private headers, cookies, or tokens. Scan diffs and generated logs
before commit.

## 5. Immutable prior evidence

Create `00_protocol/PRIOR_RESULTS_LOCK.md` and hash prior artifacts. The
new search may not reinterpret the prior negative result as positive.

Frozen facts: - B6 retained. - B8 failed to beat B6 on full DEV. - B7
direction-only is strong. - prospective escalation was stopped. -
prospective pool is untouched.

## 6. Data firewall

Development: - TRAIN: 243 dates - DEV: 157 dates

Protected: - PROSPECTIVE: 807 dates

Research agents may see only TRAIN/DEV until the final gate. Prospective
outcomes must not enter prompts, files, feature construction,
pseudo-labels, or method selection. Fail closed on a prospective-path
request.

## 7. Core pseudo-label families

### P1 --- Counterfactual diagnostic credit

For intervention block (k):

\[ `\Delta`{=tex}*{t,a,k} =
`\ell`{=tex}(f(T\^{-k}*{t,a}),c\_{t,a})-`\ell`{=tex}(f(T\_{t,a}),c\_{t,a}).
\]

Convert to soft credit:

\[ q\^{alg}*{t,a,k}=softmax(`\Delta`{=tex}*{t,a,k}/ au). \]

Test leave-one-block-out, grouped permutation, influence approximation,
and approximate Shapley. Any model-derived attribution must be
**out-of-fold on TRAIN**.

### P2 --- Hindsight reliability regime

Training-only:

\[ z_t\^H=h(X_t,T_t,R\_{t,1:10}). \]

Possible concepts include trend-supportive, reversal-prone,
information-conflict, low-resolution, high-resolution, and behaviorally
ambiguous. Student predicts the regime pre-outcome. The regime counts
only if it improves reliability.

### P3 --- Outcome-path support

Use the full future path (R\_{t,1:10}), not just the final sign.
Candidate quantities: return magnitude, directional persistence,
fraction of horizon on the final side of zero, maximum favorable/adverse
excursion, and path volatility.

Construct a soft support target measuring how strongly the realized path
supports the agent's original forecast.

## 8. Astra6 hindsight teacher

Astra6 may see TRAIN-only future outcomes plus pre-outcome market state
and trajectory. It outputs structured auxiliary targets, never "true
belief":

``` json
{
  "diagnostic_credit": {
    "paraphrase": 0.0,
    "removal": 0.0,
    "agree": 0.0,
    "contradict": 0.0
  },
  "outcome_resolution": 0.0,
  "trajectory_ambiguity": 0.0,
  "regime_distribution": {},
  "posterior_correctness": 0.0,
  "teacher_confidence": 0.0,
  "observable_support": ["..."]
}
```

Teacher rationale never becomes student input.

## 9. Teacher stability gate

Before scaling: - \>=100 stratified TRAIN units; - \>=3 independent
Astra6 generations.

Measure credit Spearman, top-credit agreement, regime agreement,
posterior stability, entropy, and agreement with algorithmic credit.

Pass only if teacher targets are stable, nontrivial beyond correctness,
not just direction restatement, and retain variance conditional on
correctness. Otherwise `DROP-ASTRA-PSEUDOLABEL` and continue algorithmic
credit only.

## 10. Discovery populations

Use four Astra6 populations.

**Explorers:** 12--24 independent proposals per major wave. Initially
blind to one another. Each specifies hypothesis, math, why B6 misses it,
cheapest falsification, leakage risks, and abandonment condition.

**Builders:** turn selected proposals into minimal executable
experiments. Prefer simple models.

**Critics:** try to kill candidates via direction, market state,
confidence, attribution leakage, in-sample pseudo-label leakage, lucky
seeds, calibration artifacts, and simpler baselines.

**Synthesizers:** after a batch completes, inspect successes and
failures and cross-pollinate only supported mechanisms.

## 11. Search loop

``` text
Independent hypotheses
→ novelty/deduplication
→ TRAIN-only cheap falsification
→ critic attack
→ limited DEV gate
→ mechanism extraction
→ cross-pollination
→ next generation
```

Maximum recommended generations: **4**.

Maintain `hypothesis_ledger.jsonl` with IDs H001..., parents,
generation, mechanism, status, metrics, critic findings, and artifacts.
Never delete failures.

Statuses: `PROPOSED`, `DUPLICATE`, `CHEAP_FAIL`, `DEV_FAIL`,
`AUDIT_FAIL`, `SURVIVED`, `CROSS_POLLINATED`, `FROZEN_FINALIST`.

## 12. Generation-1 seed families

Explore at least:

1.  Dynamic intervention gating.
2.  Algorithmic credit distillation.
3.  Astra credit distillation.
4.  Hybrid algorithmic+Astra credit.
5.  Outcome-path soft reliability.
6.  Multi-task correctness + credit.
7.  Regime-conditioned gating.
8.  Small mixture of reliability experts.
9.  **Residual-over-B6**.
10. Hard-case specialist.
11. Meta-reliability: predict when B6 is wrong.
12. Pairwise intervention-credit ranking, not pairwise agent trust.

## 13. High-priority rule: residualize, don't replace

B6 survived. Prefer learning what it misses.

Generate cross-fitted B6 prediction:

\[ `\hat `{=tex}r\^{B6,OOF}\_{t,a}. \]

Learn:

\[ logit(r^{new})=logit(r^{B6})+`\delta`{=tex}\_ heta(X,T,q). \]

Strongly regularize (`\delta`{=tex}). This makes incremental value
explicit.

## 14. Cross-fitting mandatory

Any pseudo-label depending on a trained predictor must be generated OOF
by date: 1. split TRAIN by date into K folds; 2. fit on K-1; 3. generate
credit on held-out fold; 4. concatenate OOF targets; 5. train student.

No row may create its own attribution through an in-sample fitted model
without an explicit audit.

## 15. Cheap falsification before DEV

Each candidate first passes TRAIN-only CV against: - B6; - B7
direction-only; - market-only; - confidence-only; - shuffled
pseudo-label; - shuffled trajectory.

Kill early if no OOF improvement, shuffled labels perform similarly,
direction reproduces the gain, calibration collapses, or one seed drives
the result.

## 16. DEV budget discipline

DEV is not an unlimited optimizer.

Recommended maximum distinct candidate-family evaluations: - Generation
1: 8 - Generation 2: 5 - Generation 3: 3 - Generation 4: finalists only

Log every access in `dev_evaluation_ledger.jsonl`. Tell Astra6 how many
DEV evaluations have occurred.

## 17. Advancement criteria

Do not advance on AUROC point estimate alone. Prefer: - positive paired
AUROC delta vs B6; - no material Brier/ECE deterioration; - not
explained by direction-only; - shuffled pseudo-label fails; - gain
appears across multiple strata; - paired date-bootstrap evidence is at
least suggestive.

Strong gate:

\[ 95%CI(`\Delta `{=tex}AUROC)\>0. \]

Exploratory advancement with interval crossing zero must be explicitly
marked exploratory.

## 18. Pseudo-label distillability gate

Before treating any hindsight target as useful supervision, test:

\[ X_t,T\_{t,a}ightarrow q\_{t,a}. \]

Report correlation, MAE/KL, ranking agreement, and calibration where
meaningful.

If the target cannot be predicted pre-outcome, it is mostly
hindsight-only information and should be dropped.

## 19. Scientific debate

For each survivor launch fresh Astra6 roles: - Advocate - Skeptic -
Methodologist

A fourth adjudicator receives all three reports and recommends
`ADVANCE`, `ABLATE`, or `KILL`.

Critics are explicitly rewarded for finding simpler explanations.

## 20. Cross-pollination

Children cite parent IDs. Combine at most three mechanisms. Do not build
kitchen-sink models.

Example:

``` text
H031 = H009 residual-over-B6
     + H014 algorithmic credit
     + H022 outcome-path resolution
```

## 21. Anomaly mining

On TRAIN, inspect structured B6 residuals: - confident B6 failures; -
intervention patterns associated with B6 error; - VIX/PCR strata; -
agent-specific residuals; - agree/contradict asymmetry; -
high-confidence wrong panels; - disagreement and unanimous-wrong panels.

Use TRAIN anomalies to generate hypotheses. DEV anomaly mining is logged
as DEV reuse. Prospective anomaly mining is forbidden.

## 22. Teacher variants

If stability passes, compare only: - T0 no teacher; - T1 final-outcome
teacher; - T2 outcome-path teacher; - T3 algorithmic-credit-informed
Astra teacher.

T3 tests whether Astra adds structure beyond deterministic attribution.

## 23. Small student families

Start with: - logistic regression + interactions; - GAM/splines; -
gradient-boosted trees; - small MLP; - low-rank dynamic gate; - small
mixture-of-experts gate.

Do not fine-tune a large LLM unless simpler models fail and a specific
representational bottleneck is demonstrated.

## 24. Critical comparisons

The study must answer:

\[ B6+AlgCredit\>B6? \]

\[ B6+AstraCredit\>B6? \]

\[ B6+HybridCredit\>B6+AlgCredit? \]

\[ B6+PathTarget\>B6? \]

\[ B6+Hybrid\>B7? \]

and finally on frozen prospective data:

\[ B6+Hybrid\>B6? \]

Interpretation: - Alg \> B6: credit assignment has value. - Astra \> B6:
LLM hindsight supervision has value. - Hybrid \> Alg: Astra adds beyond
algorithmic attribution. - Hybrid \> B7: result is not merely direction.

## 25. Primary statistics

Reliability: - AUROC - AUPRC - Brier - ECE

Panel utility: - wrong-majority recovery - false-consensus selective
risk - corrected panels - newly broken panels - net corrections

Bootstrap by date. Because 10-day outcomes overlap, also use block
bootstrap and a non-overlapping-date robustness analysis.

## 26. Prospective unlock gate

Keep all 807 dates sealed until: 1. search stops; 2. \<=2 finalists
chosen; 3. architecture frozen; 4. pseudo-label recipe frozen; 5.
prompts frozen; 6. hyperparameters frozen; 7. code frozen; 8. seeds
frozen; 9. primary metrics frozen; 10. failure criteria frozen; 11. git
commit recorded; 12. protocol SHA-256 recorded; 13. fresh Astra6 critic
signs off; 14. no unresolved leakage finding remains.

Then unlock exactly once under a preregistered chronological evaluation
plan.

## 27. Prospective success

Strong discovery requires: - positive paired delta vs B6; - calibration
not materially worse; - dependence-aware robustness; - direction-only
cannot reproduce; - shuffled pseudo-label cannot reproduce; - not
isolated to one agent; - downstream panel utility or selective risk
improves; - no leakage.

Preferred:

\[ 95%CI(`\Delta `{=tex}AUROC)\>0. \]

Positive point estimate with CI crossing zero → `PARTIAL`, not
`DISCOVERED`.

## 28. Failure taxonomy

Use: - N1 target unstable - N2 target not distillable - N3 distillable
but not useful - N4 TRAIN/CV gain, DEV fail - N5 DEV gain, prospective
fail - N6 direction explains gain - N7 market-only explains gain - N8
real but narrow effect

This taxonomy is itself a research output.

## 29. Final verdict

**DISCOVERED:** frozen pseudo-label/credit method prospectively beats B6
with robust controls.

**PARTIAL:** real but narrow/inconsistent effect.

**REFRAME:** another mechanism survives but Astra hindsight
pseudo-labeling does not.

**FALSIFIED:** no pseudo-label formulation survives prospective
validation.

## 30. Required directory

``` text
consensus_stress/autoresearch_astra_credit/
├── 00_protocol/
├── 01_hypotheses/
├── 02_algorithmic_credit/
├── 03_astra_teacher/
├── 04_students/
├── 05_train_cv/
├── 06_dev/
├── 07_debates/
├── 08_red_team/
├── 09_finalists/
├── 10_prospective/
└── 11_synthesis/
```

Every experiment saves hypothesis ID, parents, commit, config, seed,
model identity, prompt hash, data hash, metrics, bootstrap, controls,
critic report, and decision.

## 31. Explorer prompt

> You are one independent research scientist in a falsification-driven
> search. The strongest baseline is B6 raw intervention trajectory.
> Previous low-rank B8 failed to beat it and direction-only B7 is
> strong. Generate one technically distinct mechanism by which
> training-only future outcomes could improve pre-outcome interpretation
> of B6. Do not propose belief recovery. Specify a minimal mathematical
> method, cheapest falsification test, leakage risks, and a result that
> would make you abandon the idea. Optimize for testability and
> incremental value beyond B6.

Explorers initially do not see one another's proposals.

## 32. Critic prompt

> Try to falsify this method. Assume any reported gain may come from
> leakage, direction, market state, in-sample attribution, repeated DEV
> tuning, lucky seeds, or calibration artifacts. Identify the smallest
> decisive controls. Recommend ADVANCE only if simpler explanations are
> ruled out.

## 33. Synthesizer prompt

> Given the complete ledger of successes and failures, identify the
> smallest mechanism supported by evidence. Cross-pollinate at most
> three compatible ideas. Preserve negative evidence. Propose the next
> experiment with the highest expected information gain, not the highest
> chance of a positive number.

## 34. Resource allocation

Use Astra6 adaptively rather than repeatedly tuning one prompt.
Suggested allocation: - 10% broad independent exploration - 20%
critics/targeted redesign - 25% teacher target discovery/stability - 25%
surviving-method interpretation/cross-pollination - 10% red-team
verification - 10% independent synthesis

## 35. Discovery stop rule

Stop search when any two hold: 1. four generations completed; 2. last
generation yields no new mechanism; 3. gains are explained by
direction/market-only; 4. targets are not distillable; 5. DEV gains
shrink under stronger controls; 6. complexity rises without effect-size
gain; 7. critics converge that remaining variants are cosmetic.

Then freeze a finalist or issue `FALSIFIED/REFRAME`.

## 36. Highest-priority first experiment

Before a large swarm:

1.  Reconstruct cross-fitted B6 predictions on TRAIN.
2.  Generate OOF algorithmic leave-one-intervention-block credit.
3.  Generate Astra6 hindsight credit on a stratified TRAIN subset.
4.  Measure algorithmic-vs-Astra credit agreement.
5.  Test pre-outcome distillability of each target.
6.  Train residual gates:
    -   `B6+AlgCredit`
    -   `B6+AstraCredit`
    -   `B6+HybridCredit`
7.  Run TRAIN-only CV.
8.  Only if at least one survives, authorize one DEV evaluation batch.

This directly tests whether pseudo-labeling deserves more resources.

## 37. Final independent Astra6 synthesis

Use a fresh Astra6 context that did not design methods. Give it the
frozen protocol, prior negative result, full hypothesis ledger,
failures, survivors, DEV ledger, red-team reports, and prospective
results if unlocked.

It must answer whether credit adds beyond B6, whether targets are
stable/distillable, whether Astra adds beyond algorithmic credit,
whether path supervision helps, whether gains survive
direction/market/permutation/calibration/dependence controls, whether
panel utility improves, and what the narrowest defensible mechanism is.

Return exactly:

`DISCOVERED / PARTIAL / REFRAME / FALSIFIED`

and generate: - `FINAL_SYNTHESIS.md` - `FINAL_DECISION.md` -
`METHOD_WINNER.md` - `PSEUDOLABEL_ANALYSIS.md` -
`DISTILLABILITY_ANALYSIS.md` - `DIRECTION_AUDIT.md` -
`LEAKAGE_AUDIT.md` - `PROSPECTIVE_RESULTS.md` - `PAPER_SAFE_CLAIMS.md` -
`PAPER_UNSAFE_CLAIMS.md` - `NEXT_EXPERIMENTS.md`

## 38. Final instruction

Your job is **not to make the hypothesis true**.

Search hard enough, diversely enough, and critically enough that a
surviving positive result is difficult to dismiss as leakage, repeated
tuning, direction effects, market confounding, lucky seeds, arbitrary
teacher scores, pseudo-label memorization, or post-hoc storytelling.

Preserve important failures.

Prefer a simple mechanism that survives attack over a complicated method
with a larger point estimate.

**The prospective pool is the court of last resort. Do not touch it
until invention is over.**
