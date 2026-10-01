import sys,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from feature_builder import FrozenFeatureBuilder, GRAPH_FEATURE_NAMES
from label_policy import label_one,parse_numeric
from joint_student import JointStudent

def fixture(answer='12.5',unit='%',conf=.8):
 return {'question':'What was the increase in 2020 compared with 2019?','pre_text':['Revenue was $100.0 million in 2019.'],
  'table_original':[['Year','Revenue'],['2019','$100.0'],['2020','$112.5']], 'post_text':['Annual revenue grew.'],
  'original_response':{'answer_value':answer,'unit':unit,'confidence':conf,'supporting_evidence':['Revenue was $100.0 million in 2019.']}}
def run():
 assert len(GRAPH_FEATURE_NAMES)==96
 assert parse_numeric('(1,200.50)')==parse_numeric('-1200.50')
 assert label_one('12.50001','12.5')[0]==1 and label_one('0.125','12.5')[0]==0 and label_one('N/A','1')[0] is None
 b=FrozenFeatureBuilder(); X,G=b.transform([fixture(),fixture('10','$',.2)])
 assert X.shape==(2,4192) and G.shape==(2,96) and np.isfinite(X).all()
 y=np.array([0,1,0,1,1,0],np.float32); d=np.array([-1,1,0,0,1,-1],np.float32); rr=np.array([0,1,0,1,1,0],np.float32)
 net=JointStudent(X.shape[1],hidden=8,seed=17,epochs=3).fit(X[:2].repeat(3,axis=0),y,delta=d,relation_risk=rr,lambda_delta=.5,lambda_risk=.2)
 p=net.predict_error(X); assert p.shape==(2,) and np.isfinite(p).all() and np.all((p>=0)&(p<=1))
 bad=dict(fixture()); bad['gold_answer']='12.5'
 try:b.transform([bad])
 except ValueError:pass
 else:raise AssertionError('forbidden field passed recursive input allow-list')
 badr=fixture(); badr['original_response']['teacher_score']=.2
 try:b.transform([badr])
 except ValueError:pass
 else:raise AssertionError('forbidden nested feature passed')
 print('synthetic_tests=PASS; no FinQA answer values read; no network/model calls')
if __name__=='__main__':run()
