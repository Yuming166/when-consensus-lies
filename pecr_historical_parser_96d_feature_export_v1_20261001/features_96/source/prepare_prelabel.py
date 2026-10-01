#!/usr/bin/env python3
"""Create frozen label-blind targets/features/splits from sealed manifest+ledger only."""
import argparse, hashlib, json, math, re, sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from sklearn.model_selection import GroupKFold

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; SRC=ROOT/'src'
sys.path.insert(0,str(SRC))
from feature_builder import FrozenFeatureBuilder, GRAPH_FEATURE_NAMES

def sha(b): return hashlib.sha256(b).hexdigest()
def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def read_jsonl(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def write_jsonl(p, rows):
    with p.open('w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
def norm_surface(s): return re.sub(r'\s+',' ',str(s).strip().lower())
def sign_delta(delta, orig):
    tol=1e-8*max(1.,abs(float(orig)))
    return 0 if abs(delta)<=tol else (1 if delta>0 else -1)
def expected_sign(row):
    d=str(row.get('program_conditioned_direction','')).lower()
    return 1 if d=='up' else (-1 if d=='down' else 0)
def main():
    ap=argparse.ArgumentParser(); ap.parse_args()
    mpath=DATA/'candidate_manifest_sealed.jsonl'; lpath=DATA/'raw_ledger_sealed.jsonl'
    expected_m=(DATA/'candidate_manifest_sealed.sha256').read_text().split()[0]
    expected_l=(DATA/'raw_ledger_sealed.sha256').read_text().split()[0]
    if sha(mpath.read_bytes())!=expected_m or sha(lpath.read_bytes())!=expected_l: raise SystemExit('STOP sealed_input_hash_mismatch')
    audit=json.loads((DATA/'COLLECTION_AUDIT_V2_CORRECTED.json').read_text(encoding='utf-8'))
    if (audit.get('manifest_sha256')!=expected_m or audit.get('ledger_sha256')!=expected_l
        or not audit.get('integrity_gate_pass') or audit.get('audit_errors')
        or audit.get('attempted_slots')!=4482 or audit.get('completed_slots')!=4482
        or audit.get('unit_and_percent_compatible_pairs')!=1540
        or audit.get('unit_or_percent_incompatible_pairs')!=159):
        raise SystemExit('STOP corrected_collection_audit_missing_stale_or_invalid')
    m=[r for r in read_jsonl(mpath) if r.get('partition')=='dev_train']
    finals={}
    for x in read_jsonl(lpath):
        if x.get('status') in {'parsed_valid','parse_invalid_continue'}:
            key=(x.get('item_id'),x.get('world'))
            if key in finals: raise SystemExit(f'STOP duplicate_final_record:{key}')
            finals[key]=x
    if len(m)!=2241 or len(finals)!=4482: raise SystemExit('STOP cohort_or_slot_count')
    target_rows=[]; feature_records=[]; flow=[]
    for idx,row in enumerate(m):
        item=row['id']; group=row['source_group']; ro=finals.get((item,'original')); rm=finals.get((item,'mutated'))
        if not ro or not rm: raise SystemExit(f'STOP missing_fixed_pair:{item}')
        po=ro.get('parsed') or {}; pm=rm.get('parsed') or {}
        orig_valid=bool(po.get('valid')); mut_valid=bool(pm.get('valid'))
        original_resp=po.get('parsed') if orig_valid else None
        feature_records.append({'id':item,'source_group':group,'feature_record':{
            'question':row['question'],'pre_text':row.get('pre_text',[]),'table_original':row.get('table_original',[]),'post_text':row.get('post_text',[]),
            'original_response': original_resp if orig_valid else {'answer_value':'','unit':None,'confidence':0.0,'supporting_evidence':[]}}})
        reason=[]
        if not orig_valid: reason.append('original_parse_invalid')
        if not mut_valid: reason.append('mutated_parse_invalid')
        compatible=False; obs=None; relation=None; risk=None
        if orig_valid and mut_valid:
            uo=po.get('normalized_unit'); um=pm.get('normalized_unit'); so=bool(po.get('is_percent')); sm=bool(pm.get('is_percent'))
            compatible=(uo==um and so==sm)
            if not compatible: reason.append('unit_or_percent_incompatible')
            else:
                ov=float(po.get('numeric_value')); mv=float(pm.get('numeric_value'))
                if not math.isfinite(ov) or not math.isfinite(mv): reason.append('nonfinite_response_value')
                else:
                    obs=sign_delta(mv-ov,ov); es=expected_sign(row)
                    if es==0: reason.append('invalid_expected_direction')
                    else:
                        relation='invariant' if obs==0 else ('aligned' if obs==es else 'opposite')
                        risk=int(obs==0 or obs!=es)
        aligned=row.get('aligned_operand') or {}; literal=aligned.get('original_literal')
        span=aligned.get('span')
        source=' '.join([row['question'],' '.join(row.get('pre_text',[])),' '.join(' '.join(map(str,x)) for x in row.get('table_original',[])),' '.join(row.get('post_text',[]))])
        surface=norm_surface(literal) if literal is not None else ''
        occ=source.lower().count(surface) if surface else 0
        span_ok=isinstance(span,dict) and isinstance(span.get('start'),int) and isinstance(span.get('end'),int) and span['end']>span['start']
        try: construction_delta=float(row.get('absolute_delta'))
        except (TypeError,ValueError): construction_delta=float('nan')
        quality_ok=compatible and risk is not None and span_ok and math.isfinite(construction_delta) and construction_delta>0 and occ>=1
        if not span_ok: reason.append('ambiguous_or_invalid_operand_span')
        if not math.isfinite(construction_delta) or construction_delta<=0: reason.append('zero_or_nonfinite_construction_delta')
        if occ<1: reason.append('aligned_operand_surface_not_found')
        target_rows.append({'row_index':idx,'id':item,'source_group':group,'original_parse_valid':orig_valid,'mutated_parse_valid':mut_valid,
            'unit_percent_compatible':compatible,'pair_target_available':risk is not None,'target_missing_reasons':reason,
            'expected_sign':expected_sign(row),'observed_sign':obs,'relation_type':relation,'relation_risk':risk,
            'aligned_operand_occurrences_original':occ,'operand_span_valid':span_ok,'construction_delta_abs':construction_delta if math.isfinite(construction_delta) else None,
            'quality_eligible':bool(quality_ok),'quality_weight':(1.0/max(1,occ) if quality_ok else 0.0),
            'original_parse_reason':(po.get('errors') or []) if not orig_valid else [],'mutated_parse_reason':(pm.get('errors') or []) if not mut_valid else []})
        flow.append({'row_index':idx,'id':item,'source_group':group,'original_parse_valid':orig_valid,'mutated_parse_valid':mut_valid,'pair_target_available':risk is not None,
                     'unit_percent_compatible':compatible,'quality_eligible':bool(quality_ok),'target_missing_reasons':reason})
    # Build matrix, rejecting all non-original fields before feature code sees them.
    builder=FrozenFeatureBuilder(); X,G=builder.transform([r['feature_record'] for r in feature_records])
    np.savez_compressed(DATA/'features_prelabel.npz',X=X,graph=G)
    feat_meta=[{'row_index':r['row_index'],'id':r['id'],'source_group':r['source_group']} for r in target_rows]
    write_jsonl(DATA/'paired_targets_label_blind.jsonl',target_rows)
    write_jsonl(DATA/'student_inputs_allowlisted.jsonl',feature_records)
    write_jsonl(DATA/'candidate_flow_prelabel.jsonl',flow)
    write_jsonl(DATA/'feature_row_map.jsonl',feat_meta)
    # GroupKFold split map is generated without label values and persisted exactly.
    groups=np.asarray([x['source_group'] for x in target_rows]); n=len(groups)
    outer=np.full(n,-1,dtype=int); outer_splits=[]
    for k,(tr,te) in enumerate(GroupKFold(n_splits=5).split(np.zeros(n),groups=groups)):
        outer[te]=k
        outer_splits.append({'fold':k,'train_row_indices':tr.tolist(),'test_row_indices':te.tolist()})
    if (outer<0).any(): raise SystemExit('STOP incomplete_outer_split')
    inner=[]
    for o,sp in enumerate(outer_splits):
        tr=np.asarray(sp['train_row_indices']); gtr=groups[tr]
        for j,(it,iv) in enumerate(GroupKFold(n_splits=4).split(np.zeros(len(tr)),groups=gtr)):
            inner.append({'outer_fold':o,'inner_fold':j,'train_row_indices':tr[it].tolist(),'validation_row_indices':tr[iv].tolist()})
    split={'split_version':'source_group_nested_gkf_v1','seed':20260926,'outer_folds':outer_splits,'inner_folds':inner,
           'outer_fold_by_row':outer.tolist(),'group_count':len(set(groups)),'row_count':n}
    (DATA/'split_manifest_prelabel.json').write_text(json.dumps(split,sort_keys=True,separators=(',',':'))+'\n')
    (DATA/'feature_schema_96.json').write_text(json.dumps({'feature_names':GRAPH_FEATURE_NAMES,'graph_dim':96,'hash_dim':4096,'total_dim':X.shape[1]},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'rows':n,'groups':len(set(groups)),'X_shape':list(X.shape),'graph_shape':list(G.shape),'teacher_targets':sum(x['pair_target_available'] for x in target_rows),'quality_eligible':sum(x['quality_eligible'] for x in target_rows),'outer_folds':len(outer_splits),'inner_folds':len(inner),'labels_read':False},ensure_ascii=False))
if __name__=='__main__': main()
