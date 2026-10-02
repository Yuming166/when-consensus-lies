# Contract for a separately versioned future model generation

This is an executable input reconstruction benchmark with frozen policy
dependencies. No future responses, labels, G96 or API run were produced here.
An external caller supplies responses and follows the stage interfaces below.
The input exporter creates private payloads; it is not a network client.

1. Run `src/rebuild_worlds.py` with a new private output directory and chosen
   saved profile/model name. Retain `LOCAL_GENERATION.json`, item ID, world,
   request canonical hash, actual model identity and collection metadata.
   Preserve all 2,225 requested IDs and the 16 excluded frame IDs. Do not select
   candidates using model outputs, labels or predictor scores.
2. For each requested `(item_id, world)`, retain the actual structured
   `answer_value` type, `unit`, `confidence`, and `supporting_evidence` validation
   field. Preserve missing/malformed answers and original collection status as
   such. Never infer numeric answers from reasoning or HTTP status.
3. `src/frozen/three_world_parser.py:parse_resp` consumes
   `{'parsed_json': response_object}` and returns normalized
   `{'value','unit','confidence'}` or the historical failure reason. Check the
   resulting numbers and matrices for finiteness separately: the historical
   parser alone can accept infinity/NaN from float conversion. This matrix gate
   must report `nonfinite_numeric`, not success, without changing frozen parser
   semantics. Missing recorded status remains unknown.
4. Only an explicitly permitted, isolated label stage may access TRAIN
   `qa.answer`. Call `src/frozen/label_policy.py:label_one` with the original
   `answer_value`, **not the normalized float**, and that gold value. Its return
   is `(correct, reason)`; store `error=1-correct` only when correct is known.
   Retain the new original field hash, label-rule source SHA and gold-file SHA.
   Do not pass gold values/label columns into feature construction or decode
   any holdout. This release's reconstruction stage never reads that field.
5. G96 consumes only the original input fields
   `question, pre_text, table_original, post_text, original_response` through
   the frozen builder `_safe`/`_graph`; the original response contains the new
   answer/unit/confidence and supporting_evidence validation field. `_graph`
   returns float32; export its exact values as float64. Failure is recorded as
   invalid, without historical response defaults or another model's G.
   Hashed text features are not used by this six-method benchmark.
6. Rebuild Raw17 and Curve33 with `src/numeric.py:curve33` using the three new
   normalized answers and the saved edit operands/direction. The first 17
   Curve columns are Raw17. Preserve exact feature column identities, including
   duplicate historical names. Gold and labels are absent from these records.
7. Independently join known labels and finite feature-valid rows by explicit
   IDs, preserving original attempted-frame order. Report every exclusion,
   label support, world parse status and unit combination. The strict queue
   may change; do not lock it to historical 2,142/2,050 rows or filter by
   correctness. Create group-only five-fold assignments on the new queue and
   record their new/post-hoc status. Labels/predictions must not determine IDs,
   groups or fold membership.
8. Create a new release registry/reference directory. Fix complete HGB
   parameters and all six methods before numerical training/evaluation. Record
   software versions and paired source-group intervals. The current historical
   OOF and labels remain immutable; exact reproduction targets in this release
   cannot substitute for outcomes of a newly called model.

The pure policy modules can be imported using the release `src` directory on
Python's module path. They contain no corpus loader or network client. Tests of
these helpers in this release use only synthetic answers and tiny synthetic
tables. Exact saved input reconstruction does not certify new-model semantic
validity, financial reasoning correctness, or intervention effectiveness.
