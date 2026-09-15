# Round-7 W2b STRICT — Execution Notes

Protocol: `cs-paper-ind-ce-strict-20260915-round7-w2b`. All artifacts under
`consensus_stress/round7/ind_ce_strict/` (isolated from `round7/ind_ce/`; read-only reuse of
frozen Round-3/4/6 and W2 records). No git commit.

## 0. Concurrent-process note (external)

During this run a separate agent process (`round7/ind_ce/scripts/gen_strict_artifacts.py`,
started 00:26) was writing its own strict-style artifacts into `round7/ind_ce/` — a directory
this protocol is forbidden from writing. It used its own cache and prompt templates. We did
not read or modify it; it only contended for relay throughput. Our results use only our own
isolated artifacts.

## 1. Preregistration freeze

- `preregistration.md` frozen and hashed BEFORE any experimental call:
  SHA256 `e1c1db40d9d724ed2c04b9f0b5f759bbe05d281cb693eac9e9bd675e29fcae53`
  (recorded in `artifact_hashes.json`).
- `cohort.json`: first 25 pair_ids of `round3/selection_manifest.json` in manifest order
  (support-then-refute per pair) = 50 items. Smoke = first 10 pairs (20 items).
- G0 healthcheck: relay OK, `gpt-6-astra` available, 3/3 probes OK
  (`run_summary_healthcheck.json`).

## 2. Generation (claim-only, label-free)

- 50 calls (25 dual-direction + 25 placebo), gpt-6-astra, temp 0.7, max_tokens 300,
  8 transport attempts with backoff; HTTP stats and token usage in
  `run_summary_generation.json` (200: 59, 429: 58, 502: 3; transport_retries 61).
- Input = claim text ONLY (prompt_log recorded per row; no item_id / polarity / gold /
  evidence / original answers). Raw outputs cached content-addressed (immutable).
- **Parser correction (documented, post-freeze, uniform):** the preregistered parser
  rejected 5/50 calls (all HTTP 200) because it accepted only exact `<T>|`/`<F>|` markers
  and split sentences on any `[.!?] ` (breaking decimals like `1.5` and initials like
  `K.`, `Jr.`). A corrected parser (marker-variant mapping + abbreviation/initial/decimal-
  aware splitting) was applied uniformly to all 50 cached raw outputs. Verified: all 45
  originally-OK rows yield byte-identical parsed text; exactly the 5 originally-rejected
  rows are recovered (45/50 -> 50/50). Prompts, model, seeds, temperature, and calls are
  unchanged. See `run_summary_parser_correction.json` (raw hash before `85d9ecdc...`,
  after `39afb216...`). This is a parser fix, not method tuning.

## 3. Offline gold assignment

- `assign_strict.py` (the only label-consuming step, run after generation was complete):
  gold=SUPPORTS -> SEGMENT_FALSE, gold=REFUTES -> SEGMENT_TRUE. 50/50 assigned
  (`run_summary_assignment.json`, `e_ind_strict_artifacts.jsonl`).

## 4. Audit (30 items = first 15 pairs; label-blind judge, gpt-6-astra temp 0)

`run_summary_audit.json` + `audit_sample.jsonl`:
- Direction-compliance (decision-relevance): **0.7833 overall (47/60) — below the 0.80
  gate (G2 marginal FAIL)**; on the assigned segments (the ones actually used as
  counter-evidence) compliance = **24/30 = 0.80 (exactly at gate)**. 6 assigned segments
  judged not clearly directional (e.g., genre-mixing evidence that does not directly
  negate the claim). This is a real quality signal: claim-only generation yields
  mostly-but-not-always directional counter-evidence.
- Independence vs mirror evidence (max over both pair evidences, label-blind bound for
  E_j): token jaccard median 0.185 / p90 0.333 / max 0.467; char ratio median 0.363 /
  max 0.549; LCS max 0.565 — **PASS** (well below gates). Strict textual independence
  from the mirror construction is clean.
- Generation-input cleanliness: **PASS** (30/30 prompts are exactly the frozen templates
  with only the claim; no item_id, no `:support`/`:refute`, no SUPPORTS/REFUTES/gold, no
  evidence text).
- Placebo: irrelevance 0.80 (**PASS**, exactly at gate), format match 1.0 (**PASS**).
- Judge transport: 86 cache hits, 56 retries; all 30 items answered.

## 5. Inference

- Smoke (20 items, 200 calls): valid_rate **0.995** (199/200) — G1 PASS
  (`run_summary_smoke.json`).
- Formal (50 items, 500 calls): valid_rate **0.998** (499/500) — G1 PASS
  (`run_summary_formal.json`; 257 cache hits, 242 fresh, 143 transport retries).
- Single failure: `5ea2d97dc9e77c0009cdb2be:f1704a989c8a:support` agent 4 `ind_strict`,
  transport failed after 8 attempts (`Upstream request failed` 400). Cell excluded from
  flip stats; item-level `S_ind_strict` for that item is None (all-5 rule) -> excluded
  from item-level AUROC rows (n=46 vs 47).
- Single-slot packet `E01` for both conditions; prompts contain only claim + E01.
  `natural` condition reused from W2 round-7 records (no rerun).

## 6. Features freeze (label-free)

- `preoutcome_features.jsonl` (49 items; 1 item excluded for missing frozen round-6
  original answer of agent 1, per prereg §2.1), SHA256
  `f040260413ea6350f6c9b889046e2ae80b0287612430a826c1d0dba533c447cc` recorded in
  `preoutcome_features_meta.json` BEFORE label merge. Verified label-free (no
  gold_label/consensus_wrong fields).

## 7. Analysis (labels merged after feature freeze)

`analysis/strict_results.json` / `.md`. Headline numbers (50-item cohort, pair-grouped
bootstrap 2000, seed family 20260915):

| metric | value |
|---|---|
| P(flip|ind_strict) | 0.7258 [0.6466, 0.8115] (n=248) |
| P(flip|pm) | 0.5141 [0.4600, 0.5772] (n=249) |
| P(flip|natural, reused) | 0.8434 [0.7177, 0.9478] (n=249) |
| **Δ_CE** | **+0.2118 [0.1160, 0.3097]** (G3 PASS) |
| Δ_ind − natural | −0.1176 [−0.2539, 0.0350] |
| placebo ceiling | 0.5141 > 0.30 (**G4 FAIL**) |
| S_ind_strict AUROC (HC n=46, wrong=3) | 0.624 [0.286, 0.856] |
| S_natural AUROC (HC n=47, wrong=3) | 0.973 [0.912, 1.000] |
| RS_q AUROC | 0.943 [0.860, 1.000] |
| S_ind_strict − S_natural (paired AUROC) | −0.349 [−0.714, −0.091] |
| S_ind_strict − RS_q (paired AUROC) | −0.318 [−0.670, −0.106] |
| ρ(S_natural, S_ind_strict) | 0.033 [−0.044, 0.478] |
| OOF logistic increment (S_ind over S_natural) | +0.004 [−0.074, 0.047] (n=46) |
| Leakage audit (299 rebuilt prompts) | PASS, sha-match 1.0 |

Caveats: HC has only 3 wrong items (6.4%); all AUROC/Risk@80/OOF estimates on HC are
wide and unstable; OOF logistic on 3 positives is near-meaningless and reported as a
diagnostic only.

## 8. Gate summary

- G0 capability: PASS. G1 pipeline (smoke/formal >= 0.95): PASS (0.995 / 0.998).
- G2 audit: independence + input-cleanliness + placebo format/irrelevance PASS;
  direction-compliance 0.783 overall (marginal FAIL; assigned-segment 0.80).
- G3 Δ_CE > 0 with CI lb > 0: **PASS** (+0.2118 [+0.1160, +0.3097]).
- G4 placebo <= 0.30: **FAIL** (0.5141).
- G5 diagnostic |ind−natural|: 0.1176 (reported, no gate).

## 9. Negative-result handling (TARGET_SPEC §6)

- Placebo not clean (G4 fail) -> recorded, not tuned.
- S_ind_strict provides NO predictive increment over S_natural / RS_q (paired AUROC
  significantly NEGATIVE vs both; OOF increment CI covers 0; ρ ≈ 0) -> recorded, not
  tuned. See `decision.md` for the three-path interpretation.
