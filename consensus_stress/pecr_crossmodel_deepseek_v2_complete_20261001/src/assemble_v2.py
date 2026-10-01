#!/usr/bin/env python3
"""Assemble immutable V1 + V2-backfill into a hash-chained merged ledger."""
import datetime, hashlib, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, '/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_crossmodel_deepseek_v1_20261001/src')
from run_deepseek_collection import build_slots, sha

ROOT=Path('/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call')
V1=ROOT/'pecr_crossmodel_deepseek_v1_20261001'
V2=ROOT/'pecr_crossmodel_deepseek_v2_complete_20261001'
MAN=ROOT/'pecr_bidirectional_development_v1_20260928/data/construction_manifest_dev_train.jsonl'

def verify_chain(rows):
    prev='GENESIS'; errors=[]
    for lineno,r in enumerate(rows,1):
        if r.get('previous_record_hash') != prev: errors.append([lineno,'previous_hash'])
        body={k:v for k,v in r.items() if k!='record_hash'}
        if sha(body) != r.get('record_hash'): errors.append([lineno,'record_hash'])
        prev=r.get('record_hash')
    return prev,errors

rows,slots=build_slots(MAN,20260928)
assert len(rows)==2225 and len(slots)==6675
v1=[json.loads(x) for x in open(V1/'data/full_dev/raw_ledger_full_dev.jsonl')]
assert len(v1)==6675
v1_by_slot={r['slot']:r for r in v1}
h,errs=verify_chain(v1); assert not errs and h=='5bec6a0d4f08c264c062bf69adbcb62160e1cda8f84ca8988de56d967c0d994d'
eligible={r['slot'] for r in v1 if r.get('http_status') in (429,402)}
assert len(eligible)==2682
v2=[]
for j in slots:
    if j['slot'] not in eligible:
        continue
    p=V2/'data/v2_responses'/f"slot_{j['slot']:05d}.json"
    assert p.exists(), f'missing V2 slot {j["slot"]}'
    r=json.load(open(p)); assert r['slot']==j['slot'] and r.get('v2_backfill') is True
    assert r.get('v1_http_status') == v1_by_slot[j['slot']].get('http_status')
    v2.append(r)
assert len(v2)==2682
v2_by_slot={r['slot']:r for r in v2}
merged=[]
for j in slots:
    old=v1_by_slot[j['slot']]
    merged.append(old if old.get('http_status')==200 else v2_by_slot[j['slot']])
assert len(merged)==6675
prev='GENESIS'; errors=[]
with open(V2/'data/merged_ledger_v2.jsonl','w') as out:
    for r in merged:
        r['previous_record_hash']=prev
        r['record_hash']=sha({k:v for k,v in r.items() if k!='record_hash'})
        prev=r['record_hash']; out.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
h,errors=verify_chain(merged)
counts=Counter('http_200' if r.get('http_status')==200 else 'http_429' if r.get('http_status')==429 else 'http_402' if r.get('http_status')==402 else 'other' for r in merged)
json_valid=sum('parsed_json' in r for r in merged)
status={'ledger':'data/merged_ledger_v2.jsonl','n_records':len(merged),'counts':dict(counts),'json_valid':json_valid,'chain_head':prev,'chain_errors':errors,'v1_source_records':6675,'v2_backfill_records':len(v2),'v1_http200_preserved':sum(r.get('http_status')==200 for r in v1),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(V2/'data/MERGE_STATUS_V2.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2))
if errors or counts['other']:
    raise SystemExit(1)
