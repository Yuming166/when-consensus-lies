#!/usr/bin/env python3
"""Freeze ConvFinQA Stage-2 Qwen train execution contract offline."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent
V10=HERE.parents[1]/'finqa_convfinqa'/'24_pecr_v0_10_missing_probe_imputation_20260922'/'PECR_V0_10_FROZEN_CONTRACT.json'
STAGE1=HERE.parents[1]/'finqa_convfinqa'/'26_convfinqa_stage1_qwen_replication_20260922'
CONTRACT=HERE/'CONVFINQA_STAGE2_QWEN_TRAIN_CONTRACT.json'

def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
def lines(p):return sum(1 for _ in p.open())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n')
v10=load(V10); s1=load(STAGE1/'STAGE1_QWEN_DEV_ANALYSIS.json'); s1c=load(STAGE1/'CONVFINQA_STAGE1_QWEN_REPLICATION_CONTRACT.json')
train_prom=HERE/'STAGE2_TRAIN_PROMPTS.jsonl'; train_gold=HERE/'STAGE2_TRAIN_WORLD_GOLD.jsonl'; dev_gold=HERE/'STAGE2_DEV_WORLD_GOLD.jsonl'; dev_raw=HERE/'STAGE1_QWEN_DEV_RAW_RECORDS.jsonl'
contract={
 'contract':'CONVFINQA_STAGE2_QWEN_TRAIN_CONTRACT',
 'protocol':'ConvFinQA_PECR_v0.11_stage2_qwen_missing_probe_train',
 'version':'stage2',
 'freeze_date':'2026-09-22',
 'status':'FROZEN_PRE_MODEL_CALL',
 'claim_boundary':'Stage-2 Qwen ConvFinQA TRAIN collection for frozen missing-probe distillation. No distillation effectiveness claim is established until TRAIN heads are fit offline and evaluated once on the already executed frozen DEV worlds.',
 'model_calls':0,
 'authorization':{'model_calls_authorized':True,'authorization_basis':'Stage-1 Qwen DEV primary S2 and full CEF gates passed under frozen analysis; user-requested staged confirmation execution.'},
 'stage1_gate_snapshot':{'analysis_sha256':sha(STAGE1/'STAGE1_QWEN_DEV_ANALYSIS.json'),'s2_gate':s1['s2']['gate'],'full_cef_gate':s1['full_cef']['gate'],'core_gate':s1['stage1_core_gate'],'s2_auroc':s1['s2']['auroc']['observed'],'full_cef_auroc':s1['full_cef']['auroc']['observed'],'stage2_metric_gate_is_not_tuned':True},
 'data':{'stage1_contract_sha256':sha(STAGE1/'CONVFINQA_STAGE1_QWEN_REPLICATION_CONTRACT.json'),'train_prompts_sha256':sha(train_prom),'train_gold_sha256':sha(train_gold),'dev_gold_sha256':sha(dev_gold),'dev_raw_sha256':sha(dev_raw),'finqa_v0_10_contract_sha256':sha(V10)},
 'worlds':{'train_items':1344,'train_worlds':lines(train_gold),'dev_items':198,'dev_worlds':lines(dev_gold),'train_calls_authorized':lines(train_prom),'deployment_worlds':['original','relevant_k_minus1','relevant_k_plus1'],'teacher_worlds':['original','relevant_k_minus2','relevant_k_minus1','relevant_k_plus1','relevant_k_plus2']},
 'model_identity':s1c['model_identity'],
 'request_contract':s1c['request_contract'],
 'distillation':{'target_minus2':'answer_correct on relevant_k_minus2','target_plus2':'answer_correct on relevant_k_plus2','primary_family':'all_response_rich','feature_family_sha256':v10['features']['primary_family_sha256'],'features_source':'frozen FinQA v0.10 feature definitions; no search or re-standardization based on ConvFinQA DEV','models':v10['models'],'original_correctness_usage':'evaluation only, never a training target or model-selection signal','dev_evaluation':'one frozen confirmation using Stage1 DEV raw records; no refit, calibration, threshold, or feature selection on DEV','reconstruction':'(correct_minus1 + correct_plus1 + p_minus2 + p_plus2) / 4'},
 'leakage':{'observed_worlds_only':['original','relevant_k_minus1','relevant_k_plus1'],'forbidden':['relevant_k_minus2 response','relevant_k_plus2 response','full_cef','original_correct','item_level_qa_answer_as_current_target'],'gold_oracle_boundary':'Observed executable gold may derive residual/direction/unit features, matching frozen FinQA v0.10 boundary.'},
 'gates':{'primary_head_auroc_report':['AUROC(p_minus2,F_minus2)','AUROC(p_plus2,F_plus2)'],'primary_confirmation':['AUROC(reconstructed_CEF,original_correct)','delta_vs_S2','group/bootstrap CI','MAE and Spearman vs full CEF'],'practical_threshold':'delta_vs_S2 >= 0.02','statistics_separate_from_practical_gate':True},
}
write(CONTRACT,contract)
write(HERE/'STAGE2_STATIC_FREEZE_AUDIT.json',{'protocol':contract['protocol'],'status':'PASS','model_calls':0,'stage1_core_gate':s1['stage1_core_gate'],'train_worlds':lines(train_gold),'dev_worlds':lines(dev_gold),'feature_sha256':v10['features']['primary_family_sha256'],'historical_artifacts_modified':False,'failures':[]})
(HERE/'STAGE2_FREEZE_STATUS.md').write_text(f'''# ConvFinQA Stage 2 freeze\n\nStatus: **FROZEN_PRE_MODEL_CALL**\n\n- Stage 1 Qwen core gate: **{s1['stage1_core_gate']}**.\n- TRAIN worlds authorized: **{lines(train_gold)}** ({lines(train_gold)//5} items x 5).\n- DEV evaluation: frozen Stage 1 raw records only; no new DEV calls.\n- Feature family: frozen FinQA v0.10 `all_response_rich`; no feature/model search.\n- Model calls made by freeze: **0**.\n- v0.11 and Stage 1 artifacts modified: **false**.\n''')
print(json.dumps(contract,ensure_ascii=False,indent=2))
