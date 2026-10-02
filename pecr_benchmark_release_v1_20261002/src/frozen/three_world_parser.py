"""Exact historical numeric/unit/confidence function projection; no source I/O."""
def parse_num(x):
 if x is None:return None
 s=str(x).strip().replace(',','').replace('−','-')
 if not s:return None
 try:return float(s)
 except:return None

def norm_unit(u):
 if u is None:return ''
 s=str(u).strip().lower().replace('percentage','%').replace('percent','%')
 return s

def parse_resp(rec):
 if 'parsed_json' not in rec:return None,'missing_json'
 p=rec['parsed_json']
 if not isinstance(p,dict):return None,'json_not_object'
 v=parse_num(p.get('answer_value'))
 if v is None:return None,'answer_not_numeric'
 c=parse_num(p.get('confidence'))
 if c is None or not (0<=c<=1): return None,'confidence_invalid'
 return {'value':v,'unit':norm_unit(p.get('unit')),'confidence':c},None
