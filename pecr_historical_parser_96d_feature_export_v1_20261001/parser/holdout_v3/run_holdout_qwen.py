#!/usr/bin/env python3
from __future__ import annotations
import argparse, fcntl, hashlib, json, math, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests
ROOT=Path(__file__).resolve().parents[1]; MANIFEST=ROOT/'data/HOLDOUT_MANIFEST_SEALED.jsonl'; FRAME=ROOT/'data/HOLDOUT_FRAME_IDS_V1.jsonl'; LEDGER=ROOT/'data/raw_ledger_v3.jsonl'
ENDPOINT='http://127.0.0.1:31518/v1/chat/completions'; MODEL='Qwen3.5-4B'; PARAMS={'temperature':0,'top_p':1,'max_tokens':384,'stream':False,'response_format':{'type':'json_object'}}
SYSTEM=('You answer quantitative financial questions from only the supplied question and evidence. Do not use outside knowledge. Do not reveal chain-of-thought. Return exactly one JSON object with keys: answer_value, unit, confidence, supporting_evidence. answer_value must be a concise numeric answer as a string (keep signs and decimal precision); unit must be a short string or null; confidence must be a number from 0 to 1; supporting_evidence must be an array of at most three short verbatim snippets copied from the supplied evidence. If the evidence is insufficient, set answer_value to an empty string, unit to null, confidence to 0, and supporting_evidence to []. Do not add other keys or markdown.')
MANIFEST_SHA='293ff0891de7a9f4c8b283c55cd3eddd0a95d4fa62d12bd46c255ae3de0aaa2f'; MAX_REQUESTS=1130; PREV='GENESIS'; _NUM=re.compile(r'^\s*(?:\(\s*)?[-+]?\s*\$?\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*%?\s*\)?\s*$')
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def canon(x:Any)->bytes:return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def utc()->str:return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def parse_num(v):
 if not isinstance(v,(str,int,float)) or isinstance(v,bool):return None
 s=str(v).strip()
 if not _NUM.fullmatch(s):return None
 neg=s.startswith('(') and s.endswith(')');pct='%' in s;t=s.replace('$','').replace(',','').replace('%','').replace('(','').replace(')','').strip()
 try:x=float(t)
 except:return None
 if neg:x=-abs(x)
 return (x,pct) if math.isfinite(x) else None
def parse_content(content):
 out={'valid':False,'errors':[]}
 try:o=json.loads(content)
 except:out['errors']=['invalid_json'];return out
 if not isinstance(o,dict):out['errors']=['not_object'];return out
 if set(o)!={'answer_value','unit','confidence','supporting_evidence'}:out['errors'].append('wrong_schema_keys')
 num=parse_num(o.get('answer_value'))
 if num is None or not str(o.get('answer_value','')).strip():out['errors'].append('invalid_answer_value')
 u=o.get('unit')
 if u is not None and not isinstance(u,str):out['errors'].append('invalid_unit')
 c=o.get('confidence')
 if isinstance(c,bool) or not isinstance(c,(int,float)) or not math.isfinite(float(c)) or not 0<=float(c)<=1:out['errors'].append('invalid_confidence')
 ev=o.get('supporting_evidence')
 if not isinstance(ev,list) or len(ev)>3 or not all(isinstance(x,str) for x in ev):out['errors'].append('invalid_supporting_evidence')
 if not out['errors']:out.update(valid=True,parsed=o,numeric_value=num[0],is_percent=num[1],normalized_unit=None if u is None else ' '.join(u.lower().split()))
 return out
def relation_score(a,b,expected):
 if not a.get('valid') or not b.get('valid'):return {'status':'unscorable_invalid_answer'}
 if a['normalized_unit']!=b['normalized_unit'] or a['is_percent']!=b['is_percent']:return {'status':'unscorable_unit_mismatch'}
 d=b['numeric_value']-a['numeric_value'];eps=1e-8*max(1.0,abs(a['numeric_value']));sign='up' if d>eps else ('down' if d<-eps else 'tie')
 return {'status':'scorable','response_delta':d,'response_direction':sign,'expected_direction':expected,'teacher_relation_risk':int(sign!=expected)}
def load_rows():
 raw=MANIFEST.read_bytes();mh=sha(raw)
 if mh!=MANIFEST_SHA:raise RuntimeError('manifest_hash_mismatch:'+mh)
 rows=[json.loads(x) for x in raw.splitlines() if x.strip() and json.loads(x).get('partition')=='dev_holdout'];ids=[json.loads(x)['id'] for x in FRAME.read_text().splitlines() if x.strip()]
 if len(rows)!=565 or ids!=[r['id'] for r in rows]:raise RuntimeError('frame_order_or_ids_mismatch')
 if any(r.get('status') != 'mechanically_aligned_program_operand_and_table_cell; semantic validity unverified' for r in rows): raise RuntimeError('unexpected_manifest_status')
 if any(r.get('program_conditioned_direction') not in ('up','down') for r in rows): raise RuntimeError('invalid_expected_direction')
 return rows,mh
def render(r,w):
 if w not in ('original','mutated'):raise ValueError('invalid_world')
 key='table_original' if w=='original' else 'table_mutated';allow={'question':r['question'],'pre_text':r.get('pre_text',[]),'table':r[key],'post_text':r.get('post_text',[])}
 def check(v):
  if isinstance(v,dict):raise ValueError('nested_dict_not_allowed')
  if isinstance(v,list):
   for z in v:check(z)
  elif not isinstance(v,(str,int,float,bool,type(None))):raise ValueError('unsupported_input_type')
 for v in allow.values():check(v)
 prompt='Answer the question using the evidence below. The answer may require arithmetic. Return only the required JSON object.\n\nQUESTION:\n'+allow['question']+'\n\nPRE-TEXT:\n'+'\n'.join(map(str,allow['pre_text']))+'\n\nTABLE (JSON):\n'+json.dumps(allow['table'],ensure_ascii=False,separators=(',',':'))+'\n\nPOST-TEXT:\n'+'\n'.join(map(str,allow['post_text']))
 return prompt,allow
def record_hash(rec):x=dict(rec);x.pop('record_hash',None);return sha(canon(x))
def append(rec):
 global PREV
 rec['previous_record_hash']=PREV;rec['record_hash']=record_hash(rec);line=canon(rec)+b'\n'
 with LEDGER.open('ab',buffering=0) as f:f.write(line);os.fsync(f.fileno())
 with LEDGER.open('rb') as f:f.seek(-len(line),os.SEEK_END);saved=json.loads(f.readline())
 if saved['record_hash']!=record_hash(saved) or saved['previous_record_hash']!=PREV:raise RuntimeError('ledger_readback_integrity_failure')
 PREV=rec['record_hash']
def call(slot,r,w,mh):
 prompt,a=render(r,w);req={'model':MODEL,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],**PARAMS};rq=sha(canon(req));aid=f'slot-{slot:04d}'
 append({'attempt_id':aid,'slot':slot,'item_id':r['id'],'world':w,'utc_started':utc(),'endpoint':ENDPOINT,'model_requested':MODEL,'request':req,'request_sha256':rq,'allowlist_payload_sha256':sha(canon(a)),'manifest_sha256':mh,'status':'started'})
 s=requests.Session();s.trust_env=False
 try:resp=s.post(ENDPOINT,json=req,timeout=(10,180))
 except Exception as e:append({'attempt_id':aid,'slot':slot,'item_id':r['id'],'world':w,'status':'transport_failure_stop','error_type':type(e).__name__,'error':str(e)[:500],'utc_finished':utc()});raise
 fin={'attempt_id':aid,'slot':slot,'item_id':r['id'],'world':w,'utc_finished':utc(),'http_status':resp.status_code,'raw_response_text':resp.text,'response_sha256':sha(resp.content),'request_sha256':rq}
 if resp.status_code!=200:fin['status']='http_failure_stop';append(fin);raise RuntimeError(f'http_failure_{resp.status_code}')
 try:data=resp.json()
 except:fin['status']='invalid_api_envelope_json_stop';append(fin);raise RuntimeError('invalid_api_envelope')
 fin['response_model']=data.get('model');fin['usage']=data.get('usage')
 if fin['response_model']!=MODEL:fin['status']='model_identity_mismatch_stop';append(fin);raise RuntimeError('model_identity_mismatch')
 choices=data.get('choices')
 if not isinstance(choices,list) or len(choices)!=1:fin['status']='invalid_choice_count_stop';append(fin);raise RuntimeError('invalid_choices')
 content=(choices[0].get('message') or {}).get('content')
 if not isinstance(content,str):fin['status']='invalid_content_type_stop';append(fin);raise RuntimeError('invalid_content')
 parsed=parse_content(content);fin['parsed']=parsed;fin['finish_reason']=choices[0].get('finish_reason');fin['status']='parsed_valid' if parsed['valid'] else 'parse_invalid_continue';append(fin);return parsed
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
 if not LEDGER.exists(): LEDGER.touch()
 if LEDGER.stat().st_size:raise RuntimeError('ledger_not_empty_no_resume_or_retry')
 if MAX_REQUESTS != 1130: raise RuntimeError('budget_contract_mismatch')
 rows,mh=load_rows();
 if LEDGER.read_bytes(): raise RuntimeError('nonempty_ledger_no_resume_or_retry')
 lock=(ROOT/'runner.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);slots=[(r,w) for r in rows for w in ('original','mutated')]
 if args.dry_run:
  for i,(r,w) in enumerate(slots,1):req,_= (lambda z:(z[0],z[1]))( (lambda p,a:({'model':MODEL,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':p}],**PARAMS},a))(*render(r,w)) );print(json.dumps({'slot':i,'id':r['id'],'world':w,'request_sha256':sha(canon(req)),'prompt_chars':len(req['messages'][1]['content'])},ensure_ascii=False))
  return
 for i,(r,w) in enumerate(slots,1):
  call(i,r,w,mh)
  if i==2:print('canary_pair_passed; continuing fixed batch',flush=True)
 print(f'collection_done requests={len(slots)} rows={len(rows)} manifest_sha256={mh}',flush=True)
if __name__=='__main__':main()
