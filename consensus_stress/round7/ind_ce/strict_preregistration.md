# Round-7 W2 — Strict Protocol Preregistration Supplement (TARGET_SPEC 2026-09-15)

Status: frozen per user `TARGET_SPEC.md` (created 2026-09-15 00:12, in this directory).
Parent protocol: `cs-paper-ind-ce-20260914-round7-w2` (v1 preregistration, run completed 00:13).
This supplement supersedes the E_ind/placebo construction of v1; cohort, personas, contract,
inference conditions (natural/ind/placebo x 5), gates G1/G3/G4/G5, metrics, firewall, and
negative-result discipline are unchanged unless stated here.

## 1. E_ind_strict (strict independent counter-evidence)
- Generation is **claim-only, dual-direction, item-blind**:
  - For each of the 50 unique claims: generate 2 sentences supporting "the claim is TRUE"
    (slots 0,1) and 2 sentences supporting "the claim is FALSE" (slots 0,1) — 4 calls/claim = 200.
  - The generation prompt contains **only the claim text and the requested direction**
    (TRUE/FALSE); it never contains the item role, item id, original evidence, or any
    gold-derived polarity.
  - No post-hoc use of evaluation outcome; temp 0.7, max_tokens 300, deterministic seeds,
    content-addressed cache, retries (same client).
- **Offline assignment (frozen gold, per TARGET_SPEC):** E_ind_strict(i) = the "claim FALSE"
  sentence for `:support` items and the "claim TRUE" sentence for `:refute` items (opposes
  item i's gold). Assignment uses the frozen manifest item role; the assigned text is a fixed
  artifact and never leaks gold/target into any inference prompt (inference shows only
  claim + evidence packet).
- Audit (30-item sample, seed 20260914): (a) decision-relevance of the ASSIGNED E_ind_strict
  (expected = opposite of item role) >= 0.80; (b) independence vs E_j: token_jaccard
  median<=0.55 / p90<=0.70 / max<=0.80, character_ratio median<=0.75, LCS<0.75 per sentence;
  (c) static check: generation prompt contains no item role/gold tokens.

## 2. Matched placebo E_pm
- For each claim: generate 2 neutral, topic-matched, decision-irrelevant sentences
  (slots 0,1) — 2 calls/claim = 100. Same topic as the claim, similar length/tone to
  E_ind_strict, but **neither supports nor refutes the claim**.
- Audit (same 30-item sample): decision-irrelevance — the audit model should NOT classify
  E_pm as clearly supporting OR refuting the claim; gate: <= 0.30 clearly-support rate AND
  <= 0.30 clearly-refute rate on the sample (i.e., majority neutral).

## 3. Inference (strict)
- Conditions: `natural` (byte-identical v1/round6 reverse layout; reuse v1 records),
  `ind` (E01=E_ind_strict_a, E02=E_ind_strict_b, E03=distractor),
  `placebo` (E01=E_pm_a, E02=E_pm_b, E03=distractor).
- 100 items x 5 agents x 3 conditions = 1,500 logical calls; natural replays from v1 cache;
  ~1,000 fresh calls. Same gates: pipeline valid>=0.95; Delta_CE>0 with CI excluding 0;
  placebo flip <= 0.30 (G4 as in v1; if E_pm flip > 0.30 -> report honestly per TARGET_SPEC §6,
  do NOT re-optimize).

## 4. Metrics (unchanged from v1)
P(flip|natural/ind/placebo), Delta_CE [pair-grouped CI 2000, seed 20260914+0], S_natural/S_ind/
S_combined/S_placebo/S_pair AUROC+Risk@80 on HC (seed 20260914+1/2), OOF logistic increment,
rho(S_natural, S_ind). Outcome firewall: features frozen (hashed) before labels merge.

## 5. Negative-result discipline (TARGET_SPEC §6)
If Delta_CE not significantly >0, or placebo not clean, or S_ind shows no increment -> record
the negative result explicitly; do not tune the method to force a positive.

## 6. Outputs
All under `consensus_stress/round7/ind_ce/` with `strict_` prefixes (artifacts, records,
summaries) plus updated `analysis/ind_ce_decision.md`/`SUMMARY.md` reporting both the v1
(target-direction prompt) and strict (claim-only) results. No git commit.
