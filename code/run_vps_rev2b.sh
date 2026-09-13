#!/usr/bin/env bash
# Vong sua 2b: ba nhanh t con lai tren do thi CAT SEAM (nhanh softplus t0=0.5 da chay o rev2),
# de luat 5 (ben vung qua nhanh) ap duoc cho do thi cat seam nhu cho torus.
set -u
PY=${PY:-/home/daipv/miniconda3/envs/leo-reach/bin/python}
cd "$(dirname "$0")"; mkdir -p results/rev2
run() { CUDA_VISIBLE_DEVICES=$1 OMP_NUM_THREADS=24 nohup $PY -u experiments/exp_scale.py --device cuda --workers 1 --hidden 32 --n-layers 4 --epochs 1000 --shells s264,s1584,s3168 --seam cut --ops gcn,heat,qw "${@:2}"; }
run 0 --t-param relu --t-init 0.5 --out results/rev2/seamcut_h32l4e1000_relu_t0.5.csv > /tmp/leo_r2b_a.log 2>&1 &
run 1 --t-param relu --t-init 2.0 --out results/rev2/seamcut_h32l4e1000_relu_t2.0.csv > /tmp/leo_r2b_b.log 2>&1 &
run 1 --t-param softplus --t-init 2.0 --out results/rev2/seamcut_h32l4e1000_softplus_t2.0.csv > /tmp/leo_r2b_c.log 2>&1 &
sleep 3; echo "da khoi dong 3 nhanh cat seam"
