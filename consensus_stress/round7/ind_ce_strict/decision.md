# Round-7 W2b — Reviewer-Oriented Decision Report (STRICT independent counter-evidence)

Protocol: `cs-paper-ind-ce-strict-20260915-round7-w2b` (preregistered before any call;
prereg SHA256 `e1c1db40...`). Cohort: first 50 items / 25 pairs of the round-3 VitaminC
manifest. Evidence construction is claim-only (no item polarity, no gold, no mirror text,
no original answers); both directions are generated in one label-blind call and the
counter-evidence is assigned offline to oppose each item's gold. Inference: 5 personas x
{ind_strict, placebo_matched}, gpt-6-astra, single-slot packets, flip vs frozen round-6
original answers; `natural` reused from frozen W2 records (no rerun). See
`execution_notes.md`, `run_summary_*.json`, `analysis/strict_results.json`.

---

## 0. What was actually run (one paragraph)

50 generation calls (claim-only dual-direction + matched placebo) -> offline gold
assignment -> 30-item label-blind audit -> smoke 20 items (valid 0.995) -> formal 50 items
(valid 0.998) -> label-free feature freeze -> label merge -> pair-grouped bootstrap
analysis. A post-freeze parser correction (documented, applied uniformly to cached raw
outputs; prompts/seeds/calls unchanged) recovered 5 format-rejected generation calls
(45/50 -> 50/50); verified byte-identical text for all originally-OK rows.

## 1. Headline results (50-item cohort; pair-grouped 95% CI, 2000 reps, seed 20260915)

| quantity | estimate | CI | gate |
|---|---|---|---|
| P(flip | ind_strict) | 0.7258 | [0.6466, 0.8115] | — |
| P(flip | placebo_matched) | 0.5141 | [0.4600, 0.5772] | — |
| **Δ_CE** | **+0.2118** | **[+0.1160, +0.3097]** | **G3 PASS** |
| placebo ceiling (<= 0.30) | 0.5141 | — | **G4 FAIL** |
| P(flip | natural, reused) | 0.8434 | [0.7177, 0.9478] | diagnostic |
| S_ind_strict AUROC (HC n=46, wrong=3) | 0.624 | [0.286, 0.856] | not > 0.5 |
| S_natural AUROC (HC n=47) | 0.973 | [0.912, 1.000] | reference |
| RS_q AUROC (HC n=47) | 0.943 | [0.860, 1.000] | reference |
| ΔAUROC S_ind − S_natural | **−0.349** | **[−0.714, −0.091]** | negative |
| ΔAUROC S_ind − RS_q | **−0.318** | **[−0.670, −0.106]** | negative |
| ρ(S_natural, S_ind_strict) | 0.033 | [−0.044, 0.478] | ≈ 0 |
| OOF logistic increment (S_ind over S_natural) | +0.004 | [−0.074, 0.047] | none |

Audit (30 items, label-blind): strict independence from mirror evidence **PASS** (token
jaccard median 0.185 / max 0.467; char ratio max 0.549; LCS max 0.565); generation-input
cleanliness **PASS** (30/30 prompts = frozen template + claim only); placebo format 1.0 and
irrelevance 0.80 **PASS**; direction-compliance 0.783 overall (marginal FAIL; 0.80 on the
assigned counter-evidence segments). Inference-prompt leakage audit: **PASS** (299 rebuilt
prompts, sha-match 1.0, packet = claim + single E01 only).

## 2. (a) What W2/W2b success / partial success / failure means for the paper claim

The paper claim under stress is: *wrong consensus is disproportionately associated with
insufficient response to decision-relevant counter-evidence, and this is measurable
pre-outcome* — i.e., a natural-pair phenomenon (W2/round-3/6) that the reviewers worried
might be a mechanical artifact of the byte-identical mirror construction (plan §0/§2).

**W2/W2b SUCCESS (the hypothesis survives intact).**
Δ_CE > 0 with a clean placebo (P(flip|pm) <= 0.30), and S_ind alone predicts consensus
error on HC (AUROC clearly > 0.5) with a positive incremental value over S_natural / RS_q
and non-trivial ρ(S_natural, S_ind). Meaning: the counter-evidence-responsiveness signal is
not an artifact of the mirror; it generalizes to independently constructed, decision-relevant
counter-evidence; the paper can claim a deployable pre-outcome risk signal that does not
depend on the paired-mirror construction, and the mirror-equivalence objection is
empirically closed.

**W2/W2b PARTIAL SUCCESS (what we actually observe).**
The strict construction is *clean* (textually independent of the mirror, label-free
generation, no leakage in inference prompts), and the flip-rate comparison survives:
a gpt-6-astra panel flips significantly more on decision-relevant independent
counter-evidence than on a matched decision-irrelevant placebo (Δ_CE = +0.212, CI excludes
0). So a *selective average responsiveness to decision-relevant evidence* is not purely a
mirror artifact. BUT: (i) the matched placebo is not clean (0.514 > 0.30 — agents also flip
~51% on topic-relevant neutral content), (ii) S_ind_strict alone does not rank errors
(AUROC 0.624, CI includes 0.5 on n=46/3 wrong), (iii) S_ind_strict is *negatively*
incremental to both S_natural (−0.349) and RS_q (−0.318), and (iv) ρ(S_natural,
S_ind_strict) ≈ 0.03 — the strict signal carries almost no shared ordering with the
natural-pair signal. Meaning: the *error-ranking* power of the natural-pair signal is not
reproduced by claim-only independent counter-evidence; the mirror evidence itself (the real
paired sentence, which is stronger and direction-cleaner than LLM-generated evidence)
accounts for the predictive value. The phenomenon holds as a **natural-pair consensus
fragility phenomenon with a preregistered protocol**, not as an independently deployable
evidence-generation + ranking signal.

**W2/W2b FAILURE (not observed).**
Δ_CE <= 0 (no selective flip-rate response at all) and/or the strict evidence is
not decision-relevant and/or heavy leakage. That would have forced the claim down to
"counter-evidence responsiveness is entirely a paired-item artifact; only the natural-pair
replication is reportable." We did NOT observe this: Δ_CE is robustly positive and the
audit/leakage controls are clean. Failure is therefore rejected on the evidence.

## 3. Verdict for the paper

- **W2 (label-coupled E_ind): partial success** — flip-rate selectivity replicates
  (Δ_CE +0.293), placebo not clean (0.544), S_ind nearly non-incremental over natural at
  HC (n=96): +0.021 AUROC, OOF +0.045 [wide].
- **W2b (strict E_ind_strict): partial success on the behavioral axis, negative on the
  predictive-increment axis** — see section 2. The strict control *breaks the claim that
  the signal is a mirror artifact at the level of average responsiveness* but *fails to
  establish an independent error-ranking signal*, and it quantifies how much of the
  predictive value lives in the natural-pair mirror (ρ ≈ 0, negative increments).

Recommended paper action: keep the natural-pair consensus-fragility phenomenon as the
central, preregistered empirical contribution; add the strict experiment as a labeled
control/boundary in §Limitations or an appendix; do NOT claim that independent
counter-evidence generation can replace the paired-mirror signal, and do NOT present
S_ind_strict as an incremental risk score. Do not tune the strict protocol to chase a
better score (TARGET_SPEC §6).

## 4. (b) Most defensible, least overstated final claim (one paragraph, ready for
limitations/conclusion)

"We preregistered and ran a strict control in which counter-evidence was generated from
the claim alone — both directions in a single label-blind call, with the counter-evidence
assigned offline to oppose each item's gold, and no use of item polarity, gold labels, the
paired mirror evidence, or the model's original answers — and compared it against a
matched, topic-relevant placebo. The strict counter-evidence is textually independent of
the natural mirror (token-jaccard, character, and LCS overlap gates pass), and a leakage
audit confirmed that inference prompts contained only the claim and one evidence unit. A
gpt-6-astra five-agent panel flipped significantly more often under the independent
counter-evidence than under the matched placebo (Δ_CE = +0.212, 95% CI [+0.116, +0.310]),
showing that selective average responsiveness to decision-relevant counter-evidence is not
merely an artifact of the paired-mirror layout. However, the matched placebo was not clean
(P(flip|placebo) = 0.514), and the independent-responsiveness score carried no predictive
increment for consensus error relative to the natural-pair signal: its high-consensus AUROC
was 0.624 (CI [0.286, 0.856]), it was negatively incremental relative to both the
natural-pair score (ΔAUROC −0.349 [−0.714, −0.091]) and the frozen Qwen risk score (−0.318
[−0.670, −0.106]), and it was nearly uncorrelated with the natural-pair score (ρ = 0.03).
We therefore report our central result as a natural-pair consensus-fragility phenomenon
measured by a preregistered paired-intervention protocol: under the paired-mirror
construction, consensus items that fail to respond to the paired counter-evidence are
substantially more likely to be wrong. The strict independent-counter-evidence variant
supports only the weaker behavioral claim that panels respond selectively to
decision-relevant counter-evidence on average; it does not establish an independently
deployable pre-outcome error signal, and we make no claim that mirror-independent
counter-evidence generation can substitute for the natural-pair signal."

## 5. Honesty checklist (plan §20)

1. Could a reviewer claim the main result is mechanically caused by mirror pairing? — The
   strict control shows the *average flip-rate* effect is not purely mechanical (Δ_CE > 0
   with cleanly independent evidence), but the *error-ranking* signal is substantially
   tied to the natural pair (negative increments, ρ ≈ 0). Claim narrowed accordingly.
2. Did we empirically break the dependency? — Partially: behavioral axis yes; predictive
   axis no.
3. If not, did we narrow the claim? — Yes (section 4).
4. Does the main signal add value beyond paired-item consistency? — Yes vs simple baselines
   (S_natural AUROC 0.973, Risk@80 1.0, OOF 0.95); the strict variant does not add beyond
   it (negative increment).
5. Replication across models? — gpt-6-astra here; Qwen/Ling previously (RS_q reference).
6. Deployment honesty — counter-evidence in deployment requires a retrieval/generation
   module; the strict result bounds what such a module can currently achieve (no
   incremental ranking signal from claim-only generation).
7. Negative results: placebo not clean and no predictive increment are recorded, not tuned.

## 6. Files

`preregistration.md`, `cohort.json`, `e_gen_artifacts.jsonl`, `e_ind_strict_artifacts.jsonl`,
`audit_sample.jsonl`, `records_smoke.jsonl`, `records.jsonl`,
`preoutcome_features.jsonl` (+ meta), `run_summary_*.json`, `analysis/strict_results.json`
(+ `.md`), `artifact_hashes.json`, `execution_notes.md`, `SUMMARY.md`.
