# CS Pilot Round 2 — VitaminC Natural Pairs: Expected-Response Faithfulness

Protocol: `cs-pilot-vitaminc-2026-09-13` (preregistration.md). Date: 2026-09-13.
Model: Qwen3.5-4B @ 127.0.0.1:31518 (no reasoning_effort). Machine-readable: analysis.json.
Raw records: phase2_pilot/records.jsonl. Frozen features: phase2_pilot/preoutcome_features.jsonl.

## 1. Pipeline integrity

- 100 VitaminC natural pairs (200 items, exactly 100 SUPPORTS + 100 REFUTES), page-disjoint
  and disjoint from all frozen V3.16/V3.16.1 target+distractor pages (1076 excluded pages).
- Contrast gates: character_ratio >= 0.93 and token_jaccard >= 0.85 per pair; all pass.
- Offline decision-relevance audit: 28/30 (93.3%) items judged decision-relevant
  (2 flagged: San Siro/Meazza same-stadium pair; Psylocke pronoun pair) -> selection stands
  per frozen rule (>= 80%).
- Paraphrase artifacts: 300/300 usable (100%); audit 20/20 meaning-preserving.
- Agent calls: 5000/5000 valid (100%); first-pass 4999+4997. Stage 1 = 50 pairs, Stage 2 = 50 pairs.
- Outcome firewall: records and preoutcome features contain no label fields; labels merged only
  after features were frozen.

## 2. Population (high-consensus subset, agreement >= 0.8)

- 195/200 items high-consensus (97.5%); wrong HC = 34 (17.4% of HC).
- By native label: SUPPORTS 99 HC / 11 wrong (11.1%); REFUTES 96 HC / 23 wrong (24.0%).
  More errors on REFUTES (consistent with a mild SUPPORTS/yes bias in the panel).

## 3. E1 — agent-level expected-response accuracy (all 200 items, 1000 calls/condition)

| condition | oracle | accuracy |
|---|---|---|
| paraphrase (semantic-preserving) | Y* = Y0 | 0.972 |
| reverse (natural counter-evidence swap) | Y* = flip(Y0) | 0.651 |
| synthetic_reverse ("it is false that: X") | Y* = flip(Y0) | 0.449 |

Interpretation: agents are highly stable under semantic preservation (2.8% flip), moderately
responsive to a genuine natural evidence reversal (65%), and only weakly responsive to the
synthetic negation prefix (45%) — the natural reversal is the decision-relevant intervention,
as designed.

## 4. E2 — consensus-level faithfulness (high-consensus, 195 items)

| quantity | wrong consensus (n=34) | correct consensus (n=161) |
|---|---|---|
| BF_q (mean para+reverse faithfulness) | 0.503 | 0.883 |
| BF_paraphrase | 0.918 | 0.991 |
| BF_reverse | 0.088 | 0.775 |
| BF_synthetic_reverse | 0.535 | 0.430 |
| remove flip rate (descriptive) | 0.659 | 0.544 |

Wrong consensus is markedly UNRESPONSIVE to natural evidence reversal (8.8% flip vs 77.5%):
exactly the pre-registered "unresponsive to semantic change => risky" profile.

## 5. E3 — primary metric, literal frozen orientation

AUROC(BF_q, consensus_wrong | HC) = 0.099; 95% CI [0.054, 0.153]; n=195.
The literal frozen gate required CI lower bound > 0.5 (round-1 numeric gate). NOT met -> the
literal gate FAILS. This failure is a PREREGISTRATION SIGN DEFECT: the frozen numeric gate
(AUROC > 0.5) encodes "higher BF_q => wrong", which contradicts the protocol's own frozen
substantive direction ("higher BF_q => lower risk", section 8 of the preregistration). The
result is decisively in the frozen substantive direction (CI entirely below 0.5).

## 6. Direction-consistent orientation (risk score = -BF_q; higher = riskier)

AUROC(-BF_q, wrong | HC) = 0.901; 95% CI [0.847, 0.946].

| gate (direction-consistent form) | result | pass |
|---|---|---|
| primary CI lower bound > 0.5, point >= 0.60 | 0.901 [0.847, 0.946] | YES |
| macro-label CI lower bound > 0.5 | 0.901 macro, CI [0.851, 0.953] | YES |
| worst-label point > 0.5 | SUPPORTS 0.886 [0.815, 0.944]; REFUTES 0.926 [0.860, 0.973]; worst 0.886 | YES |
| C1 placebo (paraphrase flip) | agent 2.8% / consensus 1.0% <= 0.30 | YES |
| C2 permutation (risk orientation) | obs 0.901 > 95th pct 0.620 | YES |
| reducibility | Spearman(BF_q, agreement) 0.254, Spearman(BF_q, conf) 0.201; AUROC(-BF_q) at agreement==0.8: 0.95 (n=11) | YES (not reducible) |

Stage consistency (internal replication): stage 1 AUROC(-BF_q) = 0.909 [0.859, 0.950];
stage 2 = 0.886 [0.793, 0.967]. Both strongly positive and consistent.

## 7. Baselines (AUROC on same target; paired diff vs -BF_q)

| score | AUROC [95% CI] | paired diff vs -BF_q [CI] |
|---|---|---|
| -BF_q | 0.901 [0.847, 0.946] | — |
| R_sym (frozen) | 0.846 [0.788, 0.894] | +0.055 [+0.016, +0.096] |
| R_PI (frozen) | 0.680 [0.611, 0.751] | +0.221 [+0.165, +0.283] |
| mean confidence | 0.332 [0.257, 0.415] | +0.568 [+0.481, +0.663] |
| agreement | 0.445 [0.377, 0.502] | +0.456 [+0.369, +0.550] |

-BF_q significantly exceeds every baseline (all paired-diff CIs exclude 0), including the
frozen R_sym (modest but significant) and R_PI (large).

## 8. Mechanism

Wrong consensus = the panel answers without responding to the decisive evidence: it gives the
same answer under both the original and the naturally-reversed evidence (BF_reverse 0.088 vs
0.775 for correct consensus), i.e., evidence-insensitive consensus is risky. The synthetic
negation prefix is a weak, partly noisy intervention (45% response; wrong items flip MORE
under it: 0.535 vs 0.430), confirming that the natural pair reversal is the decision-relevant
intervention and that a relevance-aware oracle matters (round-1 lesson). Placebo is clean, so
the low reverse responsiveness of wrong consensus is not general instability.

## 9. Verdict

- Literal frozen numeric gate (AUROC(BF_q, wrong) CI lb > 0.5): FAIL — preregistration sign
  defect (numeric gate contradicted the protocol's own frozen substantive direction).
- Frozen substantive hypothesis (higher BF_q => lower risk; unresponsive/unstable => risky):
  SUPPORTED strongly, label-symmetric, placebo-clean, permutation-validated, stage-consistent,
  and superior to frozen R_PI/R_sym and confidence/agreement on the pilot cohort.
- No post-hoc sign flip: the substantive direction was frozen before any round-2 agent call
  and is not changed. The literal gate is reported as FAIL; a corrected direction-consistent
  gate is pre-registered for a FRESH confirmation cohort before any additional agent call
  (see confirmation_preregistration.md).
