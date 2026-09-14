# Mirror Equivalence: BF_reverse as a Label-Aligned Re-Encoding of Mirror-Item Behavior

Status: Agent A (concept reframing / R1) deliverable, round 6. Read-only audit of frozen
records; zero new model calls; no reported number is modified. Newly derived quantities are
explicitly labeled as derivations from sealed frozen data.

## 0. What this document does

R1's attack has two components:

1. "BF_reverse 在反转轴上恒等于模型在自然反证（镜像项）上的正确率" — the reverse-axis
   faithfulness score is (numerically) the model's correctness on the mirror item.
2. "expected-response faithfulness 是标签对齐的 re-encoding" — the "expected response"
   oracle is not measuring a latent trait; it re-encodes, through the gold labels of the
   paired mirror item, the relationship between two ordinary answers.

This document (a) proves the exact equivalence at the single-agent-call level and at the
two consensus-aggregation layers, (b) gives the decoupling decomposition on wrong
consensus (how many agents stay wrong / flip), and (c) states precisely what this does and
does not imply for the "rigidity / evidence insensitivity" narrative.

Inputs (all frozen, read-only):
- round3/preregistration.md — oracle definition: reversal expectation = flip(y0)
  (sections 3, 5); protocol `cs-paper-vitaminc-2026-09-13`.
- round3/round3_lib.py — unit_texts/build_view/build_messages (condition→view mapping).
- round3/features.py — BF_reverse / BF_q definitions and formulas.
- round3/records.jsonl — Qwen3.5-4B, 15,000 records (sealed).
- round4/ling_records.jsonl — Ling-3.0-tiny, 15,000 records (sealed).
- round3/labels_ledger.json — 600 sealed gold labels.
- round4/analysis/ling_adapted_crossmodel.md — reported mechanism numbers 0.703 / 0.029.
- round3/analysis/analysis.md, round3/analysis/gate2_decision_paper.md,
  round3/analysis/phase3_lambda.md, round3/analysis/boolq_crossdataset.md — narrative
  statements being re-based.
- round6/reframing/decoupling_audit.py and decoupling_audit.json — the audit script and
  its machine-readable output used for every derived quantity below.

## 1. Setup and notation

A natural pair `(i, j)` shares a claim C and a distractor D; the evidence packets are
swapped:
- item i: gold G_i, own evidence E_i, counter-evidence E_j (the mirror item's evidence);
- mirror item j: gold G_j = flip(G_i), own evidence E_j, counter-evidence E_i.
Binary answers: yes/no; gold maps SUPPORTS→yes, REFUTES→no; flip(yes)=no, flip(no)=yes.

Agent a is a frozen persona with a frozen 2-of-3 partition P_a and a fixed seed s_a
(round3/round3_lib.py, frozen v10.PARTITION_TABLE and v10._agent_seed). Each condition
maps evidence ids to texts (`unit_texts`):
- original(i): E01=E_i, E02=para1(E_i), E03=D;
- reverse(i):  E01=E_j, E02=para1(E_j), E03=D;
- original(j): E01=E_j, E02=para1(E_j), E03=D.
Because the claim, persona, partition, evidence texts, distractor, and seed are identical,
the reverse view of item i for agent a is byte-identical to the original view of the mirror
item j for agent a (`build_view` + `build_messages` use only the view items and persona;
`view.condition` never enters the prompt). At temperature 0 this implies

    Y(i, reverse, a) = Y(j, original, a) =: y_j(a)                         (View Identity)

Empirical check on the sealed records: reverse(i) answer == original(mirror(i)) answer for
2998/2999 (99.97%, Qwen) and 2989/3000 (99.63%, Ling) agent calls; the few mismatches are
parse-repair paths, not protocol exceptions (see decoupling_audit.json, `view_identity`).

## 2. Layer 1 — single agent call: the exact equivalence and its conditioning

Definitions (round3/features.py; round3/preregistration.md section 3):
- y_i(a) := Y(i, original, a), y_j(a) := Y(j, original, a) (deterministic, T=0).
- c_i(a) := 1[y_i(a) == g_i]  (agent correct on the original item).
- m_j(a) := 1[y_j(a) == g_j]  (agent correct on the mirror item, original condition).
- faithful_rev(i,a) := 1[Y(i, reverse, a) == flip(y_i(a))]  (oracle: flip(y0)).
By the View Identity, Y(i, reverse, a) = y_j(a), so faithful_rev(i,a) = 1[y_j(a) == flip(y_i(a))].

Lemma 1 (single-agent-call equivalence). For every agent a on item i:

    faithful_rev(i,a) = c_i(a) * m_j(a)  +  (1 - c_i(a)) * (1 - m_j(a))
                      = (2*c_i(a) - 1) * m_j(a)  +  (1 - c_i(a)).

Proof. Binary answers, so flip is an involution and y != g_i implies y = flip(g_i).
- If c_i(a) = 1 (y_i = g_i): flip(y_i) = flip(g_i) = g_j, hence
  faithful_rev = 1[y_j == g_j] = m_j(a).                                        (1)
- If c_i(a) = 0 (y_i = flip(g_i) = g_j): flip(y_i) = g_i, hence
  faithful_rev = 1[y_j == g_i] = 1 - 1[y_j == g_j] = 1 - m_j(a).                (2)
QED.

Corollary 1 (the exact sense in which R1 is right). Conditional on the agent being correct
on the original item, faithful_rev(i,a) is IDENTICALLY equal to the agent's correctness on
the mirror item: faithful_rev(i,a) = m_j(a). Unconditionally, the equality
"BF_reverse == mirror-item accuracy" holds at the agent level only when c_i(a) = 1 for the
agents being averaged; for originally-wrong agents the two are INVERTED
(faithful_rev = 1 - m_j(a)).

Corollary 2 (re-encoding, not a new latent variable). The scalar faithful_rev(i,a) is a
deterministic function of two ordinary answers (y_i(a), y_j(a)) and the frozen gold pair
(G_i, G_j). It adds no measurement beyond the model's answers on the original and the
mirror prompt; the "expected-response oracle" only decides, via G-alignment, whether
"answering the mirror gold" is coded as 1 (originally-correct agents) or 0
(originally-wrong agents). This is precisely R1's "label-aligned re-encoding".

## 3. Layer 2a — consensus aggregation within an item

BF_reverse(i) = (1/5) * sum_a faithful_rev(i,a)
              = (1/5) * sum_a [ (2*c_i(a)-1) * m_j(a) + (1 - c_i(a)) ].

Let N_c = #{a : c_i(a)=1} be the number of originally-correct agents. Then

    BF_reverse(i) = (N_c/5) * mbar_j^+  +  (1 - N_c/5) * (1 - mbar_j^-),

where mbar_j^+ is mean mirror accuracy over originally-correct agents and mbar_j^- over
originally-wrong agents. Exact identity BF_reverse(i) == mean_a m_j(a) holds iff N_c = 5
(all agents correct on the original item). Otherwise BF_reverse(i) is a mixture of mirror
accuracy and its complement with weights given by original-item correctness.

## 4. Layer 2b — high-consensus population: the two regimes and label alignment

The HC subset is agreement >= 0.8 on the original condition (round3/preregistration.md
section 5; round3/analysis/analysis.md). Because answers are binary, agreement >= 0.8
means at least 4 of 5 agents share the majority answer, so:

- Consensus-correct item: the 4+ majority agents have y_i = g_i, i.e. N_c >= 4 (weight on
  the "faithful = mirror accuracy" branch >= 0.8). The mirror gold is g_j = flip(g_i) = the
  OPPOSITE of the panel's answer, so mirror-correct behavior = flip away from the panel.
  Hence high BF_reverse on correct consensus means "the panel flips to the mirror gold".
- Consensus-wrong item: the 4+ majority agents have y_i = flip(g_i), i.e. N_c <= 1 (weight
  on the "faithful = 1 - mirror accuracy" branch >= 0.8). The mirror gold is
  g_j = flip(g_i) = the panel's (wrong) answer, so mirror-correct behavior = STAY with the
  panel's answer. Hence low BF_reverse on wrong consensus means "the panel stays, which is
  mirror-correct".

Combining the two regimes:

    BF_reverse(correct consensus) ~ mirror accuracy (majority, weight >= 0.8)
    BF_reverse(wrong consensus)   ~ 1 - mirror accuracy (majority, weight >= 0.8)

The empirical values (derived from sealed records; see decoupling_audit.json):

| quantity (HC)                      | Qwen3.5-4B (round3) | Ling-3.0-tiny (round4) |
|---|---|---|
| n HC / correct / wrong             | 567 / 502 / 65      | 574 / 455 / 119        |
| BF_reverse, correct consensus      | 0.844 (derived)     | 0.703 (reported, round4 §4) |
| BF_reverse, wrong consensus        | 0.095 (derived)     | 0.029 (reported, round4 §4) |
| mirror accuracy, correct consensus | 0.851 (derived)     | 0.715 (derived)        |
| mirror accuracy, wrong consensus   | 0.929 (derived)     | 0.992 (derived)        |
| BF_paraphrase, correct / wrong     | 0.984 / 0.892 (derived) | 0.967 / 0.887 (derived) |

The mirror-accuracy asymmetry confirms the attack: on wrong consensus the panel is
mirror-correct in ~93-99% of agent calls — i.e., the model knows the mirror item's answer;
the BF_reverse collapse (0.703 -> 0.029) is produced by the ALIGNMENT of the mirror gold
with the panel's wrong answer (staying = mirror-correct = unfaithful), not by a differential
mirror-item skill and not by a separately measurable "rigidity" trait. The mechanism-transfer
contrast 0.674 [0.629, 0.719] (round4/analysis/ling_adapted_crossmodel.md §4) is therefore
explained by (1 - mirror accuracy on wrong consensus) vs mirror accuracy on correct
consensus, i.e., 0.715 - (1 - 0.992) = 0.707 predicted vs 0.674 observed (Ling); the small
residual is the <= 0.2 weight carried by the opposite minorities in each regime
(originally-wrong agents on correct items; originally-correct agents on wrong items).

## 5. Decoupling decomposition on wrong consensus (all quantities derived from sealed records)

Definitions on a wrong-consensus HC item (majority answer W = flip(g_i); the mirror gold is
g_j = W). For each of the 5 agents:

- "stays"  := y_rev(a) == y_i(a) == W. The agent keeps the panel's wrong answer after seeing
  the natural counter-evidence. Because g_j = W, for the 4+ originally-wrong majority agents
  staying is simultaneously mirror-correct and "still wrong on the original question".
- "flips"  := y_rev(a) == g_i. The agent moves to the true label. Because g_j = W, for the
  majority agents flipping is simultaneously mirror-wrong.
- Caveat (dissenting agent): a wrong-consensus item may contain at most ONE originally-correct
  dissenting agent (agreement >= 0.8 with a wrong majority). For that agent the roles are
  reversed: "responsive" means answering W (mirror-correct), and "stays" means keeping G_i
  (mirror-wrong). The two per-item histograms below therefore coincide for the majority group
  but differ by these dissenting agents.

By Lemma 1, for originally-wrong agents flips = faithful_rev and stays = 1 - faithful_rev =
mirror-correct. Hence, on wrong consensus, "how many agents still give the wrong answer when
faced with the counter-evidence" and "how many flip" are the two cells of the responsiveness
histogram (5.1); the mirror-item-outcome histogram (5.2) is the same measurement read through
the mirror gold and differs only on items with a dissenting correct agent.

### 5.1 Per-item histogram of flips-to-true-label (reverse axis), wrong consensus

Qwen (65 wrong HC items):
- 46 items (70.8%): 0 of 5 agents flip  -> 5/5 stay with the wrong answer.
- 14 items (21.5%): 1 of 5 agents flips.
- 3 items (4.6%): 3 of 5 agents flip.
- 2 items (3.1%): 4 of 5 agents flip.
- 0 items: all 5 flip.
- Agent level: 31 / 325 calls (9.5%) flip to the true label; 294 / 325 (90.5%) stay wrong.

Ling (119 wrong HC items):
- 102 items (85.7%): 0 of 5 agents flip -> 5/5 stay with the wrong answer.
- 17 items (14.3%): 1 of 5 agents flips.
- Agent level: 17 / 595 calls (2.9%) flip to the true label; 578 / 595 (97.1%) stay wrong.

### 5.2 The same measurement read as mirror-item outcome

On the mirror item, agents whose reverse answer equals the mirror gold W are mirror-correct,
and agents whose reverse answer differs from W are mirror-wrong. For the majority group this
is exactly "stayed = mirror-correct, flipped = mirror-wrong"; the rare dissenting correct
agent is mirror-correct when responsive (answers W). Histograms of mirror-wrong per item:
- Qwen (65 wrong HC items): 57 items with 0 mirror-wrong; 3 items with 1; 1 item with 3;
  3 items with 4; 1 item with 5. Agent level: 23 / 325 (7.1%) mirror-wrong;
  302 / 325 (92.9%) mirror-correct.
- Ling (119 wrong HC items): 115 items with 0 mirror-wrong; 3 items with 1; 1 item with 2.
  Agent level: 5 / 595 (0.8%) mirror-wrong; 590 / 595 (99.2%) mirror-correct.

Relationship to 5.1: mirror-wrong = responsive - (responsive dissenting agents), so the two
histograms are not identical, but both are dominated by the same majority behavior. The honest
content of "in wrong consensus, X agents stay wrong / flip" is: the panel is overwhelmingly
non-responsive to the natural counter-evidence (Qwen 90.5%, Ling 97.1% stay), and the same
majority behavior is mirror-correct because the mirror gold is aligned with the panel's wrong
answer (Qwen 92.9%, Ling 99.2% mirror-correct).

## 6. Implications for the "rigidity / evidence insensitivity" narrative

1. Accepted (R1's core point). BF_reverse is a deterministic re-encoding of two ordinary
   answers and the frozen gold pair; on the reverse axis it adds no new measurement beyond
   "does the panel's mirror-item answer align with (the flip of) its original answer". It is
   label-aligned re-encoding, not an independent probe of a latent "rigidity" trait.
2. Accepted (with precision). The numerical claim "BF_reverse == mirror-item accuracy" holds
   exactly for originally-correct agents and for consensus-correct HC items (weight >= 0.8);
   it is INVERTED for the originally-wrong group that dominates wrong consensus. So the
   equivalence is conditional, not unconditional — but the unconditional behavior that the
   research relied on (0.703 vs 0.029) is fully reproduced by the alignment argument above.
3. Dropped. "Wrong consensus is rigid under evidence stress" as a MECHANISM claim: the data
   cannot separate "non-responsive to counter-evidence" from "mirror gold aligned with the
   wrong answer". The term "expected-response faithfulness" overstates what is measured.
4. Retained (behavioral, non-causal). The reverse axis still measures, on the frozen
   protocol, whether the panel changes its answer when evidence is swapped to the natural
   opposite; wrong consensus panels overwhelmingly do not (Qwen 90.5%, Ling 97.1% stay), and
   correct consensus panels mostly do (BF_reverse 0.844 / 0.703). This asymmetry is a real,
   pre-outcome-computable behavioral regularity on this protocol, now described as
   "counter-evidence responsiveness" rather than "evidence insensitivity".
5. Paraphrase axis is NOT subject to the mirror reduction. The paraphrase condition is the
   same item under meaning-preserving rewording (expected = y0), not a mirror prompt, so it
   measures stability under paraphrase independently of label alignment. It discriminates
   only mildly (BF_paraphrase correct vs wrong: Qwen 0.984 vs 0.892; Ling 0.967 vs 0.887,
   derived), so the bulk of RS_q's separation lives in the reverse axis — which is the
   mirror re-encoding. Agent C's reducibility audit should state this decomposition
   explicitly.
6. Causal identification is NOT claimed anywhere in this reframing. The equivalence proof is
   about measurement identity, not about a causal path from counter-evidence to error.

## 7. Boundaries of this analysis

- All decoupling / mirror-accuracy numbers in sections 4-5 are NEW DERIVATIONS from the
  sealed records + sealed labels ledger (labels merged only after preoutcome feature
  freezing, as required by the round-3 outcome firewall). They do not modify any reported
  number; existing reported numbers (0.703 / 0.029 / 0.674, AUROC 0.943 / 0.896, Risk@80
  0.846 / 0.422) are restated only, with file paths.
- The derivation assumes the View Identity holds; it is verified empirically at 99.97% /
  99.63% of calls, with the residual mismatches attributable to parse-repair paths
  (decoupling_audit.json `view_identity`).
- The proof applies to the natural-reversal axis on the frozen VitaminC protocol. BoolQ's
  negation-prefix reverse is NOT a mirror item and is outside this equivalence
  (round3/analysis/boolq_crossdataset.md).
- Companion deliverables: method_narrative_v2.md (new narrative) and rewrite_suggestions.md
  (diff-style edits for round3/round4 and benchmark/README).
