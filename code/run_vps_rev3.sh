#!/usr/bin/env bash
# Vong sua 3 (review 13/09, Major): (a) ba o DA CHUNG NHAN chay lai float64 (heat+walk, 4 nhanh t):
# torus hop/264, torus delay/264, cat-seam hop/1584; (b) doi chung cat ngau nhien S link (hops/1584,
# 4 nhanh, 3 toan tu); (c) luoi 1 (200 epoch, cau hinh bai cu) tren do thi cat seam, 2 nhanh, 4 shell.
set -u
PY=${PY:-/home/daipv/miniconda3/envs/leo-reach/bin/python}
cd "$(dirname "$0")"; mkdir -p results/rev3
run() { CUDA_VISIBLE_DEVICES=$1 OMP_NUM_THREADS=16 nohup $PY -u experiments/exp_scale.py --device cuda --workers 1 --hidden 32 --n-layers 4 "${@:2}"; }
arms() { for a in "relu 0.5" "relu 2.0" "softplus 0.5" "softplus 2.0"; do set -- $a; "$@" ; done; }
( for a in "relu 0.5" "relu 2.0" "softplus 0.5" "softplus 2.0"; do set -- $a
    run 0 --epochs 1000 --dtype float64 --shells s264 --ops heat,qw --t-param $1 --t-init $2 --out results/rev3/precision_f64_torus_264.csv >> /tmp/leo_r3_a.log 2>&1
  done
  for a in "relu 0.5" "relu 2.0" "softplus 0.5" "softplus 2.0"; do set -- $a
    run 0 --epochs 1000 --dtype float64 --seam cut --tasks hops --shells s1584 --ops heat --t-param $1 --t-init $2 --out results/rev3/precision_f64_seamcut_hops1584_heat.csv >> /tmp/leo_r3_b.log 2>&1
  done
  for a in "relu 0.5" "relu 2.0" "softplus 0.5" "softplus 2.0"; do set -- $a
    run 0 --epochs 1000 --seam random --tasks hops --shells s1584 --ops gcn,heat,qw --t-param $1 --t-init $2 --out results/rev3/randomcut_hops1584.csv >> /tmp/leo_r3_c.log 2>&1
  done ) &
( for a in "relu 0.5" "relu 2.0" "softplus 0.5" "softplus 2.0"; do set -- $a
    run 1 --epochs 1000 --dtype float64 --seam cut --tasks hops --shells s1584 --ops qw --t-param $1 --t-init $2 --out results/rev3/precision_f64_seamcut_hops1584_qw.csv >> /tmp/leo_r3_d.log 2>&1
  done
  for a in "softplus 0.5" "relu 0.5"; do set -- $a
    run 1 --epochs 200 --seam cut --shells s264,s1584,s3168,s4400 --ops gcn,heat,qw --t-param $1 --t-init $2 --out results/rev3/seamcut_grid1_h32l4.csv >> /tmp/leo_r3_e.log 2>&1
  done ) &
sleep 3; echo "da khoi dong rev3: GPU0 = f64 264 -> f64 seam heat -> random cut; GPU1 = f64 seam walk -> luoi 1 cat seam"
