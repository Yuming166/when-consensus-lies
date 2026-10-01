#!/usr/bin/env python3
"""Run the V2 post-top-up backfill for immutable V1 HTTP 429/402 slots."""
import argparse, concurrent.futures, datetime, hashlib, json, os, sys, time
from pathlib import Path
sys.path.insert(0, '/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call/pecr_crossmodel_deepseek_v1_20261001/src')
import run_deepseek_collection as v1

ROOT = Path('/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call')
V1 = ROOT / 'pecr_crossmodel_deepseek_v1_20261001'
V2 = ROOT / 'pecr_crossmodel_deepseek_v2_complete_20261001'
MANIFEST = ROOT / 'pecr_bidirectional_development_v1_20260928/data/construction_manifest_dev_train.jsonl'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--endpoint', default='https://api.deepseek.com/v1/chat/completions')
    ap.add_argument('--key-env', default='DEEPSEEK_API_KEY')
    ap.add_argument('--model', default='deepseek-flash')
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    key = os.environ.get(a.key_env)
    if not key:
        raise SystemExit(f'missing env {a.key_env}')

    v1_rows, v1_slots = v1.build_slots(MANIFEST, 20260928)
    assert len(v1_rows) == 2225 and len(v1_slots) == 6675
    v1_ledger = [json.loads(x) for x in open(V1 / 'data/full_dev/raw_ledger_full_dev.jsonl')]
    assert len(v1_ledger) == 6675
    by_slot = {r['slot']: r for r in v1_ledger}
    eligible = [j for j in v1_slots if by_slot[j['slot']].get('http_status') in (429, 402)]
    assert len(eligible) == 2682, len(eligible)
    if a.limit:
        eligible = eligible[:a.limit]

    respdir = V2 / 'data/v2_responses'
    respdir.mkdir(parents=True, exist_ok=True)
    freeze = {
        'amendment': 'PROTOCOL_AMENDMENT_V3_BACKFILL.md',
        'base_ledger': str(V1 / 'data/full_dev/raw_ledger_full_dev.jsonl'),
        'base_ledger_sha256': hashlib.sha256((V1 / 'data/full_dev/raw_ledger_full_dev.jsonl').read_bytes()).hexdigest(),
        'eligibility_rule': 'v1_http_status_in_429_402_only',
        'seed': 20260928,
        'model': a.model,
        'endpoint': a.endpoint,
        'workers': a.workers,
        'eligible_slots': len(eligible),
        'slot_world': [{'slot': j['slot'], 'item_id': j['item_id'], 'world': j['world']} for j in eligible],
    }
    (V2 / 'data/BACKFILL_SELECTION_FREEZE.json').write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + '\n')

    def job(j):
        p = respdir / f"slot_{j['slot']:05d}.json"
        if p.exists():
            return None
        rec = v1.do_call(j, a.endpoint, key, a.model)
        # Attempt ID identifies the version; request body and its hash remain identical to V1.
        rec['attempt_id'] = f"deepseek-v2-backfill-{rec['slot']:05d}"
        rec['v2_backfill'] = True
        rec['v1_http_status'] = by_slot[j['slot']].get('http_status')
        p.write_text(json.dumps(rec, ensure_ascii=False, separators=(',', ':')) + '\n')
        return rec

    done = 0; t0 = time.time(); counts = {'http_200': 0, 'http_429': 0, 'http_402': 0, 'other': 0}
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(job, j) for j in eligible]
        for fut in concurrent.futures.as_completed(futs):
            rec = fut.result()
            done += 1
            if rec:
                s = rec.get('http_status')
                if s == 200: counts['http_200'] += 1
                elif s == 429: counts['http_429'] += 1
                elif s == 402: counts['http_402'] += 1
                else: counts['other'] += 1
            if done % 100 == 0:
                el = time.time() - t0
                print(json.dumps({'done': done, 'eligible': len(eligible), 'elapsed_s': round(el, 1), 'eta_s': round(el / done * (len(eligible) - done), 1), **counts}), flush=True)
    status = {'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'eligible_slots': len(eligible), 'records_seen': done, **counts}
    (V2 / 'data/BACKFILL_STATUS.json').write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps({'backfill_finished': True, **status}), flush=True)

if __name__ == '__main__':
    main()
