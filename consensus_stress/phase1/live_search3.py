"""Third pass: confirm known closest-work papers + dates via arxiv title search."""
from __future__ import annotations
import json, re, time, urllib.request, urllib.parse

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "wcl-research-novelty-audit/0.3"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")

def arxiv_title(query, max_results=5):
    q = urllib.parse.quote(f'ti:"{query}"')
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
        out.append({"source":"arxiv","title":title,"date":published,"id":aid})
    return out

TITLES = [
    "ERASER benchmark rationalized",
    "CheckList behavioral testing",
    "TruthfulQA",
    "Measuring Faithfulness in Chain-of-Thought Reasoning",
    "Semantic Uncertainty linguistic invariances uncertainty estimation",
    "SelfCheckGPT",
    "FActScore",
    "Attributed Question Answering",
    "Selective Classification for Deep Neural Networks",
    "Active Testing estimating accuracy",
    "Stress Test Evaluation for Natural Language Inference",
    "PAWS paraphrase adversaries",
    "Semantically Equivalent Adversarial Rules",
    "Robustness Gym",
    "Language Models as Knowledge Bases",
    "CoVe chain-of-verification",
    "Let's Verify Step by Step",
    "Calibrated Language Models Must Hallucinate",
    "Beyond Accuracy behavioral testing",
    "Conformal prediction a unified",
    "Learning to abstain",
    "Self-consistency improves chain of thought",
    "Semantic entropy probes",
    "Which answers are more likely to be correct",
    "Sycophancy language models",
    "Groupthink social",
    "Majority illusion",
    "Citation integrity",
    "Do language models remember factual",
    "WinoGrande",
    "HANS heuristic analysis",
    "Annotators with Agreements",
    "QA with false presuppositions CREPE",
    "Robustness to name-based biases",
    "Natural language inference stress test",
]
rows = []
for t in TITLES:
    rs = arxiv_title(t, 3)
    for r in rs:
        r["query"] = t
        rows.append(r)
    time.sleep(0.3)
    ok = [r for r in rs if "_error" not in r]
    print(f"{t!r}: {len(ok)} hits", flush=True)
with open("consensus_stress/phase1/live_search_raw3.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("total:", len(rows))
