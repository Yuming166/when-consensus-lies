import csv, hashlib, json, platform, time
from pathlib import Path
from itertools import combinations
import numpy as np
import sklearn, scipy
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from threadpoolctl import threadpool_limits

P = Path(__file__).resolve().parents[1]
R = P.parent / 'pecr_two_track_benchmark_release_v2_20261007'
O = P / 'results'
def write(p, x):
    p.write_text(json.dumps(x, indent=2, allow_nan=False)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def npz(p):
    with np.load(p, allow_pickle=False) as f: return {k:f[k].copy() for k in f.files}
def csvrows(p):
    with p.open(newline='') as f: return list(csv.DictReader(f))

def evaluator(y, p):
    # Exact weighted metrics with tied scores; validate against sklearn below.
    order = np.argsort(-p, kind='stable')
    starts = np.r_[0, np.flatnonzero(np.diff(p[order]))+1]
    yp = y[order]; yn = 1-yp
    def evaluate(w):
        pos = np.add.reduceat(w[order]*yp, starts)
        neg = np.add.reduceat(w[order]*yn, starts)
        tp = pos.cumsum(); fp = neg.cumsum()
        if tp[-1] == 0 or fp[-1] == 0: return np.array([np.nan,np.nan])
        auc = np.sum(pos*(fp[-1]-fp+neg*.5))/(tp[-1]*fp[-1])
        ap = np.sum(pos*np.divide(tp,tp+fp,out=np.zeros_like(tp),where=(tp+fp)>0))/tp[-1]
        return np.array([auc,ap])
    return evaluate

def main():
    if O.exists(): raise RuntimeError('Refusing to overwrite results')
    O.mkdir()
    protocol=json.loads((P/'protocol/PROTOCOL.json').read_text())
    protocol_hash=sha(P/'protocol/PROTOCOL.json')
    assert protocol_hash==(P/'protocol/PROTOCOL.sha256').read_text().strip()
    assert all(sha(R/k)==v for k,v in protocol['source_sha256'].items())
    params=json.loads((P/'protocol/HGB_PARAMS.json').read_text())['parameters']
    runtime={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'fits':0,'status':'RUNNING'}
    start=time.time(); allr={}; metrics_rows=[]; contrast_rows=[]
    for track in protocol['tracks']:
        f=npz(R/f'data/{track}_features_label_blind.npz'); ids=f['item_ids'].astype(str)
        groups=f['groups'].astype(str); folds=f['outer_fold']; G=f['G96']; C=f['Curve33']; A=f['Arithmetic44']
        labels=csvrows(R/f'labels/{track}_labels.csv'); lm={r['item_id']:r for r in labels}
        y=np.array([int(lm[i]['error']) for i in ids]); n=len(y)
        assert len(set(ids))==n and np.array_equal(f['raw17'],C[:,:17])
        X={'g96':G.copy(),'g96_construction':np.c_[G,C[:,[15,18,17]]],
           'g96_raw16':np.c_[G,C[:,:16]],'raw':np.c_[G,C[:,:16],C[:,[18,17]]],
           'curve':np.c_[G,C[:,[j for j in range(33) if j not in (16,24,25,30)]]],
           'raw_plus_arithmetic44':np.c_[G,C[:,:16],C[:,[18,17]],A],
           'legacy_g96_construction':np.c_[G,C[:,[15,16,18,17]]],
           'legacy_g96_raw17':np.c_[G,C[:,:17]],'legacy_g96_raw17_edit':np.c_[G,C[:,:17],C[:,[18,17]]]}
        assert all(v.shape==(n,protocol['methods'][k]) and np.isfinite(v).all() for k,v in X.items())
        assert all(not np.shares_memory(a,b) for a,b in combinations([G,C,A,*X.values()],2))
        pred={k:np.full(n,np.nan) for k in X}; support=[]
        for fold in range(5):
            tr=folds!=fold; te=~tr
            assert not set(groups[tr])&set(groups[te]) and set(y[te])=={0,1}
            support.append({'fold':fold,'n':int(te.sum()),'groups':len(set(groups[te])),'error':int(y[te].sum()),'correct':int((1-y[te]).sum())})
            with threadpool_limits(limits=1):
                for name,x in X.items():
                    m=HistGradientBoostingClassifier(**params).fit(x[tr],y[tr])
                    pred[name][te]=m.predict_proba(x[te])[:,1]
                    assert m.n_iter_==250
                    runtime['fits']+=1;runtime['last_fit']=[track,name,fold];write(O/'RUNTIME.json',runtime)
            print(track,fold,'complete',runtime['fits'],'fits',flush=True)
        ref=npz(R/f'reference/oof/{track}_oof_scores_label_blind.npz')
        exact={k:{'exact':bool(np.array_equal(pred[k],ref[k])),'max_abs_diff':float(abs(pred[k]-ref[k]).max())} for k in protocol['refit_exact_checks']}
        assert all(np.isfinite(p).all() for p in pred.values())
        np.savez_compressed(O/f'{track}_OOF.npz',item_ids=ids,groups=groups,outer_fold=folds,y=y,**pred)
        with (O/f'{track}_OOF.csv').open('w',newline='') as out:
            w=csv.writer(out);w.writerow(['row_index','item_id','source_group','outer_fold','error',*pred])
            w.writerows([i,ids[i],groups[i],folds[i],y[i],*[p[i] for p in pred.values()]] for i in range(n))
        funcs={k:evaluator(y,p) for k,p in pred.items()}
        ones=np.ones(n);point={k:fn(ones) for k,fn in funcs.items()}
        for k,p in pred.items(): assert np.allclose(point[k],[roc_auc_score(y,p),average_precision_score(y,p)],rtol=0,atol=1e-13)
        ug,gi=np.unique(groups,return_inverse=True);rng=np.random.default_rng(protocol['bootstrap']['seed']);B=protocol['bootstrap']['B']
        draws={k:np.full((B,2),np.nan) for k in pred}
        for b in range(B):
            wg=np.bincount(rng.integers(len(ug),size=len(ug)),minlength=len(ug));w=wg[gi].astype(float)
            for k,fn in funcs.items():
                draws[k][b]=fn(w)
                if b==0:
                    assert np.allclose(draws[k][b],[roc_auc_score(y,pred[k],sample_weight=w),average_precision_score(y,pred[k],sample_weight=w)],rtol=0,atol=1e-13)
        result={'support':{'n':n,'groups':len(ug),'error':int(y.sum()),'correct':int((1-y).sum())},'fold_support':support,'reference_reproduction':exact,'matrices':{k:{'dim':v.shape[1],'sha256':hashlib.sha256(v.tobytes()).hexdigest()} for k,v in X.items()},'metrics':{},'contrasts':{}}
        for k in pred:
            result['metrics'][k]={}
            for j,metric in enumerate(['auroc','auprc']):
                result['metrics'][k][metric]=float(point[k][j]);result['metrics'][k][metric+'_ci95']=np.nanquantile(draws[k][:,j],[.025,.975]).tolist()
            metrics_rows.append({'track':track,'method':k,'dim':X[k].shape[1],**{metric:float(point[k][j]) for j,metric in enumerate(['auroc','auprc'])}})
        for k,(a,b) in protocol['controls'].items():
            result['contrasts'][k]={}
            for j,metric in enumerate(['auroc','auprc']):
                diff=draws[a][:,j]-draws[b][:,j];lo,hi=np.nanquantile(diff,[.025,.975]);al,ah=np.nanquantile(diff,protocol['bootstrap']['familywise_quantiles'])
                v={'delta':float(point[a][j]-point[b][j]),'ci95':[float(lo),float(hi)],'familywise_ci':[float(al),float(ah)]}
                result['contrasts'][k][metric]=v;contrast_rows.append({'track':track,'contrast':k,'metric':metric,'delta':v['delta'],'ci95_lo':lo,'ci95_hi':hi,'familywise_lo':al,'familywise_hi':ah})
        result['bootstrap_valid_draws']=int(np.isfinite(next(iter(draws.values()))[:,0]).sum())
        allr[track]=result;write(O/f'{track}_RESULTS.json',result);write(O/'RESULTS.json',allr)
        print(track,'bootstrap complete',flush=True)
    for name,rows in [('METRICS.csv',metrics_rows),('CONTRASTS.csv',contrast_rows)]:
        with (O/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    assert runtime['fits']==protocol['planned_fits']
    assert all(sha(R/k)==v for k,v in protocol['source_sha256'].items())
    assert sha(P/'protocol/PROTOCOL.json')==protocol_hash
    runtime.update(status='COMPLETE',elapsed_seconds=time.time()-start,source_hashes_unchanged=True)
    write(O/'RUNTIME.json',runtime)
    exact=all(v['exact'] for r in allr.values() for v in r['reference_reproduction'].values())
    write(O/'VALIDATION.json',{'status':'PASS' if exact else 'RUNTIME_DIFFERENCES','exact_primary_refits':exact,'planned_90_fits_completed':True,'finite_independent_matrices':True,'no_group_cross_fold':True,'original_ids_labels_folds_preserved':True,'bootstrap_matches_sklearn':True,'source_hashes_unchanged':True,'no_API_no_gold_no_holdout':True})
    print('COMPLETE',runtime,flush=True)
if __name__=='__main__':main()
