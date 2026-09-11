#!/usr/bin/env bash
# Chay 4 nhanh t tren 2 GPU cua VPS. Moi nhanh MOT CSV rieng (hai tien trinh khong ghi chung tep).
# Resumable: chay lai thi bo qua o da xong. Log: /tmp/leo_<arm>.log
set -u
PY=${PY:-/home/daipv/miniconda3/envs/leo-reach/bin/python}
cd "$(dirname "$0")"
mkdir -p results
launch() {  # gpu tp ti
  local gpu=$1 tp=$2 ti=$3 tag="${2}_t${3}"
  CUDA_VISIBLE_DEVICES=$gpu nohup $PY -u experiments/exp_scale.py --device cuda --workers 1 \
     --t-param "$tp" --t-init "$ti" --out "results/scale_${tag}.csv" > "/tmp/leo_${tag}.log" 2>&1
}
# GPU0: relu 0.5 -> relu 2.0 ; GPU1: softplus 0.5 -> softplus 2.0  (tuan tu trong moi GPU)
( launch 0 relu 0.5; launch 0 relu 2.0 ) &
( launch 1 softplus 0.5; launch 1 softplus 2.0 ) &
sleep 3
echo "da khoi dong; theo doi: tail -2 /tmp/leo_*.log"
