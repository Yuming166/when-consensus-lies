#!/usr/bin/env python3
"""Release entry: validate, retrain, and render fixed historical-risk benchmarks."""
import argparse
import csv
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from threadpoolctl import threadpool_info, threadpool_limits

# Python -I removes the script directory; use only this release's own modules.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluation import evaluate, support
from numeric import ALIGNED_NATIVE, COHORTS, ROOT, load_cohort, load_native, read_jsonl, sha256


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def validation(root):
    data = {name: load_cohort(name, root) for name in COHORTS}
    if (root / 'cohorts' / ALIGNED_NATIVE).exists():
        data[ALIGNED_NATIVE] = load_cohort(ALIGNED_NATIVE, root)
        a, s = data[ALIGNED_NATIVE], data[COHORTS[1]]
        assert all(np.array_equal(a[k], s[k]) for k in ('item_ids', 'groups', 'y', 'outer_fold', 'raw17', 'Curve33'))
    native = load_native(data[COHORTS[1]], root)
    if ALIGNED_NATIVE in data:
        assert np.array_equal(data[ALIGNED_NATIVE]['G96'], native['G96'])
        assert np.array_equal(data[ALIGNED_NATIVE]['reference']['full_curve'], native['reference']['native_G_curve'])
        assert np.array_equal(data[ALIGNED_NATIVE]['reference']['raw_three_world'], native['reference']['native_G_raw'])
    checks = {'unique_IDs_and_exact_row_order': True, 'label_group_fold_reference_alignment': True,
              'group_disjoint_and_group_only_reconstructed_folds': True,
              'exact_named_feature_column_order_and_dimensions': True,
              'finite_pairwise_nonsharing_writable_matrices': True,
              'Raw17_equals_Curve33_prefix_and_exact_arithmetic': True,
              'world_raw_curve_have_identical_ID_coverage': True,
              'saved_native_shared_aliases_equal_primary_OOF': True}
    receipt = {'all_passed': True, 'cohorts': {}, 'checks': checks, 'model_API_calls': 0,
               'corpus_gold_ledger_checkpoint_inputs': False, 'fits': 0}
    for name, d in data.items():
        receipt['cohorts'][name] = {**support(d['y'], d['groups'], len(d['y'])),
                                  'fold_support': fold_support(d),
                                  'matrix_dimensions': {k: list(a.shape) for k, a in d['methods'].items()}}
    coverage = root / 'coverage/FINAL_SUMMARY.json'
    if not coverage.exists():
        coverage = root / 'coverage/SUMMARY.json'
    if coverage.exists():
        summary = json.loads(coverage.read_text())
        receipt['coverage_summary'] = summary
    framepath = root / 'coverage/attempted_frame_final.jsonl'
    if framepath.exists():
        frame = read_jsonl(framepath)
        for name, d in data.items():
            records = [r for r in frame if r['cohort'] == name]
            assert len(records) == len({r['item_id'] for r in records}) == 2241
            assert [r['frame_row_index'] for r in records] == list(range(2241))
            assert sum(r['requested'] for r in records) == 2225
            strict = [r for r in records if r['strict_member']]
            assert [r['item_id'] for r in strict] == d['item_ids'].tolist()
            assert [r['source_group'] for r in strict] == d['groups'].tolist()
            assert [r['error'] for r in strict] == d['y'].tolist()
            assert sum(r['requested'] and not r['strict_member'] for r in records) == (83 if name == COHORTS[0] else 175)
            for row in records:
                assert set(row['worlds']) == {'original', 'positive', 'negative'}
                if not row['requested']:
                    assert all(w['offline_parser_valid'] is None for w in row['worlds'].values())
                if row['strict_member'] and name != COHORTS[1]:
                    assert row['G96_origin']['same_generation_as_label_and_curve'] is True
                    assert row['G96_origin']['saved_fallback'] is False
            if name == ALIGNED_NATIVE:
                assert all(not r['G96_origin']['G96_available'] for r in records if not r['strict_member'])
        receipt['checks']['full_attempted_coverage_and_unknown_statuses_verified'] = True
        receipt['checks']['aligned_tracks_same_generation_original_feature_binding'] = True
        receipt['checks']['native_missing_G_not_filled_with_shared_G'] = True
    seal = root / 'SHA256SUMS.txt'
    if seal.exists():
        for line in seal.read_text().splitlines():
            digest, rel = line.split('  ', 1)
            p = root / rel
            assert p.resolve().is_relative_to(root.resolve()) and sha256(p) == digest, rel
        receipt['release_seal_verified'] = True
    return data, native, receipt


def fold_support(d):
    result = []
    for k in range(5):
        m = d['outer_fold'] == k
        result.append({'fold': k, 'n': int(m.sum()), 'groups': len(set(d['groups'][m])),
                       'error_1': int(d['y'][m].sum()), 'correct_0': int(m.sum() - d['y'][m].sum())})
    return result


def compare_predictions(out, ids, groups, folds, preds, reference):
    result = {}
    with (out / 'PREDICTION_DIFFERENCES.csv').open('x', newline='') as f:
        w = csv.writer(f)
        w.writerow(['row_index', 'item_id', 'source_group', 'outer_fold', 'method',
                    'reference_prediction', 'new_prediction', 'difference'])
        for key, p in preds.items():
            delta = p - reference[key]
            result[key] = {'exact_prediction_match': bool(np.array_equal(p, reference[key])),
                           'different_rows': int(np.count_nonzero(delta)),
                           'max_abs_prediction_difference': float(np.max(np.abs(delta)))}
            for i in np.flatnonzero(delta):
                w.writerow([i, ids[i], groups[i], int(folds[i]), key,
                            repr(float(reference[key][i])), repr(float(p[i])), repr(float(delta[i]))])
    return {'methods': result, 'all_predictions_exact': all(x['exact_prediction_match'] for x in result.values()),
            'old_primary_modified': False, 'no_search_or_retry': True}


def reference_evaluation(name, root):
    if name == COHORTS[0]:
        return json.loads((root / 'reference/qwen/METRICS.json').read_text())['evaluation']
    if name == COHORTS[1]:
        return json.loads((root / 'reference/deepseek/PRIMARY_AND_ABLATION.json').read_text())['deepseek_v2_component']['evaluation']
    if name == ALIGNED_NATIVE:
        return json.loads((root / 'reference/deepseek_aligned/METRICS.json').read_text())['evaluation']
    return json.loads((root / 'reference/native/METRICS.json').read_text())['evaluation']


def compare_evaluation(actual, reference):
    diffs = []
    not_recomputed = []
    for method, values in reference['metrics'].items():
        for key in ('auroc', 'auprc', 'auroc_ci95', 'auprc_ci95'):
            if key in values and values[key] != actual['metrics'][method][key]:
                diffs.append({'method': method, 'key': key, 'old': values[key], 'new': actual['metrics'][method][key]})
    actual_pairs = {(v['left'], v['right']): v for v in actual['contrasts'].values()}
    for contrast in reference['contrasts'].values():
        pair = (contrast['left'], contrast['right'])
        if pair not in actual_pairs:
            not_recomputed.append({'pair': list(pair), 'reason': 'not in fixed release contrast specification'})
            continue
        for key in ('delta_auroc', 'delta_auprc', 'delta_auroc_ci95', 'delta_auprc_ci95'):
            if contrast[key] != actual_pairs[pair][key]:
                diffs.append({'pair': list(pair), 'key': key, 'old': contrast[key], 'new': actual_pairs[pair][key]})
    return {'all_saved_points_and_intervals_exact': not diffs, 'differences': diffs,
            'historical_additional_contrasts_not_recomputed': not_recomputed}


def retrain(root, out):
    assert not out.exists(), 'Output directory must be new; references are immutable'
    assert not any(out.resolve().is_relative_to((root / p).resolve()) for p in ('cohorts', 'reference', 'src', 'protocol', 'coverage'))
    data, native, receipt = validation(root)
    spec = json.loads((root / 'protocol/METHODS.json').read_text())
    params = json.loads((root / 'protocol/HGB_PARAMS.json').read_text())['parameters']
    assert HistGradientBoostingClassifier(**params).get_params() == params
    out.mkdir(parents=True)
    source_paths = [p for folder in ('cohorts', 'reference', 'src', 'protocol')
                    for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    before = {str(p.relative_to(root)): sha256(p) for p in source_paths}
    write_json(out / 'VALIDATION.json', receipt)
    runtime = {'started_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
               'python_prefix': sys.prefix, 'base_prefix': sys.base_prefix,
               'system_site_packages': any('site-packages' in p and not Path(p).is_relative_to(Path(sys.prefix)) for p in sys.path),
               'platform': platform.platform(),
               'versions': {n: importlib.metadata.version(n) for n in
                            ('numpy', 'scipy', 'scikit-learn', 'threadpoolctl', 'joblib', 'narwhals', 'cloudpickle')},
               'package_locations': {n: str(importlib.metadata.distribution(n).locate_file('')) for n in
                                     ('numpy', 'scipy', 'scikit-learn', 'threadpoolctl')},
               'effective_HGB_parameters': params, 'threads': 1,
               'planned_fits': (90 if ALIGNED_NATIVE in data else 70), 'completed_fits': 0,
               'model_API_calls': 0, 'corpus_gold_ledger_checkpoint_inputs': False, 'search_or_retry': False}
    write_json(out / 'RUNTIME.json', runtime)
    all_preds = {}
    fitted = [(name, d, d['methods']) for name, d in data.items()]
    if ALIGNED_NATIVE not in data:
        fitted.append(('deepseek_native_origin', data[COHORTS[1]], native['methods']))
    with threadpool_limits(limits=1):
        runtime['threadpools_during_fit'] = threadpool_info()
        assert all(p['num_threads'] == 1 for p in runtime['threadpools_during_fit'])
        for name, d, methods in fitted:
            preds = {k: np.full(len(d['y']), np.nan) for k in methods}
            matrix_hashes = {k: __import__('hashlib').sha256(x.tobytes()).hexdigest() for k, x in methods.items()}
            for key in methods:
                for k in range(5):
                    train, test = d['outer_fold'] != k, d['outer_fold'] == k
                    assert not set(d['groups'][train]) & set(d['groups'][test])
                    model = HistGradientBoostingClassifier(**params)
                    model.fit(methods[key][train], d['y'][train])
                    preds[key][test] = model.predict_proba(methods[key][test])[:, 1]
                    runtime['completed_fits'] += 1
                    write_json(out / 'RUNTIME.json', runtime)
                print(f'{name}/{key}: five fixed fits complete', flush=True)
            assert all(np.isfinite(p).all() for p in preds.values())
            assert all(__import__('hashlib').sha256(methods[k].tobytes()).hexdigest() == h for k, h in matrix_hashes.items())
            all_preds[name] = preds
            # Keep every fitted prediction even if later report generation fails.
            checkpoint = out / 'fit_checkpoints'
            checkpoint.mkdir(exist_ok=True)
            np.savez_compressed(checkpoint / (name + '.npz'),
                                **{k: d[k] for k in ('item_ids', 'groups', 'y', 'outer_fold')}, **preds)
    assert runtime['completed_fits'] == runtime['planned_fits']
    if ALIGNED_NATIVE in data:
        all_preds['deepseek_native_origin'] = {
            'native_G_curve': all_preds[ALIGNED_NATIVE]['full_curve'].copy(),
            'native_G_raw': all_preds[ALIGNED_NATIVE]['raw_three_world'].copy()}
        fitted.append(('deepseek_native_origin', data[COHORTS[1]], {}))
    # The two already fitted shared variants are reused; native comparison needs only ten new fits.
    all_preds['deepseek_native_origin']['shared_G_curve'] = all_preds[COHORTS[1]]['full_curve'].copy()
    all_preds['deepseek_native_origin']['shared_G_raw'] = all_preds[COHORTS[1]]['raw_three_world'].copy()
    summary = {}
    for name, d, _ in fitted:
        dst = out / name
        dst.mkdir()
        preds = all_preds[name]
        np.savez_compressed(dst / 'OOF.npz', **{k: d[k] for k in ('item_ids', 'groups', 'y', 'outer_fold')}, **preds)
        ref = native['reference'] if name == 'deepseek_native_origin' else d['reference']
        comparison = compare_predictions(dst, d['item_ids'], d['groups'], d['outer_fold'], preds, ref)
        contrasts = spec['contrasts'] if name != 'deepseek_native_origin' else {
            'native_curve_minus_raw': ('native_G_curve', 'native_G_raw'),
            'shared_curve_minus_raw': ('shared_G_curve', 'shared_G_raw'),
            'native_minus_shared_curve': ('native_G_curve', 'shared_G_curve'),
            'native_minus_shared_raw': ('native_G_raw', 'shared_G_raw')}
        ev = evaluate(d['y'], d['groups'], preds, contrasts)
        comparison['saved_evaluation'] = compare_evaluation(ev, reference_evaluation(name, root))
        write_json(dst / 'COMPARISON.json', comparison)
        report = {'status': 'fixed post-hoc development benchmark, not independent confirmation',
                  'support': support(d['y'], d['groups'], len(d['y'])), 'fold_support': fold_support(d),
                  'evaluation': ev, 'comparison': comparison}
        write_json(dst / 'METRICS.json', report)
        summary[name] = report
        print(f'{name}: predictions exact={comparison["all_predictions_exact"]}; saved metrics/CI exact={comparison["saved_evaluation"]["all_saved_points_and_intervals_exact"]}', flush=True)
    assert all(sha256(root / p) == h for p, h in before.items())
    write_json(out / 'INPUT_HASHES.json', before)
    write_json(out / 'RESULTS.json', summary)
    runtime['finished_utc'] = datetime.now(timezone.utc).isoformat()
    runtime['numeric_inputs_unchanged'] = True
    write_json(out / 'RUNTIME.json', runtime)
    render(summary, out / 'tables')
    files = sorted(p for p in out.rglob('*') if p.is_file())
    (out / 'SHA256SUMS.txt').write_text(''.join(f'{sha256(p)}  {p.relative_to(out)}\n' for p in files))
    print(f'Fixed release retrain complete: {runtime["completed_fits"]} fits; differences preserved without tuning.', flush=True)


def render(summary, out):
    out.mkdir(parents=True, exist_ok=False)
    with (out / 'primary_and_components.csv').open('x', newline='') as f:
        fields = ['cohort', 'method', 'n', 'groups', 'error_1', 'correct_0', 'auroc', 'auprc',
                  'auroc_ci95_low', 'auroc_ci95_high', 'auprc_ci95_low', 'auprc_ci95_high']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, result in summary.items():
            for method, m in result['evaluation']['metrics'].items():
                s = result['support']
                w.writerow({'cohort': name, 'method': method, **{k: s[k] for k in fields[2:6]},
                            'auroc': m['auroc'], 'auprc': m['auprc'],
                            'auroc_ci95_low': m['auroc_ci95'][0], 'auroc_ci95_high': m['auroc_ci95'][1],
                            'auprc_ci95_low': m['auprc_ci95'][0], 'auprc_ci95_high': m['auprc_ci95'][1]})
    lines = ['% Generated from saved fixed OOF; no manually entered estimates.',
             '\\begin{tabular}{llrr}', '\\hline', 'Cohort & Method & AUROC & AP \\\\', '\\hline']
    for name, result in summary.items():
        for method, m in result['evaluation']['metrics'].items():
            lines.append(name.replace('_', '\\_') + ' & ' + method.replace('_', '\\_') +
                         f' & {m["auroc"]:.4f} & {m["auprc"]:.4f} ' + '\\\\')
    lines += ['\\hline', '\\end{tabular}']
    (out / 'primary_and_components.tex').write_text('\n'.join(lines) + '\n')
    write_json(out / 'paired_contrasts.json', {name: r['evaluation']['contrasts'] for name, r in summary.items()})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    sub = p.add_subparsers(dest='command', required=True)
    v = sub.add_parser('validate'); v.add_argument('--report', type=Path)
    r = sub.add_parser('retrain'); r.add_argument('--outdir', type=Path, required=True)
    t = sub.add_parser('tables'); t.add_argument('--results', type=Path, required=True); t.add_argument('--outdir', type=Path, required=True)
    args = p.parse_args(); root = args.root.resolve()
    if args.command == 'validate':
        _, _, receipt = validation(root)
        if args.report:
            assert not args.report.exists(), 'Refusing to overwrite report'; write_json(args.report, receipt)
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    elif args.command == 'retrain': retrain(root, args.outdir.resolve())
    else: render(json.loads(args.results.read_text()), args.outdir.resolve())


if __name__ == '__main__':
    main()
