# Reviewed-draft changelog

This file records deterministic corrections applied after the Luna Max pre-submission audit. The original segmented draft and the cleaned draft remain unchanged.

- Replaced the unjustified conditional-expectation equality for missing-probe imputation with a plug-in-hybrid description; kept the deployed heads as $P(F_{\pm2}=1\mid z)$ estimates.
- Explicitly distinguished missing-head AUROCs (targets $F_{-2}$ and $F_{+2}$) from the combined imputed AUROC for original correctness $C$.
- Softened “rejects,” “rules out,” “more informative,” and “cross-model-stable” wording to match the bounded evidence.
- Changed “confidence values” to “confidence-based AUROCs.”
- Defined the secondary retention ratio against the same-cohort confidence AUROC.
- Removed the historical mixed call-accounting paragraph from the main text.
- Standardized the imputation notation to $z$, $\hat p_{-2}$, and $\hat p_{+2}$.
- Qualified transformed gold as computed from the frozen gold program independently of the model response.
- Added artifact provenance anchors for CST, S&P, FinQA, and ConvFinQA.
- Added the analyzer-repair, feature-hash, no-new-calls, and post-hoc sensitivity disclosures to the reproducibility appendix.

No experimental records, frozen contracts, model outputs, or result values were changed.
