#!/usr/bin/env python3
"""DeepSeek cross-model PECR collection.

Frozen protocol (PRE_CALL_PLAN.md v1): same manifest, same seed-20260928 order,
byte-identical prompts except the model field, temperature=0, max_tokens=384,
single attempt per (item, world), no retries/backfill.

Two phases for crash safety:
  collect : concurrent HTTP calls -> data/full_dev/responses/slot_XXXXX.json
            (resumable: existing slot files are skipped)
  assemble: hash-chained append-only ledger in slot order -> raw_ledger_full_dev.jsonl
"""
import argparse, json, hashlib, datetime, os, random, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def sha(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def table_text(t): return '\n'.join(' | '.join(map(str,r)) for r in t)

SYS="You answer quantitative financial questions from only the supplied question and evidence. Do not use outside knowledge. Do not reveal chain-of-thought. Return exactly one JSON object with keys: answer_value, unit, confidence, supporting_evidence. answer_value must be a concise numeric answer as a string (keep signs and decimal precision); unit must be a short string or null; confidence must be a number from 0 to 1; supporting_evidence must be an array of at most three short verbatim snippets copied from the supplied evidence. If the evidence is insufficient, set answer_value to an empty string, unit to null, confidence to 0, and supporting_evidence to []. Do not add other keys or markdown."

MAX_TOKENS=8192  # Amendments V1+V2
REASONING_EFFORT='low'  # Amendment V2: see protocol/PROTOCOL_AMENDMENT_V2_reasoning_effort.md
def make_req(r,w,model):
    t=r['table_original'] if w=='original' else r['table_mutated'] if w=='positive' else r['bidirectional']['reverse_table']
    content=f"Answer the question using the evidence below. The answer may require arithmetic. Return only the required JSON object.\n\nQUESTION:\n{r['question']}\n\nPRE-TEXT:\n{' '.join(r.get('pre_text',[]))}\n\nTABLE:\n{table_text(t)}\n\nPOST-TEXT:\n{' '.join(r.get('post_text',[]))}"
    return {'model':model,'messages':[{'role':'system','content':SYS},{'role':'user',content:content} if False else {'role':'user','content':content}],'temperature':0,'max_tokens':MAX_TOKENS,'reasoning_effort':REASONING_EFFORT}

def build_slots(manifest, seed, limit=0):
    rows=[json.loads(l) for l in open(manifest) if l.strip() and json.loads(l).get('bidirectional',{}).get('construction_status')=='valid_candidate']
    random.Random(seed).shuffle(rows)
    if limit: rows=rows[:limit]
    slots=[]
    s=0
    for r in rows:
        for w in ('original','positive','negative'):
            s+=1; slots.append({'slot':s,'item_id':r['id'],'source_group':r['source_group'],'world':w,'row':r})
    return rows, slots

def do_call(job, endpoint, key, model, timeout=180):
    req=make_req(job['row'], job['world'], model)
    rec={'slot':job['slot'],'attempt_id':f"deepseek-full-{job['slot']:05d}",'item_id':job['item_id'],
         'source_group':job['source_group'],'world':job['world'],'endpoint':endpoint,'model_requested':model,
         'request':req,'request_sha256':sha(req),
         'utc_started':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        resp=requests.post(endpoint,json=req,timeout=timeout,
                           headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'})
        rec['http_status']=resp.status_code; rec['response_text']=resp.text
        rec['response_sha256']=hashlib.sha256(resp.content).hexdigest()
        try:
            body=resp.json(); rec['assistant_content']=body['choices'][0]['message']['content']
            if 'usage' in body: rec['usage']=body['usage']
            if 'model' in body: rec['model_reported']=body['model']
            try: rec['parsed_json']=json.loads(rec['assistant_content'])
            except Exception: pass
        except Exception as e: rec['response_parse_error']=repr(e)
    except Exception as e:
        rec['request_error']=repr(e)
    rec['utc_finished']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    return rec

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',required=True); ap.add_argument('--outdir',required=True)
    ap.add_argument('--endpoint',default='https://api.deepseek.com/v1/chat/completions')
    ap.add_argument('--key-env',default='DEEPSEEK_API_KEY')
    ap.add_argument('--model',default='deepseek-flash')
    ap.add_argument('--seed',type=int,default=20260928); ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--workers',type=int,default=16)
    ap.add_argument('--phase',choices=['collect','assemble'],default='collect')
    a=ap.parse_args()
    key=os.environ.get(a.key_env)
    if a.phase=='collect' and not key: raise SystemExit(f'missing env {a.key_env}')
    os.makedirs(a.outdir,exist_ok=True)
    respdir=os.path.join(a.outdir,'responses'); os.makedirs(respdir,exist_ok=True)
    rows, slots = build_slots(a.manifest, a.seed, a.limit)
    if a.phase=='collect':
        sel={'seed':a.seed,'n_items':len(rows),'n_requests':len(slots),'model':a.model,'endpoint':a.endpoint,
             'ids':[r['id'] for r in rows]}
        open(os.path.join(a.outdir,'selection_freeze.json'),'w').write(json.dumps(sel,ensure_ascii=False,indent=2))
        todo=[j for j in slots if not os.path.exists(os.path.join(respdir,f"slot_{j['slot']:05d}.json"))]
        print(json.dumps({'total_slots':len(slots),'todo':len(todo)}),flush=True)
        done=0; t0=time.time()
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs={ex.submit(do_call,j,a.endpoint,key,a.model):j for j in todo}
            for fut in as_completed(futs):
                j=futs[fut]
                try: rec=fut.result()
                except Exception as e:
                    rec={'slot':j['slot'],'attempt_id':f"deepseek-full-{j['slot']:05d}",'item_id':j['item_id'],
                         'source_group':j['source_group'],'world':j['world'],'endpoint':a.endpoint,
                         'model_requested':a.model,'driver_error':repr(e),
                         'utc_finished':datetime.datetime.now(datetime.timezone.utc).isoformat()}
                with open(os.path.join(respdir,f"slot_{j['slot']:05d}.json"),'w') as f:
                    f.write(json.dumps(rec,ensure_ascii=False,separators=(',',':'))+'\n')
                done+=1
                if done%100==0:
                    el=time.time()-t0
                    print(json.dumps({'collected':done,'of':len(todo),'elapsed_s':round(el,1),'eta_s':round(el/max(done,1)*(len(todo)-done),1)}),flush=True)
        print(json.dumps({'collect_finished':True,'collected':done}),flush=True)
    else:  # assemble
        ledger=os.path.join(a.outdir,'raw_ledger_full_dev.jsonl')
        prev='GENESIS'; counts=Counter(); missing=[]
        with open(ledger,'w') as out:
            for j in slots:
                p=os.path.join(respdir,f"slot_{j['slot']:05d}.json")
                if not os.path.exists(p): missing.append(j['slot']); continue
                rec=json.load(open(p))
                rec.pop('row',None)
                rec['previous_record_hash']=prev
                hs=rec.get('http_status'); counts[f'http_{hs}']+=1
                if 'parsed_json' in rec: counts['json_valid']+=1
                elif 'assistant_content' in rec: counts['json_invalid']+=1
                if 'request_error' in rec or 'driver_error' in rec: counts['request_error']+=1
                rec['record_hash']=sha({k:v for k,v in rec.items() if k!='record_hash'})
                prev=rec['record_hash']
                out.write(json.dumps(rec,ensure_ascii=False,separators=(',',':'))+'\n')
        summary={'counts':dict(counts),'missing_slots':missing,'ledger':ledger,'chain_head':prev,
                 'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        open(os.path.join(a.outdir,'collection_status.json'),'w').write(json.dumps(summary,ensure_ascii=False,indent=2))
        print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
