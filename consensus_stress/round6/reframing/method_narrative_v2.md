# Method Narrative v2 — Counter-Evidence Responsiveness (反证响应性)

Status: Agent A deliverable, round 6. Replaces the "consensus stress testing framework /
expected-response faithfulness / evidence insensitivity" narrative per
autoresearch_score4_upgrade.md sections 0/2/4/5 and per the R1 attack formalized in
mirror_equivalence_analysis.md. No reported number is changed; no new model calls; no causal
claim is made.

## 1. One-sentence positioning

**We propose counter-evidence responsiveness as a pre-outcome, evidence-level signal: an
already-formed multi-agent consensus is at elevated error risk when the panel does not
change its answer after its evidence packet is swapped to the natural counter-evidence; on
the frozen VitaminC natural-pair protocol this signal, combined with paraphrase stability
into RS_q = -BF_q, ranks consensus errors with AUROC 0.943 [0.924, 0.960] (Qwen3.5-4B,
round3/analysis/analysis.md) and 0.896 [0.873, 0.916] (Ling-3.0-tiny,
round4/analysis/ling_adapted_crossmodel.md), with unchanged Risk@80 reductions
0.846 [0.638, 0.981] and 0.422 [0.274, 0.591].**

定位一句话：把"共识压力测试框架 / 期望响应忠实度 / 证据不敏感"降为"反证响应性"——用
已形成共识在自然反证下"改不改答案"这一事前可观测行为，作为共识错误的选择性路由信号。

## 2. What changed vs v1 (mechanism framing)

| v1 (dropped) | v2 (adopted) |
|---|---|
| "Consensus Stress Testing framework" as the mechanism sell | A measurement + benchmark (CST-Bench) of one behavioral regularity: counter-evidence responsiveness |
| "Expected-response faithfulness" as a latent faithfulness trait | Label-aligned re-encoding of mirror-item behavior, honest about the equivalence (mirror_equivalence_analysis.md) |
| "Evidence insensitivity / rigidity" as the explanation of wrong consensus | "Non-responsive to natural counter-evidence" as a descriptive, pre-outcome behavioral regularity, without a causal trait claim |
| "Stress curve / breakpoint / robustness radius" as mechanism evidence | Keep the curve as a descriptive trajectory of the same regularity; no claim that the trajectory reveals a distinct mechanism (round3/analysis/phase3_lambda.md, reframed in rewrite_suggestions.md) |

The measurement and the benchmark are unchanged; only the interpretive layer is narrowed.

## 3. Narrowed mechanism claim (what we may assert)

1. Descriptive (supported). On the frozen protocol, correct consensus panels predominantly
   change their answer when the evidence is swapped to the natural opposite
   (reverse fidelity 0.844 Qwen derived / 0.703 Ling reported,
   round4/analysis/ling_adapted_crossmodel.md §4), while wrong consensus panels
   predominantly do not (0.095 Qwen derived / 0.029 Ling reported). Decoupling on wrong
   consensus: 90.5% (Qwen) / 97.1% (Ling) of agent calls stay with the wrong answer
   (derivation: round6/reframing/decoupling_audit.json).
2. Predictive (unchanged, pre-outcome). RS_q = -BF_q ranks consensus errors before labels
   are merged: AUROC 0.943 [0.924, 0.960] and Risk@80 0.846 [0.638, 0.981] on Qwen HC;
   AUROC 0.896 [0.873, 0.916] and Risk@80 0.422 [0.274, 0.591] on Ling HC; cross-model
   procedure transfer AUROC 0.723 [0.682, 0.765]
   (round3/analysis/analysis.md; round4/analysis/ling_adapted_crossmodel.md).
3. Boundary claim (unchanged). The regularity is specific to NATURAL counter-evidence:
   BoolQ, whose reverse axis is a negation prefix, reverses direction (AUROC 0.449,
   round3/analysis/boolq_crossdataset.md). We do not claim transfer to arbitrary
   perturbations or datasets.
4. NOT claimed: any causal identification (that counter-evidence causes the error, or that
   responsiveness causes correctness); any latent "rigidity" trait; any new heuristic beyond
   what the frozen RS_q formula computes (reducibility audit, Agent C).

## 4. What "expected-response faithfulness" becomes

Terminology downgrade (for paper text, see rewrite_suggestions.md):
- "expected-response faithfulness (BF_reverse)" -> "reverse-axis counter-evidence
  responsiveness (BF_reverse)", defined operationally as the fraction of agent calls whose
  answer changes to the flip of the original answer under natural evidence swap.
- "faithfulness profile" -> "responsiveness profile (paraphrase stability + counter-evidence
  responsiveness)".
- "consensus stress testing" as a framework -> "a benchmark (CST-Bench) and a pre-outcome
  risk signal built on counter-evidence responsiveness".

The mirror-equivalence caveat is stated once in the method section: BF_reverse is a
deterministic re-encoding of the panel's original and mirror-item answers together with the
frozen paired gold; on correct consensus it coincides with mirror-item accuracy, on wrong
consensus it is its complement (mirror_equivalence_analysis.md sections 2-4). The AUROC and
Risk@80 numbers are unchanged because they are ranking facts about the frozen scores; the
narrative about WHY they rank is what changes.

## 5. Evidence retained (unchanged numbers, with paths)

- Placebo / paraphrase control: agent-level paraphrase flip 0.038 (Qwen,
  round3/analysis/analysis.md gate G5; c1_placebo.agent_paraphrase_flip_rate = 0.0377 in
  round3/analysis/analysis.json); Ling 0.061 (round4/analysis/ling_adapted_crossmodel.md §2).
  Kept as: the paraphrase axis is stable, so the reverse-axis asymmetry is not explained by
  general prompt instability.
- Permutation control: Qwen 0.943 > 95th pct 0.596; Ling 0.896 > 0.564
  (round3/analysis/analysis.md; round4/analysis/ling_adapted_crossmodel.md). Kept as: the
  observed ranking beats the 95th percentile of 1000 per-item preserve/flip-swap
  permutations that randomize the sign of each BF component per item
  (round3/analysis_lib.py `permutation_risk`), i.e., the directional association between
  low responsiveness and error is not reproduced when component signs are scrambled per item.
- Reducibility: Qwen Spearman(RS_q, agreement) = -0.004, vs confidence = -0.161,
  agreement==0.8 AUROC 0.844; Ling -0.148 / -0.050
  (round3/analysis/analysis.md; round4/analysis/ling_adapted_crossmodel.md). Kept as: RS_q is
  not a re-expression of agreement or confidence (this is separate from the mirror reduction,
  which concerns BF_reverse vs mirror-item accuracy).
- Risk@80 / AUROC: unchanged (section 3 above).
- Cross-model / cross-dataset: Ling within-model pass and BoolQ negative retained as-is
  (round4/analysis/ling_adapted_crossmodel.md; round3/analysis/boolq_crossdataset.md).

## 6. What must NOT be said (discipline checklist)

- No "evidence insensitivity", "rigidity trait", or "stress testing framework" as a
  mechanism explanation.
- No causal wording: "responsive/non-responsive" is descriptive of the frozen protocol
  behavior, not a mechanism causing consensus error.
- No new numbers in the narrative beyond the decoupling derivation documented in
  round6/reframing/decoupling_audit.json.
- No claim that BF_reverse measures something beyond (original answer, mirror answer, gold
  alignment) on the reverse axis.
