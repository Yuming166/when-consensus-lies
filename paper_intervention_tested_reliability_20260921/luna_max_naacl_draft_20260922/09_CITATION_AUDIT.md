# Citation audit for the reviewed NAACL draft

Draft under review:

```text
08_NAACL_FIRST_DRAFT_REVIEWED.md
```

There are 14 remaining `[CITATION NEEDED]` placeholders. They are intentionally not replaced with guessed references. The following map records the minimum source families that should be verified before submission.

| # | Manuscript claim | Candidate primary source family | Action |
|---:|---|---|---|
| 1 | Confidence and agreement are common reliability signals | calibration of modern neural networks; LM confidence/knowledge estimation | Verify one calibration source and one LM-specific confidence source if both claims remain. |
| 2 | FinQA provides executable financial numerical reasoning programs | canonical FinQA dataset paper | Verify dataset citation and program/execution description. |
| 3 | ConvFinQA contains conversational financial numerical reasoning | canonical ConvFinQA dataset paper | Verify benchmark citation and current-turn task description. |
| 4 | VitaminC cohorts motivate CST | canonical VitaminC fact-verification benchmark paper | Verify dataset citation; the CST numerical results themselves come from internal frozen artifacts. |
| 5 | PECR is first evaluated on FinQA | canonical FinQA paper | Reuse the verified FinQA citation rather than adding a second source. |
| 6 | ConvFinQA protocol | canonical ConvFinQA paper | Reuse the verified ConvFinQA citation. |
| 7 | Confidence, calibration, and selective prediction | calibration source plus LM-confidence source | Split the sentence if one citation cannot support all components. |
| 8 | Selective prediction and abstention | selective classification / risk-coverage source | Verify a primary selective-prediction source. |
| 9 | Repeated-sampling agreement, entropy, and semantic dispersion | self-consistency, self-checking, and semantic-uncertainty sources | Split the current broad sentence; do not use one citation for all three concepts. |
| 10 | Self-consistency methods | Self-Consistency for chain-of-thought reasoning | Verify the canonical paper and cite only the claim it supports. |
| 11 | Robustness and stress testing | behavioral NLP testing and, if retained, a separate robustness/OOD source | CheckList supports behavioral testing; add a separate source for adversarial/OOD claims. |
| 12 | Metamorphic testing | primary metamorphic-testing source, optionally an NLP behavioral-testing source | Verify relation-preserving testing terminology and scope. |
| 13 | Counterfactual reasoning and causal evaluation | counterfactually augmented data plus a separate causal-evaluation source | Split the sentence; do not let one counterfactual source stand for causal evaluation. |
| 14 | Process and reasoning verification | process supervision / verifier training sources | Verify whether the final text discusses traces, proofs, tool calls, or outcome-based verification. |

## Citation insertion policy

1. Use citations only for external background and dataset provenance. Do not cite external work as evidence for the project’s frozen AUROCs.
2. Keep internal evidence references as artifact IDs in the appendix/provenance ledger, not as fabricated bibliographic entries.
3. Do not claim novelty from the absence of a citation. The related-work section should position PECR as a program-backed intervention diagnostic and state the overlap with metamorphic testing explicitly.
4. Split multi-topic sentences when one source cannot support every clause.
5. After inserting BibTeX keys, rerun a bibliography-to-citation consistency check and a citation-context check.

## Current decision

The reviewed draft is suitable as a **content-complete first draft with citation placeholders**. It is not yet a submission-ready bibliography version.
