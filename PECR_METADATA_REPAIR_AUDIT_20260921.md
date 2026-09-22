# PECR DEV metadata repair audit

Audit date: 2026-09-21. No model calls were made.

## Audit decision

The repair changed only `program_ops` metadata used to define within-operation permutation strata. The original pre-repair raw manifest was not persisted, so this package explicitly reports no raw before-file hash rather than inventing one. A deterministic before/after projection hash is provided instead.

| item | value |
|---|---|
| records checked | 126 |
| records whose program_ops projection differs | 11 |
| reconstructed before projection SHA-256 | `655751001f203d70283ea585b2e2d210889761665fd99054789c8717c638c7f4` |
| final projection SHA-256 | `ea744f23eb989e02db9678e902a7d342b425954ac9722d7b658eadd9545cc7a2` |
| final cohort manifest SHA-256 | `6d249216f4da6b9bdcfc291ff2ae57ff8a1a516c1515b1d0e4877cd585b16735` |

## Model-facing byte audit

The final hashes independently match the hashes recorded in `DEV_ONE_SHOT_OFFLINE_METADATA_REPAIR.md`:

- `DEV_ONE_SHOT_WORLD_INPUTS.jsonl`: `b7d52a26b27be8cbd6bc71992ba5cd8603cce9f88f0d5005289c682ae1e47b10`
- `DEV_ONE_SHOT_WORLD_GOLD.jsonl`: `08f98e22a8fd4f3a13996fe9f362bfa9b3bcc7b4d9fe8bc0121269e87787abff`
- `DEV_ONE_SHOT_PROMPTS.jsonl`: `3f83f924f2d1ec639840c54843e0385d03536b8e34653ff99eb968f1ef6ddd82`

No model calls were rerun, no model result was used to derive the repair, and the repair rule is independently derivable from the executable program trace.

## Statistical scope

`program_ops` is used only for within-operation permutation strata. Therefore the primary CEF score and AUROC are deterministically independent of this metadata field, while the corrected final-operation null must use the repaired trace-derived strata. This is not a claim that the pre-repair and post-repair null p-values are numerically identical.

## Reproducibility

- Re-run: `python prepaper_audit/build_prepaper_audit.py`.
- Source note: `finqa_convfinqa/22_pecr_v0_8_official_dev_one_shot_20260921/DEV_ONE_SHOT_OFFLINE_METADATA_REPAIR.md`.
