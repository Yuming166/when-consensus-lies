#!/usr/bin/env python3
"""Read-only generation/coverage acceptance. Never reads gold or fits a model."""
import ast, csv, hashlib, json, math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
Q = BASE / 'pecr_qwen_generation_aligned_correction_v1_20261002'
OLD = BASE / 'pecr_strict_numeric_retrain_export_v1_20261001'
D = BASE / 'pecr_crossmodel_deepseek_v2_complete_20261001'
N = BASE / 'pecr_oof_sensitivity_native_g_v1_20261002/results/native_g'
METHOD = BASE / 'pecr_trd_delta_method_development_v3_20260926/v3_2'
WORLDS = ('original','positive','negative')
FIELDS = ('answer_value','unit','confidence')

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def relative(p): return '../'+str(Path(p).resolve().relative_to(BASE))
def jread(p): return json.loads(Path(p).read_text())
def jlread(p): return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def cread(p):
    with Path(p).open(newline='') as f:return list(csv.DictReader(f))
def jwrite(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False);f.write('\n')
def ordered_hash(ids):return hashlib.sha256((''.join(str(i)+'\n' for i in ids)).encode()).hexdigest()
def ast_functions(path,names,namespace):
    tree=ast.parse(Path(path).read_text());nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    assert {n.name for n in nodes}==set(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace);return namespace
def normunit(v):
    return '' if v is None else str(v).strip().lower().replace('percentage','%').replace('percent','%')
def unit_export(fields,vh):
    present='unit' in fields;v=fields.get('unit');safe=(v is None or isinstance(v,(int,bool)) or
        isinstance(v,float) and math.isfinite(v) or isinstance(v,str) and len(v)<=256 and '\n' not in v and '\r' not in v)
    return {'unit_key_present':present,'raw_unit':v if present and safe else None,
        'raw_unit_type':type(v).__name__ if present else 'missing','raw_unit_sha256':vh(v) if present else None,
        'unit_export_status':'preserved' if present and safe else 'narrative_hashed' if present else 'missing',
        'normalized_unit_from_saved_field':normunit(v) if present and safe else None,
        'normalization_is_unit_conversion':False}
def partition(requested,parsed,known):
    if not requested:return 'unrequested_construction_exclusion'
    if parsed and known:return 'strict_parsed_labeled'
    if parsed:return 'valid_unknown_label'
    return 'invalid_known_label' if known else 'invalid_unknown_label'

def main():
    outputs=['audit/generation_binding_audit.json','coverage/attempted_frame.jsonl',
        'coverage/attempted_frame.csv','coverage/SUMMARY.json','coverage/SUMMARY.csv',
        'coverage/COVERAGE.md','coverage/ID_HASHES.json','reports/GENERATION_BINDING.md']
    assert all(not (ROOT/p).exists() for p in outputs),'refuse_existing_audit_outputs'
    for p in outputs:(ROOT/p).parent.mkdir(parents=True,exist_ok=True)
    helper=Q/'src/build_generation_labels.py'
    ns=ast_functions(helper,{'Cursor','select','canon','vh'},{'json':json,'hashlib':hashlib})
    select,vh=ns['select'],ns['vh']
    # Exclude every label-access function: this audit never evaluates TRAIN paths.
    nns=ast_functions(OLD/'src/numeric.py',{'curve33'},{'np':np,'WORLD_ORDER':WORLDS})
    curve33=nns['curve33']
    paths=[Q/'data/label_blind_frame.jsonl',Q/'data/labels_current.csv',Q/'data/generation_map.jsonl',
        Q/'audit/LABEL_ACCESS_RECEIPT.json',Q/'audit/LABEL_SOURCE_HASHES.json',
        Q/'audit/FEATURE_AUDIT.json',Q/'audit/FEATURE_SOURCE_HASHES.json',
        Q/'src/build_aligned_features.py',helper,Q/'data/schema.json',Q/'results/refit/OOF.npz',
        OLD/'attempted/attempted_frame.jsonl',OLD/'attempted/graph_origin_status.jsonl',
        OLD/'schema.json',OLD/'src/numeric.py',OLD/'sources/SOURCE_HASHES.json',
        D/'data/labels_deepseek_v2.csv',D/'data/LABEL_RECEIPT_DEEPSEEK_V2.json',
        D/'src/make_deepseek_labels_v2.py',D/'data/merged_ledger_v2.jsonl',
        D/'results/within_deepseek_v2/CURVE_HGB_AUDITED_OOF.npz',
        METHOD/'data/features_prelabel.npz',METHOD/'data/feature_row_map.jsonl',
        N/'G96_NATIVE.npz',N/'OOF.npz',N/'METRICS.json',N/'FEATURE_STATUS.jsonl',
        N/'SOURCE_HASHES.json',N/'NATIVE_G_AUDIT.json',N/'VALIDATION.json',
        ROOT/'protocol/RELEASE_SPEC.json',Path(__file__)]
    for root in [Q/'data/strict',OLD/'cohorts/deepseek_v2_component']:
        paths.extend(root/n for n in ['features_label_blind.jsonl','manifest.jsonl','labels.csv','folds.csv','fold_provenance.json'])
    paths.append(OLD/'cohorts/deepseek_v2_component/reference/COMPONENT_ABLATION_OOF.npz')
    before={relative(p):sha(p) for p in paths}
    qframe=jlread(Q/'data/label_blind_frame.jsonl');full=jlread(OLD/'attempted/attempted_frame.jsonl')
    qlabels={r['item_id']:r for r in cread(Q/'data/labels_current.csv')}
    dlabels={r['id']:r for r in cread(D/'data/labels_deepseek_v2.csv')}
    generation={r['item_id']:r for r in jlread(Q/'data/generation_map.jsonl')}
    graphorig={r['item_id']:r for r in jlread(OLD/'attempted/graph_origin_status.jsonl')}
    assert len(qframe)==len(full)==2241
    assert [(r['item_id'],r['source_group']) for r in qframe]==[(r['item_id'],r['source_group']) for r in full]
    ids=[r['item_id'] for r in full];assert len(set(ids))==2241
    assert set(qlabels)==set(dlabels)==set(generation)==set(graphorig)==set(ids)
    feature_receipt=jread(Q/'audit/FEATURE_AUDIT.json');label_receipt=jread(Q/'audit/LABEL_ACCESS_RECEIPT.json')
    assert not feature_receipt['old_G96_or_old_response_graph_used']
    assert not feature_receipt['feature_uses_gold_labels_program_results_predictions']
    assert feature_receipt['supporting_evidence_validated_only']
    assert sha(Q/'data/labels_current.csv')==label_receipt['label_file_sha256']
    assert sha(Q/'data/label_blind_frame.jsonl')==feature_receipt['frame_sha256']
    dr=jread(D/'data/LABEL_RECEIPT_DEEPSEEK_V2.json')
    assert sha(D/'data/labels_deepseek_v2.csv')==dr['label_file_sha256']
    native_source=jread(N/'SOURCE_HASHES.json')
    ds_native_ledger=[r for r in native_source['files'] if r['path_relative_to_analysis'].endswith('pecr_crossmodel_deepseek_v2_complete_20261001/data/merged_ledger_v2.jsonl')]
    assert len(ds_native_ledger)==1 and ds_native_ledger[0]['sha256']==before[relative(D/'data/merged_ledger_v2.jsonl')]
    assert dr['predictions_source']=='V2 merged DeepSeek original-world parsed_json.answer_value only'
    ds_label_code=(D/'src/make_deepseek_labels_v2.py').read_text()
    assert "V2/'data/merged_ledger_v2.jsonl'" in ds_label_code and "r.get('world')=='original'" in ds_label_code
    assert "get('answer_value')" in ds_label_code and 'label_one(pred,lookup.get(i))' in ds_label_code
    # Recover only numeric fields/metadata from private DS records. Nonselected values are lexical skips.
    metadata_keys=['item_id','world','slot','attempt_id','http_status','record_hash','request_sha256',
        'response_sha256','utc_started','utc_finished','model_requested','model_reported','status','source_group']
    dsrecords={}
    with (D/'data/merged_ledger_v2.jsonl').open() as f:
        for ln,line in enumerate(f,1):
            r=select(line,metadata_keys+['parsed_json.'+k for k in FIELDS])
            key=(r['item_id'],r['world']);assert key not in dsrecords
            fields={k:r['parsed_json.'+k] for k in FIELDS if 'parsed_json.'+k in r}
            dsrecords[key]={'meta':r,'fields':fields,'line':ln}
    assert len(dsrecords)==6675 and len({i for i,w in dsrecords})==2225
    # Current Qwen world raw units (including numeric parse failures) come from the same source file.
    qsource=BASE/'pecr_bidirectional_development_v1_20260928/data/full_dev/raw_ledger_full_dev.jsonl'
    before[relative(qsource)]=sha(qsource);paths.append(qsource);qrecords={}
    with qsource.open() as f:
        for ln,line in enumerate(f,1):
            r=select(line,metadata_keys+['parsed_json.'+k for k in FIELDS])
            key=(r['item_id'],r['world']);assert key not in qrecords
            qrecords[key]={'meta':r,'fields':{k:r['parsed_json.'+k] for k in FIELDS if 'parsed_json.'+k in r},'line':ln}
    assert len(qrecords)==6675
    strict_roots={'qwen_generation_aligned':Q/'data/strict',
                  'deepseek_shared_qwen':OLD/'cohorts/deepseek_v2_component'}
    strict={};binding_checks={}
    snapshot=np.load(METHOD/'data/features_prelabel.npz',allow_pickle=False)['graph']
    rowmap={r['id']:r['row_index'] for r in jlread(METHOD/'data/feature_row_map.jsonl')}
    assert snapshot.shape==(2241,96) and np.isfinite(snapshot).all()
    for name,p in strict_roots.items():
        rows=jlread(p/'features_label_blind.jsonl');mans=jlread(p/'manifest.jsonl');labs=cread(p/'labels.csv');folds=cread(p/'folds.csv')
        assert len(rows)==len(mans)==len(labs)==len(folds)
        assert len({r['item_id'] for r in rows})==len(rows)
        for i,(r,m,l,fo) in enumerate(zip(rows,mans,labs,folds)):
            assert r['item_id']==m['item_id']==l['item_id']==fo['item_id']
            assert r['source_group']==m['source_group']==l['source_group']==fo['source_group']
            assert np.array_equal(np.array(r['Curve33']),curve33(r,m))
            assert np.array_equal(np.array(r['raw17']),np.array(r['Curve33'][:17]))
            assert len(r['G96'])==96 and np.isfinite(r['G96']).all()
            if name=='deepseek_shared_qwen':assert np.array_equal(np.array(r['G96']),snapshot[rowmap[r['item_id']]])
        groups=np.array([r['source_group'] for r in rows]);outer=np.array([int(r['outer_fold']) for r in folds]);y=np.array([int(r['error']) for r in labs])
        for g in np.unique(groups):assert len(set(outer[groups==g]))==1
        strict[name]={'rows':rows,'lookup':{r['item_id']:r for r in rows},'ids':[r['item_id'] for r in rows],
            'groups':groups,'outer_fold':outer,'y':y}
        binding_checks[name]={'strict_ids_unique':True,'label_manifest_fold_ID_group_alignment':True,
            'curve_exact_saved_response_arithmetic':True,'raw_exact_curve_prefix':True,
            'finite_G96_raw17_Curve33_dimensions':True,'groups_do_not_cross_fold':True,
            'fold_status':'posthoc; no original freeze time inferred'}
    assert len(strict['qwen_generation_aligned']['rows'])==2142
    assert len(strict['deepseek_shared_qwen']['rows'])==2050
    qoof=np.load(Q/'results/refit/OOF.npz',allow_pickle=False)
    doof=np.load(OLD/'cohorts/deepseek_v2_component/reference/COMPONENT_ABLATION_OOF.npz',allow_pickle=False)
    auxiliary=np.load(D/'results/within_deepseek_v2/CURVE_HGB_AUDITED_OOF.npz',allow_pickle=False)
    for name,z in [('qwen_generation_aligned',qoof),('deepseek_shared_qwen',doof),('deepseek_shared_qwen',auxiliary)]:
        assert np.array_equal(z['y'],strict[name]['y']) and np.array_equal(z['groups'],strict[name]['groups'])
        if 'item_ids' in z.files:assert np.array_equal(z['item_ids'],np.array(strict[name]['ids']))
    noof=np.load(N/'OOF.npz',allow_pickle=False);ng=np.load(N/'G96_NATIVE.npz',allow_pickle=False)
    assert np.array_equal(noof['item_ids'],np.array(strict['deepseek_shared_qwen']['ids']))
    assert np.array_equal(noof['y'],strict['deepseek_shared_qwen']['y'])
    assert np.array_equal(noof['outer_fold'],strict['deepseek_shared_qwen']['outer_fold'])
    assert np.array_equal(ng['item_ids'],noof['item_ids']) and ng['G96_native'].shape==(2050,96)
    assert np.array_equal(noof['shared_G_curve'],doof['full_curve'])
    assert np.array_equal(noof['shared_G_raw'],doof['raw_three_world'])
    native_status={r['item_id']:r for r in jlread(N/'FEATURE_STATUS.jsonl')}
    assert all(r['target_frozen_safe_status']=='valid' and not r['target_fallback_used'] for r in native_status.values())
    attempted=[];summary={};world_counts={};unit_counts={};id_hashes={}
    for name in ['qwen_generation_aligned','deepseek_shared_qwen']:
        partitions=Counter();wc={w:Counter() for w in WORLDS};uc=Counter();strict_units=Counter()
        for fr,qfr in zip(full,qframe):
            iid=fr['item_id'];isq=name=='qwen_generation_aligned'
            flags=qfr if isq else fr['families']['deepseek_v2_component']
            lab=qlabels[iid] if isq else dlabels[iid]
            requested=flags['requested'];known=lab['error']!='';parsed=flags['all_three_strict_parse_valid']
            part=partition(requested,parsed,known);isstrict=iid in strict[name]['lookup']
            assert isstrict==(part=='strict_parsed_labeled')
            recs=qrecords if isq else dsrecords;ws={};all_units=[]
            for w in WORLDS:
                record=recs.get((iid,w));src=flags['worlds'][w]
                fields=record['fields'] if record else {}
                ue=unit_export(fields,vh);all_units.append(ue['normalized_unit_from_saved_field'])
                stat=src.get('historical_strict_parser_status') if isq else src.get('offline_parser_status')
                stat=stat or 'unknown'
                present=src['record_present'];assert present==(record is not None)
                md=record['meta'] if record else {}
                if isq and record:
                    for hash_key in ['record_hash','request_sha256','response_sha256']:
                        assert src[hash_key]==md.get(hash_key),'Qwen_feature_frame_response_source_hash_mismatch'
                ws[w]={'record_present':present,'recorded_status':src.get('recorded_status') or 'unknown',
                    'offline_parser_status':stat,'parser_status_basis':'historical offline parser on saved response; no new model response',
                    'offline_parser_valid':src.get('historical_strict_parser_valid') if isq else (True if stat=='ok' else None if stat=='unknown' else False),
                    'http_status':src.get('http_status'),'assistant_json_present':src.get('parsed_json_present') if isq else src.get('assistant_json_present'),
                    'source_record_hash':md.get('record_hash'),'request_sha256':md.get('request_sha256'),
                    'response_sha256':md.get('response_sha256'),
                    'request_hash_kind':'source_recorded' if md.get('request_sha256') else 'unknown',
                    'response_hash_kind':'source_recorded' if md.get('response_sha256') else 'derived_saved_selected_fields' if fields else 'unknown',
                    'derived_selected_response_fields_sha256':vh(fields) if fields else None,
                    'source_line':record['line'] if record else None,
                    'source_path':relative(qsource if isq else D/'data/merged_ledger_v2.jsonl'),
                    'utc_started':md.get('utc_started'),'utc_finished':md.get('utc_finished'),
                    'collection_batch':None,'collection_batch_status':'unknown_not_recorded',
                    'model_requested':md.get('model_requested'),'model_reported_recorded':md.get('model_reported'),
                    'numeric_answer_field_sha256':vh(fields.get('answer_value')) if 'answer_value' in fields else None,**ue}
                if not ws[w]['response_sha256'] and fields:ws[w]['response_sha256']=vh(fields)
                wc[w][stat]+=1
            units='unknown' if not requested or any(u is None for u in all_units) else (
                'nonempty_' if all(all_units) else 'empty_')+('same' if len(set(all_units))==1 else 'mismatch')
            uc[units]+=1
            if isstrict:strict_units[units]+=1
            original=(recs.get((iid,'original')) or {}).get('fields',{})
            if isq:
                gr=generation[iid]
                assert lab['answer_value_canonical_sha256']==(gr['current_original']['answer_value_canonical_sha256'] or '')
                if requested:
                    assert lab['response_record_hash']==ws['original']['source_record_hash']
                    assert lab['response_sha256']==ws['original']['response_sha256']
                    assert ws['original']['numeric_answer_field_sha256']==gr['current_original']['answer_value_canonical_sha256']
                origin={'kind':'target_Qwen_current_original','model':'Qwen3.5-4B','same_generation_as_label_and_curve':True,
                    'source_generation':'current_three_world_original','answer_field_sha256':gr['current_original']['answer_value_canonical_sha256'],
                    'saved_fallback':False,'G96_available':bool(qfr['G96_valid'])}
                label_binding='per_item_response_record_and_answer_field_hash_verified'
            else:
                origin={'kind':'shared_Qwen_historical_original','model':'Qwen3.5-4B','same_generation_as_label_and_curve':False,
                    'source_generation':'earlier_paired_Qwen_feature_input_snapshot','answer_field_sha256':generation[iid]['old_label_input']['answer_value_canonical_sha256'],
                    'saved_fallback':graphorig[iid]['uses_saved_fallback_original_response_fields'],'G96_available':True,
                    'native_counterpart_available':iid in native_status}
                label_binding='posthoc_source_recipe_saved_label_file_original_response_binding; no new gold verification'
            if isstrict:
                r=strict[name]['lookup'][iid]
                for w in WORLDS:
                    fv=(recs[(iid,w)]['fields']);v=float(str(fv['answer_value']).strip().replace(',','').replace('−','-'))
                    assert v==r['responses'][w]['value']
                    assert float(fv['confidence'])==r['responses'][w]['confidence']
                    assert normunit(fv.get('unit'))==r['responses'][w]['unit']
                assert int(lab['error'])==int(strict[name]['y'][strict[name]['ids'].index(iid)])
                if isq:assert np.array_equal(np.array(r['G96']),np.array(qfr['G96']))
            partitions[part]+=1
            attempted.append({'cohort':name,'frame_row_index':fr['row_index'],'item_id':iid,
                'item_id_sha256':hashlib.sha256(iid.encode()).hexdigest(),'source_group':fr['source_group'],
                'requested':requested,'construction_excluded':fr['construction_excluded'],
                'construction_status':fr['construction_status'],'construction_flags':fr['construction_flags'],
                'partition':part,'strict_member':isstrict,'all_three_offline_parse_valid':parsed,
                'label_status':lab['label_status'],'error':int(lab['error']) if known else None,
                'label_missing':not known,'label_reason':lab['label_reason'],
                'label_source_path':relative(Q/'data/labels_current.csv' if isq else D/'data/labels_deepseek_v2.csv'),
                'label_source_sha256':sha(Q/'data/labels_current.csv' if isq else D/'data/labels_deepseek_v2.csv') if fr['row_index']==0 else before[relative(Q/'data/labels_current.csv' if isq else D/'data/labels_deepseek_v2.csv')],
                'label_response_binding':label_binding,'binding_added_posthoc':True,
                'original_label_target_answer_sha256':ws['original']['numeric_answer_field_sha256'],
                'unit_combination_from_saved_fields':units,'G96_origin':origin,'worlds':ws})
        s=strict[name];summary[name]={'frame_rows':2241,'frame_groups':453,'requested_rows':2225,'unrequested_rows':16,
            'strict_rows':len(s['ids']),'strict_groups':len(set(s['groups'])),'strict_error':int(s['y'].sum()),
            'strict_correct':int((s['y']==0).sum()),'strict_coverage_requested':len(s['ids'])/2225,
            'strict_coverage_frame':len(s['ids'])/2241,'mutually_exclusive_partitions':dict(partitions),
            'requested_not_strict':2225-len(s['ids']),'strict_unit_combinations':dict(strict_units)}
        world_counts[name]={w:dict(c) for w,c in wc.items()};unit_counts[name]=dict(uc)
        id_hashes[name]={'hash_contract':'SHA256 UTF8 one item_id per line, final newline; original order',
            'frame':ordered_hash(ids),'requested':ordered_hash([r['item_id'] for r in attempted if r['cohort']==name and r['requested']]),
            'strict_training_order':ordered_hash(s['ids'])}
    assert summary['qwen_generation_aligned']['mutually_exclusive_partitions']=={
        'strict_parsed_labeled':2142,'valid_unknown_label':52,'invalid_known_label':7,'invalid_unknown_label':24,'unrequested_construction_exclusion':16}
    assert summary['deepseek_shared_qwen']['mutually_exclusive_partitions']=={
        'strict_parsed_labeled':2050,'valid_unknown_label':54,'invalid_known_label':79,'invalid_unknown_label':42,'unrequested_construction_exclusion':16}
    assert before=={relative(p):sha(p) for p in paths},'source_changed_during_audit'
    outsummary={'cohorts':summary,'world_offline_parser_status':world_counts,'full_frame_unit_combinations':unit_counts,
        'recorded_status_policy':'unknown remains unknown even if HTTP200/offline parser valid',
        'TRAIN_gold_holdout_access':False,'model_API_calls':0,'training_fits':0}
    jwrite(ROOT/'coverage/SUMMARY.json',outsummary);jwrite(ROOT/'coverage/ID_HASHES.json',id_hashes)
    with (ROOT/'coverage/attempted_frame.jsonl').open('x') as f:
        for r in attempted:f.write(json.dumps(r,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n')
    flat=[]
    for r in attempted:
        z={k:v for k,v in r.items() if k not in ('worlds','G96_origin','construction_flags')}
        z['construction_flags_json']=json.dumps(r['construction_flags'],sort_keys=True)
        for k,v in r['G96_origin'].items():z['G96_'+k]=v
        for w,wd in r['worlds'].items():
            for k,v in wd.items():z[w+'_'+k]=v
        flat.append(z)
    with (ROOT/'coverage/attempted_frame.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in flat for k in r)));w.writeheader();w.writerows(flat)
    with (ROOT/'coverage/SUMMARY.csv').open('x',newline='') as f:
        rows=[{'cohort':c,'partition':p,'rows':n,'full_frame_denominator':2241,'requested_denominator':2225}
            for c,s in summary.items() for p,n in s['mutually_exclusive_partitions'].items()]
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    native_methods={'graph_only':False,'raw_three_world':True,'full_curve':True,
        'no_input_normalization':False,'no_curvature_asymmetry':False,'no_direction_information':False}
    audit={'status':'PASS_PROVENANCE_BINDING_WITH_EXPLICIT_SHARED_G_BOUNDARY','checked_utc':datetime.now(timezone.utc).isoformat(),
        'sources':[{'path_relative_to_release':p,'sha256':h} for p,h in before.items()],
        'sources_unchanged':True,'strict_numeric_binding_checks':binding_checks,
        'qwen_label_original_curve_G_same_generation':True,'deepseek_label_original_curve_same_generation':True,
        'deepseek_primary_G_kind':'shared_Qwen_historical_original','deepseek_primary_G_target_native':False,
        'deepseek_label_binding_added_posthoc':True,'label_gold_accuracy_rechecked_in_release':False,
        'deepseek_native_available_six_method_flags':native_methods,
        'deepseek_native_existing_variants':list(jread(N/'METRICS.json')['evaluation']['metrics']),
        'deepseek_shared_graph_only_existing_auxiliary_OOF':'saved older audit OOF; aligned y/group support; not a native graph result',
        'native_same_strict_ID_label_fold_support_verified':True,'native_shared_OOF_exact_primary_match':True,
        'coverage_summary':outsummary,'ordered_ID_hashes':id_hashes,'output_restrictions':{
            'TRAIN_gold_holdout_access':False,'financial_body_export':False,'raw_ledger_export':False,
            'model_reasoning_export':False,'credentials_export':False,'model_API_calls':0,'training_fits':0}}
    jwrite(ROOT/'audit/generation_binding_audit.json',audit)
    lines=['# Full attempted coverage and unit/parse boundary','',
        '| Cohort | Frame | Requested | Strict | Error/correct | Groups | Requested outside strict |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for c,s in summary.items():lines.append(f"| {c} | 2241 | 2225 | {s['strict_rows']} | {s['strict_error']}/{s['strict_correct']} | {s['strict_groups']} | {s['requested_not_strict']} |")
    lines+=['','| Mutually exclusive partition | Qwen corrected | DeepSeek shared G |','|---|---:|---:|']
    for p in ['strict_parsed_labeled','valid_unknown_label','invalid_known_label','invalid_unknown_label','unrequested_construction_exclusion']:
        lines.append(f"| {p} | {summary['qwen_generation_aligned']['mutually_exclusive_partitions'][p]} | {summary['deepseek_shared_qwen']['mutually_exclusive_partitions'][p]} |")
    lines+=['','Partitions sum to2241. Qwen requested outside strict is83=52+7+24; DeepSeek outside strict is175=54+79+42.',
        'A strict parser does not imply compatible units. Unit strings are normalized by the historical strip/lower/percent replacements only, with no conversion.',
        'Each cohort has all2241 rows in attempted_frame exports, including per-world recorded status, offline parser status, unit state, label missingness, source hashes and G origin.',
        'Unknown recorded status is never upgraded to success. Unrequested records retain unknown parser state.',
        '', '## Per-world offline parsing']
    for c,ws in world_counts.items():
        for w,d in ws.items():lines.append(c+' / '+w+': '+json.dumps(d,sort_keys=True))
    lines+=['','## Strict unit combinations']
    for c,s in summary.items():lines.append(c+': '+json.dumps(s['strict_unit_combinations'],sort_keys=True))
    (ROOT/'coverage/COVERAGE.md').write_text('\n'.join(lines)+'\n')
    report=['# Generation and numeric binding acceptance','',
        'PASS for source/row binding, with explicit shared-Qwen DeepSeek feature provenance. No TRAIN/gold/holdout access, model/API call or fit was performed in this acceptance task.',
        'This post-hoc audit binds saved artifacts; it does not independently recheck numeric-gold correctness or invent historical per-row freeze receipts.',
        '', '## Qwen corrected primary',
        'Every current-label answer hash and original response record/response hash matches generation_map and the corrected feature frame. Curve/Raw exactly reconstruct from their saved three responses and edit operands. Corrected G96 matches the current frame, whose audited builder reads the same current original fields; old responses/G are not substituted.',
        'Support2142/452 includes1699 errors and443 correct. All2225 requested items remain visible;83 requested outside strict split52 valid-unlabeled,7 invalid-labeled and24 invalid-unlabeled, plus16 unrequested exclusions.',
        '', '## DeepSeek shared primary',
        'The existing DeepSeek label generator/receipt targets V2 merged original parsed_json.answer_value. The same source file supplies all three response worlds. Each exported strict numeric world matches those source fields after the historical parser normalization; the same saved labels bind OOF by existing real training row order.',
        'DeepSeek per-response label hashes were not embedded in the original label CSV; their binding is added now from the saved source recipe/file/ID provenance, not falsely dated as a historical freeze. No gold was read to certify label correctness here.',
        'Primary G96 is historical shared_Qwen, copied exactly from the saved Qwen snapshot, including saved fallback fields. It is deliberately cross-model and not target-native. Per-row origin includes the actual old label-input snapshot hash rather than substituting the actual old model answer for its default field.',
        'Support2050/448 includes1257 errors and793 correct. The175 requested outside strict split54 valid-unlabeled,79 invalid-labeled and42 invalid-unlabeled, plus16 unrequested.',
        '', '## Native availability',
        'Existing target-native DeepSeek scores cover native Raw and native Full Curve only; shared Raw/Curve are their paired reference variants. These four saved variants have the same2050 IDs/labels/folds, and shared scores match primary OOF exactly.',
        'Native graph-only and all three native family-removal variants do not exist. Thus native six-method coverage is incomplete; no missing method was trained, fabricated or marked successful.',
        'A saved DeepSeek shared-G graph-only score exists in the earlier audited OOF with matching y/group support. It remains a shared-G source artifact and cannot fill a native-method cell.',
        '', '## Traceability',
        'audit/generation_binding_audit.json records source-relative paths and all inspected source hashes. coverage/ID_HASHES.json defines ordered ID hash semantics. coverage/attempted_frame JSONL/CSV contains two full2241 cohorts and per-world statuses/units, missing labels and feature-source boundary.',
        'Raw ledgers, financial text, narrative answers, reasoning and credentials are not exported. Missing collection batches/finished timestamps remain unknown. Recorded request/response hashes retain source-recorded semantics; separately derived field hashes are explicitly labeled.',
        'The portable release can refit from numeric artifacts; rerunning this private-source binding check requires the source tree and does not require dataset gold.',
        'Source and numeric provenance consistency is not independent generalization, a causal mechanism, an ARR score or an acceptance guarantee.']
    (ROOT/'reports/GENERATION_BINDING.md').write_text('\n'.join(report)+'\n')
    print(json.dumps({'status':audit['status'],'cohorts':summary,'native_methods':native_methods,'gold_read':False,'fits':0},sort_keys=True))

if __name__=='__main__':main()
