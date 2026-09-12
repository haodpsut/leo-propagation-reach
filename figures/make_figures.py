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
SHNAME = {"s264": "Small", "s1584": "ShellOne", "s3168": "Double", "s4400": "Large"}   # ten macro chi chu cai
NUM = {}


def M(name, value):
    key = re.sub(r"[^A-Za-z]", "", name)
    assert key not in NUM or NUM[key] == value, "macro %s bi dat hai lan khac gia tri" % key
    NUM[key] = value
    return value


def save(fig, name, target_w=W_WIDE):
    path_pdf = os.path.join(OUTD, "%s.pdf" % name)
    got = None
    for _ in range(12):
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
        fig.set_size_inches(max(w + (target_w - got), 1.5), h)   # legend rong hon khung thi dung, khong am
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
        elif len(common) < WIN_SEEDS:
            vd = "n<%d" % WIN_SEEDS          # giong het analysis/make_tables.py
        elif qw >= WIN_SEEDS and st["qw"][0] < st["heat"][0]:
            vd = "qw"
        elif hw >= WIN_SEEDS and st["heat"][0] < st["qw"][0]:
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
M("numFloorCellsLarge", n_floor); M("numRankableCellsLarge", n_rank)
M("numGridTwelvePlateau", sum(1 for r in g12 if not r["pathology"] and r["mae"] >= 0.98 * r["const_mae"] and r["shell"] != "s264"))
# do lech lon nhat giua ba toan tu (trung binh) o s4400, moi cfg/nhanh/tac vu: cho cau "within X of each other"
spread = []
for cfg in CFGS:
    for arm in ARMS:
        for task in ("hops", "delay"):
            st = summarise(cell(g12, task, "s4400", arm, cfg, 200))[0]
            mus = [v[0] for v in st.values()]
            if len(mus) == 3: spread.append(max(mus) - min(mus))
M("numLargeSpreadMax", "%.3f" % max(spread))   # o >=1584, hops, 2 cfg x 4 arm x 3 shell = 24

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

# --- Hinh 3: t hoc duoc theo quy mo, hai panel: 200 epoch (luoi 1-2) va 1000 epoch (luoi 3), h32l4, softplus 0.5, hops
def tl_panel(ax, rows, epochs, shells):
    for op in ("heat", "qw"):
        tl = []
        for sh in shells:
            c = cell(rows, "hops", sh, "softplus/t0=0.5", "h32l4", epochs)
            ts = np.array([r["t_learned"] for r in c.get(op, {}).values()])
            tl.append(ts.mean(0) if len(ts) else np.full(4, np.nan))
        tl = np.array(tl)
        for l in range(tl.shape[1]):
            ax.plot(range(len(shells)), tl[:, l], color=C[op], ls=LS[op], marker=MK[op], ms=3,
                    alpha=0.35 + 0.65 * l / 3, label=LBL[op] if l == 0 else None)
    ax.set_xticks(range(len(shells))); ax.set_xticklabels([str(NN[s]) for s in shells])
    ax.set_xlabel("satellites in shell"); ax.set_title("%d epochs" % epochs, fontsize=8)

fig, axes = plt.subplots(1, 2, figsize=(W_WIDE, 2.3))
tl_panel(axes[0], g12, 200, SHELLS)
g3_early = load_grid("grid3/scale_h32l4e1000_*.csv")
if g3_early:
    tl_panel(axes[1], g3_early, 1000, SHELLS[:3])
axes[0].set_ylabel("learned $t$ per layer")
axes[0].legend(fontsize=7)
save(fig, "fig3-t-learned", W_WIDE)
if g3_early:
    for sh in SHELLS[:3]:
        for op in ("heat", "qw"):
            c = cell(g3_early, "hops", sh, "softplus/t0=0.5", "h32l4", 1000)
            ts = np.array([r["t_learned"] for r in c.get(op, {}).values()])
            M("numTlayerOne" + SHNAME[sh] + ("Heat" if op == "heat" else "Walk"), "%.1f" % ts.mean(0)[0])

# ================================================================ LUOI 3 (neu co)
g3 = load_grid("grid3/scale_h32l4e1000_*.csv")
if g3:
    print("  grid3: %d hang, %d benh ly" % (len(g3), sum(r["pathology"] for r in g3)))
    M("numGridThreeRuns", len(g3)); M("numGridThreePathology", sum(r["pathology"] for r in g3))
    ARMS3 = ["relu/t0=0.5", "softplus/t0=0.5"]
    fig, axes = plt.subplots(1, 2, figsize=(W_WIDE, 2.6), sharey=True)
    X = [0, 1, 2]
    for ax, task in zip(axes, ("hops", "delay")):
        for op in ("gcn", "heat", "qw"):
            for ai, arm in enumerate(ARMS3):
                mu, sd = [], []
                for sh in SHELLS[:3]:
                    st, cm, gain, vd = summarise(cell(g3, task, sh, arm, "h32l4", 1000))
                    mu.append(st.get(op, (np.nan,))[0]); sd.append(st.get(op, (0, 0))[1])
                off = (-0.06 if ai == 0 else 0.06) + {"gcn": -0.12, "heat": 0.0, "qw": 0.12}[op]
                ax.errorbar([x + off for x in X], mu, yerr=sd, color=C[op], marker=MK[op],
                            ls=["-", "--"][ai], capsize=1.5, lw=0.9, ms=3.2, elinewidth=0.6,
                            label=(LBL[op] + ", " + arm.split("/")[0]))
        cms = [summarise(cell(g3, task, sh, ARMS3[0], "h32l4", 1000))[1] for sh in SHELLS[:3]]
        ax.plot(X, cms, color=C["const"], ls=":", lw=0.9, label="constant predictor")
        ax.set_xticks(X); ax.set_xticklabels(["264", "1584", "3168"])
        ax.set_xlabel("satellites in shell"); ax.set_title(task + " field", fontsize=8)
    axes[0].set_ylabel("MAE (mean $\\pm$ sd, valid seeds)")
    h, l = axes[1].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=6.5, bbox_to_anchor=(0.5, -0.04),
               handlelength=2.2, columnspacing=1.0)
    fig.subplots_adjust(bottom=0.36, wspace=0.08)
    save(fig, "fig4-scale-1000ep")
    for task in ("hops", "delay"):
        for sh in SHELLS[:3]:
            vs = [summarise(cell(g3, task, sh, a, "h32l4", 1000))[3] for a in ARMS3]
            M("numGthree" + task.capitalize() + SHNAME[sh] + "Verdict", " / ".join(vs))
            M("numGthree" + task.capitalize() + SHNAME[sh] + "Robust",
              "yes" if len(set(vs)) == 1 and vs[0] in ("heat", "qw") else "no")
else:
    print("  grid3: chua co (bo qua fig4 va macro G3)")

# ================================================================ hien vat ban so bo (06/2026), doc tu CSV da nop
PRE = os.path.join(ROOT, "code", "results-as-submitted-2026-06-28")
if os.path.exists(os.path.join(PRE, "exp_e_shell1.csv")):
    pre = {r["op"]: r for r in csv.DictReader(open(os.path.join(PRE, "exp_e_shell1.csv")))}
    M("numPrelimWalkMAE", "%.3f" % float(pre["qw"]["mae_mean"]))
    M("numPrelimHeatMAE", "%.3f" % float(pre["heat"]["mae_mean"]))
    M("numPrelimParams", int(float(pre["qw"]["params"])))
    n_seeds = len(list(csv.DictReader(open(os.path.join(PRE, "exp_e_shell1_perseed.csv"))))) // 3
    M("numPrelimSeeds", n_seeds)
    # params cua cau hinh ma phat hanh (hidden 16, 3 lop) tu luoi 1
    M("numReleasedParams", int(next(r for r in g12 if r["cfg"] == "h16l3")["params"]))
    M("numSubmittedParams", int(next(r for r in g12 if r["cfg"] == "h32l4")["params"]))

# ================================================================ bang shell, doc tu code/src/scale.py (khong go tay)
sys.path.insert(0, os.path.join(ROOT, "code"))
from src.scale import SHELLS as _SH                                   # noqa: E402
T = ["% GENERATED by figures/make_figures.py from code/src/scale.py::SHELLS\n\\begin{tabular}{@{}rrrrrl@{}}\n\\toprule\n"
     "satellites & planes & per plane & incl.\\ ($^{\\circ}$) & alt.\\ (km) & note \\\\\n\\midrule"]
NOTE = {"s264": "main scale of the preliminary version", "s1584": "Starlink shell-1 geometry~\\cite{starlink}",
        "s3168": "scale-up, synthetic", "s4400": "scale-up, synthetic"}
for k in SHELLS:
    tot, planes, f, inc, alt, _ = _SH[k]
    T.append("%d & %d & %d & %g & %g & %s \\\\" % (tot, planes, tot // planes, inc, alt, NOTE[k]))
T.append("\\bottomrule\n\\end{tabular}")
io.open(os.path.join(OUTD, "tab0-shells.tex"), "w").write("\n".join(T) + "\n")
M("numShellIncl", "%g" % _SH["s1584"][3]); M("numShellAlt", "%g" % _SH["s1584"][4])

# ================================================================ bang LaTeX
def fmt(st, op):
    return "%.3f $\\pm$ %.3f (%d)" % (st[op][0], st[op][1], st[op][2]) if op in st else "---"

T = []
# Bang 1: luoi 1-2, tac vu hops: cai thien cua toan tu tot nhat so voi hang so, theo cfg x nhanh x shell
T.append("% GENERATED by figures/make_figures.py\n\\begin{tabular}{@{}llrrrr@{}}\n\\toprule\n"
         "config & $t$ arm & 264 & 1584 & 3168 & 4400 \\\\\n\\midrule")
for cfg in CFGS:
    for arm in ARMS:
        cells = [summarise(cell(g12, "hops", sh, arm, cfg, 200)) for sh in SHELLS]
        row = " & ".join(("%.1f" % (100 * g)) + ("" if vd != "floor" else "$^{\\dagger}$") for (_, _, g, vd) in cells)
        T.append("%s & %s & %s \\\\" % (CFGNAME[cfg].lower(), arm.replace("/t0=", ", $t_0{=}$"), row))
T.append("\\bottomrule\n\\end{tabular}")
io.open(os.path.join(OUTD, "tab1-floor.tex"), "w").write("\n".join(T) + "\n")

if g3:
    T = ["% GENERATED by figures/make_figures.py\n\\begin{tabular}{@{}llrllrl@{}}\n\\toprule\n"
         "task & shell & GCN & heat $e^{-tL}$ & walk $|e^{-itL}|^2$ & seeds heat:walk & verdict \\\\\n\\midrule"]
    for task in ("hops", "delay"):
        for arm in ARMS3:
            T.append("\\multicolumn{7}{@{}l}{\\emph{%s field, %s}} \\\\" % (task, arm.replace("/t0=", ", $t_0{=}$")))
            for sh in SHELLS[:3]:
                c = cell(g3, task, sh, arm, "h32l4", 1000)
                st, cm, gain, vd = summarise(c)
                common = sorted(set(c.get("heat", {})) & set(c.get("qw", {})))
                hw = sum(c["heat"][s]["mae"] < c["qw"][s]["mae"] for s in common) if common else 0
                qw = len(common) - hw
                gcn = "%.3f" % st["gcn"][0] if "gcn" in st else "---"
                T.append("& %d & %s & %s & %s & %d:%d & %s \\\\" % (NN[sh], gcn, fmt(st, "heat"), fmt(st, "qw"), hw, qw, vd.replace("<", "$<$")))
    T.append("\\bottomrule\n\\end{tabular}")
    io.open(os.path.join(OUTD, "tab2-grid3.tex"), "w").write("\n".join(T) + "\n")
    # so hang benh ly va plateau cua luoi 3, cho van xuoi
    M("numGridThreePlateau", sum(1 for r in g3 if not r["pathology"] and r["mae"] >= 0.98 * r["const_mae"]))
    # ty le benh ly
    M("numGridThreePathologyPct", round(100.0 * sum(r["pathology"] for r in g3) / len(g3), 1))
    # heat vs qw o s264 softplus (cho abstract)
    st, cm, gain, vd = summarise(cell(g3, "hops", "s264", "softplus/t0=0.5", "h32l4", 1000))
    M("numGthreeHopsSmallHeat", "%.3f" % st["heat"][0]); M("numGthreeHopsSmallHeatSd", "%.3f" % st["heat"][1])
    M("numGthreeHopsSmallWalk", "%.3f" % st["qw"][0]); M("numGthreeHopsSmallWalkSd", "%.3f" % st["qw"][1])
    M("numGthreeHopsSmallConst", "%.3f" % cm)
    # so o quyet dinh duoc / tong, va so o heat thang ben
    cells3 = [(t, sh) for t in ("hops", "delay") for sh in SHELLS[:3]]
    rob = [NUM["numGthree" + t.capitalize() + SHNAME[sh] + "Robust"] for t, sh in cells3]
    M("numGthreeCells", len(cells3)); M("numGthreeHeatRobust", sum(r == "yes" for r in rob))
    M("numGthreeWalkRobust", sum(1 for t, sh in cells3 if NUM["numGthree" + t.capitalize() + SHNAME[sh] + "Verdict"] == "qw / qw"))
    # khoang cai thien so voi hang so o luoi 3, theo tac vu (cho van xuoi)
    for task in ("hops", "delay"):
        gs = [summarise(cell(g3, task, sh, a, "h32l4", 1000))[2] for a in ARMS3 for sh in SHELLS[:3]]
        M("numGthree" + task.capitalize() + "GainMin", round(100 * min(gs))); M("numGthree" + task.capitalize() + "GainMax", round(100 * max(gs)))
    for sh in SHELLS[:3]:
        gs = []
        for arm in ARMS3:
            st, cm, gain, vd = summarise(cell(g3, "hops", sh, arm, "h32l4", 1000))
            gs.append(100 * (cm - st["gcn"][0]) / cm)
        M("numGthreeGcnGain" + SHNAME[sh], round(max(gs), 1))
    # muc tang loss lon nhat trong cac ca benh ly
    rises = [max((th[i + 1] - th[i]) / th[i] for i in range(2)) for th in
             (json.loads(r["loss_thirds"]) for r in g3) if any(th[i + 1] > th[i] * 1.01 for i in range(2))]
    M("numGridThreeRiseMaxPct", round(100 * max(rises)))
print("  bang -> figures/out/tab*.tex")

# ================================================================ bang tom tat headline (tu chinh cac macro)
if g3:
    T = ["% GENERATED by figures/make_figures.py\n\\begin{tabular}{@{}p{0.52\\textwidth}lp{0.19\\textwidth}@{}}\n\\toprule\n"
         "finding & value & derived in \\\\\n\\midrule",
         "runs, fixed 200-epoch budget (grid 1) & %d & Sec.~\\ref{sec:floor} \\\\" % NUM["numGridTwelveRuns"],
         "largest gain over constant on any shell $\\geq$1584, any arm (grid 1) & %s\\%% & Fig.~\\ref{fig:floor}, Tab.~\\ref{tab:floor} \\\\" % max(NUM["numGainLargeMaxReleased"], NUM["numGainLargeMaxSubmitted"]),
         "rankable cells at $\\geq$1584 satellites, hop field (grid 1) & %d of %d & Tab.~\\ref{tab:floor} \\\\" % (NUM["numRankableCellsLarge"], NUM["numRankableCellsLarge"] + NUM["numFloorCellsLarge"]),
         "heat-vs-walk verdicts at 264 satellites across the four $t$ arms (grid 1) & %s & Fig.~\\ref{fig:arms} \\\\" % NUM["numSTwoSixFourVerdicts"],
         "runs, 1000-epoch budget (grid 2) & %d & Sec.~\\ref{sec:budget} \\\\" % NUM["numGridThreeRuns"],
         "task-scale cells where heat wins in every arm (grid 2) & %d of %d & Tab.~\\ref{tab:grid3} \\\\" % (NUM["numGthreeHeatRobust"], NUM["numGthreeCells"]),
         "task-scale cells where walk wins in every arm (grid 2) & %d of %d & Tab.~\\ref{tab:grid3} \\\\" % (NUM["numGthreeWalkRobust"], NUM["numGthreeCells"]),
         "runs collapsing to the constant solution under long training (grid 2) & %d (%s\\%%) & Sec.~\\ref{sec:collapse} \\\\" % (NUM["numGridThreePathology"], NUM["numGridThreePathologyPct"]),
         "preliminary 1584-satellite result, walk vs heat, %d seeds & %s vs %s & Sec.~\\ref{sec:budget} \\\\" % (NUM["numPrelimSeeds"], NUM["numPrelimWalkMAE"], NUM["numPrelimHeatMAE"]),
         "\\bottomrule\n\\end{tabular}"]
    io.open(os.path.join(OUTD, "tab-summary.tex"), "w").write("\n".join(T) + "\n")

# ================================================================ hinh luong giao thuc (TikZ), so lay tu ma
shells_txt = " $\\cdot$ ".join(str(_SH[k][0]) for k in SHELLS)
proto = r"""% GENERATED by figures/make_figures.py (shell sizes from code/src/scale.py, params from results)
\begin{tikzpicture}[
  font=\footnotesize, node distance=2.5mm and 2.6mm,
  box/.style={draw, rounded corners=1pt, align=center, inner sep=2pt, minimum height=6.5mm},
  arm/.style={box, fill=black!4},
  rule/.style={box, fill=black!10, minimum width=13.5mm},
  >={Stealth[length=1.8mm]}]
\node[arm] (ops) {3 operators\\GCN $\cdot$ $e^{-t\Lap}$ $\cdot$ $|e^{-it\Lap}|^{2}$};
\node[arm, right=of ops] (shells) {4 shells\\SHELLS};
\node[arm, right=of shells] (tasks) {2 tasks\\hop $\cdot$ delay};
\node[arm, right=of tasks] (seeds) {10 seeds\\per cell};
\node[arm, below=of ops] (tp) {$t$ parameterisation\\relu $\cdot$ softplus};
\node[arm, below=of shells] (t0) {$t_{0}$\\0.5 $\cdot$ 2};
\node[arm, below=of tasks] (cap) {capacity\\PREL $\cdot$ PSUB};
\node[arm, below=of seeds] (ep) {budget\\200 $\cdot$ 1000 ep.};
\node[draw, dashed, inner sep=1.8mm, fit=(ops)(seeds)(tp)(ep)] (grid) {};
\node[anchor=south west, font=\footnotesize] at (grid.north west) {grid 1: 200 epochs, all arms $\cdot$ grid 2: 1000 epochs, submitted capacity};
\node[rule, below=6mm of grid.south, anchor=north] (r3) {3. floor\\$g<0.05$};
\node[rule, left=of r3] (r2) {2. pathology\\excluded, counted};
\node[rule, left=of r2] (r1) {1. constant\\baseline};
\node[rule, right=of r3] (r4) {4. winner\\eq.~\eqref{eq:win}};
\node[rule, right=of r4] (r5) {5. robust\\every arm};
\draw[->] (grid.south) -- (r3.north);
\draw[->] (r1) -- (r2); \draw[->] (r2) -- (r3); \draw[->] (r3) -- (r4); \draw[->] (r4) -- (r5);
\end{tikzpicture}
"""
proto = proto.replace("SHELLS", shells_txt).replace("PREL", str(NUM["numReleasedParams"])).replace("PSUB", str(NUM["numSubmittedParams"]))
io.open(os.path.join(OUTD, "fig-protocol.tex"), "w").write(proto)

# ================================================================ macro
with io.open(os.path.join(OUTD, "numbers.tex"), "w", encoding="utf-8") as fh:
    fh.write("% GENERATED by figures/make_figures.py. Do not edit.\n")
    for k, v in sorted(NUM.items()):
        fh.write("\\newcommand{\\%s}{%s}\n" % (k, v))
print("  %d macro -> figures/out/numbers.tex" % len(NUM))
