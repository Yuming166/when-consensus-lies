# When Counterfactuals Mislead: Construct Validity in Perturbation-Based Reliability Tests

**Working manuscript draft — 27 September 2026**
**Status:** synthesis draft for collaborator review; not submission-ready.

## Abstract

Perturbation-based reliability methods infer model reliability from answer changes across altered inputs. Such scores are meaningful only when the intervention itself has construct validity: irrelevant changes should be inert, while evidence-changing interventions should produce interpretable effects. We connect two studies of this measurement problem. In the Consensus Stress Test (CST), an exploratory search over placebo constructions on a reused 50-item cohort did not produce an inert placebo: among jointly parseable cases, both distractor placebos changed answers on 59.4% of cases, compared with no A/A changes; only 47.0% of all requested responses were parser-valid. CST therefore provides a cautionary construct-boundary case, not evidence of error prediction. We then evaluate Program-Executable Counterfactual Reliability (PECR), a program-conditioned relation score for numerical reasoning. In an earlier selected FinQA test subset, relation risk achieved error AUROC 0.734 (95% CI 0.662–0.799), but its advantage over a fixed-majority-direction baseline was uncertain (+0.050; 95% CI −0.009 to +0.122), with outcome-associated unscorable cases. In a later 565-item collection, the paired-support AUROC was 0.717 for relation-augmented risk versus 0.692 for graph-only risk (difference +0.026; 95% CI −0.013 to +0.065). The analysis has post-collection label-rule and implementation-chronology limitations. A post-hoc repair study yielded no PECR-triggered corrections. The results motivate construct-validity checks as prerequisites for perturbation-based reliability claims, but do not establish robust PECR superiority, effective repair, or a shared CST–PECR mechanism.

## 1. Introduction

A model's response to a counterfactual prompt is often treated as a measurement of its reliability. That interpretation requires more than observing a change. The transformed input must preserve the intended task, manipulate the intended evidence, and avoid introducing irrelevant cues that independently alter behavior. Otherwise, the score may measure prompt sensitivity rather than reasoning reliability.

We examine this issue through two related but distinct projects. CST tests whether a model's answer changes under evidence manipulations, including placebo changes that should not alter the answer. PECR uses executable numerical programs to construct transformed worlds and scores whether model answer movements follow expected numerical directions. The projects share a methodological concern—intervention validity—but they do not share an empirically established mechanism, and CST does not independently validate PECR.

Our contribution is a bounded empirical account of what happens when construct-validity checks are made explicit. CST's latest placebo method search failed its inertness objective under limited parser coverage. PECR exhibits promising error-ranking point estimates in selected cohorts, but its gains against strong baselines remain uncertain and its construction is program-conditioned. A post-hoc end-to-end repair experiment did not demonstrate a PECR repair benefit. We therefore frame the work as a measurement and construct-validity study rather than a claim of stable reliability improvement.

## 2. Conceptual framework

Let an intervention transform an input from world A to world B. A reliability interpretation requires (i) **semantic validity**—the transformation changes only the intended evidence; (ii) **directional validity**—the expected response relation follows from that evidence; and (iii) **placebo inertness**—a transformation that leaves relevant evidence unchanged rarely changes the response. These conditions are logically prior to ranking errors or claiming repair utility.

CST and PECR instantiate this framework differently. CST uses natural-language evidence and placebo controls; PECR uses benchmark programs and numerical transformations. The shared framework is an analytical lens, not evidence that either method measures a universal latent reliability trait.

## 3. CST: placebo inertness as a necessary control

### 3.1 Design and evidence status

The latest CST experiment reported here is Round-8 E1, a method-search study on a reused VitaminC cohort of 50 questions. It compared a fresh baseline, an A/A condition, two distractor placebo candidates (C1a and C1b), and a natural opposing-evidence condition (CE), across five personas. The analysis used a strict frozen JSON schema. The experiment is exploratory, not an independent confirmation, and its outcome is answer flipping—not correctness or error prediction.

### 3.2 Results

Of 1,250 attempted requests, 587 (47.0%) were parser-valid. On common support, A/A produced 0 flips among 149 cases. C1a and C1b each produced 41 flips among 69 jointly supported cases (59.4%; source-pair bootstrap 95% CI 50.7%–69.7%). CE produced 92 flips among 132 supported cases (69.7%; 95% CI 51.5%–86.2%). Placebo coverage was especially limited: each candidate had only 69 complete cases, 46.3% of the 149 baseline/A/A-supported cases. The two placebo candidates tied on their common support; the frozen tie rule selected C1a, not evidence of its superiority.

The high distractor-placebo flip rate contradicts the intended inertness criterion in this sample. Moreover, 663 requests failed schema validation; the parser was not relaxed post hoc and no requests were rerun. The estimates therefore describe a small, selected, parseable subset and should not be generalized to the full request set. The observed flips do not imply an increase in errors, because correctness was not the outcome.

### 3.3 Earlier CST evidence and interpretation

Earlier CST stages do not reverse this conclusion. The BoolQ E3 gate reported AUROC 0.363 (95% CI 0.102–0.611), a reverse-direction point estimate with an interval spanning chance; the prespecified gate failed. An earlier strict pilot had a placebo flip rate of 0.5141 and only three high-consensus incorrect cases, with independent-score AUROC 0.624 (95% CI 0.286–0.856). Thus, across the reported CST evidence, the core placebo control has not been shown inert and reliable error ranking has not been established.

These results make CST useful here as a construct-validity boundary: an intervention-based reliability score should not be interpreted until placebo stability, parser coverage, and manipulation semantics pass prespecified checks. They do not support a claim that the CST method is validated or that it shares a mechanism with PECR.

## 4. PECR: program-conditioned numerical relation scoring

### 4.1 Method and information boundary

For each selected numerical reasoning question, PECR uses a gold executable program and an operand-to-source mapping to construct counterfactual numerical worlds. The program is run on transformed operands to determine expected answer directions. The relation score then quantifies whether the model's responses across worlds accord with those expected directions.

This design is **program-conditioned**. Although the scoring rule can avoid reading the numeric gold answer, construction and expected directions depend on benchmark-provided executable information and transformed program results. We therefore call it numeric-answer-blind scoring, not end-to-end oracle-free intervention generation.

### 4.2 Earlier FinQA selected test result

In an earlier fixed selected FinQA TEST subset, 139 of 157 items were scorable and 94 of the 139 were labeled errors. Relation risk achieved error AUROC 0.7337 (95% CI 0.6615–0.7991) and AUPRC 0.8164. The AUROC increment over a fixed-majority-direction baseline was +0.0500 (95% CI −0.0092 to +0.1215), so superiority over that control was not established. All 18 items that failed numeric scoring were subsequently labeled incorrect, creating outcome-associated missingness. The estimate is thus restricted to a selected scorable cohort and cannot be treated as an unbiased full-manifest result.

Post-hoc construction and answer reviews are descriptive and do not establish construct validity. In a selected sensitivity excluding 14 constructions jointly judged invalid, the relation-versus-majority AUROC gap fell to +0.0087 (95% CI −0.0187 to +0.0485). Review provenance and label chronology remain qualified in the archived analysis. These limitations are retained rather than resolved by the favorable point estimate.

### 4.3 Later 565-item collection

A later collection targeted 565 questions with two worlds each (1,130 request slots). The collection seal records 1,129 HTTP-200 terminal responses; slot 608, the mutated-world request, remains unknown and was not retried. There were 860 parser-valid and 269 invalid responses. A completed post-collection analysis reports 565 unique score rows and project-specific labels for 412 items; 153 did not yield a valid numeric original answer and were not assigned a correctness label under that rule.

On the primary paired relation-score support (357 items from 108 source groups; 312 errors and 45 correct), relation-augmented risk achieved AUROC 0.7171, compared with 0.6919 for graph-only risk. The paired difference was +0.0259 (source-group bootstrap 95% CI −0.0135 to +0.0651); the AUPRC difference was +0.0132 (95% CI −0.0008 to +0.0292). The secondary full-coverage comparison on the 412 labeled items yielded AUROC 0.7049 for PECR and 0.6864 for graph-only, a difference of +0.0193 (95% CI −0.0133 to +0.0532). Both intervals include zero. These results are directionally compatible with an incremental signal, but do not establish a reliable advantage.

The holdout analysis is not a clean preregistered confirmation. The correctness rule was a project-specific free-text numeric comparison, not the official FinQA execution scorer. An earlier implementation attempt read target answers before halting on a schema mismatch; the exact read time lacks an independent event timestamp. A later implementation correction to parser lookup and label polarity followed that reveal. The reporting correction states that rows and metrics were not changed, but the chronology limits confirmatory interpretation. In addition, the 153 unlabeled cases and the 18 missing original answers labeled incorrect in the earlier analysis show that scorable-cohort selection is consequential.

## 5. End-to-end repair and repairability-aware selection

A post-hoc end-to-end repair follow-up applied a nominal 85-trigger budget per policy. Under intention-to-treat scoring, invalid repairs were no-ops. PECR triggered 85 cases, 83 were labeled, 78 repairs were valid, and it corrected zero errors while causing zero harms (net gain 0). The graph policy made one correction and no harm; confidence made three corrections and one harm; random selection made three corrections and four harms. Source-group intervals were wide, and differences between policies crossed zero. This study provides no evidence that PECR selection improves repair outcomes.

A separate OOF development-validation compared four selection rules at 359 selections each. Net gain per selected budget was +0.28 percentage points for PECR risk only (95% CI −1.39 to +1.95), −0.28 for PECR×repairability (−1.67 to +1.11), +0.28 for PECR×model-score disagreement (−2.23 to +2.79), and +1.39 for combined selection with abstention (−0.84 to +3.62). The combined policy's paired difference versus PECR-risk-only was +1.09 points (−1.40 to +3.90). Because this split was used for development, and all intervals include zero, these are exploratory signals rather than confirmation of stable gains.

## 6. Discussion

Across CST and PECR, the strongest common conclusion is methodological. Perturbation scores are interpretable only when their transformations are valid and their controls behave as intended. CST makes this point through a failed placebo-inertness check and substantial parser attrition. PECR operationalizes expected directions more tightly through executable programs, but that strength comes with an oracle boundary: benchmark program information conditions construction. Empirical error-ranking gains are positive in several comparisons, yet uncertainty remains against strong baselines, and the repair study is null for PECR-triggered corrections.

The evidence does not justify merging CST and PECR into one validated mechanism. Instead, CST motivates stringent intervention and placebo checks, while PECR is a domain-specific, program-conditioned scoring proposal whose incremental value requires cleaner independent confirmation and better handling of missing outcomes. A favorable story should therefore center on measurement validity and transparent boundaries, not on guaranteed improvement.

## 7. Limitations and next steps

The studies use different tasks, datasets, models, interventions, and outcomes; cross-study synthesis is conceptual. CST E1 reuses a development cohort and has low valid-response coverage. PECR analyses have selected/scorable cohorts, program-conditioned construction, post-hoc review and chronology limitations, and project-specific labeling. The 565-item paired interval crosses zero, and PECR repair produced no corrections. No result establishes deployment utility, cross-model generalization, or a shared latent reliability construct.

Before submission, the team should (i) independently reproduce every estimate from authorized source artifacts; (ii) audit benchmark scoring and the holdout chronology; (iii) pre-register a new source-group-disjoint PECR confirmation with an official or independently adjudicated outcome rule; (iv) conduct a separately powered CST placebo-equivalence study with a compact schema and prespecified coverage threshold; and (v) complete citation, ethics, data-license, and venue-format checks. No tuning should be conducted on the reported holdout results.

## References to complete

Use the verified references in the repository's existing `references.bib`, including the FinQA and ConvFinQA benchmark papers and cited counterfactual/stress-testing literature. This working draft intentionally does not introduce new bibliographic entries; reference-to-claim verification remains a handoff task.
