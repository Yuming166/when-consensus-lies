# Prioritized pre-submission audit memo

## Overall verdict

No P0 contradiction is visible in the PECR evidence supplied. The ConvFinQA Stage 2 and Stage 3 claims are represented accurately, and the manuscript correctly avoids the main prohibited interpretations:

- universal reasoning reliability;
- causal competence or causal explanations;
- hidden-state or latent-reasoning recovery;
- arbitrary-task generalization;
- confirmed Ling cross-model distillation;
- treating full discrete CEF as an AUROC upper bound.

The main remaining risks are: one incorrect conditional-expectation equation, incomplete evidence traceability outside the supplied PECR freeze, underdefined CST load-bearing quantities, unresolved citation placeholders, and duplicated methods/notation.

## Freeze-checked numerical core

These manuscript values match the supplied freeze:

- Stage 2 probe-head AUROCs: \(0.8754\) and \(0.8407\).
- Qwen ConvFinQA S2: \(0.6508\).
- Qwen imputed/student score: \(0.7474\).
- Qwen full CEF: \(0.6870\).
- Student minus S2: \(+0.0966\).
- Item-bootstrap CI: \([+0.0183,+0.1740]\).
- Post-hoc source-group CI: \([+0.0190,+0.1736]\).
- Stage 3: 198 items and 990/990 worlds.
- Ling schema validity: \(79.1\%\).
- Ling numeric validity: \(57.7\%\).
- Ling S2: \(0.8275\,[0.6525,0.9983]\).
- Ling full CEF: \(0.8251\,[0.6456,0.9988]\).
- Ling full-minus-S2 delta: \(-0.0024\,[-0.0083,0.0023]\).

The supplied notes do **not**, however, independently expose the CST, S&P, FinQA, 40-item baseline, exact Ling-imputation intervals, or \(p=0.0002\) records. Those values may be correct, but they are not auditable from the freeze excerpt provided here.

---

## P1 issues

### 1. Evidence provenance is incomplete outside the PECR freeze

**Quote:** “On frozen VitaminC cohorts…”; “The S&P branch…”; “The official FinQA DEV split contains 883 rows…”; “On 200-item TRAIN controls…”

**Severity:** P1

**Problem:** The supplied evidence freeze is explicitly a PECR/ConvFinQA freeze. It does not contain the CST values, S&P values, FinQA DEV values, TRAIN retention values, or 40-item baseline values presented as frozen results. It also gives only the qualitative Ling imputation conclusion, not the exact manuscript intervals \([-0.0539,+0.1436]\) and \([-0.0476,+0.1453]\).

**Precise correction:** Add a provenance ledger or artifact identifier for every numerical block, with:

- freeze name/date;
- endpoint definition;
- sample size;
- point estimate;
- interval and bootstrap unit;
- target label;
- source artifact.

If separate CST/S&P/FinQA freezes exist, cite them explicitly. If not, remove “frozen” or label those numbers as historical/unverified rather than silently treating them as part of the supplied freeze.

---

### 2. The imputation “idealized case” is mathematically incorrect as written

**Quote:** “In the idealized case,
\[
\mathbb{E}\!\left[
\operatorname{CEF}(x)
\mid z,F_{-1},F_{+1}
\right]
=
\frac{
F_{-1}+F_{+1}
+\Pr(F_{-2}=1\mid z)
+\Pr(F_{+2}=1\mid z)
}{4}.
\]”

**Severity:** P1

**Problem:** Conditioning on \(F_{-1},F_{+1}\) generally changes the conditional distribution of \(F_{-2},F_{+2}\). The displayed equality is only valid under an additional conditional-independence assumption that is neither stated nor established.

**Precise correction:** Either:

1. remove the equality and describe the deployed score as a plug-in estimator; or
2. condition the stronger-probe terms on the observed mild-probe fidelity outcomes:
\[
\mathbb E[\mathrm{CEF}\mid z,F_{-1},F_{+1}]
=
\frac{
F_{-1}+F_{+1}
+\Pr(F_{-2}=1\mid z,F_{-1},F_{+1})
+\Pr(F_{+2}=1\mid z,F_{-1},F_{+1})
}{4}.
\]

Given the frozen heads use \(h_{\pm2}(z)\approx P(F_{\pm2}=1\mid z)\), the safest wording is: “The score is a plug-in hybrid that replaces the two missing binary outcomes with estimates conditional on \(z\).” Do not call it the exact conditional expectation given the observed mild fidelity outcomes without an explicit assumption.

---

### 3. The main Qwen result needs sharper target labeling

**Quote:** “Their predicted probe AUROCs were \(p_{-2}=0.8754\) and \(p_{+2}=0.8407\).”

**Quote:** “A Qwen TRAIN-fit response-rich student predicted two stronger probes that were not executed at deployment…”

**Severity:** P1

**Problem:** The head AUROCs are AUROCs for predicting \(F_{-2}\) and \(F_{+2}\), not AUROCs for predicting original correctness \(C\). The manuscript defines this later, but the abstract and contribution framing could make the high head AUROCs look like correctness AUROCs.

**Precise correction:** State explicitly that:

- \(0.8754\) is \(\operatorname{AUROC}(p_{-2},F_{-2})\);
- \(0.8407\) is \(\operatorname{AUROC}(p_{+2},F_{+2})\);
- \(0.7474\) is the AUROC of the combined imputed score for original correctness \(C\).

Also replace “predicted two stronger probes” with “estimated the two unobserved stronger-probe fidelity outcomes.” The student does not generate \(r_{-2}\) or \(r_{+2}\), nor does it execute those worlds.

The manuscript should explicitly state in the contribution framing that this is the **primary new frozen empirical contribution**: Qwen TRAIN-fit missing-probe imputation improves the Qwen ConvFinQA S2 diagnostic without increasing deployment calls.

---

### 4. CST’s central score and mechanism contrast are underdefined

**Quote:** “The intervention score is \(RS_q=-BF_q\)…”

**Quote:** “The reported direction contrast was \(+0.44\,[0.24,0.65]\).”

**Severity:** P1

**Problem:** \(BF_q\), \(q\), and the exact “direction contrast” estimand are not defined in the cleaned manuscript. The CST claims therefore cannot be reproduced or checked from the prose. The relationship between the generic \(q(x)\) in §2.3 and the CST-specific subscript \(q\) is also ambiguous.

**Precise correction:** Add the frozen definitions of:

- \(BF_q\);
- the sign convention for \(RS_q\);
- the positive class used for AUROC;
- the high-consensus threshold;
- the exact denominator and conditioning event for \(35/37\);
- the four cells in the Round10 \(2\times2\) analysis;
- the formula for the \(+0.44\) contrast and its interval procedure.

If the contrast is a difference in change rates, name both rates explicitly. Do not leave “direction contrast” as a label only.

---

### 5. The manuscript omits several mandatory integrity disclosures from the supplied freeze

**Quote:** “The appendix will provide:”

**Quote:** “Metadata repair disclosure. State that an offline deterministic repair changed the `program_ops` projection…”

**Severity:** P1

**Problem:** The supplied freeze specifically records that:

- the v0.10 analyzer repair materialized the two declared original-confidence fields;
- the direction-sign calculation was made explicit;
- the feature-list hash did not change;
- no forbidden outcome-derived feature appeared;
- no model calls were added;
- the 41-feature omission check and group-bootstrap audit are post-hoc integrity/sensitivity analyses, not replacements for frozen endpoints.

The manuscript includes the 11/126 `program_ops` projection repair, but not the full analyzer-repair disclosure or the 41-feature caveat. It also presents the appendix as a future plan rather than an actual reproducibility appendix.

**Precise correction:**

1. Distinguish the v0.10 analyzer repair from the `program_ops` projection repair, or state clearly that they are the same repair if they are.
2. Add the freeze facts above, including “no DEV refit, feature/model selection, or model calls.”
3. State explicitly that the 41-feature omission check and group-bootstrap audit are post-hoc sensitivity/integrity analyses.
4. Replace “The appendix will provide” with the actual appendix content before submission, or explicitly mark unavailable artifacts as unavailable.
5. Describe the reconstructed pre-projection hash as reconstructed metadata, not as a persisted raw pre-repair artifact.

---

### 6. Fourteen citation placeholders remain unresolved

**Quote:** “[CITATION NEEDED]”

**Severity:** P1

There are 14 occurrences. They can be mapped to canonical works, but not safely finalized from the supplied freeze alone because no bibliography is provided. The repeated dataset placeholders should reuse the same references rather than create duplicate entries.

| Placeholder | Manuscript location | Safe canonical target |
|---|---|---|
| 1 | “Confidence- and agreement-based reliability signals…” | Guo et al., *On Calibration of Modern Neural Networks*; add an LM-specific confidence source such as Kadavath et al., *Language Models (Mostly) Know What They Know*, if retained |
| 2 | “gold executable program from FinQA” | Zhuo et al., canonical *FinQA* dataset paper |
| 3 | “On 198 ConvFinQA DEV items” | Canonical *ConvFinQA* dataset paper, *ConvFinQA: Exploring the Chain of Thought for Conversational Financial Question Answering* |
| 4 | “frozen VitaminC cohorts” | Schuster et al., canonical VitaminC benchmark paper |
| 5 | “PECR is evaluated first on FinQA” | Same FinQA dataset paper as #2 |
| 6 | “For ConvFinQA” | Same ConvFinQA dataset paper as #3 |
| 7 | “Confidence, calibration…” | Guo et al.; optionally Kadavath et al. for LM confidence |
| 8 | “selective prediction or abstention” | Geifman and El-Yaniv, *Selective Classification for Deep Neural Networks* |
| 9 | “Agreement-based methods…” | A sampling-consistency source such as Manakul et al., *SelfCheckGPT*, and a semantic-uncertainty source if entropy/semantic dispersion remains in the sentence |
| 10 | “Self-consistency methods…” | Wang et al., *Self-Consistency Improves Chain of Thought Reasoning in Language Models* |
| 11 | “Robustness and stress-testing…” | Ribeiro et al., *Beyond Accuracy: Behavioral Testing of NLP Models with CheckList*; add a separate verified OOD/adversarial source if those claims remain |
| 12 | “Metamorphic testing…” | Xie et al., *Testing and Validating Machine Learning Classifiers by Metamorphic Testing* |
| 13 | “Counterfactual reasoning and causal evaluation…” | Kaushik et al., *Learning the Difference that Makes a Difference with Counterfactually-Augmented Data* covers the counterfactual part; a separate verified causal-evaluation reference is needed for the causal part |
| 14 | “Process and reasoning-verification work…” | Cobbe et al., *Training Verifiers to Solve Math Word Problems*, and/or Lightman et al., *Let’s Verify Step by Step* |

Do not use one guessed citation to cover the multi-topic claims in #9, #11, #13, or #14. Split those sentences if necessary.

---

## P2 issues

### 7. Method material is duplicated across Sections 3 and 4, with notation drift

**Quote:** “### 3.4 Response-rich missing-probe imputation”

**Quote:** “### 4.5 Sparse scoring and missing-probe imputation”

**Severity:** P2

**Problem:** Full CEF/S2 and imputation are defined in §3.3–§3.4 and then reintroduced in §4.4–§4.5. The section numbers themselves are valid—there are no duplicate numeric headings—but the duplicated method prose creates opportunities for inconsistent definitions.

There is also notation drift:

- \(z=\phi(d,r_{-1},r_{+1})\) in §3.4;
- \(z_{-1,+1}\) in §4.5 without definition;
- \(p_{\pm2}\) in one equation;
- \(\hat p_{\pm2}\) in another;
- \(\widehat{\operatorname{CEF}}_{\mathrm{imp}}\) versus \(\widehat{\mathrm{CEF}}\).

**Precise correction:** Keep formal definitions and equations in Section 3; use Section 4 only for protocol, cohort, and budget details. Define once:
\[
z=\phi(d,r_{-1},r_{+1}),
\]
and use one consistent notation for \(p_{\pm2}\) or \(\hat p_{\pm2}\).

---

### 8. A few load-bearing quantities need exact wording or definitions

**Quote:** “The corresponding confidence values were near chance, \(0.5181\) and \(0.5412\).”

**Severity:** P2

**Correction:** These are not confidence values; they are **confidence AUROCs**. Change the phrase to “confidence-based AUROCs were near chance.”

**Quote:** “Ling S2 increased from `0.8275` to `0.8536`, a delta of `+0.0262`.”

**Severity:** P2

**Correction:** The displayed rounded endpoints subtract to \(0.0261\), while the freeze reports \(+0.0262\) from unrounded values. Add “computed from unrounded estimates” or report more digits.

**Quote:** “Retention of full-CEF gain.”

**Severity:** P2

**Correction:** Define the retention ratio mathematically and identify its baseline. The reader should not have to infer whether the denominator uses chance, confidence, original accuracy, or another frozen baseline.

---

### 9. Some mechanism and portability language remains stronger than the evidence warrants

**Quote:** “Round10 rejects that explanation.”

**Quote:** “The Round10 mechanism analysis rules out a direction-free interpretation…”

**Severity:** P2

**Correction:** Use “provides evidence against” or “does not support, within this frozen contrast.” The manuscript correctly denies a causal account elsewhere; these stronger verbs partially undo that caution.

**Quote:** “cross-model-stable fraction of the full-CEF gain”

**Severity:** P2

**Correction:** Unless a formal cross-model stability test exists, use “a substantial fraction in both evaluated models” or “similar point estimates in the two evaluated models.”

**Quote:** “Reliability evaluation is more informative when…”

**Severity:** P2

**Correction:** Soften to “can be more informative in settings where the expected intervention consequence is independently specified.” This preserves the bounded thesis.

**Quote:** “provide a useful item-level reliability diagnostic beyond confidence or agreement alone.”

**Severity:** P2

**Correction:** Scope this to “beyond the tested confidence and agreement baselines in the reported cohorts.” The manuscript does not establish superiority over confidence or agreement generally.

---

### 10. S&P model labels and denominators are ambiguous

**Quote:** “static AUROCs of `0.6040` for Ling and `0.5569` for Hy.”

**Quote:** “Wrong-majority dates were common, with `161/166` dates… and `14/87` dates…”

**Severity:** P2

**Correction:** Give the full model identifier for “Hy” at first use. Explain why the denominators differ and identify the subset represented by each fraction. Also define B6/B8 and the structural-hardness gate either in the main text or by a precise artifact pointer.

---

### 11. The historical call-budget audit distracts from the frozen accounting

**Quote:** “A separate historical 50-item sparse-only audit recorded a 30.0% total-call reduction…”

**Severity:** P2

**Correction:** Move this to the appendix or remove it from the main paper. The primary frozen accounting is unambiguous: five planned calls for full CEF versus three for S2, a 40% total-call and 50% counterfactual-call reduction. The historical mixed accounting invites unnecessary comparison.

---

### 12. “Independent” transformed gold should be qualified

**Quote:** “independently obtains the transformed gold answer.”

**Severity:** P2

**Correction:** Say “computed from the frozen gold program independently of the model response.” The transformed answer is independent of the model output, but it is not independent of the benchmark’s gold program. This wording better supports the manuscript’s non-causal, construction-and-scoring interpretation.

---

## Requested checks: final status

### Universal reliability, causality, hidden-state recovery, and arbitrary-task generalization

**Status: Mostly passes.**

The following caveats are appropriately explicit:

- “not universal reasoning reliability”;
- “not hidden-state recovery”;
- “not causal competence”;
- “not arbitrary reasoning-task generalization”;
- “bounded to executable financial reasoning.”

Retain these statements. Only soften the few “rejects,” “rules out,” and “more informative” formulations noted above.

### Full discrete CEF as an AUROC upper bound

**Status: Pass.**

The manuscript correctly says:

> “Full discrete CEF is a reference score rather than an AUROC upper bound.”

This is the right interpretation. Keep the explanation that discrete CEF can have ties while the continuous imputed score can break those ties. Do not call the imputed score “surpassing a teacher.”

### Qwen ConvFinQA missing-probe result as the main contribution

**Status: Correct in substance; foregrounding should be stronger.**

The manuscript already calls it:

> “The strongest new result concerns missing-probe imputation.”

and

> “Most notably…”

That is consistent with the freeze. Make it explicit in the abstract/contribution framing and distinguish:

- head AUROCs: prediction of \(F_{-2}\) and \(F_{+2}\);
- student/imputed score AUROC: prediction of original correctness \(C\).

### Confirmed Ling distillation

**Status: Pass, with no substantive correction.**

The manuscript correctly reports the positive point estimate while emphasizing that both intervals cross zero and that there was no Ling refit, calibration, feature selection, or threshold selection. Retain:

> “not statistically confirmed cross-model distillation.”

Do not upgrade the Ling result to “confirmed,” “replicated distillation,” or “cross-model validation.”
