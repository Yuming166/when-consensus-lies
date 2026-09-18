# AutoResearch Overnight --- Astra6 G2E → G2F → G2G → Conditional G3

**Date:** 2026-09-19\
**Workspace:** `consensus_stress/autoresearch_astra_credit/`\
**Research LLM:** PRIVATE `gpt-6-astra` ONLY\
**Start:** `GENERATION_2_G2D_COMPLETE`\
**DEV:** locked at start\
**Prospective:** 807 dates sealed at start\
**Mode:** unattended, fail-closed, audit-preserving

## 0. Objective

Test the remaining scientific chain:

\[ Y\_{future} `\to `{=tex}q\^{hindsight}
`\to `{=tex}`\hat `{=tex}q(X,T)
`\to `{=tex}`\Delta `{=tex}Reliability\_{\>B6}. \]

G2-D has established a promising but incomplete result. The overnight
goal is to determine whether the two surviving hindsight targets provide
**incremental reliability information beyond frozen B6**.

Do not optimize for a positive result. Optimize for a result that
survives hostile review. Never lower gates, tune repeatedly on DEV,
inspect prospective outcomes early, choose favorable seeds/subsets, or
silently discard failures.

## 1. Immutable starting evidence

Preserve all earlier artifacts/verdicts.

Generation 1: - algorithmic credit distillability Spearman ≈ 0.0525 vs
threshold 0.20 → `DROP_ALGORITHMIC_PSEUDOLABEL`; - Astra teacher Gen-1
remains `DROP-ASTRA-PSEUDOLABEL` because only 99/100 complete triplets,
despite strong observed stability.

Generation 2 replication: - 306 requests; - 305 schema-valid
successes; - 1 transport failure; - 100 complete triplets; - pairwise
Spearman 0.7576; - top-credit agreement 0.8700; - entropy 0.7638; -
verdict `ASTRA_STABILITY_REPLICATED`.

G2-D surviving targets:

`q_paraphrase` - D3 Spearman 0.3699; - direction-only 0.0192; -
Full−Direction +0.3507; - bootstrap CI excludes zero.

`q_removal` - D3 Spearman 0.3882; - direction-only −0.0118; -
Full−Direction +0.4000; - bootstrap CI excludes zero.

Do not revive q_agree, q_contradict, residual targets, or path_support
in G2-E.

## 2. North-star question

\[
`\boxed{\text{Do predicted paraphrase/removal hindsight credits add reliability information beyond B6?}}`{=tex}
\]

Distillability alone is insufficient.

## 3. Safety and model identity

Use only the isolated Astra6-credit worktree. Do not modify dirty `main`
or unrelated S&P500 processes.

Every successful LLM call must return the preregistered Astra6 identity.
Log requested/returned model, request ID, timestamp, prompt hash,
response hash and attempt number.

For 429/5xx/timeouts: - preserve failure; - retry under the already
frozen policy; - same model and semantic prompt; - never fallback.

Any successful non-Astra return → `MODEL_IDENTITY_VIOLATION` and stop.

Prospective data remain inaccessible unless a later explicit unlock
certificate passes.

## 4. G2-E --- construct only the two surviving foresight targets

Use: \[ q_P=q\_{paraphrase},`\qquad `{=tex}q_R=q\_{removal}. \]

Generate fully date-grouped OOF predictions: \[
`\hat `{=tex}q_P=h_P(X,T),`\qquad `{=tex}`\hat `{=tex}q_R=h_R(X,T). \]

No downstream row may use a target predictor fitted on that forecast
date.

B6 remains frozen.

Primary residual formulation: \[
logit(r^{new})=logit(r^{B6})+`\beta`{=tex}\_P`\hat `{=tex}q_P+`\beta`{=tex}\_R`\hat `{=tex}q_R.
\]

Secondary preregistered interaction: \[
+`\beta`{=tex}\_{PR}`\hat `{=tex}q_P`\hat `{=tex}q_R. \]

Use strong regularization. Do not replace B6 with a new representation.

## 5. Frozen candidate set

Evaluate exactly:

-   M0: B6.
-   M1: B6 + predicted paraphrase credit.
-   M2: B6 + predicted removal credit.
-   M3: B6 + both predicted credits.
-   M4: B6 + both + their interaction (secondary).

Do not add architectures after observing M0--M4.

## 6. Matched controls

Also evaluate:

-   C-RAW: B6 + matched pre-outcome raw feature block used by the credit
    predictors.
-   C-DIR: B6 + direction-only features.
-   C-MKT: B6 + market-only features.
-   C-CONF: B6 + confidence/probability summaries.
-   C-SHUFFLE: B6 + appropriately shuffled pseudo-credit.
-   C-RANDOM-PROJ: B6 + matched-dimensional random projection of the
    same pre-outcome inputs.

These determine whether pseudo-credit is merely nonlinear feature
engineering.

## 7. TRAIN-only evaluation

Use only TRAIN date-grouped CV.

Report AUROC, AUPRC, Brier, ECE and paired deltas vs B6. Use 1,000
paired date-level bootstrap replicates plus block-bootstrap and
non-overlapping-date robustness where feasible.

A candidate advances only if: 1. AUROC delta vs B6 \> 0; 2. sign is
stable across folds; 3. Brier/ECE do not materially deteriorate; 4.
shuffled pseudo-credit does not reproduce; 5. direction-only does not
reproduce; 6. candidate is not obviously dominated by C-RAW; 7. no
leakage/cross-fitting violation.

Preferred strong evidence: \[ 95%CI(`\Delta `{=tex}AUROC)\>0. \]

If none passes → `DISTILLABLE_NOT_USEFUL`; stop before DEV.

## 8. Conditional information test

For every apparent survivor compare cross-fitted: \[
P(C=1`\mid `{=tex}B6,`\hat `{=tex}q) \] against \[
P(C=1`\mid `{=tex}B6). \]

Use frozen B6-score bins or a preregistered smooth conditional model.
Report incremental likelihood/deviance or equivalent predictive gain.

Do not claim conditional mutual information unless a justified estimator
is actually used.

## 9. G2-F red team

Only if G2-E passes.

Attack: - teacher necessity: shuffled/random/matched raw targets; - full
cross-fitting trace
(q\^H`\to `{=tex}h`\to`{=tex}`\hat `{=tex}q`\to `{=tex}r); - direction
mediation; - market mediation; - confidence mediation; - teacher-run
sensitivity; - agent-ID proxy; - temporal dependence; - small
preregistered regularization neighborhood; - outcome-label permutation.

Kill if shuffled credit matches it, matched raw features fully reproduce
it with equal/lower complexity, direction/market explains it, one
fold/agent drives it, cross-fitting fails, dependence-aware analyses
eliminate it, calibration materially worsens, or teacher-run choice
changes the sign.

Use `DISTILLABLE_BUT_REDUNDANT` or `AUDIT_FAIL` as appropriate.

## 10. Astra6 debate

For each survivor use fresh contexts: - Advocate; - Skeptic; -
Methodologist; - skeptical ACL/NAACL Reviewer; - Adjudicator.

Adjudicator returns `ADVANCE`, `TARGETED_ABLATION`, or `KILL`, plus
narrowest supported claim, strongest alternative explanation, decisive
evidence and remaining risk. It must not be instructed to seek a
positive result.

## 11. G2-G DEV unlock

DEV may unlock only if: - G2-E passes; - G2-F passes; - no leakage; -
matched raw features do not fully explain gain; -
direction/market/confidence do not fully explain gain; - temporal
robustness is acceptable; - fresh adjudicator returns `ADVANCE`.

Before DEV freeze \<=2 finalists, architecture, credit predictors,
hyperparameters, prompts, seeds, metrics, failure criteria, Git commit
and artifact hashes. Write `DEV_UNLOCK_CERTIFICATE.json`.

Otherwise → `GENERATION_2_COMPLETE_NO_DEV`.

## 12. One-time DEV

If unlocked, evaluate frozen finalists once. No post-DEV tuning.

Primary: \[ `\Delta `{=tex}AUROC\_{finalist-B6}. \]

Also report AUPRC, Brier, ECE, paired date bootstrap, block bootstrap,
non-overlap robustness, corrected B6 errors, newly introduced errors,
net corrections, wrong-majority recovery and false-consensus selective
risk where defined.

Preferred strong DEV signal: \[ 95%CI(`\Delta `{=tex}AUROC)\>0 \]
without material calibration deterioration.

Positive point estimate with CI crossing zero → `PARTIAL_ANOMALY`.

No gain → `DEV_INCREMENT_NOT_REPLICATED`.

## 13. Conditional Generation 3

Start G3 overnight only after `DEV_INCREMENT_FOUND`, or one narrowly
defined `PARTIAL_ANOMALY` if the G2 adjudicator explicitly authorizes a
single decisive replication.

G3 is not broad method search.

Consolidate whether the surviving mechanism is: - paraphrase/invariance
credit; - removal/evidence-dependence credit; - complementary
interaction; - generic low-dimensional nonlinear summary.

Use minimal ablations. Add no new pseudo-label families.

## 14. Hard cases and panel utility

Only after a valid G2/DEV survivor.

Define hard cases pre-outcome using frozen quantities such as B6 near
0.5, small within-panel reliability margin, high intervention
disagreement, or high confidence with behavioral instability. Never
define hard cases by realized correctness.

Evaluate panel-level false-consensus detection and correct-minority
recovery against majority, confidence weighting, B6 weighting and
finalist weighting.

Reliability remains primary; do not optimize PnL/alpha.

## 15. Prospective remains a separate court of last resort

Even successful G3 does not automatically expose the 807 prospective
outcomes.

Before access create and hash: - `PROSPECTIVE_PREREGISTRATION.md`; -
`PROSPECTIVE_UNLOCK_CERTIFICATE.json`.

Freeze one primary finalist (optionally one secondary), weights/recipes,
temporal boundaries, metrics, bootstrap, hard subsets, panel
aggregation, failure criteria, code commit and artifact hashes.

A fresh Astra6 red-team context must approve the certificate.

Only then may one chronological prospective evaluation occur. No tuning
from prospective outcomes.

## 16. Prospective success standard

The strongest result requires: \[
`\boxed{\text{Frozen pseudo-credit method} > B6}`{=tex} \] on untouched
prospective dates, with positive paired discrimination gain, no material
calibration loss, dependence-aware robustness, direction-only unable to
reproduce, matched raw baseline unable to fully reproduce, and no
leakage.

Only then may final synthesis consider `DISCOVERED`.

Positive but uncertain → `PARTIAL`.

Failure → `FALSIFIED_ON_PROSPECTIVE`.

## 17. No overnight rescue

Forbidden: - lowering gates; - metric shopping; - post-outcome subset
selection; - adding new target families after failure; - repeated
DEV/prospective evaluation; - seed selection by performance; - silent
row exclusion; - model-family switching; - horizon/label/split changes.

Save new ideas to `NEXT_GENERATION_IDEAS.md`; do not execute them
against consumed confirmatory data.

## 18. Complete ledger

Maintain `OVERNIGHT_EXPERIMENT_LEDGER.jsonl`.

Each record: hypothesis ID, parent, stage, timestamp, split touched,
features, target, student, hyperparameters, seed, LLM identity if used,
metrics, bootstrap, red-team status, verdict and artifact paths.

## 19. Required outputs

Create at minimum:

``` text
overnight/
├── OVERNIGHT_RUN_STATUS.json
├── OVERNIGHT_EXECUTIVE_SUMMARY.md
├── G2E_RESULTS.md
├── G2F_RED_TEAM.md
├── G2G_ADJUDICATION.md
├── MATCHED_BASELINE_ANALYSIS.md
├── CONDITIONAL_INFORMATION_ANALYSIS.md
├── TEMPORAL_ROBUSTNESS.md
├── MODEL_IDENTITY_AUDIT.json
├── OVERNIGHT_EXPERIMENT_LEDGER.jsonl
├── DEV_RESULTS.md                  # only if unlocked
├── G3_SYNTHESIS.md                 # only if authorized
├── PROSPECTIVE_PREREGISTRATION.md  # only if reached
├── PROSPECTIVE_RESULTS.md          # only if legally unlocked
├── PAPER_SAFE_CLAIMS.md
├── PAPER_UNSAFE_CLAIMS.md
└── MORNING_BRIEF.md
```

## 20. Morning brief

`MORNING_BRIEF.md` begins with exactly one: -
`HYPOTHESIS_STRONGLY_SUPPORTED` - `HYPOTHESIS_PARTIALLY_SUPPORTED` -
`DISTILLABLE_NOT_USEFUL` - `DISTILLABLE_BUT_REDUNDANT` -
`DEV_INCREMENT_NOT_REPLICATED` - `PROSPECTIVE_FAILED` - `AUDIT_FAIL` -
`RUN_INCOMPLETE`

Then report: furthest stage; whether DEV/prospective were touched; exact
candidate; B6 metrics; candidate metrics; paired deltas/CIs; matched raw
baseline; direction/shuffle controls; temporal robustness; red-team and
adjudicator verdicts; narrowest defensible claim; failures; whether the
result materially strengthens the paper; next experiment.

Do not hide negative evidence.

## 21. Paper-strength criterion

Do not assign an artificial paper score autonomously.

A material methodological upgrade requires evidence for: \[
`\text{stable hindsight component}`{=tex} `\to`{=tex}
`\text{pre-outcome distillable}`{=tex} `\to`{=tex}
`\text{incremental beyond B6}`{=tex} `\to`{=tex}
`\text{not reducible to direction/market/confidence}`{=tex} `\to`{=tex}
`\text{replication on untouched temporal data}`{=tex}. \]

If the chain breaks, state exactly where.

## 22. Paper-safe framing

If all gates including prospective pass:

> Outcome-conditioned hindsight supervision can identify
> intervention-specific reliability signals that are recoverable from
> pre-outcome behavioral responses and improve reliability estimation
> beyond the raw intervention trajectory.

If only TRAIN/DEV passes:

> We identify a candidate hindsight-supervised signal that is stable,
> pre-outcome-distillable, and incrementally useful on development data;
> prospective validation remains required.

If only distillability passes:

> Astra6 hindsight judgments for paraphrase and evidence-removal
> responses are reproducible and partially recoverable from pre-outcome
> observations, but their incremental reliability value remains
> unestablished.

Never claim recovered true beliefs, causal cognition, deployment-grade
trust, generalization beyond tested settings, or market alpha without
direct evidence.

## 23. Final Astra6 synthesis

Use a fresh Astra6 context to inspect all positive and negative
artifacts.

Ask it to identify exactly which arrows in: \[
`\text{stability}`{=tex}`\to`{=tex}`\text{distillability}`{=tex}`\to`{=tex}`\text{increment}`{=tex}`\to`{=tex}`\text{controls}`{=tex}`\to`{=tex}`\text{DEV}`{=tex}`\to`{=tex}`\text{prospective}`{=tex}
\] passed.

Required JSON:

``` json
{
  "final_status": "...",
  "furthest_validated_arrow": "...",
  "winning_method": "...",
  "b6_delta": {},
  "matched_raw_comparison": {},
  "direction_control": {},
  "temporal_robustness": {},
  "dev_status": "...",
  "prospective_status": "...",
  "paper_contribution": "...",
  "safe_claim": "...",
  "unsafe_claims": [],
  "recommended_next_action": "..."
}
```

## 24. Final instruction

Run autonomously through the pre-authorized gates. Complete all frozen
G2-E candidates and controls even if one fails, but stop when a frozen
stage gate says the current hypothesis has failed.

Do not invent a new method against consumed confirmatory data.

By morning, the objective is to know with substantially greater
confidence whether the G2-D anomaly supports a stronger scientific
story.

The highest-value positive result is: \[
`\boxed{B6+\widehat q_{Astra}>B6}`{=tex} \] with the gain surviving
matched raw features, direction, market, confidence, shuffled targets,
temporal dependence, adversarial review, and---only if properly
unlocked---untouched temporal validation.

Anything weaker must be reported as weaker.
