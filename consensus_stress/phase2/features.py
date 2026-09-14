"""Build preoutcome features from pilot records (NO label fields)."""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_lib as pl

ROOT = Path(__file__).resolve().parent
SCORED = ("paraphrase", "reverse")  # substitute unscored per Amendment B audit

def load_records():
    rows = [json.loads(l) for l in (ROOT / "records.jsonl").read_text().splitlines() if l]
    return rows

def build_features(rows):
    by_q = {}
    for r in rows:
        by_q.setdefault(r["cqid"], []).append(r)
    out = []
    for cqid in sorted(by_q):
        recs = by_q[cqid]
        by_cond = {}
        for r in recs:
            by_cond.setdefault((r["condition"], r["agent_index"]), r)
        orig = [by_cond[("original", i)]["decision"]["answer"] for i in range(pl.N_AGENTS)
                if ("original", i) in by_cond and by_cond[("original", i)]["decision"]]
        if len(orig) != pl.N_AGENTS:
            continue
        confs = [by_cond[("original", i)]["decision"]["confidence"] for i in range(pl.N_AGENTS)]
        # consensus
        from collections import Counter
        cnt = Counter(orig)
        consensus, n = cnt.most_common(1)[0]
        agreement = n / pl.N_AGENTS
        # per-agent faithfulness for scored conditions
        per_agent = {}
        for i in range(pl.N_AGENTS):
            y0 = orig[i]
            f = {}
            for cond in SCORED:
                d = by_cond.get((cond, i), {}).get("decision")
                if d is None:
                    f[cond] = None
                else:
                    if cond == "paraphrase":
                        f[cond] = int(d["answer"] == y0)
                    else:  # reverse
                        f[cond] = int(d["answer"] != y0)
            per_agent[i] = f
        # descriptive substitute/remove behavior
        sub_flips = []
        rem_flips = []
        for i in range(pl.N_AGENTS):
            sd = by_cond.get(("substitute", i), {}).get("decision")
            rd = by_cond.get(("remove", i), {}).get("decision")
            sub_flips.append(int(sd is not None and sd["answer"] != orig[i]))
            rem_flips.append(int(rd is not None and rd["answer"] != orig[i]))
        # BF_q over scored conditions (only agents with all scored conditions present)
        n_scored = 0
        bf_sum = 0.0
        for i in range(pl.N_AGENTS):
            vals = [per_agent[i].get(c) for c in SCORED]
            if any(v is None for v in vals):
                continue
            bf_sum += sum(vals)
            n_scored += len(vals)
        bf_q = bf_sum / n_scored if n_scored else None
        per_cond_bf = {}
        for cond in SCORED:
            vals = [per_agent[i][cond] for i in range(pl.N_AGENTS) if per_agent[i][cond] is not None]
            per_cond_bf[cond] = sum(vals) / len(vals) if vals else None
        # compute inert properly
        inert = []
        for i in range(pl.N_AGENTS):
            flips = []
            for c in ("remove", "reverse", "substitute"):
                d = by_cond.get((c, i), {}).get("decision")
                flips.append(d is not None and d["answer"] != orig[i])
            inert.append(int(not any(flips)))
        d_inert = sum(inert) / pl.N_AGENTS
        total_flips = 0
        for i in range(pl.N_AGENTS):
            for c in ("remove", "reverse", "substitute"):
                d = by_cond.get((c, i), {}).get("decision")
                if d is not None and d["answer"] != orig[i]:
                    total_flips += 1
        flip_inertia = 1.0 - total_flips / (pl.N_AGENTS * 3)
        seen = []
        shared = 0
        for i in range(pl.N_AGENTS):
            cites = set(by_cond.get(("original", i), {}).get("decision", {}).get("cited_evidence_ids", []))
            shared += int(any(cites & prior for prior in seen))
            seen.append(cites)
        frac_shared = shared / pl.N_AGENTS
        rpi = 0.1 * d_inert + 0.3 * flip_inertia + 0.6 * frac_shared
        out.append({
            "cqid": cqid,
            "consensus": consensus,
            "agreement": agreement,
            "mean_confidence": sum(confs) / len(confs),
            "conf_dispersion": max(confs) - min(confs),
            "bf_q": bf_q,
            "bf_paraphrase": per_cond_bf.get("paraphrase"),
            "bf_reverse": per_cond_bf.get("reverse"),
            "sub_flip_rate": sum(sub_flips) / pl.N_AGENTS,
            "rem_flip_rate": sum(rem_flips) / pl.N_AGENTS,
            "D_inert": d_inert,
            "flip_inertia": flip_inertia,
            "frac_shared": frac_shared,
            "R_PI": rpi,
            "_agent_answers": {str(i): orig[i] for i in range(pl.N_AGENTS)},
            "_agent_confs": {str(i): confs[i] for i in range(pl.N_AGENTS)},
        })
    return out

def main():
    rows = load_records()
    feats = build_features(rows)
    pl.write_jsonl(ROOT / "preoutcome_features.jsonl", feats)
    print(f"features: {len(feats)} questions; NO label fields: {all('label' not in f and 'gold' not in f and 'correct' not in f for f in feats)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
