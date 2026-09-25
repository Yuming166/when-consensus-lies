#!/usr/bin/env python3
"""Stage B only: compare frozen signs after Stage-A reviewer form is frozen by SHA-256."""
import argparse,csv,hashlib,json
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument('--review-form',required=True,type=Path)
ap.add_argument('--review-sha256',required=True)
ap.add_argument('--sealed-sign-key',required=True,type=Path)
ap.add_argument('--output',required=True,type=Path)
a=ap.parse_args()
actual=sha(a.review_form)
if actual.lower()!=a.review_sha256.lower(): raise SystemExit('STOP: reviewer form hash mismatch')
rows=list(csv.DictReader(a.review_form.open(newline='')))
key={r['item_id']:r['frozen_expected_sign_pair_minus_plus'] for r in map(json.loads,a.sealed_sign_key.open())}
if len(rows)!=20 or len({r['item_id'] for r in rows})!=20 or set(r['item_id'] for r in rows)!=set(key): raise SystemExit('STOP: expected exactly the fixed 20 IDs')
out=[]
for r in rows:
  def sign(s):
    s=(s or '').strip()
    if s in {'-1','+1','1'}: return int(s.replace('+',''))
    return None
  frozen=key[r['item_id']]; ind=[sign(r.get('independently_derived_minus_direction')),sign(r.get('independently_derived_plus_direction'))]
  out.append({'item_id':r['item_id'],'reviewer_derived_sign_pair_minus_plus':ind,'frozen_expected_sign_pair_minus_plus':frozen,'minus_agreement':ind[0]==frozen[0] if ind[0] is not None else None,'plus_agreement':ind[1]==frozen[1] if ind[1] is not None else None,'overall_agreement':ind==frozen if all(v is not None for v in ind) else None,'reviewer_validity_judgment':r.get('overall_valid_invalid_uncertain'),'reviewer_reason':r.get('minus_direction_reason_and_calculation','')+' | '+r.get('plus_direction_reason_and_calculation',''),'text_coherence_judgment':r.get('world_text_financial_coherence'),'evidence_reference':r.get('evidence_reference','')})
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps({'artifact':'PECR_CONSTRUCTION_DISAGREEMENT_V2','posthoc':True,'review_form_sha256':actual,'sealed_key_sha256':sha(a.sealed_sign_key),'rows':out},indent=2,ensure_ascii=False)+'\n')
