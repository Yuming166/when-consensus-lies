# ConvFinQA Stage 2 confirmation

- Status: **STAGE2_ANALYSIS_COMPLETE**
- Primary: all_response_rich + shallow GBDT two binary heads.
- Head AUROC -2: **0.8754098360655738**; +2: **0.8406936416184971**.
- Student AUROC: **0.7473995695839312**; S2: **0.6508249641319943**; full CEF: **0.6869619799139168**.
- Student minus S2: **0.09657460545193686**, bootstrap CI **[0.01827068331473532, 0.1739720174818759]**.
- Gap closure: **2.672456575682382**.
- Teacher MAE: **0.04911308345104847**; Spearman: **0.5262217342952324**.
- Practical +0.02 gate: **True**.

Original correctness is evaluation-only; no DEV refit or feature/model selection was performed.
