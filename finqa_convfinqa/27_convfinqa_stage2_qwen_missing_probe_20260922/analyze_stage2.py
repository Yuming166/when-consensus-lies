#!/usr/bin/env python3
"""Fit the frozen ConvFinQA missing-probe heads on TRAIN and confirm once on DEV.

This script is offline: it consumes completed Qwen TRAIN/DEV records, uses only
original/-1/+1-derived features, and never uses original correctness to fit or
select the student.  The DEV set is read once after the train fit.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math, random
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

HERE=Path(__file__).resolve().parent
S1=HERE.parents[1]/'finqa_convfinqa'/'26_convfinqa_stage1_qwen_replication_20260922'
CONTRACT=HERE/'CONVFINQA_STAGE2_QWEN_TRAIN_CONTRACT.json'
TRAIN_GOLD=HERE/'STAGE2_TRAIN_WORLD_GOLD.jsonl'; TRAIN_RAW=HERE/'STAGE2_QWEN_TRAIN_RAW_RECORDS.jsonl'
DEV_GOLD=HERE/'STAGE2_DEV_WORLD_GOLD.jsonl'; DEV_RAW=HERE/'STAGE1_QWEN_DEV_RAW_RECORDS.jsonl'
OUT=HERE/'STAGE2_CONFIRMATION_ANALYSIS.json'; MD=HERE/'STAGE2_CONFIRMATION_ANALYSIS.md'
ROWS_TRAIN=HERE/'STAGE2_TRAIN_FEATURE_ROWS.jsonl'; ROWS_DEV=HERE/'STAGE2_DEV_FEATURE_ROWS.jsonl'; PRED=HERE/'STAGE2_DEV_PREDICTIONS.jsonl'
SEED=20260922; BOOTSTRAP=5000

def load_json(p):return json.loads(p.read_text())
def load_jsonl(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def write_json(p,x):p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n')
def write_jsonl(p,xs):p.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n' for x in xs))
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def auc(scores,labels):
 scores=list(map(float,scores)); labels=list(map(int,labels)); pos=[s for s,y in zip(scores,labels) if y]; neg=[s for s,y in zip(scores,labels) if not y]
 if not pos or not neg:return None
 return sum(1 if p>n else .5 if p==n else 0 for p in pos for n in neg)/(len(pos)*len(neg))
def pct(xs,q):
 if not xs:return None
 x=sorted(xs); z=(len(x)-1)*q; lo=math.floor(z);hi=math.ceil(z)
 return x[lo] if lo==hi else x[lo]+(x[hi]-x[lo])*(z-lo)
def bootstrap_delta(a,b,y,seed=SEED,reps=BOOTSTRAP):
 rng=random.Random(seed); obs=None if auc(a,y) is None or auc(b,y) is None else auc(a,y)-auc(b,y); vals=[]
 for _ in range(reps):
  idx=[rng.randrange(len(y)) for _ in y]; aa=[a[i] for i in idx];bb=[b[i] for i in idx];yy=[y[i] for i in idx]; va=auc(aa,yy);vb=auc(bb,yy)
  if va is not None and vb is not None:vals.append(va-vb)
 return {'observed':obs,'ci_95':[pct(vals,.025),pct(vals,.975)],'replicates':reps,'valid_replicates':len(vals),'seed':seed}
def bootstrap_auc(a,y,seed=SEED,reps=BOOTSTRAP):
 rng=random.Random(seed);obs=auc(a,y);vals=[]
 for _ in range(reps):
  idx=[rng.randrange(len(y)) for _ in y];v=auc([a[i] for i in idx],[y[i] for i in idx])
  if v is not None:vals.append(v)
 return {'observed':obs,'ci_95':[pct(vals,.025),pct(vals,.975)],'replicates':reps,'valid_replicates':len(vals),'seed':seed}
def spearman(a,b):
 def rank(x):
  order=sorted(range(len(x)),key=lambda i:x[i]);out=[0.0]*len(x);i=0
  while i<len(x):
   j=i+1
   while j<len(x) and x[order[j]]==x[order[i]]:j+=1
   r=(i+1+j)/2
   for k in order[i:j]:out[k]=r
   i=j
  return out
 x=rank(list(map(float,a)));y=rank(list(map(float,b)));mx=sum(x)/len(x);my=sum(y)/len(y);num=sum((u-mx)*(v-my) for u,v in zip(x,y));den=math.sqrt(sum((u-mx)**2 for u in x)*sum((v-my)**2 for v in y));return None if den==0 else num/den

def parse_surface(raw):
 if raw is None or isinstance(raw,bool):return None
 text=str(raw).strip();
 if not text or len(text)>128:return None
 percent='%' in text; par='(' in text and ')' in text;clean=''.join(text.replace('$','').replace(',','').replace('%','').replace('(','').replace(')','').split())
 if not clean or clean in {'+','-','.'}:return None
 try:v=Decimal(clean)
 except (InvalidOperation,ValueError):return None
 if text.startswith('-') or par:v=-abs(v)
 return v/Decimal(100) if percent else v

def score_records(gold_path,raw_path):
 gs=load_jsonl(gold_path); rs=load_jsonl(raw_path); r={x['world_id']:x for x in rs};out={}
 for g in gs:
  x=r[g['world_id']]; pred=parse_surface(x.get('answer')) if x.get('valid') else None
  exp=Decimal(str(g['expected_normalized_answer']));tol=Decimal(str(g['expected_tolerance']))
  out[g['world_id']]={'gold':g,'raw':x,'pred':pred,'valid':pred is not None,'correct':int(pred is not None and abs(pred-exp)<=tol),'expected':exp,'confidence':float(x.get('confidence') or 0.0)}
 return out

def numeric(x):
 if not x['valid']:return {'valid':0,'correct':x['correct'],'signed_residual':0.0,'abs_residual':0.0,'pred':None,'expected':float(x['expected'])}
 scale=max(abs(x['expected']),Decimal(str(x['gold']['expected_tolerance'])),Decimal('1e-12'));res=(x['pred']-x['expected'])/scale
 return {'valid':1,'correct':x['correct'],'signed_residual':float(res),'abs_residual':float(abs(res)),'pred':float(x['pred']),'expected':float(x['expected'])}

def features(base,probe):
 b=numeric(base);p=numeric(probe);bp=base['pred'];pp=probe['pred'];bg=base['expected'];pg=probe['expected'];gdelta=pg-bg if bg is not None and pg is not None else None;pdelta=pp-bp if bp is not None and pp is not None else None;scale=max(abs(gdelta or Decimal(0)),Decimal('1e-12'));direction=0.0;mag=0.0;normdelta=0.0
 if base['valid'] and probe['valid'] and gdelta is not None and pdelta is not None:
  normdelta=float(pdelta/scale);pred_sign=(pdelta>0)-(pdelta<0);gold_sign=(gdelta>0)-(gdelta<0);direction=float(pred_sign==gold_sign) if gdelta!=0 else 0.0;mag=float(abs(pdelta-gdelta)/scale) if gdelta!=0 else 0.0
 conf=probe['confidence'];bconf=base['confidence']
 return {'correct':float(p['correct']),'valid':float(p['valid']),'confidence':conf,'confidence_delta':conf-bconf,'confidence_valid':float(0<=conf<=1),'signed_residual':p['signed_residual'],'abs_residual':p['abs_residual'],'direction_fidelity':direction,'magnitude_error':mag,'normalized_pred_delta':normdelta}

def build_rows(scored):
 by=defaultdict(dict)
 for wid,x in scored.items():by[x['gold']['item_id']][x['gold']['world_label']]=x
 rows=[]
 for item in sorted(by):
  w=by[item];need=['original','relevant_k_minus2','relevant_k_minus1','relevant_k_plus1','relevant_k_plus2']
  if not all(k in w for k in need):raise RuntimeError(f'incomplete {item}')
  base=w['original']; minus=features(base,w['relevant_k_minus1']);plus=features(base,w['relevant_k_plus1']);row={'item_id':item,'source_group_id':base['gold']['source_group_id'],'filename':base['gold']['filename'],'original_correct':base['correct'],'original_confidence':float(base['confidence']),'original_confidence_valid':float(0<=base['confidence']<=1),'minus1_correct':minus['correct'],'plus1_correct':plus['correct'],'target_minus2':w['relevant_k_minus2']['correct'],'target_plus2':w['relevant_k_plus2']['correct'],'teacher_cef':sum(w[k]['correct'] for k in need[1:])/4.0}
  for side,fs in [('minus1',minus),('plus1',plus)]:
   for n,v in fs.items():row[f'{side}_{n}']=float(v)
  for n in ['correct','valid','confidence','confidence_delta','signed_residual','abs_residual','direction_fidelity','magnitude_error','normalized_pred_delta']:
   a=float(row[f'minus1_{n}']);b=float(row[f'plus1_{n}']);row[f'pair_{n}_mean']=(a+b)/2;row[f'pair_{n}_diff']=a-b;row[f'pair_{n}_abs_diff']=abs(a-b)
  rows.append(row)
 return rows

def model(kind,seed):
 if kind=='logistic':return Pipeline([('impute',SimpleImputer(strategy='constant',fill_value=0.0)),('scale',StandardScaler()),('model',LogisticRegression(C=1.0,solver='liblinear',max_iter=2000,random_state=seed))])
 if kind=='gbdt':return Pipeline([('impute',SimpleImputer(strategy='constant',fill_value=0.0)),('model',GradientBoostingClassifier(n_estimators=64,learning_rate=.05,max_depth=2,min_samples_leaf=8,random_state=seed))])
 raise ValueError(kind)

def main():
 contract=load_json(CONTRACT);v10=load_json(HERE.parents[1]/'finqa_convfinqa'/'24_pecr_v0_10_missing_probe_imputation_20260922'/'PECR_V0_10_FROZEN_CONTRACT.json');families=v10['features']['families']
 train=build_rows(score_records(TRAIN_GOLD,TRAIN_RAW));dev=build_rows(score_records(DEV_GOLD,DEV_RAW));write_jsonl(ROWS_TRAIN,train);write_jsonl(ROWS_DEV,dev)
 results={};pred_rows=[]
 for family in ['s2','s2_direction','all_response_rich']:
  names=families[family];X=np.array([[float(r[n]) for n in names] for r in train]);Xd=np.array([[float(r[n]) for n in names] for r in dev]);ym=np.array([r['target_minus2'] for r in train]);yp=np.array([r['target_plus2'] for r in train]);ymd=np.array([r['target_minus2'] for r in dev]);ypd=np.array([r['target_plus2'] for r in dev]);
  for kind in ['logistic','gbdt']:
   mm=model(kind,SEED+1);mp=model(kind,SEED+2);mm.fit(X,ym);mp.fit(X,yp);pm=mm.predict_proba(Xd)[:,1] if len(np.unique(ym))>1 else np.full(len(dev),ym[0]);pp=mp.predict_proba(Xd)[:,1] if len(np.unique(yp))>1 else np.full(len(dev),yp[0]);s2=np.array([(r['minus1_correct']+r['plus1_correct'])/2 for r in dev]);full=np.array([r['teacher_cef'] for r in dev]);hat=(np.array([r['minus1_correct'] for r in dev])+np.array([r['plus1_correct'] for r in dev])+pm+pp)/4;orig=np.array([r['original_correct'] for r in dev]);key=f'{family}__{kind}';results[key]={'family':family,'model':kind,'feature_count':len(names),'features':names,'head_minus2':{'auroc':auc(pm,ymd),'positive_count':int(ymd.sum()),'n':len(ymd)},'head_plus2':{'auroc':auc(pp,ypd),'positive_count':int(ypd.sum()),'n':len(ypd)},'student_auroc':auc(hat,orig),'s2_auroc':auc(s2,orig),'full_cef_auroc':auc(full,orig),'delta_vs_s2':bootstrap_delta(hat.tolist(),s2.tolist(),orig.tolist(),seed=SEED+100),'teacher_mae':float(np.mean(np.abs(hat-full))),'teacher_rmse':float(np.sqrt(np.mean((hat-full)**2))),'teacher_spearman':spearman(hat.tolist(),full.tolist()),'gap_closure':None if abs(auc(full,orig)-auc(s2,orig))<1e-12 else (auc(hat,orig)-auc(s2,orig))/(auc(full,orig)-auc(s2,orig))}
   if family=='all_response_rich' and kind=='gbdt':
    for i,r in enumerate(dev):pred_rows.append({'item_id':r['item_id'],'source_group_id':r['source_group_id'],'p_minus2':float(pm[i]),'p_plus2':float(pp[i]),'cef_hat':float(hat[i]),'s2':float(s2[i]),'full_cef':float(full[i]),'original_correct':int(orig[i]),'target_minus2':int(ymd[i]),'target_plus2':int(ypd[i])})
 write_jsonl(PRED,pred_rows)
 primary=results['all_response_rich__gbdt'];out={'protocol':contract['protocol'],'status':'STAGE2_ANALYSIS_COMPLETE','model_calls':len(load_jsonl(TRAIN_RAW)),'train_items':len(train),'dev_items':len(dev),'train_worlds':len(load_jsonl(TRAIN_GOLD)),'dev_worlds':len(load_jsonl(DEV_GOLD)),'target_support':{'train_minus2':sum(r['target_minus2'] for r in train),'train_plus2':sum(r['target_plus2'] for r in train),'dev_minus2':sum(r['target_minus2'] for r in dev),'dev_plus2':sum(r['target_plus2'] for r in dev)},'families':results,'primary_key':'all_response_rich__gbdt','primary':primary,'practical_gate':{'threshold':.02,'delta':primary['delta_vs_s2']['observed'],'pass':bool(primary['delta_vs_s2']['observed'] is not None and primary['delta_vs_s2']['observed']>=.02)},'claim_boundary':'ConvFinQA Qwen TRAIN-fit missing-probe distillation confirmed once on frozen DEV if and only if the reported primary gate is interpreted with its CI and no post-hoc tuning.'}
 write_json(OUT,out);MD.write_text(f"# ConvFinQA Stage 2 confirmation\n\n- Status: **{out['status']}**\n- Primary: all_response_rich + shallow GBDT two binary heads.\n- Head AUROC -2: **{primary['head_minus2']['auroc']}**; +2: **{primary['head_plus2']['auroc']}**.\n- Student AUROC: **{primary['student_auroc']}**; S2: **{primary['s2_auroc']}**; full CEF: **{primary['full_cef_auroc']}**.\n- Student minus S2: **{primary['delta_vs_s2']['observed']}**, bootstrap CI **{primary['delta_vs_s2']['ci_95']}**.\n- Gap closure: **{primary['gap_closure']}**.\n- Teacher MAE: **{primary['teacher_mae']}**; Spearman: **{primary['teacher_spearman']}**.\n- Practical +0.02 gate: **{out['practical_gate']['pass']}**.\n\nOriginal correctness is evaluation-only; no DEV refit or feature/model selection was performed.\n")
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
