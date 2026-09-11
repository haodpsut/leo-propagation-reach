"""Tables from results/scale.csv. The ONLY reader of the CSV; the paper reads only this output.

Rules, all declared in claim-structure.md before the run:
  * every headline number is printed next to the count of INVALID runs behind it;
  * "wins" at a (task, shell, arm) = lower mean MAE AND wins >= WIN_SEEDS of the seeds;
  * a ranking is "robust" only if it holds in ALL arms (t_param x t_init);
  * invalid rows are never dropped silently: they are excluded from means and COUNTED.

Usage: python analysis/make_tables.py results/scale.csv [--out results/tables.md]
"""
import argparse
import collections
import csv
import json
import sys

WIN_SEEDS = 7          # out of 10, declared


def load(path):
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        for k in ("mae", "aurc", "const_mae", "t_init"):
            r[k] = float(r[k])
        r["seed"] = int(r["seed"])
        r["valid"] = r["valid"] == "True"
        r["beats_const"] = r["beats_const"] == "True"
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--out", default=None)
    ap.add_argument("--metric", default="mae", choices=["mae", "aurc"])
    a = ap.parse_args()
    rows = load(a.csv)
    out = []
    P = out.append
    n_inv = sum(not r["valid"] for r in rows)
    P(f"# scale study: {len(rows)} runs, {n_inv} INVALID (kept in CSV, excluded from means)\n")

    # group: (task, shell, arm) -> op -> list of rows
    G = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        arm = f"{r['t_param']}/t0={r['t_init']:g}"
        G[(r["task"], r["shell"], arm)][r["op"]].append(r)
    shells = ["s264", "s1584", "s3168", "s4400"]
    ops = ["gcn", "heat", "qw"]
    arms = sorted({k[2] for k in G})
    tasks = sorted({k[0] for k in G})

    verdict = {}   # (task, shell, arm) -> winner among heat/qw or "tie"
    for task in tasks:
        for arm in arms:
            P(f"\n## task={task} · arm={arm} · metric={a.metric}\n")
            P("| shell | " + " | ".join(f"{op} mean±std (n valid / n inv / beats-const)" for op in ops)
              + " | heat vs qw: seeds won | verdict |")
            P("|---|" + "---|" * (len(ops) + 2))
            for sh in shells:
                cell = G.get((task, sh, arm))
                if not cell:
                    continue
                stats, line = {}, [sh]
                for op in ops:
                    rs = cell.get(op, [])
                    v = [r for r in rs if r["valid"]]
                    m = [r[a.metric] for r in v]
                    inv = len(rs) - len(v)
                    bc = sum(r["beats_const"] for r in v)
                    if m:
                        mu = sum(m) / len(m)
                        sd = (sum((x - mu) ** 2 for x in m) / max(len(m) - 1, 1)) ** 0.5
                        stats[op] = {r["seed"]: r[a.metric] for r in v}
                        line.append(f"{mu:.4f}±{sd:.4f} ({len(v)}/{inv}/{bc})")
                    else:
                        line.append(f"— (0/{inv}/0)")
                # paired seed comparison heat vs qw
                if "heat" in stats and "qw" in stats:
                    common = sorted(set(stats["heat"]) & set(stats["qw"]))
                    hw = sum(stats["heat"][s] < stats["qw"][s] for s in common)
                    qw = sum(stats["qw"][s] < stats["heat"][s] for s in common)
                    mh = sum(stats["heat"].values()) / len(stats["heat"])
                    mq = sum(stats["qw"].values()) / len(stats["qw"])
                    if len(common) >= WIN_SEEDS and qw >= WIN_SEEDS and mq < mh:
                        vd = "qw"
                    elif len(common) >= WIN_SEEDS and hw >= WIN_SEEDS and mh < mq:
                        vd = "heat"
                    else:
                        vd = "tie" if len(common) >= WIN_SEEDS else f"n<{WIN_SEEDS}"
                    line.append(f"heat {hw} · qw {qw} (of {len(common)})")
                    line.append(vd)
                    verdict[(task, sh, arm)] = vd
                else:
                    line += ["—", "—"]
                P("| " + " | ".join(line) + " |")

    P("\n## Robustness across arms (the claim's own test)\n")
    P("A ranking at (task, shell) counts only if it is the SAME in every arm.\n")
    P("| task | shell | " + " | ".join(arms) + " | robust? |")
    P("|---|---|" + "---|" * (len(arms) + 1))
    for task in tasks:
        for sh in shells:
            vs = [verdict.get((task, sh, arm), "—") for arm in arms]
            robust = ("YES: " + vs[0]) if (len(set(vs)) == 1 and vs[0] in ("heat", "qw")) else "no"
            P(f"| {task} | {sh} | " + " | ".join(vs) + f" | {robust} |")

    # learned t, to show reach, per arm
    P("\n## Learned propagation time t (mean over valid runs, per layer)\n")
    P("| task | shell | arm | heat t | qw t |")
    P("|---|---|---|---|---|")
    for task in tasks:
        for sh in shells:
            for arm in arms:
                cell = G.get((task, sh, arm))
                if not cell:
                    continue
                def mt(op):
                    ts = [json.loads(r["t_learned"]) for r in cell.get(op, []) if r["valid"]]
                    if not ts:
                        return "—"
                    L = len(ts[0])
                    return "[" + ", ".join(f"{sum(t[i] for t in ts)/len(ts):.2f}" for i in range(L)) + "]"
                P(f"| {task} | {sh} | {arm} | {mt('heat')} | {mt('qw')} |")

    text = "\n".join(out)
    print(text)
    if a.out:
        open(a.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
