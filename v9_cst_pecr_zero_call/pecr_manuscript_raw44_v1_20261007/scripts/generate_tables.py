import csv,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];B=P.parent;R=B/'pecr_two_track_benchmark_release_v2_20261007';C=B/'pecr_raw44_attribution_controls_v1_20261007'
D=json.loads((C/'results/RESULTS.json').read_text()); sources=[C/'results/RESULTS.json',R/'results/primary_contrasts.csv',R/'reference/source_reports/two_track_component_ablation.json',R/'coverage/coverage_summary.json',R/'schemas/feature_schema.json']
T=P/'tables';T.mkdir(exist_ok=True)
def table(name,caption,label,cols,header,rows,note='',wide=True):
 env='table*' if wide else 'table'
 txt='\\begin{'+env+'}[t]\n\\centering\\small\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{@{}'+cols+'@{}}\n\\toprule\n'+header+'\\\\\n\\midrule\n'+'\\\\\n'.join(rows)+'\\\\\n\\bottomrule\n\\end{tabular}\n'
 if note:txt+='\\par\\vspace{3pt}\\begin{minipage}{'+('\\textwidth' if wide else '\\columnwidth')+'}\\footnotesize '+note+'\\end{minipage}\n'
 txt+='\\end{'+env+'}\n';(T/name).write_text(txt)
methods=[('g96','Original-answer G96',1),('g96_construction','G96 + construction metadata',1),('g96_raw16','G96 + Raw16',3),('raw','Raw: G96 + Raw16 + $(h,t)$',3),('curve','G96 + Curve29',3),('raw_plus_arithmetic44',r'\textbf{PECR: Raw + Arithmetic44}',3)]
rows=[]
for k,label,calls in methods:
 vals=[]
 for tr in ['qwen35','deepseek_v41']:
  vals.extend(f'{D[tr]["metrics"][k][m]:.4f}' for m in ['auroc','auprc'])
 if k=='raw_plus_arithmetic44':vals=[r'\textbf{'+v+'}' for v in vals]
 rows.append(f'{label} & {D["qwen35"]["matrices"][k]["dim"]} & {calls} & '+' & '.join(vals))
table('main_results.tex','Error ranking on the two generation-aligned response tracks. All methods use the same strict items, five source-group folds, and fixed HGB within each track.','tab:main','lrrrrrr',r'& & & \multicolumn{2}{c}{Qwen3.5-4B} & \multicolumn{2}{c}{DeepSeek V4.1 Flash}\\\cmidrule(lr){4-5}\cmidrule(l){6-7} Input & Dim. & Calls & AUROC & AP & AUROC & AP',rows,r'Qwen: 1,597 items, 413 groups, 1,258 errors; DeepSeek: 1,537 items, 407 groups, 837 errors. Calls count the response slots consumed by a detector. Construction and its expected direction are supplied benchmark information. AP uses error as the positive class.')
pcs=list(csv.DictReader((R/'results/primary_contrasts.csv').open()))
rows=[]
for r in pcs:
 track='Qwen3.5-4B' if r['track'].startswith('Qwen') else 'DeepSeek V4.1 Flash'
 baseline='Raw' if r['contrast'].endswith(' - Raw') else 'Curve29'
 v=lambda k:float(r[k])
 rows.append(f'{track} & {baseline} & {v("delta_auroc"):+.4f} & [{v("adjusted_ci_low"):+.4f}, {v("adjusted_ci_high"):+.4f}] & {v("delta_auprc"):+.4f} & [{v("adjusted_auprc_ci_low"):+.4f}, {v("adjusted_auprc_ci_high"):+.4f}]')
table('primary_contrasts.tex','Paired gains of PECR over equal-call comparators. Differences subtract the comparator from PECR.','tab:primary','llrlrl',r'Track & Comparator & $\Delta$AUROC & Adjusted 95\% CI & $\Delta$AP & Adjusted 95\% CI',rows,r'Intervals retain the saved analyses: 5,000 paired source-group draws; six-contrast campaign correction for Qwen and three-contrast correction for DeepSeek, separately by metric. They condition on saved OOF predictions.')
cn=[('construction_minus_g96',r'Construction model $-$ G96'),('raw16_minus_g96',r'(G96 + Raw16) $-$ G96'),('edit_minus_raw16',r'Raw $-$ (G96 + Raw16)'),('raw_minus_construction',r'Raw $-$ construction model')]
rows=[]
for k,l in cn:
 vals=[]
 for tr in ['qwen35','deepseek_v41']:
  v=D[tr]['contrasts'][k]['auroc'];vals.extend([f'{v["delta"]:+.4f}',f'[{v["familywise_ci"][0]:+.4f}, {v["familywise_ci"][1]:+.4f}]'])
 rows.append(l+' & '+' & '.join(vals))
table('controls.tex',r'Attribution controls on the same strict cohorts. The construction model is G96 + $[\mathbb{I}(e=1),h,t]$ and consumes no edited-world responses.','tab:controls','lrlrl',r'& \multicolumn{2}{c}{Qwen3.5-4B} & \multicolumn{2}{c}{DeepSeek V4.1 Flash}\\\cmidrule(lr){2-3}\cmidrule(l){4-5} Contrast & $\Delta$AUROC & Adjusted 95\% CI & $\Delta$AUROC & Adjusted 95\% CI',rows,r'Fixed post-hoc controls: 10,000 paired source-group bootstrap draws and Bonferroni correction over these four contrasts in both tracks (eight comparisons). AUROC and AP form separate families. G96 includes the original answer; this control isolates added construction descriptors, not all possible construction information.')
# Component ablations from unrounded saved JSON.
abl=json.loads((R/'reference/source_reports/two_track_component_ablation.json').read_text())['tracks']
for metric,suffix in [('auroc',''),('auprc','_ap')]:
 rows=[]
 for k,l in [('raw44_full','Full PECR'),('drop_worldwise','w/o worldwise (24)'),('drop_joint','w/o cross-world (16)'),('drop_question','w/o question cues (4)')]:
  vals=[]
  for tr in ['qwen35','deepseek_v41']:
   x=abl[tr];vals.append(f'{x["metrics"][k][metric]:.4f}')
   if k=='raw44_full':vals.append('---')
   else:
    v=x['source_group_bootstrap']['contrasts'][k];ci=v['family6_ci95_'+metric]
    vals.append(f'{v["delta_"+metric]:+.4f} [{ci[0]:+.4f},{ci[1]:+.4f}]')
  rows.append(l+' & '+str(abl['qwen35']['dimensions'][k])+' & '+' & '.join(vals))
 met='AUROC' if metric=='auroc' else 'AP'
 table('ablations'+suffix+'.tex','Fixed component removals from Arithmetic44 ('+met+'). Differences are full PECR minus the ablated variant.','tab:ablation'+suffix.replace('_','-'),'lrrlrl',r'& & \multicolumn{2}{c}{Qwen3.5-4B} & \multicolumn{2}{c}{DeepSeek V4.1 Flash}\\\cmidrule(lr){3-4}\cmidrule(l){5-6} Variant & Dim. & '+met+r' & $\Delta$ [adjusted 95\% CI] & '+met+r' & $\Delta$ [adjusted 95\% CI]',rows,r'All variants retain the same Raw block. Intervals use 5,000 paired source-group draws and Bonferroni correction across three block removals in two tracks (six comparisons per metric). A positive difference favors retaining the block.')
# clean legacy diagnostic table
rows=[]
for k,l in [('g96','G96'),('legacy_g96_construction',r'G96 + $[\mathbb{I}(e=1),\mu,h,t]$'),('legacy_g96_raw17','G96 + historical Raw17'),('legacy_g96_raw17_edit',r'G96 + historical Raw17 + $(h,t)$')]:
 vals=[]
 for tr in D:vals.extend(f'{D[tr]["metrics"][k][m]:.4f}' for m in ['auroc','auprc'])
 rows.append(l+' & '+str(D['qwen35']['matrices'][k]['dim'])+' & '+' & '.join(vals))
table('legacy_controls.tex','Historical-descriptor compatibility controls, refitted on the current cohorts. These are excluded from the main clean comparison.','tab:legacy','lrrrrr',r'& & \multicolumn{2}{c}{Qwen} & \multicolumn{2}{c}{DeepSeek}\\\cmidrule(lr){3-4}\cmidrule(l){5-6} Input & Dim. & AUROC & AP & AUROC & AP',rows,r'$\mu$ denotes the inherited Raw17[16] scalar named construction\_absolute\_delta. Its alignment with repaired edits is unresolved; it is neither substituted by $|h|$ nor used by the proposed primary method.')
# Recompute response pattern counts from exact source features and separate labels.
import numpy as np
patterns={}
for tr in D:
 f=np.load(R/f'data/{tr}_features_label_blind.npz');c=f['Curve33'];lm={r['item_id']:int(r['error']) for r in csv.DictReader((R/f'labels/{tr}_labels.csv').open()) if r['error'] != ''};y=np.array([lm[i] for i in f['item_ids']])
 fl=(c[:,8]>0).astype(int)+(c[:,9]>0).astype(int);al=(c[:,6]>0).astype(int)+(c[:,7]>0).astype(int)
 masks=[(fl==0)&(al==2),(fl==0)&(al==1),(fl==0)&(al==0),fl==1,fl==2]
 assert np.all(np.sum(masks,axis=0)==1)
 patterns[tr]=[(int(m.sum()),float(y[m].mean()*100)) for m in masks]
rows=[]
for j,l in enumerate(['Both sides aligned','Mixed directions','Both sides reversed','One side flat','Both sides flat']):rows.append(l+' & '+' & '.join(f'{patterns[tr][j][0]:,} ({patterns[tr][j][1]:.1f})' for tr in ['qwen35','deepseek_v41']))
table('patterns.tex','Response patterns and original-answer errors.','tab:patterns','lrr',r'Pattern & Qwen $N$ (error \%) & DeepSeek $N$ (error \%)',rows,r'All strict items are retained. Categories are mutually exclusive; flatness is exact zero change. Alignment uses the saved expected direction.',wide=True)
cov=json.loads((R/'coverage/coverage_summary.json').read_text());rows=[]
for label,key in [('Attempted','attempted'),('Strict','strict'),('Source groups (strict)','strict_groups'),('Errors (strict)','strict_error'),('Correct (strict)','strict_correct'),('Attempted, excluded','strict_excluded')]:rows.append(label+' & '+' & '.join(f'{cov[t][key]:,}' for t in ['qwen35','deepseek_v41']))
rows.append('Strict / attempted & 94.0\\% & 96.2\\%')
table('coverage.tex','Model-specific coverage in the repaired benchmark.','tab:coverage','lrr',r'Population & Qwen & DeepSeek',rows,wide=False)
rows=['Requested construction frame & 2,225 & 2,225','Unrequested records & 16 & 16','Requested, not attempted & 526 & 628','Attempted, strict & 1,597 & 1,537','Attempted, excluded & 102 & 60']
table('frame.tex','Full construction-frame accounting. The last three rows partition the 2,225 requested candidates per track; unrequested records remain separate.','tab:frame','lrr',r'Partition & Qwen & DeepSeek',rows,wide=False)
rows=[]
for k,l in cn:
 vals=[]
 for tr in ['qwen35','deepseek_v41']:
  v=D[tr]['contrasts'][k]['auprc'];vals.extend([f'{v["delta"]:+.4f}',f'[{v["familywise_ci"][0]:+.4f}, {v["familywise_ci"][1]:+.4f}]'])
 rows.append(l+' & '+' & '.join(vals))
table('controls_ap.tex','AP attribution controls with the same eight-comparison correction as Table~\\ref{tab:controls}.','tab:controls-ap','lrlrl',r'& \multicolumn{2}{c}{Qwen} & \multicolumn{2}{c}{DeepSeek}\\\cmidrule(lr){2-3}\cmidrule(l){4-5} Contrast & $\Delta$AP & Adjusted 95\% CI & $\Delta$AP & Adjusted 95\% CI',rows)
# Audit all generated tables and numeric sources.
sources += [R/f'data/{t}_features_label_blind.npz' for t in D]+[R/f'labels/{t}_labels.csv' for t in D]+[R/'tables/raw44_component_ablation.tex']
(P/'audit/TABLE_SOURCES.json').write_text(json.dumps({'sources':{str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'outputs':{str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in T.glob('*.tex')}},indent=2)+'\n')
print('Tables generated:',len(list(T.glob('*.tex'))))
