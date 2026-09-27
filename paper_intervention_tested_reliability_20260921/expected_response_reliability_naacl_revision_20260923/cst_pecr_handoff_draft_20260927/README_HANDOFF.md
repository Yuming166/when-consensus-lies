# CST–PECR paper handoff (working draft)

This package is a scoped handoff for continued writing. The manuscript is a synthesis draft, not a submission-ready NAACL paper. It deliberately preserves null/negative and exploratory results and does not tune claims to favor the hypothesis.

## Start here
- `MANUSCRIPT_DRAFT.md`: integrated narrative from CST to PECR.
- `RESULTS_AND_EVIDENCE_MAP.md`: concise numeric results, status, and exact source artifacts.
- `SHA256SUMS.txt`: hashes of the two documents above.

## Evidence hierarchy and cautions
- CST Round-8 E1 is exploratory method search on a reused 50-item cohort. Placebo inertness failed; parser-valid yield was 47.0% overall and 28.0% in either placebo arm. No error-ranking result was established.
- PECR's earlier selected FinQA TEST result (139/157 scorable) is program-conditioned and numeric-answer-blind only at scoring. The comparison to the fixed-majority-direction baseline is uncertain; all 18 unscorable items were later labeled incorrect.
- The 565-item PECR collection has a post-collection label/analysis report with implementation chronology limitations. The relation-augmented score has a positive point-estimate delta over graph-only, but its 95% CI crosses zero. Do not call it confirmed superiority.
- End-to-end repair V2 is post hoc; PECR-triggered repairs yielded zero corrections and zero harms. No repair benefit was demonstrated.
- Repairability-aware OOF development validation is exploratory, with every 95% CI crossing zero; no independent validation.

## Publication scope
This handoff excludes raw model ledgers, prompts/stimuli, benchmark data, API configuration/secrets, caches, logs, and runtime artifacts. The full evidence remains in the local experiment directories referenced in `RESULTS_AND_EVIDENCE_MAP.md`; transfer those separately only after a privacy/licensing/sensitivity review.

## Suggested next work
1. Have the incoming collaborator inspect the cited source reports and reproduce manuscript numbers.
2. Decide whether the paper is framed as a construct-validity/measurement-boundary paper, not as a validated CST+PECR shared mechanism.
3. Resolve citation completeness, independently verify dataset/scorer details, and run a full LaTeX build and claim-by-claim audit before submission.
4. Any future tuning must use a fresh source-group-disjoint validation and newly frozen protocol; preserve the current holdout analyses as reported.
