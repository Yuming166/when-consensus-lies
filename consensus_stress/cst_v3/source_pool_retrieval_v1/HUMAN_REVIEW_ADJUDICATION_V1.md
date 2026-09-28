# CST V3 human-review adjudication v1

## Scope

This record resolves the three item-level disagreements between the two independent reviewer files supplied for the 34 inherited attempts. The original reviewer CSVs remain unchanged and are the audit trail.

## Adjudication decisions

| item_id | disagreement | adopted reviewer | adopted values | reason/status |
|---|---|---|---|---|
| `5ee3949ac9e77c0008ccfd84:dabb11a3a4e5:support` | `counter_target`, `counter_is_directional` | reviewer1 | `counter_target=support`; `counter_is_directional=uncertain` | Adopt reviewer1's judgment. The row remains `construction-failure` because the required support append is missing. |
| `5ee3949ac9e77c0008ccfd84:dabb11a3a4e5:refute` | `A_relation`, `AA_target`, `neutral_target`, `support_target` | reviewer2 | `A_relation=refute`; `AA_target=refute`; `neutral_target=refute`; `support_target=insufficient` | Adopt reviewer2's judgment. The row remains `construction-failure` because the required counter append is missing. |
| `5ea2d97bc9e77c0009cda6e4:2a8eb9fe5136:support` | `counter_is_directional` | reviewer1 | `counter_is_directional=no` | Adopt reviewer1's judgment. The row remains `construction-failure` because the required support append is missing. |

All fields not listed above retain the common reviewer value. The user supplied the adjudication decisions; no model output was used.

## Final review status

- Reviewer coverage: `34/34` items for each reviewer.
- Resolved item-level disagreements: `3`.
- Final eligible items: `0`.
- Final construction failures: `34`.
- Eligible source groups: `0/17`.
- CST model calls: `0`.
- CST launch decision: `NO-GO`.

The adjudication does not repair missing source material or convert any item into a complete four-condition CST row. It only fixes the semantic review record for the three disputed items.
