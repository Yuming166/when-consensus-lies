"""Second, higher-precision live pass: arxiv title+abstract searches on known closest-work terms."""
from __future__ import annotations
import json, re, time, urllib.request, urllib.parse

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "wcl-research-novelty-audit/0.2"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")

def arxiv(query, max_results=10, field="all"):
    q = urllib.parse.quote(f'{field}:"{query}"')
    url = f"https://export.arxiv.org/api/query?search_query={q}&start=0&max_results={max_results}"
    try:
        xml = get(url)
    except Exception as e:
        return [{"_error": str(e)}]
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", re.search(r"<title>(.*?)</title>", e, re.S).group(1))).strip()
        published = re.search(r"<published>(.*?)</published>", e).group(1).strip()[:10]
        aid = re.search(r"<id>(.*?)</id>", e).group(1).strip()
        summ = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", re.search(r"<summary>(.*?)</summary>", e, re.S).group(1))).strip()
        out.append({"source":"arxiv","title":title,"date":published,"id":aid,"abstract_snippet":summ[:350]})
    return out

QUERIES = [
    ("rationale faithfulness evaluation", "ti"),
    ("counterfactual evaluation faithfulness", "ti"),
    ("attribution faithfulness language models", "ti"),
    ("self-consistency chain of thought", "ti"),
    ("semantic entropy uncertainty", "ti"),
    ("selective prediction", "ti"),
    ("behavioral testing natural language", "ti"),
    ("metamorphic testing language models", "ti"),
    ("stress testing large language models", "ti"),
    ("multi-agent debate", "ti"),
    ("multi-agent agreement reliability", "ti"),
    ("knowledge probing language models", "ti"),
    ("calibration language models", "ti"),
    ("hallucination detection agreement", "ti"),
    ("citation faithfulness", "ti"),
    ("evidence attribution question answering", "ti"),
    ("robustness radius neural networks", "ti"),
    ("robustness to paraphrases", "ti"),
    ("active testing", "ti"),
    ("selective question answering", "ti"),
]
rows = []
for query, field in QUERIES:
    rs = arxiv(query, 8, field)
    for r in rs:
        r["query"] = query
        rows.append(r)
    time.sleep(0.4)
    print(f"{query!r}: {len(rs)}", flush=True)
with open("consensus_stress/phase1/live_search_raw2.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("total:", len(rows))
