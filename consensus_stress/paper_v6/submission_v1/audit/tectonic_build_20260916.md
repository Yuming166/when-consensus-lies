# Tectonic build record — submission_v1 — 2026-09-16

## Build boundary

This record documents an actual local build of the current generated source. The PDF and intermediate TeX files remain in a temporary directory and are **not** added to the source-only submission package.

- Build directory: `/tmp/cstbench-finalbuild-Phh8RJ/latex/`
- Tectonic: `/storage/gaoym/tools/tectonic` version `0.17.0`
- Mode: `--only-cached`, `--keep-intermediates`, `--keep-logs`, `--reruns 2`, `--color never`
- Bibliography workflow: Tectonic ran BibTeX and two TeX reruns, followed by `xdvipdfmx`.
- Input source: the checked-in `latex/main.tex` and `../references.bib`; no generated source was edited in the build directory.

## Result

- Return code: **0**
- PDF: A4, **22 pages**, produced successfully.
- PDF SHA-256: `d30f6926230b3642afa32b9bbf312366a0e8fc481f880d3cde0ba13ddff84a5a`
- `main.bbl`: generated successfully.
- Fatal TeX errors: **0**
- Undefined citations: **0**
- Undefined references: **0**
- Hyperref token warnings: **0**
- Overfull hboxes: **0**
- Underfull hboxes: **148**
- Underfull vboxes: **3**

The earlier same-day build in `/tmp/cstbench-tectonic-relatedfix-uDNPr9/latex/` produced the same 22-page, 183,247-byte PDF with SHA-256 `8180e977e49b6d15b85cbafd946f7dab206d4a52428b357aed54887d557cde7a`. The later fresh build has the same page size, page count, byte size, and diagnostics but a different binary hash, consistent with per-build PDF metadata/timestamp variation; the deterministic identity used for the source package is the `main.tex` regeneration/hash, not a stable PDF byte hash.

## Known warning boundary

The build retains `\usepackage[review]{acl}` for review line numbers. The final log contains one `lineno` reference warning and five font-related fallback warnings (four missing `TU/ptm`/`TU/pcr` shapes plus the aggregate fallback notice). These do not produce clipping or overfull boxes in the rendered inspection, but they should be rechecked in the venue's final compilation environment. The review line-number warning is not evidence to disable review mode for a submission build.

The rendered contact sheet and affected pages were inspected after compilation. Table 6 is dense but readable; path-like source references can break across lines; no clipping, margin overflow, or table overlap was observed. This visual check is bounded to the temporary build and does not constitute a venue-specific camera-ready validation.
