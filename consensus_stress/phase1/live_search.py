"""Bounded live literature search for the Phase 1 novelty audit.

Queries arxiv API + Crossref for a fixed list of search terms. Outputs JSONL + CSV.
No claims of exhaustiveness; every hit carries its own date/venue and the query.
"""
from __future__ import annotations
import csv, json, re, sys, time, urllib.request, urllib.parse

def get(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "wcl-research-novelty-audit/0.1 (research; contact none)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")

def arxiv(query: str, max_results: int = 12) -> list[dict]:
    q = urllib.parse.quote(query)
    url = f"https://export.arxiv.org/api/query?search_query={q}&start=0&max_results={max_results}"
    try:
        xml = get(url)
    except Exception as e:
        return [{"_error": str(e)}]
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.S)
    out = []
    for e in entries:
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", re.search(r"<title>(.*?)</title>", e, re.S).group(1))).strip()
        published = re.search(r"<published>(.*?)</published>", e).group(1).strip()[:10]
        aid = re.search(r"<id>(.*?)</id>", e).group(1).strip()
        authors = re.findall(r"<name>(.*?)</name>", e)
        summary = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", re.search(r"<summary>(.*?)</summary>", e, re.S).group(1))).strip()
        out.append({"source": "arxiv", "title": title, "date": published, "id": aid,
                    "authors": authors[:8], "abstract_snippet": summary[:400]})
    return out

def crossref(query: str, rows: int = 8) -> list[dict]:
    url = "https://api.crossref.org/works?rows=%d&select=title,DOI,container-title,published,author&query=%s" % (
        rows, urllib.parse.quote(query))
    try:
        data = json.loads(get(url))
    except Exception as e:
        return [{"_error": str(e)}]
    out = []
    for it in data.get("message", {}).get("items", []):
        title = (it.get("title") or [""])[0]
        year = (it.get("published", {}).get("date-parts", [[None]])[0][0])
        out.append({"source": "crossref", "title": re.sub(r"\s+"," ",title).strip()[:200],
                    "date": str(year), "id": it.get("DOI", ""),
                    "venue": (it.get("container-title") or [""])[0][:80]})
    return out

QUERIES = [
    # concept 1: expected-response faithfulness
    "expected response faithfulness",
    "faithfulness of language model rationales",
    "counterfactual faithfulness evaluation language models",
    "do language models use the evidence they cite",
    # concept 2: consensus stress testing
    "consensus stress testing",
    "stress testing multi-agent LLM consensus",
    "stress testing language model agreement",
    # concept 3: stress curve
    "stress curve language model robustness",
    "perturbation strength response curve LLM",
    "robustness curve model calibration",
    # concept 4: robustness responsiveness
    "robustness responsiveness tradeoff neural networks",
    "invariance vs sensitivity language models",
    # concept 5: active probing
    "active testing machine learning",
    "active probing language models reliability",
    "adaptive intervention selection calibration",
    # selective prediction / calibration / multi-agent
    "selective prediction large language models",
    "multi-agent calibration agreement confidence",
    "multi-agent debate consensus correctness",
    "self-consistency chain of thought reliability",
    "citation reliability attribution hallucination evidence",
]

rows = []
for q in QUERIES:
    ar = arxiv(q)
    cr = crossref(q)
    time.sleep(0.5)  # polite throttling
    for r in ar + cr:
        r["query"] = q
        rows.append(r)
    print(f"{q!r}: arxiv={len(ar)} crossref={len(cr)}", flush=True)

with open("consensus_stress/phase1/live_search_raw.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("total rows:", len(rows))
