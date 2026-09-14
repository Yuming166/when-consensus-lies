#!/usr/bin/env python3
"""Round-6 Agent B: build label-blind per-item probe scores from frozen records.

Reversal-only / reversal+paraphrase cost-curve probes. NO label fields are read or
written. All scores are derived from the frozen Round-3 (Qwen) and Round-4 (Ling)
records plus the frozen label-blind preoutcome features (used ONLY for a consistency
cross-check, not for scores).

Probe definitions (risk direction; higher = predicted more likely consensus wrong;
`1 - BF` is a monotone shift of the leaderboard convention `-BF`):

- reversal-only probe at K calls/item (K in {1,2,5}): mean f_reverse over the first K
  agents (agent_index 0..K-1) on the natural-reverse condition.
    f_reverse(agent i) = 1 if the agent's natural-reverse answer == flip(its own
    frozen original answer), else 0; None if the reverse call is missing/invalid.
  Budget = K natural-reverse calls/item on top of the already-formed 5-agent consensus.
- reversal-only(10): mean over all 5 agents' natural-reverse (5 calls) + all 5 agents'
  synthetic-reverse (5 calls); both conditions share the frozen oracle expectation
  flip(y0). Budget = 10 reversal-family calls/item.
- reversal+paraphrase combo at 2K calls/item (K in {1,2,5}): mean over the first K
  agents of (f_paraphrase + f_reverse)/2. K=5 equals the frozen BF_q score function
  (10 scored calls).
- RS_q: frozen -BF_q (25 calls/item, parent protocol), the proposed method.

Missing/invalid calls are treated as missing responses (not labels), exactly like the
Round-5 protocol; a probe score is the mean over the valid calls among its selected
calls, and is missing only if none are valid.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
# repo root: .../when-consensus-lies-publish-20260911
ROOT = HERE
for _ in range(5):
    if (ROOT / "consensus_stress" / "benchmark").is_dir():
        break
    ROOT = ROOT.parent
FROZEN = ROOT / "consensus_stress" / "benchmark" / "frozen" / "vitaminc"
OUT = HERE.parent / "label_blind"

N_AGENTS = 5
MODELS = {
    "qwen": {"records": FROZEN / "records.jsonl", "features": FROZEN / "preoutcome_features.jsonl"},
    "ling": {"records": FROZEN / "ling_records.jsonl", "features": FROZEN / "ling_preoutcome_features.jsonl"},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def flip(answer: str) -> str:
    return "no" if answer == "yes" else "yes"


def decision_answer(record: dict) -> str | None:
    d = record.get("decision")
    return d.get("answer") if isinstance(d, dict) and d.get("answer") in ("yes", "no") else None


def usage_of(record: dict) -> dict:
    attempts = record.get("attempts") or []
    usage = attempts[-1].get("usage") if attempts else record.get("usage")
    return dict(usage or {})


def mean_valid(values: list[float | None]) -> float | None:
    valid = [v for v in values if v is not None]
    return float(sum(valid) / len(valid)) if valid else None


def token_sum(records: list[dict]) -> dict:
    sums = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for rec in records:
        usage = usage_of(rec)
        for key in sums:
            val = usage.get(key)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                sums[key] += val
    return sums


def per_agent_fidelity(records_by_cond_agent: dict) -> dict:
    """For each agent i: y0 (own original answer) and f_para/f_rev/f_srev (None if invalid)."""
    out = {}
    for i in range(N_AGENTS):
        orig = records_by_cond_agent.get(("original", i))
        y0 = decision_answer(orig) if orig else None
        row = {"y0": y0, "f_paraphrase": None, "f_reverse": None, "f_synthetic_reverse": None}
        if y0 is not None:
            expected = {"paraphrase": y0, "reverse": flip(y0), "synthetic_reverse": flip(y0)}
            for cond, key in (("paraphrase", "f_paraphrase"),
                              ("reverse", "f_reverse"),
                              ("synthetic_reverse", "f_synthetic_reverse")):
                rec = records_by_cond_agent.get((cond, i))
                ans = decision_answer(rec) if rec else None
                if ans is not None:
                    row[key] = int(ans == expected[cond])
        out[i] = row
    return out


def build_scores(model: str) -> list[dict]:
    cfg = MODELS[model]
    records = load_jsonl(cfg["records"])
    by_item: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        by_item[rec["cqid"]].append(rec)

    rows: list[dict] = []
    for cqid in sorted(by_item):
        recs = by_item[cqid]
        item_id = recs[0]["item_id"]
        pair_id = recs[0]["pair_id"]
        by_cond_agent = {(r["condition"], r["agent_index"]): r for r in recs}
        fid = per_agent_fidelity(by_cond_agent)

        f_rev = [fid[i]["f_reverse"] for i in range(N_AGENTS)]
        f_srev = [fid[i]["f_synthetic_reverse"] for i in range(N_AGENTS)]
        f_para = [fid[i]["f_paraphrase"] for i in range(N_AGENTS)]
        y0s = [fid[i]["y0"] for i in range(N_AGENTS)]

        # ---- label-blind risk scores (1 - BF) ----
        risk_rev_k1 = 1.0 - mean_valid(f_rev[:1])
        risk_rev_k2 = 1.0 - mean_valid(f_rev[:2])
        risk_rev_k5 = 1.0 - mean_valid(f_rev[:5])
        risk_rev_k10 = 1.0 - mean_valid(f_rev[:5] + f_srev[:5])

        combo_vals = lambda k: [v for i in range(k) for v in (f_para[i], f_rev[i])]
        risk_combo_k1 = 1.0 - mean_valid(combo_vals(1))
        risk_combo_k2 = 1.0 - mean_valid(combo_vals(2))
        risk_combo_k5 = 1.0 - mean_valid(combo_vals(5))

        # ---- token/call accounting per probe (label-blind) ----
        def tokens_for(conds_and_agents):
            return token_sum([by_cond_agent[(cond, i)]
                              for cond, i in conds_and_agents
                              if (cond, i) in by_cond_agent])

        rows.append({
            "cqid": cqid,
            "item_id": item_id,
            "pair_id": pair_id,
            "_y0": y0s,
            "_f_paraphrase": f_para,
            "_f_reverse": f_rev,
            "_f_synthetic_reverse": f_srev,
            "risk_reversal_only_k1": risk_rev_k1,
            "risk_reversal_only_k2": risk_rev_k2,
            "risk_reversal_only_k5": risk_rev_k5,
            "risk_reversal_only_k10": risk_rev_k10,
            "risk_reversal_paraphrase_k1": risk_combo_k1,
            "risk_reversal_paraphrase_k2": risk_combo_k2,
            "risk_reversal_paraphrase_k5": risk_combo_k5,
            "reverse_valid_n": sum(v is not None for v in f_rev),
            "tokens": {
                "rev_k1": tokens_for([("reverse", 0)]),
                "rev_k2": tokens_for([("reverse", i) for i in range(2)]),
                "rev_k5": tokens_for([("reverse", i) for i in range(5)]),
                "rev_k10": tokens_for([("reverse", i) for i in range(5)]
                                      + [("synthetic_reverse", i) for i in range(5)]),
                "combo_k1": tokens_for([("paraphrase", 0), ("reverse", 0)]),
                "combo_k2": tokens_for([(c, i) for i in range(2) for c in ("paraphrase", "reverse")]),
                "combo_k5": tokens_for([(c, i) for i in range(5) for c in ("paraphrase", "reverse")]),
                "rs_q_full": token_sum(recs),
            },
        })
    return rows


def consistency_check(model: str, rows: list[dict]) -> dict:
    """Cross-check records-derived scores against frozen label-blind features (no labels)."""
    cfg = MODELS[model]
    feats = {f["cqid"]: f for f in load_jsonl(cfg["features"])}
    rev_mm = para_mm = combo_mm = 0
    rev_check = para_check = combo_check = 0
    for row in rows:
        f = feats[row["cqid"]]
        bf_rev_from_rec = mean_valid(row["_f_reverse"])
        bf_rev_frozen = f.get("bf_reverse")
        if bf_rev_frozen is not None:
            rev_check += 1
            rev_mm += abs(bf_rev_from_rec - bf_rev_frozen) > 1e-9
        bf_para_from_rec = mean_valid(row["_f_paraphrase"])
        bf_para_frozen = f.get("bf_paraphrase")
        if bf_para_frozen is not None:
            para_check += 1
            para_mm += abs(bf_para_from_rec - bf_para_frozen) > 1e-9
        bf_q_from_rec = mean_valid([v for i in range(N_AGENTS)
                                    for v in (row["_f_paraphrase"][i], row["_f_reverse"][i])])
        bf_q_frozen = f.get("bf_q")
        if bf_q_frozen is not None:
            combo_check += 1
            combo_mm += abs(bf_q_from_rec - bf_q_frozen) > 1e-9
    return {
        "model": model,
        "n_items_checked": len(rows),
        "bf_reverse_checked": rev_check, "bf_reverse_mismatch": rev_mm,
        "bf_paraphrase_checked": para_check, "bf_paraphrase_mismatch": para_mm,
        "bf_q_checked": combo_check, "bf_q_mismatch": combo_mm,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"protocol": "cs-round6-cost-curve-20260914",
               "parent": "cs-round5-matched-baselines-cst-bench-20260913",
               "note": "label-blind; no gold labels or consensus_wrong used; 1-BF is a "
                       "monotone shift of the -BF leaderboard convention.",
               "frozen_input_hashes": {name: sha256(path) for name, path in {
                   "records": MODELS["qwen"]["records"], "ling_records": MODELS["ling"]["records"],
                   "features": MODELS["qwen"]["features"], "ling_features": MODELS["ling"]["features"],
               }.items()},
               "models": {}}
    for model, cfg in MODELS.items():
        rows = build_scores(model)
        out_path = OUT / f"probe_scores_label_blind_{model}.jsonl"
        write_jsonl(out_path, rows)
        consistency = consistency_check(model, rows)
        consistency["scores_path"] = str(out_path.relative_to(ROOT))
        consistency["scores_sha256"] = sha256(out_path)
        consistency["n_items"] = len(rows)
        consistency["missing_reverse_calls"] = sum(
            1 for r in rows for v in r["_f_reverse"] if v is None)
        consistency["items_with_score"] = {
            key: sum(r[key] is not None for r in rows)
            for key in ("risk_reversal_only_k1", "risk_reversal_only_k2", "risk_reversal_only_k5",
                        "risk_reversal_only_k10", "risk_reversal_paraphrase_k5")
        }
        summary["models"][model] = consistency
        print(json.dumps(consistency, ensure_ascii=False, indent=2, sort_keys=True))
    summary_path = OUT / "probe_scores_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    print("summary:", summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
