# Scoped GitHub publication — 2026-09-22

Target repository: `Yuming166/when-consensus-lies`
Target ref: current checkout branch `codex/astra6-credit-20260918`

This publication contains the current paper/results package only. It does not publish the entire dirty worktree.

## Included scope

- The paper evidence ledger and bounded-claim memos at repository root.
- The reviewed, cited, audited NAACL Markdown/LaTeX package under `paper_intervention_tested_reliability_20260921/luna_max_naacl_draft_20260922/`.
- The ConvFinQA executable-semantics audit, frozen Stage 1 replication summary, Qwen missing-probe confirmation summary, Ling replication/zero-shot transfer summary, and final evidence freeze.
- Reproducibility contracts, deterministic analysis scripts, decision records, and static audit manifests for those summaries.

## Explicit exclusions

- All raw model-output records, prompts, public/gold row-level JSONL, feature rows, datasets, archives, upstream data, logs, PID files, caches, `__pycache__`, and runtime residue.
- Historical exploratory directories unrelated to the final evidence boundary.
- No changes to `main`, no force-push, no rebase, and no merge into `main`.

## Claim boundary retained in the published files

- Qwen ConvFinQA missing-probe imputation is prospectively confirmed on frozen DEV with the reported item-bootstrap interval.
- Ling zero-shot imputation is point-positive but not statistically confirmed.
- Full discrete CEF is a reference diagnostic, not an AUROC upper bound.
- FinQA/ConvFinQA support bounded executable financial-reasoning claims, not universal reasoning reliability or arbitrary-task generalization.
