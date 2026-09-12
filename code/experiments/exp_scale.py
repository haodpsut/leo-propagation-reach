"""Exp SCALE: operator ranking vs constellation scale, param-matched, multi-seed, two tasks.

One CSV row per (task, shell, seed, op). Resumable: existing rows are skipped, so a killed run
continues where it stopped. Every row carries the validity fields; NOTHING is filtered here.
Filtering happens in the analysis script, where the count of invalid runs is printed next to
every headline number (rule: report the collapse rate, never hide it).

Usage (VPS, CPU-parallel, one process per cell):
    OMP_NUM_THREADS=1 python experiments/exp_scale.py --workers 60 --out results/scale.csv
Usage (GPU):
    python experiments/exp_scale.py --device cuda --workers 1 --out results/scale.csv
Smoke:
    python experiments/exp_scale.py --shells s264 --seeds 0 --epochs 5 --n-train 2 --n-eval 2
"""
import argparse
import csv
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

FIELDS = ["task", "shell", "seed", "op", "t_param", "t_init", "n_nodes", "mae", "aurc", "train_mae",
          "const_mae", "beats_const", "valid",
          "monotone", "loss_thirds", "t_learned", "params", "epochs", "n_train", "n_eval",
          "hidden", "n_layers", "secs", "device"]


def cell(args):
    task, shell, seed, op, cfg = args
    import torch
    torch.set_num_threads(1)
    from src.scale import make_samples, train_eval_logged
    t0 = time.time()
    tr = make_samples(shell, cfg["n_train"], seed=1000 + seed, target=task)
    ev = make_samples(shell, cfg["n_eval"], seed=2000 + seed, target=task)
    r = train_eval_logged(op, tr, ev, hidden=cfg["hidden"], n_layers=cfg["n_layers"],
                          epochs=cfg["epochs"], seed=seed, device=cfg["device"],
                          t_param=cfg["t_param"], t_init=cfg["t_init"])
    r.update(task=task, shell=shell, seed=seed, epochs=cfg["epochs"], n_train=cfg["n_train"],
             n_eval=cfg["n_eval"], hidden=cfg["hidden"], n_layers=cfg["n_layers"],
             secs=round(time.time() - t0, 1), device=cfg["device"])
    r["loss_thirds"] = json.dumps([round(x, 5) for x in r["loss_thirds"]])
    r["t_learned"] = json.dumps([round(x, 4) for x in r["t_learned"]])
    return r


def done_keys(path):
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return {(r["task"], r["shell"], int(r["seed"]), r["op"], r["t_param"], float(r["t_init"]))
                for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shells", default="s264,s1584,s3168,s4400")
    ap.add_argument("--tasks", default="hops,delay")
    ap.add_argument("--ops", default="gcn,heat,qw", help="gcn,heat,qw | ppr,sgc (reach-matched, no t)")
    ap.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    ap.add_argument("--n-train", type=int, default=8)
    ap.add_argument("--n-eval", type=int, default=6)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--hidden", type=int, default=16)
    ap.add_argument("--n-layers", type=int, default=3)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--t-param", default="softplus", choices=["softplus", "relu"],
                    help="relu = old parameterisation (control arm); softplus = fixed")
    ap.add_argument("--t-init", type=float, default=0.5, help="initial propagation time (arm)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default="results/scale.csv")
    a = ap.parse_args()
    cfg = dict(n_train=a.n_train, n_eval=a.n_eval, epochs=a.epochs, hidden=a.hidden,
               n_layers=a.n_layers, device=a.device, t_param=a.t_param, t_init=a.t_init)
    grid = list(itertools.product(a.tasks.split(","), a.shells.split(","),
                                  [int(s) for s in a.seeds.split(",")], a.ops.split(",")))
    have = done_keys(a.out)
    todo = [g for g in grid if (g + (a.t_param, float(a.t_init))) not in have]
    print(f"[scale] {len(grid)} cells, {len(have)} done, {len(todo)} to run, workers={a.workers}, "
          f"device={a.device}", flush=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    new = not os.path.exists(a.out)
    # large shells first so the tail of the run is short cells
    order = {"s4400": 0, "s3168": 1, "s1584": 2, "s264": 3}
    todo.sort(key=lambda g: order.get(g[1], 9))
    with open(a.out, "a", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            wr.writeheader()
        n_ok = n_bad = 0
        if a.workers <= 1:
            it = (cell((t, s, sd, op, cfg)) for t, s, sd, op in todo)
            for r in it:
                wr.writerow(r); f.flush()
                n_ok += r["valid"]; n_bad += (not r["valid"])
                print(f"  {r['task']:5s} {r['shell']:6s} seed{r['seed']:<2d} {r['op']:4s} "
                      f"mae={r['mae']:.4f} const={r['const_mae']:.3f} valid={r['valid']} {r['secs']}s", flush=True)
        else:
            with ProcessPoolExecutor(max_workers=a.workers) as ex:
                futs = [ex.submit(cell, (t, s, sd, op, cfg)) for t, s, sd, op in todo]
                for fu in as_completed(futs):
                    r = fu.result()
                    wr.writerow(r); f.flush()
                    n_ok += r["valid"]; n_bad += (not r["valid"])
                    print(f"  {r['task']:5s} {r['shell']:6s} seed{r['seed']:<2d} {r['op']:4s} "
                          f"mae={r['mae']:.4f} const={r['const_mae']:.3f} valid={r['valid']} {r['secs']}s", flush=True)
    print(f"[scale] wrote {a.out}: {n_ok} valid, {n_bad} INVALID (diverged/non-monotone). "
          f"Invalid rows are kept in the CSV and counted by the analysis.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
