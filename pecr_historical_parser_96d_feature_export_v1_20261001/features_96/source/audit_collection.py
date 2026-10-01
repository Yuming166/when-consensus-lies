#!/usr/bin/env python3
"""V2 correction of the label-blind collection audit; preserves V1 artifacts."""
import argparse,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def rec_hash(r):
 x=dict(r);x.pop('record_hash',None);return sha(canon(x))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ledger',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 mp=Path(a.manifest);lp=Path(a.ledger); mh=sha(mp.read_bytes()); rows=[json.loads(x) for x in mp.read_text().splitlines() if x.strip()];rows=[r for r in rows if r.get('partition')=='dev_train']
 errors=[]
 if len(rows)!=2241:errors.append(f'candidate_count:{len(rows)}')
 ids=[r.get('id') for r in rows]
 if len(set(ids))!=len(ids) or any(not x for x in ids):errors.append('manifest_duplicate_or_missing_id')
 if any(not r.get('source_group') for r in rows):errors.append('manifest_missing_source_group')
 records=[];prev='GENESIS'; malformed=0
 with lp.open(encoding='utf-8') as f:
  for ln,line in enumerate(f,1):
   try:r=json.loads(line)
   except Exception: malformed+=1;errors.append(f'ledger_json_line:{ln}');continue
   if r.get('previous_record_hash')!=prev or r.get('record_hash')!=rec_hash(r):errors.append(f'ledger_hash_chain:{ln}')
   prev=r.get('record_hash');records.append(r)
 if malformed:errors.append(f'malformed_lines:{malformed}')
 if len(records)!=8964:errors.append(f'ledger_records:{len(records)}')
 starts=[r for r in records if r.get('status')=='started']; fins=[r for r in records if r.get('status') in {'parsed_valid','parse_invalid_continue'}]
 if len(starts)!=4482 or len(fins)!=4482:errors.append('started_or_completed_count')
 byslot=defaultdict(list)
 for r in records:byslot[r.get('slot')].append(r)
 if set(byslot)!=set(range(1,4483)):errors.append('slot_set')
 parsed={}; status=Counter(); parse_errors=Counter()
 for idx,row in enumerate(rows):
  for j,world in enumerate(('original','mutated')):
   slot=2*idx+j+1; pair=byslot.get(slot,[])
   if len(pair)!=2:errors.append(f'slot_multiplicity:{slot}');continue
   st,fin=pair
   if st.get('status')!='started' or fin.get('status') not in {'parsed_valid','parse_invalid_continue'}:errors.append(f'slot_status:{slot}')
   for rec in (st,fin):
    if rec.get('slot')!=slot or rec.get('item_id')!=row['id'] or rec.get('world')!=world:errors.append(f'slot_mapping:{slot}')
   if st.get('candidate_manifest_sha256')!=mh:errors.append(f'manifest_hash:{slot}')
   req=st.get('request')
   if not isinstance(req,dict) or sha(canon(req))!=st.get('request_sha256') or fin.get('request_sha256')!=st.get('request_sha256'):errors.append(f'request_hash:{slot}')
   if st.get('model_requested')!='Qwen3.5-4B' or not str(st.get('endpoint','')).startswith('http://127.0.0.1:31518/'):errors.append(f'model_or_endpoint:{slot}')
   if fin.get('http_status')!=200 or fin.get('response_model')!='Qwen3.5-4B':errors.append(f'response_identity:{slot}')
   txt=fin.get('raw_response_text','')
   if not isinstance(txt,str) or sha(txt.encode())!=fin.get('response_sha256'):errors.append(f'response_hash:{slot}')
   p=fin.get('parsed') or {};parsed[(row['id'],world)]=p;status[fin.get('status')]+=1
   if p.get('valid'):
    try:
     if not math.isfinite(float(p['numeric_value'])):raise ValueError
    except Exception:errors.append(f'parsed_numeric_invalid:{slot}')
   else:
    for er in p.get('errors',[]):parse_errors[str(er)]+=1
 both=compatible=0;incompatible=0;world_valid=Counter()
 for row in rows:
  o=parsed.get((row['id'],'original'),{});m=parsed.get((row['id'],'mutated'),{})
  if o.get('valid'):world_valid['original']+=1
  if m.get('valid'):world_valid['mutated']+=1
  if o.get('valid') and m.get('valid'):
   both+=1
   # IMPORTANT: units are on the outer parser result; do not shadow it with nested parsed JSON.
   same_unit=o.get('normalized_unit')==m.get('normalized_unit')
   same_scale=bool(o.get('is_percent'))==bool(m.get('is_percent'))
   if same_unit and same_scale:compatible+=1
   else:incompatible+=1
 result={'audit_version':'paired_collection_label_blind_audit_v2_corrected','manifest_sha256':mh,'ledger_sha256':sha(lp.read_bytes()),
  'candidate_rows':len(rows),'source_groups':len({r['source_group'] for r in rows}),'record_count':len(records),'attempted_slots':len(starts),'completed_slots':len(fins),
  'response_status_counts':dict(status),'parse_error_counts':dict(parse_errors),'parsed_valid_by_world':dict(world_valid),'both_world_valid':both,
  'unit_and_percent_compatible_pairs':compatible,'unit_or_percent_incompatible_pairs':incompatible,'chain_error_count':sum('ledger_hash_chain:' in e for e in errors),
  'malformed_json_lines':malformed,'audit_errors':errors,'integrity_gate_pass':not errors,'label_values_read':False,'correctness_metrics_computed':False,
  'compatibility_definition':'both strict parsed; normalized_unit exact equality including null; is_percent boolean exact equality; no conversion'}
 Path(a.out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,indent=2,ensure_ascii=False));raise SystemExit(0 if not errors else 2)
if __name__=='__main__':main()
