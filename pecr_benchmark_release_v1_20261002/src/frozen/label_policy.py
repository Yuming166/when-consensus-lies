"""Frozen V3.1 numeric free-text correctness policy; do not edit after checkpoint."""
from decimal import Decimal, InvalidOperation
import re
NUM_RE=re.compile(r'^\s*(?:\(\s*)?[-+]?\s*\$?\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*%?\s*\)?\s*$')
def parse_numeric(v):
    if isinstance(v,bool) or not isinstance(v,(str,int,float,Decimal)): return None
    s=str(v).strip()
    if not NUM_RE.fullmatch(s): return None
    par=s.startswith('(') and s.endswith(')')
    s=s.replace('$','').replace(',','').replace('%','').replace('(','').replace(')','').strip()
    try: x=Decimal(s)
    except InvalidOperation: return None
    if not x.is_finite(): return None
    return -abs(x) if par else x
def label_one(pred_answer,gold_answer):
    p=parse_numeric(pred_answer); g=parse_numeric(gold_answer)
    if p is None: return None,'invalid_original_numeric_answer'
    if g is None: return None,'invalid_or_missing_gold_numeric_answer'
    tol=max(Decimal('0.0001'),Decimal('0.0001')*abs(g))
    return int(abs(p-g)<=tol),None
