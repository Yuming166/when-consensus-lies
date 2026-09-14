# Phase 6 — Cross-Model (Ling-3.0-tiny): HONEST FAIL at pipeline/validity layer

Protocol: `cs-paper-vitaminc-2026-09-13` section 9 (frozen before Ling calls). Same cohort
(first 100 pairs = 200 items of the main cohort), same artifacts, same oracle, same
conditions, same BF_q, same gates. Server: vLLM 0.29.0 on GPU5 (127.0.0.1:31520,
enable_thinking=false via the model's own chat template), model Ling-3.0-tiny.

## Result

- 5,000 calls; **valid rate 0.3108 (1,554/5,000)** — pipeline gate (>= 0.95) FAILS.
- First-pass valid 11.9%; repair attempts raise success to 31% but 69% still fail both.
- Dominant failure (6,890 parse errors): "missing decision fields: ['agent_id']" — the tiny
  model emits {"answer","confidence","cited_evidence_ids"} but omits/incorrectly names the
  frozen per-call agent_id. Per-condition success: original 35.7%, paraphrase 42.5%,
  reverse 35.8%, synthetic_reverse 32.8%, remove 8.6%.

## Diagnosis (honest)

- The identical frozen protocol does NOT transfer to Ling-3.0-tiny at the execution level:
  the model cannot satisfy the strict per-call JSON contract (agent_id integrity check).
- Because 69% of calls fail, the remaining 31% form a model-dependent filtered subset;
  computing substantive gates (AUROC / Risk@80) on it would be biased and is NOT reported
  as a valid result. Per-model comparison and cross-model transfer are therefore
  NOT EVALUABLE this round.
- The failure is model capability (instruction-following for the strict contract), not the
  oracle definition, evidence construction, or sample size. The server itself was started
  safely (GPU5, no interference with GPU4/GPU6); the JSON-parsing issue was reproducible
  in smoke tests with several prompt variants before the run.

## Boundaries / next-round design

- Cross-model within-model validity: FAIL (pipeline) — no substantive claim about Ling's
  mechanism this round. No fudging: no parser relaxation, no filtered-subset gating, no
  post-hoc oracle changes.
- Next round: pre-register a model-capability parse accommodation (e.g., accept
  agent_id-independent records with the task-assignment agent_index, or add a frozen
  JSON exemplar to the prompt) BEFORE Ling calls, or choose a second model that satisfies
  the strict contract; keep the frozen oracle and gates unchanged.
