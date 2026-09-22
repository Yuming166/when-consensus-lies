# ConvFinQA Stage 3 Ling freeze

- Status: `FROZEN_PRE_MODEL_CALL`
- Cohort: the already frozen 198-item, 990-world ConvFinQA DEV cohort from Stage 1.
- Model: `Ling-3.0-tiny` only; endpoint and model identity are frozen in the contract.
- Protocol: one fresh original/-2/-1/+1/+2 request per world; no retries, cache, fallback, or tuning.
- Primary evaluation: frozen `S2` and `full CEF` against current-turn normalized executable numeric correctness.
- No Ling result has been inspected or used for feature/model selection.
