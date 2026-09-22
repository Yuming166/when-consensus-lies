# ConvFinQA executable-semantics audit (2026-09-22)

- Status: **PROCEED_TO_FREEZE_REPLICATION_CONTRACT**
- Model/API calls: **0**
- Data source: released ConvFinQA archive, commit `cf3eed2d5984`
- `data.zip` SHA256: `d764271fae60d81b62e6d58dfc481807ebc8cfbcd633811241723c4a2101072a`

## Dataset shape

- Train item/conversation records: **3037**
- Dev item/conversation records: **421**
- Train turn records: **11104**
- Dev turn records: **1490**
- Train program turns: **7193**
- Train number turns excluded: **3911**
- Dev program turns: **1003**
- Dev number turns excluded: **487**
- Private test turn records are present but labels/program annotations are unavailable; they are **not auditable** and no test eligibility claim is made.

## Executable-world feasibility

- Eligible train program turns: **1814**
- Eligible dev program turns: **283**
- Eligible train conversations after one-per-conversation deduplication: **1344**
- Eligible dev conversations after one-per-conversation deduplication: **198**
- One-per-source-file sensitivity capacity: train **754**, dev **114**
- Train/dev source-file disjoint: **True**
- Train/dev conversation disjoint: **True**

Each eligible row passed: self-contained program execution, alignment to `annotation.exe_ans`, unique source occurrence to program-literal mapping, dependency-to-final-step check, all four `k=-2,-1,+1,+2` transformed executions, and two numeric-surface invariance checks.

## Conversation-state boundary

`program_turn` records expose `annotation.cur_dial`, `annotation.cur_program`, and `annotation.exe_ans`; the current question is taken as `cur_dial[-1]`. `number_turn` records are not treated as executable PECR items because their current program is an extracted number rather than an arithmetic program. All observed `#n` symbolic references were also checked to be local to the current comma-separated program sequence (train **3872**, dev **550**; no nonlocal references).

## Decision

**PROCEED_TO_FREEZE_REPLICATION_CONTRACT**

Freeze a ConvFinQA train-fit/dev-confirmation contract; do not call models until the item selection and feature mapping are sealed.

This audit establishes construction feasibility and sample capacity only. It does not establish PECR accuracy, missing-probe distillation improvement, or cross-task generalization.
