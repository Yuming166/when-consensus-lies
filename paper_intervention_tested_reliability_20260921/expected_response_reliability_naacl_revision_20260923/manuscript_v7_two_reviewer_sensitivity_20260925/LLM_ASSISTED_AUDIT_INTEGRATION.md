# Manuscript v4 integration note (2026-09-25)

This version retains the post-hoc LLM-assisted audit without presenting it as independent human review. It also makes the fixed-majority-direction control prominent: relation-risk AUROC is 0.7337 versus 0.6837; the paired difference is +0.0500 (95% CI [-0.0092, +0.1215]), crossing zero. The manuscript therefore does not claim established superiority over this stronger control.

A versioned exploratory leave-out sensitivity is included. Removing the five highlighted AMT/BLK cases gives n=134, AUROC 0.7448 versus 0.7016, difference +0.0432 (95% CI [-0.0111, +0.1076]). Removing all 20 purposively selected diagnostics gives n=119 and identical AUROC 0.7295 for relation and fixed-majority scores. These 20 cases are exactly the cases differing from the majority-direction prior; this is a structural limitation, not independent validation. That V6-era provenance interpretation is superseded in V7 by the project lead’s clarification that reviewer 2 independently completed the human forms; see the V7 provenance note. The LLM audit remains a separate exploratory analysis.

No model calls were made, and frozen experimental artifacts were not modified. The PDF has not been compiled or page-checked because no TeX compiler is available in the current environment.
