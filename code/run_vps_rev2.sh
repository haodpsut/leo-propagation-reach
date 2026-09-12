#!/usr/bin/env bash
# Vong sua 2 (review 12/09, Major): (a) nhanh CAT SEAM that (moi luoi truoc do la torus du canh);
# (b) thang reach cho baseline co dinh: SGC K' in {2,8,32,64}, PPR CHINH XAC alpha in {0.2,0.05,0.02,0.01};
# (c) o kiem do chinh xac: float64 toan bo, hops/1584/softplus t0=0.5, 10 seed, 3 toan tu.
set -u
PY=${PY:-/home/daipv/miniconda3/envs/leo-reach/bin/python}
cd "$(dirname "$0")"; mkdir -p results/rev2
run() { CUDA_VISIBLE_DEVICES=$1 OMP_NUM_THREADS=36 nohup $PY -u experiments/exp_scale.py --device cuda --workers 1 --hidden 32 --n-layers 4 --epochs 1000 --shells s264,s1584,s3168 "${@:2}"; }
( run 0 --dtype float64 --tasks hops --shells s1584 --ops gcn,heat,qw --out results/rev2/precision_f64_hops1584.csv > /tmp/leo_r2_prec.log 2>&1
  run 0 --seam cut --ops gcn,heat,qw --out results/rev2/seamcut_h32l4e1000_softplus_t0.5.csv > /tmp/leo_r2_seam.log 2>&1
  run 0 --seam cut --ops ppr,sgc --out results/rev2/seamcut_pprsgc.csv > /tmp/leo_r2_seamb.log 2>&1 ) &
( for K in 2 8 32 64; do run 1 --ops sgc --sgc-k $K --out results/rev2/sweep_sgc_k$K.csv > /tmp/leo_r2_sgc$K.log 2>&1; done
  for A in 0.2 0.05 0.02 0.01; do run 1 --ops ppr --ppr-k 0 --ppr-alpha $A --out results/rev2/sweep_ppr_exact_a$A.csv > /tmp/leo_r2_ppr$A.log 2>&1; done ) &
sleep 3; echo "da khoi dong 2 chuoi (rev2)"
