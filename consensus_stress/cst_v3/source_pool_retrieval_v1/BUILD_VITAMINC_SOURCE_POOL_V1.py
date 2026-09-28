"""Zero-call VitaminC source-pool retrieval for all inherited CST attempts."""
from pathlib import Path
import csv, json, hashlib, re
from collections import Counter, defaultdict
BASE=Path('/home/gaoym')
DATA=BASE/'when-consensus-lies-publish-20260911/data/benchmarks/vitaminc/test.jsonl'
SEL=BASE/'when-consensus-lies-publish-20260911/consensus_stress/round3/selection_manifest.json'
EXC=BASE/'cst_zero_call_upgrade_20260928/SOURCE_GROUP_EXCLUSION_AUDIT.json'
ATT=BASE/'cst_zero_call_upgrade_20260928/candidate_blind_review_v1/CANDIDATE_ATTEMPTS.csv'
OUT=Path(__file__).resolve().parent

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def norm(s): return re.sub(r'\s+',' ',(s or '').strip())
def compact_text(x): return norm(x)
def read_jsonl(path):
    with open(path,encoding='utf-8') as f: return [json.loads(line) for line in f]
def input_text(claim, a_id, a_text, append_label, append_id, append_text):
    a=f'[A evidence_id={a_id}]\n{a_text}' if a_id and a_text else '[A: MISSING]'
    b=f'[{append_label} evidence_id={append_id}]\n{append_text}' if append_id and append_text else f'[{append_label}: MISSING]'
    return f'PROPOSITION:\n{claim}\n\nEVIDENCE:\n{a}\n\n{b}'

selection=json.load(open(SEL,encoding='utf-8')); exclusion=json.load(open(EXC,encoding='utf-8'))
actual_data_hash=sha256(DATA); actual_sel_hash=sha256(SEL); actual_exc_hash=sha256(EXC)
assert actual_data_hash==selection['dataset_sha256']
assert actual_data_hash==exclusion['source_dataset_sha256']
assert actual_sel_hash==exclusion['selection_manifest_sha256']
source_groups=set(exclusion['candidate_groups'])
assert source_groups==set(exclusion['candidate_group_to_page'])
all_rows=read_jsonl(DATA); page_by_group={g: exclusion['candidate_group_to_page'][g][0] for g in source_groups}
pool=[x for x in all_rows if x.get('group') in source_groups and x.get('page')==page_by_group[x['group']]]
by_group=defaultdict(list); by_id={}
for x in pool: by_group[x['group']].append(x); by_id[x['unique_id']]=x
attempts=list(csv.DictReader(open(ATT,encoding='utf-8')))
assert len(attempts)==34 and set(r['source_group'] for r in attempts)==source_groups
records=[]; outputs=[]; failures=[]
for a in attempts:
    group=a['source_group']; claim=a['original_claim']; aid=a['original_evidence_id']; cid=a['counter_evidence_id']; page=exclusion['candidate_group_to_page'][group][0]
    group_rows=by_group[group]; original=by_id.get(aid); counter=by_id.get(cid); rowfail=[]
    if original is None: rowfail.append('ORIGINAL_EVIDENCE_NOT_IN_FINAL_SNAPSHOT')
    if counter is None: rowfail.append('COUNTER_EVIDENCE_NOT_IN_FINAL_SNAPSHOT')
    if original and compact_text(original.get('claim')) != compact_text(claim): rowfail.append('ORIGINAL_CLAIM_MISMATCH')
    if counter and compact_text(counter.get('claim')) != compact_text(claim): rowfail.append('COUNTER_CLAIM_MISMATCH')
    support=[]; counter_candidates=[]
    for x in group_rows:
        if compact_text(x.get('claim')) != compact_text(claim): continue
        # A is always retained, so it cannot also be the appended material.
        # The inherited opposite-polarity evidence may serve one directional role:
        # for a refute-A item it is support material; for a support-A item it is counter material.
        if x['unique_id'] == aid: continue
        if x.get('label')=='SUPPORTS': support.append(x)
        if x.get('label')=='REFUTES': counter_candidates.append(x)
    neutral=[x for x in group_rows if x['unique_id'] not in {aid,cid} and compact_text(x.get('claim')) != compact_text(claim)]
    alen=len(compact_text(original.get('evidence','')) if original else '')
    neutral.sort(key=lambda x:(abs(len(compact_text(x.get('evidence','')))-alen),x['unique_id']))
    support.sort(key=lambda x:(abs(len(compact_text(x.get('evidence','')))-alen),x['unique_id']))
    counter_candidates.sort(key=lambda x:(0 if x['unique_id']==cid else 1,abs(len(compact_text(x.get('evidence','')))-alen),x['unique_id']))
    role_lists={'neutral':neutral,'support':support,'counter':counter_candidates}; selected={r:(v[0] if v else None) for r,v in role_lists.items()}
    for role,vals in role_lists.items():
        if not vals: rowfail.append(f'{role.upper()}_MATERIAL_NOT_RETRIEVED')
    if rowfail: failures.append({'item_id':a['item_id'],'source_group':group,'failure_codes':rowfail})
    for role,vals in role_lists.items():
        for rank,x in enumerate(vals,1):
            records.append({'item_id':a['item_id'],'source_group':group,'page':page,'role':role,'rank':rank,'selected':rank==1,'candidate_unique_id':x['unique_id'],'candidate_case_id':x['case_id'],'candidate_claim':x['claim'],'candidate_label_from_snapshot':x['label'],'candidate_evidence':x['evidence'],'candidate_wiki_revision_id':x.get('wiki_revision_id'),'retrieval_basis':('same_group_same_page_same_claim_and_snapshot_relation' if role in {'support','counter'} else 'same_group_same_page_different_claim_proposition_neutrality_unverified'),'semantic_status':'PENDING_TWO_HUMAN_REVIEWERS'})
    def pick(role):
        x=selected[role]; return (x['unique_id'],x['evidence']) if x else ('MISSING','MISSING')
    nid,nt=pick('neutral'); sid,st=pick('support'); xid,xt=pick('counter'); at=original or {'unique_id':'MISSING','evidence':'MISSING'}
    outputs.append({'item_id':a['item_id'],'source_group':group,'page':page,'pair_id':a['pair_id'],'proposition':claim,'A_evidence_id':aid if original else 'MISSING','A_evidence_text':at.get('evidence','MISSING'),'neutral_evidence_id':nid,'neutral_evidence_text':nt,'support_evidence_id':sid,'support_evidence_text':st,'counter_evidence_id':xid,'counter_evidence_text':xt,'AA_full_input':input_text(claim,aid,at.get('evidence'),'AA_REPEAT_CONTRACT','AA_REPEAT','Repeat A; no new factual content.'),'neutral_full_input':input_text(claim,aid,at.get('evidence'),'NEUTRAL_APPEND',nid,nt),'support_full_input':input_text(claim,aid,at.get('evidence'),'SUPPORT_APPEND',sid,st),'counter_full_input':input_text(claim,aid,at.get('evidence'),'COUNTER_APPEND',xid,xt),'neutral_candidate_count':len(neutral),'support_candidate_count':len(support),'counter_candidate_count':len(counter_candidates),'retrieval_failure_codes':'|'.join(rowfail) if rowfail else '','human_review_status':'PENDING_TWO_INDEPENDENT_REVIEWERS','tri_state_status':'NOT_INFERRED_FROM_SNAPSHOT'})
with (OUT/'VITAMINC_FIXED_SOURCE_POOL.jsonl').open('w',encoding='utf-8') as f:
    for x in pool: f.write(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n')
with (OUT/'ATTEMPT_SOURCE_RECORDS_V1.jsonl').open('w',encoding='utf-8') as f:
    for x in records: f.write(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n')
fields=list(outputs[0])
with (OUT/'FOUR_CONDITION_FULL_INPUTS_V1.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(outputs)
(OUT/'RETRIEVAL_FAILURES_V1.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n')
summary={'run_date':'2026-09-29','model_calls':0,'snapshot_path':str(DATA),'snapshot_sha256':actual_data_hash,'selection_manifest_path':str(SEL),'selection_manifest_sha256':actual_sel_hash,'historical_exclusion_path':str(EXC),'historical_exclusion_sha256':actual_exc_hash,'source_groups':sorted(source_groups),'source_group_count':len(source_groups),'fixed_pool_rows':len(pool),'attempt_rows':len(outputs),'attempt_groups':len(set(x['source_group'] for x in outputs)),'candidate_role_record_count':len(records),'rows_with_retrieval_failures':len(failures),'failure_code_counts':dict(Counter(code for x in failures for code in x['failure_codes'])),'note':'Retrieval labels are mechanical provenance roles only. Neutrality, directional validity, conflict resolution, and final three-state targets require two independent human reviews of the complete inputs.'}
(OUT/'SOURCE_POOL_AUDIT_V1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
paths=[OUT/'VITAMINC_FIXED_SOURCE_POOL.jsonl',OUT/'ATTEMPT_SOURCE_RECORDS_V1.jsonl',OUT/'FOUR_CONDITION_FULL_INPUTS_V1.csv',OUT/'RETRIEVAL_FAILURES_V1.json',OUT/'SOURCE_POOL_AUDIT_V1.json']
with (OUT/'SHA256SUMS_SOURCE_POOL_V1.txt').open('w') as f:
    for p in paths: f.write(f'{sha256(p)}  {p.name}\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
