"""Frozen 4,192-hash + 96 typed feature builder; strict original-side allow-list."""
from __future__ import annotations
import math, re
from typing import Any
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

NUM_RE = re.compile(r'(?<![A-Za-z0-9])(?:\(\s*)?[-+]?\s*\$?\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*%?\s*\)?')
WORD_RE = re.compile(r"[a-z0-9]+(?:['’-][a-z0-9]+)?", re.I)
SECTION = ('question','pre','table','post','answer')
SUMMARY = ('log_abs_mean','log_abs_max','log_abs_std','negative_rate','decimal_rate','percent_rate','currency_rate')
TYPES = ('percent','currency','negative','decimal')
GRAPH_FEATURE_NAMES = (
    [f'{s}_number_count' for s in SECTION]
    + [f'{s}_{m}' for s in ('all','question','evidence','answer') for m in SUMMARY]
    + ['table_rows','table_cols','answer_number_count','answer_matches_evidence_count','question_evidence_number_overlap',
       'question_evidence_token_jaccard','question_token_count','evidence_token_count','answer_token_count',
       'answer_confidence','answer_unit_present','answer_percent_marker','answer_currency_marker','answer_negative_marker',
       'evidence_numeric_density','question_numeric_density','table_numeric_density','pre_post_numeric_ratio',
       'table_mean_numeric_per_row','table_rows_with_numbers','max_numbers_in_row','unique_numeric_values',
       'repeated_numeric_values','answer_log_abs_value','answer_rank_in_evidence','answer_near_evidence_value']
    + [f'type_count_{t}_{s}' for s in ('question','evidence','answer') for t in TYPES]
    + ['table_numeric_cell_row_mean','table_numeric_cell_col_mean','table_numeric_cell_col_max','table_numeric_row_ratio',
       'table_numeric_distinct_cols']
    + ['evidence_pair_count_log','evidence_pairs_less_rate','evidence_pairs_equal_rate','evidence_pairs_greater_rate']
    + ['question_has_increase_cue','question_has_decrease_cue','question_has_comparison_cue','question_has_percentage_cue','question_has_temporal_cue',
       'evidence_has_years','evidence_has_financial_terms','evidence_has_comparison_cue','answer_has_percent_word','answer_has_currency_word']
    + ['input_missing_pre','input_missing_post','input_missing_table']
    + ['unit_is_percent','unit_is_currency','unit_is_other']
)
assert len(GRAPH_FEATURE_NAMES) == 96, len(GRAPH_FEATURE_NAMES)


def _flatten(x: Any) -> list[str]:
    if x is None: return []
    if isinstance(x, str): return [x]
    if isinstance(x, (int,float)) and not isinstance(x,bool): return [str(x)]
    if isinstance(x, list):
        z=[]
        for y in x: z.extend(_flatten(y))
        return z
    raise TypeError(f'non_allowlisted_input_type:{type(x).__name__}')


def _safe(rec: dict) -> dict:
    if not isinstance(rec,dict): raise TypeError('record_not_object')
    allowed={'question','pre_text','table_original','post_text','original_response'}
    extra=set(rec)-allowed
    if extra: raise ValueError('forbidden_or_unknown_feature_field:'+','.join(sorted(extra)))
    if not isinstance(rec.get('question'),str): raise ValueError('missing_question')
    if not isinstance(rec.get('original_response'),dict): raise ValueError('missing_original_response')
    r=rec['original_response']; ra={'answer_value','unit','confidence','supporting_evidence'}
    if set(r)-ra: raise ValueError('forbidden_or_unknown_response_field')
    if not isinstance(r.get('answer_value'),(str,int,float)): raise ValueError('invalid_answer_value_type')
    if not isinstance(r.get('confidence'),(int,float)) or isinstance(r.get('confidence'),bool): raise ValueError('invalid_confidence')
    if not 0 <= float(r['confidence']) <= 1: raise ValueError('confidence_out_of_range')
    if r.get('unit') is not None and not isinstance(r['unit'],str): raise ValueError('invalid_unit')
    _flatten(rec.get('pre_text',[])); _flatten(rec.get('post_text',[]))
    if not isinstance(rec.get('table_original',[]),list): raise TypeError('table_not_list')
    for row in rec.get('table_original',[]):
        if not isinstance(row,list): raise TypeError('table_row_not_list')
        _flatten(row)
    _flatten(r.get('supporting_evidence',[]))
    return rec


def _number(token):
    s=token.strip(); par=s.startswith('(') and s.endswith(')'); pct='%' in s; cur='$' in s
    t=s.replace('$','').replace(',','').replace('%','').replace('(','').replace(')','').replace(' ','')
    try: v=float(t)
    except Exception: return None
    if par: v=-abs(v)
    if not math.isfinite(v): return None
    return {'v':v,'percent':pct,'currency':cur,'negative':v<0,'decimal':'.' in t,'surface':s}

def _nodes(text):
    out=[]
    for m in NUM_RE.finditer(text):
        x=_number(m.group())
        if x is not None: x.update(start=m.start(),end=m.end()); out.append(x)
    return out

def _tokens(s): return set(w.lower() for w in WORD_RE.findall(s))

def _graph(rec):
    rec=_safe(rec)
    q=rec['question']; pre=' '.join(_flatten(rec.get('pre_text',[]))); post=' '.join(_flatten(rec.get('post_text',[])))
    rows=[_flatten(row) for row in rec.get('table_original',[])]; tabletxt=' '.join(' '.join(r) for r in rows)
    r=rec['original_response']; ans=str(r['answer_value']); unit=str(r.get('unit') or '')
    ev=' '.join([pre,tabletxt,post]); evidence=' '.join(_flatten(r.get('supporting_evidence',[])))
    sect={'question':q,'pre':pre,'table':tabletxt,'post':post,'answer':ans+' '+unit,'evidence':ev}
    ns={k:_nodes(v) for k,v in sect.items()}
    evn=ns['evidence']; alln=ns['question']+ns['pre']+ns['table']+ns['post']+ns['answer']
    def sm(items):
        if not items:return [0.]*7
        a=np.asarray([math.log1p(abs(n['v'])) for n in items])
        return [float(a.mean()),float(a.max()),float(a.std()),float(np.mean([n['negative'] for n in items])),float(np.mean([n['decimal'] for n in items])),float(np.mean([n['percent'] for n in items])),float(np.mean([n['currency'] for n in items]))]
    flat_table=[(ri,ci,n) for ri,row in enumerate(rows) for ci,cell in enumerate(row) for n in _nodes(cell)]
    qn=ns['question']; an=ns['answer']; qtok=_tokens(q); etok=_tokens(ev); atok=_tokens(ans+' '+unit)
    ans_matches=sum(any(abs(n['v']-a['v'])<=1e-9*max(1,abs(a['v'])) for n in evn) for a in an)
    overlap_num=len({round(n['v'],8) for n in qn}&{round(n['v'],8) for n in evn})
    nums=[n['v'] for n in evn]; pair_total=max(1,len(nums)*(len(nums)-1)//2)
    less=sum(nums[i]<nums[j] for i in range(len(nums)) for j in range(i+1,len(nums)))
    equal=sum(nums[i]==nums[j] for i in range(len(nums)) for j in range(i+1,len(nums)))
    greater=max(0,len(nums)*(len(nums)-1)//2-less-equal)
    ansn=_number(ans); perrow=[sum(len(_nodes(c)) for c in row) for row in rows]
    uvals={round(n['v'],8) for _,_,n in flat_table}; cols=max((len(row) for row in rows),default=0)
    ansrank=near=0.
    if ansn and evn:
        ds=[abs(math.log1p(abs(n['v']))-math.log1p(abs(ansn['v']))) for n in evn]
        ansrank=(sorted(ds).index(min(ds))+1)/len(ds)
        near=float(any(abs(n['v']-ansn['v'])<=1e-3*max(1,abs(ansn['v'])) for n in evn))
    qlow=q.lower(); elow=ev.lower(); alow=(ans+' '+unit).lower(); qset=_tokens(q)
    financial={'revenue','income','asset','liability','cash','debt','sales','expense','profit','loss','investment','equity'}
    cues_up={'increase','increased','growth','higher','rise','rose','gain'}; cues_dn={'decrease','decreased','lower','fall','fell','decline','loss'}
    table_cells=max(1,sum(len(row) for row in rows)); ntable=len(flat_table)
    f=[]
    f += [len(ns[s]) for s in SECTION]
    f += sm(alln)+sm(qn)+sm(evn)+sm(an)
    f += [len(rows),cols,len(an),ans_matches,overlap_num,len(qtok&etok)/max(1,len(qtok|etok)),len(qtok),len(_tokens(ev)),len(atok),
          float(r['confidence']),float(bool(unit)),float('%' in ans or '%' in unit),float('$' in ans or '$' in unit),float(bool(ansn and ansn['negative'])),
          len(evn)/max(1,len(ev.split())),len(qn)/max(1,len(q.split())),ntable/table_cells,(len(ns['pre'])+1)/(len(ns['post'])+1),
          float(np.mean(perrow) if perrow else 0),sum(x>0 for x in perrow),max(perrow,default=0),len(uvals),max(0,ntable-len(uvals)),
          math.log1p(abs(ansn['v'])) if ansn else 0.,ansrank,near]
    for section in ('question','evidence','answer'):
        for typ in TYPES: f.append(float(sum(bool(n[typ]) for n in ns[section])))
    row_idx=[x[0] for x in flat_table]; col_idx=[x[1] for x in flat_table]
    f += [float(np.mean(row_idx) if row_idx else 0),float(np.mean(col_idx) if col_idx else 0),float(max(col_idx,default=0)),sum(x>0 for x in perrow)/max(1,len(rows)),
          len(set(col_idx))]
    f += [math.log1p(len(nums)*(len(nums)-1)//2),less/pair_total,equal/pair_total,greater/pair_total]
    f += [float(bool(qset&cues_up)),float(bool(qset&cues_dn)),float(bool(qset&{'than','compared','difference','ratio','versus','vs'})),float(bool(qset&{'percent','percentage','rate'})),float(bool(qset&{'year','years','quarter','period','annual','quarterly'})),
          float(bool(re.search(r'\b(?:19|20)\d{2}\b',ev))),float(bool(_tokens(ev)&financial)),float(bool(_tokens(ev)&{'than','compared','difference','versus','vs'})),float(bool(re.search(r'percent|percentage|%',alow))),float(bool(re.search(r'\$|dollar|usd',alow)))]
    f += [float(not bool(pre)),float(not bool(post)),float(not bool(rows))]
    ul=unit.lower(); f += [float('%' in ul or 'percent' in ul),float('$' in ul or 'dollar' in ul or 'usd' in ul),float(bool(ul) and not ('%' in ul or 'percent' in ul or '$' in ul or 'dollar' in ul or 'usd' in ul))]
    if len(f)!=96: raise AssertionError(f'graph schema {len(f)} != 96')
    a=np.asarray(f,dtype=np.float32)
    if not np.isfinite(a).all(): raise ValueError('nonfinite_graph_feature')
    return a

class FrozenFeatureBuilder:
    def __init__(self):
        self.vectorizer=HashingVectorizer(n_features=4096,alternate_sign=False,norm='l2',lowercase=True,ngram_range=(1,2),token_pattern=r"(?u)\b\w[\w.$%'-]*\b",dtype=np.float32)
    def _text(self,rec):
        rec=_safe(rec); r=rec['original_response']
        parts=[rec['question']]+_flatten(rec.get('pre_text',[]))+_flatten(rec.get('table_original',[]))+_flatten(rec.get('post_text',[]))
        parts += [str(r['answer_value']),str(r.get('unit') or ''),str(r['confidence'])]+_flatten(r.get('supporting_evidence',[]))
        return ' \n '.join(parts)
    def transform(self,records):
        from scipy.sparse import hstack
        text=self.vectorizer.transform([self._text(x) for x in records]).toarray().astype(np.float32,copy=False)
        graph=np.vstack([_graph(x) for x in records]).astype(np.float32)
        return np.concatenate([text,graph],axis=1),graph
