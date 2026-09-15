#!/usr/bin/env python3
"""Round-7 W2b STRICT analysis. Label merge happens AFTER preoutcome features are
frozen (hash verified). Pair-grouped bootstrap, 2,000 reps, seed family 20260915+k.
Computes: flip rates + Delta_CE CI; S_ind_strict AUROC/Risk@80 on HC; paired AUROC
increments vs S_natural / RS_q / S_pm; rho(S_natural, S_ind_strict); OOF logistic
increments; gates; leakage audit."""
from __future__ import annotations
import hashlib, json, math, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
R3 = HERE.parent.parent / "round3"
R6 = HERE.parent.parent / "round6" / "large_model"
W2 = HERE.parent / "ind_ce"
sys.path.insert(0, str(R3))
sys.path.insert(0, str(HERE / "scripts"))
sys.path.insert(0, "/home/gaoym/.tmp_sp500_naacl_symmetric_20260909/src")
import analysis_lib as al  # noqa: E402
from relay_client import write_json  # noqa: E402

BOOTSTRAP_N = 2000
BOOT_SEED = 20260915
HC_THRESHOLD = 0.8
CONDITIONS = ("ind_strict", "pm", "natural")


def load_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l]


def flip_rate_and_ci(ours, orig, cond, *, seed, n=BOOTSTRAP_N, item_filter=None):
    rng = random.Random(seed)
    rows = []
    for (it, i, c), d in ours.items():
        if c != cond:
            continue
        if item_filter is not None and it not in item_filter:
            continue
        y0 = orig.get((it, i))
        if y0 is not None:
            rows.append((":".join(it.split(":")[:2]), int(y0 != d["answer"])))
    obs = sum(v for _, v in rows) / max(1, len(rows))
    by_pair = {}
    for pid, v in rows:
        by_pair.setdefault(pid, []).append(v)
    groups = sorted(by_pair)

    def stat():
        s = []
        for _ in range(len(groups)):
            s.extend(by_pair[rng.choice(groups)])
        return sum(s) / max(1, len(s))

    vals = sorted(stat() for _ in range(n))
    return {"rate": round(obs, 4), "n": len(rows), "n_pairs": len(groups),
            "ci": [round(vals[int(0.025 * n)], 4), round(vals[int(0.975 * n) - 1], 4)]}


def diff_ci(ours, orig, key_a, key_b, *, seed, n=BOOTSTRAP_N, item_filter=None):
    rng = random.Random(seed)
    rows_a, rows_b = [], []
    for (it, i, c), d in ours.items():
        if item_filter is not None and it not in item_filter:
            continue
        y0 = orig.get((it, i))
        if y0 is None:
            continue
        pid = ":".join(it.split(":")[:2])
        if c == key_a:
            rows_a.append((pid, int(y0 != d["answer"])))
        elif c == key_b:
            rows_b.append((pid, int(y0 != d["answer"])))
    obs_a = sum(v for _, v in rows_a) / max(1, len(rows_a))
    obs_b = sum(v for _, v in rows_b) / max(1, len(rows_b))
    obs = obs_a - obs_b
    by_a, by_b = {}, {}
    for pid, v in rows_a:
        by_a.setdefault(pid, []).append(v)
    for pid, v in rows_b:
        by_b.setdefault(pid, []).append(v)
    groups = sorted(set(by_a) | set(by_b))

    def stat():
        sa, sb = [], []
        for _ in range(len(groups)):
            pid = rng.choice(groups)
            sa.extend(by_a.get(pid, []))
            sb.extend(by_b.get(pid, []))
        return (sum(sa) / max(1, len(sa))) - (sum(sb) / max(1, len(sb)))

    vals = sorted(stat() for _ in range(n))
    return {"diff": round(obs, 4), "n_a": len(rows_a), "n_b": len(rows_b),
            "ci": [round(vals[int(0.025 * n)], 4), round(vals[int(0.975 * n) - 1], 4)]}


def rho_ci(feats, key_a, key_b, *, seed, n=BOOTSTRAP_N):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key_a) is not None and f.get(key_b) is not None]
    by_pair = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    groups = sorted(by_pair)
    obs = al.spearman([f[key_a] for f in rows], [f[key_b] for f in rows])
    vals = []
    for _ in range(n):
        sample = []
        for _ in range(len(groups)):
            sample.extend(by_pair[rng.choice(groups)])
        r = al.spearman([f[key_a] for f in sample], [f[key_b] for f in sample])
        if r is not None:
            vals.append(r)
    vals = sorted(vals)
    return {"rho": round(obs, 4) if obs is not None else None,
            "ci": [round(vals[int(0.025 * len(vals))], 4),
                   round(vals[int(0.975 * len(vals)) - 1], 4)],
            "n": len(rows)}


def oof_logistic_incr(feats, cols_a, cols_b, label_key, *, seed):
    """Leave-one-pair-out logistic. cols_b = cols_a + [extra]. Returns OOF AUROC for
    both models + paired-bootstrap CI on the difference of fixed OOF predictions."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    rows = [f for f in feats if all(f.get(c) is not None for c in cols_a + cols_b)
            and f.get(label_key) is not None]
    by_pair = {}
    for f in rows:
        by_pair.setdefault(f["pair_id"], []).append(f)
    pairs = sorted(by_pair)
    preds_a, preds_b, y = {}, {}, {}
    for pid in pairs:
        test = by_pair[pid]
        train = [f for p in pairs if p != pid for f in by_pair[p]]
        Xa = np.array([[f[c] for c in cols_a] for f in train])
        Xb = np.array([[f[c] for c in cols_b] for f in train])
        ya = np.array([f[label_key] for f in train])
        if len(set(ya.tolist())) < 2 or len(train) < 4:
            for f in test:
                preds_a[f["item_id"]] = 0.5
                preds_b[f["item_id"]] = 0.5
                y[f["item_id"]] = f[label_key]
            continue
        clf_a = LogisticRegression(max_iter=2000)
        clf_b = LogisticRegression(max_iter=2000)
        try:
            clf_a.fit(Xa, ya)
            clf_b.fit(Xb, ya)
        except Exception:
            for f in test:
                preds_a[f["item_id"]] = 0.5
                preds_b[f["item_id"]] = 0.5
                y[f["item_id"]] = f[label_key]
            continue
        for f in test:
            preds_a[f["item_id"]] = float(clf_a.predict_proba(np.array([[f[c] for c in cols_a]]))[0, 1])
            preds_b[f["item_id"]] = float(clf_b.predict_proba(np.array([[f[c] for c in cols_b]]))[0, 1])
            y[f["item_id"]] = f[label_key]
    items = sorted(y)
    aa = al.auROC([preds_a[i] for i in items], [y[i] for i in items])
    bb = al.auROC([preds_b[i] for i in items], [y[i] for i in items])
    rng = random.Random(seed)
    by_pair2 = {}
    for i in items:
        by_pair2.setdefault(":".join(i.split(":")[:2]), []).append(i)
    g2 = sorted(by_pair2)

    def stat():
        samp = []
        for _ in range(len(g2)):
            samp.extend(by_pair2[rng.choice(g2)])
        a = al.auROC([preds_a[i] for i in samp], [y[i] for i in samp])
        b = al.auROC([preds_b[i] for i in samp], [y[i] for i in samp])
        return (a - b) if (a is not None and b is not None) else None

    vals = sorted(v for v in (stat() for _ in range(BOOTSTRAP_N)) if v is not None)
    return {"model_a_cols": cols_a, "model_b_cols": cols_b,
            "oof_auroc_a": round(aa, 4) if aa is not None else None,
            "oof_auroc_b": round(bb, 4) if bb is not None else None,
            "diff": round((bb - aa), 4) if (aa is not None and bb is not None) else None,
            "ci": [round(vals[int(0.025 * len(vals))], 4),
                   round(vals[int(0.975 * len(vals)) - 1], 4)],
            "n": len(items)}


def leakage_audit(feats, strict_artifacts, n_items=30):
    """Rebuild inference messages for the first n_items x 2 conditions x 5 agents and
    verify prompts contain claim + E01 only; no gold/target/original answers/mirror
    evidence; no item_id. Also verify messages_sha256 matches the sent records."""
    sys.path.insert(0, str(HERE.parent.parent / "round4"))
    import round3_lib as pl  # noqa: F401
    from sp500_forecastability import pilot_llm_v10 as v10  # noqa: F401
    from ling_adapted_run import build_messages  # noqa: E402
    cohort = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    sel = json.loads((R3 / "selection_manifest.json").read_text(encoding="utf-8"))
    ev_by_id = {e["unique_id"]: e["evidence"] for e in sel["evidence"]}
    pairs = {p["pair_id"]: p for p in sel["pairs"] if p["pair_id"] in set(cohort["pairs"])}
    para = json.loads((R3 / "paraphrase_manifest.json").read_text(encoding="utf-8"))
    artifacts = {uid: {"para1": row["para1"], "para2": row["para2"]}
                 for uid, row in para.items() if row.get("usable")}
    natural = [pl.NaturalPair(
        pair_id=r["pair_id"], case_id=r["case_id"], page=r["page"], claim=r["claim"],
        supports_id=r["supports_id"], refutes_id=r["refutes_id"],
        supports_evidence=ev_by_id[r["supports_id"]], refutes_evidence=ev_by_id[r["refutes_id"]],
        character_ratio=float(r["character_ratio"]), token_jaccard=float(r["token_jaccard"]))
        for r in pairs.values()]
    distractors = {r["pair_id"]: pl.Distractor(
        distractor_id=r["distractor_id"], distractor_page=r["distractor_page"],
        evidence=ev_by_id[r["distractor_id"]]) for r in pairs.values()}
    comps = {c.item_id: c for c in pl.build_composites(natural, distractors, artifacts)}
    assigned = {r["item_id"]: r for r in strict_artifacts if r.get("success")}
    records = {}
    for fn in ("records_smoke.jsonl", "records.jsonl"):
        for r in load_jsonl(HERE / fn):
            if r.get("decision"):
                records[(r["item_id"], r["agent_index"], r["condition"])] = r
    checks = []
    bad = []
    skipped = 0
    for it in cohort["items"][:n_items]:
        comp = comps[it]
        a = assigned[it]
        evs = [ev_by_id[pairs[a["pair_id"]]["supports_id"]],
               ev_by_id[pairs[a["pair_id"]]["refutes_id"]]]
        for cond in ("ind_strict", "pm"):
            text = a["E_ind_strict"] if cond == "ind_strict" else a["E_pm"]
            for i in range(5):
                persona = v10.AGENT_PERSONAS[i][1]
                view = v10.EvidenceView(condition=cond, items=(("E01", text),))
                msgs = build_messages(comp, view, persona=persona, repair=False)
                sha = hashlib.sha256(
                    json.dumps(msgs, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
                rec = records.get((it, i, cond))
                if rec is None or not rec.get("decision"):
                    skipped += 1
                    continue
                rec_sha = rec.get("messages_sha256")
                user_content = msgs[-1]["content"]
                import json as _json
                payload = _json.loads(user_content.split("Task payload:\n", 1)[1])
                packet = payload.get("evidence_packet") or []
                packet_ok = (len(packet) == 1 and packet[0]["evidence_id"] == "E01"
                             and packet[0]["text"] == text)
                ok = (
                    rec_sha == sha
                    and packet_ok
                    and comp.claim in payload.get("question", "")
                    and it not in user_content
                    and "gold_label" not in user_content
                    and "consensus_wrong" not in user_content
                    and '"answer": "yes"' not in user_content
                    and '"answer": "no"' not in user_content
                )
                checks.append({"item_id": it, "agent_index": i, "condition": cond,
                               "sha_match": rec_sha == sha, "pass": ok})
                if not ok:
                    bad.append((it, i, cond, rec_sha == sha))
    n = len(checks)
    return {"n_checks": n, "n_skipped_unavailable": skipped,
            "pass": len(bad) == 0,
            "sha_match_rate": round(sum(1 for c in checks if c["sha_match"]) / n, 4),
            "failures": bad[:20]}


def main() -> int:
    meta = json.loads((HERE / "preoutcome_features_meta.json").read_text(encoding="utf-8"))
    actual_sha = hashlib.sha256((HERE / "preoutcome_features.jsonl").read_bytes()).hexdigest()
    assert actual_sha == meta["sha256"], "preoutcome features changed after freeze!"
    feats = load_jsonl(HERE / "preoutcome_features.jsonl")
    gold = {it["item_id"]: it["gold_label"] for it in json.loads(
        (R3 / "labels_ledger.json").read_text(encoding="utf-8"))["items"]}
    for f in feats:
        g = gold[f["item_id"]]
        f["gold_label"] = g
        f["gold_yes"] = g == "SUPPORTS"
        f["consensus_wrong"] = int((f["consensus"] == "yes") != f["gold_yes"])
    hc = [f for f in feats if f["agreement"] >= HC_THRESHOLD]
    hc2 = []
    for f in hc:
        row = dict(f)
        for src in ("S_natural", "S_ind_strict", "S_pm", "S_combined_natural_ind"):
            v = f.get(src)
            row[f"R_{src}"] = (-v) if v is not None else None
        row["RS_q"] = f.get("RS_q")
        hc2.append(row)

    # ---- flip rates & Delta_CE over (item, agent) pairs ----
    ours = {}
    for fn in ("records_smoke.jsonl", "records.jsonl"):
        for r in load_jsonl(HERE / fn):
            if r.get("decision"):
                ours[(r["item_id"], r["agent_index"], r["condition"])] = r["decision"]
    for r in load_jsonl(W2 / "records.jsonl"):
        if r.get("decision") and r["condition"] == "natural":
            ours[(r["item_id"], r["agent_index"], "natural")] = r["decision"]
    orig = {}
    for r in load_jsonl(R6 / "records.jsonl"):
        if r["condition"] == "original" and r.get("decision"):
            orig[(r["item_id"], r["agent_index"])] = r["decision"]["answer"]
    cohort_items = set(json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))["items"])
    flip = {c: flip_rate_and_ci(ours, orig, c, seed=BOOT_SEED + 0, item_filter=cohort_items)
            for c in CONDITIONS}
    dce = diff_ci(ours, orig, "ind_strict", "pm", seed=BOOT_SEED + 0, item_filter=cohort_items)
    dni = diff_ci(ours, orig, "ind_strict", "natural", seed=BOOT_SEED + 0, item_filter=cohort_items)
    dnp = diff_ci(ours, orig, "natural", "pm", seed=BOOT_SEED + 0, item_filter=cohort_items)

    # ---- AUROC / Risk@80 on HC ----
    auroc = {}
    for key in ("R_S_ind_strict", "R_S_natural", "R_S_pm", "RS_q", "R_S_combined_natural_ind"):
        rows = [f for f in hc2 if f.get(key) is not None]
        if not rows:
            auroc[key] = None
            continue
        auroc[key] = al.group_bootstrap(rows, key, seed=BOOT_SEED + 1)
    risk80 = {}
    for key in ("R_S_ind_strict", "R_S_natural", "R_S_pm", "RS_q", "R_S_combined_natural_ind"):
        rows = [f for f in hc2 if f.get(key) is not None]
        risk80[key] = al.risk_at_80_bootstrap(rows, key, seed=BOOT_SEED + 2) if rows else None

    # ---- paired increments ----
    paired = {
        "ind_minus_natural": al.paired_bootstrap_diff(hc2, "R_S_ind_strict", "R_S_natural", seed=BOOT_SEED + 3),
        "ind_minus_RS_q": al.paired_bootstrap_diff(hc2, "R_S_ind_strict", "RS_q", seed=BOOT_SEED + 3),
        "ind_minus_pm": al.paired_bootstrap_diff(hc2, "R_S_ind_strict", "R_S_pm", seed=BOOT_SEED + 3),
        "combined_minus_natural": al.paired_bootstrap_diff(hc2, "R_S_combined_natural_ind", "R_S_natural", seed=BOOT_SEED + 3),
    }
    rho = rho_ci(feats, "S_natural", "S_ind_strict", seed=BOOT_SEED + 4)

    # ---- OOF logistic increments (diagnostic) ----
    oof = {
        "ind_over_natural": oof_logistic_incr(hc2, ["S_natural"], ["S_natural", "S_ind_strict"],
                                              "consensus_wrong", seed=BOOT_SEED + 5),
        "ind_over_RS_q": oof_logistic_incr(hc2, ["RS_q"], ["RS_q", "S_ind_strict"],
                                           "consensus_wrong", seed=BOOT_SEED + 5),
    }

    # ---- gates ----
    gates = {
        "G3_delta_CE_gt_0": {"point": dce["diff"], "ci_lb": dce["ci"][0],
                             "pass": dce["diff"] > 0 and dce["ci"][0] > 0},
        "G4_placebo_le_0.30": {"rate": flip["pm"]["rate"], "pass": flip["pm"]["rate"] <= 0.30},
        "G5_diag_|ind-natural|": {"abs_diff": round(abs(flip["ind_strict"]["rate"] - flip["natural"]["rate"]), 4)},
    }

    # ---- leakage audit ----
    strict_artifacts = load_jsonl(HERE / "e_ind_strict_artifacts.jsonl")
    leak = leakage_audit(feats, strict_artifacts, n_items=30)

    results = {
        "protocol": "cs-paper-ind-ce-strict-20260915-round7-w2b",
        "cohort": {"n_items_total": len(feats), "n_pairs": len({f["pair_id"] for f in feats}),
                   "hc": {"n": len(hc), "n_wrong": sum(1 for f in hc if f["consensus_wrong"]),
                          "wrong_rate": round(sum(1 for f in hc if f["consensus_wrong"]) / max(1, len(hc)), 4)}},
        "flip_rates": flip,
        "delta_CE": dce, "delta_ind_natural": dni, "delta_natural_pm": dnp,
        "auroc": auroc, "risk_at_80": risk80, "paired": paired, "rho": rho, "oof": oof,
        "gates": gates, "leakage_audit": leak,
        "seeds": {"bootstrap": BOOT_SEED, "n": BOOTSTRAP_N},
    }
    write_json(HERE / "analysis" / "strict_results.json", results)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
