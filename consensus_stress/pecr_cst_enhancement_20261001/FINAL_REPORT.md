# PECR/CST examples and benchmark enhancement v2

## Completed

- Fixed-seed (`20260930`) read-only case selection and provenance audit.
- PECR: 2,241 manifest rows / 453 groups; 1,735 strict rows / 424 groups; response strata counts direction-pass 986, flat 70, opposite 94, mixed 300. Two examples per stratum plus two nested construction failures were selected.
- CST: 100 formal items / 50 pairs; stored flips were recomputed from Round-6/7 decisions with zero discrepancies. One candidate was selected for each available all-counter/all-placebo, counter-only, placebo-only and neither pattern.
- Every selected case records source ID, edit, expected relation, raw/structured answers, parse/unit status, features or flip details, line/hash provenance, label-use boundary, and authorization status.
- Benchmark table/data card, paper copy `main_v15_examples_benchmark_20261001.tex`, claim--evidence map, missing-material list, pre-freeze API call plan, and static checks are present.

## Boundaries

All cases are internal descriptive candidates. Semantic review linkage, complete CST prompts, and item-level redistribution permissions are missing, so public case confirmation is blocked. CST V3's 34/34 construction-failure adjudication remains boundary evidence and is not called a validated test set. HGB is described as an implementation for the PECR curve representation.

## Calls and preservation

This continuation made 0 experimental model calls, 0 API calls, and 0 training runs. No manifest, ledger, label, score, OOF, holdout or old paper was modified. Input hashes and selection ranks are recorded under `audit/`.

## Compilation

No LaTeX compiler was available (`pdflatex`, `tectonic`, `latexmk` absent), so no PDF compilation or page-by-page visual inspection was possible.
