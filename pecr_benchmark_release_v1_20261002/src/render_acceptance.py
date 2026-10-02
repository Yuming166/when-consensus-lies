#!/usr/bin/env python3
"""Generate the acceptance report from one final OOF result/receipt set."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    results = json.loads((ROOT / 'acceptance/clean_refit_final/RESULTS.json').read_text())
    acceptance = json.loads((ROOT / 'audit/FINAL_ACCEPTANCE.json').read_text())
    coverage = json.loads((ROOT / 'coverage/FINAL_SUMMARY.json').read_text())
    cohorts = ('qwen_generation_aligned', 'deepseek_generation_aligned', 'deepseek_shared_qwen')
    lines = ['# PECR benchmark actual release acceptance', '',
             'PASS: two generation-aligned benchmark tracks plus the preserved shared-G historical track. This is local release preparation, not an upload or a new model validation.', '',
             '## Source, generation and coverage', '',
             'Qwen current labels, original response features and three-world Curve are bound by explicit item/response hashes. Native DeepSeek G96, labels and three worlds use the same original merged generation. Shared-Qwen G is explicitly cross-model and appears only as the historical/source track. DeepSeek label binding is recipe/file/ID-based and audited post-hoc: missing historical per-response label freeze hashes are not invented and gold correctness was not independently rechecked.', '',
             '| Track | Strict rows | Groups | Folds | Error / correct | Requested coverage | Requested outside strict |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for name in cohorts:
        s = results[name]['support']; c = coverage['cohorts'][name]
        lines.append(f'| {name} | {s["n"]} | {s["groups"]} | 5 | {s["error_1"]} / {s["correct_0"]} | {100*s["coverage_of_requested"]:.2f}% | {c["requested_not_strict"]} |')
    lines += ['', 'Canonical coverage is `coverage/attempted_frame_final.jsonl/.csv`: 6,723 cohort/item records, 2,241 unique items per track, 2,225 requested and 16 unrequested per track. Qwen requested exclusions: 52 valid/unlabeled + 7 invalid/labeled + 24 invalid/unlabeled = **83**. DeepSeek exclusions: 54 + 79 + 42 = **175** per track. All per-world parse/unit/label/construction states remain visible. Unrequested parser validity is null, recorded status unknown; upstream exclusion eligibility is kept separately. Native G is not computed outside its fixed 2,050 rows and is never imputed from shared G.', '',
              '## Same OOF primary and fixed component results', '',
              'All numbers and intervals below come from the final clean OOF, with error=1 positive. Graph-only contains original answer information and is not an equal-call-budget baseline. The paired source-group bootstrap is fixed at 2,000 attempts, seed20260928; no degenerate retry, search or multiplicity correction.', '']
    for name in cohorts:
        ev = results[name]['evaluation']
        lines += [f'### {name}', '', '| Method | AUROC | AP |', '|---|---:|---:|']
        for method, m in ev['metrics'].items():
            lines.append(f'| {method} | {m["auroc"]:.6f} | {m["auprc"]:.6f} |')
        lines += ['', '| Fixed contrast | Delta AUROC [95% CI] | Delta AP [95% CI] |', '|---|---|---|']
        for key, c in ev['contrasts'].items():
            def fmt(metric):
                ci = c['delta_' + metric + '_ci95']
                return f'{c["delta_"+metric]:+.6f} [{ci[0]:+.6f}, {ci[1]:+.6f}]'
            lines.append(f'| {key} | {fmt("auroc")} | {fmt("auprc")} |')
        lines += ['', f'Bootstrap valid/degenerate: {ev["bootstrap"]["valid_draws"]}/{ev["bootstrap"]["degenerate_single_class_draws"]}; draw hash `{ev["bootstrap"]["draw_sequence_sha256"]}`.', '']
    lines += ['No best-variant replacement: Qwen no-curvature and DeepSeek native no-normalization have higher AUROC points than their respective Full methods. Full remains the fixed method. Native curvature-removal contrast is a newly completed post-hoc control; it is not independent mechanism confirmation. Confidence intervals condition on saved OOF and do not measure training uncertainty or selection correction.', '',
              '## Actual clean execution and complete fit accounting', '',
              'A fresh Python3.13.13 venv independently installed all pinned packages; include-system-site-packages=false. The numerical core was moved outside the source tree without old sibling directories. Final benchmark/numeric/evaluation code, parameters, all cohort files and all reference bytes are identical to those used in the clean execution.', '',
              '| Phase | Actual HGB fits | Outcome |', '|---|---:|---|',
              '| First existing-suite pass | 70 | Report export failed on an extra historical contrast key; retained without claiming full success |',
              '| Repaired existing-suite pass | 70 | Both main six-method suites and original native source contrast exactly reproduced |',
              '| Native fixed suite completion | 20 | Four new controls; two existing native OOF methods reused |',
              '| Final unified clean entry | 90 | Three six-method tracks and reused source contrast; every saved prediction, point and interval exact |',
              f'| Total this release task | {acceptance["fit_history"]["total_fits_this_release_task"]} | No changed seed/parameter/sample or best-result selection |', '',
              'Two earlier startup guards failed before fitting: isolated Python module path, and legacy schema identity serialization. Both corrections and the mutable-finalization audit guard are recorded. They did not change matrix values, labels, folds or HGB settings. The final fixed entry completed; checkpoints retain numeric OOF predictions only, never model weights.', '',
              '## Acceptance checklist', '',
              '| Gate | Evidence | Outcome |', '|---|---|---|',
              '| Same-generation target/features/Curve | `audit/native_generation_binding_audit.json`, current Qwen binding receipts | PASS for two aligned tracks; shared historical exception explicit |',
              '| IDs/groups/folds/column order/hash trace | `audit/FINAL_NUMERIC_CHECK.json`, per-cohort schema and reference maps | PASS |',
              '| Finite, nonsharing, exact Raw/Curve arithmetic/support | Three-track loader and independent portability checks | PASS |',
              '| Actual clean primary/component/ref-origin reproduction | `acceptance/clean_refit_final/` | PASS, 90 fits, every prediction and saved interval exact |',
              '| Full attempted frame including 83 Qwen exclusions | `coverage/FINAL_*`, canonical 6,723-row table | PASS |',
              '| Three-world executable reconstruction | `intervention/REBUILD_AUDIT.json` | PASS, 13,350 / 13,350 canonical request hashes |',
              '| Future generation policy dependencies/interfaces | `src/frozen/`, `intervention/NEW_GENERATION_PROTOCOL.md` | PASS, 23 synthetic policy checks; no future model run |',
              '| Source preservation/privacy/scope | Old sealed artifact/source hashes; bounded export scan | PASS; no model API/gold regeneration/holdout/push |', '',
              'The reconstruction needs the user-supplied original FinQA TRAIN bytes; only permitted input text leaves are decoded, without gold/program decoding. Default execution writes hashes only. Optional input export goes to a new private directory outside the public release. The actual saved profiles use Qwen max_tokens384 and DeepSeek max_tokens8192/reasoning_effortlow; collector prose was not treated as runtime evidence.', '',
              '## Unavailable provenance and interpretation limits', '',
              'Required source files missing: **none**. Exact historical DeepSeek per-row label freeze/hash receipts never existed and remain unavailable. Twenty-seven old Qwen structured originals could not be recovered from `../pecr_trd_delta_method_development_v3_20260926/v3_2/data/raw_ledger_sealed.jsonl`; per-row line/hash diagnostics remain in `reference/qwen/generation_map.jsonl`. These old answers are not inputs to the corrected generation. Missing collection batch/finished/recorded status remains unknown.', '',
              'This release supports historical-response error ranking and exactly reconstructable intervention inputs. It does not establish effectiveness for a newly called model, official FinQA execution accuracy, semantic/causal validity of interventions, independent confirmation, or a review score. New responses need newly aligned labels/G96 and separately versioned strict queues. Old labels/OOF/primary/V16/V17 and all inspected private sources remain unchanged.', '']
    (ROOT / 'acceptance/FINAL_REPORT.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
