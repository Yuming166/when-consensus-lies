# Astra6 micro editorial review — 2026-09-16

- **Run time:** `2026-09-16T20:04:24.090087+08:00 -> 2026-09-16T20:04:55.044756+08:00`
- **Existing call path:** `consensus_stress/round7/ind_ce/scripts/relay_client.py`
- **Relay endpoint:** `https://openapi.center/v1/chat/completions`
- **Requested model:** `gpt-6-astra` (strict; no fallback)
- **Substantive request policy:** at most 2 HTTP attempts; `15s` timeout per attempt; `max_tokens=320`; temperature `0.0`; one transport attempt per wrapper call (long retry policy disabled for this micro-run)
- **Data boundary:** title, claim-boundary bullets, selected reported numbers, and two review questions only; no secrets, full manuscript, or raw experiment data sent.

## Health status

```json
{
  "http_status": 200,
  "latency_seconds": 0.584,
  "models_count": 7,
  "status": "ok",
  "target_model_listed": true
}
```

## Request status

### Attempt 1

```json
{
  "attempt": 1,
  "client_errors": 1,
  "client_http_stats": {},
  "detail": "RuntimeError: transport failed after 1 attempts: RuntimeError: transport: The read operation timed out",
  "max_tokens": 320,
  "requested_model": "gpt-6-astra",
  "seed": 2026091601,
  "status": "error",
  "timeout_seconds": 15.0,
  "wall_seconds": 15.39
}
```

### Attempt 2

```json
{
  "attempt": 2,
  "attempt_http_statuses": [
    200
  ],
  "cache_hit": false,
  "http_status": 200,
  "latency_seconds": 14.976,
  "max_tokens": 320,
  "requested_model": "gpt-6-astra",
  "returned_model": "gpt-6-astra",
  "seed": 2026091602,
  "status": "ok",
  "strict_model_match": true,
  "timeout_seconds": 15.0,
  "usage": {
    "completion_tokens": 538,
    "completion_tokens_details": {
      "reasoning_tokens": 232
    },
    "prompt_tokens": 1778,
    "total_tokens": 2316
  },
  "wall_seconds": 14.977
}
```

**Returned text:**
    1. **Universal transfer risk:**
       Replace “measuring consensus reliability” with **“measuring consensus reliability under a frozen VitaminC natural-pair protocol.”**
       Replace “cross-panel portability” with **“one Qwen-fixed transfer check from Qwen to Ling.”**

    2. **Causal-mechanism risk:**
       Replace “mechanism evidence” or “directional mechanism” with **“mechanism-oriented descriptive evidence; not a causal or mediation analysis.”**
       Describe Round10’s Probe1 extension as **“post-hoc descriptive support,”** not validation of a mechanism.

    3. **Independent-prediction risk:**
       Replace any wording implying that \(S_{\mathrm{ind}}\) predicts reliability with **“independent claim-only counter-evidence probe, not an independent predictor.”**
       Likewise, call \(S_{\mathrm{natural}}\) a **“natural-mirror diagnostic,”** not a second predictive score.

    **Highest reviewer-risk issue:** The predictive results may be read as intrinsic or broadly transferable reliability estimates despite dependence on an offline, gold-conditioned natural-pair resource and a frozen protocol.

    **Suggested disclosure:**
    “Accordingly, the reported AUROCs are conditional on the frozen VitaminC resource and its gold-conditioned offline construction; outcome-blindness applies only after freezing, Qwen-to-Ling is a single transfer check, and \(S_{\mathrm{ind}}\)/Round10 provide neither independent predictive nor causal evidence.”

## Sent micro packet

```text
Title: CST-Bench: Measuring Consensus Reliability with Direction-Gated Natural-Pair Stress Tests

Claim boundaries:
- The paper claims a bounded reliability measurement under a frozen VitaminC natural-pair matched protocol. The natural-pair resource is constructed offline with gold-conditioned direction; only scoring after the resource is fixed is outcome-blind and label-free.
- The primary predictive score is RS_q = -BF_q. S_natural is a natural-mirror diagnostic. Independent claim-only counter-evidence / S_ind is a mechanism probe, not an independent predictor.
- Qwen-to-Ling is one cross-panel portability check, not model-independent or out-of-domain generalization.
- Round10 is mechanism-oriented descriptive evidence about a direction contrast, with a post-hoc Probe1 extension; it is not a causal/mediation result and does not establish general counter-evidence rigidity.

Key numbers:
- Natural-pair flips: 0.902 for correct consensus decisions versus 0.075 for wrong decisions.
- RS_q AUROC: Qwen 0.943 [0.924, 0.960] (567 HC, 65 wrong); Ling 0.896 [0.873, 0.916] (574 HC); single-point gpt-6-astra 0.969 [0.935, 0.995] (96 HC, 8 wrong).
- Qwen-fixed procedure on Ling: 0.723 [0.682, 0.765]. Round10: +0.44 [0.24, 0.65] direction contrast, 145/160 valid inference calls, and as-assigned independent-CONTRADICT flips of 35/37; the direction-audited subset is 30/32 across 7 clean items.

Questions for a short NAACL-editor/reviewer-risk check (do not introduce new evidence):
1. Which wording in this packet still most risks being read as universal transfer, a causal mechanism, or independent prediction? Give up to three minimal wording changes.
2. What is the single highest reviewer-risk issue still visible from this packet, and what one-sentence disclosure would best address it?
```

## Accepted Astra6 short review

A response was returned with `returned_model == gpt-6-astra`; it is recorded above verbatim as returned text.
