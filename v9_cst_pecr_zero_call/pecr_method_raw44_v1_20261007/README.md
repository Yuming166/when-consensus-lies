# PECR method figure: Raw + Arithmetic44

This is a native vector revision of the author's `pecr_method_phenomenon_v4.svg`.

## Deliverables

- `figures/pecr_method_raw44_v1.svg`: editable SVG; ordinary text uses Arial and Courier New, and mathematical formulas are outlined paths.
- `figures/pecr_method_raw44_v1_outlined.svg`: fully outlined SVG for appearance-preserving Illustrator import.
- `figures/pecr_method_raw44_v1.pdf`: vector PDF with embedded text fonts, for LaTeX.
- `figures/pecr_method_raw44_v1.png`: full-resolution preview.
- `figures/panel3_arithmetic44.svg` and `.png`: an enlarged view of the revised third panel.
- `CAPTION.tex`: suggested caption and single-column insertion snippet.

The artboard retains the source dimensions: 218.27 × 507 pt, approximately 7.70 × 17.89 cm. The native objects in panels 1 and 2, including the G96 ribbon, are preserved. Illustrator PostScript font-family aliases are normalized to Arial/Courier New for portable rendering. In panel 4 only the fusion formula changes; the tree icon, risk gauge, and training-only dashed label branch are preserved.

## What panel 3 actually represents

The authority is the released positional feature schema and the saved DeepSeek implementation, not the superseded Curve-centric drawing.

1. Parse up to the first 128 table-cell coordinates having finite numeric values in all three worlds; omit the header row and first column.
2. Enumerate one-step operations on two distinct cells. Sum uses one ordering of each pair; difference and ratio are ordered. Division candidates require a nonzero denominator in every world. Candidate evaluations must be finite in every world.
3. The ratio is multiplied by 100 when **all three saved response units** indicate percent. In that case the percentage-change candidate `100(x/y - 1)` is also included. Otherwise the ratio is unscaled. The algorithm does not chain operations or execute the dataset's gold program.
4. Match each candidate to each saved answer with `tau_w = max(0.01, 1e-4 * abs(a_w))`. Candidate identities preserve the operation and cell coordinates across worlds. The icon's checkmark denotes this numerical tolerance match, not answer correctness.
5. Produce Arithmetic44 in the actual order: original8, positive8, negative8, joint16, question4. The eight per-world summaries concern log count, uniqueness, edited-seed overlap, question/row and question/column lexical Jaccard similarity, question-year overlap, unit knownness, and unit compatibility. These are deterministic correspondences, not verified reasoning provenance.
6. The cross-world block includes common-candidate existence/uniqueness/count, intersection-over-union, source-set switching, edited/changed-operand overlap, question-operation/year/unit/lexical context, and the best joint numeric fit. The question block uses four fixed lexical cue flags: direct read, ratio, change, comparison.

`R18` is a compact **drawing alias**, not a new experiment: `concat(Raw16, h, t)`, where `Raw16 = Raw17[0:16]`, `h = b_new - b_old` is the signed saved positive-world input edit, and `t = h / (abs(b_old) + 1e-9)`. It omits the unresolved legacy descriptor at Raw17[16]. Thus the primary fused vector is `96 + 16 + 2 + 44 = 158` dimensions. The drawing does not rename the experimental `Raw` baseline, which additionally contains G96 and has 114 columns.

All quantities in panel 3 are symbolic. No new item-level result, gain, calibration claim, or claim that matching certifies correctness has been introduced. No model/API request, training, gold-answer or holdout read was performed.

## Sources and checks

- `../pecr_two_track_benchmark_release_v2_20261007/schemas/feature_schema.json`
- `../pecr_two_track_benchmark_release_v2_20261007/src/retrain.py`
- `../pecr_deepseek_v41_flash_report_oof_v1_20261006/src/arithmetic.py`
- `../pecr_deepseek_v41_flash_report_oof_v1_20261006/src/curve_projection.py`

`VALIDATION.json` records source hashes, dimensional checks, exact preservation of the upper-panel native objects, unique element IDs, and output hashes. `FINAL_QA.json` records the final rendering checks. `source/user_method_v4.svg` preserves the uploaded original. Rebuilding uses the existing local rendering dependencies/fonts from the preceding figure revision; the delivered SVG/PDF files themselves do not require those directories.
