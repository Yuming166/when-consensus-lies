"""Small shared-trunk multi-task MLP using NumPy only; CPU deterministic mini-batch Adam."""
from __future__ import annotations
import numpy as np

def _sigmoid(z): return 1.0/(1.0+np.exp(-np.clip(z,-30,30)))
def _softmax(z):
    z=z-z.max(axis=1,keepdims=True); e=np.exp(np.clip(z,-40,40)); return e/e.sum(axis=1,keepdims=True)

class JointStudent:
    def __init__(self,input_dim,hidden=48,seed=20260926,l2=1e-3,epochs=120,lr=0.003,batch_size=64):
        self.input_dim=input_dim; self.hidden=hidden; self.seed=seed; self.l2=l2; self.epochs=epochs; self.lr=lr; self.batch_size=batch_size
    def fit(self,X,y,relation_risk=None,relation_type=None,delta=None,fixed_risk=None,aux_weight=None,shuffle_delta=None,
            lambda_risk=0.,lambda_type=0.,lambda_delta=0.,lambda_fixed=0.,lambda_shuffle=0.,main_mask=None,use_y=True):
        X=np.asarray(X,dtype=np.float32); n,d=X.shape
        rng=np.random.default_rng(self.seed)
        params={'W1':rng.normal(0,np.sqrt(2/max(1,d)),(d,self.hidden)).astype(np.float32),'b1':np.zeros(self.hidden,np.float32),
          'Wy':rng.normal(0,.05,(self.hidden,1)).astype(np.float32),'by':np.zeros(1,np.float32),
          'Wr':rng.normal(0,.05,(self.hidden,1)).astype(np.float32),'br':np.zeros(1,np.float32),
          'Wt':rng.normal(0,.05,(self.hidden,4)).astype(np.float32),'bt':np.zeros(4,np.float32),
          'Wd':rng.normal(0,.05,(self.hidden,1)).astype(np.float32),'bd':np.zeros(1,np.float32),
          'Wf':rng.normal(0,.05,(self.hidden,1)).astype(np.float32),'bf':np.zeros(1,np.float32),
          'Ws':rng.normal(0,.05,(self.hidden,1)).astype(np.float32),'bs':np.zeros(1,np.float32)}
        m={k:np.zeros_like(v) for k,v in params.items()}; v={k:np.zeros_like(x) for k,x in params.items()}; step=0
        y=np.asarray(y,dtype=np.float32).reshape(-1,1)
        main=np.ones(n,np.float32) if main_mask is None else np.asarray(main_mask,dtype=np.float32).reshape(-1)
        def arr(a,cols=1): return None if a is None else np.asarray(a,dtype=np.float32).reshape(n,cols)
        rr=arr(relation_risk); dd=arr(delta); fr=arr(fixed_risk); sd=arr(shuffle_delta)
        rt=None if relation_type is None else np.asarray(relation_type,dtype=np.int64).reshape(-1)
        aw=np.ones((n,1),np.float32) if aux_weight is None else np.asarray(aux_weight,dtype=np.float32).reshape(n,1)
        for epoch in range(self.epochs):
            order=rng.permutation(n)
            for start in range(0,n,self.batch_size):
                ix=order[start:start+self.batch_size]; xb=X[ix]; h0=xb@params['W1']+params['b1']; h=np.tanh(h0)
                grads={k:np.zeros_like(z) for k,z in params.items()}; dh=np.zeros_like(h); count=len(ix)
                def binary(head,tar,mask,weight,lam):
                    nonlocal dh
                    if tar is None or lam==0: return
                    z=h@params['W'+head]+params['b'+head]; pr=_sigmoid(z); mk=mask[ix].reshape(-1,1)*weight[ix]
                    denom=max(1.,float(mk.sum())); g=(pr-tar[ix])*mk*(lam/denom)
                    grads['W'+head]+=h.T@g; grads['b'+head]+=g.sum(axis=0); dh+=g@params['W'+head].T
                if use_y:
                    z=h@params['Wy']+params['by']; pr=_sigmoid(z); mk=main[ix].reshape(-1,1); denom=max(1.,float(mk.sum())); g=(pr-y[ix])*mk/denom
                    grads['Wy']+=h.T@g; grads['by']+=g.sum(axis=0); dh+=g@params['Wy'].T
                ones=np.ones(n,np.float32)
                binary('r',rr,ones,aw,lambda_risk)
                binary('f',fr,ones,aw,lambda_fixed)
                binary('s',sd,ones,aw,lambda_shuffle)
                if dd is not None and lambda_delta:
                    z=h@params['Wd']+params['bd']; err=z-dd[ix]; abs_err=np.abs(err); hub=np.where(abs_err<=1.,err, np.sign(err)); mk=aw[ix]
                    denom=max(1.,float(mk.sum())); g=hub*mk*(lambda_delta/denom)
                    grads['Wd']+=h.T@g; grads['bd']+=g.sum(axis=0); dh+=g@params['Wd'].T
                if rt is not None and lambda_type:
                    z=h@params['Wt']+params['bt']; pr=_softmax(z); valid=(rt[ix]>=0)&(rt[ix]<4); mk=valid.astype(np.float32)*aw[ix,0]
                    denom=max(1.,float(mk.sum())); yy=np.zeros_like(pr); yy[np.arange(len(ix))[valid],rt[ix][valid]]=1
                    g=(pr-yy)*mk[:,None]*(lambda_type/denom)
                    grads['Wt']+=h.T@g; grads['bt']+=g.sum(axis=0); dh+=g@params['Wt'].T
                dh0=dh*(1-h*h)
                grads['W1']+=xb.T@dh0; grads['b1']+=dh0.sum(axis=0)
                for k in params:
                    if k.startswith('W'): grads[k]+=self.l2*params[k]
                step+=1
                for k in params:
                    m[k]=.9*m[k]+.1*grads[k]; v[k]=.999*v[k]+.001*(grads[k]**2)
                    mh=m[k]/(1-.9**step); vh=v[k]/(1-.999**step)
                    params[k]-=self.lr*mh/(np.sqrt(vh)+1e-8)
        self.params_=params
        return self
    def predict_error(self,X):
        p=self.params_; h=np.tanh(np.asarray(X,dtype=np.float32)@p['W1']+p['b1']); return _sigmoid(h@p['Wy']+p['by']).ravel()
    def predict_teacher(self,X,head='r'):
        p=self.params_; h=np.tanh(np.asarray(X,dtype=np.float32)@p['W1']+p['b1']); key={'r':'Wr','f':'Wf','s':'Ws','d':'Wd','t':'Wt'}[head]
        b={'r':'br','f':'bf','s':'bs','d':'bd','t':'bt'}[head]
        z=h@p[key]+p[b]
        return _softmax(z) if head=='t' else (z.ravel() if head=='d' else _sigmoid(z).ravel())
