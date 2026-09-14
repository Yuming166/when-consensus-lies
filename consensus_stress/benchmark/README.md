# CST-Bench: Consensus Stress Testing Benchmark

Protocol: `cs-round5-matched-baselines-cst-bench-20260913`
Parent protocols: `cs-paper-vitaminc-2026-09-13` and `cs-paper-ling-adapted-20260913-round4`.

CST-Bench evaluates whether a method can predict, **without seeing the outcome**, when an
already-formed multi-agent consensus is wrong under controlled evidence stress. The primary
comparison is on the frozen 300-pair VitaminC natural-pair main split. A BoolQ balanced
specificity split is packaged as a diagnostic negative control, not as part of the current
matched-budget leaderboard.

## 1. Task definition

- An item contains a claim, a model-agnostic evidence packet, and a fixed 2-of-3 partition
  for an agent. Five frozen personas independently answer the same binary question under
  five evidence conditions.
- The formed consensus is the majority answer of the five original-condition agents.
- High consensus (HC) is `agreement >= 0.8`. The target is `consensus_wrong`, i.e. the
  formed majority answer disagrees with the sealed gold label.
- A risk score must be computed **before** gold labels or correctness are merged. Higher
  risk means a greater predicted probability that the consensus is wrong.
- The proposed method, `RS_q`, is outcome-blind expected-response faithfulness:
  `RS_q = -BF_q`, where `BF_q` averages agent faithfulness over paraphrase and natural
  evidence reversal. Low faithfulness under stress yields high risk.

## 2. Frozen data construction

### VitaminC main split

- Source: official VitaminC test split.
- Natural pairs have the same `case_id`, claim, and page, with exactly one SUPPORTS and one
  REFUTES row. Eligibility requires character ratio >= 0.85 and token Jaccard >= 0.70.
- The frozen selection is 300 pairs / 600 items, label-symmetric by construction. No item is
  reselected, replaced, or filtered in Round 5.
- Each pair yields a SUPPORTS item and a REFUTES item sharing the same claim. Natural
  reversal swaps the paired counter-evidence. A deterministic non-decision-relevant
  distractor is shared by both items.
- The exact frozen selection, paraphrase artifacts, records, preoutcome features, and sealed
  labels are under `frozen/vitaminc/`; hashes are in `frozen/manifest.json` and `frozen/SHA256SUMS`.

### BoolQ specificity split

- The frozen BoolQ split is a balanced yes/no specificity test packaged under
  `frozen/boolq/`.
- Round 3 found a direction reversal and gate failure on this split. It is retained as a
  negative control showing that the mechanism is specific to natural counter-evidence rather
  than arbitrary perturbation. It is not included in the Round-5 leaderboard.

## 3. Expected-response oracle

The frozen oracle is decision-relevance-aware and label-free:

- **Original:** answer the binary evidence question.
- **Paraphrase:** the expected answer is the same as that agent's original answer.
- **Natural reverse:** the expected answer is the flip of that agent's original answer.
- **Synthetic reverse:** the expected answer is the flip of the original answer; this is a
  secondary condition and does not enter `RS_q`.
- **Remove:** no forced response; descriptive only.
- `BF_q` uses paraphrase and natural reverse. `RS_q=-BF_q` is the risk direction.

## 4. Models and agent configuration

- Primary: Qwen3.5-4B at `http://127.0.0.1:31518`.
- Secondary: Ling-3.0-tiny at `http://127.0.0.1:31520`.
- The parent method uses five frozen personas and five conditions: 25 calls/item.
- External baselines use agent 0's view and fixed prompts. Sampling calls use temperature
  0.7, `max_tokens=160`, deterministic seeds, and no `reasoning_effort`.
- No data or protocol is sent to an external service.

## 5. Matched-budget baselines

Every external method has at most 25 calls/item. Token cost is reported as the secondary
accounting dimension.

### Shared sampling family (25 calls/item)

Twenty-five stochastic calls are made on agent 0's original view. Four label-blind methods
and two supervised calibration methods derive scores from this shared call family:

1. **Self-consistency disagreement:** `1 - modal answer frequency`.
2. **SelfCheckGPT answer-match:** `1 - probability that two sampled answers match`.
3. **Binary semantic entropy:** normalized entropy over yes/no clusters.
4. **Raw sampled confidence:** `1 - mean sampled confidence`.
5. **Isotonic confidence:** pair-grouped 5-fold OOF isotonic calibration to error probability.
6. **Temperature confidence:** pair-grouped 5-fold OOF temperature scaling converted to
   error risk.

The runner collects 25 sampling calls plus 25 intervention calls per item/model, so the unique
experimental footprint is 50 calls/item/model. Nevertheless, each listed method consumes at
most 25 calls/item; the sampling family is shared only as an efficiency optimization.
Calibration is the only label-using baseline and is evaluated strictly OOF.

Because this task has binary answers, self-consistency disagreement, SelfCheckGPT answer-match,
and binary semantic entropy are monotonic transforms of the same yes/no sample distribution.
They can therefore have identical AUROC/Risk@80 rankings. They are still reported separately to
preserve method fidelity to the cited baseline families.

### Single-agent intervention family (25 calls/item)

One fixed agent/persona is sampled five times under each of the five parent conditions. The
pre-registered score is `RS_single=-BF_single`, where `BF_single` averages replicate
faithfulness over paraphrase and natural reverse. This directly tests whether multiple agent
personas are necessary.

## 6. Frozen gates inherited from the parent protocols

The proposed method's parent gate is not re-run or retuned in Round 5. On each model's HC
subset, the frozen within-model gate requires all of:

1. pipeline validity >= 0.95;
2. primary AUROC CI lower bound > 0.5 and point estimate >= 0.60;
3. macro-label AUROC CI lower bound > 0.5;
4. worst-label AUROC CI lower bound > 0.5;
5. paraphrase placebo/infidelity <= 0.30;
6. observed AUROC above the pre-registered permutation 95th percentile;
7. reducibility checks versus agreement and confidence;
8. for the formal Risk@80 phase, the paired Risk@80 CI must exclude zero in the favorable
   direction.

Round 5 is a benchmark/baseline comparison, not a new rescue gate. It reports external
baseline validity, coverage, paired CIs, and token/call accounting without changing any
parent gate.

## 7. Metrics and uncertainty

For each method and model on that model's HC subset:

- **AUROC** for predicting `consensus_wrong`, with pair-grouped bootstrap 95% CI
  (2,000 replicates).
- **Risk@80**: error-rate reduction when retaining the lowest-risk 80% of items, with
  pair-grouped bootstrap 95% CI.
- **Calls/item** and mean prompt/completion/total tokens per item.
- **Paired differences** are `RS_q - baseline` on the exact intersection of valid HC rows.
  Positive AUROC or Risk@80 differences favor `RS_q`.
- Ranking is descriptive: AUROC point estimate, then Risk@80, then lower calls/item. No
  multiplicity correction is applied; paired CIs are the primary uncertainty summaries.

## 8. Reproduction

From the repository root, using the specified Python environment
(`/storage/gaoym/sp500-forecastability-lab/.venv/bin/python`):

```bash
python consensus_stress/benchmark/prepare_frozen_cohort.py

python consensus_stress/benchmark/run_baselines.py \
  --model qwen --workers 24

# Optional secondary model
python consensus_stress/benchmark/run_baselines.py \
  --model ling --workers 24

python consensus_stress/benchmark/build_baseline_scores.py --model qwen
python consensus_stress/benchmark/build_baseline_scores.py --model ling
python consensus_stress/benchmark/analyze_leaderboard.py --models qwen ling
```

Outputs:

- Round-5 records and score files: `consensus_stress/round5/`.
- Detailed analysis JSON: `consensus_stress/round5/analysis/baseline_leaderboard.json`.
- Dependency pin: `requirements.txt`.
- Benchmark outputs: `methods.yaml`, `leaderboard.json`, `leaderboard.csv`, and `LEADERBOARD.md`.

The packaged frozen artifacts do not include response caches. Re-running the baseline calls
requires the two local model endpoints to be available.

## 9. Claim boundaries

- The primary claim is limited to the frozen VitaminC natural-pair protocol and the two
  model families evaluated here.
- Qwen is primary; Ling is secondary. A Ling result cannot rescue a Qwen loss.
- BoolQ is a specificity negative control, not evidence of universal transfer.
- The table does not support claims of zero-shot transfer, universal SOTA, or superiority
  over all possible reliability methods.
- If an external baseline wins, the win is retained in the leaderboard and discussed rather
  than removed or relabeled.
