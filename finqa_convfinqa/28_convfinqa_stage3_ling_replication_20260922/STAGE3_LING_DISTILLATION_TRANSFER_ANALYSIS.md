# ConvFinQA Stage 3 Ling zero-shot missing-probe transfer

- Status: **STAGE3_LING_DISTILLATION_TRANSFER_ANALYSIS_COMPLETE**
- Mapping: frozen Qwen TRAIN-fit heads applied once to Ling DEV; no Ling refit or calibration.
- Primary: all_response_rich + shallow GBDT two binary heads.
- Head AUROC -2: **0.8845486111111112**; +2: **0.7460526315789474**.
- Student AUROC: **0.8536155202821869**; S2: **0.8274544385655497**; full CEF: **0.8251028806584362**.
- Student minus S2: **0.026161081716637224**, bootstrap CI **[-0.053852759832739766, 0.14359157986111112]**.
- Gap closure: **-11.124999999999805**.
- Teacher MAE: **0.027093754565749695**; Spearman: **0.3972813484918841**.
- Practical +0.02 gate: **True**.

Original correctness is evaluation-only; no Ling refit, calibration, feature/model selection, or threshold selection was performed.
