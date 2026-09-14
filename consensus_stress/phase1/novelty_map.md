# Phase 1 — Novelty Map (Consensus Stress Testing)

Audit date: 2026-09-12. Method: HYBRID audit.

## Audit method and coverage boundaries (honest label)

- LIVE retrieval was attempted and partially succeeded on 2026-09-12:
  - Pass 1: arxiv full-text + Crossref, 20 queries x 20 rows -> `live_search_raw.jsonl` (400 rows).
  - Pass 2: arxiv title-precise, 20 queries -> `live_search_raw2.jsonl` (31 rows).
  - Pass 3 (targeted known-paper title checks): arxiv API returned HTTP 429 rate-limit for all rows;
    DBLP returned non-JSON responses; Semantic Scholar returned 429. Those targeted checks were NOT
    live-verified in this run.
- Every row below is tagged:
  - `[LIVE-verified]` = found in this run's arxiv/Crossref output with date;
  - `[model-knowledge, not live-verified this run]` = from training knowledge; date/venue from memory,
    may be stale; flagged because live verification was rate-limited.
- No claim of exhaustiveness. "No one has done X" is NEVER asserted without a dated source; instead we
  state "no live hit found for query Q on 2026-09-12 within max_results".

## The five candidate concepts

### C1. Expected-response faithfulness (agent/consensus level)

Definition: for intervention T: e -> T(e), define expected behavioral response Y*(T) from the
transformation semantics alone (same-answer for semantic-preserving; flip for explicit polarity
reversal; no-forced-response for removal/weak), and measure BR(T) = 1[Y(T) == Y*(T)].

Closest work:
- Counterfactual faithfulness evaluation of attribution methods (arxiv 2408.11252, 2024-08-21)
  [LIVE-verified]: uses counterfactuals to test whether attribution methods track model behavior.
  Unit = single model's attribution, not multi-agent consensus; no expected-response accuracy metric.
- Faithfulness of rationale/grounded-generation evaluation ("Precision Is Not Faithfulness",
  arxiv 2606.09376, 2026-06-08) [LIVE-verified]: coverage-aware faithfulness of generated claims vs
  ground truth; object = model output vs evidence, single model, labels involved.
- ERASER benchmark for rationalized NLP models (DeYoung et al., ACL 2020)
  [model-knowledge, not live-verified]: measures whether rationales are faithful via sufficiency/
  comprehensiveness (remove rationales, measure score drop) — single-model explanation faithfulness.
- Measuring Faithfulness in Chain-of-Thought Reasoning (Lanham et al., 2023)
  [model-knowledge, not live-verified]: perturb CoT and measure answer changes — single model.
- CREPE / false-presupposition QA [model-knowledge]: tests sensitivity to false presuppositions.

Attack questions:
1. Is C1 reducible to known faithfulness metrics? Partially: for the polarity-reversal condition,
   "expected response = flip" is the complement of existing inertia/flip-rate features already used
   in R_PI/R_sym. The genuinely new parts are (a) scoring the EXPECTED response as accuracy over a
   pre-registered transformation semantics, (b) doing it at CONSENSUS level for a multi-agent panel,
   (c) the semantic-preserving axis (robustness) that known single-model faithfulness metrics do not
   jointly measure.
2. Is a multi-agent formulation necessary? For C1 alone, no — a single model could have
   expected-response accuracy. The multi-agent consensus formulation is what differentiates.
3. Closest competing paper: Counterfactual attribution faithfulness (2408.11252) + CoT faithfulness
   (Lanham et al.). Neither evaluates an already-formed multi-agent consensus nor reports
   pre-outcome error prediction.

Differentiation verdict: PARTIALLY novel as an object; the consensus-level expected-response
measurement with transformation-derived oracle (no labels) is a defensible new measurement.

### C2. Consensus Stress Testing

Definition: treat interventions as probes applied to an ALREADY-FORMED consensus, evaluated
outcome-blind, measuring whether the collective response is appropriately evidence-responsive.

Closest work:
- "Evidence-State Reliability Under Controlled Degradation" (arxiv 2608.21559, 2026-08-21)
  [LIVE-verified]: controlled evidence degradation in multi-stage LLM pipelines; evidence-state
  reliability (completeness/groundedness/consistency/usability). Overlaps in "controlled evidence
  change + reliability", but unit = pipeline evidence state, not consensus response appropriateness;
  no expected-response oracle; no error prediction.
- REST: Stress Testing Large Reasoning Models by Asking Multiple Problems at Once (arxiv 2507.10541,
  2025-07-14) [LIVE-verified]: stress tests reasoning models by packing many problems into one
  prompt; unit = single model task load, not evidence transformation of a formed consensus.
- METAL: Metamorphic Testing for LLM qualities (arxiv 2312.06056, 2023-12-11) [LIVE-verified]:
  metamorphic relations on inputs and check output invariances — closest methodology to "apply
  transformation, check expected property", but single-model quality attributes, not consensus error
  prediction; metamorphic relations are usually invariance-style, not expected-directional-response.
- Stress Test Evaluation for NLI (Naik et al., 2018) [model-knowledge, not live-verified]:
  controlled sentence perturbations for NLI — single-model robustness evaluation with labels,
  no consensus, no pre-outcome error prediction.
- CheckList (Ribeiro et al., ACL 2020) [model-knowledge, not live-verified]: behavioral testing with
  capability tests (invariance, directional expectation, minimum functionality) — this is the closest
  conceptual ancestor of "expected behavioral response"; but applied to a single model's capabilities,
  not to ranking already-formed multi-agent consensus errors before labels.

Attack questions:
1. Does it predict unrevealed future consensus error? CheckList/METAL/NLI stress tests do NOT predict
   error; they describe behavior. This is the differentiation to defend empirically.
2. Is it just metamorphic testing? Metamorphic testing checks invariants (output should stay same).
   Consensus stress testing checks a MIX: invariance under semantic preservation AND directional
   response under semantic change, then uses the resulting profile to rank error risk. The novelty
   is the use for selective prediction, not the transformation technique.
3. Multi-agent necessity: yes for this concept — the object is the consensus.

Differentiation verdict: differentiated on the outcome-blind selective-prediction use of controlled
evidence stress on a formed multi-agent consensus.

### C3. Consensus Stress Curve (perturbation-strength trajectory)

Definition: parameterized stress level lambda in [0,1], measure A_q(lambda) = consensus agreement
(or expected-response fidelity) after stress; derived: stress area, breakpoint, robustness radius.

Closest work:
- Robustness/perturbation curves: adversarial robustness literature measures accuracy vs
  perturbation budget (e.g., "Robustness radius" in certified robustness; Madry et al. 2017-2018)
  [model-knowledge, not live-verified]: single model, input-space adversarial budget, no consensus,
  no expected-response semantics.
- "Are Compressed Language Models Less Subgroup Robust?" (arxiv 2024-03-26) [LIVE-verified pass1,
  noisy match]: subgroup robustness vs compression; not a consensus stress curve.
- Deep learning testing "stress" curves and model robustness surfaces (METAL, robustness gym)
  [LIVE-verified pass1]: no consensus agreement-vs-strength trajectory.

Attack questions:
1. Is a stress curve just an ROC/AURC-style risk-coverage curve renamed? Risk-coverage curves vary
   the ROUTING threshold; a stress curve varies the EVIDENCE STRESS level. Different axis. But AURC
   style summary (area) is a known aggregate.
2. Is breakpoint = certified robustness radius? Similar shape, different object (consensus agreement
   under evidence stress vs worst-case input perturbation).
3. Feasibility: needs a continuous, meaningful stress knob on evidence (e.g., fraction of units
   reversed/removed). For BoolQ (3 units, 2-of-3 views) a coarse lambda grid is possible.

Differentiation verdict: differentiated only if the stress curve is defined on EVIDENCE semantics
(consensus response trajectory) and used for reliability ranking; risk of being "components
combined" (robustness curve + consensus) is real and must be defended by the pre-outcome error
prediction result.

### C4. Robustness-Responsiveness Map

Definition: separate robustness to semantic-preserving changes from responsiveness to
semantic-changing changes; 2x2 behavioral categories (reliable / evidence-insensitive / brittle /
unstable).

Closest work:
- Invariance-vs-sensitivity analyses in explainability (e.g., sufficiency/comprehensiveness in
  ERASER) [model-knowledge, not live-verified] — two complementary directions but as explanation
  faithfulness of a single model, not as a pre-outcome reliability classifier.
- Robustness-responsiveness tradeoff discussions in ML robustness literature (e.g., adversarial
  robustness vs accuracy tradeoff) [model-knowledge, not live-verified] — different axes.
- Behavioral testing (CheckList) invariance/directional tests [model-knowledge, not live-verified]
  — same idea of separate invariance and directional tests, but not a map used to predict errors.

Attack questions:
1. Is it just a 2D feature vector? As a representation it is; the novelty claim must rest on its
   use for pre-outcome error ranking and interpretability of failure modes.
2. Does it reduce to (1 - flip_rate, flip_rate)? If robustness = stability under paraphrase and
   responsiveness = expected flip under reversal, then the pair is a re-expression of raw flip
   statistics unless the EXPECTED-response semantics (appropriate vs inappropriate change) is the
   measured object. Must keep the expected-response definition in the representation.

Differentiation verdict: weak as a standalone contribution; valuable as an interpretability layer
of the stress profile, not as the primary novelty.

### C5. Active Consensus Probing

Definition: under intervention budget B, adaptively select the next probe T to maximize expected
reliability information; label-blind at test time; compare to fixed probing at matched budget.

Closest work:
- Active testing / active evaluation of model accuracy (e.g., "Active Testing: An Efficient and
  Robust Framework for Estimating Accuracy", Liu et al., 2015; active evaluation literature)
  [model-knowledge, not live-verified]: actively select items to label to estimate accuracy —
  related but different: we select INTERVENTIONS per consensus, not items to label.
- Active learning (query the most informative examples; Settles 2009 survey)
  [model-knowledge, not live-verified]: acquisition of training labels, not probes on a formed
  consensus.
- Adaptive sequential testing in reliability engineering ("Adaptive Sequential Test Planning for
  Multi-Mechanism Reliability Qualification via Bayesian MCTS", arxiv 2026-08-10) [LIVE-verified
  pass1]: active test selection in reliability qualification — closest in spirit, different domain.
- KGLens (arxiv 2023-12-15) [LIVE-verified pass1]: knowledge probing with knowledge graphs —
  different objective (fact probing vs consensus reliability).

Attack questions:
1. Is it reducible to active learning? Active learning selects data to LABEL for training; active
   probing selects evidence interventions to run for reliability estimation at test time, with no
   label feedback. The budget-constrained sequential decision framing is shared.
2. What is the acquisition objective? Must be label-blind (e.g., expected response entropy,
   disagreement gain, uncertainty of the BF estimate). Risk: if acquisition uses correctness, it is
   forbidden by plan Rule 6.
3. Strongest competing work: active testing/evaluation literature + sequential reliability testing.

Differentiation verdict: plausible but the highest-risk concept; only pursue if Gate 2 phenomenon
holds and budget allows.

## Gate 1 summary

Candidate concepts with a genuinely differentiated element (per plan Gate 1):
1. C2 Consensus Stress Testing — outcome-blind controlled evidence stress on a formed consensus
   used for selective prediction: differentiated (no live hit for the same object+use on 2026-09-12).
2. C1 Expected-response faithfulness at consensus level with transformation-derived oracle:
   partially differentiated as a measurement (consensus-level expected-response accuracy).
3. C3 Consensus Stress Curve: differentiated only if evidence-semantics trajectory + error
   prediction; otherwise combination.
4. C4 Robustness-Responsiveness Map: weak standalone; keep as interpretability layer.
5. C5 Active Probing: contingent on C2/C1 empirical support; otherwise future direction.

Gate 1 decision: PASS for C2 (+ C1 as measurement), C3/C4 as secondary representations, C5 as
contingent future work. All claims must be empirical and outcome-blind; no "nobody has done this"
assertions without dated sources.
