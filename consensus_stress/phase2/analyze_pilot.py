"""Merge labels AFTER preoutcome features are frozen; compute Gate 2 metrics."""
from __future__ import annotations
import json, random, sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_lib as pl

ROOT = Path(__file__).resolve().parent
HC_THRESHOLD = 0.8
BOOTSTRAP_SEED = 20_260_913
BOOTSTRAP_N = 1000
PERM_N = 500


def load():
    feats = [json.loads(l) for l in (ROOT / "preoutcome_features.jsonl").read_text().splitlines() if l]
    ledger = json.loads((ROOT / "labels_ledger.json").read_text())
    gold = {it["cqid"]: it["gold_label"] for it in ledger["items"]}
    for f in feats:
        f["gold"] = gold[f["cqid"]]
        f["consensus_wrong"] = int((f["consensus"] == "yes") != (f["gold"] == "yes"))
    return feats


def auROC(scores, labels):
    pos = sum(1 for l in labels if l == 1)
    neg = sum(1 for l in labels if l == 0)
    if pos == 0 or neg == 0:
        return None
    return float(roc_auc_score(labels, scores))


def bootstrap_auroc(feats, score_key, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(score_key) is not None]
    if not rows:
        return None
    obs = auROC([f[score_key] for f in rows], [f["consensus_wrong"] for f in rows])
    if obs is None:
        return None
    vals = []
    for _ in range(n):
        sample = [rows[i] for i in (rng.randrange(len(rows)) for _ in range(len(rows)))]
        a = auROC([f[score_key] for f in sample], [f["consensus_wrong"] for f in sample])
        if a is not None:
            vals.append(a)
    vals = sorted(vals)
    lo = vals[int(0.025 * len(vals))] if vals else None
    hi = vals[int(0.975 * len(vals)) - 1] if vals else None
    return {"auroc": obs, "ci": [lo, hi], "n": len(rows)}


def paired_bootstrap_diff(feats, key_a, key_b, n=BOOTSTRAP_N, seed=BOOTSTRAP_SEED + 1):
    rng = random.Random(seed)
    rows = [f for f in feats if f.get(key_a) is not None and f.get(key_b) is not None]
    if not rows:
        return None
    labels = [f["consensus_wrong"] for f in rows]
    obs = auROC([f[key_a] for f in rows], labels) - auROC([f[key_b] for f in rows], labels)
    vals = []
    for _ in range(n):
        idx = [rng.randrange(len(rows)) for _ in range(len(rows))]
        a = auROC([rows[i][key_a] for i in idx], [labels[i] for i in idx])
        b = auROC([rows[i][key_b] for i in idx], [labels[i] for i in idx])
        if a is not None and b is not None:
            vals.append(a - b)
    vals = sorted(vals)
    return {"diff": obs, "ci": [vals[int(0.025*len(vals))], vals[int(0.975*len(vals))-1]], "n": len(rows)}


def permutation_control(feats, n=PERM_N, seed=BOOTSTRAP_SEED + 2):
    """Swap preserve/flip roles of paraphrase and reverse per question."""
    rng = random.Random(seed)
    rows = [f for f in feats if f["bf_paraphrase"] is not None and f["bf_reverse"] is not None]
    labels = [f["consensus_wrong"] for f in rows]
    obs = auROC([f["bf_q"] for f in rows], labels)
    perms = []
    for _ in range(n):
        pseudo = []
        for f in rows:
            if rng.random() < 0.5:
                pseudo.append(0.5 * f["bf_paraphrase"] + 0.5 * (1.0 - f["bf_reverse"]))
            else:
                pseudo.append(0.5 * (1.0 - f["bf_paraphrase"]) + 0.5 * f["bf_reverse"])
        a = auROC(pseudo, labels)
        if a is not None:
            perms.append(a)
    perms = sorted(perms)
    return {"obs_auroc": obs, "perm_mean": float(np.mean(perms)), "perm_95pct": perms[int(0.95*len(perms))],
            "perm_ci": [perms[int(0.025*len(perms))], perms[int(0.975*len(perms))-1]], "n": len(rows)}


def agent_randomization_control(feats, n=PERM_N, seed=BOOTSTRAP_SEED + 3):
    """Randomly permute agents' per-condition answers before computing faithfulness."""
    rng = random.Random(seed)
    rows = [f for f in feats if f["bf_q"] is not None]
    labels = [f["consensus_wrong"] for f in rows]
    obs = auROC([f["bf_q"] for f in rows], labels)
    perms = []
    for _ in range(n):
        pseudo = []
        for f in rows:
            bfp = [f["_agent_bf_para"][i] for i in sorted(f["_agent_bf_para"])]
            bfr = [f["_agent_bf_rev"][i] for i in sorted(f["_agent_bf_rev"])]
            rng.shuffle(bfp); rng.shuffle(bfr)
            pseudo.append(0.5 * np.mean(bfp) + 0.5 * np.mean(bfr))
        a = auROC(pseudo, labels)
        if a is not None:
            perms.append(a)
    perms = sorted(perms)
    return {"obs_auroc": obs, "perm_mean": float(np.mean(perms)), "perm_95pct": perms[int(0.95*len(perms))], "n": len(rows)}


def main():
    feats = load()
    # agent-level per-condition faithfulness for C3
    recs = [json.loads(l) for l in (ROOT / "records.jsonl").read_text().splitlines() if l]
    by_q = {}
    for r in recs:
        by_q.setdefault(r["cqid"], {}).setdefault(r["agent_index"], {})[r["condition"]] = r["decision"]
    for f in feats:
        q = by_q[f["cqid"]]
        f["_agent_bf_para"] = {}
        f["_agent_bf_rev"] = {}
        for i in range(pl.N_AGENTS):
            y0 = q.get(i, {}).get("original", {}).get("answer")
            p = q.get(i, {}).get("paraphrase", {}).get("answer")
            rv = q.get(i, {}).get("reverse", {}).get("answer")
            f["_agent_bf_para"][str(i)] = int(p == y0) if (y0 and p) else None
            f["_agent_bf_rev"][str(i)] = int(rv != y0) if (y0 and rv) else None

    hc = [f for f in feats if f["agreement"] >= HC_THRESHOLD]
    wrong = [f for f in hc if f["consensus_wrong"]]
    print(f"total={len(feats)} high_consensus={len(hc)} wrong_hc={len(wrong)} rate={len(wrong)/max(1,len(hc)):.3f}")

    # E1 agent-level expected-response accuracy
    n_par, ok_par = 0, 0
    n_rev, ok_rev = 0, 0
    for f in feats:
        for i in sorted(f["_agent_bf_para"]):
            v = f["_agent_bf_para"][i]
            if v is not None:
                n_par += 1; ok_par += v
        for i in sorted(f["_agent_bf_rev"]):
            v = f["_agent_bf_rev"][i]
            if v is not None:
                n_rev += 1; ok_rev += v
    e1 = {
        "paraphrase_agent_accuracy": ok_par / max(1, n_par),
        "reverse_agent_accuracy": ok_rev / max(1, n_rev),
        "overall_agent_accuracy": (ok_par + ok_rev) / max(1, n_par + n_rev),
        "n_pairs": n_par + n_rev,
    }
    print("E1:", json.dumps(e1))

    # E2 consensus-level BF
    e2 = {
        "bf_mean_correct": float(np.mean([f["bf_q"] for f in hc if not f["consensus_wrong"] and f["bf_q"] is not None])),
        "bf_mean_wrong": float(np.mean([f["bf_q"] for f in hc if f["consensus_wrong"] and f["bf_q"] is not None])),
        "bf_paraphrase_mean": float(np.mean([f["bf_paraphrase"] for f in hc if f["bf_paraphrase"] is not None])),
        "bf_reverse_mean": float(np.mean([f["bf_reverse"] for f in hc if f["bf_reverse"] is not None])),
        "sub_flip_rate_hc": float(np.mean([f["sub_flip_rate"] for f in hc])),
        "rem_flip_rate_hc": float(np.mean([f["rem_flip_rate"] for f in hc])),
    }
    print("E2:", json.dumps(e2))

    # E3 + S1 AUROCs (high consensus)
    e3 = bootstrap_auroc(hc, "bf_q")
    print("E3 BF_q:", json.dumps(e3))
    scores = {}
    for key in ["bf_paraphrase", "bf_reverse", "R_PI", "mean_confidence", "agreement", "sub_flip_rate", "rem_flip_rate"]:
        scores[key] = bootstrap_auroc(hc, key)
        print("AUROC", key, json.dumps(scores[key]))

    # S2 paired diffs vs bf_q (high consensus)
    diffs = {}
    for key in ["R_PI", "mean_confidence", "agreement"]:
        diffs[key] = paired_bootstrap_diff(hc, "bf_q", key)
        print("diff bf_q -", key, json.dumps(diffs[key]))

    # S3 label subgroups
    sub = {}
    for lab in ("yes", "no"):
        hcl = [f for f in hc if f["gold"] == lab]
        sub[lab] = bootstrap_auroc(hcl, "bf_q")
        print("label", lab, json.dumps(sub[lab]))

    # S4 mean BF difference CI (bootstrap on high consensus)
    rng = random.Random(BOOTSTRAP_SEED + 4)
    hc_bf = [(f["bf_q"], f["consensus_wrong"]) for f in hc if f["bf_q"] is not None]
    obs_diff = np.mean([b for b, w in hc_bf if w]) - np.mean([b for b, w in hc_bf if not w])
    vals = []
    for _ in range(BOOTSTRAP_N):
        s = [hc_bf[i] for i in (rng.randrange(len(hc_bf)) for _ in range(len(hc_bf)))]
        w = [b for b, x in s if x]; c = [b for b, x in s if not x]
        if w and c:
            vals.append(np.mean(w) - np.mean(c))
    vals = sorted(vals)
    s4 = {"diff_wrong_minus_correct": float(obs_diff), "ci": [float(vals[int(0.025*len(vals))]), float(vals[int(0.975*len(vals))-1])]}

    # controls
    # consensus-level paraphrase flip rate (placebo): majority under original vs paraphrase
    cf_n = 0; cf_flips = 0
    for f in feats:
        q = by_q[f["cqid"]]
        orig_maj = Counter(q.get(i, {}).get("original", {}).get("answer") for i in range(pl.N_AGENTS)
                           if q.get(i, {}).get("original"))
        para_maj = Counter(q.get(i, {}).get("paraphrase", {}).get("answer") for i in range(pl.N_AGENTS)
                           if q.get(i, {}).get("paraphrase"))
        if not orig_maj or not para_maj:
            continue
        cf_n += 1
        if orig_maj.most_common(1)[0][0] != para_maj.most_common(1)[0][0]:
            cf_flips += 1
    placebo = {
        "paraphrase_agent_flip_rate": 1.0 - e1["paraphrase_agent_accuracy"],
        "paraphrase_consensus_flip_rate": cf_flips / max(1, cf_n),
        "n_questions": cf_n,
    }
    perm = permutation_control(hc)
    print("permutation:", json.dumps(perm))
    arand = agent_randomization_control(hc)
    print("agent_rand:", json.dumps(arand))

    # spearman reducibility checks
    sp_agr = spearmanr([f["bf_q"] for f in hc if f["bf_q"] is not None],
                       [f["agreement"] for f in hc if f["bf_q"] is not None])[0]
    sp_conf = spearmanr([f["bf_q"] for f in hc if f["bf_q"] is not None],
                        [f["mean_confidence"] for f in hc if f["bf_q"] is not None])[0]
    # AUROC BF_q conditioned on agreement==0.8
    exact = [f for f in hc if abs(f["agreement"] - 0.8) < 1e-9]
    cond80 = bootstrap_auroc(exact, "bf_q") if len(exact) >= 6 else None
    print("spearman bf-agreement:", sp_agr, "bf-confidence:", sp_conf)
    print("cond80:", json.dumps(cond80))

    out = {
        "protocol": pl.PROTOCOL_VERSION,
        "n_total": len(feats), "n_high_consensus": len(hc), "n_wrong_hc": len(wrong),
        "wrong_hc_rate": len(wrong) / max(1, len(hc)),
        "e1_agent_level": e1,
        "e2_consensus_bf": e2,
        "e3_bf_q_auroc": e3,
        "score_aurocs": scores,
        "paired_diffs_vs_bfq": diffs,
        "label_subgroups": sub,
        "s4_bf_diff": s4,
        "placebo": placebo,
        "permutation_control": perm,
        "agent_randomization_control": arand,
        "spearman_bf_agreement": float(sp_agr),
        "spearman_bf_confidence": float(sp_conf),
        "bfq_auroc_at_agreement_0_8": cond80,
    }
    pl.write_json(ROOT / "analysis" / "analysis.json", out)
    print("wrote analysis.json")

if __name__ == "__main__":
    main()
