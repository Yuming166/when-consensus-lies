#!/usr/bin/env python3
"""Secondary (descriptive) transfer analysis: Curve HGB trained on ALL Qwen
dev_train features, scored on DeepSeek features; and the reverse direction.
Same frozen feature builder and hyperparameters as run_curve_hgb_audited.py."""
import json, sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

sys.path.insert(0, '/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_curve_feature_development_v2_audit_20260928/src')
import importlib.util
spec = importlib.util.spec_from_file_location(
    'curve_audited',
    '/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_curve_feature_development_v2_audit_20260928/src/run_curve_hgb_audited.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

QWEN_FEAT = '/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_bidirectional_transformer_development_v1_20260928/data/parsed_v2/labeled_features.jsonl'

def load(path):
    rows = [json.loads(l) for l in open(path)]
    manifest = mod  # features() looks up manifest itself via global MAN
    man = {json.loads(l)['id']: json.loads(l) for l in open(mod.MAN)}
    X, y, g = [], [], []
    for r in rows:
        _, curve = mod.features(r, man[r['id']])
        X.append(np.concatenate([np.asarray(r['graph'], dtype=np.float64), curve]))
        y.append(int(r['y'])); g.append(r['source_group'])
    return np.asarray(X), np.asarray(y), np.asarray(g)

def group_ci(y, groups, pred, B=2000, seed=20261001):
    rng = np.random.default_rng(seed); ug = np.unique(groups); vals = []
    for _ in range(B):
        sel = rng.choice(ug, len(ug), replace=True)
        ix = np.concatenate([np.where(groups == q)[0] for q in sel])
        vals.append(roc_auc_score(y[ix], pred[ix]))
    return [float(np.quantile(vals, .025)), float(np.quantile(vals, .975))]

def fit(X, y):
    clf = HistGradientBoostingClassifier(max_iter=250, max_leaf_nodes=15, learning_rate=.05,
                                         l2_regularization=1.0, random_state=20260928)
    return clf.fit(X, y)

def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    ds_feat = sys.argv[2]
    Xq, yq, gq = load(QWEN_FEAT)
    Xd, yd, gd = load(ds_feat)
    res = {'qwen_n': len(yq), 'deepseek_n': len(yd),
           'deepseek_errors': int(yd.sum()), 'deepseek_correct': int((yd == 0).sum())}
    p = fit(Xq, yq).predict_proba(Xd)[:, 1]
    res['qwen_trained_on_deepseek'] = {
        'auroc': float(roc_auc_score(yd, p)), 'auprc': float(average_precision_score(yd, p)),
        'auroc_group_ci95': group_ci(yd, gd, p)}
    p2 = fit(Xd, yd).predict_proba(Xq)[:, 1]
    res['deepseek_trained_on_qwen'] = {
        'auroc': float(roc_auc_score(yq, p2)), 'auprc': float(average_precision_score(yq, p2)),
        'auroc_group_ci95': group_ci(yq, gq, p2)}
    np.savez(out / 'TRANSFER_PREDICTIONS.npz', qwen_on_deepseek=p, deepseek_on_qwen=p2)
    (out / 'TRANSFER_RESULTS.json').write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))

if __name__ == '__main__':
    main()
