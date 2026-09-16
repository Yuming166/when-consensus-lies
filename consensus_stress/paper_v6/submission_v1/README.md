# CST-Bench submission_v1

This directory is a clean submission candidate derived from `paper_v6` on 2026-09-16.
The original v6 source draft is preserved under `consensus_stress/paper_v6/archive/pre_reconcile_20260916/`.

## Scope

- The clean manuscript removes agent/front-matter metadata and in-text `(ref)` audit markers.
- The current manuscript contains 10 live `\citep{...}` commands using 18 unique keys from `references.bib`, 25 key references in total, and 0 `[CITE]` placeholders; the ten-placeholder extraction is retained only as historical provenance.
- `RS_q = -BF_q` is the primary predictive score; `S_natural` is retained as a separate natural-mirror diagnostic.
- Independent counter-evidence is reported by protocol version (W2 v1 versus strict TARGET_SPEC), with cohort and metric-specific sample sizes; the strict placebo ceiling (G4) is reported as failed rather than hidden.
- Round10 reports logical-call accounting, parser yield, direction audit, the as-assigned 35/37 result, direction-audited 30/32 subset, post-hoc Probe1 as-assigned total 44/46, and the small direction-clean construction cell; these are mechanism-oriented descriptive results, not clean universal or causal evidence.

## Numerical reconciliation

The preregistered Phase-4 main result retains Qwen Risk@80 `0.846 [0.638, 0.981]`. The separate matched-baseline leaderboard recomputation reports a lower CI bound of `0.651` on its valid-intersection bootstrap; it is not substituted into the preregistered main claim. The conflict is recorded in `consensus_stress/paper_v6/audit/claim_numeric_audit.md` and the source artifacts.

## Claim boundary

This package makes no field/universal SOTA, universal transfer, causal/mediation, S&P500 alpha, general-rigidity, or independent-CE-predictor claim. The matched-baseline leaderboard remains a separate descriptive artifact.

## Current dynamic metadata (2026-09-16)

- Canonical `manuscript.md`: **1,244 lines**, **77,732 bytes**, SHA-256 `eab44a229c494e9c933f0c330b624b19127f737477d8551aa41af399efa6bf52`.
- Generated `latex/main.tex`: **1,022 lines**, **83,466 bytes**, SHA-256 `d9e913e2785060f1e7a1f9fac4275379fa7780b2174ce01c0b876c0abd696941`; the current converter snapshot records this source/output pair as aligned.
- Live `citation_contexts.json`: **10** contexts / **18** unique keys / **25** key references, SHA-256 `0d089486b46db29cb260252a375cbe269e1507e38fe48ffdcb363a58b9a3dbaf`; current `[CITE]` count is **0**. The historical ten-placeholder extraction remains provenance only.
- The old files under `consensus_stress/paper_v6/references/` and the stored literature-relay request are explicitly historical/provenance artifacts, not the current live map.

## Final static validation (2026-09-16)

- Converter result: 1,244 manuscript source lines -> 1,022 LaTeX lines; 66 converter headings, 302 paragraphs, 7 tables with 6 captions, 10 equations, and 10 preserved citation commands.
- Citation audit: 18 unique LaTeX keys, 22 bibliography entries, 0 missing keys, 0 duplicate keys, and 0 `[CITE]` placeholders.
- LaTeX static audit: table/tabularx environments 7/7, itemize 4/4, enumerate 3/3, braces 499/499, display math delimiters `\[`/`\]` are 10/10, inline math delimiters `\(`/`\)` are 122/122, and raw `$` count is 14; no remaining `\textbackslash{}` math-command artifacts.
- The current live citation map is in `citation_map.md`; the historical placeholder map and relay candidate response are explicitly labeled as provenance only.

## Astra6 editorial check

- The successful bounded packet review in `audit/astra6_micro_review_20260916.md` used the private relay: health probe HTTP 200; first short request timed out; second request returned `gpt-6-astra` with HTTP 200 and strict model match. No fallback, secrets, full manuscript, or raw artifacts were sent.
- The latest Astra6 layout-only review has been completed after the external build and is recorded in `audit/astra6_final_layout_review_20260916.md`. Its actionable layout/presentation recommendations were executed before this update. It was a layout/editorial check only, adds no scientific evidence, and does not change the claim boundary.
- The earlier three-attempt substantive request remains recorded in `audit/astra6_submission_v1_followup_20260916.md` as two read timeouts followed by HTTP 502; it is not treated as editorial evidence.
- A later metadata-only request is recorded in `audit/astra6_metadata_review_20260916.md`; all three transport attempts timed out, so it produced no editorial evidence and was not used for claims.

## External build and layout verification (2026-09-16)

- The current generated LaTeX source was compiled with Tectonic **0.17.0** using the local offline cache; the run completed with return code **0**.
- The run completed the TeX/BibTeX cycle and produced a **22-page PDF** in an external temporary build location. The PDF and build intermediates are not included in `submission_v1`; no PDF path is asserted here.
- Final build-log diagnostics: **overfull hbox = 0**, **underfull hbox = 148**, **underfull vbox = 3**, **review-mode lineno warning = 1**, **font fallback = 5**, and **hyperref token warning = 0**.
- The nonzero underfull, lineno, and font-fallback diagnostics are disclosed rather than silently treated as absent; they do not alter the scientific claim boundary. The full build record is in `audit/tectonic_build_20260916.md`.
- The small call-accounting table in the method section remains intentionally uncaptioned and unlabeled. Astra6 judged this non-blocking because it is explanatory and not cross-referenced; adding a normal caption would risk shifting the existing Tables 1–6 numbering.
