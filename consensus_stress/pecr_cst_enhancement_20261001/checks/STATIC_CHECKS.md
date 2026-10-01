# Static checks

- `python -m py_compile src/build_audit.py`: passed.
- `python src/build_audit.py`: passed; 14 candidate rows written; 0 model/API/training calls.
- PECR selectors use only whitelisted ID, source group, direction, operation, responses, parse reasons and status; source labels remain explicitly disclosed as present in the file.
- Nested construction status used; top-level provenance status is not used as a failure flag.
- Selected PECR raw ledger keys are unique and request/response hashes are checked; selected CST flip patterns have 0 stored-flip discrepancies.
- No holdout path read; script asserts against holdout paths.
- Input hashes are saved in `audit/INPUT_HASHES.json`; prior recovery hashes remain unchanged.
- LaTeX copy is separate from V14/source. `pdflatex`, `tectonic`, and `latexmk` are unavailable in PATH, so compilation and page-image inspection are blocked and not claimed.
