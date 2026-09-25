# PECR independent review handoff v2

## What to send to reviewers

**Construction, Stage A:** send only `CONSTRUCTION_STAGE_A_DIRECTION_BLIND_V2.jsonl` and `CONSTRUCTION_STAGE_A_FORM_V2.csv`. This is 20 unique non-modal expected-sign cases. It includes source program, source question/table, three public worlds and construction paths; it excludes frozen expected signs, all model answers, risk scores, and correctness labels. Reviewer independently derives each world direction and documents reasons. Return completed form and its SHA-256. Do not send the sealed Stage-B key or coordinator note yet.

**Answer/gold semantic review:** send `ANSWER_GOLD_REVIEW_28_UNIQUE_ITEMS_V2.jsonl` and `ANSWER_GOLD_REVIEW_FORM_28_V2.csv`. Gold answer and original model answer are visible by request. The underlying queue has **35 flagged records but 28 unique IDs**; seven records are duplicate occurrences of already represented IDs. `ANSWER_GOLD_REVIEW_35_QUEUE_RECORDS_V2.jsonl` preserves every occurrence and its queue ordinal/reason; `ANSWER_GOLD_REVIEW_28_UNIQUE_ITEMS_V2.jsonl` is the deduplicated reviewer packet. Review one judgment per unique question and retain queue record ordinals/reasons. Frozen correctness labels and PECR risk scores are withheld. This is not a blind-to-gold review; it is an independent semantic adjudication with gold shown, and the label itself withheld.

The 35-record/28-item answer review is distinct from the construction-sign review. No relation-minus/plus model responses are included in the answer packet, so it cannot adjudicate three-world response validity.

## Stage B
After the completed Stage-A construction form is SHA-256 frozen, run `make_construction_disagreement_v2.py` with the form, its hash, and the sealed key. Only then create a per-item disagreement table. The BLK and AMT coordinator note is also Stage-B only.

After the answer/gold review form is completed and hashed, use `make_answer_label_comparison_v2.py` to compare reviewer judgments with frozen labels. Optional sensitivity requires a separately completed alternate binary label column; the script writes parallel metrics and never overwrites primary labels/scores.

All analyses are offline. No model/API calls are part of this workflow.

## Public-branch release boundary
This public handoff intentionally excludes the sealed Stage-B expected-sign key and BLK/AMT coordinator-only note. Do not treat the public repository copy as permission to reveal those materials before the Stage-A form is returned and hashed. The released answer/gold packet does contain benchmark answers and model responses; it is published at the project owner's explicit request, with the associated benchmark-contamination risk acknowledged.
