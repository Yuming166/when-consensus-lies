# NAACL first-draft package (2026-09-22)

This directory contains the content-complete NAACL first draft after Luna Max review, deterministic claim repairs, external citation insertion, and ACL-style LaTeX conversion.

## Canonical files

- `08_NAACL_FIRST_DRAFT_REVIEWED.md`: reviewed manuscript before bibliography insertion; retained as the reviewed source snapshot.
- `12_NAACL_FIRST_DRAFT_CITED.md`: current canonical Markdown manuscript with verified citation keys and five table captions.
- `13_NAACL_FIRST_DRAFT_REFERENCES.bib`: paper-local bibliography for every external citation in the cited draft.
- `latex/main.tex`: generated ACL/NAACL LaTeX source.
- `latex/acl.sty`, `latex/acl_natbib.bst`: copied ACL style assets; not edited.

## Audits

- `14_CITATION_VERIFICATION.json`: first-party source fetch manifest for 13 cited works.
- `15_FINAL_CITATION_LATEX_AUDIT.md` and `.json`: citation-key coverage, placeholder, table, brace, and LaTeX-structure audit.
- `16_LUNA_MAX_CITED_MICROREVIEW.md` and `.json`: optional final Luna Max micro-review, when available.

## Evidence boundary

The manuscript uses internal artifact IDs for frozen empirical results. External references support only background, benchmark provenance, and related-work positioning. No external citation is used as evidence for the project's AUROCs, confidence intervals, permutation values, call counts, or imputation gains.

The ConvFinQA Qwen missing-probe result remains the main new method result. Ling zero-shot imputation remains suggestive and not statistically confirmed. Full discrete CEF remains a reference diagnostic, not an AUROC upper bound. The scope remains executable financial reasoning on the reported eligible cohorts; no universal reliability, hidden-state-recovery, causal-competence, or arbitrary-task-generalization claim is made.

## Build note

The Markdown-to-LaTeX conversion passed static citation, structure, and delimiter checks. A PDF compile was not run because no `pdflatex`, `tectonic`, `latex`, or `xelatex` executable was available in the environment at packaging time.

No frozen experiment directory was changed by this packaging step.
