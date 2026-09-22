# ConvFinQA Stage-1 Qwen DEV analysis

Status: **ANALYSIS_PASS**
- worlds: 990 / 990
- items: 198
- schema-valid rate: 0.997979797979798
- S2 AUROC: 0.6508249641319943 CI=[0.5707206089649238, 0.7352946713323885] gate=True
- Full CEF AUROC: 0.6869619799139168 CI=[0.5953899280278206, 0.7822079023959867] gate=True
- Full minus S2 paired delta: 0.03613701578192252 CI=[-0.013138440708701151, 0.09394080457456473]
- Core gate: **True**

Primary correctness is normalized current-turn executable numeric correctness. Unit mismatch counts are diagnostic only; item-level QA answers were not used as current-turn targets.
