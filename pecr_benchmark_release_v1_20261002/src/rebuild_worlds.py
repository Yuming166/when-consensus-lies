#!/usr/bin/env python3
"""Offline FinQA TRAIN prompt reconstruction; no gold decoder or network client.

Only id, qa.question, pre_text, post_text and table are JSON-decoded from TRAIN.
The original candidate selection is frozen; this module does not reconstruct or
execute programs, infer directions, select new candidates, or regenerate labels.
Financial text and complete payloads are returned in memory only. CLI output is
restricted to hashes, counts, public IDs, and diagnostic status codes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, localcontext
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ('original', 'positive', 'negative')
ORIGINS = ('qwen', 'deepseek')
TRAIN_FIELDS = ('id', 'qa.question', 'pre_text', 'post_text', 'table')
FORBIDDEN_DECODE = ('qa.answer', 'qa.program', 'qa.exe_ans', 'exe_ans')
NUM_RE = re.compile(r'[-+]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def value_sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


class Cursor:
    """Skip unselected JSON values lexically, including all gold subtrees."""
    def __init__(self, text):
        self.s, self.i, self.n = text, 0, len(text)

    def ws(self):
        while self.i < self.n and self.s[self.i] in ' \t\r\n':
            self.i += 1

    def string_slice(self):
        self.ws()
        assert self.s[self.i] == '"'
        a = self.i
        self.i += 1
        escaped = False
        while self.i < self.n:
            ch = self.s[self.i]
            self.i += 1
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                return a, self.i
        raise ValueError('unterminated_string')

    def key(self):
        a, b = self.string_slice()
        return json.loads(self.s[a:b])

    def skip(self):
        self.ws()
        a = self.i
        if self.s[self.i] == '"':
            self.string_slice()
        elif self.s[self.i] in '[{':
            stack = []
            quoted = escaped = False
            while self.i < self.n:
                ch = self.s[self.i]
                self.i += 1
                if quoted:
                    if escaped:
                        escaped = False
                    elif ch == '\\':
                        escaped = True
                    elif ch == '"':
                        quoted = False
                elif ch == '"':
                    quoted = True
                elif ch in '[{':
                    stack.append(ch)
                elif ch in ']}':
                    op = stack.pop()
                    assert (op, ch) in (('[', ']'), ('{', '}'))
                    if not stack:
                        break
            else:
                raise ValueError('unterminated_container')
        else:
            while self.i < self.n and self.s[self.i] not in ',]} \t\r\n':
                self.i += 1
            assert self.i > a, 'empty_json_value'
        return a, self.i


def select(text, paths):
    """Decode only selected leaves and structural keys; arrays use indices."""
    c = Cursor(text)
    out = {}
    paths = {tuple(p.split('.')) for p in paths}

    def walk(prefix):
        c.ws()
        if prefix in paths:
            a, b = c.skip()
            key = '.'.join(prefix)
            assert key not in out
            out[key] = json.loads(c.s[a:b])
            return
        if not any(p[:len(prefix)] == prefix for p in paths):
            c.skip()
            return
        if c.s[c.i] == '{':
            c.i += 1
            first = True
            while True:
                c.ws()
                if c.s[c.i] == '}':
                    c.i += 1
                    break
                if not first:
                    assert c.s[c.i] == ','
                    c.i += 1
                key = c.key()
                c.ws()
                assert c.s[c.i] == ':'
                c.i += 1
                walk(prefix + (key,))
                first = False
        elif c.s[c.i] == '[':
            c.i += 1
            first = True
            i = 0
            while True:
                c.ws()
                if c.s[c.i] == ']':
                    c.i += 1
                    break
                if not first:
                    assert c.s[c.i] == ','
                    c.i += 1
                walk(prefix + (str(i),))
                i += 1
                first = False
        else:
            c.skip()
    walk(())
    c.ws()
    assert c.i == c.n, 'trailing_json_data'
    return out


def scan_train_text(train_path, requested_ids):
    """Read only approved text fields of frozen requested TRAIN records.

    All nonselected fields are lexically skipped, not JSON-decoded. The source
    bytes are loaded once to run the quote-aware scanner; no full dataset object
    or full qa object is constructed. Nonrequested records decode their ID only.
    """
    c = Cursor(Path(train_path).read_text(encoding='utf-8'))
    c.ws()
    assert c.s[c.i] == '['
    c.i += 1
    first = True
    count = 0
    found = {}
    wanted = set(requested_ids)
    while True:
        c.ws()
        if c.s[c.i] == ']':
            c.i += 1
            break
        if not first:
            assert c.s[c.i] == ','
            c.i += 1
        a, b = c.skip()
        record_text = c.s[a:b]
        rid = select(record_text, ('id',)).get('id')
        count += 1
        if rid in wanted:
            assert rid not in found, 'duplicate_requested_train_id'
            fields = select(record_text, TRAIN_FIELDS)
            assert all(k in fields for k in TRAIN_FIELDS), 'missing_allowed_text_field'
            assert fields['id'] == rid
            found[rid] = {'question': fields['qa.question'],
                          'pre_text': fields['pre_text'],
                          'table_original': fields['table'],
                          'post_text': fields['post_text']}
        first = False
    c.ws()
    assert c.i == c.n, 'trailing_train_data'
    return found, count


def positive_surface(surface, value):
    """Exact original V3 mutate_surface/fmt_decimal serialization."""
    surface = str(surface)
    if surface.strip().endswith('%'):
        value *= Decimal(100)
    out = format(value.normalize(), 'f')
    if '.' in out:
        out = out.rstrip('0').rstrip('.')
    if not out or out == '-0':
        out = '0'
    return ('$ ' if '$' in surface else '') + out + (
        '%' if surface.strip().endswith('%') else '')


def negative_surface(surface, value):
    """Exact original bidirectional V1 fmt_like serialization (six decimals)."""
    prefix = '$ ' if '$' in str(surface) else ''
    if value == value.to_integral_value():
        out = str(int(value))
    else:
        out = format(value, '.6f').rstrip('0').rstrip('.')
    return prefix + out


def build_worlds(original, edit):
    """Return three table-evidence records in memory, using saved operand edits.

    The negative recipe intentionally matches the historical formatter/parser;
    it is not replaced by a normalized percentage or monetary convention.
    """
    assert edit['requested'], 'unrequested_rows_have_no_restored_worlds'
    cell = edit['table_cell']
    assert isinstance(cell, list) and len(cell) == 2
    ri, ci = cell
    table = original['table_original']
    surface = table[ri][ci]
    with localcontext() as context:
        context.prec = 28
        old = Decimal(str(edit['operand_old_saved']))
        new = Decimal(str(edit['operand_new_saved']))
        # Reverse uses the original literal's number, not normalized cell text.
        hit = NUM_RE.search(str(edit['operand_old_saved']).replace('−', '-'))
        assert hit is not None, 'saved_operand_has_no_decimal'
        reverse_old = Decimal(hit.group(0).replace(',', ''))
        reverse = reverse_old - (new - reverse_old)
        pos = [list(row) for row in table]
        neg = [list(row) for row in table]
        pos[ri][ci] = positive_surface(surface, new)
        neg[ri][ci] = negative_surface(surface, reverse)
    assert old.is_finite() and new.is_finite() and reverse.is_finite()
    return {'original': dict(original),
            'positive': {**original, 'table_original': pos},
            'negative': {**original, 'table_original': neg}}


def make_request(world_record, origin, templates):
    """Build the exact saved request in memory; no send/write operation."""
    table_text = '\n'.join(' | '.join(map(str, row))
                           for row in world_record['table_original'])
    content = templates['user_template'].format(
        question=world_record['question'],
        pre_text=' '.join(world_record.get('pre_text', [])),
        table=table_text,
        post_text=' '.join(world_record.get('post_text', [])))
    request = dict(templates['origins'][origin])
    request['messages'] = [{'role': 'system', 'content': templates['system']},
                           {'role': 'user', 'content': content}]
    return request


def load_jsonl(path):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def verify(train_path, package_root=ROOT, require_source_hash=True):
    """Validate all frozen requests; return text-free report and per-request hashes."""
    package_root = Path(package_root)
    ip = package_root / 'intervention'
    templates = json.loads((ip / 'prompt_templates.json').read_text())
    receipt = json.loads((ip / 'source_hashes.json').read_text())
    specs = load_jsonl(ip / 'edit_spec.jsonl')
    saved = load_jsonl(ip / 'saved_request_hashes.jsonl')
    text_hashes = load_jsonl(ip / 'original_text_hashes.jsonl')
    assert len(specs) == 2241
    assert [r['row_index'] for r in specs] == list(range(2241))
    assert len({r['item_id'] for r in specs}) == len(specs)
    requested = [r for r in specs if r['requested']]
    excluded = [r for r in specs if not r['requested']]
    assert len(requested) == 2225 and len(excluded) == 16
    expected_train_sha = receipt['verification_train_sha256']
    observed_train_sha = file_sha(train_path)
    if require_source_hash:
        assert observed_train_sha == expected_train_sha, 'train_bytes_hash_mismatch'
    originals, train_count = scan_train_text(train_path, {r['item_id'] for r in requested})
    textmap = {r['item_id']: r['original_text_sha256'] for r in text_hashes}
    assert len(textmap) == len(text_hashes) == len(requested)
    expected = {}
    for r in saved:
        key = r['origin'], r['item_id'], r['world']
        assert key not in expected, 'duplicate_saved_request'
        expected[key] = r
    assert len(expected) == 13350
    assert set(expected) == {(o, r['item_id'], w) for o in ORIGINS
                            for r in requested for w in WORLDS}
    counters = Counter()
    rows = []
    text_mismatches = []
    missing_ids = []
    for spec in requested:
        rid = spec['item_id']
        original = originals.get(rid)
        if original is None:
            missing_ids.append(rid)
            text_status = 'missing_requested_train_id'
            worlds = None
        else:
            text_status = ('match' if value_sha(original) == textmap[rid]
                           else 'original_text_hash_mismatch')
            if text_status != 'match':
                text_mismatches.append(rid)
            worlds = build_worlds(original, spec)
        counters['original_text_' + text_status] += 1
        for origin in ORIGINS:
            for world in WORLDS:
                source = expected[origin, rid, world]
                observed = (value_sha(make_request(worlds[world], origin, templates))
                            if worlds is not None else None)
                status = ('match' if observed == source['request_sha256']
                          else 'missing_original_text' if observed is None
                          else 'request_hash_mismatch')
                counters[origin + '_' + world + '_' + status] += 1
                rows.append({'row_index': spec['row_index'], 'item_id': rid,
                             'source_group': spec['source_group'], 'origin': origin,
                             'world': world, 'status': status,
                             'expected_request_sha256': source['request_sha256'],
                             'rebuilt_request_sha256': observed})
    report = {'schema_version': 'pecr_offline_world_rebuild_v1',
              'all_requests_exact': all(r['status'] == 'match' for r in rows),
              'train_sha256_expected': expected_train_sha,
              'train_sha256_observed': observed_train_sha,
              'train_sha256_match': observed_train_sha == expected_train_sha,
              'train_record_count_lexically_scanned': train_count,
              'decoded_train_leaf_allowlist': list(TRAIN_FIELDS),
              'forbidden_gold_fields_never_decoded': list(FORBIDDEN_DECODE),
              'full_dataset_or_qa_json_decode': False,
              'financial_text_or_payload_written_in_release': False,
              'model_or_network_calls': 0,
              'frame_rows': len(specs), 'requested_rows': len(requested),
              'requested_groups': len({r['source_group'] for r in requested}),
              'unrequested_rows': len(excluded),
              'unrequested_status': 'unknown_not_requested_not_reconstructed',
              'request_hashes_expected': len(expected),
              'request_hashes_checked': len(rows), 'counts': dict(counters),
              'missing_requested_ids': missing_ids,
              'original_text_mismatch_ids': text_mismatches,
              'canonicalization': 'UTF8 JSON ensure_ascii=False sort_keys=True separators=(comma,colon)',
              'intervention_input_hashes': {
                  p.name: file_sha(p) for p in (ip / 'edit_spec.jsonl',
                  ip / 'saved_request_hashes.jsonl', ip / 'original_text_hashes.jsonl',
                  ip / 'prompt_templates.json', ip / 'source_hashes.json')},
              'runtime': {'decimal_precision': 28},
              'claim_boundary': 'Exact saved input/prompt reconstruction; no new inference, labels, or effectiveness validation.'}
    return report, rows


def write_local_inputs(train_path, directory, profile, model, package_root=ROOT):
    """Explicit optional export outside the release, for the user's own later run.

    This function writes financial evidence supplied by the user to a new private
    directory, never to the release. It does not call a model or reuse labels/G.
    Saved-profile verification remains a separate step before this export.
    """
    package_root = Path(package_root).resolve()
    directory = Path(directory)
    assert directory.is_absolute(), 'private_input_directory_must_be_absolute'
    directory = directory.resolve()
    assert directory != package_root and package_root not in directory.parents, (
        'private_input_directory_must_be_outside_release')
    assert not directory.exists(), 'refuse_existing_private_input_directory'
    ip = package_root / 'intervention'
    receipt = json.loads((ip / 'source_hashes.json').read_text())
    assert file_sha(train_path) == receipt['verification_train_sha256'], 'train_bytes_hash_mismatch'
    templates = json.loads((ip / 'prompt_templates.json').read_text())
    specs = [r for r in load_jsonl(ip / 'edit_spec.jsonl') if r['requested']]
    originals, _ = scan_train_text(train_path, {r['item_id'] for r in specs})
    assert len(originals) == len(specs) == 2225
    templates['origins'][profile] = dict(templates['origins'][profile])
    if model is not None:
        assert model.strip(), 'model_override_must_be_nonempty'
        templates['origins'][profile]['model'] = model
    generation_spec = {
        'schema_version': 'pecr_user_local_input_generation_v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'train_sha256': file_sha(train_path),
        'edit_spec_sha256': file_sha(ip / 'edit_spec.jsonl'),
        'saved_prompt_template_sha256': file_sha(ip / 'prompt_templates.json'),
        'saved_profile': profile,
        'effective_request_configuration': templates['origins'][profile],
        'model_override': model,
        'rows_per_world': len(specs), 'worlds': list(WORLDS),
        'source_saved_payload_exact_check': 'separate audit-only saved-profile verification',
        'new_response_requirement': 'Any new responses require independently versioned new labels, original-response G, parse status, and strict queue; historical labels/G are not reusable.',
        'no_model_or_network_call': True,
        'contains_user_supplied_financial_text': True,
        'not_a_public_release_artifact': True}
    generation_id = 'user-local-' + value_sha(generation_spec)[:24]
    generation_spec['generation_id'] = generation_id
    directory.mkdir(parents=True, mode=0o700)
    paths = {w: directory / ('inputs_' + w + '.jsonl') for w in WORLDS}
    handles = {w: p.open('x', encoding='utf-8') for w, p in paths.items()}
    try:
        for spec in specs:
            worlds = build_worlds(originals[spec['item_id']], spec)
            for world in WORLDS:
                payload = make_request(worlds[world], profile, templates)
                row = {'generation_id': generation_id, 'row_index': spec['row_index'],
                       'item_id': spec['item_id'], 'source_group': spec['source_group'],
                       'world': world, 'profile': profile, 'request': payload,
                       'request_sha256': value_sha(payload)}
                handles[world].write(canonical(row).decode('utf-8') + '\n')
    finally:
        for f in handles.values():
            f.close()
    generation_spec['input_file_hashes'] = {p.name: file_sha(p) for p in paths.values()}
    manifest = directory / 'LOCAL_GENERATION.json'
    with manifest.open('x', encoding='utf-8') as f:
        json.dump(generation_spec, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write('\n')
    for p in [*paths.values(), manifest]:
        p.chmod(0o600)
    return generation_id


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--train', required=True, type=Path,
                    help='User-provided exact FinQA TRAIN JSON; never a holdout file')
    ap.add_argument('--report', required=True, type=Path,
                    help='New text-free JSON audit path; existing files are refused')
    ap.add_argument('--request-hashes-out', type=Path,
                    help='Optional new JSONL path for text-free per-request comparison')
    ap.add_argument('--package-root', type=Path, default=ROOT)
    ap.add_argument('--write-local-inputs', type=Path,
                    help='Explicit optional NEW absolute private directory outside release; contains user-supplied evidence, never called by default')
    ap.add_argument('--profile', choices=ORIGINS, default='qwen',
                    help='Request configuration for optional local export; saved exact-check always validates both origins')
    ap.add_argument('--model',
                    help='Override model name only for optional new local generation; saved exact-check is unchanged')
    args = ap.parse_args()
    outputs = [args.report] + ([args.request_hashes_out] if args.request_hashes_out else [])
    assert all(not p.exists() for p in outputs), 'refuse_existing_output'
    assert args.model is None or args.write_local_inputs, 'model_override_requires_local_export'
    if args.write_local_inputs:
        assert args.write_local_inputs.is_absolute(), 'private_input_directory_must_be_absolute'
        private = args.write_local_inputs.resolve()
        root = args.package_root.resolve()
        assert private != root and root not in private.parents, 'private_directory_inside_release'
        assert not private.exists(), 'refuse_existing_private_input_directory'
    report, rows = verify(args.train, args.package_root)
    if args.write_local_inputs:
        assert report['all_requests_exact'], 'refuse_local_export_after_failed_saved_source_audit'
        report['local_input_generation_id'] = write_local_inputs(
            args.train, args.write_local_inputs, args.profile, args.model, args.package_root)
        report['optional_private_inputs_written_outside_release'] = True
        report['financial_text_or_payload_written_outside_release'] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open('x', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write('\n')
    if args.request_hashes_out:
        args.request_hashes_out.parent.mkdir(parents=True, exist_ok=True)
        with args.request_hashes_out.open('x', encoding='utf-8') as f:
            for row in rows:
                f.write(canonical(row).decode('utf-8') + '\n')
    print(json.dumps({'all_requests_exact': report['all_requests_exact'],
                      'requested_rows': report['requested_rows'],
                      'request_hashes_checked': report['request_hashes_checked'],
                      'unrequested_rows': report['unrequested_rows']}, sort_keys=True))
    if not report['all_requests_exact']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
