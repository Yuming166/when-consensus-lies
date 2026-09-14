# Large-Model Single-Point Validation — Within-Model Results (gpt-6-astra)

Protocol: `cs-paper-gpt-singlepoint-20260914-round6` · Relay: `https://openapi.center/v1` ·
Model: **gpt-6-astra** (verified in 2,483/2,483 successful records) · Date: 2026-09-14.

## Run summary (formal, 100 items x 5 agents x 5 conditions = 2,500 logical calls)

| metric | value |
|---|---|
| records | 2500 |
| valid | 2483 |
| **valid rate (G1 gate >= 0.95)** | **0.9932** (PASS) |
| first-pass rate | 0.9472 |
| HTTP statuses (all internal attempts) | 200 x 1511, 429 x 826, 502 x 115, 400 x 125 |
| transport retries | 929 |
| cache hits (mirror-equivalent views) | 1472 |
| elapsed (s) | 5520.89 |
| token usage (logical, incl. cache replays) | prompt 5534850, completion 171187 |

Failures: 17/2,500 records are transport failures (429/502/400 "Upstream request failed");
**0 parse failures** (contract adaptation not needed; no JSON exemplar escalation required).
2 items lack complete 5-agent original answers (transport failures on `original`) and are
excluded from feature-level analysis by the Round-3 feature construction rule (all 5 originals
required to define consensus/agreement); this is not post-hoc subset selection on outcomes.

## Cohort & HC

- Items attempted: 100 (50 pairs). Items with complete features: 98 (label-free, SHA256
  `f1d167aad462da7dc2af8efae593685f386e3b434e8d36af79361b7989204e03`, frozen before label merge).
- High-consensus (agreement >= 0.8): **96** items; wrong: **8**
  (error rate 0.0833); HC by label SUPPORTS/REFUTES =
  {"REFUTES": 49, "SUPPORTS": 47}; wrong-HC by label = {"REFUTES": 7, "SUPPORTS": 1}.

## Gates (all frozen in preregistration Section 5)

| gate | result | verdict |
|---|---|---|
| G1 pipeline valid >= 0.95 | 0.9932 | **PASS** |
| G2 primary AUROC(RS_q, wrong\|HC) CI lb > 0.5 | 0.969 [0.935, 0.995] (n=96) | **PASS** (lb 0.935 > 0.5; point >= 0.60) |
| G3 placebo paraphrase flip <= 0.30 | 0.0394 (n=482) | **PASS** |
| G4 permutation obs > p95 | obs 0.9695 > p95 0.8942 | **PASS** |
| G5 mechanism fidelity (correct-wrong bf_reverse) CI excl. 0 | mean diff 0.832 [0.745, 0.928] (correct n=88, wrong n=8) | **PASS** |

## Risk@80 (secondary)

- Risk@80 error reduction: **1.000** [0.836, 1.000] (overall HC error 0.0833, n=96).
- All 8 wrong HC items fall in the highest-risk 20% under RS_q.

## Reducibility (reported, not a gate)

- Spearman(RS_q, agreement): 0.3176
- Spearman(RS_q, mean confidence): -0.1841

## Boundaries

- N=8 wrong HC items is small; CIs are pair-grouped but the wrong-N drives wide tails. The
  result supports the pre-registered CI-level gate (lb > 0.5) and the mechanism direction, but
  is a single-point (100-item) validation, not a full-cohort estimate.
- All numbers are on the frozen Round-3 VitaminC cohort subset (first 50 pairs); no label was
  used to select prompts, adapters, or subsets; labels merged only after feature freeze.
- Model is a relay GPT-class model (gpt-6-astra); the relay is a third-party proxy; per-call
  model id is recorded and matches `gpt-6-astra` in every successful record.
