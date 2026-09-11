# leo-propagation-reach

Operator ranking vs constellation scale on dynamic LEO inter-satellite-link graphs:
local GCN, heat kernel `exp(-tL)`, and quantum-walk probability kernel `|exp(-itL)|^2`,
param-matched, multi-seed, two tasks, four scales, and four propagation-time arms.

Successor to the code of `haodpsut/qi-gnn-dynamic-wireless` (TNSE SI submission, rejected
2026-09-10). Old files under `code/src/{data,train,models,operators,...}.py` and
`code/experiments/exp_[a-d]*.py` are the submitted artifact and are left untouched;
everything new is in `code/src/scale.py` and `code/experiments/exp_scale.py`.

## Run (VPS, CPU-parallel)
```
cd code
for tp in relu softplus; do for ti in 0.5 2.0; do
  OMP_NUM_THREADS=1 python experiments/exp_scale.py --t-param $tp --t-init $ti --workers 60 --out results/scale.csv
done; done
```
Resumable: rerunning skips finished cells. Invalid (diverged) rows are kept and counted.

## Declared before running
`claim-structure.md`, `occupied-check.md`, `venue-precedent.md`.
