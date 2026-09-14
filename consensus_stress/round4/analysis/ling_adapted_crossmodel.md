# Round 4 — Cross-Model Procedure/Score Transfer (Ling-3.0-tiny): PASS

Protocol: `cs-paper-ling-adapted-20260913-round4` (frozen before all Round-4 Ling calls).
Cohort: the complete frozen Round-3 paper-scale VitaminC cohort, **300 pairs / 600 items**.
Research model: Ling-3.0-tiny on GPU5. Qwen results are the frozen Round-3 records; no Qwen
calls were rerun.

## 1. Contract adaptation and pipeline

The only protocol adaptation was response transport: Ling no longer self-reports `agent_id`.
The task dispatcher binds the frozen `agent_index`/persona/partition server-side, and the parser
validates `answer`, `confidence`, and `cited_evidence_ids`. A frozen JSON exemplar is present in
every prompt. This does not change evidence, oracle, conditions, `BF_q`, `RS_q=-BF_q`, or gates.

- Calls: **15,000 / 15,000 valid (100.0%)**; first-pass valid **14,992 / 15,000 (99.95%)**.
- Every condition (`original`, `paraphrase`, `reverse`, `synthetic_reverse`, `remove`) has
  **3,000 / 3,000 valid calls**.
- Pipeline gate (>=0.95): **PASS**.

## 2. Ling within-model gate

Ling HC subset: **574 / 600 items** (`agreement>=0.8`), **119 wrong** (20.73% HC error).

| Frozen criterion | Result | PASS |
|---|---:|---|
| Primary AUROC(RS_q=-BF_q, wrong\|HC) | **0.896 [0.873, 0.916]** | Yes (CI lb>0.5; point>=0.60) |
| Macro-label AUROC | **0.919 [0.895, 0.944]** | Yes |
| Worst label (SUPPORTS) | **0.881 [0.834, 0.928]** | Yes |
| Paraphrase placebo agent infidelity | **0.061** | Yes (<=0.30) |
| Permutation | observed **0.896** > 95th percentile **0.564** | Yes |
| Reducibility | Spearman vs agreement **-0.148**; vs confidence **-0.050** | Yes (absolute values<0.9) |
| Risk@80 (descriptive) | **0.422 [0.274, 0.591]** | CI excludes zero |

**Ling within-model gate: PASS (8/8).** Per-label AUROCs: SUPPORTS 0.881 [0.834, 0.928];
REFUTES 0.957 [0.934, 0.977].

## 3. Cross-model procedure/score transfer

On the identical Ling HC items, with Ling's own outcome labels:

| Signal | AUROC [CI] | Risk@80 [CI] |
|---|---:|---:|
| Frozen Qwen item-level `RS_q` applied to Ling errors | **0.723 [0.682, 0.765]** | **0.296 [0.148, 0.439]** |
| Ling's own unchanged `RS_q` procedure | **0.896 [0.873, 0.916]** | **0.422 [0.274, 0.591]** |
| Paired diff: Qwen-transfer − Ling-own | **-0.173 [-0.217, -0.130]** | **-0.126 [-0.226, -0.062]** |

Both transfer components have AUROC CI lower bounds above 0.5, so the pre-registered transfer
criterion passes. However, Ling's own procedure score is significantly better than direct
item-level Qwen-score transfer. Item-level Spearman(Qwen RS_q, Ling RS_q) is only
**0.496** on 574 HC items. This supports the intended bounded claim: **the stress-testing
procedure and aggregate reliability signal transfer across model families, while item-level
risk ordering is partly model-dependent.**

For context on the same full cohort, frozen Qwen achieved AUROC **0.943 [0.924, 0.960]** and
Risk@80 **0.846 [0.636, 0.981]** on 567 HC items. Ling had a higher HC error rate (20.73% vs
Qwen 11.46%), so the two models do not have identical failure distributions.

### Paired outcome overlap

Across all 600 items: same consensus **511/600**; both wrong **57**, Qwen-only wrong **19**,
Ling-only wrong **70**, both correct **454**. On the 543 items where both models are HC:
same consensus **480/543**; both wrong **54**, Qwen-only wrong **10**, Ling-only wrong **53**,
both correct **426**.

## 4. Mechanism transfer: natural evidence reversal

On Ling HC items, natural-evidence reverse fidelity (`bf_reverse`) is:

- Correct consensus: **0.703**
- Wrong consensus: **0.029**
- Correct-minus-wrong: **0.674 [0.629, 0.719]** (pair-grouped bootstrap CI)

The CI excludes zero, so the mechanism gate **passes**: wrong Ling consensus is much more rigid
under natural evidence reversal than correct consensus. This replicates the central Qwen
mechanism in a different model family.

## 5. Optional Phase-5 active-probing pilot (offline, exploratory)

At a matched budget of one stress condition × 5 agents per item on the frozen Qwen HC cohort:

- Active reversal probe: AUROC **0.931 [0.912, 0.948]**; Risk@80 **0.884 [0.575, 1.000]**
- Fixed label-blind four-condition rotation: AUROC **0.593 [0.529, 0.659]**; Risk@80
  **0.095 [-0.155, 0.342]**
- Paired active-minus-fixed: AUROC **+0.338 [+0.269, +0.405]**; Risk@80
  **+0.790 [+0.580, +0.849]**

This exploratory offline pilot passes both pre-registered uncertainty criteria and strengthens
the NAACL narrative: probe selection, not merely more probing, drives reliability information
gain. It uses no new model calls and is not a Phase-6 gate.

## 6. Claim boundary

PASS supports cross-family transfer on this frozen VitaminC natural-pair protocol for
Qwen3.5-4B and Ling-3.0-tiny. It does not claim universal transfer, superiority over all
reliability baselines, or zero-shot generalization to arbitrary datasets. The BoolQ negative
result from Round 3 remains a specificity boundary: natural counter-evidence is essential.
