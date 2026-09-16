# Final Static Audit — submission_v1

**Audit time:** 2026-09-16T22:15:23+08:00 (Asia/Shanghai)
**Scope:** current `manuscript.md`, section fragments, generated `latex/main.tex`, `references.bib`, live citation metadata, Astra6 review records, the successful offline Tectonic/PDF build diagnostics, and the latest Astra6 layout-only review.
**Status:** **STATIC PASS; OFFLINE TECTONIC/PDF BUILD PASS (RC=0, 22 pages); LAYOUT-ONLY REVIEW COMPLETE.**

## Changes covered by this audit

- Narrowed the Round10 claims to distinguish the **as-assigned** independent-CONTRADICT result (35/37), the direction-audited subset (30/32 across 7 clean items), and the post-hoc Probe1 as-assigned total (44/46); Probe1 is not treated as a fully audited clean result.
- Renamed Round10 Table 5 language from “direction effect” to “direction contrast” and retained the non-causal/non-mediation boundary.
- Disambiguated Method reporting of the larger cached strict TARGET_SPEC analysis (+0.027) versus the separate strict 25-pair analysis (+0.004), with cohort and metric-specific counts.
- Clarified that the direction-clean natural-versus-independent construction comparison has only 3 items, so it is distinct from the 30/32 direction-audited subset.
- Clarified Table 6 cohort versus metric-specific complete-case counts: the larger strict run has cohort HC=96/wrong=8 but `S_ind` scored n=72 over 42 pairs and OOF n=72/wrong=5; the 25-pair strict run has cohort HC=47/wrong=3 and metric n=46 over 25 pairs.
- Changed the strict independent-CE control description to a topic-matched, decision-irrelevant placebo and explicitly recorded the preregistered placebo-ceiling (G4) failure in W2 v1 and both strict analyses.
- Replaced the broad E_sel “placebo leg collapses” wording with a consensus-direction-stratified, unresolved residual-contrast statement.
- Added the Astra6-recommended disclosure that AUROCs are conditional on the frozen VitaminC resource and its offline gold-conditioned construction; the Qwen-to-Ling result is a single transfer check; `S_ind` and Round10 are neither independent predictive nor causal evidence.
- Regenerated the live citation context/map and refreshed all manuscript-dependent metadata after the final prose edits.
- Repointed historical relay provenance to the exact archived pre-reconcile draft and corrected the Round10 source report so the combined 44/46 result is labeled post-hoc/as-assigned rather than fully clean.
- Recorded the successful external Tectonic 0.17.0 offline-cache build (RC=0, 22-page PDF) and its final warning ledger without adding the PDF or build intermediates to the submission package.
- Recorded completion of the latest Astra6 layout-only review and execution of its actionable layout/presentation recommendations; this review adds no scientific evidence and does not change the claim boundary.
- This report update modifies only `README.md` and this audit file; metadata JSON, manuscript, LaTeX, bibliography, and experimental artifacts were not modified by this update.

## Checks

- **Markdown/fragment synchronization: PASS.** 7 canonical top-level units and 7 fragment units; whitespace-normalized content matches for every unit; no missing or extra units.
- **Converter regeneration: PASS.** Current `manuscript.md` has 1,244 lines; converter output has 1,022 lines and reports 66 headings, 302 paragraphs, 7 tables, 6 captioned tables, 10 equations, and 10 preserved citation commands. In-memory regeneration matches `main.tex` exactly (`d9e913e2785060f1e7a1f9fac4275379fa7780b2174ce01c0b876c0abd696941`).
- **Citation coverage: PASS.** 10 live `\citep{...}` commands contain 25 key references and 18 unique keys; `references.bib` has 22 unique keys; missing keys `[]`; duplicate keys `[]`; `[CITE]` placeholders `0`.
- **LaTeX structure: PASS (static only).** `table` 7/7, `tabularx` 7/7, `itemize` 4/4, `enumerate` 3/3, captions 6, labels 6, braces 499/499.
- **Math delimiter audit: PASS (static only).** Display delimiters `\[`/`\]` are 10/10; inline `\(`/`\)` pairs are 122/122; raw dollar count is 14 (7 pairs); no inline display delimiter remains.
- **Generated pseudo-command audit: PASS.** No `\textbackslash{}` math-command artifacts or escaped display-delimiter artifacts remain; current `[CITE]` count is 0.
- **Live citation metadata: PASS.** `citation_contexts.json` is rooted at the current manuscript SHA `eab44a229c494e9c933f0c330b624b19127f737477d8551aa41af399efa6bf52` with 10 live contexts; the old ten-placeholder extraction remains explicitly historical. `citation_map.md` uses current line numbers.
- **Citation-validation snapshot reconciliation: PASS.** The duplicate top-level manuscript/context fields in `citation_validation.json` match the current files (manuscript 1,244 lines / 77,732 bytes; live context SHA `0d089486b46db29cb260252a375cbe269e1507e38fe48ffdcb363a58b9a3dbaf`, 262 lines / 16,883 bytes); its `final_static_snapshot` remains consistent.
- **Artifact inventory: PASS.** The manuscript's 17 explicitly listed repository-root paths exist; no missing path was found.
- **Offline TeX/PDF build: PASS.** Tectonic 0.17.0 compiled the current generated source from the offline cache with RC=0 and produced a 22-page PDF. The PDF/build intermediates remain external verification artifacts and are not included in `submission_v1`; no PDF path is asserted.
- **Final build warning ledger: RECORDED.** Overfull hbox 0; underfull hbox 148; underfull vbox 3; review-mode lineno warning 1; font fallback 5; hyperref token warning 0. The nonzero warning counts are disclosed and are not relabeled as zero-warning output.
- **Table 6/layout review boundary: RECORDED.** The latest Astra6 layout-only review was completed and its actionable recommendations were executed; the full bounded response is in `audit/astra6_final_layout_review_20260916.md`. The review does not add scientific evidence or change the frozen VitaminC, single-transfer, mechanism-probe, Round10, or non-causal claim boundaries.
- **Call-accounting table decision: RECORDED.** The first small auxiliary call-accounting table remains intentionally uncaptioned and unlabeled. It is explanatory, not cross-referenced by number, and Astra6 judged it non-blocking; adding a normal caption could shift the existing Tables 1–6 numbering, so no change was made.
- **Astra6 micro-review: RECORDED.** Health probe returned HTTP 200 with `gpt-6-astra`; attempt 1 timed out at 15s; attempt 2 returned HTTP 200 with strict model match. The short response is recorded in `audit/astra6_micro_review_20260916.md` and was used only for wording-risk review, not for new evidence.
- **Latest Astra6 transport boundary: RECORDED.** The later metadata-only request is in `audit/astra6_metadata_review_20260916.md`; all three transport attempts timed out and yielded no editorial evidence, so it was not used for claims.

## Evidence anchors

- Canonical source: `manuscript.md` (1,244 lines; SHA `eab44a229c494e9c933f0c330b624b19127f737477d8551aa41af399efa6bf52`).
- Generated submission source: `latex/main.tex` (1,022 lines; SHA `d9e913e2785060f1e7a1f9fac4275379fa7780b2174ce01c0b876c0abd696941`).
- Round10 claim boundary: current `manuscript.md:129`, `:417`, `:723`, `:833`, `:1067`, and `:1197-1202`, covering 35/37, 30/32, post-hoc as-assigned 44/46, the n=3 direction-clean construction comparison, and the non-causal boundary.
- Table 6 protocol-specific rows and G4 caveat: `manuscript.md:980-997`.
- Live citation map: `citation_contexts.json` (SHA `0d089486b46db29cb260252a375cbe269e1507e38fe48ffdcb363a58b9a3dbaf`) and `citation_map.md`.
- Offline build: external Tectonic 0.17.0 run, RC=0, 22-page PDF; the detailed record is `audit/tectonic_build_20260916.md`, and the PDF is not part of this directory.
- Astra6 packet review: `audit/astra6_micro_review_20260916.md`; latest layout-only review: `audit/astra6_final_layout_review_20260916.md`, without asserting a PDF path.

## Boundary

This report establishes a statically validated and externally compiled submission candidate; the compiled PDF was used for verification but is not included in this package. The supported scientific claim remains: frozen VitaminC natural-pair matched-protocol reliability measurement plus bounded direction-gated mechanism-oriented descriptive evidence. It does not establish universal transfer, causal/mediation effects, an independent-CE predictor, S&P500 alpha, general counter-evidence rigidity, or field-wide SOTA.
