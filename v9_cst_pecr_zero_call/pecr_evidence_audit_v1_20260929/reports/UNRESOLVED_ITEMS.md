# Unresolved and non-auditable items

1. The reviewer-completed forms, reviewer identities/independence, disagreement records, and adjudication record for the 50-item blind review were not present in the inspected review directory. The 50/50 VALID result remains project-lead reported.
2. The full mechanical-candidate exclusion rationale for the 16 identity-break items is available as construction flags, but the flags are conservative mechanical checks, not proof that the underlying source table is invalid.
3. The 490 mechanical candidates absent from the strict feature table cannot be assigned a single failure cause without conflating overlapping label, parse, JSON, and construction statuses; the item-level audit preserves these as separate flags.
4. The saved OOF arrays do not include a self-contained fold manifest or feature snapshot. Reproducibility is supported by code, hashes, and reports but not fully independently reconstructible from OOF files alone.
5. No claim about the 565-item holdout is made here; it was not read or used in this audit.
