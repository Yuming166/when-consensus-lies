# CST manuscript materials (bounded-evidence framing)

## CST subsection

### Consensus Stress Testing: evidence for a boundary, not a validated router

We use Consensus Stress Testing (CST) as a construct-validity probe for whether a panel changes its answer when exposed to decision-relevant evidence. The strongest completed control is a preregistered strict independent-counter-evidence pilot: counter-evidence was generated from the claim alone, assigned offline, and compared with a topic-relevant matched placebo. The strict condition produced more answer flips than the placebo (0.7258 vs. 0.5141; paired contrast +0.2118, 95% CI [+0.1160, +0.3097]). This result is consistent with selective average responsiveness to decision-relevant evidence, and it is not explained solely by the paired-mirror construction used in the natural-reverse axis.

The same result does not establish a clean intervention construct. The placebo flip rate was 0.5141, exceeding the prespecified inertness ceiling of 0.30, so the placebo gate failed. Moreover, independent counter-evidence did not provide a reliable error-ranking score: on the high-consensus subset, the AUROC was 0.624 (95% CI [0.286, 0.856]; 46 scorable items, three wrong items), with negative paired differences relative to both the natural-reverse score (−0.349, 95% CI [−0.714, −0.091]) and the frozen Qwen score (−0.318, 95% CI [−0.670, −0.106]). Thus, the completed CST evidence supports a bounded behavioral statement—panels can respond more to one evidence intervention than to a matched placebo on average—but not an independently validated pre-outcome router.

Two audits further constrain interpretation. First, the natural-reverse prompt for each item was byte-identical to the original prompt of its mirror item in all 3,000/3,000 reconstructed cases, making that axis mechanically non-independent; its high AUROC should not be interpreted as an independent evidence-direction replication. Second, the exploratory E1 audit had only 587/1,250 records under the frozen strict parser. A post-hoc bounded parser recovered the remainder, but under that sensitivity analysis the placebo still induced 153/250 flips while A/A induced 0/250, and the same-case CE-minus-placebo interval crossed zero (+8.4 percentage points, 95% CI [−21.9, +30.4]). Finally, the proposed V3 three-state extension has no model results: all 34 inherited candidate items failed the recorded construction review, leaving 0/17 eligible source groups. We therefore treat CST as boundary evidence for intervention construct validity, not as a validated router or as an independent replication of PECR.

CST and PECR address a related question—whether a controlled intervention produces the expected response—but they operationalize different interventions. PECR is program-conditioned, whereas CST is evidence-intervention based. Their shared mechanism remains an open hypothesis rather than a demonstrated result.

## Compact results table

| Analysis | Control / coverage | Observation | Interpretation |
|---|---|---|---|
| Round 7 strict CE | matched placebo; 50-item cohort | CE flip 0.7258; placebo 0.5141; Δ +0.2118 [0.1160, 0.3097] | behavioral contrast, but placebo gate fails |
| Round 7 strict placebo gate | prespecified ceiling ≤0.30 | 0.5141 | control not inert |
| Round 7 error ranking | HC n=46; wrong=3 | AUROC 0.624 [0.286, 0.856] | no reliable independent ranking |
| Natural-reverse audit | paired prompt identity | 3,000/3,000 identical; Qwen answer agreement 99.97% | mechanically non-independent |
| E1 strict parser | 1,250 attempted | 587 valid; 663 invalid | limited frozen coverage |
| E1 post-hoc sensitivity | A/A and placebo | A/A 0/250; placebo 153/250 | placebo not inert; post-hoc only |
| E1 same-case CE−placebo | relaxed parser | +8.4 pp [−21.9, +30.4], n=250 | uncertain; interval crosses zero |
| V3 review | 34 items / 17 groups | 34 failures; 0 eligible groups; 0 calls | no V3 validation result |

## Limitations

The CST evidence is limited by a failed placebo gate, a small strict error-ranking cohort with only three wrong high-consensus items, and parser attrition in E1. The E1 relaxed analysis is post hoc and cannot replace the frozen strict analysis. The two E1 placebo variants were largely identical in stimulus and request content, so their agreement is not an independent replication. Natural-reverse is mechanically equivalent to paired-original prompts and therefore cannot identify an independent evidence-response mechanism. The V3 three-state protocol remains unvalidated because its inherited candidate set failed full-input construction review and has not received model calls. We also do not infer a common CST–PECR mechanism from the fact that both use interventions: PECR is program-conditioned and CST is evidence-based. These boundaries motivate future work but are not repaired by relabeling, parser relaxation, selective item replacement, or additional post-hoc analyses.

## Three likely reviewer objections and honest answers

1. **“Is the positive CST contrast just a noisy or non-inert placebo result?”**
   Partly unresolved. The strict CE-minus-placebo interval is positive, but the placebo flip rate is 0.5141 and fails the prespecified ≤0.30 gate. We therefore claim only a bounded average contrast, not a clean causal intervention effect.

2. **“Is natural-reverse an independent test of evidence responsiveness?”**
   No. The audit reconstructs byte-identical prompts for 3,000/3,000 reverse/mirror-original pairs, with near-perfect answer agreement. The natural axis is retained as a behavioral result under the frozen protocol, but not as an independent mechanism test.

3. **“Why should CST and PECR be presented together?”**
   They share a research question about response to controlled interventions, but they test different intervention spaces and neither currently validates the other's mechanism. PECR is the program-conditioned result; CST is boundary evidence about evidence interventions. Any stronger unification would be speculative.
