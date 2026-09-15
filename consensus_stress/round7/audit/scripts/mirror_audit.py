#!/usr/bin/env python3
"""Round-7 W1 P0 audit (1/3): mirror equivalence — verbatim view identity,
answer identity (Qwen/Ling), BF_reverse vs paired-item predictions, and
how much predictive power can be reconstructed from paired-item predictions.

READ-ONLY on frozen data (benchmark/frozen/vitaminc + round3 artifacts).
Zero model calls. All derived quantities are post-hoc derivations from sealed
records + sealed labels ledger (labels merged only after preoutcome freeze).

Outputs: consensus_stress/round7/audit/mirror_audit.json
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _audit_common as C
sys.path.insert(0, str(C.R3))
import round3_lib as pl  # frozen prompt construction (read-only)
import analysis_lib as al  # frozen bootstrap conventions (read-only; used for reference)

OUT = HERE.parent / "mirror_audit.json"


def build_composites() -> dict[str, dict]:
    """Reconstruct round3 Composite payloads from frozen manifests (no model calls)."""
    sel = json.loads((C.R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    para = json.loads((C.R3 / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    ev = {e["unique_id"]: str(e["evidence"]) for e in sel["evidence"]}
    comps: dict[str, dict] = {}
    for p in sel["pairs"]:
        pid = p["pair_id"]
        dist_id = p["distractor_id"]
        base = {
            "pair_id": pid, "stage": p["stage"], "claim": p["claim"],
            "supports_id": p["supports_id"], "refutes_id": p["refutes_id"],
            "distractor": ev.get(dist_id, ""),
            "distractor_para": (para.get(dist_id, {}).get("para1") or ""),
        }
        for role, gold, gold_yes in (("support", "SUPPORTS", True), ("refute", "REFUTES", False)):
            own = p["supports_id"] if role == "support" else p["refutes_id"]
            opp = p["refutes_id"] if role == "support" else p["supports_id"]
            comps[f"{pid}:{role}"] = {
                **base,
                "item_id": f"{pid}:{role}", "gold_label": gold, "gold_yes": gold_yes,
                "evidence": ev.get(own, ""), "evidence_opp": ev.get(opp, ""),
                "para1": para.get(own, {}).get("para1") or "",
                "para1_opp": para.get(opp, {}).get("para1") or "",
                "para2": para.get(own, {}).get("para2") or "",
                "source_ids": (own, opp),
            }
    return comps


def comp_to_round3(comp: dict) -> pl.Composite:
    return pl.Composite(
        pair_id=comp["pair_id"], stage=comp["stage"], item_id=comp["item_id"],
        cqid=pl.cqid_for(comp["item_id"]), claim=comp["claim"],
        gold_label=comp["gold_label"], gold_yes=comp["gold_yes"],
        evidence=comp["evidence"], evidence_opp=comp["evidence_opp"],
        para1=comp["para1"], para1_opp=comp["para1_opp"], para2=comp["para2"],
        distractor=comp["distractor"], distractor_para=comp["distractor_para"],
        source_ids=tuple(comp["source_ids"]),
    )


def verbatim_identity(comps: dict[str, dict]) -> dict:
    """reverse(i) messages vs original(mirror(i)) messages, per (item, agent)."""
    total = match_units = match_messages = 0
    for item_id, cdict in sorted(comps.items()):
        mirror_id = C.mirror_item_id(item_id)
        c = comp_to_round3(cdict)
        cm = comp_to_round3(comps[mirror_id])
        for a in range(pl.N_AGENTS):
            view_rev = pl.build_view(c, a, "reverse")
            view_orig = pl.build_view(cm, a, "original")
            msgs_rev = pl.build_messages(c, view_rev,
                                         agent_id=pl.v10.AGENT_PERSONAS[a][0],
                                         persona=pl.v10.AGENT_PERSONAS[a][1])
            msgs_orig = pl.build_messages(cm, view_orig,
                                          agent_id=pl.v10.AGENT_PERSONAS[a][0],
                                          persona=pl.v10.AGENT_PERSONAS[a][1])
            total += 1
            match_units += int(pl.unit_texts(c, "reverse") == pl.unit_texts(cm, "original"))
            match_messages += int(pl.canonical_json(msgs_rev) == pl.canonical_json(msgs_orig))
    return {"n_calls": total, "unit_texts_identical": match_units,
            "messages_identical": match_messages,
            "unit_texts_rate": match_units / total,
            "messages_rate": match_messages / total}


def answer_identity(model_key: str) -> dict:
    """Y(reverse(i), a) == Y(original(mirror(i)), a) from sealed records."""
    recs = C.load_jsonl(C.MODEL_FILES[model_key]["records"])
    by_key: dict[tuple, dict] = {}
    for r in recs:
        dec = r.get("decision") or {}
        if dec:
            by_key[(r["item_id"], r["agent_index"], r["condition"])] = dec
    n_match = n_total = 0
    n_item_full = n_item_total = 0
    n_consensus_match = n_consensus_total = 0
    by_item: dict[str, list[tuple[str, str]]] = {}
    for (item_id, a, cond), dec in by_key.items():
        if cond != "reverse":
            continue
        mir = by_key.get((C.mirror_item_id(item_id), a, "original"))
        n_total += 1
        if mir is not None:
            n_match += int(dec["answer"] == mir["answer"])
        by_item.setdefault(item_id, []).append((dec["answer"],
                                                by_key.get((C.mirror_item_id(item_id), a, "original"), {}).get("answer")))
    for item_id, pairs in by_item.items():
        if len(pairs) != pl.N_AGENTS:
            continue
        n_item_total += 1
        if all(a1 is not None and a1 == a2 for a1, a2 in pairs):
            n_item_full += 1
        if all(a2 is not None for _, a2 in pairs):
            c_rev = Counter(a1 for a1, _ in pairs)
            c_orig = Counter(a2 for _, a2 in pairs)
            n_consensus_total += 1
            n_consensus_match += int(c_rev.most_common(1)[0][0] == c_orig.most_common(1)[0][0])
    return {"agent_call_match": n_match, "agent_call_total": n_total,
            "agent_call_rate": (n_match / n_total) if n_total else None,
            "item_full_match": n_item_full, "item_full_total": n_item_total,
            "item_full_rate": (n_item_full / n_item_total) if n_item_total else None,
            "consensus_match": n_consensus_match, "consensus_total": n_consensus_total,
            "consensus_rate": (n_consensus_match / n_consensus_total) if n_consensus_total else None}


def main() -> int:
    comps = build_composites()
    verbatim = verbatim_identity(comps)

    result = {
        "protocol": "round7-w1-p0-mirror-equivalence-audit",
        "status": "post-hoc derivation from sealed frozen data; zero new model calls",
        "seed_base": C.SEED_BASE, "bootstrap_n": C.BOOTSTRAP_N,
        "hc_threshold": C.HC_THRESHOLD,
        "verbatim_view_identity": verbatim,
        "answer_identity": {},
        "correlations": {},
        "mirror_only_reconstruction": {},
        "wrong_joint": {},
        "models": [],
    }

    # --- correlations & reconstruction per model (HC subset) ---
    offset = 0
    for model_key in ("qwen", "ling"):
        full = C.load_full(model_key)
        hc = C.add_mirror_refs([r for r in full if r["agreement"] >= C.HC_THRESHOLD], full=full)
        display = C.MODEL_FILES[model_key]["display"]
        ai = answer_identity(model_key)
        result["answer_identity"][model_key] = {"model": display, **ai}

        corr_pairs = [
            ("bf_reverse", "mirror_bf_reverse", "BF_reverse(i) vs BF_reverse(mirror j)"),
            ("bf_reverse", "mirror_rev_flip_rate", "BF_reverse(i) vs rev_flip_rate(j)"),
            ("bf_reverse", "mirror_risk_bf_q", "BF_reverse(i) vs RS_q(j)"),
            ("bf_reverse", "mirror_bf_paraphrase", "BF_reverse(i) vs bf_paraphrase(j)"),
            ("bf_reverse", "mirror_agreement", "BF_reverse(i) vs agreement(j)"),
            ("bf_reverse", "mirror_mean_confidence", "BF_reverse(i) vs mean_confidence(j)"),
            ("risk_bf_q", "mirror_risk_bf_q", "RS_q(i) vs RS_q(j)"),
            ("rev_flip_rate", "mirror_rev_flip_rate", "rev_flip_rate(i) vs rev_flip_rate(j)"),
            ("bf_paraphrase", "mirror_bf_paraphrase", "bf_paraphrase(i) vs bf_paraphrase(j)"),
        ]
        corrs = {}
        for key_a, key_b, label in corr_pairs:
            sp = C.spearman_ci(hc, key_a, key_b, seed=C.SEED_BASE + offset)
            rows = [r for r in hc if r.get(key_a) is not None and r.get(key_b) is not None]
            exact = sum(1 for r in rows if abs(r[key_a] - r[key_b]) < 1e-12)
            corrs[f"{key_a}__{key_b}"] = {
                "label": label, **sp,
                "pearson": C.pearson([r[key_a] for r in rows], [r[key_b] for r in rows]),
                "n_exact_equal": exact,
                "n": len(rows),
                "exact_equal_rate": exact / len(rows) if rows else None,
            }
            offset += 1
        result["correlations"][model_key] = {"model": display, "pairs": corrs}

        # risk-direction variants (higher = riskier, matching RS_q = -BF_q)
        for r in hc:
            r["risk_bf_reverse"] = (-r["bf_reverse"]) if r.get("bf_reverse") is not None else None
            for vk in ("mirror_bf_reverse", "mirror_rev_flip_rate"):
                v = r.get(vk)
                r[f"risk_{vk}"] = (-v) if v is not None else None
        recon_pairs = [
            ("mirror_risk_bf_q", "mirror RS_q(j) on wrong(i)"),
            ("risk_mirror_bf_reverse", "mirror BF_reverse(j) on wrong(i) (risk dir)"),
            ("risk_mirror_rev_flip_rate", "mirror rev_flip_rate(j) on wrong(i) (risk dir)"),
            ("mirror_bf_paraphrase", "mirror bf_paraphrase(j) on wrong(i)"),
            ("mirror_agreement", "mirror agreement(j) on wrong(i)"),
            ("mirror_mean_confidence", "mirror mean_confidence(j) on wrong(i)"),
            ("risk_bf_q", "own RS_q(i) on wrong(i) [reference]"),
            ("risk_bf_reverse", "own BF_reverse(i) on wrong(i) (risk dir) [reference]"),
        ]
        recon = {}
        for key, label in recon_pairs:
            g = C.group_bootstrap_auroc(hc, key, seed=C.SEED_BASE + offset)
            recon[key] = {"label": label, **g}
            offset += 1
        result["mirror_only_reconstruction"][model_key] = {"model": display, "auroc": recon}

        # wrong(i) x wrong(j) joint on HC items where mirror is also present
        joint = Counter()
        for r in hc:
            if r["mirror_item_id"] is None or r.get("mirror_consensus_wrong") is None:
                continue
            joint[(r["consensus_wrong"], r["mirror_consensus_wrong"])] += 1
        total = sum(joint.values())
        result["wrong_joint"][model_key] = {
            "model": display,
            "both_wrong": joint[(1, 1)], "i_wrong_j_correct": joint[(1, 0)],
            "i_correct_j_wrong": joint[(0, 1)], "both_correct": joint[(0, 0)],
            "n_items_with_mirror_hc": total,
            "p_both_wrong_given_i_wrong": (joint[(1, 1)] / (joint[(1, 1)] + joint[(1, 0)])
                                           if joint[(1, 1)] + joint[(1, 0)] else None),
        }
        result["models"].append({"model": display, "hc_n": len(hc),
                                 "hc_pairs": len({r["pair_id"] for r in hc}),
                                 "hc_wrong": sum(r["consensus_wrong"] for r in hc)})

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
