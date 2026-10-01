#!/usr/bin/env python3
"""Finite, sequential Qwen collection for frozen dev_train candidates only (runner V2)."""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, sys, time, fcntl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / 'TRAIN_OPERAND_ALIGNED_CANDIDATES_V1.jsonl'
LEDGER = HERE / 'raw_ledger.jsonl'
ENDPOINT = 'http://127.0.0.1:31518/v1/chat/completions'
MODEL = 'Qwen3.5-4B'
PARAMS = {'temperature': 0, 'top_p': 1, 'max_tokens': 384,
          'stream': False, 'response_format': {'type': 'json_object'}}
SYSTEM = ('You answer quantitative financial questions from only the supplied question and evidence. '
'Do not use outside knowledge. Do not reveal chain-of-thought. Return exactly one JSON object with keys: '
'answer_value, unit, confidence, supporting_evidence. answer_value must be a concise numeric answer as a string '
'(keep signs and decimal precision); unit must be a short string or null; confidence must be a number from 0 to 1; '
'supporting_evidence must be an array of at most three short verbatim snippets copied from the supplied evidence. '
'If the evidence is insufficient, set answer_value to an empty string, unit to null, confidence to 0, and '
'supporting_evidence to []. Do not add other keys or markdown.')
EXPECTED_COUNT = 2241
EXPECTED_SLOTS = 4482
EXPECTED_MANIFEST_SHA256 = '293ff0891de7a9f4c8b283c55cd3eddd0a95d4fa62d12bd46c255ae3de0aaa2f'
CHECKPOINT = HERE / 'FREEZE_CHECKPOINT.json'
CHECKPOINT_SHA = HERE / 'FREEZE_CHECKPOINT.sha256'
CONTRACT = HERE / 'RUN_CONTRACT_V2.md'
TESTS = HERE / 'offline_tests_v2.py'
FIXTURE = HERE / 'SYNTHETIC_PROMPT_FIXTURE.json'
IDENTITY = HERE / 'MODEL_IDENTITY.json'
LOCK = HERE / 'runner_v2.lock'


def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def canon(x: Any) -> bytes: return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
def utc() -> str: return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')

def load_candidates():
    raw = MANIFEST.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    manifest_hash = sha(raw)
    if manifest_hash != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError(f'manifest_hash_mismatch:{manifest_hash}')
    rows = [r for r in rows if r.get('partition') == 'dev_train']
    if len(rows) != EXPECTED_COUNT: raise RuntimeError(f'candidate_count_mismatch:{len(rows)}')
    return rows, manifest_hash

def verify_freeze():
    if not CHECKPOINT.exists() or not CHECKPOINT_SHA.exists():
        raise RuntimeError('freeze_checkpoint_missing')
    raw = CHECKPOINT.read_bytes()
    expected = CHECKPOINT_SHA.read_text().strip().split()[0]
    if sha(raw) != expected:
        raise RuntimeError('freeze_checkpoint_sidecar_mismatch')
    ck = json.loads(raw)
    for rel, expected_hash in ck['frozen_artifacts'].items():
        path = HERE / rel
        if not path.is_file() or sha(path.read_bytes()) != expected_hash:
            raise RuntimeError(f'frozen_artifact_hash_mismatch:{rel}')
    identity = json.loads(IDENTITY.read_text())
    root = Path(identity['artifact_root'])
    for item in identity['artifact_files']:
        path = root / item['path']
        if not path.is_file() or path.stat().st_size != item['bytes']:
            raise RuntimeError(f'model_artifact_missing_or_size_changed:{item["path"]}')
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != item['sha256']:
            raise RuntimeError(f'model_artifact_hash_changed:{item["path"]}')
    return ck

def acquire_run_lock():
    f = LOCK.open('a+')
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as e:
        f.close()
        raise RuntimeError('runner_already_active') from e
    return f

def render_prompt(r: dict, world: str) -> tuple[str, dict]:
    # Recursive input allow-list: only these primitive fields can enter a prompt.
    table_key = 'table_original' if world == 'original' else 'table_mutated'
    allowed = {
      'question': r.get('question'),
      'pre_text': r.get('pre_text', []),
      'table': r.get(table_key),
      'post_text': r.get('post_text', []),
    }
    def check(v):
        if isinstance(v, dict): raise TypeError('nested_dict_not_allowed')
        if isinstance(v, list):
            for z in v: check(z)
        elif not isinstance(v, (str, int, float, type(None), bool)):
            raise TypeError(f'unsupported_prompt_type:{type(v).__name__}')
    for value in allowed.values(): check(value)
    if not isinstance(allowed['question'], str) or not isinstance(allowed['table'], list):
        raise ValueError('missing_question_or_table')
    pre = '\n'.join(str(x) for x in allowed['pre_text'])
    post = '\n'.join(str(x) for x in allowed['post_text'])
    prompt = ('Answer the question using the evidence below. The answer may require arithmetic. '
              'Return only the required JSON object.\n\nQUESTION:\n' + allowed['question'] +
              '\n\nPRE-TEXT:\n' + pre + '\n\nTABLE (JSON):\n' +
              json.dumps(allowed['table'], ensure_ascii=False, separators=(',', ':')) +
              '\n\nPOST-TEXT:\n' + post)
    return prompt, allowed

_NUM = re.compile(r'^\s*(?:\(\s*)?[-+]?\s*\$?\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*%?\s*\)?\s*$')
def parse_answer_number(value: Any):
    if not isinstance(value, (str,int,float)) or isinstance(value,bool): return None
    s = str(value).strip()
    if not _NUM.fullmatch(s): return None
    negparen = s.startswith('(') and s.endswith(')')
    percent = '%' in s
    t = s.replace('$','').replace(',','').replace('%','').replace('(','').replace(')','').strip()
    try: x = float(t)
    except ValueError: return None
    if negparen: x = -abs(x)
    if not math.isfinite(x): return None
    # Percent suffix is retained as a distinct scale marker; only like-for-like pairs compare.
    return x, percent

def relation_pair_target(original: dict, mutated: dict, expected: str):
    if not original.get('valid') or not mutated.get('valid'):
        return {'status':'unscorable_invalid_answer'}
    if original['normalized_unit'] != mutated['normalized_unit'] or original['is_percent'] != mutated['is_percent']:
        return {'status':'unscorable_unit_mismatch'}
    delta = mutated['numeric_value'] - original['numeric_value']
    eps = 1e-8 * max(1.0, abs(original['numeric_value']))
    sign = 'up' if delta > eps else ('down' if delta < -eps else 'tie')
    risk = int(sign != expected)
    return {'status':'scorable','response_delta':delta,'response_direction':sign,
            'expected_direction':expected,'teacher_relation_risk':risk}

def parse_content(content: str):
    result = {'valid': False, 'errors': []}
    try: obj = json.loads(content)
    except Exception as e:
        result['errors'].append('invalid_json'); return result
    if not isinstance(obj, dict): result['errors'].append('not_object'); return result
    required = {'answer_value','unit','confidence','supporting_evidence'}
    if set(obj) != required:
        result['errors'].append('wrong_schema_keys')
        return result
    num = parse_answer_number(obj['answer_value'])
    if num is None or not str(obj['answer_value']).strip(): result['errors'].append('invalid_answer_value')
    unit = obj['unit']
    if unit is not None and not isinstance(unit,str): result['errors'].append('invalid_unit')
    conf = obj['confidence']
    if isinstance(conf,bool) or not isinstance(conf,(int,float)) or not math.isfinite(float(conf)) or not 0 <= float(conf) <= 1:
        result['errors'].append('invalid_confidence')
    ev = obj['supporting_evidence']
    if not isinstance(ev,list) or len(ev)>3 or not all(isinstance(x,str) for x in ev): result['errors'].append('invalid_supporting_evidence')
    if not result['errors']:
        result.update({'valid':True,'parsed':obj,'numeric_value':num[0],'is_percent':num[1],
                       'normalized_unit':None if unit is None else ' '.join(unit.lower().split())})
    return result

def record_hash(rec):
    clone = dict(rec); clone.pop('record_hash',None)
    return sha(canon(clone))

PREVIOUS_HASH = 'GENESIS'
def append_record(rec):
    global PREVIOUS_HASH
    rec['previous_record_hash'] = PREVIOUS_HASH
    rec['record_hash'] = record_hash(rec)
    line = canon(rec) + b'\n'
    with LEDGER.open('ab', buffering=0) as f:
        f.write(line); os.fsync(f.fileno())
    with LEDGER.open('rb') as f:
        f.seek(-len(line), os.SEEK_END)
        saved = f.readline()
    check = json.loads(saved)
    if check.get('record_hash') != record_hash(check) or check.get('previous_record_hash') != PREVIOUS_HASH:
        raise RuntimeError('ledger_readback_integrity_failure')
    PREVIOUS_HASH = rec['record_hash']

def next_slot():
    if not LEDGER.exists() or LEDGER.stat().st_size == 0: return 1
    # Contract V1 is one-shot: any non-empty ledger forbids a restart/retry.
    raise RuntimeError('ledger_not_empty_no_resume_or_retry')

def call_one(slot, row, world, manifest_sha):
    user, allow = render_prompt(row, world)
    req = {'model':MODEL,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':user}],**PARAMS}
    req_bytes = canon(req)
    attempt_id = f"slot-{slot:04d}"
    base = {'attempt_id':attempt_id,'slot':slot,'item_id':row.get('id'),'world':world,
            'utc_started':utc(),'endpoint':ENDPOINT,'model_requested':MODEL,'request':req,
            'request_sha256':sha(req_bytes),'allowlist_payload_sha256':sha(canon(allow)),
            'candidate_manifest_sha256':manifest_sha,'status':'started'}
    append_record(dict(base))
    try:
        session = requests.Session()
        session.trust_env = False  # Never route loopback requests through ambient proxy settings.
        resp = session.post(ENDPOINT, json=req, timeout=(10,180))
    except Exception as e:
        fail = {'attempt_id':attempt_id,'slot':slot,'item_id':row.get('id'),'world':world,
                'status':'transport_failure_stop','error_type':type(e).__name__,
                'error':str(e)[:500],'utc_finished':utc()}
        append_record(fail); raise RuntimeError(f'transport_failure_at_slot_{slot}') from e
    finished = {'attempt_id':attempt_id,'slot':slot,'item_id':row.get('id'),'world':world,
                'utc_finished':utc(),'http_status':resp.status_code,
                'raw_response_text':resp.text,'response_sha256':sha(resp.content),
                'request_sha256':base['request_sha256']}
    if resp.status_code != 200:
        finished['status']='http_failure_stop'; append_record(finished)
        raise RuntimeError(f'http_failure_at_slot_{slot}:{resp.status_code}')
    try: data = resp.json()
    except Exception:
        finished['status']='invalid_api_envelope_json_stop'; append_record(finished)
        raise RuntimeError(f'api_envelope_json_invalid_at_slot_{slot}')
    if not isinstance(data, dict):
        finished['status']='invalid_api_envelope_type_stop'; append_record(finished)
        raise RuntimeError(f'api_envelope_type_invalid_at_slot_{slot}')
    returned = data.get('model')
    finished['response_model'] = returned
    finished['usage'] = data.get('usage')
    if returned != MODEL:
        finished['status']='model_identity_mismatch_stop'; append_record(finished)
        raise RuntimeError(f'model_identity_mismatch_at_slot_{slot}')
    choices = data.get('choices')
    if not isinstance(choices,list) or len(choices)!=1 or not isinstance(choices[0],dict):
        finished['status']='invalid_choice_count_stop'; append_record(finished)
        raise RuntimeError(f'choice_count_invalid_at_slot_{slot}')
    msg = choices[0].get('message') or {}
    content = msg.get('content')
    finished['finish_reason'] = choices[0].get('finish_reason')
    if not isinstance(content,str):
        finished['status']='invalid_content_type_stop'; append_record(finished)
        raise RuntimeError(f'content_type_invalid_at_slot_{slot}')
    parsed = parse_content(content)
    finished['parsed'] = parsed
    finished['status'] = 'parsed_valid' if parsed['valid'] else 'parse_invalid_continue'
    append_record(finished)
    if slot <= 2 and not parsed['valid']:
        raise RuntimeError(f'canary_parse_invalid_at_slot_{slot}')
    return parsed

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    ck = verify_freeze()
    lock_handle = acquire_run_lock()
    rows, mh=load_candidates()
    if len(rows) * 2 != EXPECTED_SLOTS: raise RuntimeError('slot_count_mismatch')
    if next_slot()!=1: raise RuntimeError('unexpected_slot')
    slots=[]
    for r in rows: slots += [(r,'original'),(r,'mutated')]
    if args.dry_run:
        for i,(r,w) in enumerate(slots,1):
            u,a=render_prompt(r,w)
            req={'model':MODEL,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':u}],**PARAMS}
            print(json.dumps({'slot':i,'id':r['id'],'world':w,'request_sha256':sha(canon(req)),
                              'allowlist_keys':sorted(a),'prompt_chars':len(u),'model':MODEL},ensure_ascii=False))
        return
    for i,(r,w) in enumerate(slots,1):
        call_one(i,r,w,mh)
        if i == 2: print('canary_pair_passed; continuing fixed dev_train batch under same frozen contract', flush=True)
    print(f'dev_train_collection_done slots={len(slots)} manifest_sha256={mh}')
if __name__=='__main__': main()
