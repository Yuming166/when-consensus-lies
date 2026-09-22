# ConvFinQA Stage 3 Ling DEV analysis

Status: **ANALYSIS_PASS**
- worlds: 990 / 990
- items: 198
- schema-valid rate: 0.7909090909090909
- S2 AUROC: 0.8274544385655497 CI=[0.6525499706055261, 0.9982638888888888] gate=True
- Full CEF AUROC: 0.8251028806584362 CI=[0.6455938103115522, 0.9988375378036487] gate=True
- Full minus S2 paired delta: -0.0023515579071134995 CI=[-0.008290801762304402, 0.0023026315789473895]
- Core gate: **True**

Primary correctness is normalized current-turn executable numeric correctness. Unit mismatch counts are diagnostic only; item-level QA answers were not used as current-turn targets.
