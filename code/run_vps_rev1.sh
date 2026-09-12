#!/usr/bin/env bash
# Vong sua 1 (review 12/09): (a) nhanh t0=2 cho luoi 1000 epoch de luat 5 du 4 nhanh;
# (b) hai baseline reach-matched tach roi (ppr, sgc) o 200 va 1000 epoch, cau hinh bai cu.
set -u
PY=${PY:-/home/daipv/miniconda3/envs/leo-reach/bin/python}
cd "$(dirname "$0")"; mkdir -p results
run() { CUDA_VISIBLE_DEVICES=$1 OMP_NUM_THREADS=36 nohup $PY -u experiments/exp_scale.py --device cuda --workers 1 --hidden 32 --n-layers 4 "${@:2}"; }
( run 0 --epochs 1000 --shells s264,s1584,s3168 --t-param relu --t-init 2.0 --out results/scale_h32l4e1000_relu_t2.0.csv > /tmp/leo_rev_a.log 2>&1
  run 0 --epochs 200  --shells s264,s1584,s3168,s4400 --ops ppr,sgc --t-param softplus --t-init 0.5 --out results/scale_h32l4_pprsgc.csv > /tmp/leo_rev_c.log 2>&1 ) &
( run 1 --epochs 1000 --shells s264,s1584,s3168 --t-param softplus --t-init 2.0 --out results/scale_h32l4e1000_softplus_t2.0.csv > /tmp/leo_rev_b.log 2>&1
  run 1 --epochs 1000 --shells s264,s1584,s3168 --ops ppr,sgc --t-param softplus --t-init 0.5 --out results/scale_h32l4e1000_pprsgc.csv > /tmp/leo_rev_d.log 2>&1 ) &
sleep 3; echo "da khoi dong 2 chuoi"
