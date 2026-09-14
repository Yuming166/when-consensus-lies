# Large-Model Single-Point Validation — Mechanism Transfer (Qwen/Ling frozen RS_q -> gpt-6-astra errors)

Protocol: `cs-paper-gpt-singlepoint-20260914-round6` · Secondary evidence (not a gate).

Frozen Round-3 Qwen3.5-4B `RS_q` and Round-4 Ling-3.0-tiny `RS_q` (both `=-BF_q`) are evaluated
against **gpt-6-astra's own** `consensus_wrong` on the gpt HC subset (n=96).

| source | AUROC (pair-grouped CI) | Risk@80 reduction (CI) | Spearman(src RS_q, gpt RS_q) |
|---|---|---|---|
| Qwen3.5-4B (round3) | 0.838 [0.693, 0.950] (n=96) | 0.684 [-0.120, 1.000] | 0.6787 |
| Ling-3.0-tiny (round4) | 0.737 [0.568, 0.862] (n=96) | 0.211 [-0.440, 0.844] | 0.3656 |

## Interpretation

- Both frozen scores transfer at aggregate level (AUROC CI lower bound > 0.5), with Qwen's
  risk score transferring more strongly than Ling's (consistent with Qwen's higher item-level
  RS_q correlation, Spearman 0.68 vs 0.37).
- Item-level transfer is secondary; the within-model mechanism (natural-reversal fidelity
  lower on wrong HC consensus) is the primary claim and passes (see within-model report).
- Boundaries: transfer AUROC is computed against only 8 wrong HC items; treat the CI as
  indicative; no claim of per-item ranking equivalence across models.
