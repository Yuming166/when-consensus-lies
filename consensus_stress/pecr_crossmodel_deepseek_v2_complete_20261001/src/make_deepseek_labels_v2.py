#!/usr/bin/env python3
"""Generate labels for the V2 merged ledger using V1's frozen label policy."""
import csv, datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, '/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_trd_delta_method_development_v3_20260926/v3_2/src')
from label_policy import label_one
from extract_train_labels import extract
ROOT=Path('/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call')
V1=ROOT/'pecr_crossmodel_deepseek_v1_20261001'; V2=ROOT/'pecr_crossmodel_deepseek_v2_complete_20261001'
V32=ROOT/'pecr_trd_delta_method_development_v3_20260926/v3_2'
TRAIN=Path('/data/yuanrz/dataset/FinQA/dataset/train.json'); EXPECT='49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6'
def shafile(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
manifest=[json.loads(x) for x in open(V32/'data/candidate_manifest_sealed.jsonl') if x.strip()]
active=[r for r in manifest if r.get('partition')=='dev_train']; assert len(active)==2241
ids={r['id'] for r in active}; assert shafile(TRAIN)==EXPECT
lookup=dict(extract(TRAIN.read_text(),ids))
orig={}
for line in open(V2/'data/merged_ledger_v2.jsonl'):
 r=json.loads(line)
 if r.get('world')=='original':orig[r['item_id']]=r
out=V2/'data/labels_deepseek_v2.csv'; counts={'correct':0,'error':0,'unlabeled':0}; reasons={}
with out.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['id','correct','error','label_status','label_reason'],lineterminator='\n');w.writeheader()
 for r in active:
  i=r['id']; rec=orig.get(i); pred=rec.get('parsed_json',{}).get('answer_value') if rec and isinstance(rec.get('parsed_json'),dict) else None
  label,reason=label_one(pred,lookup.get(i))
  if label is None: status='unlabeled';counts['unlabeled']+=1;reasons[reason]=reasons.get(reason,0)+1
  elif label==1:status='correct';counts['correct']+=1;reason=''
  else:status='error';counts['error']+=1;reason=''
  w.writerow({'id':i,'correct':label if label is not None else '','error':1-label if label is not None else '','label_status':status,'label_reason':reason})
receipt={'status':'deepseek_v2_labels_generated','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label_source_sha256':shafile(TRAIN),'label_file_sha256':shafile(out),'label_rule':'label_policy.label_one (frozen V3.1 numeric free-text tolerance); identical to Qwen/V1','predictions_source':'V2 merged DeepSeek original-world parsed_json.answer_value only','gold_fields_accessed':'qa.answer for dev_train ids only','cohort_rows':len(active),'labels':counts,'unlabeled_reasons':reasons}
(V2/'data/LABEL_RECEIPT_DEEPSEEK_V2.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
