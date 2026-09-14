#!/usr/bin/env bash
# Vong sua 4 (review 14/09, Major): luoi 1 tren do thi cat seam con thieu HAI nhanh t0=2 (rev3 chi chay
# softplus 0.5 va relu 0.5). Chay them 2 nhanh x 4 shell x 3 toan tu x 10 seed x 2 task = 480 run,
# ghi noi vao CUNG tep results/rev3/seamcut_grid1_h32l4.csv (cung cau hinh, bo sinh doc chung).
set -u
PY=${PY:-/home/daipv/miniconda3/envs/leo-reach/bin/python}
cd "$(dirname "$0")"; mkdir -p results/rev3
run() { CUDA_VISIBLE_DEVICES=$1 OMP_NUM_THREADS=16 nohup $PY -u experiments/exp_scale.py --device cuda --workers 1 --hidden 32 --n-layers 4 "${@:2}"; }
( run 0 --epochs 200 --seam cut --shells s264,s1584,s3168,s4400 --ops gcn,heat,qw --t-param relu --t-init 2.0 --out results/rev3/seamcut_grid1_h32l4.csv >> /tmp/leo_r4_a.log 2>&1 ) &
( run 1 --epochs 200 --seam cut --shells s264,s1584,s3168,s4400 --ops gcn,heat,qw --t-param softplus --t-init 2.0 --out results/rev3/seamcut_grid1_h32l4.csv >> /tmp/leo_r4_b.log 2>&1 ) &
sleep 3; echo "da khoi dong rev4: GPU0 = luoi 1 cat seam relu t0=2; GPU1 = softplus t0=2"
