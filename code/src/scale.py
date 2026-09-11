"""Scale study helpers: larger Walker shells, a delay-field task, and a training loop that
records what the validity gate needs (loss trajectory, learned propagation times).

Everything here is ADDITIVE. src/data.py, src/train.py and experiments/exp_*.py are the
artifact of the rejected TNSE submission and are left untouched.

⚠ Two things the old code/text disagreed on, fixed here and stated in the paper:
  * make_leo_samples() ran with seam=False while the text said "counter-rotating seam cut".
    The scale study cuts the seam (seam=True), which is the physically standard +Grid.
  * "Starlink shell-1 geometry" is real (72x22). The 3168 and 4400 shells below are scale-ups
    of that geometry (72x44, 100x44), NOT real constellations; the paper must say so.
"""
import numpy as np
import torch
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from .constellation import Walker, grid_isl_graph
from .graphs import bfs_hops, largest_cc, eccentricity
from .models import PropGNN, n_params, build_propagator
from .operators import laplacian, eig_sym, gcn_propagator
from .metrics import mae, far_node_aurc


class SoftPropGNN(PropGNN):
    """PropGNN with t = softplus(theta) instead of relu(t).

    ⛔ WHY (found in the Mac smoke test, 11/09/2026, before any real run): with relu(t) the
    learned times went NEGATIVE in layers 2-3 (heat [2.72,-0.15,-0.16], qw [0.87,-0.04,-0.04]).
    relu(t<0)=0 makes the propagator the identity AND kills its gradient, so both spectral
    models were propagating in ONE layer only. Any "operator ranking" measured under relu(t) is
    confounded by how far t drifts from its init before dying. softplus keeps t>0 with a live
    gradient. theta is initialised so that softplus(theta)=0.5, matching the old init.
    The old parameterisation is kept as a control arm (t_param='relu').
    """

    def __init__(self, *a, t_param="softplus", t_init=0.5, **k):
        super().__init__(*a, **k)
        self.t_param = t_param
        with torch.no_grad():
            # ⚠ t_init is an ARM of the study, not a constant: the Mac smoke showed the learned
            #   reach (and the operator ranking) depends on where t starts.
            self.t.fill_(float(np.log(np.expm1(t_init))) if t_param == "softplus" else t_init)

    def times(self):
        return torch.nn.functional.softplus(self.t) if self.t_param == "softplus" else self.t

    def forward(self, X, w, U, gcn_phi):
        T = self.times()
        H = X
        for l in range(self.n_layers):
            Phi = build_propagator(self.op_kind, w, U, T[l, 0], gcn_phi)
            H = self.act(self.lins[l](Phi @ H))
        return self.readout(H).squeeze(-1)


SHELLS = {
    # name: (total, planes, phasing, inclination, altitude_km, note)
    "s264":  (264,  24,  1, 53.0, 550.0, "24x11, main case-study scale of the old paper"),
    "s1584": (1584, 72,  1, 53.0, 550.0, "Starlink shell-1 geometry, 72x22"),
    "s3168": (3168, 72,  1, 53.0, 550.0, "scale-up 72x44 of shell-1 geometry (synthetic)"),
    "s4400": (4400, 100, 1, 53.0, 550.0, "scale-up 100x44 (synthetic)"),
}


def walker(name):
    tot, planes, f, inc, alt, _ = SHELLS[name]
    return Walker(tot, planes, f, inc, alt)


class ScaleSample:
    """Snapshot + destination. target='hops' (old task) or 'delay' (propagation delay field)."""

    def __init__(self, A, W, dest, target="hops"):
        self.A, self.dest, self.n, self.target = A, dest, A.shape[0], target
        hops = bfs_hops(A, dest)
        self.reachable = np.isfinite(hops)
        self.hops = np.where(self.reachable, hops, 0.0)
        self.ecc = max(eccentricity(A, dest), 1.0)
        if target == "hops":
            field, denom = self.hops, self.ecc
        elif target == "delay":
            # shortest-path propagation delay (s) using the ISL delay weights W
            d = dijkstra(csr_matrix(np.where(A > 0, W, 0.0)), directed=False, indices=dest)
            fin = np.isfinite(d)
            field = np.where(fin, d, 0.0)
            denom = max(float(field.max()), 1e-9)      # "delay eccentricity"
        else:
            raise ValueError(target)
        self.y = (field / denom).astype(np.float32)
        deg = A.sum(1)
        seed = np.zeros(self.n, dtype=np.float32)
        seed[dest] = 1.0
        self.X = np.stack([seed, (deg / max(deg.max(), 1.0)).astype(np.float32)], axis=1)
        w, U = eig_sym(laplacian(A, normalized=False))
        self.w, self.U = w.astype(np.float64), U.astype(np.float64)


def make_samples(name, n, seed, target="hops", seam=True):
    wk = walker(name)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        t = float(rng.uniform(0, wk.period_s))
        A, W = grid_isl_graph(wk, t, seam=seam)
        cc = largest_cc(A)
        A, W = A[np.ix_(cc, cc)], W[np.ix_(cc, cc)]
        out.append(ScaleSample(A, W, int(rng.integers(0, A.shape[0])), target=target))
    return out


def _tensors(s, device):
    f = lambda a: torch.tensor(a, dtype=torch.float32, device=device)   # noqa: E731
    return f(s.X), f(s.w), f(s.U), f(s.y), f(gcn_propagator(s.A))


# ⛔ VALIDITY, declared in claim-structure.md BEFORE any run, REVISED 11/09 after measuring the
#    null: the constant predictor already scores MAE ~0.19 (hops) / ~0.17 (delay), so the first
#    draft's "final MAE < 0.5" would have passed a model that learned nothing. Validity is now
#    about TRAINING PATHOLOGY only (NaN, non-decreasing loss); whether a run beats the constant
#    baseline is a RESULT and is reported as its own column, never used to drop rows.
MIN_LOSS_DROP = 0.10     # first-third -> last-third loss must fall by >=10%


def train_eval_logged(op, train_s, eval_s, hidden=16, n_layers=3, epochs=200, lr=0.01,
                      seed=0, device="cpu", t_param="softplus", t_init=0.5):
    np.random.seed(seed)
    torch.manual_seed(seed)
    model = SoftPropGNN(in_dim=2, hidden=hidden, out_dim=1, n_layers=n_layers, op_kind=op,
                        t_param=t_param, t_init=t_init).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    cache = [_tensors(s, device) for s in train_s]
    hist = []
    for ep in range(epochs):
        model.train()
        opt.zero_grad()
        loss = sum(torch.nn.functional.mse_loss(model(X, w, U, g), y) for X, w, U, y, g in cache)
        loss = loss / len(cache)
        loss.backward()
        opt.step()
        hist.append(float(loss.item()))
    # train MAE at the end, for the validity gate
    model.eval()
    with torch.no_grad():
        tr_mae = float(np.mean([mae(model(X, w, U, g).cpu().numpy(), y.cpu().numpy())
                                for X, w, U, y, g in cache]))
        maes, aurcs = [], []
        for s in eval_s:
            X, w, U, y, g = _tensors(s, device)
            p = model(X, w, U, g).cpu().numpy()
            maes.append(mae(p, s.y))
            aurcs.append(far_node_aurc(p, s.y, s.hops, s.ecc))
    k = max(len(hist) // 3, 1)
    thirds = [float(np.mean(hist[i * k:(i + 1) * k])) for i in range(3)]
    monotone = thirds[0] > thirds[1] > thirds[2]
    finite = all(np.isfinite(hist)) and np.isfinite(tr_mae)
    dropped = finite and thirds[0] > 0 and (thirds[0] - thirds[2]) / thirds[0] >= MIN_LOSS_DROP
    valid = bool(finite and monotone and dropped)
    const_mae = float(np.mean([mae(np.full(s.n, s.y.mean(), np.float32), s.y) for s in eval_s]))
    t_learned = model.times().detach().cpu().numpy().ravel().tolist() if op != "gcn" else []
    return {
        "op": op, "mae": float(np.mean(maes)), "aurc": float(np.nanmean(aurcs)),
        "train_mae": tr_mae, "const_mae": const_mae,
        "beats_const": bool(np.mean(maes) < const_mae),
        "loss_thirds": thirds, "monotone": bool(monotone),
        "valid": valid, "t_learned": t_learned, "t_param": t_param, "t_init": t_init,
        "params": n_params(model),
        "n_nodes": int(np.mean([s.n for s in eval_s])),
    }
