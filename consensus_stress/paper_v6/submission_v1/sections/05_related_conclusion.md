# 2 Related Work

## 2.1 Self-consistency and sampling-based uncertainty

Self-consistency, self-checking, and semantic-uncertainty methods estimate reliability from repeated outputs to the same input \citep{wang-etal-2022-self-consistency,manakul-etal-2023-selfcheckgpt,kuhn-etal-2023-semantic-uncertainty}. Confidence calibration, selective prediction, risk--coverage analysis, AURC, and conformal prediction instead use confidence or abstention policies to characterize error risk \citep{guo-etal-2017-calibration,geifman-elyaniv-2017-selective,angelopoulos-bates-2021-conformal}. These approaches generally treat repeated answers, confidence values, or output distributions as the primary uncertainty object.

CST-Bench evaluates an already-formed consensus panel with a fixed, natural-pair probe whose evidence direction opposes the item's gold label. The probe is pre-outcome and label-free: labels are withheld while consensus and probe features are computed. The resulting signal is therefore not unchanged-input disagreement or confidence alone, but the panel's response to decision-relevant, direction-gated evidence. The protocol does not assert that repeated sampling is uninformative; it tests whether a formed consensus responds in the prescribed direction before correctness is revealed. The natural-pair probe is thus a measurement instrument for predictive reliability, not merely another source of output variance.

The answer-prior control further separates the probe from a label-only heuristic. The consensus label alone produced AUROC 0.671 for Qwen3.5-4B and 0.634 for Ling-3.0-tiny, while a label-only baseline had AUROC 0.51. The Qwen natural-pair probe produced AUROC 0.943. These comparisons do not eliminate every interaction with answer priors, but show that the measurement is not adequately described by the consensus label alone.

## 2.2 Fact verification and evidence-based reasoning

Fact-verification and evidence-based reasoning benchmarks study whether systems select, assess, or generate claims in relation to supporting evidence \citep{thorne-etal-2018-fever,wadden-etal-2020-fact,schuster-etal-2021-get}. Their labels and evidence structures can provide settings for testing whether a model responds appropriately when evidential direction changes \citep{schuster-etal-2021-get,thorne-etal-2018-fever,kaushik-etal-2019-counterfactually-augmented}.

CST-Bench does not train a new verifier. It uses an existing task structure to assess the reliability of an already-formed consensus decision before the outcome is available. Its applicability depends on the dataset's axis and pair construction. On VitaminC, the frozen resource contains 300 natural pairs and 600 items, with paired evidence direction fixed to oppose each item's gold label. This makes the probe decision-relevant without requiring a newly generated counterfactual.

On BoolQ, the reverse operation used a negation prefix rather than natural counter-evidence. The resulting RS_q AUROC was 0.449 [0.308, 0.579]; the direction was reversed, and the permutation failed. FEVER supplied no usable natural pairs: its evidence-overlap Jaccard was 1.000, making the probe vacuous. These results identify a boundary condition for the measurement object itself. A natural pair must encode a usable evidence-direction contrast; surface reversal or complete overlap does not guarantee such a contrast.

CST-Bench should therefore not be read as a general fact-verification method. Its target is narrower: whether a consensus panel updates in the direction specified by a fixed, decision-relevant, gold-opposing natural-pair probe.

## 2.3 Multi-agent debate, consensus, and reliability auditing

Multi-agent debate and deliberation methods study how interaction changes answer formation, aggregation, or reasoning quality \citep{du-etal-2024-multiagent-debate,irving-etal-2018-ai-safety-debate}. Work on consensus reliability and model auditing examines whether outputs can be trusted under distribution shifts, structured tests, or targeted evaluations \citep{liang-etal-2022-helm,lin-etal-2022-truthfulqa,ovadia-etal-2019-uncertainty-shift}. Metamorphic and behavioral testing methods similarly use controlled transformations to expose systematic response patterns \citep{ribeiro-etal-2020-beyond,naik-etal-2018-stress}.

CST-Bench takes consensus as the object to audit, not as the intervention used to improve a final answer. The panel is formed first; the subsequent probe is outcome-firewalled and evaluates that fixed consensus's response to evidence with a prescribed direction. This differs from debate-based methods that seek to improve an answer through additional interaction and from generic invariance tests whose perturbations need not oppose the gold label.

The protocol links:

1. an existing consensus decision;
2. a direction-bearing natural-pair intervention; and
3. a pre-outcome reliability measurement.

The resulting score is intended to rank risk before the label is available, not to measure reasoning quality generally.

## 2.4 Stress testing, counterfactual probing, and adversarial evaluation

NLI stress tests, adversarial evaluations, controlled perturbations, and counterfactual or faithfulness probes use structured changes to diagnose model behavior \citep{naik-etal-2018-stress,glockner-etal-2018-breaking,kaushik-etal-2019-counterfactually-augmented}. These methods motivate treating a targeted intervention as behavioral measurement rather than as a new task score \citep{ribeiro-etal-2020-beyond,naik-etal-2018-stress}.

CST-Bench extends this perspective to a consensus panel with a stricter protocol boundary: the probe is fixed in advance, its direction is tied to the item's gold-opposing natural pair, and outcome labels are unavailable during feature construction. The direction is not cosmetic. The proposed interpretation is not that panels are rigid to counter-evidence in general, nor that natural-pair overlap alone explains the result.

A clean neutral placebo flipped at rate 0.038. A content-level matched placebo ranged from 0.51 to 0.56 and was direction-asymmetric: 0.92 for yes-answerers and 0.09 for no-answerers. These controls motivate a direction-gated account and show why placebo behavior and answer priors must be reported rather than treated as incidental.

Independent claim-only counter-evidence serves a different purpose. Its score,
\(S_{\text{ind}}\), is a mechanism probe rather than an independent predictor. The earlier W2 v1
protocol reached AUROC 0.983 with OOF increment +0.045 [0.015,0.084] (HC n=96,
metric n=96, 50 pairs). Under strict TARGET_SPEC, we retain two protocol-specific analyses
rather than pooling them. The larger cached analysis gives AUROC 0.699 (CI includes 0.5)
and OOF increment +0.027 [0.000,0.058] (cohort HC=96/wrong=8; \(S_{\text{ind}}\) n=72 over
42 pairs; OOF n=72, wrong=5). The separate strict 25-pair analysis gives AUROC
0.624 [0.286,0.856] and OOF increment +0.004 [−0.074,0.047] (cohort HC=47/wrong=3;
metric/OOF n=46 over 25 pairs). These protocol-specific results are not pooled into a
range. The analysis therefore tests the behavioral account without extending CST-Bench's
predictive claim.

## 2.5 Positioning

CST-Bench lies at the intersection of consensus auditing, evidence-sensitive behavioral testing, and pre-outcome reliability measurement. Its defining combination is:

1. an already-formed multi-agent consensus as the evaluation object;
2. a fixed natural-pair probe whose direction opposes the item's gold label;
3. a label-free, pre-outcome measurement of whether the panel updates toward that evidence direction; and
4. an explicit separation between predictive reliability results and mechanism-oriented stress tests.

This positioning is narrower than a claim about universal model rigidity. It does not require claiming that the protocol is the only way to audit consensus panels. The contribution is the operationalization and empirical evaluation of this particular direction-gated protocol.
# 6 Conclusion

## 6.1 Empirical phenomenon

CST-Bench identifies a pre-outcome, label-free regularity in VitaminC consensus panels. The natural-pair probe fixes an evidence direction against the item's gold label. The natural mirror flipped correct consensus at 0.902 and wrong consensus at 0.075. Corresponding rates were 0.843 and 0.095 for Qwen3.5-4B and 0.703 and 0.029 for Ling-3.0-tiny.

Using \(RS_q=-BF_q\) as the primary predictive score, AUROC for identifying wrong high-confidence consensus decisions was 0.943 [0.924, 0.960] for Qwen3.5-4B, with Risk@80 of 0.846 [0.638, 0.981]. Ling-3.0-tiny AUROC was 0.896 [0.873, 0.916], with Risk@80 of 0.422. The gpt-6-astra single-point evaluation yielded AUROC 0.969 [0.935, 0.995].

The Qwen evaluation included 567 high-confidence consensus decisions and 65 wrong decisions; the Ling evaluation included 574 high-confidence consensus decisions; and the gpt-6-astra evaluation included 96 high-confidence consensus decisions and 8 wrong decisions.

The natural-pair property is further supported by \(S_{\text{pair}}\), computed from the two original answers. It reconstructed the reverse-axis ranking with Spearman correlation 0.998 and retained approximately 98.7% and 97.0% of the \(RS_q\) ranking. This is a property of the natural-pair construction, not evidence that independent counter-evidence is itself a predictor.

## 6.2 Protocol contribution

CST-Bench specifies a reproducible measurement procedure with 5 consensus calls, 10 main probe calls, and 10 auxiliary calls. It uses frozen gates, an outcome firewall, preregistration, and pair-grouped confidence intervals. The VitaminC resource contains 300 frozen natural pairs and 600 items.

A single cross-panel portability check applying the Qwen-fixed procedure to Ling yielded AUROC 0.723 [0.682, 0.765]. Item-level Spearman correlation between Qwen and Ling \(RS_q\) values was 0.496. This check is nontrivial but imperfect; it is not evidence of model-independent or out-of-domain generalization.

## 6.3 Boundaries and honest negatives

The protocol is axis-native rather than universally portable. BoolQ produced reversed RS_q AUROC of 0.449 [0.308, 0.579] using a negation-prefix reverse; the associated permutation failed. FEVER had no usable natural pairs because evidence-overlap Jaccard was 1.000. The S&P500 evaluation was an as-of sequential stress test with a null result and supports no alpha claim.

The controls also constrain interpretation. Answer-prior AUROCs were 0.671 for Qwen3.5-4B and 0.634 for Ling-3.0-tiny, compared with label-only AUROC 0.51. The clean neutral placebo flip rate was 0.038; the content-level matched placebo ranged from 0.51 to 0.56, with rates of 0.92 for yes-answerers and 0.09 for no-answerers. These results support reporting direction and placebo asymmetry explicitly, but do not support reducing the signal to generic perturbation sensitivity.

The Round10 2x2 analysis provided mechanism-oriented descriptive evidence, not an additional independent prediction benchmark. It used 16 generation + 2 audit + 160 inference calls (178 logical calls); 145/160 inference rows were valid, generation parsing was valid for 10/16 items, and 6/16 were format-invalid but recorded and audited. The overall CONTRADICT-minus-AGREE direction contrast was +0.44 [0.24, 0.65]. The as-assigned independent-CONTRADICT cell flipped wrong consensus in 35/37 cases; after direction auditing, the clean subset was 30/32 across 7 clean items. The post-hoc Probe1 extension gives an as-assigned total of 44/46, adds 2 items / 9 agent rows, is post-hoc, and relies on one batched direction audit. Within the direction-stratified comparison, the natural mirror was numerically similar to the direction-clean independent condition; this does not establish equivalence. The direction-clean construction comparison had \(n=3\) items, so a small residual effect was not ruled out. This comparison is not a causal or mediation analysis, an AUROC result, or a generalization test.

The selective-responsiveness score \(E_{\text{sel}}\) was dropped in Round9. The graph study was also dropped. Neither analysis is part of the final contribution.

## 6.4 Deepest bounded conclusion

The strongest supported conclusion is a direction-gated behavioral regularity: under the frozen CST-Bench protocol, a gold-opposing natural-pair probe can expose which consensus decisions are unreliable before outcome access.

The evidence does not establish rigidity to counter-evidence in general, a universal mechanism of LLM failure, or an independent-counter-evidence predictor. The mechanism-oriented evidence is consistent with a direction-sensitive interpretation, but does not justify a causal or mediation claim. The small clean comparison cell leaves a small residual effect unresolved.

CST-Bench should therefore be interpreted as a reliability-measurement protocol evaluated under the frozen VitaminC natural-pair design, together with a bounded mechanism probe. Its predictive result comes from the pre-outcome natural-pair score; its mechanism result comes from direction-controlled behavioral comparisons. The two claims should not be merged.
# 7 Reproducibility and Artifact Inventory

This section inventories the repository artifacts that accompany the submission.
It distinguishes frozen inputs, pre-outcome features, outcome labels, model and
run records, analysis outputs, and source/hash records. It does not claim that
every listed artifact is reproduced inside the PDF; the paths below identify the
authoritative repository locations.

## 7.1 Frozen data artifacts

The repository preserves the VitaminC frozen manifest containing 300 natural
pairs and 600 items at `consensus_stress/round3/selection_manifest.json`. Pair
ordering is fixed; a changed ordering constitutes a new artifact rather than a
reproduction of the frozen run.

Labels remain separate from pre-outcome features. The label ledger is stored at
`consensus_stress/round3/labels_ledger.json`, and pre-outcome feature records at
`consensus_stress/round3/preoutcome_features.jsonl`. The artifact record
identifies every field available before outcome access and records that labels
are merged only after those features are frozen.

SHA-256 hashes for manifests, ledgers, feature files, and preregistration
materials are taken from stored artifacts, not substituted with hashes from
regenerated files.

## 7.2 Protocol and preregistration map

The call-level CST-Bench record contains:

- 5 consensus calls;
- 10 main probe calls;
- 10 auxiliary calls;
- frozen gates;
- the outcome firewall;
- preregistration procedures; and
- pair-grouped confidence intervals.

Pilot and main preregistration materials are under
`consensus_stress/round2/phase2_pilot/` and
`consensus_stress/round3/preregistration.md`. The Ling contract adaptation is
documented under `consensus_stress/round4/`, and the cross-model analysis is at
`consensus_stress/round4/analysis/ling_adapted_crossmodel.md`.

The registry records the main protocol as `cs-paper-vitaminc-20260913` and the
Ling adaptation as `cs-round4-ling-adapted-crossmodel-20260913`; the registry
is stored at `consensus_stress/registry.yaml`. A protocol-to-artifact mapping
connects each reported analysis to its manifest, preregistration, run records,
pre-outcome feature file, analysis-script directory, and hash file, while
separating frozen inputs from files generated after outcome labels are merged.

## 7.3 Model and run records

The main VitaminC panels are Qwen3.5-4B and Ling-3.0-tiny. The gpt-6-astra
result is identified as a single-point evaluation; no additional model or run
counts are inferred. Large-model records are stored under
`consensus_stress/round6/large_model/`.

Analysis scripts are identified through relevant round-specific script
directories and artifact locations, without introducing script names absent from
the frozen package. Model, contract, run, and sampling records are listed
separately so that procedural transfer is not confused with item-level score
agreement.

## 7.4 Independent counter-evidence artifacts

Independent counter-evidence materials are stored under
`consensus_stress/round7/ind_ce/`. The W2 v1 record and its strict companion
files include `preregistration.md`, `artifact_hashes.json`,
`frozen_hashes.json`, `records.jsonl`, and `preoutcome_features.jsonl`; the
same directory also stores `strict_preregistration.md`, `strict_records.jsonl`,
and `strict_preoutcome_features.jsonl`. The parallel strict package is under
`consensus_stress/round7/ind_ce_strict/` and contains its own `preregistration.md`,
`artifact_hashes.json`, `records.jsonl`, and `preoutcome_features.jsonl`.

Round9 Probe1 results are recorded at
`consensus_stress/round9_mechanism/probe1_results.md`, and the Probe1 decision
record at `consensus_stress/round9_mechanism/probe1_decision.md`. The clean
independent result and Probe1-inclusive result remain separate records. All
independent counter-evidence results are marked as mechanism evidence and are
not combined with the natural-pair score to claim independent prediction.

## 7.5 Statistical reporting anchors

The manuscript reports the following fixed predictive measurements without
changing precision:

- Qwen3.5-4B AUROC: 0.943 [0.924, 0.960];
- Qwen3.5-4B Risk@80: 0.846 [0.638, 0.981];
- Ling-3.0-tiny AUROC: 0.896 [0.873, 0.916];
- Ling-3.0-tiny Risk@80: 0.422; and
- gpt-6-astra single-point AUROC: 0.969 [0.935, 0.995].

The natural-mirror reporting anchors are overall correct-consensus and
wrong-consensus flip rates of 0.902 and 0.075, respectively, with Qwen rates of
0.843 and 0.095 and Ling rates of 0.703 and 0.029.

The natural-pair reconstruction reports Spearman correlation
\(S_{\text{pair}}\) = 0.998 and approximately 98.7% and 97.0% ranking
retention. This is a natural-pair property check, not an independent-prediction
analysis.

Separate control and boundary records contain:

- answer-prior AUROC 0.671 for Qwen3.5-4B;
- answer-prior AUROC 0.634 for Ling-3.0-tiny;
- label-only AUROC 0.51;
- Qwen probe AUROC 0.943;
- clean neutral placebo flip rate 0.038;
- content-level matched placebo range 0.51--0.56;
- yes-answerer and no-answerer rates of 0.92 and 0.09;
- BoolQ AUROC 0.449 [0.308, 0.579];
- FEVER evidence-overlap Jaccard 1.000; and
- the null S&P500 as-of sequential stress test, which supports no alpha claim.

## 7.6 Mechanism-versus-prediction audit

The artifact audit separates predictive reliability measurements from mechanism
evidence. Natural-pair AUROC and Risk@80 results are predictive reliability
measurements. Round10 is direction-dominant mechanism-oriented descriptive evidence and records 16
items, 178 logical calls, direction contrast +0.44 [0.24, 0.65], as-assigned independent-CONTRADICT flips of 35/37; direction-audited subset 30/32
across 7 clean items; post-hoc Probe1 as-assigned total 44/46; and a direction-clean
construction comparison with \(n=3\) items. Within that small direction-stratified
comparison, the natural mirror is approximately the direction-clean independent condition; the small direction-clean construction cell does not rule out a small residual
contrast, and the comparison is not causal or mediation evidence.

The independent claim-only record reports protocol-specific W2 v1 and strict
TARGET_SPEC estimates with cohort and version labels. \(S_{\text{ind}}\) is a
mechanism probe, not an independent predictor. \(E_{\text{sel}}\) is marked as
dropped in Round9, and the graph study is marked as dropped; neither supports
C1, C2, or C3.

## 7.7 Source map and hash audit

The source map is anchored to the Round7 paper draft at
`consensus_stress/round7/paper/naacl_draft_v5_astra.md`, the Round8 theory
synthesis at `consensus_stress/round8_theory/grand_theory_synthesis.md`, and the
Round9 reframing at
`consensus_stress/round9_mechanism/paper_scientific_question_v2.md`. It also
identifies the Round9 Probe1 results and decision records.

Each source-map entry distinguishes:

- frozen data and manifests;
- preregistration files;
- pre-outcome features;
- post-outcome labels;
- model and run records;
- analysis scripts; and
- stored hashes.

The hash audit covers frozen manifests, the labels ledger, pre-outcome features,
records, preregistrations, and relevant analysis files. It preserves the
SHA-256 pair-ordering convention. The outcome-firewall merge is inspectable
through the order: (1) freeze the manifest; (2) compute pre-outcome features;
(3) hash the artifacts; and (4) merge labels for evaluation.

This organization supports reproduction of the reported reliability
measurements, direction-gated mechanism checks, and negative results without
expanding claims beyond the frozen evidence. The central contribution remains
an outcome-blind, label-free scoring protocol conditional on a fixed offline
gold-conditioned natural-pair resource, together with a bounded direction-gated
behavioral interpretation.

The distinction between predictive reliability measurement and mechanism
evidence is preserved throughout the manuscript and artifact records. No
causal, mediation, alpha, universal-rigidity, or universal-SOTA claim is made.
