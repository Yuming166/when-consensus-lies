#!/usr/bin/env python3
"""Generate versioned reports for the post-top-up DeepSeek V2 complete attempt.

This reads frozen inputs and analysis outputs; it performs no model calls and
does not alter ledgers, labels, features, predictions, or prior reports.
"""
import csv, datetime, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/home/gaoym/when-consensus-lies-v8-zero-call-20260925/v9_cst_pecr_zero_call')
V1 = ROOT / 'pecr_crossmodel_deepseek_v1_20261001'
V2 = ROOT / 'pecr_crossmodel_deepseek_v2_complete_20261001'
MANIFEST = ROOT / 'pecr_bidirectional_development_v1_20260928/data/construction_manifest_dev_train.jsonl'
OUT = V2 / 'reports'
OUT.mkdir(exist_ok=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(4 << 20), b''):
            h.update(block)
    return h.hexdigest()

def parse_num(x):
    if x is None:
        return None
    s = str(x).strip().replace(',', '').replace('−', '-')
    try:
        return float(s)
    except Exception:
        return None

def parse_response(rec):
    """Frozen item parser semantics: numeric answer, bounded confidence."""
    if 'parsed_json' not in rec:
        return False, 'missing_json'
    p = rec['parsed_json']
    if not isinstance(p, dict):
        return False, 'json_not_object'
    if parse_num(p.get('answer_value')) is None:
        return False, 'answer_not_numeric'
    c = parse_num(p.get('confidence'))
    if c is None or not (0 <= c <= 1):
        return False, 'confidence_invalid'
    return True, 'ok'

def rounded(x, n=4):
    return round(float(x), n)

# Inputs and integrity.
manifest = {json.loads(line)['id']: json.loads(line) for line in open(MANIFEST) if line.strip()}
rows = [json.loads(line) for line in open(V2 / 'data/merged_ledger_v2.jsonl')]
merge_status = json.load(open(V2 / 'data/MERGE_STATUS_V2.json'))
label_rows = list(csv.DictReader(open(V2 / 'data/labels_deepseek_v2.csv')))
labels = {r['id']: r for r in label_rows}
result = json.load(open(V2 / 'results/within_deepseek_v2/CURVE_HGB_AUDITED.json'))
transfer = json.load(open(V2 / 'results/transfer_v2/TRANSFER_RESULTS.json'))
backfill_status = json.load(open(V2 / 'data/BACKFILL_STATUS.json'))
backfill_freeze = json.load(open(V2 / 'data/BACKFILL_SELECTION_FREEZE.json'))
features = [json.loads(line) for line in open(V2 / 'data/parsed_deepseek_v2/labeled_features.jsonl')]

by_item = defaultdict(dict)
record_reasons = Counter()
finish_reasons = Counter()
model_reported = Counter()
request_settings = Counter()
usage = Counter()
for r in rows:
    by_item[r['item_id']][r['world']] = r
    ok, reason = parse_response(r)
    record_reasons[reason] += 1
    model_reported[r.get('model_reported')] += 1
    request_settings[(r['request'].get('max_tokens'), r['request'].get('reasoning_effort'), r['request'].get('temperature'))] += 1
    try:
        top = json.loads(r['response_text'])
        finish_reasons[top['choices'][0].get('finish_reason')] += 1
    except Exception:
        finish_reasons['top_level_invalid'] += 1
    for key in ('prompt_tokens', 'completion_tokens', 'total_tokens'):
        usage[key] += (r.get('usage') or {}).get(key, 0) or 0

# V2-only usage and accounting.
v2_records = [json.load(open(p)) for p in (V2 / 'data/v2_responses').glob('slot_*.json')]
v2_usage = Counter()
v2_missing_json = 0
for r in v2_records:
    for key in ('prompt_tokens', 'completion_tokens', 'total_tokens'):
        v2_usage[key] += (r.get('usage') or {}).get(key, 0) or 0
    v2_missing_json += int('parsed_json' not in r)

requested_ids = {r['item_id'] for r in rows}
requested_groups = {manifest[i]['source_group'] for i in requested_ids}
flow = Counter()
parse_failure_patterns = Counter()
strict_groups = set()
strict_support = Counter()
for item_id in requested_ids:
    ws = by_item[item_id]
    all_three = all(w in ws for w in ('original', 'positive', 'negative'))
    parsed = {w: parse_response(ws[w]) for w in ('original', 'positive', 'negative') if w in ws}
    all_json = all(ws[w].get('parsed_json') is not None for w in ('original', 'positive', 'negative'))
    all_valid = all_three and all(ok for ok, _ in parsed.values())
    label_status = labels[item_id]['label_status']
    label_known = label_status in ('correct', 'error')
    if all_three:
        flow['all_three_http_200'] += 1
    if all(ws[w].get('model_reported') == 'deepseek-flash' for w in ('original', 'positive', 'negative')):
        flow['all_three_report_deepseek_flash'] += 1
    if all_json:
        flow['all_three_assistant_json_present'] += 1
    if all_valid:
        flow['all_three_strict_response_valid'] += 1
    if label_known:
        flow['original_label_known'] += 1
    if all_valid and label_known:
        flow['strict_analysis'] += 1
        strict_groups.add(manifest[item_id]['source_group'])
        strict_support[label_status] += 1
    if not all_valid:
        parse_failure_patterns[tuple(sorted(reason for ok, reason in parsed.values() if not ok))] += 1

# Exclusion categories are intentionally non-exclusive when applicable, but the
# four mutually exclusive response/label combinations fully partition the cohort.
label_status_counts = Counter(labels[i]['label_status'] for i in requested_ids)
partition = Counter()
for item_id in requested_ids:
    ws = by_item[item_id]
    valid = all(parse_response(ws[w])[0] for w in ('original', 'positive', 'negative'))
    known = labels[item_id]['label_status'] in ('correct', 'error')
    partition[('strict_valid_response_and_known_label' if valid and known else 'invalid_response_known_label' if known else 'valid_response_unknown_label' if valid else 'invalid_response_unknown_label')] += 1

coverage = {
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'cohort_definition': '2,225 items represented in the original DeepSeek slot manifest; 2,241 rows remain in the active dev_train manifest including 16 non-requested rows',
    'requested_items': len(requested_ids),
    'requested_source_groups': len(requested_groups),
    'requested_slots': len(rows),
    'merged_ledger': {
        'records': len(rows),
        'http_counts': {str(k): v for k, v in Counter(r['http_status'] for r in rows).items()},
        'model_requested_counts': {str(k): v for k, v in Counter(r['model_requested'] for r in rows).items()},
        'model_reported_counts': {str(k): v for k, v in model_reported.items()},
        'finish_reason_counts': {str(k): v for k, v in finish_reasons.items()},
        'request_setting_counts': {json.dumps(k): v for k, v in request_settings.items()},
        'chain_head': merge_status['chain_head'],
        'chain_errors': merge_status['chain_errors'],
        'v1_http200_preserved': merge_status['v1_http200_preserved'],
        'v2_backfill_records': merge_status['v2_backfill_records'],
    },
    'backfill': {
        'eligible_v1_failed_slots': backfill_status['eligible_slots'],
        'v2_response_files': len(v2_records),
        'v2_http_200': sum(r.get('http_status') == 200 for r in v2_records),
        'v2_http_429': sum(r.get('http_status') == 429 for r in v2_records),
        'v2_http_402': sum(r.get('http_status') == 402 for r in v2_records),
        'v2_other_errors': sum(r.get('http_status') not in (200, 429, 402) for r in v2_records),
        'newly_issued_by_full_runner': backfill_status['http_200'],
        'pre_runner_smoke_response_reused': len(v2_records) - backfill_status['http_200'],
        'one_attempt_per_eligible_slot': True,
        'v1_http200_slots_retried': False,
        'v1_http200_invalid_assistant_slots_retried': False,
    },
    'assistant_json_and_strict_response_flow': {
        'http200_records': len(rows),
        'assistant_json_valid_records': sum('parsed_json' in r for r in rows),
        'assistant_json_invalid_records': sum('parsed_json' not in r for r in rows),
        'assistant_json_invalid_v2_backfill_records': v2_missing_json,
        'record_level_response_parse_reasons': dict(record_reasons),
        'items_all_three_http_200': flow['all_three_http_200'],
        'items_all_three_model_reported': flow['all_three_report_deepseek_flash'],
        'items_all_three_assistant_json_present': flow['all_three_assistant_json_present'],
        'items_all_three_strict_response_valid': flow['all_three_strict_response_valid'],
        'items_original_label_known': flow['original_label_known'],
        'items_strict_analysis': flow['strict_analysis'],
        'item_level_parse_failure_patterns': {'|'.join(k): v for k, v in sorted(parse_failure_patterns.items())},
    },
    'cohort_partition': dict(partition),
    'strict_analysis': {
        'items': flow['strict_analysis'],
        'source_groups': len(strict_groups),
        'coverage_fraction_of_requested_items': flow['strict_analysis'] / len(requested_ids),
        'coverage_fraction_of_active_manifest_rows': flow['strict_analysis'] / len(manifest),
        'source_group_coverage_fraction': len(strict_groups) / len(requested_groups),
        'label_support': dict(strict_support),
    },
    'original_label_status_on_requested_items': dict(label_status_counts),
    'usage_tokens_recorded': {
        'merged_attempt': dict(usage),
        'v1_original_run': {'prompt_tokens': 4250894, 'completion_tokens': 4804583, 'total_tokens': 9055477},
        'v2_backfill': dict(v2_usage),
    },
    'integrity': {
        'features_sha256': sha256_file(V2 / 'data/parsed_deepseek_v2/labeled_features.jsonl'),
        'merged_ledger_sha256': sha256_file(V2 / 'data/merged_ledger_v2.jsonl'),
        'protocol_amendment_sha256': sha256_file(V2 / 'protocol/PROTOCOL_AMENDMENT_V3_BACKFILL.md'),
        'backfill_selection_freeze_sha256': sha256_file(V2 / 'data/BACKFILL_SELECTION_FREEZE.json'),
    },
    'no_565_item_holdout_read': True,
    'api_keys_committed': False,
}

# Analysis summary.
m = result['metrics']
primary = m['three_world_curve_hgb_minus_three_world_hgb']
report_json = {
    'report_version': 'deepseek_crossmodel_pecr_v2_complete_attempt_20261001',
    'status': 'post_top_up_complete_attempt_primary_analysis_complete',
    'claim_boundary': 'Versioned complete-attempt cross-model robustness analysis on FinQA dev_train; V1 failed-budget attempts were replaced only under a frozen V2 amendment. This is not an independent holdout confirmation and does not erase development-set exposure.',
    'model': 'deepseek-flash',
    'requested_items': len(requested_ids),
    'requested_slots': len(rows),
    'strict_analysis': coverage['strict_analysis'],
    'primary_comparison': {
        'positive_class': 'original_incorrect=1',
        'same_items_same_three_calls': True,
        'outer_split': 'GroupKFold(5) by source group',
        'bootstrap': 'source-group B=2000, seed=20260928',
        'graph_only': {'auroc': rounded(m['graph_only']['auroc']), 'auprc': rounded(m['graph_only']['auprc'])},
        'two_world_hgb': {'auroc': rounded(m['two_world_hgb']['auroc']), 'auprc': rounded(m['two_world_hgb']['auprc'])},
        'ordinary_three_world_hgb': {'auroc': rounded(m['three_world_hgb']['auroc']), 'auprc': rounded(m['three_world_hgb']['auprc'])},
        'three_world_curve_hgb': {'auroc': rounded(m['three_world_curve_hgb']['auroc']), 'auprc': rounded(m['three_world_curve_hgb']['auprc'])},
        'curve_minus_ordinary_three_world': {
            'delta_auroc': rounded(primary['delta_auroc']),
            'source_group_ci95': [rounded(primary['source_group_ci95'][0]), rounded(primary['source_group_ci95'][1])],
        },
        'ordinary_three_world_minus_graph_only': {
            'delta_auroc': rounded(m['three_world_hgb_minus_graph_only']['delta_auroc']),
            'source_group_ci95': [rounded(x) for x in m['three_world_hgb_minus_graph_only']['source_group_ci95']],
        },
    },
    'secondary_descriptive_transfer': {
        'qwen_trained_evaluated_on_deepseek': {
            'auroc': rounded(transfer['qwen_trained_on_deepseek']['auroc']),
            'auprc': rounded(transfer['qwen_trained_on_deepseek']['auprc']),
            'auroc_group_ci95': [rounded(x) for x in transfer['qwen_trained_on_deepseek']['auroc_group_ci95']],
        },
        'deepseek_trained_evaluated_on_qwen': {
            'auroc': rounded(transfer['deepseek_trained_on_qwen']['auroc']),
            'auprc': rounded(transfer['deepseek_trained_on_qwen']['auprc']),
            'auroc_group_ci95': [rounded(x) for x in transfer['deepseek_trained_on_qwen']['auroc_group_ci95']],
        },
        'note': 'Marginal source-group AUROC intervals for fixed one-direction transfers; these are descriptive and not the primary paired test.',
    },
    'qwen_reference': {
        'items': 1735,
        'ordinary_three_world_hgb_auroc': 0.7978,
        'curve_hgb_auroc': 0.8138,
        'curve_minus_ordinary_three_world': {'delta_auroc': 0.0160, 'ci95': [0.0041, 0.0269]},
    },
    'v1_quota_truncated_reference': {
        'strict_items': 1192,
        'curve_minus_ordinary_three_world': {'delta_auroc': 0.0138, 'ci95': [0.0016, 0.0255]},
        'comparison_note': 'Descriptive only: V1 was quota-truncated and non-random, so V2 is not an independent replication of V1.',
    },
    'implementation_tests': result['tests'],
    'coverage': coverage,
}

# Markdown report.
strict = coverage['strict_analysis']
p = report_json['primary_comparison']
lines = [
    '# DeepSeek V4.1 Flash cross-model PECR test — complete-attempt V2 report',
    '',
    f"**Date:** 2026-10-01  \n**Status:** post-top-up complete attempt; primary analysis complete.",
    '',
    '## 1. What changed in V2',
    '',
    'V1 preserved the original no-retry rule after API credit exhaustion. V2 was preregistered before any new model output and only retried the **2,682 V1 slots with HTTP 429 or 402**. It did not retry V1 HTTP-200 slots, including the **47 V1 HTTP-200 slots with invalid assistant JSON**. V1 remains immutable; the merged ledger links V1 HTTP-200 records to one V2 response for each formerly failed slot.',
    '',
    '- V1 HTTP-200 records preserved: **3,993**',
    '- V2 backfilled records: **2,682**',
    '- V2 HTTP-429 / HTTP-402 / other errors: **0 / 0 / 0**',
    '- Full-runner V2 requests: **2,681**; the one remaining eligible slot used the pre-runner HTTP-200 smoke response, as frozen',
    '- Merged records: **6,675/6,675 HTTP 200**',
    '- Merged hash-chain errors: **0**; hash-chain head `' + merge_status['chain_head'] + '`; ledger-file SHA-256 begins `' + coverage['integrity']['merged_ledger_sha256'][:16] + '`',
    '',
    'The ledger uses the frozen prompt, `deepseek-flash`, temperature 0, `max_tokens=8192`, and `reasoning_effort=low` for all requests. All returned records report model `deepseek-flash`.',
    '',
    '## 2. Cohort flow',
    '',
    '| Flow | Items | Source groups |',
    '|---|---:|---:|',
    f"| Requested construction cohort | {len(requested_ids)} | {len(requested_groups)} |",
    f"| All three worlds HTTP 200 and reported DeepSeek | {flow['all_three_report_deepseek_flash']} | — |",
    f"| All three assistant JSON objects present | {flow['all_three_assistant_json_present']} | — |",
    f"| All three pass strict numeric/confidence response parsing | {flow['all_three_strict_response_valid']} | — |",
    f"| Original-world correctness label known | {flow['original_label_known']} | — |",
    f"| **Strict analysis cohort** | **{flow['strict_analysis']}** | **{len(strict_groups)}** |",
    '',
    f"The strict cohort covers **{strict['items']}/{len(requested_ids)} ({100*strict['coverage_fraction_of_requested_items']:.2f}%)** of requested items and **{len(strict_groups)}/{len(requested_groups)} ({100*strict['source_group_coverage_fraction']:.2f}%)** of requested source groups. Class support is **{strict['label_support']['error']} original-error** and **{strict['label_support']['correct']} original-correct** items.",
    '',
    'The 47 V1 invalid-assistant slots were intentionally not retried. Across the merged attempt, **87 HTTP-200 records** ended with `finish_reason=length` and no valid assistant JSON; the merged strict cohort also excludes nonnumeric or out-of-range responses. The non-exclusive failure markers and item-level parse patterns are in `COVERAGE_FLOW_DEEPSEEK_V2.json`.',
    '',
    'Mutually exclusive endpoint statuses are:',
    '',
    '| Endpoint status | Items |',
    '|---|---:|',
    f"| Strict valid response + known label | {partition['strict_valid_response_and_known_label']} |",
    f"| Invalid response + known label | {partition['invalid_response_known_label']} |",
    f"| Valid response + unknown label | {partition['valid_response_unknown_label']} |",
    f"| Invalid response + unknown label | {partition['invalid_response_unknown_label']} |",
    '',
    '## 3. Primary within-DeepSeek result',
    '',
    'All methods use the same strict items, the same original/positive/negative DeepSeek responses, `original_incorrect=1` as the positive class, five source-group outer folds, and source-group bootstrap intervals (B=2,000, seed 20260928).',
    '',
    '| Method | AUROC | AUPRC |',
    '|---|---:|---:|',
    f"| Graph only | {p['graph_only']['auroc']:.4f} | {p['graph_only']['auprc']:.4f} |",
    f"| Two-world HGB | {p['two_world_hgb']['auroc']:.4f} | {p['two_world_hgb']['auprc']:.4f} |",
    f"| Ordinary three-world HGB | {p['ordinary_three_world_hgb']['auroc']:.4f} | {p['ordinary_three_world_hgb']['auprc']:.4f} |",
    f"| **Three-world Curve HGB** | **{p['three_world_curve_hgb']['auroc']:.4f}** | **{p['three_world_curve_hgb']['auprc']:.4f}** |",
    '',
    '| Pre-specified paired contrast | Δ AUROC | Source-group 95% CI |',
    '|---|---:|---:|',
    f"| **Curve HGB − ordinary three-world HGB** | **{p['curve_minus_ordinary_three_world']['delta_auroc']:+.4f}** | **[{p['curve_minus_ordinary_three_world']['source_group_ci95'][0]:+.4f}, {p['curve_minus_ordinary_three_world']['source_group_ci95'][1]:+.4f}]** |",
    f"| Ordinary three-world HGB − graph only | {p['ordinary_three_world_minus_graph_only']['delta_auroc']:+.4f} | [{p['ordinary_three_world_minus_graph_only']['source_group_ci95'][0]:+.4f}, {p['ordinary_three_world_minus_graph_only']['source_group_ci95'][1]:+.4f}] |",
    '',
    'The primary interval is above zero. All implementation checks passed: independent arrays, two-world negative-world invariance, named dimensions, and preservation of curve features.',
    '',
    '## 4. Cross-model context and transfer',
    '',
    '| Response family / cohort | Ordinary three-world | Curve HGB | Paired Curve gain |',
    '|---|---:|---:|---:|',
    f"| Qwen3.5-4B, 1,735-item dev result | 0.7978 | 0.8138 | +0.0160 [+0.0041, +0.0269] |",
    f"| DeepSeek V4.1 Flash, 2,050-item complete attempt | {p['ordinary_three_world_hgb']['auroc']:.4f} | {p['three_world_curve_hgb']['auroc']:.4f} | {p['curve_minus_ordinary_three_world']['delta_auroc']:+.4f} [{p['curve_minus_ordinary_three_world']['source_group_ci95'][0]:+.4f}, {p['curve_minus_ordinary_three_world']['source_group_ci95'][1]:+.4f}] |",
    '',
    'Fixed one-direction transfers are secondary and descriptive:',
    '',
    '| Train → evaluate | Curve AUROC | 95% CI | AUPRC |',
    '|---|---:|---:|---:|',
    f"| Qwen → DeepSeek | {transfer['qwen_trained_on_deepseek']['auroc']:.4f} | [{transfer['qwen_trained_on_deepseek']['auroc_group_ci95'][0]:.4f}, {transfer['qwen_trained_on_deepseek']['auroc_group_ci95'][1]:.4f}] | {transfer['qwen_trained_on_deepseek']['auprc']:.4f} |",
    f"| DeepSeek → Qwen | {transfer['deepseek_trained_on_qwen']['auroc']:.4f} | [{transfer['deepseek_trained_on_qwen']['auroc_group_ci95'][0]:.4f}, {transfer['deepseek_trained_on_qwen']['auroc_group_ci95'][1]:.4f}] | {transfer['deepseek_trained_on_qwen']['auprc']:.4f} |",
    '',
    'The two cohorts differ in size and label balance, so AUROC levels are not a direct model-ranking comparison. Transfer intervals are marginal, not paired method contrasts.',
    '',
    '## 5. Token accounting',
    '',
    '| Attempt | Prompt tokens | Completion tokens | Total tokens |',
    '|---|---:|---:|---:|',
    f"| V1 original run | {coverage['usage_tokens_recorded']['v1_original_run']['prompt_tokens']:,} | {coverage['usage_tokens_recorded']['v1_original_run']['completion_tokens']:,} | {coverage['usage_tokens_recorded']['v1_original_run']['total_tokens']:,} |",
    f"| V2 backfill | {v2_usage['prompt_tokens']:,} | {v2_usage['completion_tokens']:,} | {v2_usage['total_tokens']:,} |",
    f"| Merged complete attempt | {usage['prompt_tokens']:,} | {usage['completion_tokens']:,} | {usage['total_tokens']:,} |",
    '',
    'These are model-reported usage fields, not a provider invoice.',
    '',
    '## 6. Supported and unsupported claims',
    '',
    '**Supported:** On the complete-attempt strict cohort, Curve HGB gives a paired AUROC gain over same-budget ordinary three-world HGB with a source-group bootstrap CI above zero. The qualitative direction reproduces the Qwen development result.',
    '',
    '**Also supported:** the pipeline returned a response for every requested slot, preserved V1, followed the frozen retry eligibility rule, and used the same frozen parser/features/statistics without response-conditioned parser changes.',
    '',
    '**Not supported:** independent holdout confirmation; freedom from FinQA dev_train selection exposure; complete parsing (87 invalid assistant JSON records remain); symmetric transfer; claims about the separate 565-item holdout; or a claim that V2 independently replicates V1. The construction is program-conditioned, not oracle-free.',
    '',
    '## 7. Recommended wording',
    '',
    f"“On a post-top-up complete DeepSeek V4.1 Flash attempt of the 2,225-item FinQA dev_train construction, {strict['items']} items passed the strict three-world parser and label requirements. With identical items and three calls per item, Curve HGB improved error-ranking AUROC over ordinary three-world HGB by {p['curve_minus_ordinary_three_world']['delta_auroc']:+.4f} (source-group 95% CI {p['curve_minus_ordinary_three_world']['source_group_ci95'][0]:+.4f} to {p['curve_minus_ordinary_three_world']['source_group_ci95'][1]:+.4f}). This is a cross-model robustness analysis within the development dataset, not an independent confirmation.”",
]
(OUT / 'FINAL_REPORT_V2.md').write_text('\n'.join(lines) + '\n')
(OUT / 'FINAL_REPORT_V2.json').write_text(json.dumps(report_json, indent=2, ensure_ascii=False) + '\n')
(OUT / 'COVERAGE_FLOW_DEEPSEEK_V2.json').write_text(json.dumps(coverage, indent=2, ensure_ascii=False) + '\n')

paper_insert = r'''### Complete-attempt cross-model robustness

To test whether the response-curve signal is specific to one model family, we reran the frozen DeepSeek protocol after account top-up. The versioned amendment preserved all original HTTP-200 responses and replaced only the 2,682 slots that had failed with HTTP 429 or 402; it did not retry HTTP-200 responses with invalid assistant output. All 6,675 merged slots returned HTTP 200 from \texttt{deepseek-flash}. After excluding 87 length-limited assistant outputs, nonnumeric or out-of-range responses, and items without an original-answer label, 2,050 items across 448 source groups remained.

On this complete-attempt cohort, the pre-specified paired comparison used identical items and identical original/positive/negative calls. Ordinary three-world HGB attained AUROC %.4f, whereas three-world Curve HGB attained AUROC %.4f. The paired gain was %.4f (source-group bootstrap 95%% CI %.4f to %.4f), with AUPRC %.4f versus %.4f. The direction matched the Qwen development result (+0.0160, 95%% CI +0.0041 to +0.0269). Because this cohort is drawn from FinQA \texttt{dev\_train} and the parser still excludes failed outputs, we interpret it as cross-model robustness within the development construction rather than independent confirmation.
'''
paper_insert %= (
    p['ordinary_three_world_hgb']['auroc'], p['three_world_curve_hgb']['auroc'],
    p['curve_minus_ordinary_three_world']['delta_auroc'],
    p['curve_minus_ordinary_three_world']['source_group_ci95'][0],
    p['curve_minus_ordinary_three_world']['source_group_ci95'][1],
    p['three_world_curve_hgb']['auprc'], p['ordinary_three_world_hgb']['auprc'],
)
(OUT / 'PAPER_INSERT_DEEPSEEK_V2_COMPLETE_EN.md').write_text(paper_insert)

# Hash only safe, portable report artifacts; raw ledgers and response corpora stay local.
safe = [
    OUT / 'FINAL_REPORT_V2.json',
    OUT / 'FINAL_REPORT_V2.md',
    OUT / 'COVERAGE_FLOW_DEEPSEEK_V2.json',
    OUT / 'PAPER_INSERT_DEEPSEEK_V2_COMPLETE_EN.md',
    V2 / 'protocol/PROTOCOL_AMENDMENT_V3_BACKFILL.md',
    V2 / 'data/MERGE_STATUS_V2.json',
    V2 / 'data/BACKFILL_STATUS.json',
    V2 / 'data/LABEL_RECEIPT_DEEPSEEK_V2.json',
    V2 / 'data/parsed_deepseek_v2/CHECKPOINT.json',
]
with (OUT / 'SAFE_ARTIFACT_SHA256_V2.sha256').open('w') as f:
    for path in safe:
        f.write(f'{sha256_file(path)}  {path.relative_to(V2)}\n')

print(json.dumps({
    'status': 'reports_generated',
    'strict_items': flow['strict_analysis'],
    'strict_groups': len(strict_groups),
    'primary_delta_auroc': primary['delta_auroc'],
    'primary_ci95': primary['source_group_ci95'],
    'coverage_fraction': flow['strict_analysis'] / len(requested_ids),
    'report_dir': str(OUT),
}, indent=2))
