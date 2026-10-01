#!/usr/bin/env python3
"""DeepSeek labels: same frozen label policy as Qwen (label_policy.label_one),
applied to DeepSeek original-world parsed answer_value vs FinQA train gold
qa.answer for the same 2,241 dev_train ids. Positive/negative worlds are never
used for labels. Writes labels CSV (same schema as labels_frozen.csv) + receipt."""
import csv, json, hashlib, sys, datetime
from pathlib import Path
sys.path.insert(0, '/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_trd_delta_method_development_v3_20260926/v3_2/src')
from label_policy import label_one
from extract_train_labels import extract

ROOT = Path('/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_crossmodel_deepseek_v1_20261001')
V32 = Path('/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_trd_delta_method_development_v3_20260926/v3_2')
TRAIN = Path('/data/yuanrz/dataset/FinQA/dataset/train.json')
EXPECTED_TRAIN_SHA = '49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6'

def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''): h.update(b)
    return h.hexdigest()

def main():
    ledger = ROOT / 'data/full_dev/raw_ledger_full_dev.jsonl'
    manifest = [json.loads(x) for x in (V32 / 'data/candidate_manifest_sealed.jsonl').read_text().splitlines() if x]
    active = [r for r in manifest if r.get('partition') == 'dev_train']
    assert len(active) == 2241, 'active partition count'
    target_ids = {r['id'] for r in active}
    assert sha_file(TRAIN) == EXPECTED_TRAIN_SHA, 'train.json bytes changed'
    lookup = dict(extract(TRAIN.read_text(encoding='utf-8'), target_ids))

    orig = {}
    for line in open(ledger):
        r = json.loads(line)
        if r.get('world') == 'original':
            orig[r['item_id']] = r
    out = ROOT / 'data/labels_deepseek.csv'
    counts = {'correct': 0, 'error': 0, 'unlabeled': 0}; reasons = {}
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'correct', 'error', 'label_status', 'label_reason'])
        w.writeheader()
        for r in active:
            i = r['id']
            rec = orig.get(i)
            pred = None
            if rec and isinstance(rec.get('parsed_json'), dict):
                pred = rec['parsed_json'].get('answer_value')
            label, reason = label_one(pred, lookup.get(i))
            if label is None:
                status = 'unlabeled'; counts['unlabeled'] += 1
                reasons[reason] = reasons.get(reason, 0) + 1
            elif label == 1:
                status = 'correct'; counts['correct'] += 1; reason = ''
            else:
                status = 'error'; counts['error'] += 1; reason = ''
            w.writerow({'id': i, 'correct': label if label is not None else '',
                        'error': (1 - label) if label is not None else '',
                        'label_status': status, 'label_reason': reason})
    receipt = {
        'status': 'deepseek_labels_generated',
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'label_source_sha256': sha_file(TRAIN),
        'label_file_sha256': sha_file(out),
        'label_rule': 'label_policy.label_one (frozen V3.1 numeric free-text tolerance); identical to Qwen labels',
        'predictions_source': 'DeepSeek original-world parsed_json.answer_value only',
        'gold_fields_accessed': 'qa.answer for dev_train ids only',
        'cohort_rows': len(active), 'labels': counts, 'unlabeled_reasons': reasons,
    }
    (ROOT / 'data/LABEL_RECEIPT_DEEPSEEK.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
