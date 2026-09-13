"""Two machine-independent quantities of the GRAPHS, computed without training.

Review round 2 (12/09/2026) asked for (i) the constant predictor on the far-node metric for
every cell (rule 1 was honoured for MAE only) and (ii) the measured reach of every operator
beside the learned t of Table 8, because "reach-matched" had been asserted, not measured.

  python analysis/fields.py const  -> results/const_aurc.json   {task}/{shell}/{seed}: far-node
                                      error of the predictor that outputs the target mean, on
                                      the six evaluation instances of that seed (torus, seam kept)
  python analysis/fields.py reach  -> results/reach.json        per shell: expected hop distance
                                      of one row of each propagator, per layer at the learned t
                                      of the softplus/t0=0.5 arm (mean over valid seeds) and
                                      composed over the four layers; the same for the fixed
                                      ladder (SGC K', exact PPR alpha, truncated PPR)

Both are properties of the deterministic graph generator, so they are the same on every machine
up to floating point; nothing here is a training result.
"""
import json
import os
import sys

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from src.constellation import grid_isl_graph          # noqa: E402
from src.graphs import bfs_hops, eccentricity, largest_cc  # noqa: E402
from src.metrics import far_node_aurc                 # noqa: E402
from src.operators import gcn_propagator, laplacian, eig_sym  # noqa: E402
from src.scale import walker                          # noqa: E402

SHELLS = ["s264", "s1584", "s3168"]
SGC_LADDER = [1, 2, 8, 32, 64]
PPR_EXACT_LADDER = [0.2, 0.05, 0.02, 0.01]


def instances(name, n, seed, seam=True):
    """Same draws as src.scale.make_samples, without the eigendecomposition."""
    wk = walker(name)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        t = float(rng.uniform(0, wk.period_s))
        A, W = grid_isl_graph(wk, t, seam=seam)
        cc = largest_cc(A)
        A, W = A[np.ix_(cc, cc)], W[np.ix_(cc, cc)]
        dest = int(rng.integers(0, A.shape[0]))
        out.append((A, W, dest))
    return out


def field(A, W, dest, task):
    hops = bfs_hops(A, dest)
    hops = np.where(np.isfinite(hops), hops, 0.0)
    ecc = max(eccentricity(A, dest), 1.0)
    if task == "hops":
        y = hops / ecc
    else:
        d = dijkstra(csr_matrix(np.where(A > 0, W, 0.0)), directed=False, indices=dest)
        d = np.where(np.isfinite(d), d, 0.0)
        y = d / max(float(d.max()), 1e-9)
    return y.astype(np.float32), hops, ecc


def const_aurc(out):
    res = {}
    for task in ("hops", "delay"):
        for sh in SHELLS:
            for seed in range(10):
                vals = []
                for A, W, dest in instances(sh, 6, 2000 + seed):
                    y, hops, ecc = field(A, W, dest, task)
                    vals.append(far_node_aurc(np.full(len(y), y.mean(), np.float32), y, hops, ecc))
                res.setdefault(task, {}).setdefault(sh, {})[str(seed)] = float(np.nanmean(vals))
                print(task, sh, seed, "%.4f" % res[task][sh][str(seed)], flush=True)
    json.dump(res, open(out, "w"), indent=1)


def expected_hops(P, src, hops):
    r = np.abs(P[src]); r = r / r.sum()
    return float((r * hops).sum())


def reach(out, learned):
    res = {}
    for sh in SHELLS:
        A, W, dest = instances(sh, 1, 2000)[0]
        n = A.shape[0]
        hops = bfs_hops(A, 0)
        w, U = eig_sym(laplacian(A, normalized=False))
        g = gcn_propagator(A)
        heat = lambda t: (U * np.exp(-t * w)) @ U.T                       # noqa: E731
        walk = lambda t: np.abs((U * np.exp(-1j * t * w)) @ U.T) ** 2     # noqa: E731
        R = {"ecc": float(eccentricity(A, 0)), "gcn": expected_hops(g, 0, hops),
             "gcn_composed": expected_hops(np.linalg.matrix_power(g, 4), 0, hops)}
        for op, fn in (("heat", heat), ("qw", walk)):
            ts = learned[sh][op]
            per = [expected_hops(fn(t), 0, hops) for t in ts]
            comp = np.eye(n)
            for t in ts:
                comp = comp @ fn(t)
            R[op] = {"t": ts, "per_layer": per, "composed": expected_hops(comp, 0, hops)}
        I = np.eye(n)
        for K in SGC_LADDER:
            P = np.linalg.matrix_power(g, K)
            R["sgc_K%d" % K] = {"per_layer": expected_hops(P, 0, hops), "composed": expected_hops(np.linalg.matrix_power(P, 4), 0, hops)}
        for a in PPR_EXACT_LADDER:
            P = a * np.linalg.solve(I - (1 - a) * g, I); P = P / P.sum(1, keepdims=True)
            R["ppr_exact_a%g" % a] = {"per_layer": expected_hops(P, 0, hops), "composed": expected_hops(np.linalg.matrix_power(P, 4), 0, hops)}
        # the round-1 baseline: alpha = 0.05 truncated at K = 20 power steps
        P = I * 0.05; Q = I.copy()
        for k in range(20):
            Q = Q @ g; P = P + 0.05 * (0.95 ** (k + 1)) * Q
        P = P / P.sum(1, keepdims=True)
        R["ppr_trunc_a0.05_K20"] = {"per_layer": expected_hops(P, 0, hops), "composed": expected_hops(np.linalg.matrix_power(P, 4), 0, hops)}
        res[sh] = R
        print(sh, json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in R.items()}, default=lambda o: round(o, 2) if isinstance(o, float) else o)[:400], flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "const":
        const_aurc(os.path.join(HERE, "..", "results", "const_aurc.json"))
    elif what == "reach":
        learned = json.load(open(sys.argv[2]))
        reach(os.path.join(HERE, "..", "results", "reach.json"), learned)
