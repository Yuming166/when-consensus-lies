#!/usr/bin/env python3
"""Complete four fixed native-G controls; reuse the two saved native OOF methods."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_info, threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluation import B, SEED, evaluate, support
from numeric import ROOT, load_cohort, matrices, sha256

METHODS = ('graph_only', 'raw_three_world', 'full_curve', 'no_input_normalization',
           'no_curvature_asymmetry', 'no_direction_information')
NEW = ('graph_only', 'no_input_normalization', 'no_curvature_asymmetry', 'no_direction_information')
EXISTING = {'raw_three_world': 'native_G_raw', 'full_curve': 'native_G_curve'}
CONTRASTS = {'full_minus_raw': ('full_curve', 'raw_three_world'),
             'full_minus_graph': ('full_curve', 'graph_only'),
             'full_minus_no_input_normalization': ('full_curve', 'no_input_normalization'),
             'full_minus_no_curvature_asymmetry': ('full_curve', 'no_curvature_asymmetry'),
             'full_minus_no_direction_information': ('full_curve', 'no_direction_information')}


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def array_hash(a):
    a = np.ascontiguousarray(a)
    meta = json.dumps({'shape': list(a.shape), 'dtype': a.dtype.str}, sort_keys=True)
    return hashlib.sha256(meta.encode() + b'\n' + a.tobytes(order='C')).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--outdir', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.outdir.resolve()
    assert not out.exists(), 'Native completion output must be a new directory'
    assert not any(out.is_relative_to(root / p) for p in ('cohorts', 'src', 'protocol', 'coverage'))
    assert out != root / 'reference/native', 'Preserve existing four-variant reference'
    assert B == 2000 and SEED == 20260928
    source_paths = [root / 'protocol/HGB_PARAMS.json', root / 'src/evaluation.py',
                    root / 'reference/native/G96_NATIVE.npz', root / 'reference/native/G96_SCHEMA.json',
                    root / 'reference/native/OOF.npz', root / 'reference/native/RUNTIME.json']
    source_paths += [p for p in (root / 'cohorts/deepseek_shared_qwen').iterdir() if p.is_file()]
    source_paths += [root / 'reference/deepseek/OOF.npz']
    before = {str(p.relative_to(root)): sha256(p) for p in source_paths}
    code_before = {str(p.relative_to(root)): sha256(p) for p in (Path(__file__).resolve(), root / 'src/numeric.py')}
    shared = load_cohort('deepseek_shared_qwen', root)
    assert len(shared['y']) == 2050 and len(set(shared['groups'])) == 448
    assert int(shared['y'].sum()) == 1257 and int((shared['y'] == 0).sum()) == 793
    with np.load(root / 'reference/native/G96_NATIVE.npz', allow_pickle=False) as saved:
        assert np.array_equal(saved['item_ids'], shared['item_ids'])
        assert np.array_equal(saved['groups'], shared['groups'])
        G = np.array(saved['G96_native'], dtype=np.float64, copy=True)
    native_schema = json.loads((root / 'reference/native/G96_SCHEMA.json').read_text())
    assert native_schema['dim'] == 96
    assert native_schema['feature_names'] == shared['schema']['G96']['feature_names']
    # The earlier native schema stores an explanatory identity string; the
    # portable shared schema stores indexed records. Verify their actual column
    # names/indices without rewriting either preserved schema.
    native_identity = native_schema['column_identity']
    expected_identity = [{'index': i, 'name': name} for i, name in enumerate(native_schema['feature_names'])]
    assert expected_identity == shared['schema']['G96']['column_identity']
    if isinstance(native_identity, list):
        assert native_identity == expected_identity
    else:
        assert isinstance(native_identity, str) and native_identity
    assert array_hash(G) == native_schema['native_matrix_sha256']
    Xs = matrices(G, shared['raw17'], shared['Curve33'], shared['schema'])
    assert set(Xs) == set(METHODS)
    matrix_before = {key: array_hash(value) for key, value in Xs.items()}
    with np.load(root / 'reference/native/OOF.npz', allow_pickle=False) as saved:
        assert all(np.array_equal(saved[key], shared[key]) for key in ('item_ids', 'groups', 'y', 'outer_fold'))
        predictions = {new_key: np.array(saved[old_key], copy=True) for new_key, old_key in EXISTING.items()}
    assert all(p.shape == (2050,) and np.isfinite(p).all() for p in predictions.values())
    params = json.loads((root / 'protocol/HGB_PARAMS.json').read_text())['parameters']
    assert len(params) == 21 and HistGradientBoostingClassifier(**params).get_params() == params
    assert params['random_state'] == 20260928 and params['max_iter'] == 250
    assert params['max_leaf_nodes'] == 15 and params['learning_rate'] == .05 and params['l2_regularization'] == 1.
    status = {key: {'status': 'existing_saved_native_oof_reused', 'source_field': source,
                    'new_fits': 0, 'source_relative': '../native/OOF.npz'} for key, source in EXISTING.items()}
    status.update({key: {'status': 'new_post_hoc_fixed_suite_completion', 'new_fits': 5,
                         'not_a_recovered_historical_reference': True} for key in NEW})
    out.mkdir(parents=True, exist_ok=False)
    runtime = {'started_utc': datetime.now(timezone.utc).isoformat(),
               'status': 'post-hoc fixed native suite completion; four new references, two existing references',
               'python': sys.version, 'prefix': sys.prefix, 'base_prefix': sys.base_prefix,
               'platform': platform.platform(),
               'versions': {name: importlib.metadata.version(name) for name in
                            ('numpy', 'scipy', 'scikit-learn', 'threadpoolctl', 'joblib', 'narwhals', 'cloudpickle')},
               'HGB_effective_parameters': params, 'threads': 1, 'planned_fits': 20, 'completed_fits': 0,
               'reused_existing_methods': list(EXISTING), 'new_methods': list(NEW),
               'model_API_calls': 0, 'gold_ledger_holdout_checkpoint_inputs': False,
               'seed_parameter_sample_search': False, 'existing_reference_modified': False,
               'method_status': status, 'loaded_code_hashes_before': code_before,
               'native_schema_column_identity_representation': type(native_identity).__name__,
               'native_column_order_verified_against_explicit_shared_indexed_names': True,
               'pre_fit_launch_correction': {'fits_before_correction': 0,
                   'reason': 'Existing native schema identity is an explanatory string, not an indexed list; exact feature-name order and derived indexed identities were verified.'}}
    write_json(out / 'RUNTIME.json', runtime)
    y, folds, groups = shared['y'], shared['outer_fold'], shared['groups']
    with threadpool_limits(limits=1):
        runtime['threadpools_during_fit'] = threadpool_info()
        assert all(info['num_threads'] == 1 for info in runtime['threadpools_during_fit'])
        for key in NEW:
            prediction = np.full(2050, np.nan)
            for fold in range(5):
                train, test = folds != fold, folds == fold
                assert not set(groups[train]) & set(groups[test])
                model = HistGradientBoostingClassifier(**params)
                model.fit(Xs[key][train], y[train])
                prediction[test] = model.predict_proba(Xs[key][test])[:, 1]
                runtime['completed_fits'] += 1
                write_json(out / 'RUNTIME.json', runtime)
            assert np.isfinite(prediction).all()
            predictions[key] = prediction
            # Commit each completed method to a new checkpoint file before evaluation/export.
            np.savez_compressed(out / f'CHECKPOINT_{key}.npz', item_ids=shared['item_ids'], groups=groups,
                                y=y, outer_fold=folds, prediction=prediction)
            print(f'Native suite completion: {key} five fixed fits complete', flush=True)
    assert runtime['completed_fits'] == 20
    assert all(array_hash(Xs[key]) == value for key, value in matrix_before.items())
    ordered = {key: predictions[key] for key in METHODS}
    np.savez_compressed(out / 'OOF.npz', item_ids=shared['item_ids'], groups=groups, y=y, outer_fold=folds, **ordered)
    with (out / 'OOF.csv').open('x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row_index', 'item_id', 'source_group', 'outer_fold', 'error', *METHODS])
        for i in range(2050):
            writer.writerow([i, shared['item_ids'][i], groups[i], int(folds[i]), int(y[i]), *[float(ordered[k][i]) for k in METHODS]])
    evaluation = evaluate(y, groups, ordered, CONTRASTS)
    fold_support = []
    for k in range(5):
        mask = folds == k
        fold_support.append({'outer_fold': k, **support(y[mask], groups[mask], 2050)})
    write_json(out / 'METRICS.json', {'status': runtime['status'], 'support': support(y, groups, 2050),
                                   'fold_support': fold_support, 'evaluation': evaluation,
                                   'method_status': status, 'new_fits': 20, 'reused_predictions': 2,
                                   'primary_reference_old_files_modified': False,
                                   'new_controls_are_post_hoc_not_recovered_history': True})
    source_after = {path: sha256(root / path) for path in before}
    assert source_after == before
    code_after = {path: sha256(root / path) for path in code_before}
    runtime.update({'finished_utc': datetime.now(timezone.utc).isoformat(), 'source_inputs_unchanged': True,
                    'training_matrices_unchanged': True, 'loaded_code_hashes_after': code_after,
                    'numeric_module_file_changed_by_parallel_packaging': code_after['src/numeric.py'] != code_before['src/numeric.py'],
                    'loaded_functions_not_reloaded_during_fitting': True})
    assert code_after['src/freeze_native_suite.py'] == code_before['src/freeze_native_suite.py']
    write_json(out / 'RUNTIME.json', runtime)
    write_json(out / 'SOURCE_HASHES.json', {'paths_relative_to_release_root': before, 'after': source_after,
                                        'all_numeric_parameter_evaluation_sources_unchanged': True,
                                        'training_matrix_hashes': matrix_before, 'loaded_code_hashes_before': code_before,
                                        'loaded_code_hashes_after': code_after})
    write_json(out / 'VALIDATION.json', {'all_passed': True, 'rows': 2050, 'groups': 448, 'folds': 5,
                                      'new_fit_count': 20, 'existing_native_predictions_refitted': False,
                                      'ids_y_groups_folds_same_saved_order': True,
                                      'G96_schema_order_and_saved_matrix_hash_verified': True,
                                      'matrices_finite_nonsharing_and_unchanged': True,
                                      'numeric_sources_unchanged': True,
                                      'bootstrap_valid_draws': evaluation['bootstrap']['valid_draws'],
                                      'bootstrap_degenerate_draws': evaluation['bootstrap']['degenerate_single_class_draws']})
    md = ['# Fixed native-G suite completion', '',
          'This post-hoc completion creates four new fixed control references on the existing 2,050-row / 448-group DeepSeek queue. Native Raw and Full predictions are copied from the existing source comparison; neither is refitted. This is not recovery of four historical references.', '',
          'Exactly 20 HGB fits: native Graph-only plus the three already fixed feature-family masks, five saved folds each. Complete 21 effective parameters and one-thread limits are unchanged. There is no seed, parameter, row, threshold or method search.', '',
          '| Native-G method | Status | AUROC | AUPRC |', '|---|---|---:|---:|']
    for key in METHODS:
        m = evaluation['metrics'][key]
        md.append(f"| {key} | {status[key]['status']} | {m['auroc']:.6f} | {m['auprc']:.6f} |")
    md += ['', '| Fixed contrast | Delta AUROC [95% CI] | Delta AUPRC [95% CI] |', '|---|---|---|']
    for key, c in evaluation['contrasts'].items():
        def fmt(metric):
            value, limits = c['delta_' + metric], c['delta_' + metric + '_ci95']
            return f'{value:.6f} [{limits[0]:.6f}, {limits[1]:.6f}]'
        md.append(f"| {key} | {fmt('auroc')} | {fmt('auprc')} |")
    md += ['', 'Intervals condition on saved OOF predictions and use 2,000 source-group paired percentile draws, seed 20260928. These post-hoc controls do not establish independent confirmation or necessity of every curve family.', '',
           'Numeric inputs, parameters and evaluation-source hashes are verified before/after fitting. Existing source references are preserved. Native schema and matrix hash, exact IDs/y/groups/folds, common support, finite/nonsharing matrices and per-method checkpoints are verified. No gold, ledger, holdout, checkpoint model or API is read.', '',
           'The completion itself is reference construction, not the later independent uniform release reproduction. The root agent will separately validate the newly frozen six-method reference in the final clean acceptance run.', '',
           'Run from a package with preserved inputs: `python src/freeze_native_suite.py --outdir reference/deepseek_aligned_new_version`; an existing output directory is refused.', '']
    (root / 'reports/NATIVE_SUITE_COMPLETION.md').write_text('\n'.join(md))
    files = sorted(p for p in out.iterdir() if p.is_file())
    (out / 'SHA256SUMS.txt').write_text(''.join(f'{sha256(p)}  {p.name}\n' for p in files))
    print('Native fixed suite complete: 20 fits, two saved OOF methods reused, sources unchanged.', flush=True)


if __name__ == '__main__':
    main()
