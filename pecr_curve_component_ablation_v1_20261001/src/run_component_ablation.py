#!/usr/bin/env python3
"""Pre-registered, zero-call mechanism ablation for audited Curve HGB."""
import hashlib, json, os
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = Path('/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call')
HERE = ROOT / 'pecr_curve_component_ablation_v1_20261001'
FEAT_PATH = Path(os.environ.get('FEATURE_PATH', str(ROOT / 'pecr_crossmodel_deepseek_v2_complete_20261001/data/parsed_deepseek_v2/labeled_features.jsonl')))
MAN_PATH = ROOT / 'pecr_bidirectional_development_v1_20260928/data/construction_manifest_dev_train.jsonl'
PROTOCOL = HERE / 'protocol/PRE_REGISTERED_COMPONENT_ABLATION_V1.json'

CURVE_NAMES = (
    'positive_response_delta', 'negative_response_delta',
    'positive_abs_delta', 'negative_abs_delta',
    'positive_signed_delta', 'negative_signed_delta',
    'positive_direction_pass', 'negative_direction_pass',
    'positive_flat', 'negative_flat', 'response_symmetry',
    'positive_confidence_delta', 'negative_confidence_delta',
    'all_units_same', 'all_units_nonempty', 'expected_direction_up',
    'construction_absolute_delta', 'relative_input_edit', 'raw_input_edit',
    'positive_slope', 'negative_slope', 'positive_abs_slope',
    'negative_abs_slope', 'slope_asymmetry', 'local_curvature',
    'slope_difference', 'positive_confidence_direction_agreement',
    'negative_confidence_direction_agreement', 'positive_confidence_stable',
    'negative_confidence_stable', 'slope_magnitude_asymmetry',
    'signed_response_agreement', 'both_nonflat',
)
REMOVE = {
    'no_input_normalization': {
        'relative_input_edit', 'positive_slope', 'negative_slope',
        'positive_abs_slope', 'negative_abs_slope',
    },
    'no_curvature_asymmetry': {
        'local_curvature', 'slope_asymmetry', 'slope_difference',
        'slope_magnitude_asymmetry',
    },
    'no_direction_information': {
        'positive_signed_delta', 'negative_signed_delta',
        'positive_direction_pass', 'negative_direction_pass',
        'expected_direction_up', 'positive_confidence_direction_agreement',
        'negative_confidence_direction_agreement', 'signed_response_agreement',
    },
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def paired_ci(y, groups, a, b, B=2000, seed=20260928):
    rng = np.random.default_rng(seed)
    ug = np.unique(groups)
    vals = []
    for _ in range(B):
        chosen = rng.choice(ug, len(ug), replace=True)
        ix = np.concatenate([np.where(groups == g)[0] for g in chosen])
        vals.append(roc_auc_score(y[ix], a[ix]) - roc_auc_score(y[ix], b[ix]))
    return [float(np.quantile(vals, .025)), float(np.quantile(vals, .975))]

def main():
    protocol = json.loads(PROTOCOL.read_text())
    expected_hash = os.environ.get('EXPECTED_HASH', protocol['data']['expected_sha256_labeled_features'])
    observed_hash = sha256(FEAT_PATH)
    if observed_hash != expected_hash:
        raise AssertionError(f'feature hash mismatch: {observed_hash}')
    rows = [json.loads(line) for line in FEAT_PATH.open()]
    expected_n = int(os.environ.get('EXPECTED_N', protocol['fixed_evaluation']['n_expected']))
    if len(rows) != expected_n:
        raise AssertionError(len(rows))
    manifest = {json.loads(line)['id']: json.loads(line) for line in MAN_PATH.open()}
    y = np.asarray([r['y'] for r in rows], dtype=int)
    groups = np.asarray([r['source_group'] for r in rows])
    graph = np.asarray([r['graph'] for r in rows], dtype=np.float64).copy()
    raw = np.asarray([r['response_features'] for r in rows], dtype=np.float64).copy()
    curve = np.asarray([r['response_curve'] if 'response_curve' in r else None for r in rows], dtype=object)
    # Curve dimensions are deterministically reconstructed from the frozen responses
    # using the exact audited implementation; this avoids relying on an unstored array.

    def num(x):
        try: return float(x)
        except Exception: return np.nan
    curve_rows = []
    for row in rows:
        o, p, n = (row['responses'][w] for w in ('original', 'positive', 'negative'))
        direction = float(row['direction'])
        mr = manifest[row['id']]
        old = num(mr['aligned_operand']['original_literal']); new = num(mr['aligned_operand']['new_value'])
        inp = new - old
        dp, dn = p['value'] - o['value'], o['value'] - n['value']
        den = abs(inp) + 1e-9
        sp, sn = dp / den, dn / den
        curve_rows.append([
            dp, dn, abs(dp), abs(dn), dp * direction, dn * direction,
            float(dp * direction > 0), float(dn * direction > 0),
            float(dp == 0), float(dn == 0),
            min(abs(dp), abs(dn)) / (max(abs(dp), abs(dn)) + 1e-9),
            p['confidence'] - o['confidence'], n['confidence'] - o['confidence'],
            float(len({o['unit'], p['unit'], n['unit']}) <= 1),
            float(all(x['unit'] for x in (o, p, n))), float(direction == 1),
            float(mr['absolute_delta']), inp / (abs(old) + 1e-9), inp,
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
        ])
    CURVE = np.asarray(curve_rows, dtype=np.float64).copy()
    RAW = np.asarray(raw, dtype=np.float64).copy()
    if CURVE.shape != (len(rows), len(CURVE_NAMES)) or RAW.shape != (len(rows), 17):
        raise AssertionError((CURVE.shape, RAW.shape))
    indexes = {name: i for i, name in enumerate(CURVE_NAMES)}
    remove_ix = {k: np.asarray(sorted(indexes[x] for x in v), dtype=int) for k, v in REMOVE.items()}
    keep = np.ones(len(CURVE_NAMES), dtype=bool)
    full_ix = np.flatnonzero(keep)
    ablations = {k: np.setdiff1d(full_ix, ix, assume_unique=True) for k, ix in remove_ix.items()}
    for k, ix in remove_ix.items():
        if len(ix) != len(REMOVE[k]) or len(np.intersect1d(ix, ablations[k])) != 0:
            raise AssertionError(k)
    methods = {
        'full_curve': np.concatenate([graph, CURVE], axis=1),
        'raw_three_world': np.concatenate([graph, RAW], axis=1),
    }
    for k, ix in ablations.items():
        methods[k] = np.concatenate([graph, CURVE[:, ix]], axis=1)
    # Independent allocation and exact removed-column checks.
    tests = {
        'feature_hash_matches_frozen_v2': observed_hash == expected_hash,
        'arrays_do_not_share_memory': not any(
            np.shares_memory(methods[a], methods[b])
            for a in methods for b in methods if a != b
        ),
        'raw_curve_first_17_match_excluding_documented_symmetry_swap': True,
    }
    # The only intended difference among dimensions 0..16 is identity -> response_symmetry.
    if not (np.array_equal(RAW[:, :11], CURVE[:, :11]) and np.array_equal(RAW[:, 12:17], CURVE[:, 12:17])):
        tests['raw_curve_first_17_match_excluding_documented_symmetry_swap'] = False
    for k, ix in remove_ix.items():
        removed = methods['full_curve'][:, graph.shape[1] + ix]
        kept = methods[k][:, graph.shape[1]:]
        tests[f'exact_removal_{k}'] = bool(
            np.array_equal(kept, np.delete(CURVE, ix, axis=1)) and np.all(np.isfinite(removed))
        )
    if not all(tests.values()): raise AssertionError(tests)

    predictions = {name: np.full(len(y), np.nan) for name in methods}
    folds = []
    splitter = GroupKFold(5)
    for fold, (train, test) in enumerate(splitter.split(graph, y, groups)):
        folds.append({'fold': fold, 'train_n': len(train), 'test_n': len(test), 'test_groups': len(set(groups[test]))})
        for name, X in methods.items():
            clf = HistGradientBoostingClassifier(max_iter=250, max_leaf_nodes=15, learning_rate=.05, l2_regularization=1.0, random_state=20260928)
            clf.fit(X[train], y[train]); predictions[name][test] = clf.predict_proba(X[test])[:, 1]

    metrics = {}
    for name, pred in predictions.items():
        metrics[name] = {
            'auroc': float(roc_auc_score(y, pred)),
            'auprc': float(average_precision_score(y, pred)),
            'coverage': float(np.isfinite(pred).mean()),
            'support_n': int(np.isfinite(pred).sum()),
        }
    comparisons = [
        ('full_curve', 'raw_three_world', 'primary'),
        ('no_input_normalization', 'full_curve', 'primary'),
        ('no_curvature_asymmetry', 'full_curve', 'primary'),
        ('no_direction_information', 'full_curve', 'primary'),
        ('no_input_normalization', 'raw_three_world', 'secondary'),
        ('no_curvature_asymmetry', 'raw_three_world', 'secondary'),
        ('no_direction_information', 'raw_three_world', 'secondary'),
    ]
    for a, b, role in comparisons:
        metrics[f'{a}_minus_{b}'] = {
            'role': role,
            'delta_auroc': metrics[a]['auroc'] - metrics[b]['auroc'],
            'source_group_ci95': paired_ci(y, groups, predictions[a], predictions[b]),
        }
    result = {
        'version': os.environ.get('RESULT_VERSION', protocol['version']),
        'feature_sha256': observed_hash,
        'n': len(y), 'errors': int(y.sum()), 'correct': int((y == 0).sum()),
        'groups': len(np.unique(groups)),
        'feature_sets': {
            'curve_names': list(CURVE_NAMES),
            'removed': {k: sorted(v) for k, v in REMOVE.items()},
            'dimensions': {name: int(X.shape[1]) for name, X in methods.items()},
        },
        'tests': tests, 'folds': folds, 'metrics': metrics,
        'protocol': protocol['fixed_evaluation'],
        'model_calls': 0,
    }
    outdir = Path(os.environ.get('ABLATION_OUTDIR', HERE / 'results'))
    outdir.mkdir(parents=True, exist_ok=True)
    np.savez(outdir / 'COMPONENT_ABLATION_OOF.npz', y=y, groups=groups, **predictions)
    (outdir / 'COMPONENT_ABLATION.json').write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))
if __name__ == '__main__': main()
