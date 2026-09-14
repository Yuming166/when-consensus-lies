#!/usr/bin/env python3
"""Revise naacl_draft_v3.md in chunks using gpt-6-astra via private relay.
Strict rules: no number/CI/claim changes, keep [CITE], preserve headings, return ONLY markdown."""
import os, json, time, urllib.request, sys

KEY = os.environ.get("OPENAPI_CENTER_API_KEY", "")
BASE = "https://openapi.center/v1/chat/completions"
MODEL = "gpt-6-astra"
SRC = "naacl_draft_v3.md"
OUTDIR = "revision/chunks"

SYSTEM = (
    "You are an experienced NAACL/ACL area chair and paper author. Revise the given paper "
    "section to improve clarity, flow, precision, and reviewer-perceived rigor. STRICT RULES: "
    "(1) Do NOT change, add, or remove any experimental number, confidence interval, or factual "
    "claim - every number must remain identical. (2) Keep all honest boundaries and negative "
    "results; do not soften them. (3) Do NOT add new citations; keep any [CITE] placeholders. "
    "(4) Preserve the exact markdown section headings and overall structure. (5) Improve "
    "academic English, tighten argumentation, remove redundancy and hedging. (6) Keep the "
    "bounded, reviewer-aware tone (honest about limitations). Return ONLY the revised markdown."
)

def call(text, timeout=600):
    payload = {"model": MODEL,
               "messages": [{"role": "system", "content": SYSTEM},
                            {"role": "user", "content": text}],
               "max_tokens": 32768, "temperature": 0.3}
    for attempt in range(4):
        try:
            req = urllib.request.Request(BASE, data=json.dumps(payload).encode(),
                                         headers={"Authorization": "Bearer " + KEY,
                                                  "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            content = d["choices"][0]["message"]["content"]
            if content.strip():
                return content
            print("  empty content, retry", flush=True)
        except Exception as e:
            print(f"  attempt {attempt+1} failed: {type(e).__name__}: {e}", flush=True)
            time.sleep(15)
    raise RuntimeError("all attempts failed")

def split_chunks(t):
    marks = ["## 2 Related Work", "## 4 Experiments and Results", "### 4.5 Cost",
             "# Section 5 — Discussion"]
    idx = []
    for m in marks:
        i = t.find(m)
        if i < 0:
            raise SystemExit(f"marker not found: {m}")
        idx.append(i)
    return [t[0:idx[0]], t[idx[0]:idx[1]], t[idx[1]:idx[2]], t[idx[2]:idx[3]], t[idx[3]:]]

def main():
    if not KEY:
        raise SystemExit("OPENAPI_CENTER_API_KEY not set")
    text = open(SRC, encoding="utf-8").read()
    chunks = split_chunks(text)
    print(f"total len={len(text)} chars, chunks={len(chunks)}", flush=True)
    for n, ch in enumerate(chunks, 1):
        print(f"[{time.strftime('%H:%M:%S')}] chunk {n} len={len(ch)} -> calling {MODEL} ...", flush=True)
        out = call(ch)
        open(f"{OUTDIR}/chunk{n}.md", "w", encoding="utf-8").write(out.strip() + "\n")
        print(f"[{time.strftime('%H:%M:%S')}] chunk {n} done, out={len(out)} chars", flush=True)
    print("ALL CHUNKS DONE", flush=True)

if __name__ == "__main__":
    main()
