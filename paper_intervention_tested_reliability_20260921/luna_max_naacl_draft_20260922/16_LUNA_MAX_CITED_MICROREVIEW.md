**Final pass: no P0/P1 issues remain.** The central contribution is bounded and the title is clear; remaining items are P2-level surgical edits.

- **P2 — Central contribution/title: clear.** The paper consistently identifies expected-response fidelity under outcome-blind interventions as the core contribution, with CST and PECR as evidence lines and the S&P branch as a boundary case. The title accurately reflects that scope; no title change is required.

- **P2 — Primary new result is explicitly foregrounded, but its terminology needs correction.** The Qwen ConvFinQA missing-probe result is called the “strongest new result” in §1 and is highlighted again in §5.6, §7.3, and §9. However, “raised/improved Qwen S2 from 0.6508 to 0.7474” is technically misleading: S2 remains \(0.6508\); \(0.7474\) is the imputed \(\widehat{\mathrm{CEF}}\) score under the same three-call deployment budget. Apply this terminology fix consistently in the abstract, introduction, discussion, and conclusion.

- **P2 — S&P portability language slightly outruns the evidence.** With B8–B6 \(=-0.0143\) and CI \([-0.0560,0.0287]\), the frozen result establishes no demonstrated incremental B8 gain on the 469 DEV units; it does not establish a general domain-level portability boundary. Soften “marks a portability boundary”/“negative boundary” in the abstract and results, while retaining the current bounded interpretation.

- **P2 — Comparative claims need an internal evidence pointer or slight softening.** Phrases such as “beyond confidence, agreement, and frozen provenance comparisons,” “more informative than change alone,” and “highest observed AUROC among” baselines are not fully numerically anchored in the supplied main text. Keep them only if the frozen comparison tables/appendix are linked; otherwise present them as evaluated comparisons rather than demonstrated superiority. No new experiment is needed.

- **P2 — The \(+0.02\) practical threshold needs provenance.** “Passes the frozen practical threshold of \(+0.02\)” appears without a protocol or ledger pointer. Add a brief freeze/provenance reference if it was genuinely fixed in advance; otherwise remove the threshold claim. The reported delta and intervals can remain unchanged.

- **P2 — Citation/bibliography check passes at the prose level.** External dataset and related-work claims have nearby citations, and no invented bibliography claim is apparent. Because the bibliography itself is not included here, perform the mechanical ACL conversion check that every citation key resolves and that the cited entries match the claims; no additional references are evidently required.

**Recommended pre-conversion edits:** (1) correct \(\widehat{\mathrm{CEF}}\)-versus-S2 wording; (2) soften S&P boundary language and anchor or remove the threshold sentence.
