# Research State — Frozen Baseline Snapshot (Phase 0)

Audit date: 2026-09-12. Auditor: consensus-stress orchestrator (DeepSeek v4 flash Max).
Scope: docs/protocols/*, docs/results/*, docs/research_brief.md, docs/asof_provenance_faithfulness.md,
docs/data_contract.md, README.md in `/home/gaoym/when-consensus-lies-publish-20260911`, plus frozen
code reference at `/home/gaoym/.tmp_sp500_naacl_symmetric_20260909`.

## 1. What the baseline study is

"When Consensus Lies" studies whether an already-formed multi-agent consensus can be
ranked by pre-outcome risk before the ground-truth label is revealed. Five fixed persona
agents (literal evidence, skeptical auditor, consistency checker, counterfactual reasoner,
minimal judge) receive environment-assigned evidence views (2-of-3 evidence units on BoolQ;
page-pair evidence on VitaminC) and must answer yes/no (BoolQ) or SUPPORTS/REFUTES (VitaminC)
with confidence and cited evidence IDs, no chain-of-thought, no abstention. Paired evidence
interventions (remove / reverse / substitute) are applied, and observable response behavior
is compressed into frozen risk scores:

- R_PI  = 0.1*D_inert + 0.3*flip_inertia + 0.6*frac_shared  (BoolQ)
- R_sym = 0.3*reverse_inertia + 0.7*intervention_disagreement (VitaminC, selected on Qwen dev, frozen)

Labels live in a sealed outcome ledger; all pre-outcome routes are frozen before label access.

## 2. Completed / positive results (frozen)

| Experiment | Verdict | Core numbers |
|---|---|---|
| Synthetic V3 (rule agents, leave-one-mechanism-out) | PASS | conditional-provenance AUROC 0.977 [0.971, 0.982]; AURC 0.233 |
| BoolQ V12.1 (Qwen3.5-4B, 358 q, 7160 calls, R_PI) | PASS | AUROC 0.705 [0.620, 0.781]; Risk@80 0.220 -> 0.133 (-0.087) |
| VitaminC V3.16.1 (Qwen+Ling, 578 items, 23120 calls, R_sym) | PASS both | Qwen AUROC 0.839 [0.802, 0.873]; Ling 0.727 [0.689, 0.764] |
| VitaminC V3.15.2 (Ling on BoolQ evidence) | PASS aggregate-only | AUROC 0.640 [0.558, 0.717] |

## 3. Failed / invalidated / boundary results (frozen, preserved)

See known_failures.md for the full list. Summary:
- S&P500 V1 and V2 routing endpoints FAILED (AURC difference CIs include 0).
- Synthetic V4 learned router FAILED primary (better calibration only; drifted under mechanism holdout).
- BoolQ label-asymmetry: no-label AUROC 0.213 (Qwen) / 0.120 (Ling); label-invariant detection NOT established.
- Cross-model item-level risk Spearman ~0.29 in both settings: only aggregate transfer.
- V10 invalidated pre-formal; V12 auxiliary abort; V3.15/V3.15.1 transport aborts; V3.16
  Ling SUPPORTS adequacy boundary (17 errors < 20); V3.16.1 70 pages had prior distractor exposure.
- Synthetic V3 matched-coverage is post-hoc only.

## 4. What is frozen (do not modify)

- baseline scripts/results in the code repo (read-only reference)
- docs/ in this repository (frozen)
- R_PI / R_sym weights, high-consensus threshold 0.8, router coverage 0.8, bootstrap seeds,
  dataset hashes, model endpoints (Qwen3.5-4B at 127.0.0.1:31518, Ling at 31520)
- the numbers in baseline_results.json as historical references

## 5. Gap that this program addresses (from the plan)

The current risk scores use fixed intervention families (remove/reverse/substitute) and
measure invariance/aggregate change (inertia, flip rate, disagreement, shared source) but do
NOT evaluate whether the collective response was the *expected* response to the semantic
change of the evidence, do NOT separate semantic-preserving stability from semantic-changing
responsiveness, and do NOT use an intervention-strength/stress trajectory. The upgrade target
is outcome-blind consensus stress testing / expected-response faithfulness with the claim
"agreement is not itself evidence that the consensus is appropriately evidence-responsive."

## 6. Gate 0 checklist

- [x] All protocol/result/brief docs read and summarized in this file + baseline_manifest.json
- [x] baseline_results.json reproduces the documented numbers verbatim (machine-readable)
- [x] known_failures.md preserves every invalidated/failed/boundary result
- [x] outcome_firewall.md codifies forbidden inputs and freeze order
- [x] Baseline code/config identified as frozen in the reference repo; no baseline file modified
- [x] No outcome leakage mechanism found in the frozen protocol (labels sealed; forbidden inputs listed)
- [x] Venv verified: /storage/gaoym/sp500-forecastability-lab/.venv (pandas 3.0.5, pyarrow 25.0.1,
      numpy 2.5.2, scikit-learn 1.9.0, scipy 1.18.1, PyYAML 6.0.3); torch absent but not required
      for HTTP-based pilot calls
- Gate 0 decision: PASS. Baseline frozen before any new experiment.

## 7. Boundary of this audit

- No live re-run of the 23k+ baseline calls was performed (would require ~46k local model calls);
  the documented numbers are trusted as frozen protocol artifacts and recorded verbatim.
- If later evidence contradicts a frozen number, the contradiction is recorded in the registry,
  not silently patched.
