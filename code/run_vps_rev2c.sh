#!/usr/bin/env bash
# Can bang lai 13/09: GPU1 gach hai nhanh o s3168 (~6 phut/o). Tach shell nho sang GPU0, file rieng
# (rules.load doc glob seamcut_*.csv nen hai file mot nhanh la binh thuong).
set -u
PY=${PY:-/home/daipv/miniconda3/envs/leo-reach/bin/python}
cd "$(dirname "$0")"
pkill -f "seamcut_h32l4e1000_relu_t2.0.csv" ; pkill -f "seamcut_h32l4e1000_softplus_t2.0.csv"; sleep 3
run() { CUDA_VISIBLE_DEVICES=$1 OMP_NUM_THREADS=16 nohup $PY -u experiments/exp_scale.py --device cuda --workers 1 --hidden 32 --n-layers 4 --epochs 1000 --seam cut --ops gcn,heat,qw "${@:2}"; }
run 1 --shells s3168 --t-param relu --t-init 2.0 --out results/rev2/seamcut_h32l4e1000_relu_t2.0.csv > /tmp/leo_r2b_b.log 2>&1 &
run 1 --shells s3168 --t-param softplus --t-init 2.0 --out results/rev2/seamcut_h32l4e1000_softplus_t2.0.csv > /tmp/leo_r2b_c.log 2>&1 &
run 0 --shells s264,s1584 --t-param relu --t-init 2.0 --out results/rev2/seamcut_h32l4e1000_relu_t2.0_small.csv > /tmp/leo_r2b_d.log 2>&1 &
run 0 --shells s264,s1584 --t-param softplus --t-init 2.0 --out results/rev2/seamcut_h32l4e1000_softplus_t2.0_small.csv > /tmp/leo_r2b_e.log 2>&1 &
sleep 3; echo "da can bang: 3 tien trinh GPU0, 2 tien trinh GPU1"
