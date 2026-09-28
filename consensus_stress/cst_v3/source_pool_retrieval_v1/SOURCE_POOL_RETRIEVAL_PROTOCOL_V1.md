# VitaminC fixed-source-pool retrieval v1

**Date:** 2026-09-29
**Model calls:** 0
**Status:** mechanical retrieval and audit only; pending two-person human review.

## Frozen inputs checked

- VitaminC snapshot: `/home/gaoym/when-consensus-lies-publish-20260911/data/benchmarks/vitaminc/test.jsonl`
- Selection manifest: `/home/gaoym/when-consensus-lies-publish-20260911/consensus_stress/round3/selection_manifest.json`
- Historical exclusion audit: `/home/gaoym/cst_zero_call_upgrade_20260928/SOURCE_GROUP_EXCLUSION_AUDIT.json`

The script verifies the recorded SHA-256 hashes in the selection manifest and exclusion audit before retrieval. The fixed pool is restricted to the 17 audited `(source_group, page)` pairs, not every page sharing a group label.

## Mechanical retrieval roles

For every one of the 34 inherited directional attempts:

- `A`: exact original evidence ID/text, retained in every condition;
- `neutral`: all same fixed `(source_group, page)` records with a different claim, ranked deterministically by evidence-length proximity; proposition-neutrality is **not inferred**;
- `support`: same-claim records with snapshot label `SUPPORTS`, excluding A;
- `counter`: same-claim records with snapshot label `REFUTES`, excluding A.

The inherited opposite-polarity pair evidence may therefore appear as one directional append: for an A-support item it is a counter candidate; for an A-refute item it is a support candidate. It is not automatically valid for the complete input.

All candidate records are retained in `ATTEMPT_SOURCE_RECORDS_V1.jsonl`; the first deterministic candidate is used only to materialize a provisional complete-input row. No candidate is declared semantically valid, and no candidate is selected using model outputs.

## Failure accounting

The fixed pool contains 114 VitaminC rows across 17 groups/pages. All 34 attempts have at least one mechanical neutral candidate and the inherited opposite-polarity candidate. However:

- 17 A-support rows have no additional same-claim support append;
- 17 A-refute rows have no additional same-claim counter append;
- therefore 34/34 rows fail the four-condition completeness requirement;
- no row is launchable and no source group is counted as human-reviewed eligible.

This is an explicit material-availability failure, not a reason to substitute a more favorable page or silently reuse A. Human reviewers must still inspect the complete provisional inputs and may mark them invalid, ambiguous, descriptive-only, or eligible only under the frozen rules.
