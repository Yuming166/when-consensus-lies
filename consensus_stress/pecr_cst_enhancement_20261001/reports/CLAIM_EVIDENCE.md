# Claim–evidence map and missing materials

| Claim boundary | Evidence | Status |
|---|---|---|
| PECR is a bidirectional response-curve representation | Frozen feature implementation and audited result (`CURVE_HGB_AUDITED.json`), 1,735 strict rows | Supported as development implementation result |
| Curve HGB exceeds ordinary three-world HGB on this development split | AUROC 0.813757 vs 0.797802; source-group CI for delta [0.004111, 0.026887] | Bounded development finding; not independent generalization |
| CST counter response is selective | Stored `_agent_flip` recomputed from Round-6/7 decisions; selected strata have zero flip discrepancies | Behavioral flip pattern only; semantic validity unresolved |
| CST placebo is a valid inert control | Round-7 stored patterns include placebo flips; historical ceiling failure remains | Unsupported; explicitly failed control |
| Selected examples are semantically valid and publishable | No completed human forms, identities/adjudication, or item-level redistribution permission | Blocked |
| CST full prompts can be reproduced | Structured records/cache expose hashes and assistant content; complete request messages absent | Blocked |
| V3 is a validated main test set | V3 invalid-construction evidence and no eligible groups | Unsupported; boundary evidence only |

## Missing material checklist

- PECR item-level semantic review forms, reviewer identities, disagreement and adjudication.
- PECR source-document redistribution/license terms.
- CST complete rendered prompts/messages and source-group/independence mapping.
- CST human semantic validity review and redistribution permissions.
- Full fold manifests/feature snapshots/training traces for independently reproducible HGB OOF.
- Offline LaTeX compiler and resulting PDF for page-by-page visual inspection.

## Frozen pre-call cross-model plan

For N selected PECR items, M answer models, and R retries, a complete three-world run costs `3*N*M*R` answer calls; a matched CST run costs `3*100*M*R` condition calls (plus any separately frozen original calls). Freeze model IDs, prompts, temperatures, retry policy, request hashes, and stopping rules before execution. The present package performs zero calls.
