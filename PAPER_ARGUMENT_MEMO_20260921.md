# Paper argument memo: CST, S&P boundary, and PECR

Date: 2026-09-21
Purpose: test whether the three evidence lines form one coherent paper argument before writing `main.tex`.

## 1. What CST measures

CST measures whether an already-formed multi-agent decision responds to controlled evidence interventions in the expected direction. The observable is not hidden chain-of-thought and not a claimed latent belief. It is an outcome-blind response profile: what changes when evidence is paraphrased, removed, reversed, or replaced, with evidence identity and intervention semantics maintained by the environment.

The strongest CST evidence is the expected-response faithfulness profile. On the frozen VitaminC cohorts, `RS_q=-BF_q` ranked high-consensus errors beyond confidence, agreement, and frozen provenance baselines, with placebo and permutation controls. Round10 sharpened the mechanism: the large effect is directional. Consensus-opposing independent counter-evidence flipped wrong consensus at about 0.95, while consensus-agreeing or no-new-information evidence rarely flipped it. The near-duplicate natural mirror does not provide an independent overlap/rigidity mechanism after direction is controlled.

Thus CST's paper-safe contribution is an intervention-tested, label-free measurement of directional response fidelity—not a claim to recover an internal belief state.

## 2. Why Round10 matters

Generic sensitivity asks whether the answer changes. That is insufficient: a model can flip in response to irrelevant, agreeing, or malformed evidence. Round10 shows why direction must be part of the observable. The relevant question is whether the response moves in the direction implied by the intervention. This is the conceptual bridge from `input change -> output change` to `known semantic intervention -> expected output response`.

The lesson is not that every directional response is reliable. It is that a directionless flip rate is under-specified. A valid reliability measurement needs an independently determined expected response and a scorer that checks that response.

## 3. Why the S&P 500 negative boundary belongs in the paper

The bounded S&P 500 branch is a stress test of portability, not an unrelated appendix. It passed a structural-hardness gate: static reliability was much lower than the earlier benchmark and wrong-majority panels were common. But the later B8 behavioral-state candidate did not beat the simpler B6 raw trajectory on held-out DEV, with B8-B6 AUROC difference -0.0143 and a confidence interval spanning zero. The operational decision was `KEEP_B6_NO_ESCALATION`; teacher and untouched prospective evaluation were not authorized.

This negative branch protects the paper from overclaiming. Intervention response is not automatically a transferable reliability signal, and a harder sequential market setting can expose a mismatch between a useful behavioral measurement and a useful forecast feature. The paper should say that the negative result motivated a narrower, executable-program benchmark rather than pretending that all domains validated the same method.

## 4. How PECR extends the same principle

PECR uses the same conceptual move in a domain where the expected response is mechanically executable. FinQA supplies a gold reasoning program. For a valid operand intervention, the program can be rerun to produce the transformed gold answer. The model is therefore evaluated on:

`known program transformation -> corresponding answer transformation`.

This is stronger than a generic flip. Full CEF aggregates whether the model answers multiple transformed worlds correctly; S2 uses two frozen probes as a sparse approximation. Across Qwen3.5-4B and Ling-3.0-tiny, full CEF and S2 predict original correctness on source-disjoint TRAIN cohorts and on a frozen eligible, source-deduplicated DEV cohort. This does not mean the model has high absolute counterfactual accuracy or that CEF is causal; it means the pattern of executable test success contains diagnostic information about whether the original answer is correct.

## 5. Unified paper thesis

The coherent thesis is:

> Reliability evaluation should test expected behavior under executable, outcome-blind interventions rather than treating arbitrary output sensitivity or self-reported confidence as sufficient. CST demonstrates the directional-response principle in evidence interventions; the S&P branch marks the portability boundary; PECR instantiates the principle with gold-executable financial programs and obtains a reproducible sparse correctness diagnostic.

This is a methods-and-boundaries paper, not a universal reliability theorem. The S&P negative result is useful because it tells the reader where the general principle does not yet yield a validated predictor. PECR is the strongest positive instantiation because the expected transformation is externally executable and the sparse diagnostic survives cross-model and eligible DEV validation.

## 6. Writing order

1. Define outcome-blind expected-response testing.
2. Show CST as the general evidence-intervention case, with Round10's directional correction.
3. Present S&P as a bounded negative portability result.
4. Introduce PECR as the clean executable-program instantiation.
5. Report eligibility and absolute-ability limits before the positive AUROC table.
6. Close with strong-baseline and second-benchmark work as pending, not implied evidence.
