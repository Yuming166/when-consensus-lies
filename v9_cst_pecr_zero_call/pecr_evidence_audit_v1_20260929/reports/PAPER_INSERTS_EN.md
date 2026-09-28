# Paper-ready English insertions (with claim boundaries)

## Data flow and coverage

We constructed a three-world development queue from 2,241 manifest items. A label-blind mechanical construction retained 2,225 candidates and excluded 16 items flagged by conservative identity checks. The retained candidates generated 6,675 requests (original, positive, and negative worlds); 6,673 records contained a parsed JSON payload, yielding 2,223 items with JSON present in all three worlds. After restricting to items with frozen correctness labels and strict numeric/confidence parsing, the final analysis set contained 1,735 items from 424 source groups (1,375 original-answer errors and 360 correct answers). Thus, the reported 1,735/1,735 feature coverage is conditional on the strict analysis set; it corresponds to 77.98% of the 2,225 mechanical candidates and 77.42% of the full 2,241-item manifest.

## Main development results

Using fixed out-of-fold predictions on the 1,735-item development set, graph-only, two-world HGB, ordinary three-world HGB, and Curve HGB obtained AUROCs of 0.7275, 0.7722, 0.7978, and 0.8138, respectively; corresponding AUPRC values were 0.9032, 0.9201, 0.9308, and 0.9371. Curve HGB exceeded ordinary three-world HGB by 0.0160 AUROC, with a source-group bootstrap 95% interval of [0.0041, 0.0269] under the fixed OOF protocol. The two-world comparison was unfavorable relative to ordinary three-world HGB (−0.0256, 95% CI [−0.0428, −0.0091]), indicating that the additional reverse-world response contains useful signal in this development analysis.

## Transformer exploratory results

A saved Transformer full model achieved AUROC 0.7924 and AUPRC 0.9265, below Curve HGB (0.8138/0.9371). Removing consistency, edit, numeric, or reverse components yielded AUROCs of 0.7914, 0.7915, 0.7924, and 0.7922, while shuffled pairing yielded 0.7926. These exploratory ablations do not provide clean evidence that the proposed Transformer mechanisms add value; the no-HGB ablation fell to 0.5247, underscoring that the neural model relied heavily on the HGB branch.

## Limitations

These are repeatedly used development-set analyses rather than independent confirmation results. The reverse-world construction is mechanically generated and its semantic validity has only been assessed in a reported 50-item review outcome; the underlying reviewer records were not available for independent verification. We therefore present the results as evidence that program-conditioned multi-world response features are promising on this development queue, not as an independent generalization or state-of-the-art claim.
