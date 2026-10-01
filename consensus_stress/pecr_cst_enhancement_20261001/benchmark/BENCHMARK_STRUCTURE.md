# Benchmark structure (zero-call audit)

| Stage | PECR | CST | Gate / failure rule |
|---|---|---|---|
| Source and split | 2,241 mechanically aligned dev/train rows, 453 source groups; 1,735 strict parsed rows, 424 groups | 100 formal items / 50 paired clusters in Round-7 `ind_ce`, matched to Round-6 originals | Preserve source-group or paired-cluster identity; pair ID is not a source group |
| Construction | Original, positive, reverse operand/table edits; nested `valid_candidate` status | Natural, counter-evidence, placebo evidence views; evidence replacement is partition-filtered | Mechanical alignment is necessary; semantic validity requires review evidence |
| Response parsing | Numeric value, unit, confidence for original/positive/negative; strict complete rows only | Structured yes/no/abstain decisions, five agents, original plus three conditions | Missing/invalid parse is excluded from strict analysis and reported |
| Track metric | Error ranking AUROC/AUPRC under source-group GroupKFold; Curve HGB versus ordinary three-world HGB | Flip rates and counter-minus-placebo contrast with inertness ceiling | CST and PECR remain complementary tracks; no aggregate score |
| Boundary evidence | 16 `obvious_total_identity_break` rows remain construction-failure examples | CST V3 invalid constructions remain boundary evidence, not a validated test set | Any failed construction or unresolved review blocks confirmation |
| Reproducibility | Frozen manifests, raw ledger, parser rows, feature implementation, seeds and hashes | Cohort, manifests, structured records, cache keys and message hashes | Full prompt text and item-level redistribution authorization are missing for selected CST cases |
| Human review / license | Existing 50-item review packet is reported, but forms, identities, disagreement and adjudication are unavailable | Generated audit samples are not human adjudication | No public case confirmation until review and permission evidence are recovered |

The benchmark is staged as **construction validity → response selectivity → original-answer error diagnosis**. Cases are descriptive illustrations only and are not estimates of overall effects.

## Coverage notes

- The PECR top-level status is a provenance string; construction status is read from the nested `bidirectional` object. The strict file includes labels, so case selection is described as response-field restricted rather than file-level label blind.
- PECR operation/direction distributions and unit/parse coverage are saved in `audit/AUDIT_SUMMARY.json`; raw ledger request and response hashes are checked per selected item.
- CST records corroborate all selected flip patterns with zero stored-flip discrepancies. The inspected cache contains assistant content but not complete request messages; a message hash is not a recoverable prompt.
- Existing HGB numbers are development results from `CURVE_HGB_AUDITED.json`; HGB is an implementation choice, not a claimed algorithmic contribution.
