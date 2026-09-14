# Artifact repair note (outcome-free, pre-call)

- One distractor unit (unique_id=5ee39419c9e77c0008ccfc9b_1, a citation-heavy Google-Books
  sentence from page "Aeneas") could not be paraphrased within the frozen generation
  constraints (2 attempts + regeneration; parse filter rejected outputs).
- Distractors are NON-decision-relevant by the frozen oracle (R5); this does not affect any
  scored condition. To keep the frozen "all artifacts usable" pipeline invariant, the
  distractor for pair 5ea2d97bc9e77c0009cda654:3b2a4ae4ae0e (page Sea of Japan) was swapped
  to the next deterministic candidate (page Jaret Reddick, jaccard(claim,D)=0), and its
  paraphrase was generated and verified usable.
- No labels, no outcomes, and no scored evidence units were involved. selection_audit.json
  and artifact_hashes.json were regenerated from the final frozen state.
