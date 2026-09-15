#!/usr/bin/env python3
"""Round-7 W1 P0 audit (2/3): simplest paired-prediction statistic S_pair(i)=f(ŷ_i,ŷ_j).

S_pair uses ONLY the frozen original-condition panel answers of item i and its
mirror item j (_agent_answers; label-free) — no reverse calls, no paraphrase,
no labels.

Variants (label-convention note: gold SUPPORTS->yes, REFUTES->no; the reverse
oracle expects flip(y0), so 'mirror answer == flip(original answer)' is the
label-consistent form; 'mirror answer == original answer' is the same info with
sign reversed; panel-level uses the consensus answers):
  s_pair_flip(i)  = mean_a 1[y_j(a) == flip(y_i(a))]     (= BF_reverse by View Identity)
  s_pair_same(i)  = mean_a 1[y_j(a) == y_i(a)]           (= 1 - rev_flip_rate(i))
  s_pair_panel(i) = 1[consensus_j == consensus_i]

Comparison on HC subset (agreement >= 0.8): AUROC [pair-grouped bootstrap 95%
CI, seed base 20260913 + fixed offsets (round5 rule), 2000 replicates] against
BF_reverse (bf_reverse) and RS_q (risk_bf_q), plus paired AUROC diffs.

Honest conclusion is written in s_pair_diagnostic.md; this script only computes.

Outputs: consensus_stress/round7/audit/s_pair_results.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _audit_common as C

OUT = HERE.parent / "s_pair_results.json"


def add_s_pair(hc, full):
    """Attach S_pair variants; mirror answers come from the full 600-item set."""
    by_item = {r["item_id"]: r for r in full}
    for r in hc:
        j = by_item.get(C.mirror_item_id(r["item_id"]))
        if j is None:
            r["s_pair_flip"] = None
            r["s_pair_same"] = None
            r["s_pair_panel"] = None
            continue
        yi = r.get("_agent_answers", {})
        yj = j.get("_agent_answers", {})
        vals_f, vals_s = [], []
        for a in map(str, range(5)):
            if a in yi and a in yj and yi[a] in ("yes", "no") and yj[a] in ("yes", "no"):
                vals_f.append(int(yj[a] == C.flip(yi[a])))
                vals_s.append(int(yj[a] == yi[a]))
        r["s_pair_flip"] = (sum(vals_f) / len(vals_f)) if vals_f else None
        r["s_pair_same"] = (sum(vals_s) / len(vals_s)) if vals_s else None
        r["s_pair_panel"] = int(r["consensus"] == j["consensus"]) if (r.get("consensus") and j.get("consensus")) else None
        # risk-direction variants (higher = riskier, matching RS_q = -BF_q convention)
        for vk in ("s_pair_flip", "s_pair_same", "s_pair_panel"):
            v = r.get(vk)
            r[f"risk_{vk}"] = (-v) if v is not None else None
        r["risk_bf_reverse"] = (-r["bf_reverse"]) if r.get("bf_reverse") is not None else None
    return hc


def main() -> int:
    result = {
        "protocol": "round7-w1-p0-s_pair-diagnostic",
        "status": "post-hoc derivation from sealed frozen data; zero new model calls",
        "seed_base": C.SEED_BASE, "bootstrap_n": C.BOOTSTRAP_N,
        "hc_threshold": C.HC_THRESHOLD,
        "definition": {
            "s_pair_flip": "mean over 5 agents of 1[mirror-original answer == flip(original answer)]; label-consistent with reverse oracle",
            "s_pair_same": "mean over 5 agents of 1[mirror-original answer == original answer]",
            "s_pair_panel": "1[consensus(mirror) == consensus(item)]",
            "bf_reverse": "frozen bf_reverse feature (5-agent mean reverse faithfulness)",
            "rs_q": "frozen risk_bf_q = -bf_q",
        },
        "models": [],
    }
    offset = 0
    for model_key in ("qwen", "ling"):
        full = C.load_full(model_key)
        hc = C.add_mirror_refs([r for r in full if r["agreement"] >= C.HC_THRESHOLD], full=full)
        hc = add_s_pair(hc, full)
        display = C.MODEL_FILES[model_key]["display"]
        mrec = {"model": display, "n_items": len(hc),
                "n_pairs": len({r["pair_id"] for r in hc}),
                "wrong": sum(r["consensus_wrong"] for r in hc),
                "auroc": {}, "paired_diff": {}, "spearman": {},
                "exact_equality": {}}

        # item-level exact equality of S_pair variants vs frozen features
        for vk, fk in (("s_pair_flip", "bf_reverse"),
                       ("s_pair_flip", "rev_flip_rate"),
                       ("s_pair_same", "rev_flip_rate")):
            rows = [r for r in hc if r.get(vk) is not None and r.get(fk) is not None]
            if fk == "rev_flip_rate" and vk == "s_pair_same":
                # s_pair_same = 1 - rev_flip_rate by construction; check complement exactness
                eq = sum(1 for r in rows if abs(r[vk] + r[fk] - 1.0) < 1e-12)
                maxdiff = max((abs(r[vk] + r[fk] - 1.0) for r in rows), default=None)
            else:
                eq = sum(1 for r in rows if abs(r[vk] - r[fk]) < 1e-12)
                maxdiff = max((abs(r[vk] - r[fk]) for r in rows), default=None)
            mrec["exact_equality"][f"{vk}=={fk}"] = {
                "n": len(rows), "n_exact_equal": eq,
                "exact_equal_rate": eq / len(rows) if rows else None,
                "max_abs_diff": maxdiff,
            }

        for key in ("risk_s_pair_flip", "risk_s_pair_same", "risk_s_pair_panel",
                    "s_pair_flip", "s_pair_same", "s_pair_panel",
                    "risk_bf_reverse", "bf_reverse", "risk_bf_q"):
            g = C.group_bootstrap_auroc(hc, key, seed=C.SEED_BASE + offset)
            mrec["auroc"][key] = g
            offset += 1

        for key_a, key_b, label in (
                ("risk_s_pair_flip", "risk_bf_reverse", "S_pair_flip(risk) - BF_reverse(risk)"),
                ("risk_s_pair_flip", "risk_bf_q", "S_pair_flip(risk) - RS_q"),
                ("s_pair_same", "risk_bf_q", "S_pair_same(as-is) - RS_q"),
                ("s_pair_panel", "risk_bf_q", "S_pair_panel(as-is) - RS_q"),
                ("risk_bf_q", "risk_bf_reverse", "RS_q - BF_reverse(risk)"),
                ("risk_bf_q", "risk_s_pair_flip", "RS_q - S_pair_flip(risk)"),
                ("risk_bf_q", "s_pair_same", "RS_q - S_pair_same(as-is)")):
            d = C.paired_bootstrap_diff(hc, key_a, key_b, seed=C.SEED_BASE + offset)
            mrec["paired_diff"][f"{key_a}-{key_b}"] = {"label": label, **d}
            offset += 1

        for key_a, key_b, label in (
                ("s_pair_flip", "bf_reverse", "Spearman S_pair_flip vs BF_reverse"),
                ("s_pair_flip", "risk_bf_q", "Spearman S_pair_flip vs RS_q"),
                ("s_pair_same", "risk_bf_q", "Spearman S_pair_same vs RS_q")):
            s = C.spearman_ci(hc, key_a, key_b, seed=C.SEED_BASE + offset)
            mrec["spearman"][f"{key_a}__{key_b}"] = {"label": label, **s}
            offset += 1

        result["models"].append(mrec)

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
