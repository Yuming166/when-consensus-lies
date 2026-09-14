"""Round-3 paraphrase audit: judge 30 sampled paraphrase pairs meaning-preserving (offline, Qwen)."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
N_SAMPLE = 30

JUDGE_PROMPT = (
    "Decide whether the paraphrase preserves the meaning and polarity of the original "
    "sentence (no added/removed negation, no changed numbers/dates/entities). "
    "Reply with exactly one JSON object: {{\"preserves_meaning\": true or false, \"reason\": \"...\"}}\n\n"
    "Original: {src}\n\nParaphrase: {para}"
)


def main() -> int:
    manifest = json.loads((ROOT / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    items = [{"uid": uid, **row} for uid, row in manifest.items() if row.get("para1")]
    items.sort(key=lambda x: pl.hpair("paraaudit:" + x["uid"]))
    sample = items[:N_SAMPLE]
    client = pl.CachedChatClient(ROOT / "cache", max_completion_tokens=160)
    judgments = []
    for it in sample:
        prompt = JUDGE_PROMPT.format(src=it["source_text"], para=it["para1"])
        try:
            res = client.call([{"role": "user", "content": prompt}], seed=20260913 + 30)
            text = res.content.strip()
            j = json.loads(text[text.index("{"):text.rindex("}") + 1])
            ok = bool(j.get("preserves_meaning"))
        except Exception:
            ok = False
        judgments.append({"uid": it["uid"], "preserves_meaning": ok})
    n_ok = sum(1 for j in judgments if j["preserves_meaning"])
    result = {
        "protocol": pl.PROTOCOL_VERSION,
        "n_sampled": len(judgments),
        "n_preserving": n_ok,
        "fraction_preserving": round(n_ok / len(judgments), 4),
        "threshold_ge_80pct": n_ok / len(judgments) >= 0.80,
        "judgments": judgments,
    }
    pl.write_json(ROOT / "paraphrase_audit.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "judgments"}, indent=2))
    return 0 if result["threshold_ge_80pct"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
