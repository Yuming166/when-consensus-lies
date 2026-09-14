"""Third-pass retry with long backoff; confirms key known papers with dates."""
from __future__ import annotations
import json, re, time, urllib.request, urllib.parse

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "wcl-research-novelty-audit/0.3b"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            time.sleep(8 + 8*i)
    return ""

def arxiv_title(query, max_results=3):
    q = urllib.parse.quote(f'ti:"{query}"')
    url = f"https://export.arxiv.org/api/query?search_query={q}&start=0&max_results={max_results}"
    xml = get(url)
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", re.search(r"<title>(.*?)</title>", e, re.S).group(1))).strip()
        published = re.search(r"<published>(.*?)</published>", e).group(1).strip()[:10]
        aid = re.search(r"<id>(.*?)</id>", e).group(1).strip()
        out.append({"source":"arxiv","title":title,"date":published,"id":aid})
    return out

TITLES = [
    "ERASER", "CheckList", "TruthfulQA", "Measuring Faithfulness in Chain-of-Thought",
    "Semantic Uncertainty", "SelfCheckGPT", "FActScore", "Attributed Question Answering",
    "Selective Classification for Deep Neural Networks", "Active Testing",
    "Stress Test Evaluation for Natural Language Inference", "PAWS",
    "Semantically Equivalent Adversarial Rules", "Robustness Gym",
    "Language Models as Knowledge Bases", "Chain-of-Verification", "Let's Verify Step by Step",
    "Conformal Prediction", "Self-Consistency Improves Chain of Thought",
    "Semantic Entropy", "Sycophancy", "Majority Illusion", "HANS",
]
rows = []
for t in TITLES:
    rs = arxiv_title(t, 3)
    for r in rs:
        r["query"] = t
        rows.append(r)
    time.sleep(6)
    print(f"{t!r}: {len([r for r in rs if '_error' not in r])} hits", flush=True)
with open("consensus_stress/phase1/live_search_raw3.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("total:", len(rows))
