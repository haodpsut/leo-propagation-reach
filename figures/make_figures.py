"""Sinh MOI hinh va MOI macro so cua bai tu results/grid*/scale_*.csv.

⛔ LUAT MOT NGUON: khong con so nao duoc go tay vao paper/. Van xuoi doc so qua macro trong
figures/out/numbers.tex; tep do sinh ra o day. Chay lai thi nghiem = cap nhat het.

Quy tac doc CSV lap lai y het analysis/make_tables.py (mot bo quy tac, hai dau ra):
  * benh ly = NaN hoac loss tang >1% giua cac phan ba  -> loai, DEM
  * plateau = flat tai san hang so                      -> giu, dem rieng
  * o xep hang duoc  <=> toan tu tot nhat cai thien >= FLOOR_GAIN so voi hang so
  * thang  <=> trung binh thap hon VA >= WIN_SEEDS/10 seed
Luoi:  grid12/  (200 epoch; h16l3 = ma phat hanh, h32l4 = cau hinh bai TNSE cu)
       grid3/   (1000 epoch, h32l4, s264-s3168)  -- neu chua co thi hinh/macro lien quan bi bo qua
Chay:  python3 figures/make_figures.py
"""
import csv
import glob
import io
import json
import os
import re
import sys

import numpy as np
import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "code", "results")
OUTD = os.path.join(HERE, "out")
os.makedirs(OUTD, exist_ok=True)

mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif", "font.size": 9,
    "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 8,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "xtick.direction": "in", "ytick.direction": "in",
    "lines.linewidth": 1.1, "lines.markersize": 4.0, "legend.frameon": False,
    "figure.dpi": 130, "pdf.fonttype": 42, "ps.fonttype": 42,
})
C = {"gcn": "#555555", "heat": "#D55E00", "qw": "#0072B2", "const": "#009E73"}
MK = {"gcn": "s", "heat": "o", "qw": "^"}
LS = {"gcn": ":", "heat": "-", "qw": "--"}
LBL = {"gcn": "GCN (local)", "heat": r"heat $e^{-tL}$", "qw": r"walk $|e^{-itL}|^2$"}
W_WIDE = 4.60          # elsarticle preprint, mot cot
W_HALF = 2.99
FLOOR_GAIN, WIN_SEEDS = 0.05, 7
SHELLS = ["s264", "s1584", "s3168", "s4400"]
NN = {"s264": 264, "s1584": 1584, "s3168": 3168, "s4400": 4400}
NUM = {}


def M(name, value):
    key = re.sub(r"[^A-Za-z]", "", name)
    assert key not in NUM or NUM[key] == value, "macro %s bi dat hai lan khac gia tri" % key
    NUM[key] = value
    return value


def save(fig, name, target_w=W_WIDE):
    path_pdf = os.path.join(OUTD, "%s.pdf" % name)
    got = None
    for _ in range(6):
        fig.savefig(path_pdf, bbox_inches="tight")
        blob = open(path_pdf, "rb").read()
        mm = re.findall(rb"/MediaBox\s*\[([^\]]*)\]", blob)
        if not mm:
            break
        x0, y0, x1, y1 = [float(v) for v in mm[0].split()]
        got = (x1 - x0) / 72.0
        if abs(got - target_w) < 0.005:
            break
        w, h = fig.get_size_inches()
        fig.set_size_inches(w + (target_w - got), h)
    fig.savefig(os.path.join(OUTD, "%s.png" % name), bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("     %-18s %.2f in" % (name, got or -1))


# ---------------------------------------------------------------- doc CSV, cung quy tac
def load_grid(pattern):
    rows = []
    for f in sorted(glob.glob(os.path.join(RES, pattern))):
        for r in csv.DictReader(open(f)):
            r["mae"] = float(r["mae"]); r["const_mae"] = float(r["const_mae"])
            r["seed"] = int(r["seed"]); r["t_init"] = float(r["t_init"])
            th = json.loads(r["loss_thirds"])
            finite = r["mae"] == r["mae"]
            rising = any(th[i + 1] > th[i] * 1.01 for i in range(len(th) - 1))
            r["pathology"] = (not finite) or rising
            r["arm"] = "%s/t0=%g" % (r["t_param"], r["t_init"])
            r["cfg"] = "h%sl%s" % (r["hidden"], r["n_layers"])
            r["t_learned"] = json.loads(r["t_learned"])
            rows.append(r)
    return rows


def cell(rows, task, shell, arm, cfg, epochs):
    out = {}
    for r in rows:
        if (r["task"], r["shell"], r["arm"], r["cfg"], r["epochs"]) == (task, shell, arm, cfg, str(epochs)) \
                and not r["pathology"]:
            out.setdefault(r["op"], {})[r["seed"]] = r
    return out


def summarise(c):
    """-> {op: (mean, std, n)}, gain cua op tot nhat so voi hang so, verdict heat/qw."""
    st = {op: (np.mean([r["mae"] for r in d.values()]), np.std([r["mae"] for r in d.values()], ddof=1) if len(d) > 1 else 0.0, len(d))
          for op, d in c.items()}
    cm = np.mean([r["const_mae"] for d in c.values() for r in d.values()]) if c else np.nan
    best = min(v[0] for v in st.values()) if st else np.nan
    gain = (cm - best) / cm if c else np.nan
    vd = "n/a"
    if "heat" in c and "qw" in c:
        common = sorted(set(c["heat"]) & set(c["qw"]))
        hw = sum(c["heat"][s]["mae"] < c["qw"][s]["mae"] for s in common)
        qw = sum(c["qw"][s]["mae"] < c["heat"][s]["mae"] for s in common)
        if gain < FLOOR_GAIN:
            vd = "floor"
        elif len(common) >= WIN_SEEDS and qw >= WIN_SEEDS and st["qw"][0] < st["heat"][0]:
            vd = "qw"
        elif len(common) >= WIN_SEEDS and hw >= WIN_SEEDS and st["heat"][0] < st["qw"][0]:
            vd = "heat"
        else:
            vd = "tie"
    return st, cm, gain, vd


# ================================================================ LUOI 1-2
g12 = load_grid("grid12/scale_*.csv")
print("  grid12: %d hang, %d benh ly" % (len(g12), sum(r["pathology"] for r in g12)))
M("numGridTwelveRuns", len(g12))
M("numGridTwelvePathology", sum(r["pathology"] for r in g12))
ARMS = ["relu/t0=0.5", "relu/t0=2", "softplus/t0=0.5", "softplus/t0=2"]
CFGS = ["h16l3", "h32l4"]
CFGNAME = {"h16l3": "Released", "h32l4": "Submitted"}   # ten macro chi duoc chu cai

# --- Hinh 1: cai thien so voi hang so theo quy mo, moi cfg mot panel, moi nhanh mot duong (tac vu hops)
fig, axes = plt.subplots(1, 2, figsize=(W_WIDE, 2.3), sharey=True)
n_floor = n_rank = 0
for ax, cfg in zip(axes, CFGS):
    for ai, arm in enumerate(ARMS):
        ys = []
        for sh in SHELLS:
            st, cm, gain, vd = summarise(cell(g12, "hops", sh, arm, cfg, 200))
            ys.append(100 * gain)
            if sh != "s264":
                n_floor += vd == "floor"; n_rank += vd != "floor"
        ax.plot([NN[s] for s in SHELLS], ys, marker="osd^"[ai], ls=["-", "--", "-", "--"][ai],
                color=["#D55E00", "#D55E00", "#0072B2", "#0072B2"][ai], label=arm.replace("/t0=", ", $t_0$="))
    ax.axhline(100 * FLOOR_GAIN, color="#009E73", lw=0.8, ls=":")
    ax.set_xscale("log"); ax.set_xticks([264, 1584, 3168, 4400]); ax.set_xticklabels(["264", "1584", "3168", "4400"], rotation=30); ax.minorticks_off()
    ax.set_xlabel("satellites in shell")
    ax.set_title({"h16l3": "released: width 16, 3 layers", "h32l4": "submitted: width 32, 4 layers"}[cfg], fontsize=8)
axes[0].set_ylabel("best-operator gain over constant (%)")
axes[0].legend(loc="upper right")
save(fig, "fig1-floor")
M("numFloorCellsLarge", n_floor); M("numRankableCellsLarge", n_rank)   # o >=1584, hops, 2 cfg x 4 arm x 3 shell = 24

# gain o s264 theo cfg (min..max qua 4 nhanh, hops) va o >=1584 (max)
for cfg in CFGS:
    g264 = [summarise(cell(g12, "hops", "s264", a, cfg, 200))[2] for a in ARMS]
    gbig = [summarise(cell(g12, t, s, a, cfg, 200))[2] for a in ARMS for s in SHELLS[1:] for t in ("hops", "delay")]
    M("numGainSTwoSixFourMin" + CFGNAME[cfg], round(100 * min(g264), 1))
    M("numGainSTwoSixFourMax" + CFGNAME[cfg], round(100 * max(g264), 1))
    M("numGainLargeMax" + CFGNAME[cfg], round(100 * max(gbig), 1))

# --- Hinh 2: s264, thu hang heat vs qw theo nhanh (h32l4, hops): strip theo seed
fig, axes = plt.subplots(1, 4, figsize=(W_WIDE, 2.2), sharey=True)
verd = []
for ax, arm in zip(axes, ARMS):
    c = cell(g12, "hops", "s264", arm, "h32l4", 200)
    st, cm, gain, vd = summarise(c); verd.append(vd)
    for xi, op in enumerate(["gcn", "heat", "qw"]):
        ys = [r["mae"] for r in c.get(op, {}).values()]
        ax.scatter(np.full(len(ys), xi) + np.random.default_rng(0).uniform(-0.12, 0.12, len(ys)), ys,
                   s=12, color=C[op], marker=MK[op], alpha=0.8)
        ax.hlines(np.mean(ys), xi - 0.25, xi + 0.25, color=C[op], lw=1.4)
    ax.axhline(cm, color=C["const"], lw=0.8, ls=":")
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["GCN", "heat", "walk"])
    ax.set_title(arm.replace("/t0=", "\n$t_0$=") + "\nverdict: " + vd, fontsize=8)
axes[0].set_ylabel("MAE, 264 satellites")
save(fig, "fig2-s264-arms")
M("numSTwoSixFourVerdicts", " / ".join(verd))
M("numSTwoSixFourRobust", "yes" if len(set(verd)) == 1 and verd[0] in ("heat", "qw") else "no")

# --- Hinh 3: t hoc duoc theo quy mo (h32l4, softplus 0.5, hops): moi lop mot duong, heat va qw
fig, ax = plt.subplots(figsize=(W_HALF, 2.2))
for op in ("heat", "qw"):
    tl = []
    for sh in SHELLS:
        c = cell(g12, "hops", sh, "softplus/t0=0.5", "h32l4", 200)
        ts = np.array([r["t_learned"] for r in c.get(op, {}).values()])
        tl.append(ts.mean(0) if len(ts) else np.full(4, np.nan))
    tl = np.array(tl)
    for l in range(tl.shape[1]):
        ax.plot([NN[s] for s in SHELLS], tl[:, l], color=C[op], ls=LS[op], marker=MK[op], ms=3,
                alpha=0.35 + 0.65 * l / 3, label=LBL[op] if l == 0 else None)
ax.set_xscale("log"); ax.set_xticks([264, 1584, 3168, 4400]); ax.set_xticklabels(["264", "1584", "3168", "4400"], rotation=30); ax.minorticks_off()
ax.set_xlabel("satellites in shell"); ax.set_ylabel("learned $t$ (4 layers, 200 epochs)")
ax.legend()
save(fig, "fig3-t-learned", W_HALF)

# ================================================================ LUOI 3 (neu co)
g3 = load_grid("grid3/scale_h32l4e1000_*.csv")
if g3:
    print("  grid3: %d hang, %d benh ly" % (len(g3), sum(r["pathology"] for r in g3)))
    M("numGridThreeRuns", len(g3)); M("numGridThreePathology", sum(r["pathology"] for r in g3))
    ARMS3 = ["relu/t0=0.5", "softplus/t0=0.5"]
    fig, axes = plt.subplots(1, 2, figsize=(W_WIDE, 2.4), sharey=True)
    for ax, task in zip(axes, ("hops", "delay")):
        for op in ("gcn", "heat", "qw"):
            for ai, arm in enumerate(ARMS3):
                mu, sd = [], []
                for sh in SHELLS[:3]:
                    st, cm, gain, vd = summarise(cell(g3, task, sh, arm, "h32l4", 1000))
                    mu.append(st.get(op, (np.nan,))[0]); sd.append(st.get(op, (0, 0))[1])
                ax.errorbar([NN[s] for s in SHELLS[:3]], mu, yerr=sd, color=C[op], marker=MK[op],
                            ls=["-", "--"][ai], capsize=2, lw=1.0, ms=3.5,
                            label=(LBL[op] + ", " + arm.split("/")[0]))
        cms = [summarise(cell(g3, task, sh, ARMS3[0], "h32l4", 1000))[1] for sh in SHELLS[:3]]
        ax.plot([NN[s] for s in SHELLS[:3]], cms, color=C["const"], ls=":", lw=0.9, label="constant")
        ax.set_xscale("log"); ax.set_xticks([264, 1584, 3168]); ax.set_xticklabels(["264", "1584", "3168"])
        ax.set_xlabel("satellites in shell"); ax.set_title(task + " field, 1000 epochs")
    axes[0].set_ylabel("MAE (mean ± sd over 10 seeds)")
    axes[1].legend(fontsize=6.5, ncol=2)
    save(fig, "fig4-scale-1000ep")
    for task in ("hops", "delay"):
        for sh in SHELLS[:3]:
            vs = [summarise(cell(g3, task, sh, a, "h32l4", 1000))[3] for a in ARMS3]
            M("numGthree" + task.capitalize() + sh.upper() + "Verdict", " / ".join(vs))
            M("numGthree" + task.capitalize() + sh.upper() + "Robust",
              "yes" if len(set(vs)) == 1 and vs[0] in ("heat", "qw") else "no")
else:
    print("  grid3: chua co (bo qua fig4 va macro G3)")

# ================================================================ macro
with io.open(os.path.join(OUTD, "numbers.tex"), "w", encoding="utf-8") as fh:
    fh.write("% GENERATED by figures/make_figures.py. Do not edit.\n")
    for k, v in sorted(NUM.items()):
        fh.write("\\newcommand{\\%s}{%s}\n" % (k, v))
print("  %d macro -> figures/out/numbers.tex" % len(NUM))
