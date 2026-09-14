"""Round-3 paper-scale: build preoutcome features from records (NO label fields)."""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round3_lib as pl

ROOT = Path(__file__).resolve().parent
FLIP_CONDITIONS = ("remove", "reverse", "synthetic_reverse")


def load_records() -> list[dict]:
    return [json.loads(line) for line in (ROOT / "records.jsonl").read_text(encoding="utf-8").splitlines() if line]


def build_features(rows: list[dict]) -> list[dict]:
    by_q: dict[str, list[dict]] = {}
    for r in rows:
        by_q.setdefault(r["cqid"], []).append(r)
    out: list[dict] = []
    for cqid in sorted(by_q):
        recs = by_q[cqid]
        by_cond = {(r["condition"], r["agent_index"]): r for r in recs}
        orig = [by_cond[("original", i)]["decision"]["answer"] for i in range(pl.N_AGENTS)
                if ("original", i) in by_cond and by_cond[("original", i)]["decision"]]
        if len(orig) != pl.N_AGENTS:
            continue
        confs = [by_cond[("original", i)]["decision"]["confidence"] for i in range(pl.N_AGENTS)]
        cnt = Counter(orig)
        consensus, n = cnt.most_common(1)[0]
        agreement = n / pl.N_AGENTS

        per_agent_f = {}
        for i in range(pl.N_AGENTS):
            y0 = orig[i]
            f = {}
            _conds = [c for c in (("paraphrase", y0), ("reverse", flip(y0)), ("synthetic_reverse", flip(y0)))
                      if c[0] in set(pl.SCORED_ALL) | {"paraphrase", "reverse"}]
            for cond, expected in _conds:
                d = by_cond.get((cond, i), {}).get("decision")
                f[cond] = None if d is None else int(d["answer"] == expected)
            per_agent_f[i] = f

        flips = {}
        for cond in FLIP_CONDITIONS:
            flips[cond] = [int(by_cond.get((cond, i), {}).get("decision") is not None
                               and by_cond[(cond, i)]["decision"]["answer"] != orig[i])
                           for i in range(pl.N_AGENTS)]

        # BF_q over primary scored conditions {paraphrase, reverse}
        n_scored = 0
        bf_sum = 0.0
        for i in range(pl.N_AGENTS):
            vals = [per_agent_f[i].get(c) for c in pl.PRIMARY_SCORED]
            if any(v is None for v in vals):
                continue
            bf_sum += sum(vals)
            n_scored += len(vals)
        bf_q = bf_sum / n_scored if n_scored else None

        per_cond_bf = {}
        for cond in pl.SCORED_ALL:
            vals = [per_agent_f[i][cond] for i in range(pl.N_AGENTS)
                    if per_agent_f[i][cond] is not None]
            per_cond_bf[cond] = sum(vals) / len(vals) if vals else None

        # R_PI (frozen weights 0.1/0.3/0.6; flip conditions {remove,reverse,synthetic_reverse})
        inert = [int(not any(flips[c][i] for c in FLIP_CONDITIONS)) for i in range(pl.N_AGENTS)]
        d_inert = sum(inert) / pl.N_AGENTS
        total_flips = sum(flips[c][i] for c in FLIP_CONDITIONS for i in range(pl.N_AGENTS))
        flip_inertia = 1.0 - total_flips / (pl.N_AGENTS * len(FLIP_CONDITIONS))
        seen: list[set] = []
        shared = 0
        for i in range(pl.N_AGENTS):
            cites = set(by_cond[("original", i)]["decision"].get("cited_evidence_ids", []))
            shared += int(any(cites & prior for prior in seen))
            seen.append(cites)
        frac_shared = shared / pl.N_AGENTS
        rpi = 0.1 * d_inert + 0.3 * flip_inertia + 0.6 * frac_shared

        # R_sym (frozen weights 0.3/0.7; V3.16.1 definitions)
        reverse_inertia = sum(1.0 - flips["reverse"][i] for i in range(pl.N_AGENTS)) / pl.N_AGENTS
        per_agent_flip_rate = [sum(flips[c][i] for c in FLIP_CONDITIONS) / len(FLIP_CONDITIONS)
                               for i in range(pl.N_AGENTS)]
        import statistics
        intervention_disagreement = min(1.0, 2.0 * statistics.pstdev(per_agent_flip_rate))
        rsym = 0.3 * reverse_inertia + 0.7 * intervention_disagreement

        out.append({
            "cqid": cqid,
            "item_id": recs[0]["item_id"],
            "pair_id": recs[0]["pair_id"],
            "stage": recs[0]["stage"],
            "consensus": consensus,
            "agreement": agreement,
            "mean_confidence": sum(confs) / len(confs),
            "conf_dispersion": max(confs) - min(confs),
            "bf_q": bf_q,
            "bf_paraphrase": per_cond_bf.get("paraphrase"),
            "bf_reverse": per_cond_bf.get("reverse"),
            "bf_synthetic_reverse": per_cond_bf.get("synthetic_reverse"),
            "para_flip_rate": sum(flips_cond("paraphrase", by_cond, orig)) / pl.N_AGENTS,
            "rev_flip_rate": sum(flips["reverse"]) / pl.N_AGENTS,
            "synth_flip_rate": sum(flips.get("synthetic_reverse", [])) / pl.N_AGENTS,
            "rem_flip_rate": sum(flips["remove"]) / pl.N_AGENTS,
            "D_inert": d_inert,
            "flip_inertia": flip_inertia,
            "frac_shared": frac_shared,
            "R_PI": rpi,
            "reverse_inertia": reverse_inertia,
            "intervention_disagreement": intervention_disagreement,
            "R_sym": rsym,
            "_agent_answers": {str(i): orig[i] for i in range(pl.N_AGENTS)},
            "_agent_confs": {str(i): confs[i] for i in range(pl.N_AGENTS)},
        })
    return out


def flip(y: str) -> str:
    return "no" if y == "yes" else "yes"


def flips_cond(cond, by_cond, orig):
    return [int(by_cond.get((cond, i), {}).get("decision") is not None
                and by_cond[(cond, i)]["decision"]["answer"] != orig[i])
            for i in range(pl.N_AGENTS)]


def main() -> int:
    rows = load_records()
    feats = build_features(rows)
    pl.write_jsonl(ROOT / "preoutcome_features.jsonl", feats)
    # per-agent per-condition faithfulness for later controls
    by_q: dict[str, dict] = {}
    for r in rows:
        by_q.setdefault(r["cqid"], {})[(r["agent_index"], r["condition"])] = r["decision"]
    for f in feats:
        q = by_q[f["cqid"]]
        f["_agent_bf"] = {}
        for i in range(pl.N_AGENTS):
            y0 = q.get((i, "original"), {}).get("answer")
            row = {}
            for cond in pl.SCORED_ALL:
                d = q.get((i, cond), {})
                if y0 is None or not d:
                    row[cond] = None
                else:
                    exp = y0 if cond == "paraphrase" else flip(y0)
                    row[cond] = int(d["answer"] == exp)
            f["_agent_bf"][str(i)] = row
    pl.write_jsonl(ROOT / "preoutcome_features.jsonl", feats)
    print(f"preoutcome features: {len(feats)} items (NO label fields)")
    print("keys sample:", sorted(feats[0].keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
