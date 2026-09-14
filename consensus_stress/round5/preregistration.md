# Round 5 Preregistration — Matched-Budget External Baselines and CST-Bench Leaderboard

Status: **FROZEN BEFORE ANY Round-5 model call**. No Round-5 baseline call has been made.
Protocol id: `cs-round5-matched-baselines-cst-bench-20260913`.
Parent protocols: `cs-paper-vitaminc-2026-09-13` (Round 3, Qwen) and
`cs-paper-ling-adapted-20260913-round4` (Ling).
Orchestrator model: server default (not openapi.center). Research models are local only:
Qwen3.5-4B at `http://127.0.0.1:31518/v1/chat/completions` and Ling-3.0-tiny at
`http://127.0.0.1:31520/v1/chat/completions`. No `reasoning_effort` field is sent.
No data or protocol leaves the local machine.

## 1. Frozen cohort and comparison population

- Reuse exactly the Round-3 300 natural VitaminC pairs / 600 items. No reselection,
  replacement, filtering, oracle change, condition change, or outcome-based exclusion.
- The primary model is Qwen; Ling is the secondary model. The evaluated population for a
  model is that model's already-frozen high-consensus (HC) subset, `agreement >= 0.8`
  (Qwen n=567; Ling n=574). The binary target is that model's frozen `consensus_wrong`.
- External baselines are run on all 600 items before labels are merged. If a baseline has
  missing scores, its headline metric is computed on its valid HC rows, while every paired
  difference versus `RS_q` is computed on the exact intersection of valid HC rows.
- Internal comparators (`RS_q`, `R_sym`, `R_PI`, vote agreement, and confidence) are reused
  from the frozen Round-3/Round-4 preoutcome features. No internal score is recomputed or
  retuned.

Frozen input SHA256 values:

- `round3/selection_manifest.json`: `5f575ff873b3243b4916f77ab81269476da937d466eec967eff0934efe39089b`
- `round3/paraphrase_manifest.json`: `5b322c4973328b5323edf8111a4e4195c4a4d895c9890dfb73a8d0f29d514435`
- `round3/preoutcome_features.jsonl`: `d0c588d05211769c14234377d669881d079dacaac0ebaf2ec9326561d967584d`
- `round3/labels_ledger.json`: `770ede3f79b018c47aa982e6cb3f13b9d504b5c14950f7f1a8f6de196ffcbc5a`
- `round4/ling_preoutcome_features.jsonl`: `35e853cf0815cb1428ec8f2ee671993bd1f87ba8b28ade24a630ac4c79bc26bb`
- `round3/records.jsonl`: `ce5280ede80c92f471ff73b1b8fe1c0fc339bd057aae67825e54f7d42a706a08`
- `round4/ling_records.jsonl`: `fc0e32126b3ce0a1c5394d11a706a072611a9fd12797b3624789cc0dda62d4d2`

## 2. Outcome firewall and no post-hoc tuning

- Gold labels and `consensus_wrong` are merged only after all Round-5 baseline records and
  per-item baseline scores are written and hashed.
- No baseline prompt, sampling parameter, aggregation formula, calibration fold, metric,
  operating point, or exclusion rule may be changed after the first Round-5 call.
- Isotonic and temperature calibration are the only label-using baselines. Their labels are
  used only inside pre-specified pair-grouped 5-fold nested out-of-fold (OOF) fits; they are
  not used to choose the prompt, temperature, sample count, aggregation, model, metric, or
  any other baseline. All other baselines and `RS_q` remain outcome-blind.
- If any external baseline exceeds `RS_q`, the result is reported unchanged and discussed;
  metrics, cohort, or operating points must not be switched.

## 3. Common request contract

For every external baseline call:

- OpenAI-compatible `/v1/chat/completions`; model string is exactly the served model.
- Temperature `0.7`; default server top-p; `max_tokens=160`; one deterministic integer
  seed per call; no `reasoning_effort`; no few-shot examples beyond the fixed JSON exemplar.
- The baseline uses agent 0's frozen 2-of-3 evidence view so that all methods face the same
  evidence-access constraints as one agent in the parent protocol.
- The fixed response contract is the Round-4 adapted JSON contract:
  `{"answer":"yes|no","confidence":[0,1],"cited_evidence_ids":[...]}`.
  A strict parse requires exactly those keys (an optional `agent_id` is tolerated and
  ignored), `answer` in {yes,no}, finite confidence in [0,1], and unique in-packet citations.
- There is no repair call. This keeps the per-method call budget at or below 25 even when a
  response is invalid. Parse failures are recorded and treated as missing responses, not as
  labels.
- Exact seed formula: item index `i` in the sorted `cqid` order, sample/replicate `j`,
  `seed = 20260913 + 100*i + j`. For the sampling family `j=0..24`; for the single-agent
  intervention family `j=25..49`, assigned by condition and replicate in the frozen order
  below.
- Caches are content-addressed and model-specific; no Round-3/Round-4 cache is rewritten.

## 4. External baseline families and risk definitions

Two call families are collected for efficiency. Each listed method has a **per-method
budget of 25 calls/item**; the sampling family shares its 25 calls across the four
sampling/confidence methods. The total unique experimental footprint is therefore 50 new
calls/item/model, while no method consumes more than 25 calls/item.

### 4.1 Sampling family (25 calls/item, shared)

Run 25 stochastic calls on agent 0's `original` evidence view. Let valid answers define
empirical probabilities `p_yes`, `p_no`; `M=max(p_yes,p_no)`; and let `c_bar` be the mean
confidence over valid calls. If no call parses, all sampling-family risks are set to 1.

1. **Self-consistency disagreement (Wang et al. style):**
   `risk = 1 - M`.
2. **SelfCheckGPT answer-match (Manakul et al. style):**
   primary answer is the modal valid answer (ties broken by first valid call);
   `risk = 1 - mean(answer == primary)`. Equivalently for binary answers this is
   `1 - (p_yes^2 + p_no^2)`.
3. **Semantic entropy (Kuhn et al. style, binary simplification):**
   yes/no are the semantic clusters; `risk = -(p_yes log2 p_yes + p_no log2 p_no)`,
   normalized by `log2(2)=1`; missing values are treated as zero probability.
4. **Raw sampled mean confidence:** `risk = 1 - c_bar`.
5. **Isotonic-calibrated sampled confidence:** pair-grouped 5-fold OOF isotonic regression
   maps `c_bar` to P(`consensus_wrong`); the held-out predicted probability is the risk.
6. **Temperature-calibrated sampled confidence:** pair-grouped 5-fold OOF temperature
   scaling maps `logit(clamp(c_bar,0.01,0.99))` to P(wrong); the held-out probability is
   the risk. Temperature is fit by labeled log-loss on training folds only.

Fold rule: sort unique `pair_id`, seed 20260913, assign pairs round-robin to folds 0-4;
for each test fold, fit on the other four folds and predict the held-out pairs. This is
identical for both models and both calibrators.

### 4.2 Single-agent intervention family (25 calls/item)

Run five stochastic replicates for each frozen condition in the order
`original, paraphrase, reverse, synthetic_reverse, remove` (25 total). This is the parent
stress protocol degraded from five personas to one fixed agent/persona and five repeats.

For replicate `k=0..4`, let `y0_k` be its valid original answer. Expected responses are:
paraphrase `y0_k`, reverse `flip(y0_k)`, synthetic reverse `flip(y0_k)`; remove remains
descriptive and is not scored, exactly as in the parent protocol. A replicate is usable
only if its original, paraphrase, and reverse calls all parse.

`BF_single = mean over usable replicates of 0.5*f_paraphrase + 0.5*f_reverse`.
`RS_single = -BF_single` (higher is riskier). If no replicate is usable, the score is
missing. Synthetic reverse and remove are collected for audit and budget symmetry but do
not enter the pre-registered score.

## 5. Internal methods included in CST-Bench

All are frozen from the parent rounds and evaluated in the risk direction:

- **RS_q (Consensus Stress Testing):** `-BF_q`, the parent primary score.
- **R_sym:** frozen symmetric intervention score.
- **R_PI:** frozen provenance/intervention score.
- **Vote agreement:** `1 - agreement` (uses 5 original calls).
- **Frozen mean confidence:** `1 - mean_confidence` (uses 5 original calls).

The leaderboard labels `RS_q` as the proposed method and all other rows as baselines.
No row is removed if it wins.

## 6. Metrics, uncertainty, and SOTA rule

For every method and model on that model's HC rows:

- AUROC for `consensus_wrong`, pair-grouped bootstrap with 2,000 replicates and seed
  `20260913 + method_index`.
- Risk@80: error-rate reduction when retaining the lowest-risk 80% of items,
  pair-grouped bootstrap with 2,000 replicates.
- Mean prompt/completion/total tokens per item over the calls required by that method.
  For shared sampling methods, token counts are the shared 25-call family mean and are
  reported as such.
- Paired AUROC and Risk@80 differences are `RS_q - baseline`, computed on the exact
  intersection of valid HC rows, with pair-grouped bootstrap CIs. Positive differences
  favor `RS_q`.
- The primary SOTA claim is Qwen AUROC. A method is reported as matching or beating the
  proposed method if its paired difference CI is <= 0 or its point estimate is >= `RS_q`.
  Ling is secondary and cannot rescue a Qwen loss.
- Ranking is by AUROC point estimate; ties are broken by Risk@80, then lower calls/item.
  CIs must be shown next to every point estimate. Ranking is descriptive, not a gate.

No multiple-comparison correction is applied to this exploratory benchmark table; the
paired CIs are the primary uncertainty summaries. No claim of universal SOTA is permitted.

## 7. Execution and validity reporting

- Expected new calls: 600 items × 25 sampling calls + 600 × 25 intervention calls =
  30,000 per model; 60,000 total if Ling budget permits.
- Run Qwen first. Run Ling only if both services remain healthy. Do not occupy or restart
  GPU4/GPU6. Existing services are used as-is.
- Pipeline validity is reported as parsed calls / attempted calls overall, per family, per
  condition, and per item. A method is not silently repaired or filtered by outcome.
- All records include raw content hash (not necessarily raw content), parsed decision,
  usage, HTTP status, latency, seed, cache key, model, condition, and replicate/sample
  index. Raw content may be retained locally because no data leaves the machine.
- The analysis may begin only after writing and hashing `*_baseline_records.jsonl` and
  `*_baseline_scores.jsonl` for a model.

## 8. CST-Bench package

Create `consensus_stress/benchmark/` with:

- `README.md`: task, cohort, oracle, budget-matching rule, methods, metrics, claim
  boundaries, and reproduction commands.
- `prepare_frozen_cohort.py`: verifies and copies/hashes frozen split inputs without
  reselecting.
- `run_baselines.py`: unified internal/external runner interface.
- `analyze_leaderboard.py`: builds the leaderboard JSON/CSV/Markdown from frozen records.
- `methods.yaml`: machine-readable method definitions and budget metadata.
- `leaderboard.csv` and `LEADERBOARD.md`: method × model results with CIs and budgets.
- No docs/ changes, no git commit/push, and no modification of Round-3/Round-4 frozen code.
