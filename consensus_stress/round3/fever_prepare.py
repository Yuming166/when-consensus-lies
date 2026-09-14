"""Phase 6 cross-dataset: FEVER natural claim-pair cohort (offline + Qwen semantic audit).

Construction: near-duplicate SUPPORTS/REFUTES claims (cr>=0.85, tj>=0.65, single evidence).
Pair claim = C_S (the SUPPORTS claim). S-item (C_S, E_S) gold SUPPORTS; R-item (C_S, E_R)
gold REFUTES. Audited offline: J1 "E_S supports C_S" AND J2 "E_R refutes C_S" (Qwen judge).
Keeps pairs passing both; target up to 60 pairs (120 items), one pair per page.
"""
from __future__ import annotations
import difflib
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
DATASET = ROOT.parents[1] / "data" / "benchmarks" / "fever-validation.jsonl"
N_TARGET_PAIRS = 60
AUDIT_MIN_PASS_FRACTION = 0.80

JUDGE_PROMPT = (
    "You are an evidence-semantics auditor. Answer exactly one JSON object with key "
    "\"verdict\" (\"supports\" or \"refutes\") and key \"confident\" (true/false).\n\n"
    "Claim: {claim}\n\nEvidence sentence: {evidence}\n\n"
    "Question: Does the evidence sentence support or refute the claim? "
    "Reply: {{\"verdict\": \"supports\" or \"refutes\", \"confident\": true or false}}"
)


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip().casefold()


def toks(t: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", t.casefold()))


def jac(a: str, b: str) -> float:
    ta, tb = toks(a), toks(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def cr(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def load_rows():
    return [json.loads(l) for l in Path(DATASET).read_text(encoding="utf-8").splitlines() if l]


def build_candidates(rows):
    sups = [r for r in rows if r["label"] == "SUPPORTS" and len(r.get("evidence") or []) == 1]
    refs = [r for r in rows if r["label"] == "REFUTES" and len(r.get("evidence") or []) == 1]
    idx = defaultdict(list)
    for r in sups:
        ts = sorted(toks(r["claim"]))
        idx[tuple(ts[:3] + ts[-3:])].append(r)
    cands = []
    for r in refs:
        ts = sorted(toks(r["claim"]))
        best = None
        for c in idx.get(tuple(ts[:3] + ts[-3:]), [])[:80]:
            j = jac(r["claim"], c["claim"])
            if j < 0.65:
                continue
            d = cr(r["claim"], c["claim"])
            if d >= 0.85 and (best is None or d > best[0]):
                best = (d, j, c)
        if best:
            cands.append({"refutes_row": r, "supports_row": best[2], "cr": best[0], "tj": best[1]})
    return cands


def audit_pair(client, cand) -> dict:
    claim = cand["supports_row"]["claim"]
    e_s = cand["supports_row"]["evidence"][0][2]
    e_r = cand["refutes_row"]["evidence"][0][2]

    def judge(claim_, ev):
        prompt = JUDGE_PROMPT.format(claim=claim_, evidence=ev)
        try:
            res = client.call([{"role": "user", "content": prompt}], seed=20260913 + 80)
            text = res.content.strip()
            j = json.loads(text[text.index("{"):text.rindex("}") + 1])
            return str(j.get("verdict", "")).lower(), bool(j.get("confident", False))
        except Exception:
            return None, False

    v1, c1 = judge(claim, e_s)          # expect supports
    v2, c2 = judge(claim, e_r)          # expect refutes
    return {"j1_supports": v1 == "supports", "j1_confident": c1,
            "j2_refutes": v2 == "refutes", "j2_confident": c2,
            "pass": v1 == "supports" and v2 == "refutes"}


def main() -> int:
    rows = load_rows()
    cands = build_candidates(rows)
    print("candidate pairs:", len(cands))
    # one candidate per REFUTES claim already; dedupe by page (refutes evidence page)
    by_page = {}
    for c in cands:
        page = c["refutes_row"]["evidence"][0][0]
        if page not in by_page or c["cr"] > by_page[page]["cr"]:
            by_page[page] = c
    cands = sorted(by_page.values(), key=lambda c: -c["cr"])
    print("candidates after one-per-page:", len(cands))

    client = pl.CachedChatClient(ROOT / "cache", max_completion_tokens=120)
    audited = []
    for c in cands:
        a = audit_pair(client, c)
        a.update({"refutes_page": c["refutes_row"]["evidence"][0][0],
                  "supports_page": c["supports_row"]["evidence"][0][0],
                  "cr": round(c["cr"], 4), "tj": round(c["tj"], 4)})
        audited.append({**a, "refutes_claim": c["refutes_row"]["claim"], "supports_claim": c["supports_row"]["claim"],
                        "e_s": c["supports_row"]["evidence"][0][2], "e_r": c["refutes_row"]["evidence"][0][2]})
    passed = [a for a in audited if a["pass"]]
    print(f"audited={len(audited)} passed={len(passed)} pass_fraction={len(passed)/max(1,len(audited)):.3f}")
    if len(passed) / max(1, len(audited)) < AUDIT_MIN_PASS_FRACTION:
        print("WARNING: audit pass fraction below 0.80; reporting boundary")
    # deterministic hash order on claim
    passed.sort(key=lambda a: pl.hpair("fever:" + a["supports_claim"]))
    selected = passed[:N_TARGET_PAIRS]
    print("selected pairs:", len(selected))

    # distractor assignment: FEVER rows outside used pages
    used_pages = {a["refutes_page"] for a in selected} | {a["supports_page"] for a in selected}
    by_page_rows = defaultdict(list)
    for r in rows:
        pg = str(r.get("page") or (r.get("evidence") or [[None]])[0][0])
        by_page_rows.setdefault(pg, []).append(r)
    cand_rows = []
    for page in sorted(by_page_rows):
        if page in used_pages:
            continue
        rr = sorted(by_page_rows[page], key=lambda r: str(r["id"]))[0]
        if len(rr.get("evidence") or []):
            cand_rows.append({"page": page, "sentence": rr["evidence"][0][2]})
    cand_rows.sort(key=lambda r: pl.hpair("feverdist:" + r["page"]))

    pair_rows = []
    dist_map = {}
    used_dist = set()
    for idx, a in enumerate(selected):
        claim = a["supports_claim"]
        dist = None
        for cd in cand_rows:
            if cd["page"] in used_dist:
                continue
            if jac(claim, cd["sentence"]) > 0.05:
                continue
            if "\ufffd" in cd["sentence"]:
                continue
            dist = cd
            break
        if dist is None:
            raise ValueError(f"no distractor for {claim[:60]}")
        used_dist.add(dist["page"])
        pid = "fever:" + hashlib.sha256((claim + a["e_s"] + a["e_r"]).encode()).hexdigest()[:16]
        dist_map[pid] = dist["sentence"]
        pair_rows.append({
            "pair_id": pid,
            "stage": 1, "case_id": "fever", "page": a["refutes_page"],
            "claim": claim, "supports_id": "fs_" + pid, "refutes_id": "fr_" + pid,
            "supports_evidence": a["e_s"], "refutes_evidence": a["e_r"],
            "character_ratio": a["cr"], "token_jaccard": a["tj"],
            "distractor_id": "fd_" + pid, "distractor_page": dist["page"],
            "items": [
                {"item_id": pid + ":support", "gold_label": "SUPPORTS"},
                {"item_id": pid + ":refute", "gold_label": "REFUTES"},
            ],
        })

    selection = {
        "protocol": pl.PROTOCOL_VERSION + "-fever",
        "dataset": str(DATASET),
        "dataset_sha256": pl.file_sha256(DATASET),
        "n_agents": pl.N_AGENTS,
        "partition_table": [sorted(s) for s in pl.v10.PARTITION_TABLE],
        "conditions": list(pl.CONDITIONS),
        "construction": "near-duplicate SUPPORTS/REFUTES claims; pair claim = C_S; "
                        "S-item (C_S,E_S) SUPPORTS; R-item (C_S,E_R) REFUTES; audited J1/J2",
        "audit": {"n_audited": len(audited), "n_passed": len(passed),
                  "pass_fraction": round(len(passed) / max(1, len(audited)), 4)},
        "pairs": pair_rows,
        "evidence": [
            {"unique_id": r["supports_id"], "page": next((x["supports_page"] for x in selected if x["e_s"] == r["supports_evidence"]), r["page"]),
             "evidence": r["supports_evidence"], "label_role": "SUPPORTS"}
            for r in pair_rows
        ] + [
            {"unique_id": r["refutes_id"], "page": r["page"], "evidence": r["refutes_evidence"], "label_role": "REFUTES"}
            for r in pair_rows
        ] + [
            {"unique_id": r["distractor_id"], "page": r["distractor_page"], "evidence": dist_sentence(r, dist_map),
             "label_role": "distractor"}
            for r in pair_rows
        ],
    }
    pl.write_json(ROOT / "fever_selection_manifest.json", selection)
    ledger = {"protocol": pl.PROTOCOL_VERSION + "-fever", "status": "sealed",
              "items": [{"item_id": it["item_id"], "gold_label": it["gold_label"]}
                        for r in pair_rows for it in r["items"]]}
    pl.write_json(ROOT / "fever_labels_ledger.json", ledger)
    pl.write_json(ROOT / "fever_audit.json", {"candidates": audited, "selected": selected})
    print("FEVER_SELECTION_OK pairs:", len(pair_rows), "items:", sum(len(r["items"]) for r in pair_rows))
    return 0


def dist_sentence(pair, dist_map):
    return dist_map.get(pair["pair_id"], "")


if __name__ == "__main__":
    raise SystemExit(main())
