# PAPER EVIDENCE LEDGER

Freeze date: 2026-09-21. This is the single pre-paper traceability map for the current evidence boundary.

## Frozen main story

> A small number of executable counterfactual probes can reveal item-level answer correctness reliability on a structurally eligible FinQA cohort, replicate across Qwen3.5-4B and Ling-3.0-tiny, and remain predictive on a frozen source-deduplicated eligible DEV cohort.

This is a diagnostic-correlate claim, not a claim of universal reliability, latent reasoning fidelity, causal validity, or high counterfactual reasoning ability.

## Evidence map

### Consensus stress testing (CST) — `PASS_BOUNDED_WITH_MECHANISM_REFRAME`

**Paper role:** Primary evidence for outcome-blind intervention-response measurement and direction-sensitive expected-response faithfulness; report the direction account, not an overlap/rigidity mechanism.

**Allowed claim:** On frozen VitaminC natural-pair cohorts, expected-response faithfulness / directional response features ranked high-consensus errors beyond confidence, agreement, and frozen provenance baselines under placebo and permutation controls.

**Boundary:** CST results are benchmark- and protocol-bounded; do not turn them into causal cognition or universal multi-agent reliability claims.

| experiment | status | paper-safe result |
|---|---|---|
| `cs-pilot-vitaminc-conf-20260913` | `PASS` | AUROC(RS_q=-BF_q, wrong|HC)=0.912 [0.848, 0.973] on a 50-pair confirmation cohort; placebo clean and permutation-validated; label-symmetric gate passed. |
| `cs-phase4-reliability-20260913` | `PASS` | Combined high-consensus analysis: RS_q AUROC 0.906 [0.865, 0.944]; Risk@80 CI lower bound positive; paired gains over R_sym/R_PI; OOF calibration analysis retained as secondary. |
| `cs-paper-vitaminc-20260913` | `PASS` | Paper-scale 300-pair / 600-item cohort: RS_q AUROC 0.943 [0.924, 0.960], worst-label SUPPORTS 0.917 [0.819, 0.999], Risk@80 0.846 [0.638, 0.981], paired gains vs R_sym/R_PI. |
| `round10-2x2-20260915` | `DIRECTION_DOMINANT` | Direction contrast +0.44 [0.24, 0.65]; consensus-opposing independent CE flips wrong consensus at 0.946 (35/37); construction/near-duplicate effect does not survive direction control in the available clean subset. |

### S&P 500 bounded negative/stop-escalation boundary — `NO_ESCALATION_REFRAME`

**Paper role:** Stress-test and limitation boundary; prevents importing CST/PECR positive results into a claim of universal behavioral-state or prospective financial reliability.

**Allowed claim:** The bounded S&P 500 pilot was structurally harder than the previous benchmark, but the behavioral-state candidate B8 did not beat B6 and the protocol stopped before teacher/prospective escalation.

**Boundary:** No causal cognition, alpha, profitable trading, prospective reliability gain, teacher benefit, or deployment claim.

| experiment | status | paper-safe result |
|---|---|---|
| `sp500-f0-hardness-20260918` | `PASS_BOUNDED_HARDNESS` | Ling static AUROC 0.6040 and Hy 0.5569; 161/166 wrong-majority dates and 14/87 5/5-wrong dates; F0 passed only to authorize intervention-validity audit. |
| `sp500-wave3-b678-20260918` | `NO_ESCALATION` | On 469 complete DEV units, B6 AUROC 0.6320 [0.5546, 0.7051] vs B8 0.6177 [0.5430, 0.6950]; B8-B6 -0.0143 [-0.0560, 0.0287]. Decision: KEEP_B6_NO_ESCALATION. |
| `sp500-zero-shot-boundary-v314` | `FORMAL_NEGATIVE` | Zero-shot Qwen3.6 HoVer transfer failed its frozen safety/adequacy gates despite valid transport; 5 fixes/4 harms and no verified transfer. |
| `sp500-v316-adequacy-boundary` | `NO_CONFIRMED_JOINT_PASS` | Qwen and Ling performance gates passed, but the frozen joint gate was withheld because Ling had only 17 high-consensus SUPPORTS errors (<20 minimum); report as a power/adequacy boundary, not as a performance null. |

### Program-Executable Counterfactual Reliability (PECR) — `PASS_OFFICIAL_DEV_SIGNAL_VALIDATION`

**Paper role:** Primary new method signal: executable counterfactual fidelity predicts original answer correctness; two fixed probes provide a lower-cost approximation.

**Allowed claim:** On structurally eligible FinQA cohorts, full CEF and frozen S2 predict original correctness for Qwen3.5-4B and Ling-3.0-tiny; the official DEV one-shot uses 126 source-deduplicated eligible items.

**Boundary:** Absolute transformed-world accuracy remains modest; two probes are a lossy approximation; the cohort is not all DEV; this is a diagnostic correlate, not proof of latent reasoning or causality.

| experiment | status | paper-safe result |
|---|---|---|
| `pecr-v0.2-train-discovery` | `PASS_DESCRIPTIVE_TRAIN_ONLY` | CEF AUROC 0.8998 [0.8210, 0.9659], shuffle p approximately 1e-4; high-vs-low CEF correctness 83.3% vs 10.5%. |
| `pecr-v0.3-source-disjoint-holdout` | `PASS_HELDOUT_CONFIRMATION` | Qwen full CEF AUROC 0.8165 [0.7463, 0.8809] on 200 source-file-disjoint TRAIN items; D-only OOF AUROC 0.5525 vs D+CEF 0.7938. |
| `pecr-v0.4-prospective-sparse-replication` | `PASS_PROSPECTIVE_SPARSE_SIGNAL_REPLICATED` | Qwen full CEF AUROC 0.9017; S2 0.8843; MLP S2 0.8936; retention ratio secondary because calls included all four relevant worlds. |
| `pecr-v0.5-actual-sparse-cost-audit` | `PASS_ACTUAL_SPARSE_COST_AUDIT` | On actual sparse-only calls, S2 AUROC 0.8007; 30.0% total-call reduction and 37.5% counterfactual-call reduction; 50-item full-teacher control retention 0.7414 is secondary/underpowered. |
| `pecr-v0.6-cross-model-ling` | `PASS_CROSS_MODEL_SPARSE_REPLICATION` | Frozen S2 AUROC 0.7857 [0.7000, 0.8667] on Ling-3.0-tiny; original accuracy 18.0%; global and within-operation nulls passed. |
| `pecr-v0.7-larger-teacher-control` | `PASS_COMPRESSION_QUANTIFICATION` | On 200 same-item TRAIN controls, Qwen S2/full retention 0.8079 [0.6920, 0.9081] and Ling 0.8122 [0.6573, 0.9420]; full-minus-S2 gaps approximately 0.072 and 0.070. |
| `pecr-v0.8-official-dev-one-shot` | `PASS_OFFICIAL_DEV_SIGNAL_VALIDATION` | On 126 eligible source-deduplicated DEV items: Qwen full/S2 AUROC 0.9008/0.8317; Ling 0.8477/0.8379; S2 CIs above 0.5; confidence 0.5181/0.5412; no retuning or probe reselection. |

## Abstract eligibility

| claim | abstract? | evidence | wording guard |
|---|---|---|---|
| `C1` Executable counterfactual fidelity is a reproducible item-level correctness diagnostic on eligible FinQA cohorts. | yes | `pecr-v0.2-train-discovery`, `pecr-v0.3-source-disjoint-holdout`, `pecr-v0.8-official-dev-one-shot` | predicts / is associated with original correctness; do not say proves reasoning fidelity |
| `C2` Two fixed executable probes provide a lower-cost sparse diagnostic that remains predictive across Qwen3.5-4B and Ling-3.0-tiny. | yes | `pecr-v0.5-actual-sparse-cost-audit`, `pecr-v0.6-cross-model-ling`, `pecr-v0.7-larger-teacher-control`, `pecr-v0.8-official-dev-one-shot` | substantial and cross-model-stable fraction; do not say equivalent or almost all |
| `C3` CST shows why directional, executable response tests are more informative than generic output sensitivity in the bounded evidence-intervention setting. | no | `cs-pilot-vitaminc-conf-20260913`, `cs-phase4-reliability-20260913`, `round10-2x2-20260915` | direction-sensitive expected-response faithfulness; drop overlap/rigidity mechanism |
| `C4` The S&P 500 branch is a negative/stop-escalation boundary rather than a positive universality result. | no | `sp500-f0-hardness-20260918`, `sp500-wave3-b678-20260918`, `sp500-zero-shot-boundary-v314`, `sp500-v316-adequacy-boundary` | bounded hardness and negative transfer/adequacy evidence; no causal or financial-performance claim |

## Locked non-claims

- Do not call the 126-item DEV cohort the full DEV split.
- Do not use S2 retention > 1 on Ling DEV as a capability improvement; retention is a ratio secondary endpoint.
- Do not describe transformed-world absolute accuracy as strong counterfactual reasoning.
- Do not resurrect generic flip rate, paraphrase sensitivity, or S&P B8 superiority as the main signal.
- Do not merge Qwen-to-Ling PECR transfer with Qwen-Hy answer-repair or with the S&P negative branch.

## Required companion audits

- `PECR_DEV_ELIGIBILITY_AUDIT_20260921.{json,md}`: 883 → 182 → 126 attrition and structural comparison.
- `PECR_METADATA_REPAIR_AUDIT_20260921.{json,md}`: output-blind repair trail and explicit missing raw before-hash boundary.
- `STRONG_RELIABILITY_BASELINE_PLAN_20260921.md`: pre-registered cost-matched baseline extension; not yet run.
- `PAPER_ARGUMENT_MEMO_20260921.md`: CST → negative S&P boundary → PECR argument chain.

## Re-run

`python prepaper_audit/build_prepaper_audit.py`

The JSON ledger contains artifact paths, existence, byte counts, and SHA-256 hashes where artifacts are present.
