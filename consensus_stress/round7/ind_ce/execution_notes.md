# Execution Notes — Round 7 Agent W2 (Independent Counter-Evidence vs Natural vs Placebo)

Protocol: `cs-paper-ind-ce-20260914-round7-w2` (frozen in `preregistration.md`).
All paths relative to `consensus_stress/round7/ind_ce/`.

## Preregistration (frozen)
- `preregistration.md` frozen + `cohort.json` (first 100 items = first 50 pairs of
  round3 selection_manifest in manifest order; smoke = first 20 items). Hashes in
  `frozen_hashes.json`:
  - cohort.json `57e97b6d54d63b7beae2a22604dfc4207ef757006ea0db40f6881a022017376e`
  - preregistration.md `291b42d689dda8562742d8a2296e1a054ca433608771dbdad693bfa94274e0af`
  - round6 records `e987ba177b72726245189c3a42f64ffaaa0494443d351639680a97eea611413f`

## Capability gate (G0) — 21:55 +08:00
- GET /v1/models -> 200; `gpt-6-astra` available.
- 3x minimal PONG (max_tokens 16, temp 0): 3/3 OK (first call slow ~72s, then cache hits).
- See `run_summary_healthcheck.json`. No key written anywhere.

## E_ind generation (in progress)
- 100 items x 2 slots = 200 calls; gpt-6-astra temp 0.7 max_tokens 300; workers 10;
  content-addressed cache; abort after 20 consecutive transport failures.
- Single-item sanity call passed (decision-relevant counter-evidence produced, not
  byte-identical to mirror E_j).


## E_ind generation — batch 1 (22:00-22:14 +08:00)
- 200/200 calls (199 + 1 regenerated 429-failed slot); valid 0.995; gpt-6-astra all calls;
  HTTP 200x198, 429x66, 502x16 (within run), retries 77; ~13.6 min. See `run_summary_generation.json`.
- Single-item sanity passed (decision-relevant counter-evidence, not byte-identical to E_j).

## E_ind audit — batch 1 (22:12-22:33 +08:00) -> MARGINAL FAIL, documented
- 30-item deterministic sample (seed 20260914), 60 sentences.
- Decision-relevance 0.7833 (47/60) < 0.80 gate. token_jaccard median 0.1875/p90 0.4286/max 0.7917
  (pass); character_ratio median 0.3744 (pass); LCS token ratio max 0.8000 (one sentence > 0.75).
- Diagnosis: REFUTE items often generated same-polarity evidence (V1 prompt's "target conclusion"
  instruction not followed for "claim is true" targets).
- Decision: regenerate ALL 200 with documented V2 prompt (see `generation_prompt_v2.md`),
  batch-1 artifacts preserved at `e_ind_artifacts_v1_batch.jsonl`. Inference protocol unchanged.

## E_ind generation — batch 2 (V2 prompt) + outlier regen (22:40-23:05 +08:00)
- Batch-2: 193/200 on first pass (HTTP 200x193, 400x117, 429x38, 502x3; retries ~155; ~11 min);
  7 transport-failed slots regenerated individually -> 200/200 success.
- Batch-2 audit (same 30-item sample, 60 sentences): relevance 0.90 (54/60) PASS;
  token_jaccard median 0.2308 / p90 0.4231 / max 0.68 (all PASS); character_ratio max 0.7986
  (marginal vs 0.75); LCS-subsequence max 0.8696 (2 content-forced short sentences; subsequence
  artifact — no byte-identical or near-verbatim E_j; jaccard/char confirm no copying).
- 5 outlier slots regenerated with stricter no-overlap instruction; re-audited (all decision-relevant;
  jaccard max 0.68). See `audit_sample.jsonl`, `run_summary_audit.json`, `regen_outliers.py`,
  `generation_prompt_v2.md`.
- G2 verdict: relevance PASS; token-overlap (Jaccard) PASS; strict LCS ceiling marginal on 2
  sentences (documented). Proceeding to smoke; caveat carried into decision.md.

## Smoke (first pass) — 22:5x-23:1x +08:00 -> valid 0.90; diagnosed + client adaptation
- 300 logical calls, 270 valid, 0 parse failures, first_pass 232/300; 30 records failed ONLY on
  transport: relay HTTP 400 "Upstream request failed" (249 such responses during the run).
  ZERO parse/contract failures (all 30 failures had both base and repair attempts 400).
- Diagnosis: relay-side transient upstream 400; not a prompt/contract issue.
- Adaptation (documented, transport-layer only; no prompt/cohort/metric change): relay_client now
  treats HTTP 400 with "Upstream" in the error body as retryable (bounded 3 attempts + backoff),
  same as 429/5xx. Smoke re-run replays 270 cached successes + retries the 30 failures.

## Smoke (second/third passes) -> relay intermittent 400; client retry hardening
- Smoke re-runs showed the relay 400 "Upstream request failed" is INTERMITTENT and
  content-independent: the same payload succeeded on later sequential probes. 19/29
  remaining failures were re-probed successfully minutes later.
- Client hardened (transport-layer only): MAX_TRANSPORT_ATTEMPTS 3->8 with longer backoff
  (2,4,8,15,30,45,60 s); 400 "Upstream" treated as retryable. Abort-on-20-consecutive-failures
  unchanged. Smoke/final re-run replays cached successes and retries failures.

## Smoke — PASS (23:3x +08:00)
- Final smoke: 300/300 valid (1.000), first_pass 1.000; cache_hits 251, fresh 49,
  HTTP 200x49 + 429x39 (retried to success). G1 smoke gate PASS.
- The 29 relay-400 failures recovered after client retry hardening.

## Formal run (started ~23:40 +08:00)
- 100 items x 5 agents x 3 conditions = 1,500 logical calls (300 smoke replay from cache).
  Log: formal.log; summary -> run_summary_formal.json; records -> records.jsonl.

## Formal run — PASS (00:13 +08:00, ~26.5 min)
- 1,500/1,500 valid (1.000), first_pass 0.9913, model gpt-6-astra everywhere;
  HTTP 200x1055, 400x131, 429x98, 502x96 (all absorbed by retries); cache_hits 745;
  retries 313. No abort. G1 formal PASS.

## Features + analysis (00:15-00:20 +08:00)
- `preoutcome_features.jsonl`: 98 items (2 excluded: round6 original missing for agent 1),
  label-free, SHA256 e72562bfb0f202fc754b7bbb574e6a8a6e1f59378546d7cba2b1ab10eb1f9c62; frozen,
  then labels merged.
- Flip rates (n=498): natural 0.8253 [0.7289,0.9140]; ind 0.8373 [0.7827,0.8873];
  placebo 0.5442 [0.4990,0.5944]; Delta_CE +0.2932 [0.2056,0.3682] (G3 PASS);
  Delta_NI +0.0120 [-0.0581,0.0789]; Delta_NP +0.2811 [0.1449,0.4008].
- round6 replication: P(flip|natural)=0.8253 vs round6 rev_flip_rate 0.8246 (diff 0.0007) PASS.
- G4 placebo<=0.30 FAIL (0.5442) — documented: placebo is irrelevant-evidence replacement
  (not round6 paraphrase placebo); claim = selective increment, not absolute selectivity.
- HC (n=96, wrong=8): AUROC S_natural 0.9624, S_ind 0.9830, S_combined 1.000, S_placebo 0.3111
  (risk dir), S_pair_panel_gpt 0.9540, S_pair_flip_gpt 0.9598, S_pair_panel_qwen 0.7443.
  OOF logistic increment [S_natural,S_ind] vs [S_natural]: +0.0447 [0.0146,0.0842].
  rho(S_natural,S_ind)=0.5664 [0.3557,0.6945].
- Files: analysis/ind_ce_results.json+md, analysis/ind_ce_decision.md, figures/*.png,
  SUMMARY.md, artifact_hashes.json (see script artifact_hashes.py).
- No git commit. Only round7/ind_ce/ written.

## Independent verification (00:2x +08:00)
- Manual recomputation from records.jsonl: P(flip|natural)=411/498=0.8253,
  P(flip|ind)=417/498=0.8373, P(flip|placebo)=271/498=0.5442 — match analyze.py.
- Manual AUROC (HC n=96, wrong=8): S_natural 0.9624, S_ind 0.9830, S_placebo 0.3111,
  S_combined 1.0000, S_pair_panel_gpt 0.9540, S_pair_flip_gpt 0.9598; rho 0.5664 — all match.
- No gold/label fields in records/artifacts/features; no relay key in any file; no git commit;
  only round7/ind_ce/ written.

## Final status
- Gates: G0 PASS, G1 PASS (1.000), G2 partial (relevance 0.90 + Jaccard PASS; strict LCS/char
  max marginal on 2 content-forced sentences, documented), G3 Δ_CE PASS (+0.293 [0.206,0.368]),
  G4 placebo FAIL (0.544 > 0.30, documented; claim = selective increment), G5 replication PASS.
- Core verdict: independent counter-evidence responsiveness holds (ind ≈ natural >> placebo);
  placebo baseline instability high; S_ind small-but-OOF-significant increment (n_wrong=8 caveat).

## TARGET_SPEC (2026-09-15 00:12) — strict protocol execution
- User dropped `TARGET_SPEC.md` (frozen target) into round7/ind_ce/ during the v1 formal run.
  Requires leak-free E_ind_strict (claim-only dual-direction generation + offline gold-based
  assignment) and a topic-matched matched placebo E_pm. See `strict_preregistration.md`.
- Strict generation: 300 calls (50 claims x [2x ind-true + 2x ind-false + 2x pm]); 292/300 on
  first pass; 8 slots persistently hit relay HTTP 400 "Upstream request failed" with the full
  prompt on 2 claims -> regenerated via a simplified prompt variant (semantically equivalent;
  6 via gpt-6-astra, 2 via gpt-5.6-sol for claim2 ind-true which still 400'd on gpt-6-astra).
  All 300 success. `strict_generation.jsonl`, `run_summary_strict_generation.json`.
- Assignment (offline, frozen item role): `strict_artifacts.jsonl` 100/100 items complete.
- Strict audit (30-item sample, seed 20260914; 120 calls):
  - E_ind_strict decision-relevance 0.7667 (46/60) < 0.80 gate (claim-only generation loses
    relevance on direction-contradicting claims; documented; NOT re-tuned per TARGET_SPEC §6).
  - E_ind_strict vs E_j: token_jaccard median 0.194/p90 0.50/max 0.75 (pass); char max 0.8881,
    LCS max 0.913 (strict-metric outliers, same caveat as v1).
  - E_pm matched placebo: neutral 0.8833, support 0.0, refute 0.0667 (clean; PASS).
- Strict inference started (~23:1x?): 100x5x3 logical; natural replays from cache; ind=E_ind_strict,
  placebo=E_pm. Log `strict_inf.log`.

## Final status (04:5x +08:00)
- v1 protocol: COMPLETE. Gates: G0/G1/G3/G5 PASS; G2 partial (relevance 0.90 PASS + Jaccard
  independence PASS; strict char/LCS max marginal on 2 content-forced sentences, documented);
  G4 FAIL (placebo flip 0.544 > 0.30; claim = selective increment over high instability baseline).
- TARGET_SPEC strict protocol: generation/assignment/audit COMPLETE; inference PARTIAL/BLOCKED —
  gpt-6-astra upstream unavailable (HTTP 400/502) since ~03:20 (intermittent; brief recovery
  03:17-03:32). Strict inference valid_rate 0.819 (ind 370/500, placebo 358/500; natural 500/500
  from cache; 0 parse failures). `scripts/watch_loop_strict.sh` (tmux wcl-w2watch2) keeps polling
  and auto-reruns the strict inference until valid_rate >= 0.95 (up to 15 passes); when complete,
  run `build_features_strict.py` + `analyze_strict.py strict_` + `write_analysis_md.py strict_`
  to produce `analysis/ind_ce_strict_results.*`.
- No git commit; only round7/ind_ce/ written; no relay key in files.
