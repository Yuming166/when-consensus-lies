#!/usr/bin/env python3
import argparse,json,csv,hashlib,re,os,random
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
NUM=re.compile(r'^[-+]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?$')
def parse_num(x):
 if x is None:return None
 s=str(x).strip().replace(',','').replace('−','-')
 if not s:return None
 try:return float(s)
 except:return None
def norm_unit(u):
 if u is None:return ''
 s=str(u).strip().lower().replace('percentage','%').replace('percent','%')
 return s

def parse_resp(rec):
 if 'parsed_json' not in rec:return None,'missing_json'
 p=rec['parsed_json']
 if not isinstance(p,dict):return None,'json_not_object'
 v=parse_num(p.get('answer_value'))
 if v is None:return None,'answer_not_numeric'
 c=parse_num(p.get('confidence'))
 if c is None or not (0<=c<=1): return None,'confidence_invalid'
 return {'value':v,'unit':norm_unit(p.get('unit')),'confidence':c},None

def mark_table(table,cell):
 out=[]
 for i,row in enumerate(table):
  cells=[]
  for j,x in enumerate(row):
   s=str(x)
   if [i,j]==list(cell): s='[EDIT_OLD] '+s+' [/EDIT_OLD]'
   cells.append(s)
  out.append(' | '.join(cells))
 return '\n'.join(out)
def text_for(r,w):
 b=r['bidirectional']; t=r['table_original'] if w=='original' else r['table_mutated'] if w=='positive' else b['reverse_table']
 cell=r['aligned_operand']['table_cell']; s=' '.join(r.get('pre_text',[]))+' '+r['question']+' '+mark_table(t,cell)+' '+' '.join(r.get('post_text',[]))
 return s

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--manifest',required=True); ap.add_argument('--ledger',required=True); ap.add_argument('--labels',required=True); ap.add_argument('--feature-npz',required=True); ap.add_argument('--row-map',required=True); ap.add_argument('--outdir',required=True); a=ap.parse_args(); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
 manifest={json.loads(l)['id']:json.loads(l) for l in open(a.manifest) if l.strip()}
 labels={r['id']:int(r['error']) for r in csv.DictReader(open(a.labels)) if r['label_status'] in ('error','correct')}
 graph=np.load(a.feature_npz,allow_pickle=True)['graph']; rowmap={json.loads(l)['id']:json.loads(l)['row_index'] for l in open(a.row_map)}
 by=defaultdict(dict); recs=[]; prev='GENESIS'; bad=[]
 for ln,l in enumerate(open(a.ledger),1):
  r=json.loads(l); recs.append(r)
  if r.get('previous_record_hash')!=prev: bad.append([ln,'previous_hash'])
  q={k:v for k,v in r.items() if k!='record_hash'}
  if hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=r.get('record_hash'): bad.append([ln,'record_hash'])
  prev=r.get('record_hash'); by[r['item_id']][r['world']]=r
 counts=Counter(); rows=[]
 for iid,y in labels.items():
  r=manifest.get(iid); ws=by.get(iid,{})
  if not r or not all(w in ws for w in ('original','positive','negative')): counts['missing_world_or_manifest']+=1; continue
  parsed={}; reasons={}
  for w in ('original','positive','negative'):
   parsed[w],reasons[w]=parse_resp(ws[w])
  if any(parsed[w] is None for w in parsed): counts['invalid_response']+=1; status='invalid_response'
  else:
   vals=[parsed[w]['value'] for w in parsed]; units=[parsed[w]['unit'] for w in parsed]; exp=1 if r['program_conditioned_direction']=='up' else -1
   dp=vals[1]-vals[0]; dn=vals[0]-vals[2]
   ident=float(min(abs(dp),abs(dn))/(max(abs(dp),abs(dn))+1e-9))
   feat=[dp,dn,abs(dp),abs(dn),dp*exp,dn*exp,float(dp*exp>0),float(dn*exp>0),float(dp==0),float(dn==0),ident,parsed['positive']['confidence']-parsed['original']['confidence'],parsed['negative']['confidence']-parsed['original']['confidence'],float(len(set(units))<=1),float(all(u!='' for u in units)),float(exp==1),float(r['absolute_delta'])]
   status='complete'; counts['complete']+=1
   rows.append({'id':iid,'source_group':r['source_group'],'y':y,'graph_row':rowmap[iid],'graph':graph[rowmap[iid]].astype(float).tolist(),'response_features':feat,'responses':parsed,'texts':{w:text_for(r,w) for w in ('original','positive','negative')},'direction':exp,'operation':r.get('program_original','').split('(')[0],'label_blind_construct':r.get('status',''),'parse_reasons':reasons,'status':status})
  if status!='complete': counts[status]+=1
 outjson={'n_ledger_records':len(recs),'n_label_rows':len(labels),'n_complete':len(rows),'counts':dict(counts),'chain_head':prev,'chain_errors':bad,'model_identity':Counter(x.get('model_requested') for x in recs),'http_status':Counter(str(x.get('http_status')) for x in recs),'json_invalid_records':[{'slot':x.get('slot'),'id':x.get('item_id'),'world':x.get('world'),'response':x.get('response_text','')[:500]} for x in recs if 'parsed_json' not in x]}
 (out/'integrity_audit.json').write_text(json.dumps(outjson,ensure_ascii=False,indent=2,default=dict))
 with (out/'labeled_features.jsonl').open('w') as f:
  for x in rows:f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
 (out/'labeled_features.sha256').write_text(hashlib.sha256((out/'labeled_features.jsonl').read_bytes()).hexdigest()+'\n')
 # checkpoint
 (out/'CHECKPOINT.json').write_text(json.dumps({'integrity_sha256':hashlib.sha256((out/'integrity_audit.json').read_bytes()).hexdigest(),'features_sha256':hashlib.sha256((out/'labeled_features.jsonl').read_bytes()).hexdigest(),'parser_version':'v1_strict_numeric_unit_confidence','label_blind_construction':True},indent=2))
 print(json.dumps(outjson,ensure_ascii=False,indent=2,default=dict))
if __name__=='__main__':main()
