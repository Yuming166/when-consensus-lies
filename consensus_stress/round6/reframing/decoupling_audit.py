#!/usr/bin/env python3
"""Audit: mirror-equivalence of BF_reverse and decoupling decomposition.

READ-ONLY on frozen data. No model calls. Derives only quantities that are
deterministic functions of the sealed records + sealed labels ledger.

Inputs (frozen):
  round3/labels_ledger.json        (600 item_ids + gold labels, sealed)
  round3/records.jsonl             (Qwen3.5-4B, 15,000 records)
  round4/ling_records.jsonl        (Ling-3.0-tiny, 15,000 records)

Key structural fact being audited:
  For item i with gold G_i, the "reverse" view of agent a is byte-identical to
  the "original" view of agent a on the mirror item j (same pair, same claim,
  same swapped evidence units E01/E02/E03, same partition, same persona, same
  seed). Therefore Y(i, reverse, a) == Y(j, original, a) at T=0.

Definitions used (frozen protocol, round3/preregistration.md §3 and
round3/features.py):
  faithful_reverse(i,a) = 1[Y(i,reverse,a) == flip(Y(i,original,a))]
  flip_reverse(i,a)     = 1[Y(i,reverse,a) != Y(i,original,a)]  = 1 - faithful
  mirror_gold(j)        = flip(gold_i)
  mirror_correct(i,a)   = 1[Y(i,reverse,a) == flip(gold_i)]   (mirror item gold)
  BF_reverse(i)         = mean_a faithful_reverse(i,a)

Lemma (single agent call):
  faithful_reverse(i,a) = 1[y_i == G_i] * mirror_correct(i,a)
                        + 1[y_i != G_i] * (1 - mirror_correct(i,a))
  i.e. identical to mirror-item correctness only when y_i == G_i (agent correct
  on original); inverted when y_i != G_i.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # consensus_stress/
HC = 0.8


def flip(y: str) -> str:
    return "no" if y == "yes" else "yes"


def load_labels() -> dict[str, str]:
    d = json.loads((ROOT / "round3/labels_ledger.json").read_text())
    return {it["item_id"]: it["gold_label"] for it in d["items"]}


def load_records(path: Path) -> dict[str, dict]:
    """{(item_id, agent_index, condition): decision}"""
    out = {}
    for line in path.read_text().splitlines():
        r = json.loads(line)
        dec = r.get("decision") or {}
        if not dec:
            continue
        out[(r["item_id"], r["agent_index"], r["condition"])] = dec
    return out


def analyze(records: dict, labels: dict, name: str, n_agents: int = 5):
    items = sorted({k[0] for k in records if k[2] == "original"})
    rows = []
    for it in items:
        gold = labels.get(it)
        if gold is None:
            continue
        orig = [records.get((it, a, "original")) for a in range(n_agents)]
        if any(o is None for o in orig):
            continue
        ans = [o["answer"] for o in orig]
        cnt = Counter(ans)
        consensus, n_agree = cnt.most_common(1)[0]
        agreement = n_agree / n_agents
        gb = "yes" if gold == "SUPPORTS" else "no"
        wrong = int(consensus != gb)
        per = []
        for a in range(n_agents):
            y0 = ans[a]
            rev = records.get((it, a, "reverse"))
            para = records.get((it, a, "paraphrase"))
            y_rev = rev["answer"] if rev else None
            y_para = para["answer"] if para else None
            faithful_rev = None if y_rev is None else int(y_rev == flip(y0))
            faithful_para = None if y_para is None else int(y_para == y0)
            mirror_corr = None if y_rev is None else int(y_rev == flip(gb))
            per.append({
                "agent": a, "y0": y0, "gold_binary": gb,
                "y0_correct": int(y0 == gb),
                "faithful_rev": faithful_rev, "flip_rev": None if faithful_rev is None else 1 - faithful_rev,
                "mirror_correct": mirror_corr, "faithful_para": faithful_para,
            })
        rows.append({
            "item_id": it, "gold": gold, "consensus": consensus,
            "agreement": agreement, "wrong": wrong, "hc": agreement >= HC,
            "per": per,
        })
    hc = [r for r in rows if r["hc"]]
    hc_wrong = [r for r in hc if r["wrong"]]
    hc_correct = [r for r in hc if not r["wrong"]]

    def mean(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else None

    def bf_rev(r):
        return mean([p["faithful_rev"] for p in r["per"]])
    def bf_para(r):
        return mean([p["faithful_para"] for p in r["per"]])
    def mir_acc(r):
        return mean([p["mirror_correct"] for p in r["per"]])

    out = {
        "model": name,
        "n_items": len(rows), "n_hc": len(hc),
        "n_hc_wrong": len(hc_wrong), "n_hc_correct": len(hc_correct),
        "BF_reverse_correct": mean([bf_rev(r) for r in hc_correct]),
        "BF_reverse_wrong": mean([bf_rev(r) for r in hc_wrong]),
        "BF_paraphrase_correct": mean([bf_para(r) for r in hc_correct]),
        "BF_paraphrase_wrong": mean([bf_para(r) for r in hc_wrong]),
        "mirror_accuracy_correct": mean([mir_acc(r) for r in hc_correct]),
        "mirror_accuracy_wrong": mean([mir_acc(r) for r in hc_wrong]),
    }
    # Decoupling on WRONG consensus (HC): how many of the 5 agents flip on the
    # reverse call (faithful_rev==1), and how many are correct on the mirror item.
    stayed_counts = Counter()   # agents with faithful_rev == 0 (keep own answer)
    resp_counts = Counter()     # agents with faithful_rev == 1 (change to flip of own answer)
    mir_wrong_counts = Counter()
    for r in hc_wrong:
        stayed_counts[sum(p["flip_rev"] == 1 for p in r["per"])] += 1
        resp_counts[sum(p["faithful_rev"] == 1 for p in r["per"])] += 1
        mir_wrong_counts[sum(p["mirror_correct"] == 0 for p in r["per"])] += 1
    # View identity: Y(i, reverse, a) == Y(mirror(i), original, a)
    def mirror_id(item_id: str) -> str:
        return item_id.replace(":support", ":refute") if item_id.endswith(":support") \
            else item_id.replace(":refute", ":support")
    ident = {"match": 0, "total": 0, "missing_mirror": 0}
    for it, ag, cond in records:
        if cond != "reverse":
            continue
        y_rev = records.get((it, ag, "reverse"))
        y_mir = records.get((mirror_id(it), ag, "original"))
        if y_mir is None:
            ident["missing_mirror"] += 1
            continue
        ident["total"] += 1
        ident["match"] += int(y_rev["answer"] == y_mir["answer"])
    out["view_identity"] = ident
    out["wrong_consensus_stayed_distribution_over_5_agents"] = {
        str(k): stayed_counts[k] for k in sorted(stayed_counts)
    }
    out["wrong_consensus_responsive_distribution_over_5_agents"] = {
        str(k): resp_counts[k] for k in sorted(resp_counts)
    }
    out["wrong_consensus_mirror_wrong_distribution_over_5_agents"] = {
        str(k): mir_wrong_counts[k] for k in sorted(mir_wrong_counts)
    }
    n_wa = 5 * len(hc_wrong)
    out["wrong_consensus_agent_totals"] = {
        "n_agent_calls": n_wa,
        "responsive": sum(k * v for k, v in resp_counts.items()),
        "stayed": sum(k * v for k, v in stayed_counts.items()),
        "mirror_correct": n_wa - sum(k * v for k, v in mir_wrong_counts.items()),
        "mirror_wrong": sum(k * v for k, v in mir_wrong_counts.items()),
    }
    # Per-group (originally correct vs wrong) decomposition
    grp = {"orig_correct": [], "orig_wrong": []}
    for r in hc:
        for p in r["per"]:
            grp["orig_correct" if p["y0_correct"] else "orig_wrong"].append(p)
    out["per_group"] = {
        "orig_correct": {
            "n": len(grp["orig_correct"]),
            "faithful_rev": mean([p["faithful_rev"] for p in grp["orig_correct"]]),
            "mirror_correct": mean([p["mirror_correct"] for p in grp["orig_correct"]]),
            "faithful_minus_mirror": mean([p["faithful_rev"] for p in grp["orig_correct"]])
                                   - mean([p["mirror_correct"] for p in grp["orig_correct"]]),
        },
        "orig_wrong": {
            "n": len(grp["orig_wrong"]),
            "faithful_rev": mean([p["faithful_rev"] for p in grp["orig_wrong"]]),
            "mirror_correct": mean([p["mirror_correct"] for p in grp["orig_wrong"]]),
            "faithful_minus_mirror": mean([p["faithful_rev"] for p in grp["orig_wrong"]])
                                   - mean([p["mirror_correct"] for p in grp["orig_wrong"]]),
        },
    }
    return out


def main():
    labels = load_labels()
    qwen = analyze(load_records(ROOT / "round3/records.jsonl"), labels, "Qwen3.5-4B")
    ling = analyze(load_records(ROOT / "round4/ling_records.jsonl"), labels, "Ling-3.0-tiny")
    result = {"labels_ledger": "round3/labels_ledger.json",
              "qwen_records": "round3/records.jsonl",
              "ling_records": "round4/ling_records.jsonl",
              "models": [qwen, ling]}
    out_path = ROOT / "round6/reframing/decoupling_audit.json"
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
