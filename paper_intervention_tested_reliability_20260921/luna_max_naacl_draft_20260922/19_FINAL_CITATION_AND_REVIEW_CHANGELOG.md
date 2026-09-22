# Final citation/review changelog — 2026-09-22

## Completed

1. Replaced all 14 `[CITATION NEEDED]` placeholders with 13 paper-local citation keys.
2. Verified all 13 cited sources were fetchable from first-party ACL Anthology, PMLR, or arXiv records; see `14_CITATION_VERIFICATION.json`.
3. Added five table captions and generated `latex/main.tex` from the cited Markdown draft.
4. Passed static citation-key, bibliography, delimiter, environment, stale-placeholder, and expected-anchor checks.
5. Preserved the reviewed manuscript's numerical evidence: the numeric token multiset is unchanged after citation/caption packaging; see `18_NUMERIC_PRESERVATION_AUDIT.*`.
6. Ran a final Luna Max micro-review. It found no P0/P1 issues and six P2 suggestions.
7. Applied the P2 edits that materially improve precision:
   - described `0.7474` as the imputed score versus the fixed S2 score `0.6508`, rather than saying S2 itself increased;
   - softened S&P wording to a bounded portability check/caution;
   - changed the baseline paragraph from a definitive “highest observed” claim to a direct cohort comparison;
   - anchored the `+0.02` practical threshold to the frozen Stage 2 artifact ID;
   - changed the discussion heading to “Expected response versus change alone.”

## Remaining environment boundary

No PDF compile was run because this environment has no `pdflatex`, `tectonic`, `latex`, or `xelatex` executable. The generated ACL source is ready for one external template-build pass to inspect page count, table wrapping, and bibliography rendering.

No frozen experiment artifact or historical model-output directory was modified.
