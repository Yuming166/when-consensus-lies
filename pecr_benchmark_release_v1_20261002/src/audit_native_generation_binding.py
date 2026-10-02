#!/usr/bin/env python3
"""Audit saved target-native DeepSeek binding; no gold access, API or fit."""
import argparse, copy, csv, hashlib, json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
OLD_NATIVE = BASE / 'pecr_oof_sensitivity_native_g_v1_20261002/results/native_g'
WORLDS = ('original', 'positive', 'negative')
METHODS = ('graph_only', 'raw_three_world', 'full_curve',
           'no_input_normalization', 'no_curvature_asymmetry', 'no_direction_information')

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def relative(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return '../' + str(p.relative_to(BASE))

def readj(p):
    return json.loads(Path(p).read_text())

def readjl(p):
    return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]

def readcsv(p):
    with Path(p).open(newline='') as f:
        return list(csv.DictReader(f))

def writej(p, obj):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        f.write('\n')

def idhash(ids):
    return hashlib.sha256(''.join(str(i) + '\n' for i in ids).encode()).hexdigest()

def flatten(r):
    out = {k: v for k, v in r.items() if k not in ('worlds', 'G96_origin', 'construction_flags')}
    out['construction_flags_json'] = json.dumps(r['construction_flags'], ensure_ascii=False, sort_keys=True)
    for k, v in r['G96_origin'].items():
        out['G96_' + k] = v
    for w in WORLDS:
        for k, v in r['worlds'][w].items():
            out[w + '_' + k] = v
    return out

def writecoverage(path, rows):
    with path.with_suffix('.jsonl').open('x', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n')
    flattened = [flatten(r) for r in rows]
    keys = list(dict.fromkeys(k for r in flattened for k in r))
    with path.with_suffix('.csv').open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator='\n')
        w.writeheader()
        w.writerows(flattened)

def summarize(rows):
    result = {}
    for name in dict.fromkeys(r['cohort'] for r in rows):
        rr = [r for r in rows if r['cohort'] == name]
        ss = [r for r in rr if r['strict_member']]
        result[name] = {
            'frame_rows': len(rr), 'frame_groups': len({r['source_group'] for r in rr}),
            'requested_rows': sum(r['requested'] for r in rr),
            'unrequested_rows': sum(not r['requested'] for r in rr),
            'strict_rows': len(ss), 'strict_groups': len({r['source_group'] for r in ss}),
            'strict_error': sum(r['error'] == 1 for r in ss),
            'strict_correct': sum(r['error'] == 0 for r in ss),
            'requested_not_strict': sum(r['requested'] and not r['strict_member'] for r in rr),
            'mutually_exclusive_partitions': dict(Counter(r['partition'] for r in rr)),
            'strict_unit_combinations': dict(Counter(r['unit_combination_from_saved_fields'] for r in ss)),
            'G96_computation_status': dict(Counter(r['G96_origin'].get('computation_status', 'inherited_saved') for r in rr)),
            'offline_parser_status': {w: dict(Counter(r['worlds'][w]['offline_parser_status'] for r in rr)) for w in WORLDS},
        }
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--oof', required=True, type=Path, help='completed six-method saved OOF')
    parser.add_argument('--metrics', type=Path)
    parser.add_argument('--completion-source', type=Path, action='append', default=[])
    args = parser.parse_args()
    outputs = [
        'audit/native_generation_binding_audit.json',
        'coverage/native_attempted_frame.jsonl', 'coverage/native_attempted_frame.csv',
        'coverage/attempted_frame_final.jsonl', 'coverage/attempted_frame_final.csv',
        'coverage/FINAL_SUMMARY.json', 'coverage/FINAL_SUMMARY.csv',
        'coverage/FINAL_ID_HASHES.json', 'coverage/FINAL_COVERAGE.md',
        'reports/NATIVE_GENERATION_BINDING.md']
    assert all(not (ROOT / x).exists() for x in outputs), 'refuse_existing_completion_audit'
    paths = [ROOT / 'audit/generation_binding_audit.json', ROOT / 'coverage/attempted_frame.jsonl',
             ROOT / 'protocol/RELEASE_SPEC.json', ROOT / 'protocol/METHODS.json',
             ROOT / 'protocol/HGB_PARAMS.json', Path(__file__), args.oof,
             OLD_NATIVE / 'G96_NATIVE.npz', OLD_NATIVE / 'OOF.npz',
             OLD_NATIVE / 'NATIVE_G_AUDIT.json', OLD_NATIVE / 'FEATURE_STATUS.jsonl',
             OLD_NATIVE / 'SOURCE_HASHES.json', OLD_NATIVE / 'native_features_label_blind.jsonl']
    if args.metrics:
        paths.append(args.metrics)
    paths.extend(args.completion_source)
    qcohort = ROOT / 'cohorts/qwen_generation_aligned'
    paths.extend(qcohort / n for n in ['features_label_blind.jsonl', 'manifest.jsonl', 'labels.csv', 'folds.csv', 'fold_provenance.json', 'schema.json'])
    cohort = ROOT / 'cohorts/deepseek_generation_aligned'
    shared = ROOT / 'cohorts/deepseek_shared_qwen'
    for p in (cohort, shared):
        paths.extend(p / n for n in ['features_label_blind.jsonl', 'manifest.jsonl', 'labels.csv',
                                    'folds.csv', 'fold_provenance.json', 'schema.json'])
    before = {relative(p): sha(p) for p in paths}
    previous = readj(ROOT / 'audit/generation_binding_audit.json')
    assert previous['deepseek_label_original_curve_same_generation']
    assert not previous['deepseek_primary_G_target_native']
    previous_hashes = {r['path_relative_to_release']: r['sha256'] for r in previous['sources']}
    for n in ['features_label_blind.jsonl', 'manifest.jsonl', 'labels.csv', 'folds.csv', 'fold_provenance.json']:
        original = '../pecr_qwen_generation_aligned_correction_v1_20261002/data/strict/' + n
        assert sha(qcohort / n) == previous_hashes[original], ('changed_portable_qwen', n)
    oldrows = readjl(ROOT / 'coverage/attempted_frame.jsonl')
    assert len(oldrows) == 4482
    dsfull = [r for r in oldrows if r['cohort'] == 'deepseek_shared_qwen']
    features = readjl(cohort / 'features_label_blind.jsonl')
    oldfeatures = readjl(shared / 'features_label_blind.jsonl')
    assert len(features) == len(oldfeatures) == 2050
    ids = [r['item_id'] for r in features]
    groups = np.array([r['source_group'] for r in features])
    native = np.load(OLD_NATIVE / 'G96_NATIVE.npz', allow_pickle=False)
    oldoof = np.load(OLD_NATIVE / 'OOF.npz', allow_pickle=False)
    oof = np.load(args.oof, allow_pickle=False)
    assert np.array_equal(native['item_ids'], ids)
    assert np.array_equal(native['groups'], groups)
    original_native_json = readjl(OLD_NATIVE / 'native_features_label_blind.jsonl')
    assert [r['item_id'] for r in original_native_json] == ids
    for i, (r, old, ng) in enumerate(zip(features, oldfeatures, original_native_json)):
        assert r['row_index'] == old['row_index'] == ng['row_index'] == i
        assert r['item_id'] == old['item_id'] == ng['item_id']
        assert r['source_group'] == old['source_group'] == ng['source_group']
        assert np.array_equal(r['G96'], native['G96_native'][i])
        assert np.array_equal(r['G96'], ng['G96'])
        for k in ['raw17', 'Curve33', 'responses', 'direction']:
            assert r[k] == old[k], ('changed_world_feature', i, k)
        assert len(r['G96']) == 96 and len(r['raw17']) == 17 and len(r['Curve33']) == 33
        assert np.isfinite(r['G96']).all() and np.isfinite(r['raw17']).all() and np.isfinite(r['Curve33']).all()
    # Every original manifest, label and fold byte is preserved; no target-dependent selection.
    for n in ['manifest.jsonl', 'labels.csv', 'folds.csv', 'fold_provenance.json']:
        assert sha(cohort / n) == sha(shared / n), ('changed_support', n)
    labels = readcsv(cohort / 'labels.csv')
    folds = readcsv(cohort / 'folds.csv')
    y = np.array([int(r['error']) for r in labels])
    outer = np.array([int(r['outer_fold']) for r in folds])
    assert np.array_equal(oof['y'], y)
    assert np.array_equal(oof['groups'], groups)
    if 'item_ids' in oof.files:
        assert np.array_equal(oof['item_ids'], ids)
    if 'outer_fold' in oof.files:
        assert np.array_equal(oof['outer_fold'], outer)
    assert np.array_equal(oldoof['item_ids'], ids)
    assert np.array_equal(oldoof['outer_fold'], outer)
    assert np.array_equal(oldoof['y'], y)
    assert np.array_equal(oof['full_curve'], oldoof['native_G_curve'])
    assert np.array_equal(oof['raw_three_world'], oldoof['native_G_raw'])
    for m in METHODS:
        assert m in oof.files
        assert oof[m].shape == (2050,) and np.isfinite(oof[m]).all()
        assert ((oof[m] >= 0) & (oof[m] <= 1)).all()
    for g in set(groups):
        assert len(set(outer[groups == g])) == 1
    assert len(set(ids)) == 2050 and len(set(groups)) == 448 and set(outer) == set(range(5))
    origin = readj(OLD_NATIVE / 'NATIVE_G_AUDIT.json')
    assert origin['native_safe_valid_rows'] == 2050 and origin['native_fallback_rows'] == 0
    assert origin['G96_response_fields_consumed'] == ['answer_value', 'unit', 'confidence']
    assert origin['supporting_evidence_validated_but_unused_by_G96']
    assert not origin['native_uses_positive_negative_responses']
    assert not origin['native_uses_labels_gold_predictions_reasoning']
    native_source = readj(OLD_NATIVE / 'SOURCE_HASHES.json')
    ledger = [r for r in native_source['files'] if r['path_relative_to_analysis'].endswith(
        'pecr_crossmodel_deepseek_v2_complete_20261001/data/merged_ledger_v2.jsonl')]
    prior_ledger = [r for r in previous['sources'] if r['path_relative_to_release'].endswith(
        'pecr_crossmodel_deepseek_v2_complete_20261001/data/merged_ledger_v2.jsonl')]
    assert len(ledger) == len(prior_ledger) == 1 and ledger[0]['sha256'] == prior_ledger[0]['sha256']
    strict = set(ids)
    nativefull = copy.deepcopy(dsfull)
    for r in nativefull:
        r['cohort'] = 'deepseek_generation_aligned'
        computed = r['item_id'] in strict
        r['G96_origin'] = {
            'kind': 'target_DeepSeek_original', 'model': 'deepseek-flash',
            'same_generation_as_label_and_curve': True if computed else None,
            'source_generation': 'same_DeepSeek_V2_three_world_original' if computed else 'not_computed',
            'answer_field_sha256': r['original_label_target_answer_sha256'] if computed else None,
            'saved_fallback': False if computed else None,
            'G96_available': computed,
            'computation_status': 'computed_saved_target_native' if computed else 'not_computed',
            'source_native_G96_file_sha256': before[relative(OLD_NATIVE / 'G96_NATIVE.npz')] if computed else None,
            'source_native_G96_row_index': ids.index(r['item_id']) if computed else None,
            'response_binding_basis': 'existing_native_builder_recipe_and_source_ledger_SHA; new_per_item_original_field_hash' if computed else 'not_computed',
        }
        r['binding_added_posthoc'] = True
    # Preserve old snapshot and distinguish unknown state from upstream exclusion eligibility.
    completed = copy.deepcopy(oldrows) + nativefull
    unknown_normalized = 0
    for r in completed:
        for w in WORLDS:
            state = r['worlds'][w]
            if not r['requested']:
                state['upstream_offline_parser_eligibility_flag'] = state['offline_parser_valid']
                state['offline_parser_valid'] = None
                unknown_normalized += 1
    assert len(completed) == 6723
    assert len({(r['cohort'], r['item_id']) for r in completed}) == 6723
    assert len(nativefull) == 2241
    summary = summarize(completed)
    assert summary['deepseek_generation_aligned']['G96_computation_status'] == {
        'computed_saved_target_native': 2050, 'not_computed': 191}
    assert summary['deepseek_generation_aligned']['mutually_exclusive_partitions'] == {
        'strict_parsed_labeled': 2050, 'valid_unknown_label': 54,
        'invalid_known_label': 79, 'invalid_unknown_label': 42,
        'unrequested_construction_exclusion': 16}
    after = {relative(p): sha(p) for p in paths}
    if before != after:
        failure = ROOT / 'audit/native_binding_unstable_source_failure.json'
        if not failure.exists():
            writej(failure, {'status': 'REJECTED_UNSTABLE_SOURCE', 'sources_changed': {k: {'before': before[k], 'after': after[k]} for k in before if before[k] != after[k]}, 'outputs_written': False, 'training_fits': 0, 'TRAIN_gold_holdout_access': False})
        raise AssertionError('sources_changed_during_native_audit')
    audit = {
        'status': 'PASS_NATIVE_SAME_GENERATION_SAVED_SOURCE_BINDING_SIX_METHODS',
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'cohort': 'deepseek_generation_aligned',
        'strict_rows': 2050, 'strict_groups': 448, 'folds': 5,
        'labels_error_correct': {'error': int(y.sum()), 'correct': int((y == 0).sum())},
        'all_six_saved_methods_available': {m: True for m in METHODS},
        'same_native_G96_elementwise_saved_NPZ_JSONL': True,
        'label_raw_curve_manifest_folds_preserved_from_same_DeepSeek_V2_queue': True,
        'native_full_and_raw_exact_existing_native_saved_OOF': True,
        'group_disjoint_folds': True, 'finite_dimensions_G96_raw17_Curve33': True,
        'target_original_answer_hash_bound_per_item_posthoc': True,
        'native_outside_strict_G96_not_computed': 191,
        'same_generation_G_label_curve_supported_by_existing_builder_source_recipe': True,
        'historical_label_receipt_contains_prediction_file_digest_or_per_item_target_hash': False,
        'historical_label_correctness_independently_rechecked': False,
        'private_corpus_feature_values_reconstructed_in_this_audit': False,
        'TRAIN_gold_holdout_access': False, 'model_API_calls': 0, 'training_fits': 0,
        'as_before_shared_audit_retained': True,
        'completed_unknown_parser_states_normalized': unknown_normalized,
        'normalization_note': 'Only unrequested eligibility flags become null parser validity; original snapshot retained, no recorded status becomes success.',
        'sources': [{'path_relative_to_release': p, 'sha256': h} for p, h in before.items()],
        'sources_unchanged': True,
        'native_builder_declared_source_receipt': native_source,
        'coverage_summary': summary,
    }
    for name in outputs:
        (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
    writej(ROOT / outputs[0], audit)
    writecoverage(ROOT / 'coverage/native_attempted_frame', nativefull)
    writecoverage(ROOT / 'coverage/attempted_frame_final', completed)
    writej(ROOT / 'coverage/FINAL_SUMMARY.json', {
        'cohorts': summary, 'TRAIN_gold_holdout_access': False,
        'model_API_calls': 0, 'training_fits': 0,
        'native_six_methods_available_after_fixed_supplement': True,
        'as_before_coverage_retained': True})
    with (ROOT / 'coverage/FINAL_SUMMARY.csv').open('x', newline='') as f:
        keys = ['cohort', 'frame_rows', 'frame_groups', 'requested_rows', 'unrequested_rows',
                'strict_rows', 'strict_groups', 'strict_error', 'strict_correct', 'requested_not_strict']
        writer = csv.DictWriter(f, fieldnames=keys, lineterminator='\n')
        writer.writeheader()
        writer.writerows({'cohort': n, **{k: v[k] for k in keys[1:]}} for n, v in summary.items())
    hashes = {'hash_contract': 'SHA256 UTF8 one item_id per line final newline; original row order', 'cohorts': {}}
    for name in summary:
        rr = [r for r in completed if r['cohort'] == name]
        sid = ids if name == 'deepseek_generation_aligned' else [
            r['item_id'] for r in readjl(ROOT / 'cohorts' / name / 'features_label_blind.jsonl')]
        hashes['cohorts'][name] = {'frame': idhash([r['item_id'] for r in rr]),
            'requested': idhash([r['item_id'] for r in rr if r['requested']]),
            'strict_training_order': idhash(sid)}
    writej(ROOT / 'coverage/FINAL_ID_HASHES.json', hashes)
    table = '| Cohort | Frame | Requested | Strict | Groups | Error / correct | Requested outside strict |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for name, s in summary.items():
        table += '| {} | {} | {} | {} | {} | {} / {} | {} |\n'.format(
            name, s['frame_rows'], s['requested_rows'], s['strict_rows'], s['strict_groups'],
            s['strict_error'], s['strict_correct'], s['requested_not_strict'])
    coverage = '# Completed coverage with target-native DeepSeek track\n\n' + table + '\n'
    coverage += 'Each cohort has 2,241 rows, including 2,225 requested and 16 unrequested construction exclusions. '
    coverage += 'DeepSeek target-native strict support is unchanged: 2,050 rows / 448 groups; 175 requested exclusions are 54 valid unknown-label, 79 invalid known-label and 42 invalid unknown-label rows. '
    coverage += 'Native G96 exists only for those 2,050 strict rows. All 191 other rows explicitly say not_computed; shared Qwen G is never substituted.\n\n'
    coverage += 'attempted_frame_final.jsonl / .csv is the final three-cohort coverage view; the original two-cohort attempted_frame exports remain the as-before audit. '
    coverage += 'Unrequested offline_parser_valid is null in the completed view. The upstream exclusion eligibility flag is preserved separately; recorded statuses remain unknown.\n\n'
    coverage += 'All six native methods are now available as saved post-hoc fixed-method results. The old report stating four methods missing describes availability before the authorized supplement and is retained.\n'
    (ROOT / 'coverage/FINAL_COVERAGE.md').write_text(coverage)
    report = '# Target-native generation binding completion\n\n'
    report += 'PASS for the saved target-native DeepSeek numeric/source binding and six-method support. This audit made no TRAIN/gold/holdout access, model/API call or fit.\n\n'
    report += 'The target-native cohort retains exactly the 2,050 IDs / 448 groups, labels, three-world numeric responses, Raw17, Curve33, manifests and five folds from the existing DeepSeek V2 strict queue. Only G96 changes; every element equals both the existing native NPZ and native JSONL at the original row index. Full Curve and Raw OOF remain exactly equal to their existing native counterparts. All six saved methods have finite length-2,050 predictions on the same support.\n\n'
    report += 'Native G96 uses the same DeepSeek original answer_value, unit and confidence as the label/curve generation. Supporting evidence is validated but unused by G96. The saved native source receipt identifies the identical merged-ledger digest used by the earlier binding audit. New per-item original answer field hashes expose this binding without exporting ledger content. No default answer, shared Qwen G, positive/negative response or label enters native G96.\n\n'
    report += 'The historical DeepSeek label receipt records the label-file hash and original-world source recipe, but contains no contemporaneous merged-ledger digest or per-item response hash. The new per-item binding is post-hoc; this release does not independently recheck numeric-gold correctness, reconstruct private corpus feature values, or invent a freeze time. The historical generator selected 2,241 dev_train IDs; this is a recorded legacy scope, not new gold access in this release.\n\n'
    report += 'All 2,241 attempted rows remain visible. G96 is not_computed on the 175 requested excluded rows and 16 unrequested rows. The shared-Qwen track and its original audit remain a historical source comparison; their source-binding PASS does not satisfy the same-generation feature requirement by itself.\n\n'
    report += 'The four newly completed native methods are the already fixed graph baseline and three existing ablations. Completion is post-hoc provenance correction on a fixed queue, not independent model validation, method search or an acceptance/ARR-score guarantee.\n\n'
    report += 'Paths and inspected hashes are in audit/native_generation_binding_audit.json. The final coverage entry is coverage/attempted_frame_final.jsonl; CSV, summary and ordered-ID hashes accompany it. No raw ledger, financial body, model reasoning, credentials or checkpoint is exported.\n'
    (ROOT / 'reports/NATIVE_GENERATION_BINDING.md').write_text(report)
    print(json.dumps({'status': audit['status'], 'native_rows': 2050, 'native_groups': 448,
                      'full_coverage_rows': len(completed), 'new_fits_in_this_audit': 0}))

if __name__ == '__main__':
    main()

