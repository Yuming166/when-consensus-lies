#!/usr/bin/env python3
"""Post-review label comparison and optional explicit sensitivity; never edits primary data."""
import argparse,csv,hashlib,json
from pathlib import Path
from sklearn.metrics import roc_auc_score,average_precision_score

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument('--review-form',required=True,type=Path)
ap.add_argument('--review-sha256',required=True)
ap.add_argument('--frozen-labels',required=True,type=Path)
ap.add_argument('--frozen-labels-sha256',required=True)
ap.add_argument('--merged-primary',required=True,type=Path)
ap.add_argument('--alternate-label-column',default='alternate_incorrect_label')
ap.add_argument('--output',required=True,type=Path)
a=ap.parse_args()
for p,want in [(a.review_form,a.review_sha256),(a.frozen_labels,a.frozen_labels_sha256)]:
 if sha(p).lower()!=want.lower(): raise SystemExit(f'STOP: hash mismatch for {p}')
reviews=list(csv.DictReader(a.review_form.open(newline='')))
labels=json.load(a.frozen_labels.open())['labels']; frozen={r['item_id']:bool(r['original_correct']) for r in labels}
if len(reviews)!=28 or len({r['item_id'] for r in reviews})!=28: raise SystemExit('STOP: expected 28 unique reviewed IDs')
merged=[json.loads(s) for s in a.merged_primary.open()]
# Item-level independent semantic judgment categories. Ambiguous/unscorable remain excluded from alternate labels.
comp=[]
for r in reviews:
 iid=r['item_id']; judgment=(r.get('model_answer_correct_incorrect_ambiguous_unscorable') or '').strip().lower()
 if iid not in frozen: raise SystemExit(f'unknown ID {iid}')
 alternate = True if judgment=='correct' else False if judgment=='incorrect' else None
 comp.append({'item_id':iid,'reviewer_judgment':judgment or None,'frozen_original_correct':frozen[iid],'reviewer_vs_frozen':'agree' if alternate is not None and alternate==frozen[iid] else 'disagree' if alternate is not None else 'unresolved','alternate_correct_label':alternate,'reason_category':r.get('difference_category_numeric_percentage_unit_rounding_extraction_other')})
# Only fixed scorable primary rows are used. Sensitivity relabels reviewed IDs only and reports coverage.
base={r['item_id']:r for r in merged}
score_fields={'relation_risk':'score_relation_risk','confidence_risk':'score_original_confidence_risk','any_change_risk':'score_any_change_risk'}
base_y={iid:(not bool(r['original_correct'])) for iid,r in base.items()}
metrics={}
for name,sf in score_fields.items():
 ids=[i for i,r in base.items() if r.get(sf) is not None]
 y=[base_y[i] for i in ids]; s=[base[i][sf] for i in ids]
 metrics[name]={'n':len(ids),'error_prevalence':sum(y)/len(y) if y else None,'auroc_error_positive':float(roc_auc_score(y,s)) if len(set(y))==2 else None,'auprc_error_positive':float(average_precision_score(y,s)) if len(set(y))==2 else None}
# This script does not infer an alternate label from free-text itself. Ambiguous and unscorable remain missing.
review_map={r['item_id']:r for r in comp}
ids=[i for i in base if i not in review_map or review_map[i]['alternate_correct_label'] is not None]
y=[base_y[i] if i not in review_map else not review_map[i]['alternate_correct_label'] for i in ids]
alt_metrics={}
for name,sf in score_fields.items():
 ss=[base[i][sf] for i in ids]
 alt_metrics[name]={'n':len(ids),'reviewed_ids_with_resolved_judgment':sum(i in review_map for i in ids),'coverage_of_primary_n':len(ids)/len(base) if base else None,'error_prevalence':sum(y)/len(y) if y else None,'auroc_error_positive':float(roc_auc_score(y,ss)) if len(set(y))==2 else None,'auprc_error_positive':float(average_precision_score(y,ss)) if len(set(y))==2 else None}
out={'artifact':'PECR_ANSWER_LABEL_REVIEW_COMPARISON_AND_SENSITIVITY_V2','posthoc_not_preregistered':True,'review_sha256':sha(a.review_form),'frozen_label_sha256':sha(a.frozen_labels),'primary_merged_sha256':sha(a.merged_primary),'note':'Primary labels/scores are read-only. Sensitivity keeps all frozen primary rows, substitutes only unambiguous reviewed 28-case judgments; ambiguous/unscorable judgments retain frozen label for this explicitly partial sensitivity and are flagged per item. This is not a replacement primary analysis.','reviewed_queue_records':35,'reviewed_unique_ids':len(reviews),'item_comparisons':comp,'frozen_primary_metrics':metrics,'partial_review_label_sensitivity_metrics':alt_metrics}
a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
