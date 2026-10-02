"""Fixed paired source-group evaluation, shared by all analyses in V1."""
from collections import Counter
import hashlib
import json

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

B = 2000
SEED = 20260928


def support(y, groups, strict_n, requested_n=2225):
    y, groups = np.asarray(y), np.asarray(groups)
    return {'n': len(y), 'groups': len(set(groups)),
            'error_1': int((y == 1).sum()), 'correct_0': int((y == 0).sum()),
            'error_prevalence': float((y == 1).mean()) if len(y) else None,
            'coverage_of_strict': len(y) / strict_n,
            'coverage_of_requested': len(y) / requested_n,
            'coverage_of_full_frame': len(y) / 2241}


def evaluate(y, groups, predictions, contrasts, B=B, seed=SEED):
    y, groups = np.asarray(y), np.asarray(groups)
    assert len(y) == len(groups) and set(y.tolist()) <= {0, 1}
    assert all(len(p) == len(y) and np.isfinite(p).all() for p in predictions.values())
    assert all(a in predictions and b in predictions for a, b in contrasts.values())
    both_classes = len(set(y.tolist())) == 2
    metrics = {name: {'auroc': float(roc_auc_score(y, p)) if both_classes else None,
                      'auprc': float(average_precision_score(y, p)) if both_classes else None,
                      'support_n': len(y), 'prediction_coverage': 1.0 if len(y) else 0.0}
               for name, p in predictions.items()}
    result = {'metrics': metrics, 'contrasts': {},
              'bootstrap': {'attempts': B, 'seed': seed, 'unit': 'source_group',
                            'paired': True, 'percentile': [2.5, 97.5],
                            'degenerate_single_class_draws': 0, 'valid_draws': 0,
                            'retry_degenerate_draws': False}}
    if not both_classes:
        result['status'] = 'insufficient_class_support'
        return result
    ug = np.unique(groups)
    indices = {g: np.flatnonzero(groups == g) for g in ug}
    values = {name: {'auroc': [], 'auprc': []} for name in predictions}
    rng = np.random.default_rng(seed)
    draw_hash = hashlib.sha256()
    for _ in range(B):
        chosen = rng.choice(ug, len(ug), replace=True)
        draw_hash.update(json.dumps(chosen.tolist(), separators=(',', ':')).encode() + b'\n')
        ix = np.concatenate([indices[g] for g in chosen])
        if len(set(y[ix].tolist())) < 2:
            result['bootstrap']['degenerate_single_class_draws'] += 1
            continue
        for name, p in predictions.items():
            values[name]['auroc'].append(float(roc_auc_score(y[ix], p[ix])))
            values[name]['auprc'].append(float(average_precision_score(y[ix], p[ix])))
    result['bootstrap']['valid_draws'] = B - result['bootstrap']['degenerate_single_class_draws']
    result['bootstrap']['draw_sequence_sha256'] = draw_hash.hexdigest()
    for name in predictions:
        for metric in ('auroc', 'auprc'):
            metrics[name][metric + '_ci95'] = np.quantile(values[name][metric], [.025, .975]).tolist() if values[name][metric] else None
    for contrast, (a, b) in contrasts.items():
        row = {'left': a, 'right': b}
        for metric in ('auroc', 'auprc'):
            deltas = np.asarray(values[a][metric]) - np.asarray(values[b][metric])
            row['delta_' + metric] = metrics[a][metric] - metrics[b][metric]
            row['delta_' + metric + '_ci95'] = np.quantile(deltas, [.025, .975]).tolist() if len(deltas) else None
        result['contrasts'][contrast] = row
    result['status'] = 'evaluated'
    return result
