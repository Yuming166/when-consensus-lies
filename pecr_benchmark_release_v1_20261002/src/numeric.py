"""Portable label-blind numeric matrices; no corpus, ledger, gold or network."""
import csv
import hashlib
import json
from itertools import combinations
from pathlib import Path

import numpy as np
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
COHORTS = ('qwen_generation_aligned', 'deepseek_shared_qwen')
ALIGNED_NATIVE = 'deepseek_generation_aligned'
WORLD_ORDER = ('original', 'positive', 'negative')


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]


def curve33(row, manifest):
    """Frozen component arithmetic, including historical normalization."""
    o, p, n = (row['responses'][w] for w in WORLD_ORDER)
    direction = float(row['direction'])
    old, new = float(manifest['operand_old']), float(manifest['operand_new'])
    inp = new - old
    dp, dn = p['value'] - o['value'], o['value'] - n['value']
    den = abs(inp) + 1e-9
    sp, sn = dp / den, dn / den
    return np.array([
        dp, dn, abs(dp), abs(dn), dp * direction, dn * direction,
        float(dp * direction > 0), float(dn * direction > 0),
        float(dp == 0), float(dn == 0),
        min(abs(dp), abs(dn)) / (max(abs(dp), abs(dn)) + 1e-9),
        p['confidence'] - o['confidence'], n['confidence'] - o['confidence'],
        float(len({o['unit'], p['unit'], n['unit']}) <= 1),
        float(all(x['unit'] for x in (o, p, n))), float(direction == 1),
        float(manifest['absolute_delta']), inp / (abs(old) + 1e-9), inp,
        sp, sn, abs(sp), abs(sn), (sp - sn) / (abs(sp) + abs(sn) + 1e-9),
        (p['value'] + n['value'] - 2 * o['value']) / (abs(dp) + abs(dn) + 1e-9),
        sp - sn,
        float((dp * direction > 0) == (p['confidence'] >= o['confidence'])),
        float((dn * direction > 0) == (n['confidence'] >= o['confidence'])),
        float(abs(p['confidence'] - o['confidence']) < .05),
        float(abs(n['confidence'] - o['confidence']) < .05),
        float(abs(dp - dn) / (abs(dp) + abs(dn) + 1e-9)),
        float(np.sign(dp * direction) == np.sign(dn * direction)),
        float(abs(dp) > 1e-9 and abs(dn) > 1e-9),
    ], dtype=np.float64)


def matrices(G, raw, curve, schema):
    names = schema['Curve33']['feature_names']
    out = {'graph_only': G.copy(), 'raw_three_world': np.concatenate([G, raw], axis=1),
           'full_curve': np.concatenate([G, curve], axis=1)}
    for name, removed in schema['component_removed'].items():
        keep = [i for i, feature in enumerate(names) if feature not in removed]
        out[name] = np.concatenate([G, curve[:, keep]], axis=1)
    assert {k: x.shape[1] for k, x in out.items()} == {
        'graph_only': 96, 'raw_three_world': 113, 'full_curve': 129,
        'no_input_normalization': 124, 'no_curvature_asymmetry': 125,
        'no_direction_information': 121}
    arrays = [G, raw, curve, *out.values()]
    assert all(np.isfinite(x).all() and x.flags.writeable for x in arrays)
    assert all(not np.shares_memory(a, b) for a, b in combinations(arrays, 2))
    assert np.array_equal(raw, curve[:, :17])
    return out


def load_cohort(name, root=ROOT):
    assert name in (*COHORTS, ALIGNED_NATIVE)
    d = Path(root) / 'cohorts' / name
    schema = json.loads((d / 'schema.json').read_text())
    rows, manifest = (read_jsonl(d / f) for f in ('features_label_blind.jsonl', 'manifest.jsonl'))
    with (d / 'labels.csv').open() as f:
        labels = list(csv.DictReader(f))
    with (d / 'folds.csv').open() as f:
        folds = list(csv.DictReader(f))
    n = len(rows)
    assert n == len(manifest) == len(labels) == len(folds)
    ids = np.array([r['item_id'] for r in rows])
    assert n == len(set(ids))
    for i, records in enumerate(zip(rows, manifest, labels, folds)):
        assert all(int(r['row_index']) == i for r in records)
        assert all(r['item_id'] == ids[i] and r['source_group'] == rows[i]['source_group'] for r in records)
        assert rows[i]['id'] == ids[i] and set(rows[i]['responses']) == set(WORLD_ORDER)
        assert all(set(rows[i]['responses'][w]) == {'value', 'unit', 'confidence'} for w in WORLD_ORDER)
    for key, dim in [('G96', 96), ('raw17', 17), ('Curve33', 33)]:
        assert schema[key]['dim'] == dim and len(schema[key]['feature_names']) == dim
    assert schema['G96']['feature_names'][4] == schema['G96']['feature_names'][35] == 'answer_number_count'
    assert schema['G96']['column_identity'] == [
        {'index': i, 'name': s} for i, s in enumerate(schema['G96']['feature_names'])]
    G = np.array([r['G96'] for r in rows], dtype=np.float64, copy=True)
    raw = np.array([r['raw17'] for r in rows], dtype=np.float64, copy=True)
    curve = np.array([r['Curve33'] for r in rows], dtype=np.float64, copy=True)
    assert G.shape == (n, 96) and raw.shape == (n, 17) and curve.shape == (n, 33)
    assert np.array_equal(curve, np.array([curve33(r, m) for r, m in zip(rows, manifest)]))
    methods = matrices(G, raw, curve, schema)
    y = np.array([int(r['error']) for r in labels], dtype=np.int64)
    assert set(y.tolist()) == {0, 1}
    groups = np.array([r['source_group'] for r in rows])
    outer = np.array([int(r['outer_fold']) for r in folds], dtype=np.int64)
    assert set(outer.tolist()) == set(range(5))
    for group in set(groups):
        assert len(set(outer[groups == group])) == 1
    rebuilt = np.full(n, -1, dtype=np.int64)
    for k, (_, test) in enumerate(GroupKFold(5, shuffle=False).split(np.zeros((n, 1)), groups=groups)):
        rebuilt[test] = k
    assert np.array_equal(rebuilt, outer)
    refname = 'qwen' if name == COHORTS[0] else ('deepseek_aligned' if name == ALIGNED_NATIVE else 'deepseek')
    refpath = Path(root) / 'reference' / refname / 'OOF.npz'
    with np.load(refpath, allow_pickle=False) as f:
        reference = {k: f[k].copy() for k in f.files}
    assert all(np.array_equal(reference[k], a) for k, a in
               [('item_ids', ids), ('groups', groups), ('y', y), ('outer_fold', outer)])
    assert all(np.isfinite(reference[k]).all() and reference[k].shape == (n,) for k in methods)
    return {'item_ids': ids, 'groups': groups, 'y': y, 'outer_fold': outer,
            'G96': G, 'raw17': raw, 'Curve33': curve, 'methods': methods,
            'reference': reference, 'schema': schema, 'rows': rows}


def load_native(shared, root=ROOT):
    d = Path(root) / 'reference' / 'native'
    with np.load(d / 'G96_NATIVE.npz', allow_pickle=False) as f:
        assert np.array_equal(f['item_ids'], shared['item_ids'])
        assert np.array_equal(f['groups'], shared['groups'])
        G = f['G96_native'].copy()
    with np.load(d / 'OOF.npz', allow_pickle=False) as f:
        ref = {k: f[k].copy() for k in f.files}
    assert all(np.array_equal(ref[k], shared[k]) for k in ('item_ids', 'groups', 'y', 'outer_fold'))
    assert np.array_equal(ref['shared_G_curve'], shared['reference']['full_curve'])
    assert np.array_equal(ref['shared_G_raw'], shared['reference']['raw_three_world'])
    schema = json.loads((d / 'G96_SCHEMA.json').read_text())
    assert schema['feature_names'] == shared['schema']['G96']['feature_names']
    assert G.shape == shared['G96'].shape and np.isfinite(G).all()
    out = {'native_G_curve': np.concatenate([G, shared['Curve33']], axis=1),
           'native_G_raw': np.concatenate([G, shared['raw17']], axis=1)}
    arrays = [G, *out.values(), *shared['methods'].values(), shared['G96'], shared['raw17'], shared['Curve33']]
    assert all(a.flags.writeable and np.isfinite(a).all() for a in arrays)
    assert all(not np.shares_memory(a, b) for a, b in combinations(arrays, 2))
    return {'methods': out, 'reference': ref, 'G96': G}
