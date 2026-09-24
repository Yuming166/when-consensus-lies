# Integrated manuscript v2 (2026-09-25)

`main.tex` integrates the current PECR-centered mainline, contribution statement, results table, limitations/timeline, and reviewer assessment. The earlier full draft remains untouched.

- Main claim: relation-risk error ranking on the 139-item scorable FinQA TEST subset.
- Disallowed claims: end-to-end oracle-free construction, deployment readiness, shared CST/PECR mechanism, and imputation superiority over direct prediction.
- Chronology language follows `../26_LABEL_FREEZE_TIMELINE_UTC_AUDIT_20260925.md`: records support but cannot independently verify freeze-before-label order.
- No model calls, TEST gold regeneration, or label regeneration were performed for this revision.

This is a review draft; venue-specific page-limit/format validation and author review remain.


## Build check (2026-09-25 Asia/Shanghai)

A local compiler probe found no `latexmk`, `pdflatex`, `xelatex`, `lualatex`, `tectonic`, or `bibtex`; therefore no PDF compilation is claimed. Static source checks were run after revision (citation-key coverage, balanced braces, and matched LaTeX environments); these do not substitute for a TeX build.
