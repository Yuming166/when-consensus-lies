#!/usr/bin/env python3
"""Rebuild and audit saved three-world request payloads without making calls.

Only FinQA TRAIN fields `id`, `qa.question`, `pre_text`, `post_text`, and
`table` are decoded. Other JSON values, including gold answers and programs,
are skipped lexically. The default output contains hashes and statuses only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ("original", "positive", "negative")
TRACKS = ("qwen35", "deepseek_v41")
EXPECTED_TRAIN_SHA256 = "49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def value_sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def bytes_sha(value):
    return hashlib.sha256(value).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip()]


class Cursor:
    """A quote-aware JSON cursor used to skip unselected values without decoding them."""
    def __init__(self, text):
        self.s, self.i, self.n = text, 0, len(text)

    def ws(self):
        while self.i < self.n and self.s[self.i] in " \t\r\n":
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
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                return a, self.i
        raise ValueError("unterminated_string")

    def key(self):
        a, b = self.string_slice()
        return json.loads(self.s[a:b])

    def skip(self):
        self.ws()
        a = self.i
        if self.s[self.i] == '"':
            self.string_slice()
        elif self.s[self.i] in "[{":
            stack = []
            quoted = escaped = False
            while self.i < self.n:
                ch = self.s[self.i]
                self.i += 1
                if quoted:
                    if escaped:
                        escaped = False
                    elif ch == "\\":
                        escaped = True
                    elif ch == '"':
                        quoted = False
                elif ch == '"':
                    quoted = True
                elif ch in "[{":
                    stack.append(ch)
                elif ch in "]}":
                    op = stack.pop()
                    assert (op, ch) in (("[", "]"), ("{", "}"))
                    if not stack:
                        break
            else:
                raise ValueError("unterminated_container")
        else:
            while self.i < self.n and self.s[self.i] not in ",]} \t\r\n":
                self.i += 1
            assert self.i > a, "empty_json_value"
        return a, self.i


def select(text, paths):
    """Decode requested JSON leaves only; arrays use numeric path components."""
    c = Cursor(text)
    out = {}
    paths = {tuple(p.split(".")) for p in paths}

    def walk(prefix):
        c.ws()
        if prefix in paths:
            a, b = c.skip()
            key = ".".join(prefix)
            assert key not in out
            out[key] = json.loads(c.s[a:b])
            return
        if not any(p[:len(prefix)] == prefix for p in paths):
            c.skip()
            return
        if c.s[c.i] == "{":
            c.i += 1
            first = True
            while True:
                c.ws()
                if c.s[c.i] == "}":
                    c.i += 1
                    break
                if not first:
                    assert c.s[c.i] == ","
                    c.i += 1
                key = c.key()
                c.ws()
                assert c.s[c.i] == ":"
                c.i += 1
                walk(prefix + (key,))
                first = False
        elif c.s[c.i] == "[":
            c.i += 1
            first = True
            i = 0
            while True:
                c.ws()
                if c.s[c.i] == "]":
                    c.i += 1
                    break
                if not first:
                    assert c.s[c.i] == ","
                    c.i += 1
                walk(prefix + (str(i),))
                i += 1
                first = False
        else:
            c.skip()
    walk(())
    c.ws()
    assert c.i == c.n, "trailing_json_data"
    return out


def scan_train_text(train_path, wanted):
    """Read allow-listed source fields for requested IDs; gold/programs are skipped."""
    text = Path(train_path).read_text(encoding="utf-8")
    c = Cursor(text)
    c.ws()
    assert c.s[c.i] == "[", "FinQA_TRAIN_must_be_a_JSON_array"
    c.i += 1
    first = True
    count = 0
    found = {}
    wanted = set(wanted)
    while True:
        c.ws()
        if c.s[c.i] == "]":
            c.i += 1
            break
        if not first:
            assert c.s[c.i] == ","
            c.i += 1
        a, b = c.skip()
        record_text = c.s[a:b]
        rid = select(record_text, ("id",)).get("id")
        count += 1
        if rid in wanted:
            assert rid not in found, "duplicate_requested_train_id"
            fields = select(record_text, ("id", "qa.question", "pre_text", "post_text", "table"))
            assert all(k in fields for k in ("id", "qa.question", "pre_text", "post_text", "table")), "missing_allowed_source_field"
            found[rid] = {"question": fields["qa.question"], "pre_text": fields["pre_text"],
                          "table": fields["table"], "post_text": fields["post_text"]}
        first = False
    c.ws()
    assert c.i == c.n, "trailing_train_data"
    return found, count


def _apply_text_spans(source, row):
    assert bytes_sha(source.encode("utf-8")) == row["source_line_sha256"], "text_source_line_hash_mismatch"
    patches = row["patches"]
    ordered = sorted(patches, key=lambda p: (p["start_char"], p["end_char"]), reverse=True)
    previous_start = len(source) + 1
    out = source
    for patch in ordered:
        start, end = patch["start_char"], patch["end_char"]
        assert 0 <= start <= end <= len(source), "invalid_text_patch_span"
        assert end <= previous_start, "overlapping_text_patch_spans"
        removed = source[start:end]
        assert bytes_sha(removed.encode("utf-8")) == patch["removed_sha256"], "text_patch_source_hash_mismatch"
        out = out[:start] + patch["replacement"] + out[end:]
        previous_start = start
    return out


def build_worlds(original, spec):
    assert value_sha(original) == spec["world_sha256"]["original"], "original_input_hash_mismatch"
    worlds = {"original": {k: original[k] for k in ("question", "pre_text", "table", "post_text")}}
    for world in ("positive", "negative"):
        out = json.loads(json.dumps(original, ensure_ascii=False))
        changes = spec["world_edits"][world]
        for patch in changes["table_cells"]:
            ri, ci = patch["row"], patch["column"]
            assert 0 <= ri < len(out["table"]) and 0 <= ci < len(out["table"][ri]), "table_edit_out_of_bounds"
            assert value_sha(out["table"][ri][ci]) == patch["old_value_sha256"], "table_source_cell_hash_mismatch"
            out["table"][ri][ci] = patch["new_value"]
        for patch in changes["text_spans"]:
            field, line = patch["field"], patch["line_index"]
            assert field in ("pre_text", "post_text") and 0 <= line < len(out[field]), "text_edit_out_of_bounds"
            out[field][line] = _apply_text_spans(out[field][line], patch)
        assert value_sha(out) == spec["world_sha256"][world], "rebuilt_world_hash_mismatch"
        worlds[world] = out
    return worlds


def build_request(world, track, profiles):
    profile = profiles["tracks"][track]
    table_text = "\n".join(" | ".join(map(str, row)) for row in world["table"])
    content = profiles["user_template"].format(
        question=world["question"], pre_text=" ".join(world.get("pre_text", [])),
        table=table_text, post_text=" ".join(world.get("post_text", [])))
    return {"model": profile["model_requested"],
            "messages": [{"role": "system", "content": profiles["system"]},
                         {"role": "user", "content": content}],
            "temperature": profile["temperature"], "max_tokens": profile["max_tokens"],
            **profile["extra_request_fields"]}


def _write_private_export(train_path, output_dir, tracks, package_root, originals,
                          specs, request_rows, profiles):
    output_dir = Path(output_dir).resolve()
    package_root = Path(package_root).resolve()
    assert output_dir.is_absolute(), "private_export_path_must_be_absolute"
    assert output_dir != package_root and package_root not in output_dir.parents, "private_export_must_be_outside_package"
    assert not output_dir.exists(), "refuse_existing_private_export_directory"
    output_dir.mkdir(parents=True, mode=0o700)
    by_item = {r["item_id"]: r for r in specs}
    req_by_key = {(r["track"], r["item_id"], r["world"]): r for r in request_rows}
    files = []
    for track in tracks:
        ids = sorted({r["item_id"] for r in request_rows if r["track"] == track},
                     key=lambda iid: by_item[iid]["row_index"])
        rebuilt = {iid: build_worlds(originals[iid], by_item[iid]) for iid in ids}
        for world in WORLDS:
            path = output_dir / f"inputs_{track}_{world}.jsonl"
            with path.open("x", encoding="utf-8") as f:
                for iid in ids:
                    spec = by_item[iid]
                    req = build_request(rebuilt[iid][world], track, profiles)
                    rec = {"row_index": spec["row_index"], "track_row_index": req_by_key[(track, iid, world)]["track_row_index"],
                           "item_id": iid, "source_group": spec["source_group"], "track": track,
                           "world": world, "request": req, "request_sha256": value_sha(req)}
                    assert rec["request_sha256"] == req_by_key[(track, iid, world)]["request_sha256"]
                    f.write(canonical(rec).decode("utf-8") + "\n")
            path.chmod(0o600)
            files.append(path)
    manifest = {"schema_version": "pecr_private_generation_inputs_v1",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "train_sha256": file_sha(train_path), "tracks": list(tracks),
                "requests_by_track": {t: sum(r["track"] == t for r in request_rows) for t in tracks},
                "worlds": list(WORLDS), "request_hashes_verified_against_saved_calls": True,
                "contains_user_supplied_financial_evidence": True,
                "contains_saved_model_responses_or_labels": False,
                "network_or_model_calls_made": 0,
                "model_identity_limit": "The request profile records the historical model alias/configuration; exact provider checkpoint identity is not guaranteed.",
                "file_sha256": {p.name: file_sha(p) for p in files}}
    mp = output_dir / "LOCAL_GENERATION.json"
    with mp.open("x", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
    mp.chmod(0o600)
    return manifest


def verify(train_path, package_root=ROOT):
    package_root = Path(package_root)
    ip = package_root / "intervention"
    assert file_sha(train_path) == EXPECTED_TRAIN_SHA256, "FinQA_TRAIN_byte_hash_mismatch"
    specs = load_jsonl(ip / "edit_spec.jsonl")
    requests = load_jsonl(ip / "saved_request_hashes.jsonl")
    profiles = load_json(ip / "prompt_templates.json")
    assert len(specs) == 1699 and [s["row_index"] for s in specs] == list(range(1699))
    ids = [s["item_id"] for s in specs]
    assert len(ids) == len(set(ids)), "duplicate_intervention_id"
    assert len(requests) == 9888
    request_keys = [(r["track"], r["item_id"], r["world"]) for r in requests]
    assert len(request_keys) == len(set(request_keys)), "duplicate_saved_request_hash"
    wanted = set(ids)
    originals, train_count = scan_train_text(train_path, wanted)
    assert set(originals) == wanted, "requested_train_id_missing"
    spec_by_id = {s["item_id"]: s for s in specs}
    request_map = {(r["track"], r["item_id"], r["world"]): r for r in requests}
    track_ids = {t: {r["item_id"] for r in requests if r["track"] == t} for t in TRACKS}
    assert len(track_ids["qwen35"]) == 1699 and len(track_ids["deepseek_v41"]) == 1597
    assert track_ids["deepseek_v41"] <= track_ids["qwen35"]
    counts = Counter()
    rebuilt_rows = []
    for spec in specs:
        iid = spec["item_id"]
        worlds = build_worlds(originals[iid], spec)
        for track in TRACKS:
            if iid not in track_ids[track]:
                continue
            for world in WORLDS:
                expected = request_map[(track, iid, world)]
                req = build_request(worlds[world], track, profiles)
                got = value_sha(req)
                status = "match" if got == expected["request_sha256"] else "request_hash_mismatch"
                counts[f"{track}_{world}_{status}"] += 1
                rebuilt_rows.append({"row_index": spec["row_index"], "track_row_index": expected["track_row_index"],
                    "item_id": iid, "source_group": spec["source_group"], "track": track,
                    "world": world, "status": status,
                    "expected_request_sha256": expected["request_sha256"], "rebuilt_request_sha256": got})
    exact = len(rebuilt_rows) == len(requests) and all(r["status"] == "match" for r in rebuilt_rows)
    report = {"schema_version": "pecr_two_track_intervention_rebuild_v1",
        "status": "EXACT_SAVED_REQUEST_RECONSTRUCTION" if exact else "RECONSTRUCTION_MISMATCH",
        "all_saved_request_hashes_exact": exact,
        "train_sha256_expected": EXPECTED_TRAIN_SHA256, "train_sha256_observed": file_sha(train_path),
        "train_sha256_match": file_sha(train_path) == EXPECTED_TRAIN_SHA256,
        "train_record_count_scanned": train_count,
        "decoded_train_leaf_allowlist": ["id", "qa.question", "pre_text", "post_text", "table"],
        "gold_answer_and_program_fields_decoded": False,
        "holdout_accessed": False,
        "construction_rows_rebuilt": len(specs), "qwen35_items": len(track_ids["qwen35"]),
        "deepseek_v41_items": len(track_ids["deepseek_v41"]), "deepseek_ids_subset_of_qwen_ids": True,
        "request_hashes_expected": len(requests), "request_hashes_checked": len(rebuilt_rows),
        "counts": dict(counts), "worlds": list(WORLDS), "network_or_model_calls": 0,
        "full_financial_passages_embedded_in_package": False,
        "small_text_edit_fragments_embedded": True,
        "saved_responses_labels_and_reasoning_embedded_in_intervention": False,
        "private_export_available": True,
        "claim_boundary": "Exact reconstruction of historical request objects for the saved Qwen3.5-4B and DeepSeek V4.1 Flash aliases; this does not pin provider checkpoints or reproduce model outputs."}
    return report, rebuilt_rows, originals, specs, requests, profiles


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train", required=True, type=Path, help="Exact FinQA TRAIN JSON; no DEV/test/holdout file")
    ap.add_argument("--report", required=True, type=Path, help="New text-free audit JSON output")
    ap.add_argument("--hashes-out", type=Path, help="Optional new text-free per-request hash comparison JSONL")
    ap.add_argument("--package-root", type=Path, default=ROOT)
    ap.add_argument("--export-private", type=Path, help="Optional new absolute directory outside this release; contains reconstructed financial text")
    ap.add_argument("--track", choices=(*TRACKS, "both"), default="both")
    args = ap.parse_args()
    outputs = [args.report] + ([args.hashes_out] if args.hashes_out else [])
    assert all(not p.exists() for p in outputs), "refuse_existing_audit_output"
    report, rows, originals, specs, requests, profiles = verify(args.train, args.package_root)
    if args.export_private:
        assert report["all_saved_request_hashes_exact"], "refuse_export_after_hash_mismatch"
        selected_tracks = TRACKS if args.track == "both" else (args.track,)
        manifest = _write_private_export(args.train, args.export_private, selected_tracks,
            args.package_root, originals, specs, requests, profiles)
        report["private_export_written"] = True
        report["private_export_tracks"] = list(selected_tracks)
        report["private_export_request_counts"] = manifest["requests_by_track"]
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
    if args.hashes_out:
        with args.hashes_out.open("x", encoding="utf-8") as f:
            for row in rows:
                f.write(canonical(row).decode("utf-8") + "\n")
    print(json.dumps({"status": report["status"], "qwen35_items": report["qwen35_items"],
        "deepseek_v41_items": report["deepseek_v41_items"],
        "request_hashes_checked": report["request_hashes_checked"],
        "all_saved_request_hashes_exact": report["all_saved_request_hashes_exact"]}, sort_keys=True))
    if not report["all_saved_request_hashes_exact"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
