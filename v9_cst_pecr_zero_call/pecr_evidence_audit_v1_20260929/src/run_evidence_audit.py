#!/usr/bin/env python3
import csv,hashlib,json,math,os,re,shutil,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT=Path('/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call')
OUT=ROOT/'pecr_evidence_audit_v1_20260929'
MAN=ROOT/'pecr_bidirectional_development_v1_20260928/data/dev_train_manifest_input.jsonl'
CAND=ROOT/'pecr_bidirectional_development_v1_20260928/data/construction_manifest_dev_train.jsonl'
LEDGER=ROOT/'pecr_bidirectional_development_v1_20260928/data/full_dev/raw_ledger_full_dev.jsonl'
LABELS=ROOT/'pecr_trd_delta_method_development_v3_20260926/v3_2/reports/labels_frozen.csv'
FEAT=ROOT/'pecr_bidirectional_transformer_development_v1_20260928/data/parsed_v2/labeled_features.jsonl'
CURVE=ROOT/'pecr_curve_feature_development_v2_audit_20260928/results/CURVE_HGB_AUDITED_OOF.npz'
TRANS=ROOT/'pecr_bidirectional_transformer_development_v1_20260928/results'

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def loadjl(p): return [json.loads(x) for x in open(p) if x.strip()]
def parse_num(x):
 try:
  if x is None:return None
  return float(str(x).strip().replace(',','').replace('−','-'))
 except:return None
def parse_resp(rec):
 if 'parsed_json' not in rec:return None,'missing_json'
 p=rec.get('parsed_json')
 if not isinstance(p,dict):return None,'json_not_object'
 v=parse_num(p.get('answer_value'))
 if v is None:return None,'answer_not_numeric'
 c=parse_num(p.get('confidence'))
 if c is None or not (0<=c<=1):return None,'confidence_invalid'
 return {'value':v,'unit':str(p.get('unit') or '').strip().lower()},None
def group_ci(y,g,a,b,B=2000,seed=20260928):
 rng=np.random.default_rng(seed); ug=np.unique(g); vals=[]
 for _ in range(B):
  ss=rng.choice(ug,len(ug),replace=True); ix=np.concatenate([np.flatnonzero(g==q) for q in ss])
  try: vals.append(roc_auc_score(y[ix],a[ix])-roc_auc_score(y[ix],b[ix]))
  except ValueError: pass
 return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))],len(vals)
def support(ids, labels):
 c=Counter(labels.get(i,{}).get('label_status') for i in ids)
 return {'error':c.get('error',0),'correct':c.get('correct',0),'unlabeled':c.get('unlabeled',0),'total':len(ids)}
def srcgroups(ids, m): return len({m[i]['source_group'] for i in ids if i in m})

def main():
 man_rows=loadjl(MAN); cand_rows=loadjl(CAND); ledger=loadjl(LEDGER); feat=loadjl(FEAT)
 m={r['id']:r for r in man_rows}; cm={r['id']:r for r in cand_rows}; fr={r['id']:r for r in feat}
 labels={r['id']:r for r in csv.DictReader(open(LABELS))}
 by=defaultdict(dict)
 for r in ledger: by[r['item_id']][r['world']]=r
 candidate_ids={r['id'] for r in cand_rows if r.get('bidirectional',{}).get('construction_status') == 'valid_candidate'}
 identity_ids=set(m)-candidate_ids
 item_ids=set(m)|set(by)|set(labels)|set(fr)
 audit=[]
 for iid in sorted(item_ids):
  worlds=by.get(iid,{})
  parse_reasons={}; json_present={}
  for w in ('original','positive','negative'):
   rec=worlds.get(w); json_present[w]=bool(rec and 'parsed_json' in rec)
   _,reason=parse_resp(rec) if rec else (None,'missing_world')
   parse_reasons[w]=reason
  label=labels.get(iid,{})
  flags={
   'not_mechanical_candidate': iid not in candidate_ids,
   'identity_break_candidate': iid in identity_ids,
   'missing_any_request': iid not in by or any(w not in worlds for w in ('original','positive','negative')),
   'json_incomplete_any_world': not all(json_present.values()),
   'strict_parse_failure_any_world': any(parse_reasons[w] is not None for w in ('original','positive','negative')),
   'not_label_eligible': label.get('label_status') not in ('error','correct'),
   'not_strict_analysis': iid not in fr,
  }
  audit.append({'id':iid,'source_group':m.get(iid,{}).get('source_group',label.get('source_group')),'label_status':label.get('label_status'),'label_reason':label.get('label_reason'),'candidate':iid in candidate_ids,'request_worlds':sorted(worlds),'json_present':json_present,'parse_reasons':parse_reasons,'feature_status':fr.get(iid,{}).get('status'),'strict_analysis':iid in fr,'failure_flags':flags})
 with open(OUT/'data/item_coverage_audit.jsonl','w') as f:
  for r in audit:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
 # stage sets
 allids=set(m); req=set(by); jsoncomplete={i for i in req if all('parsed_json' in by[i][w] for w in ('original','positive','negative'))}; eligible={i for i,x in labels.items() if x.get('label_status') in ('error','correct')}; strict=set(fr)
 stages=[('manifest',allids),('mechanical_candidate',candidate_ids),('three_world_requests',req),('json_complete',jsoncomplete),('label_eligible',eligible),('strict_analysis',strict)]
 flow=[]
 for n,ids in stages:
  flow.append({'stage':n,'n_items':len(ids),'source_groups':srcgroups(ids,m),'support':support(ids,labels),'relative_to_manifest':len(ids)/len(allids),'relative_to_mechanical_candidates':len(ids)/len(candidate_ids) if candidate_ids else None})
 json.dump({'stages':flow,'definitions':{'json_complete':'parsed_json key exists for all three worlds; does not imply numeric/unit/confidence validity','strict_analysis':'saved parsed_v2 feature row; all three responses pass strict numeric/confidence parser and label is eligible'},'overlap_failure_flags':True},open(OUT/'reports/QUEUE_FLOW.json','w'),indent=2)
 # failure flags counts and mutually nonexclusive examples
 fc=Counter()
 for r in audit:
  for k,v in r['failure_flags'].items():
   if v:fc[k]+=1
 json.dump({'flag_counts':fc,'note':'Flags are intentionally overlapping and are not a single-cause exclusion taxonomy.'},open(OUT/'reports/EXCLUSION_FLAG_COUNTS.json','w'),indent=2)
 # metrics from OOF
 z=np.load(CURVE,allow_pickle=True); y=z['y']; g=z['groups']
 preds={k:z[k] for k in ('graph_only','two_world_hgb','three_world_hgb','three_world_curve_hgb')}
 for p in sorted(TRANS.glob('*/OOF_*.npz')):
  q=np.load(p,allow_pickle=True); preds[p.parent.name]=q['pred']
 metrics=[]
 for name,p in preds.items():
  metrics.append({'method':name,'n':len(p),'errors':int(y.sum()),'correct':int((y==0).sum()),'auroc':float(roc_auc_score(y,p)),'auprc':float(average_precision_score(y,p)),'coverage':float(np.isfinite(p).mean())})
 comparisons=[]
 base='three_world_curve_hgb'
 for name,p in preds.items():
  if name==base:continue
  ci,nboot=group_ci(y,g,p,preds[base])
  comparisons.append({'comparison':name+' - '+base,'delta_auroc':float(roc_auc_score(y,p)-roc_auc_score(y,preds[base])),'source_group_bootstrap_ci95':ci,'B_effective':nboot})
 # hgb key comparison too
 for name in ('two_world_hgb','three_world_hgb'):
  ci,nboot=group_ci(y,g,preds[name],preds['three_world_hgb']) if name=='two_world_hgb' else (None,None)
  if ci: comparisons.append({'comparison':name+' - three_world_hgb','delta_auroc':float(roc_auc_score(y,preds[name])-roc_auc_score(y,preds['three_world_hgb'])),'source_group_bootstrap_ci95':ci,'B_effective':nboot})
 json.dump({'metrics':metrics,'comparisons':comparisons,'source':'saved OOF only; no retraining','positive_class':'original_incorrect=1','bootstrap':'source-group paired bootstrap, B=2000, seed=20260928'},open(OUT/'reports/OOF_NUMERIC_RECHECK.json','w'),indent=2)
 # hashes
 paths=[MAN,CAND,LEDGER,LABELS,FEAT,CURVE,ROOT/'pecr_curve_feature_development_v2_audit_20260928/results/CURVE_HGB_AUDITED.json',ROOT/'pecr_curve_feature_development_v2_audit_20260928/src/run_curve_hgb_audited.py',ROOT/'pecr_curve_feature_development_v2_audit_20260928/reports/IMPLEMENTATION_AUDIT.json']+sorted(TRANS.glob('*/RESULT*.json'))+sorted(TRANS.glob('*/OOF_*.npz'))
 with open(OUT/'reports/SHA256SUMS_INPUTS.txt','w') as f:
  for p in paths:
   if p.exists(): f.write(f'{sha(p)}  {p}\n')
 print(json.dumps({'flow':flow,'flags':fc,'metrics':metrics,'comparisons':comparisons},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
