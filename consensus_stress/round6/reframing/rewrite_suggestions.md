# Rewrite Suggestions — diff-style (for Agent F)

Scope: round3/round4 key paragraphs and benchmark/README sentences that carry the
"expected-response faithfulness / evidence insensitivity / rigidity / stress-testing
framework" mechanism framing. Every suggestion keeps the numbers identical and only
re-bases the interpretive wording on counter-evidence responsiveness (see
method_narrative_v2.md and mirror_equivalence_analysis.md). Line numbers refer to the
current files. No new numbers are introduced in any suggested sentence.

Conventions: `OLD` = current text (verbatim); `NEW` = suggested replacement;
`NOTE` = why. 中文备注 attached where the interpretive change is non-obvious.

---

## A. round3/analysis/gate2_decision_paper.md

### A1. Lines 28-29 (Phase 3 bullet)
OLD:
```
- Stress-area AUROC(RS_stress, wrong|HC) = 0.948 [0.925, 0.968]; wrong consensus rigid
  at every lambda (robustness radius 1.0, no breakpoint for 22/22).
```
NEW:
```
- Stress-area AUROC(RS_stress, wrong|HC) = 0.948 [0.925, 0.968]; wrong consensus is
  non-responsive to natural counter-evidence at every lambda (robustness radius 1.0, no
  breakpoint for 22/22). Descriptive trajectory of the same regularity as BF_reverse; see
  mirror_equivalence_analysis.md for the label-alignment caveat.
```
NOTE: "rigid" -> "non-responsive (descriptive)"; numbers unchanged.

### A2. Lines 33-39 (Reading paragraph)
OLD (lines 33-39, the whole Reading paragraph):
```
The paper-scale cohort confirms and exceeds the round-2 baseline: the expected-response
faithfulness representation (frozen composite BF_q / RS_q) ranks consensus errors with
AUROC 0.943 (round 2: 0.906), cuts errors at 80% coverage by 85% (round 2: 65%), and is
significantly better than frozen R_sym and R_PI on both AUROC and Risk@80 with
CI-confirmed paired differences, label-symmetric, placebo-clean, permutation-validated,
CI-level worst-label-gated, and reducibility-safe. Phase 3 gives the continuous stress
curve with per-question breakpoint/robustness-radius support.
```
NEW:
```
The paper-scale cohort confirms and exceeds the round-2 baseline: the counter-evidence
responsiveness representation (frozen composite BF_q / RS_q, where BF_reverse is the
fraction of agent calls that change answer to the flip under natural evidence swap) ranks
consensus errors with AUROC 0.943 (round 2: 0.906), cuts errors at 80% coverage by 85%
(round 2: 65%), and is significantly better than frozen R_sym and R_PI on both AUROC and
Risk@80 with CI-confirmed paired differences, label-symmetric, placebo-clean,
permutation-validated, CI-level worst-label-gated, and reducibility-safe. Phase 3 gives the
continuous responsiveness trajectory with per-question breakpoint/robustness-radius support
(descriptive; BF_reverse on the reversal axis is a label-aligned re-encoding of
mirror-item behavior — mirror_equivalence_analysis.md).
```
NOTE: re-bases "expected-response faithfulness representation" -> "counter-evidence
responsiveness representation"; keeps all numbers.

## B. round3/analysis/analysis.md

### B1. Lines 71-73 (Calibration / modeling)
OLD:
```
- Frozen composite BF_q (0.943) ties the fitted logistic OOF (0.941, paired diff CI
  includes 0): the concept (expected-response faithfulness with decision-relevance-aware
  oracle), not extra fitting, carries the signal.
```
NEW:
```
- Frozen composite BF_q (0.943) ties the fitted logistic OOF (0.941, paired diff CI
  includes 0): the pre-registered composite (paraphrase stability + counter-evidence
  responsiveness), not extra fitting, carries the signal. Note: BF_reverse is a
  label-aligned re-encoding of mirror-item behavior (mirror_equivalence_analysis.md);
  the ranking is real, the mechanism label is descriptive.
```
NOTE: drops "expected-response faithfulness with decision-relevance-aware oracle" as the
"concept that carries the signal".

### B2. Line 29 (Context: "Risk form RS_q = -BF_q")
Check the Risk-form line (line 29 in this file is not in our suggested scope); Agent F
should re-word any remaining "faithfulness" occurrence in the header/table titles the same
way as B1. (见 method_narrative_v2.md §4 术语表)

## C. round3/analysis/phase3_lambda.md

### C1. Lines 16-17 (reversal axis, mean stress area)
OLD:
```
- Mean stress area: correct 0.436 vs wrong 0.032 (correct consensus is ~14x more
  responsive to gradual natural reversal).
```
NEW:
```
- Mean stress area: correct 0.436 vs wrong 0.032 (correct consensus is ~14x more
  responsive to gradual natural reversal; descriptive trajectory, same regularity as
  BF_reverse — mirror_equivalence_analysis.md).
```
NOTE: add the descriptive qualifier; numbers unchanged.

### C2. Lines 18-20 (breakpoint)
OLD:
```
- Breakpoint (smallest lambda where the consensus flips): correct mean 0.555;
  **22/22 wrong consensus NEVER flip at any lambda in [0,1]** (rigid);
  31/203 correct never flip.
```
NEW:
```
- Breakpoint (smallest lambda where the consensus flips): correct mean 0.555;
  **22/22 wrong consensus NEVER flip at any lambda in [0,1]** (non-responsive to natural
  reversal); 31/203 correct never flip.
```
NOTE: "rigid" -> "non-responsive"; the sentence remains descriptive. The continuous-lambda
subset (22 wrong items) and the discrete decoupling (65 wrong HC items) are different
cohorts; no cross-count is claimed (mirror_equivalence_analysis.md §5).

### C3. Lines 34-37 (Reading)
OLD:
```
The continuous curve adds per-question granularity to the round-2 discrete finding:
correct consensus responds proportionally to natural evidence reversal (flip probability
rises smoothly with lambda), while false consensus is rigid at every lambda (robustness
radius 1.0, no breakpoint). Stress area is a strong, frozen, outcome-free consensus-risk
feature (AUROC 0.948), consistent with the main cohort's BF_q result (0.943).
```
NEW:
```
The continuous curve adds per-question granularity to the round-2 discrete finding:
correct consensus responds proportionally to natural evidence reversal (flip probability
rises smoothly with lambda), while false consensus stays with its answer at every lambda
(robustness radius 1.0, no breakpoint). Stress area is a strong, frozen, outcome-free
consensus-risk feature (AUROC 0.948), consistent with the main cohort's BF_q result
(0.943). These trajectories describe the same counter-evidence-responsiveness regularity;
on the discrete reversal axis BF_reverse is a label-aligned re-encoding of mirror-item
behavior (mirror_equivalence_analysis.md).
```

## D. round4/analysis/ling_adapted_crossmodel.md

### D1. Line 65 (section header)
OLD: `## 4. Mechanism transfer: natural evidence reversal`
NEW: `## 4. Cross-model consistency: counter-evidence responsiveness under natural evidence reversal`
NOTE: drop "mechanism transfer" (no causal trait claim).

### D2. Lines 73-75 (mechanism gate reading)
OLD:
```
The CI excludes zero, so the mechanism gate **passes**: wrong Ling consensus is much more rigid
under natural evidence reversal than correct consensus. This replicates the central Qwen
mechanism in a different model family.
```
NEW:
```
The CI excludes zero, so the pre-registered consistency criterion **passes**: wrong Ling
consensus is much less responsive to natural evidence reversal than correct consensus
(descriptive; BF_reverse on the reversal axis is a label-aligned re-encoding of mirror-item
behavior, mirror_equivalence_analysis.md). This replicates the same frozen-procedure
regularity in a different model family.
```
NOTE: "rigid" -> "less responsive"; "mechanism gate / mechanism" -> "consistency criterion /
regularity"; numbers 0.703 / 0.029 / 0.674 [0.629, 0.719] unchanged.

### D3. Section 6 (Claim boundary) — add one caveat sentence
OLD: (last sentence of §6)
```
The BoolQ negative result from Round 3 remains a specificity boundary: natural counter-evidence is essential.
```
NEW:
```
The BoolQ negative result from Round 3 remains a specificity boundary: natural
counter-evidence is essential. No causal claim is made: the reverse-axis signal is a
pre-outcome behavioral regularity (counter-evidence responsiveness), and BF_reverse is a
label-aligned re-encoding of the panel's original and mirror-item answers
(mirror_equivalence_analysis.md).
```

## E. benchmark/README.md

### E1. Lines 22-24 (proposed method definition)
OLD:
```
- The proposed method, `RS_q`, is outcome-blind expected-response faithfulness:
  `RS_q = -BF_q`, where `BF_q` averages agent faithfulness over paraphrase and natural
  evidence reversal. Low faithfulness under stress yields high risk.
```
NEW:
```
- The proposed method, `RS_q`, is an outcome-blind counter-evidence responsiveness score:
  `RS_q = -BF_q`, where `BF_q` averages (a) paraphrase stability (same answer under
  meaning-preserving rewording) and (b) reverse-axis responsiveness (answer changes to the
  flip under natural evidence reversal). Low responsiveness to counter-evidence yields high
  risk. Caveat: on the reversal axis BF_reverse is a label-aligned re-encoding of the
  panel's original and mirror-item answers (mirror_equivalence_analysis.md); the benchmark
  reports its pre-outcome ranking performance, not a latent trait.
```
NOTE: task definition and metric unchanged; only the label/definition of the signal changes.

### E2. Lines 45-47 (BoolQ negative control)
OLD:
```
- Round 3 found a direction reversal and gate failure on this split. It is retained as a
  negative control showing that the mechanism is specific to natural counter-evidence rather
  than arbitrary perturbation. It is not included in the Round-5 leaderboard.
```
NEW:
```
- Round 3 found a direction reversal and gate failure on this split. It is retained as a
  negative control showing that the responsiveness signal is specific to natural
  counter-evidence rather than to arbitrary perturbation. It is not included in the
  Round-5 leaderboard.
```
NOTE: "the mechanism" -> "the responsiveness signal".

### E3. Line 49 (section header)
OLD: `## 3. Expected-response oracle`
NEW: `## 3. Frozen scoring oracle (label-free)`
NOTE: keeps the oracle mechanics; drops "expected-response" branding.

### E4. Lines 100-103 (single-agent family)
OLD:
```
One fixed agent/persona is sampled five times under each of the five parent conditions. The
pre-registered score is `RS_single=-BF_single`, where `BF_single` averages replicate
faithfulness over paraphrase and natural reverse. This directly tests whether multiple agent
personas are necessary.
```
NEW:
```
One fixed agent/persona is sampled five times under each of the five parent conditions. The
pre-registered score is `RS_single=-BF_single`, where `BF_single` averages replicate
paraphrase stability and reverse-axis responsiveness. This directly tests whether multiple
agent personas are necessary.
```
NOTE: "faithfulness" -> "paraphrase stability and reverse-axis responsiveness".

### E5. Line 1 (title) and lines 6-7 (task framing)
OLD: `# CST-Bench: Consensus Stress Testing Benchmark`
NEW: `# CST-Bench: Counter-Evidence Responsiveness Benchmark (CST-Bench)`
NOTE: keep the acronym and the benchmark artifact; re-base the framing.
OLD (lines 6-7):
```
CST-Bench evaluates whether a method can predict, **without seeing the outcome**, when an
already-formed multi-agent consensus is wrong under controlled evidence stress. The primary
```
NEW:
```
CST-Bench evaluates whether a method can predict, **without seeing the outcome**, when an
already-formed multi-agent consensus is wrong, using pre-outcome evidence probes —
primarily the panel's responsiveness when its evidence is swapped to the natural
counter-evidence. The primary
```
NOTE: "under controlled evidence stress" -> "using pre-outcome evidence probes (primarily
counter-evidence responsiveness)".

## F. round3/analysis/boolq_crossdataset.md

### F1. Lines 26-29 (diagnosis, second bullet)
OLD:
```
- This is a SPECIFICITY result, not a contradiction of the main finding: it supports the
  causal claim that the risk signature is specifically "unresponsive to genuine natural
  evidence reversal", not "unresponsive to any perturbation". No parser/oracle/gate was
  changed; the negative is retained.
```
NEW:
```
- This is a SPECIFICITY result, not a contradiction of the main finding: it shows the risk
  signature is specific to natural counter-evidence rather than to arbitrary perturbation.
  No parser/oracle/gate was changed; the negative is retained. Wording note: "unresponsive"
  is descriptive of the frozen protocol behavior, not a causal claim.
```
NOTE: removes "supports the causal claim"; keeps the specificity boundary.
