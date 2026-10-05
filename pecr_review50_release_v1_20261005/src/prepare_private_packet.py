"""Export the original blinded review materials locally, never to GitHub."""
from pathlib import Path
import argparse,json,hashlib,html
P=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--historical-packet',type=Path,required=True);ap.add_argument('--outdir',type=Path,required=True);a=ap.parse_args()
r=json.loads((P/'RECOVERY_AND_SAMPLING.json').read_text())
assert hashlib.sha256(a.historical_packet.read_bytes()).hexdigest()==r['private_source_packet_sha256']
assert not a.outdir.exists() and a.outdir.is_absolute() and not a.outdir.resolve().is_relative_to(P.parent.resolve())
rows=[json.loads(l) for l in a.historical_packet.open()];ids=json.loads((P/'historical/PACKAGE_METADATA.json').read_text())['item_ids'];assert [x['item_id'] for x in rows]==ids
allowed={'review_id','item_id','source_group','question','pre_text','post_text','table_original','table_positive','table_negative','edited_cell','original_literal','positive_literal','negative_literal','operation_type','program_direction','construction_status','review_fields'}
assert all(set(x)<=allowed for x in rows)
a.outdir.mkdir(mode=0o700,parents=True)
(a.outdir/'BLINDED_MATERIALS.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
parts=['<!doctype html><meta charset="utf-8"><title>PECR 50-item blinded review</title><style>body{font:16px Arial;max-width:1200px;margin:auto}section{page-break-before:always;border-top:2px solid;padding:25px}table{border-collapse:collapse}td{border:1px solid;padding:6px}pre{white-space:pre-wrap}</style><h1>50-item construction review — no model answers or error labels</h1>']
for n,x in enumerate(rows,1):
 parts.append('<section><h2>'+html.escape(f"{n}. {x['item_id']} — {x['review_id']}")+'</h2><h3>'+html.escape(x['question'])+'</h3>')
 for field in ['pre_text','post_text']:
  parts.append('<h4>'+field+'</h4><pre>'+html.escape(json.dumps(x[field],ensure_ascii=False,indent=2))+'</pre>')
 for world in ['original','positive','negative']:
  parts.append('<h3>'+world+'</h3><table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(c))+'</td>' for c in row)+'</tr>' for row in x['table_'+world])+'</table>')
 parts.append('<h4>Saved construction metadata (direction is exposed)</h4><pre>'+html.escape(json.dumps({k:x[k] for k in ['edited_cell','original_literal','positive_literal','negative_literal','operation_type','program_direction']},ensure_ascii=False,indent=2))+'</pre></section>')
(a.outdir/'REVIEW.html').write_text('\n'.join(parts));print(a.outdir/'REVIEW.html')
