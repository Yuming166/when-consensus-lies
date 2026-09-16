# Live citation map — submission_v1

**Status.** This is the current citation-command map for `consensus_stress/paper_v6/submission_v1/manuscript.md`; it is regenerated from the canonical manuscript and does not add literature.

## Audit counts

- Live `\citep{...}` commands: **10**.
- Key references in those commands: **25**; unique keys: **18**.
- Current manuscript `[CITE]` placeholders: **0**.
- `submission_v1/references.bib`: **22 entries; 22 source-verified; 0 unverified**.
- Missing citation keys: **[]**; duplicate BibTeX keys: **[]**.

## Live slot map

| Slot | Current line | Section | Key(s) | Cited sentence |
|---|---:|---|---|---|
| C01 | 30 | 1.1 Motivation: multi-agent consensus is unreliable | `du-etal-2024-multiagent-debate` | Multi-agent LLM panels—several personas sampled from one or more models that read shared evidence and vote—are a common recipe for fact verification and reasoning \citep{du-etal-2024-multiagent-debate}. |
| C02 | 187 | 2.1 Self-consistency and sampling-based uncertainty | `wang-etal-2022-self-consistency`, `manakul-etal-2023-selfcheckgpt`, `kuhn-etal-2023-semantic-uncertainty` | Self-consistency, self-checking, and semantic-uncertainty methods estimate reliability from repeated outputs to the same input \citep{wang-etal-2022-self-consistency,manakul-etal-2023-selfcheckgpt,kuhn-etal-2023-semantic-uncertainty}. |
| C03 | 187 | 2.1 Self-consistency and sampling-based uncertainty | `guo-etal-2017-calibration`, `geifman-elyaniv-2017-selective`, `angelopoulos-bates-2021-conformal` | Confidence calibration, selective prediction, risk--coverage analysis, AURC, and conformal prediction instead use confidence or abstention policies to characterize error risk \citep{guo-etal-2017-calibration,geifman-elyaniv-2017-selective,angelopoulos-bates-2021-conformal}. |
| C04 | 195 | 2.2 Fact verification and evidence-based reasoning | `thorne-etal-2018-fever`, `wadden-etal-2020-fact`, `schuster-etal-2021-get` | Fact-verification and evidence-based reasoning benchmarks study whether systems select, assess, or generate claims in relation to supporting evidence \citep{thorne-etal-2018-fever,wadden-etal-2020-fact,schuster-etal-2021-get}. |
| C05 | 195 | 2.2 Fact verification and evidence-based reasoning | `schuster-etal-2021-get`, `thorne-etal-2018-fever`, `kaushik-etal-2019-counterfactually-augmented` | Their labels and evidence structures can provide settings for testing whether a model responds appropriately when evidential direction changes \citep{schuster-etal-2021-get,thorne-etal-2018-fever,kaushik-etal-2019-counterfactually-augmented}. |
| C06 | 205 | 2.3 Multi-agent debate, consensus, and reliability auditing | `du-etal-2024-multiagent-debate`, `irving-etal-2018-ai-safety-debate` | Multi-agent debate and deliberation methods study how interaction changes answer formation, aggregation, or reasoning quality \citep{du-etal-2024-multiagent-debate,irving-etal-2018-ai-safety-debate}. |
| C07 | 205 | 2.3 Multi-agent debate, consensus, and reliability auditing | `liang-etal-2022-helm`, `lin-etal-2022-truthfulqa`, `ovadia-etal-2019-uncertainty-shift` | Work on consensus reliability and model auditing examines whether outputs can be trusted under distribution shifts, structured tests, or targeted evaluations \citep{liang-etal-2022-helm,lin-etal-2022-truthfulqa,ovadia-etal-2019-uncertainty-shift}. |
| C08 | 205 | 2.3 Multi-agent debate, consensus, and reliability auditing | `ribeiro-etal-2020-beyond`, `naik-etal-2018-stress` | Metamorphic and behavioral testing methods similarly use controlled transformations to expose systematic response patterns \citep{ribeiro-etal-2020-beyond,naik-etal-2018-stress}. |
| C09 | 219 | 2.4 Stress testing, counterfactual probing, and adversarial evaluation | `naik-etal-2018-stress`, `glockner-etal-2018-breaking`, `kaushik-etal-2019-counterfactually-augmented` | NLI stress tests, adversarial evaluations, controlled perturbations, and counterfactual or faithfulness probes use structured changes to diagnose model behavior \citep{naik-etal-2018-stress,glockner-etal-2018-breaking,kaushik-etal-2019-counterfactually-augmented}. |
| C10 | 219 | 2.4 Stress testing, counterfactual probing, and adversarial evaluation | `ribeiro-etal-2020-beyond`, `naik-etal-2018-stress` | These methods motivate treating a targeted intervention as behavioral measurement rather than as a new task score \citep{ribeiro-etal-2020-beyond,naik-etal-2018-stress}. |

## Historical provenance (not live)

- The ten-placeholder extraction under `consensus_stress/paper_v6/references/citation_contexts.json` is retained as historical provenance for the earlier draft and private-relay literature-candidate request.
- The stored response in `submission_v1/relay_candidates.json` is literature candidate generation only. Its original context path is explicitly marked `historical_pre_reconcile_snapshot`; it was not replayed against the reconciled manuscript.
- No bibliography record is added by this live-map refresh; source verification remains represented in `citation_validation.json` and `references.bib`.
