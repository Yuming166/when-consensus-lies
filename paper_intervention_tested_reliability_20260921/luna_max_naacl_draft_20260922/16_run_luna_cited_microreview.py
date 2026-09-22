#!/usr/bin/env python3
import json,time,urllib.request,urllib.error,tomllib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
CFG=Path('/home/gaoym/.codex/config.toml')
DRAFT=HERE/'12_NAACL_FIRST_DRAFT_CITED.md'
OUT=HERE/'16_LUNA_MAX_CITED_MICROREVIEW.md'
AUDIT=HERE/'16_LUNA_MAX_CITED_MICROREVIEW.json'
def extract(obj):
    t=obj.get('output_text') if isinstance(obj,dict) else ''
    if isinstance(t,str) and t.strip(): return t.strip()
    out=[]
    for item in obj.get('output',[]) if isinstance(obj,dict) else []:
        for c in item.get('content',[]) if isinstance(item,dict) else []:
            if isinstance(c,dict) and isinstance(c.get('text'),str): out.append(c['text'])
    return '\n'.join(out).strip()
cfg=tomllib.loads(CFG.read_text()); p=cfg['model_providers']['custom']
draft=DRAFT.read_text()
instructions='''You are a senior NAACL reviewer doing a compact final pass over a cited first draft. Return at most 12 high-value findings, each tagged P0/P1/P2. Check only: (1) whether the central contribution and paper title are clear; (2) whether any sentence overclaims beyond the frozen evidence; (3) whether the ConvFinQA Qwen missing-probe result is stated as the primary new result; (4) whether citation placement is adequate and no bibliography claim is invented; (5) whether the paper needs one or two surgical edits before ACL LaTeX conversion. Do not rewrite the paper, do not invent results, and do not request new experiments. If no P0/P1 issues remain, say so explicitly.'''
payload={'model':cfg.get('model','gpt-5.6-luna'),'instructions':instructions,'input':'CITED FIRST DRAFT\n\n'+draft,'reasoning':{'effort':'max'},'max_output_tokens':3500,'temperature':0.1,'store':False}
raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(); req=urllib.request.Request(p['base_url'].rstrip('/')+'/responses',data=raw,headers={'Authorization':'Bearer '+p['experimental_bearer_token'],'Content-Type':'application/json','Accept':'application/json'},method='POST')
t0=time.time(); code=None; body=b''; err=None
try:
 with urllib.request.urlopen(req,timeout=1200) as r: body=r.read(); code=r.status
except urllib.error.HTTPError as e: body=e.read(); code=e.code
except Exception as e: err=f'{type(e).__name__}: {e}'
try: obj=json.loads(body)
except Exception: obj={}
text=extract(obj)
AUDIT.write_text(json.dumps({'timestamp_utc':datetime.now(timezone.utc).isoformat(),'http_code':code,'latency_seconds':round(time.time()-t0,2),'model':cfg.get('model'),'status':obj.get('status'),'response_id':obj.get('id'),'output_chars':len(text),'success':bool(code==200 and text),'error':err,'body_prefix':body[:500].decode('utf-8','replace')},ensure_ascii=False,indent=2)+'\n')
if code==200 and text: OUT.write_text(text+'\n'); print(json.dumps({'status':'complete','output':str(OUT),'chars':len(text),'latency_seconds':round(time.time()-t0,2)},ensure_ascii=False))
else: print(json.dumps({'status':'failed','http_code':code,'error':err,'body_prefix':body[:500].decode('utf-8','replace')},ensure_ascii=False))
