# Round 4 Preregistration — Cross-Model Procedure/Score Transfer (Ling-3.0-tiny)

Status: **FROZEN before any Round-4 Ling-3.0-tiny call**. No Ling service is running at preregistration time; only the endpoint's unavailability was checked.
Protocol id: `cs-paper-ling-adapted-20260913-round4`.
Parent protocol: `cs-paper-vitaminc-2026-09-13` (Round 3).
Orchestrator: DeepSeek v4 flash Max (server default; no openapi.center).
Research models: frozen primary Qwen3.5-4B @ `127.0.0.1:31518`; second model Ling-3.0-tiny @ `127.0.0.1:31520`.
All data and protocol artifacts remain local and are not sent to external services.

## 1. Scientific question (unchanged)

Does the Round-3 consensus-stress procedure and its aggregate reliability signal
`RS_q = -BF_q` transfer from Qwen3.5-4B to Ling-3.0-tiny on the same frozen,
model-agnostic VitaminC natural-pair artifacts? The primary mechanism claim is that
wrong high-consensus decisions are comparatively rigid under natural evidence reversal.
Item-level ordering agreement is explicitly secondary and is not a gate.

## 2. Frozen cohort and artifacts (no reselection)

- Reuse the complete Round-3 paper-scale cohort: **all 300 pairs / 600 items** from
  `consensus_stress/round3/selection_manifest.json`.
- Reuse the frozen model-agnostic artifacts: paraphrases, natural supports/refutes
  evidence, distractors, partitions, and expected-response oracle. No evidence text,
  claim, paraphrase, distractor, or oracle definition is changed.
- Reuse the sealed label ledger only after preoutcome features are frozen.
- The same item/pair IDs are used for paired Qwen–Ling analysis.

## 3. Model-capability contract adaptation (pre-registered before calls)

Round-3 Ling failed the execution layer because Ling omitted `agent_id`, although it
usually emitted the substantive fields. Round 4 therefore changes only the response
transport contract:

1. The user prompt no longer asks for `agent_id`.
2. Every prompt contains the same frozen JSON shape exemplar:
   `{"answer":"yes","confidence":0.75,"cited_evidence_ids":[]}`
   The exemplar's values are explicitly labeled illustrative and are identical across
   every item, agent, condition, and stage.
3. The parser requires `answer`, `confidence`, and `cited_evidence_ids`.
   It validates: answer in `{yes,no}`; confidence finite in `[0,1]`; citations a
   unique list of non-empty strings drawn from the assigned packet (an empty list is allowed
   when the packet is empty). No `agent_id` is required or
   validated; if the model unexpectedly emits one, it is ignored as transport metadata.
4. Agent identity is bound server-side by the task dispatcher to the frozen
   `agent_index` and its frozen persona/partition; the record stores both. The model
   is never trusted to self-identify.
5. One JSON-repair retry is allowed exactly as in Round 3. A call is valid only if it
   passes the adapted parser; there is no post-hoc imputation or filtering.

**Why this is contract accommodation, not scientific relaxation:** the removed field was
metadata for call integrity, not an input to the oracle, `BF_q`, `RS_q`, consensus,
confidence, citation sharing, agreement, gates, or any scientific endpoint. The
replacement is stronger provenance: deterministic server-side task assignment instead
of model self-report. The substantive task, evidence, conditions, expected responses,
scoring formula, direction `RS_q=-BF_q`, and gates are unchanged. The adaptation is
applied uniformly before observing Round-4 Ling outcomes, not selected on valid subsets
or labels.

## 4. Model calls (frozen)

- 5 agents × 5 conditions × 600 items = **15,000 Ling calls**.
- Conditions remain exactly `original`, `paraphrase`, `reverse`,
  `synthetic_reverse`, `remove`.
- Temperature 0, deterministic seed per frozen agent, max tokens 160, no
  `reasoning_effort`.
- Ling is served only on GPU5 with the supplied vLLM command. GPU4/GPU6 must not be used.
- Separate round-4 cache and records; no Round-3 records are rewritten.

## 5. Within-model Ling gate (frozen)

Evaluate on the Ling high-consensus (HC) subset, `agreement >= 0.8`, with
pair-grouped bootstrap (2,000 replicates), using `RS_q=-BF_q` as risk (higher = riskier):

- **Pipeline:** valid calls / 15,000 >= 0.95.
- **Primary AUROC:** `AUROC(RS_q, Ling consensus_wrong | HC)`, CI lower bound > 0.5
  and point estimate >= 0.60.
- **Macro-label AUROC:** CI lower bound > 0.5.
- **Worst-label AUROC:** CI lower bound > 0.5.
- **Paraphrase placebo:** per-agent paraphrase infidelity <= 0.30.
- **Permutation:** observed primary AUROC > pre-registered permutation 95th percentile.
- **Reducibility:** absolute Spearman(`RS_q`, agreement) < 0.9 and absolute
  Spearman(`RS_q`, mean confidence) < 0.9.

All criteria must pass. If pipeline < 0.95, no substantive gate is evaluated on a
model-dependent valid subset; the outcome is execution-layer FAIL. In that case, the
only pre-registered fallback is Qwen3.6-35B-A3B-FP8 **if and only if** it can be safely
served on two available RTX 4090s with tensor parallelism and without disturbing GPU4/GPU6;
otherwise report FAIL plus diagnostics. No protocol weakening is permitted.

## 6. Cross-model analyses (frozen primary/secondary ordering)

On the same 600 items, after Ling preoutcome features are frozen:

### 6.1 Primary: procedure/score transfer

- **Qwen-score transfer:** for each item, use the frozen Round-3 Qwen `RS_q` value to
  rank Ling's own consensus-wrong outcome; report pair-grouped AUROC and Risk@80 CI.
- **Ling procedure score:** compute Ling's own `RS_q` with the unchanged formula and
  evaluate it against Ling's outcome; report pair-grouped AUROC and Risk@80 CI.
- **Paired comparison:** pair-grouped bootstrap difference between Qwen-transfer
  `RS_q` and Ling's own `RS_q` on the identical Ling HC items, for AUROC and Risk@80.
- Transfer is supported if both score/procedure evaluations have primary AUROC CI
  lower bound > 0.5; the paired comparison quantifies whether aggregate transfer is
  comparable or degraded, but does not replace the within-model gate.

### 6.2 Primary: mechanism transfer

- Compare Ling `bf_reverse` (natural-evidence expected-response fidelity) between
  Ling-correct and Ling-wrong HC groups.
- Mechanism transfer is supported if wrong-group reverse fidelity is lower than
  correct-group reverse fidelity, with a pair-grouped bootstrap CI for the mean
  correct-minus-wrong difference excluding zero.
- The existing discrete `reverse` condition is sufficient; a continuous lambda curve is
  optional and only reportable if separately budgeted after the main result.

### 6.3 Secondary (not a gate)

- Item-level Spearman correlation between Qwen `RS_q` and Ling `RS_q` on shared HC items.
- This may be low without invalidating aggregate/procedure transfer.

## 7. Outcome firewall

Gold labels are merged only after Ling records and preoutcome features are frozen.
Forbidden score inputs before merge: gold label, gold binary, correctness,
`consensus_wrong`, and any outcome-derived selector. Labels are never passed to Ling or
used to choose probes, adapt prompts, or filter the cohort.

## 8. Optional Phase 5 active-probing pilot (contingent, pre-registered)

Only if the cross-model main line passes and time/call budget remains, run an offline
pilot on frozen Round-3 Qwen records. Compare one reversal probe versus the full
fixed five-condition profile at matched per-item model-call accounting, without using
labels for probe selection. Report AUROC/Risk@80 and paired uncertainty. This is an
exploratory addition and cannot rescue or alter any Phase-6 gate.

## 9. Outputs

All new artifacts are written under `consensus_stress/round4/`: preregistration,
registry entry, Ling records, run summary, preoutcome features, analysis JSON/Markdown,
figures as needed, and final summary. No git commit/push; no changes to `docs/` or
frozen Round-3 code.
