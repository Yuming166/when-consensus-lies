# Known Failures, Invalidations, and Boundaries (Phase 0 audit)

Audit date: 2026-09-12. Source: docs/protocols/*, docs/results/*, docs/research_brief.md.
These records are preserved; nothing below is repaired, pooled away, or relabeled as success.

## 1. INVALIDATED — BoolQ V10 validity defects (pre-formal)

- V10 was blocked by: `item.claim` on `BoolQItem`, undefined `load_fever`, "Gold answer"
  prompt leakage, FEVER-derived manifest fields, and driver ordering (`prepare` before
  substitute generation).
- Status: INVALIDATED before formal model calls; superseded by V10.1 / V11 / V12 / V12.1.

## 2. AUXILIARY ABORT — BoolQ V12 unusable substitute

- Frozen failed item `boolq-1592052e5f54e039-e03`: 13-token source, window 7-19 tokens;
  initial candidate and first repair were both 20 tokens (overlong, no truncation rule).
- V12 aborted as auxiliary stage; V12.1 made exactly one additional repair call (seed
  20260924) and then ran the full formal evaluation. V12 itself produced no validation result.

## 3. FAIL — Synthetic V4 learned monotonic router (primary endpoint)

- V4 improved calibration (ECE 0.074) and beat generic confidence routing, but:
  - behind fixed V3 structural prior on main selective-risk endpoints:
    AURC +0.081 [0.075, 0.086]; Risk@80 +0.006 [0.003, 0.009];
  - drifted under full evidence-inertia holdout (intervention coefficient 0.013,
    coverage 0.998) — training threshold failed to preserve intended 80-82% coverage.
- Interpretation: do not assume a learned router extrapolates to unseen failure mechanisms.

## 4. FAIL — S&P500 LLM replay routing endpoint (twice, V1 and V2)

- V1: AURC(amir) - AURC(majority) = -0.0874 [-0.1994, +0.0736]; upper CI >= 0 -> FAIL.
- V2 (prompt-hardened, same dates): +0.0317 [-0.0886, +0.1805] -> FAIL.
- V2 router risk ECE 0.184 did not replicate V1's 0.055; majority ECE was 0.135.
- Valid-yield repair V1->V2: 68.2% -> 75.6% (paired sign test p ~ 7e-9) is a prompt
  robustness result, not a routing-superiority result.
- No alpha / predictability / routing-superiority claim is supported.

## 5. FAIL — Ling V3.15.2 worst-label gate (label robustness)

- Aggregate replication passed (AUROC 0.640 [0.558, 0.717]), but worst-label AUROC
  for native `no` was 0.120; label-macro AUROC 0.538 [0.500, 0.582] only narrowly above
  chance. Verdict is `PASS_CROSS_FAMILY_AGGREGATE_ONLY`, never label-invariant.
- Same polarity reversal appears in Qwen (no-label AUROC 0.213) and Ling (0.120);
  consistent across families -> likely BoolQ answer priors / asymmetric evidence
  construction / polarity of remove-reverse operations, not a single-model artifact.

## 6. TRANSPORT ABORTS — V3.15 / V3.15.1 (Ling transport)

- V3.15 stopped at smoke: Ling usually omitted environment-known `agent_id`.
- V3.15.1 stopped after formal transport run: 20 empty-packet `remove` responses
  cited placeholder IDs.
- V3.15.2 fixed by inserting expected `agent_id` and clearing empty-packet citations
  (parse modes: 7126 insert agent_id; 33 insert agent_id + clear empty-packet cites;
  1 strict). No answer/confidence/prompt/score/threshold/outcome field changed.

## 7. POST-HOC ONLY — Synthetic V3 matched-coverage analysis

- The matched-coverage analysis in synthetic_v3_posthoc_matched_coverage.md is
  explicitly post-hoc, not preregistered. It must not be presented as a frozen endpoint.

## 8. BOUNDARY — VitaminC V3.16.1 cross-experiment exposure

- 70 target pages in the "fresh" V3.16.1 cohort had previously appeared only as
  distractor pages in V3.16. New distractors were assigned from outside all prior
  568 target/distractor pages. Recorded as controlled cross-experiment exposure;
  not a fully unseen-page replication.

## 9. BOUNDARY — Cross-model item-level instability

- BoolQ Qwen-Ling per-question R_PI Spearman 0.292; VitaminC Qwen-Ling risk
  Spearman 0.294. Aggregate behavioral-signal transfer is supported; universal
  item-level transfer is not.

## 10. BOUNDARY — V3.16 earlier cohort adequacy

- V3.16 Ling SUPPORTS had only 17 high-consensus errors (< preregistered minimum 20);
  favorable intervals were not used to manufacture a pass. That cohort is retained as
  an adequacy boundary.

## 11. NON-CLAIMS

- No universal factuality, citation sufficiency, live-retrieval robustness, or
  prospective trading performance claim is established by any result in this repo.
