from pathlib import Path
import csv,json,random,hashlib
P=Path(__file__).resolve().parents[1]
meta=json.loads((P/'historical/PACKAGE_METADATA.json').read_text());frame=P.parent/'pecr_benchmark_release_v1_20261002/intervention/edit_spec.jsonl';by={}
for l in frame.open():
 r=json.loads(l);by.setdefault(r['source_group'],[]).append(r)
rng=random.Random(20260928);a=[rng.choice(by[g]) for g in sorted(by)];rng.shuffle(a)
assert [r['item_id'] for r in a[:50]]==meta['item_ids']
assert len({r['source_group'] for r in a[:50]})==50
for p in (P/'forms').glob('*.csv'):
 with p.open() as f:rows=list(csv.DictReader(f))
 assert [r['item_id'] for r in rows]==meta['item_ids']
 assert all(not v for r in rows for k,v in r.items() if k not in ('review_id','item_id','source_group'))
assert hashlib.sha256(frame.read_bytes()).hexdigest()==json.loads((P/'RECOVERY_AND_SAMPLING.json').read_text())['frame_sha256']
print('PASS: exact historical sample; 50 IDs/groups; new forms blank, no fabricated judgments')
