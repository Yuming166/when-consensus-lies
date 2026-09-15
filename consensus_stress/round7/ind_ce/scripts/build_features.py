#!/usr/bin/env python3
"""Round-7 W2: build label-free preoutcome features (NO label fields) from
our three-condition records + frozen round6 gpt original answers."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
R6 = HERE.parent.parent / "round6" / "large_model"

PROTOCOL = "cs-paper-ind-ce-20260914-round7-w2"
CONDITIONS = ("natural", "ind", "placebo")


def flip(y0: str, y1: str) -> int:
    return int(y0 != y1)


def load_records() -> dict:
    out = {}
    for fn in ("records_smoke.jsonl", "records.jsonl"):
        for line in (HERE / fn).read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            r = json.loads(line)
            out[(r["item_id"], r["agent_index"], r["condition"])] = r
    return out


def load_round6_original() -> dict:
    out = {}
    for line in (R6 / "records.jsonl").read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        r = json.loads(line)
        if r["condition"] == "original" and r.get("decision"):
            out[(r["item_id"], r["agent_index"])] = r["decision"]
    return out


def main() -> int:
    recs = load_records()
    orig = load_round6_original()
    items = sorted({k[0] for k in recs})
    feats = []
    by_item = {}
    for it in items:
        orig_answers = [orig.get((it, i)) for i in range(5)]
        if any(d is None for d in orig_answers):
            continue  # round-3 rule: all 5 original answers required
        answers = [d["answer"] for d in orig_answers]
        confs = [d["confidence"] for d in orig_answers]
        consensus = max(set(answers), key=answers.count)
        agreement = answers.count(consensus) / 5.0
        row = {
            "protocol_version": PROTOCOL,
            "item_id": it, "pair_id": ":".join(it.split(":")[:2]),
            "cqid": None,  # filled below
            "consensus": consensus, "agreement": agreement,
            "mean_confidence": round(sum(confs) / 5.0, 4),
            "conf_dispersion": round(max(confs) - min(confs), 4),
        }
        by_item[it] = row
    # add cqid (must match round3 cqid_for)
    import sys
    sys.path.insert(0, str(HERE.parent.parent / "round3"))
    import round3_lib as pl
    for it, row in by_item.items():
        row["cqid"] = pl.cqid_for(it)
    # per-condition flip stats
    for cond in CONDITIONS:
        for it, row in by_item.items():
            flips = []
            for i in range(5):
                r = recs.get((it, i, cond))
                if r and r.get("decision"):
                    flips.append(flip(orig[(it, i)]["answer"], r["decision"]["answer"]))
            row[f"S_{cond}"] = round(sum(flips) / 5.0, 4) if len(flips) == 5 else None
            row[f"n_{cond}"] = len(flips)
    # combined score (frozen weights)
    for it, row in by_item.items():
        a, b = row.get("S_natural"), row.get("S_ind")
        row["S_combined"] = round(0.5 * a + 0.5 * b, 4) if (a is not None and b is not None) else None
    # ---- S_pair (W1 definition) on gpt round6 original answers ----
    pair_consensus = {}
    for it, row in by_item.items():
        pair_consensus.setdefault(row["pair_id"], {})[it] = row["consensus"]
    pair_answers = {}
    for it, row in by_item.items():
        pair_answers.setdefault(row["pair_id"], {})[it] = {i: orig[(it, i)]["answer"] for i in range(5)}
    for it, row in by_item.items():
        pid = row["pair_id"]
        mate = [k for k in pair_answers[pid] if k != it]
        if not mate:
            row.update({"S_pair_panel_gpt": None, "S_pair_flip_gpt": None, "S_pair_same_gpt": None})
            continue
        ya = pair_answers[pid][it]
        yj = pair_answers[pid][mate[0]]
        vals_f, vals_s = [], []
        for i in range(5):
            if ya[i] and yj[i]:
                vals_f.append(int(yj[i] == ("no" if ya[i] == "yes" else "yes")))
                vals_s.append(int(yj[i] == ya[i]))
        row["S_pair_panel_gpt"] = int(row["consensus"] == pair_consensus[pid][mate[0]])
        row["S_pair_flip_gpt"] = round(sum(vals_f) / len(vals_f), 4) if vals_f else None
        row["S_pair_same_gpt"] = round(sum(vals_s) / len(vals_s), 4) if vals_s else None
    # ---- S_pair (W1 definition) on Qwen frozen round3 features ----
    qwen = {}
    for line in (R3 / "preoutcome_features.jsonl").read_text(encoding="utf-8").splitlines():
        if line:
            q = json.loads(line)
            qwen[q["item_id"]] = q
    def _flip(y): return "no" if y == "yes" else "yes"
    for it, row in by_item.items():
        pid = row["pair_id"]
        mate_id = None
        for k in qwen:
            if k != it and k.split(":")[0] + ":" + k.split(":")[1] == pid:
                mate_id = k
                break
        qi, qj = qwen.get(it), qwen.get(mate_id) if mate_id else None
        if qi is None or qj is None:
            row.update({"S_pair_panel_qwen": None, "S_pair_flip_qwen": None, "S_pair_same_qwen": None})
            continue
        yi, yj = qi.get("_agent_answers", {}), qj.get("_agent_answers", {})
        vf, vs = [], []
        for a in map(str, range(5)):
            if yi.get(a) in ("yes", "no") and yj.get(a) in ("yes", "no"):
                vf.append(int(yj[a] == _flip(yi[a])))
                vs.append(int(yj[a] == yi[a]))
        row["S_pair_panel_qwen"] = int(qi["consensus"] == qj["consensus"]) if (qi.get("consensus") and qj.get("consensus")) else None
        row["S_pair_flip_qwen"] = round(sum(vf) / len(vf), 4) if vf else None
        row["S_pair_same_qwen"] = round(sum(vs) / len(vs), 4) if vs else None
    # S_pair_gpt alias (panel consensus-same, W1 definition on gpt round6)
    pair_consensus = {}
    for it, row in by_item.items():
        pair_consensus.setdefault(row["pair_id"], {})[it] = row["consensus"]
    for it, row in by_item.items():
        pid = row["pair_id"]
        mate = [k for k in pair_consensus[pid] if k != it]
        row["S_pair_gpt"] = row.get("S_pair_panel_gpt") if not mate else None
    # per-agent flip vectors (for diagnostics)
    for it, row in by_item.items():
        row["_agent_flip"] = {cond: {str(i): None for i in range(5)} for cond in CONDITIONS}
        for cond in CONDITIONS:
            for i in range(5):
                r = recs.get((it, i, cond))
                if r and r.get("decision"):
                    row["_agent_flip"][cond][str(i)] = flip(orig[(it, i)]["answer"], r["decision"]["answer"])
    feats = [by_item[it] for it in sorted(by_item)]
    out_path = HERE / "preoutcome_features.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in feats:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    h = hashlib.sha256(out_path.read_bytes()).hexdigest()
    meta = {"protocol": PROTOCOL, "n_items": len(feats),
            "label_free": True, "sha256": h,
            "conditions": list(CONDITIONS),
            "note": "consensus/agreement/mean_confidence from frozen round6 gpt-6-astra original; "
                    "S_* from round7 three-condition run; no label fields."}
    (HERE / "preoutcome_features_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print("n features:", len(feats))
    print("keys sample:", sorted(feats[0].keys()) if feats else "NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
