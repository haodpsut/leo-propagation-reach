"""MOT bo quy tac doc CSV, dung chung cho analysis/make_tables.py va figures/make_figures.py.

Review vong 1 (12/09/2026) chi ra: luat "thang = >=7/10 seed" co ty le duong tinh gia 34,4%/o
duoi gia thuyet khong (hai phia), va bai khong in mot p-value, khoang tin cay hay co hieu ung
nao. Module nay them, cho moi o:
  * sign test hai phia tren cap seed (p_sign)
  * Wilcoxon signed-rank hai phia tren e_heat - e_walk (p_wilcoxon)
  * hieu trung binh cap seed va khoang tin cay 95% bootstrap (diff, ci_lo, ci_hi)
  * hieu chinh Holm tren cac o cua cung mot thuoc (p_holm), do make_figures ap sau
va giu nguyen phan quyet theo luat da khai (verdict) de doi chieu.

Review vong 2 (12/09/2026, Major) chi ra luat 6 KHONG CO LUC: Wilcoxon chinh xac co san p toi
thieu 2/2^n, nen voi |S| <= 9 khong ket qua nao qua duoc Holm tren 24 o (0.05/24 = 0.00208).
Module nay them:
  * wilcoxon_min_p(n) va power_wilcoxon(...) : dac tinh van hanh cua luat 6, mo phong
  * pooled_stats(...)                        : MOT phep thu cho moi (task, shell), gop 4 nhanh t
                                               theo seed, Holm tren 6 -> thiet ke co luc
  * summarise(key="aurc") dung const_aurc    : san far-node tung duoc tinh bang hang so cua MAE
"""
import csv
import glob
import json
import math
import os

import numpy as np

FLOOR_GAIN, WIN_SEEDS = 0.05, 7
SHELLS = ["s264", "s1584", "s3168", "s4400"]
NN = {"s264": 264, "s1584": 1584, "s3168": 3168, "s4400": 4400}
OPS = ["gcn", "heat", "qw", "ppr", "sgc"]


def load(paths):
    rows = []
    for pat in paths:
        for f in sorted(glob.glob(pat)):
            for r in csv.DictReader(open(f)):
                for k in ("mae", "aurc", "const_mae", "t_init", "train_mae"):
                    r[k] = float(r[k])
                r["seed"] = int(r["seed"])
                r["const_aurc"] = float(r["const_aurc"]) if r.get("const_aurc") not in (None, "") else float("nan")
                r["seam"] = r.get("seam") or "keep"; r["dtype"] = r.get("dtype") or "float32"
                r["ppr_alpha"] = float(r.get("ppr_alpha") or 0.05); r["sgc_k"] = int(r.get("sgc_k") or 8); r["ppr_k"] = int(r.get("ppr_k") or 20)
                th = json.loads(r["loss_thirds"])
                finite = r["mae"] == r["mae"] and r["train_mae"] == r["train_mae"]
                rising = any(th[i + 1] > th[i] * 1.01 for i in range(len(th) - 1))
                r["pathology"] = (not finite) or rising
                r["plateau"] = (r["valid"] == "False") and not r["pathology"]
                r["arm"] = "%s/t0=%g" % (r["t_param"], r["t_init"])
                r["cfg"] = "h%sl%s" % (r["hidden"], r["n_layers"])
                r["t_learned"] = json.loads(r["t_learned"])
                r["escaped"] = r["mae"] < 0.9 * r["const_mae"]
                rows.append(r)
    return rows


def cell(rows, task, shell, arm, cfg, epochs, include_pathology=False):
    out = {}
    for r in rows:
        if (r["task"], r["shell"], r["arm"], r["cfg"], r["epochs"]) == (task, shell, arm, cfg, str(epochs)):
            if include_pathology or not r["pathology"]:
                out.setdefault(r["op"], {})[r["seed"]] = r
    return out


def cell_fixed_ops(rows, task, shell, cfg, epochs):
    """ppr/sgc khong co nhanh t: lay moi hang cua op do bat ke arm."""
    out = {}
    for r in rows:
        if (r["task"], r["shell"], r["cfg"], r["epochs"]) == (task, shell, cfg, str(epochs)) and r["op"] in ("ppr", "sgc") and not r["pathology"]:
            out.setdefault(r["op"], {})[r["seed"]] = r
    return out


def sign_test(k, n):
    """p hai phia cua sign test: P(X >= k) * 2 voi X ~ Bin(n, 1/2), k = so thang cua ben thang."""
    if n == 0:
        return float("nan")
    k = max(k, n - k)
    p = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * p)


def wilcoxon(d):
    """Wilcoxon signed-rank, hai phia, phan phoi CHINH XAC bang liet ke 2^n dau (n <= 10)."""
    d = np.asarray([x for x in d if x != 0.0], dtype=float)
    n = len(d)
    if n == 0:
        return float("nan")
    absd = np.abs(d)
    order = np.argsort(absd, kind="mergesort")
    ranks = np.empty(n); ranks[order] = np.arange(1, n + 1)
    for v in np.unique(absd):                       # rank trung binh cho tie
        idx = absd == v
        ranks[idx] = ranks[idx].mean()
    wpos = ranks[d > 0].sum()
    dist = []
    for m in range(2 ** n):
        dist.append(sum(ranks[i] for i in range(n) if (m >> i) & 1))
    dist = np.array(dist)
    p_lo = (dist <= wpos + 1e-9).mean(); p_hi = (dist >= wpos - 1e-9).mean()
    return float(min(1.0, 2 * min(p_lo, p_hi)))


def paired_stats(c, key="mae", a="heat", b="qw", seed=0, nboot=2000):
    """Thong ke cap seed giua hai toan tu a, b trong mot o."""
    common = sorted(set(c.get(a, {})) & set(c.get(b, {})))
    if not common:
        return None
    ea = np.array([c[a][s][key] for s in common]); eb = np.array([c[b][s][key] for s in common])
    d = ea - eb                                  # < 0: a tot hon
    n = len(d)
    wins_a = int((d < 0).sum()); wins_b = int((d > 0).sum())
    rng = np.random.default_rng(seed)
    boots = np.array([rng.choice(d, n, replace=True).mean() for _ in range(nboot)])
    return {"n": n, "wins_a": wins_a, "wins_b": wins_b, "diff": float(d.mean()),
            "ci_lo": float(np.percentile(boots, 2.5)), "ci_hi": float(np.percentile(boots, 97.5)),
            "p_sign": sign_test(max(wins_a, wins_b), wins_a + wins_b),
            "p_wilcoxon": wilcoxon(d), "mean_a": float(ea.mean()), "mean_b": float(eb.mean())}


def wilcoxon_min_p(n):
    """p hai phia nho nhat ma Wilcoxon chinh xac co the tra ve voi n cap khac 0."""
    return float("nan") if n <= 0 else min(1.0, 2.0 / 2 ** n)


def _wplus_null(n):
    ranks = np.arange(1, n + 1)
    dist = np.zeros(2 ** n)
    for m in range(2 ** n):
        dist[m] = sum(ranks[i] for i in range(n) if (m >> i) & 1)
    return dist


def power_wilcoxon(dbar, sd, n, alphas=(0.05, 0.05 / 24), nsim=2000, seed=0):
    """Luc cua Wilcoxon chinh xac hai phia khi d_i ~ N(dbar, sd), n cap, tai cac muc alpha.

    Mo phong (khong tie vi phan phoi lien tuc). alpha = 0.05/24 la buoc khat nhat cua Holm
    tren 24 o, tuc la LUC TREN cua o co p nho nhat; cac o khac con thap hon."""
    if n <= 1 or not (sd > 0):
        return {a: float("nan") for a in alphas}
    rng = np.random.default_rng(seed)
    D = rng.normal(dbar, sd, (nsim, n))
    ranks = np.argsort(np.argsort(np.abs(D), axis=1), axis=1) + 1
    wpos = (ranks * (D > 0)).sum(1)
    dist = np.sort(_wplus_null(n)); m = len(dist)
    p_lo = np.searchsorted(dist, wpos, side="right") / m
    p_hi = 1 - np.searchsorted(dist, wpos, side="left") / m
    p = np.minimum(1.0, 2 * np.minimum(p_lo, p_hi))
    return {a: float((p < a).mean()) for a in alphas}


def mde_wilcoxon(sd, n, alpha, target=0.8, nsim=1000, seed=0):
    """Hieu ung nho nhat |d| ma Wilcoxon chinh xac dat luc `target` tai `alpha`, sd va n cho truoc.
    (Luc hau nghiem tai hieu ung quan sat la ham cua p, khong dung; MDE la dac tinh cua THIET KE.)"""
    if n <= 1 or not (sd > 0) or wilcoxon_min_p(n) >= alpha:
        return float("nan")
    lo, hi = 0.0, 10 * sd
    for _ in range(25):
        mid = (lo + hi) / 2
        if power_wilcoxon(-mid, sd, n, (alpha,), nsim, seed)[alpha] >= target:
            hi = mid
        else:
            lo = mid
    return hi


def pooled_stats(rows, task, shell, arms, cfg, epochs, key="mae", a="heat", b="qw", seed=0, nboot=2000):
    """MOT phep thu cho (task, shell): voi moi seed, hieu e_a - e_b trung binh tren cac nhanh t
    ma seed do hop le o CA HAI toan tu; roi sign test / Wilcoxon / bootstrap tren 10 gia tri."""
    per_seed = {}
    for arm in arms:
        c = cell(rows, task, shell, arm, cfg, epochs)
        for s_ in sorted(set(c.get(a, {})) & set(c.get(b, {}))):
            per_seed.setdefault(s_, []).append(c[a][s_][key] - c[b][s_][key])
    if not per_seed:
        return None
    d = np.array([np.mean(v) for _, v in sorted(per_seed.items())])
    n_arms = [len(v) for _, v in sorted(per_seed.items())]
    n = len(d); wins_a = int((d < 0).sum()); wins_b = int((d > 0).sum())
    rng = np.random.default_rng(seed)
    boots = np.array([rng.choice(d, n, replace=True).mean() for _ in range(nboot)])
    return {"n": n, "wins_a": wins_a, "wins_b": wins_b, "diff": float(d.mean()), "sd": float(d.std(ddof=1)) if n > 1 else 0.0,
            "ci_lo": float(np.percentile(boots, 2.5)), "ci_hi": float(np.percentile(boots, 97.5)),
            "p_sign": sign_test(max(wins_a, wins_b), wins_a + wins_b), "p_wilcoxon": wilcoxon(d),
            "arms_per_seed_min": min(n_arms), "arms_per_seed_max": max(n_arms)}


def holm(pvals):
    """Hieu chinh Holm; tra ve p da hieu chinh theo cung thu tu."""
    idx = [i for i, p in sorted(enumerate(pvals), key=lambda x: (x[1] != x[1], x[1]))]
    m = sum(1 for p in pvals if p == p)
    adj = [float("nan")] * len(pvals); running = 0.0
    for rank, i in enumerate(idx):
        p = pvals[i]
        if p != p:
            continue
        running = max(running, (m - rank) * p)
        adj[i] = min(1.0, running)
    return adj


def summarise(c, key="mae", floor_gain=FLOOR_GAIN, win_seeds=WIN_SEEDS):
    st = {op: (float(np.mean([r[key] for r in d.values()])),
               float(np.std([r[key] for r in d.values()], ddof=1)) if len(d) > 1 else 0.0, len(d))
          for op, d in c.items()}
    ck = "const_aurc" if key == "aurc" else "const_mae"     # review vong 2: san far-node theo hang so far-node
    cm = float(np.mean([r[ck] for d in c.values() for r in d.values()])) if c else float("nan")
    best = min(v[0] for v in st.values()) if st else float("nan")
    gain = (cm - best) / cm if c else float("nan")
    vd = "n/a"; leader = "n/a"
    if "heat" in c and "qw" in c:
        ps = paired_stats(c, key)
        leader = "heat" if ps["mean_a"] < ps["mean_b"] else "walk"
        if gain < floor_gain:
            vd = "floor"
        elif ps["n"] < win_seeds:
            vd = "n<%d" % win_seeds
        elif ps["wins_b"] >= win_seeds and ps["mean_b"] < ps["mean_a"]:
            vd = "walk"
        elif ps["wins_a"] >= win_seeds and ps["mean_a"] < ps["mean_b"]:
            vd = "heat"
        else:
            vd = "tie"
    return st, cm, gain, vd, leader
