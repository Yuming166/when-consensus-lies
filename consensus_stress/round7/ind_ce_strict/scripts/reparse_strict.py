#!/usr/bin/env python3
"""Round-7 W2b: documented PARSER CORRECTION (post-freeze, post-generation).

Why: the preregistered parser (a) only accepted exact '<T>|'/'<F>|' markers and
(b) split sentences on any '[.!?] ' which broke on abbreviations such as 'K.
Balachander'. Five dual-direction calls returned HTTP 200 with content-valid
segments but were rejected by the parser. We re-parse ALL 50 cached raw outputs
uniformly with a corrected parser (marker-variant mapping + abbreviation-aware
sentence splitting). Prompts, models, seeds, temperatures, and calls are UNCHANGED;
raw model outputs in the content-addressed cache are immutable. This is a parser
fix applied uniformly, not method tuning. Original parse results are preserved in
the row fields `parsed_ok_original` / `parse_error_original`."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "scripts"))
from gen_strict_evidence import (clean_fence, split_sentences, validate_segment,
                                 BANNED_WORDS_DUAL, BANNED_WORDS_PM)

# ---- corrected sentence splitting: protect abbreviations ----
_ABBREV = ("mr.", "mrs.", "dr.", "prof.", "st.", "vs.", "e.g.", "i.e.", "etc.",
           "jr.", "sr.", "inc.", "no.", "u.s.", "u.k.", "u.n.", "a.d.", "b.c.")
_ABBREV = ("mr.", "mrs.", "dr.", "prof.", "st.", "vs.", "e.g.", "i.e.", "etc.",
           "jr.", "sr.", "inc.", "no.", "u.s.", "u.k.", "u.n.", "a.d.", "b.c.")


def split_sentences_corrected(text: str) -> list[str]:
    """Robust sentence splitter (final, applied uniformly to all cached raw outputs).
    0) normalize curly quotes adjacent to periods (so 'Jr.”' splits like 'Jr.');
    1) protect decimals (1.5); 2) protect single-capital initials (K. Balachander);
    3) protect common abbreviations UNLESS followed by a capitalized word (so
    'Clapp Jr. He was born' splits at the genuine boundary, while 'St. Louis'
    stays intact). Then split on remaining [.!?] + whitespace."""
    s = text.replace("“", "«").replace("”", "»")
    s = re.sub(r"[.!?][«»]", ".", s)          # period next to quote
    s = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", s)     # decimals
    s = re.sub(r"\b([A-Z])\.(?=\s+[A-Z])", r"\1<DOT>", s)  # initials
    for ab in _ABBREV:
        def _rep(m, ab=ab):
            nxt = m.group(2)
            if nxt[1:2].isupper():  # first non-space char is capitalized
                return m.group(1) + "." + nxt   # sentence boundary: leave it
            return m.group(1) + "<DOT>" + nxt
        s = re.sub(r"\b(" + re.escape(ab[:-1]) + r")\.(\s+\S)",
                   _rep, s, flags=re.IGNORECASE)
    parts = re.split(r"(?<=[.!?])\s+", s)
    return [pp.replace("<DOT>", ".").replace("«", "“").replace("»", "”").strip()
            for pp in parts if pp.strip()]


MARKER_RE = re.compile(
    r"^\s*(?:<(?P<a>[TF])>|(?P<b>[TF])\||(?:SEGMENT_(?P<c>TRUE|FALSE))\|)\s*\|?\s*(?P<rest>.+)$",
    re.IGNORECASE)


def parse_dual_corrected(content: str) -> dict[str, str] | None:
    text = clean_fence(content)
    seg: dict[str, str] = {}
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        m = MARKER_RE.match(ln)
        if not m:
            continue
        g = (m.group("a") or m.group("b") or
             ("T" if m.group("c") and m.group("c").upper() == "TRUE" else "F"))
        key = g.upper()
        seg[key] = m.group("rest")
    if set(seg) != {"T", "F"}:
        return None
    t = validate_segment_corrected(seg["T"], BANNED_WORDS_DUAL)
    f = validate_segment_corrected(seg["F"], BANNED_WORDS_DUAL)
    if t is None or f is None:
        return None
    return {"T": t, "F": f}


def validate_segment_corrected(sent_text: str, banned: set[str]) -> str | None:
    sents = split_sentences_corrected(sent_text)
    if len(sents) != 2:
        return None
    out = []
    for s in sents:
        low = s.casefold()
        from gen_strict_evidence import BANNED_PREFIXES, words, MAX_WORDS_PER_SEGMENT
        for bp in BANNED_PREFIXES:
            if low.startswith(bp):
                return None
        ws = words(s)
        if any(w in banned for w in ws):
            return None
        if not (3 <= len(ws) <= MAX_WORDS_PER_SEGMENT):
            return None
        out.append(s)
    return " ".join(out)


def parse_placebo_corrected(content: str) -> str | None:
    text = clean_fence(content)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    return validate_segment_corrected(lines[0], BANNED_WORDS_PM)


def main() -> int:
    cache_dir = HERE / "cache"
    rows = [json.loads(l) for l in
            (HERE / "e_gen_artifacts.jsonl").read_text(encoding="utf-8").splitlines() if l]
    raw_sha = hashlib.sha256((HERE / "e_gen_artifacts.jsonl").read_bytes()).hexdigest()
    n_fixed = 0
    n_changed = 0
    detail = []
    for r in rows:
        r["parsed_ok_original"] = bool(r["success"])
        r["parse_error_original"] = r["final_error"]
        content = None
        for a in r["attempts"]:
            ck = a.get("cache_key")
            if ck:
                c = json.loads((cache_dir / f"{ck}.json").read_text(encoding="utf-8"))
                content = c.get("content")
                break
        if content is None:
            detail.append({"pair_id": r["pair_id"], "kind": r["kind"], "note": "no raw content"})
            continue
        if r["kind"] == "dual":
            parsed = parse_dual_corrected(content)
            new_success = parsed is not None
            if new_success:
                r["segment_true"] = parsed["T"]
                r["segment_false"] = parsed["F"]
            else:
                r["segment_true"] = None
                r["segment_false"] = None
        else:
            parsed = parse_placebo_corrected(content)
            new_success = parsed is not None
            r["placebo"] = parsed
        if new_success and not r["success"]:
            n_fixed += 1
        if r["success"] != new_success:
            n_changed += 1
        r["success"] = new_success
        r["final_error"] = None if new_success else (r["final_error"] or "corrected parse failed")
        r["parser_correction"] = True
        detail.append({"pair_id": r["pair_id"], "kind": r["kind"],
                       "was_ok": r["parsed_ok_original"], "now_ok": new_success})
    rows.sort(key=lambda r: (r["pair_id"], r["kind"]))
    (HERE / "e_gen_artifacts.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n",
        encoding="utf-8")
    new_sha = hashlib.sha256((HERE / "e_gen_artifacts.jsonl").read_bytes()).hexdigest()
    summary = {
        "stage": "parser_correction", "note": (
            "post-freeze parser fix applied uniformly to all cached raw outputs; "
            "prompts/seeds/calls/model unchanged; raw cache immutable"),
        "rows": len(rows), "success_before": sum(1 for r in rows if r["parsed_ok_original"]),
        "success_after": sum(1 for r in rows if r["success"]),
        "n_fixed": n_fixed, "n_changed": n_changed,
        "e_gen_sha256_before": raw_sha, "e_gen_sha256_after": new_sha,
        "detail": detail,
    }
    (HERE / "run_summary_parser_correction.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
