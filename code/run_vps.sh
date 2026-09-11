#!/usr/bin/env bash
# Chay 4 nhanh t tren 2 GPU cua VPS. Moi nhanh MOT CSV rieng (hai tien trinh khong ghi chung tep).
# Resumable: chay lai thi bo qua o da xong. Log: /tmp/leo_<arm>.log
set -u
PY=${PY:-/home/daipv/miniconda3/envs/leo-reach/bin/python}
# CFG=h16l3 (mac dinh, cau hinh ma PHAT HANH) | h32l4 (cau hinh BAI CU da dung, params=3301)
CFG=${CFG:-h16l3}
case "$CFG" in h16l3) HID=16; NL=3; PFX="";; h32l4) HID=32; NL=4; PFX="h32l4_";; *) echo "CFG?"; exit 1;; esac
EPOCHS=${EPOCHS:-200}; [ "$EPOCHS" != 200 ] && PFX="${PFX%_}e${EPOCHS}_"
SHELLS=${SHELLS:-s264,s1584,s3168,s4400}
ARMS_GPU0=${ARMS_GPU0:-"relu:0.5 relu:2.0"}; ARMS_GPU1=${ARMS_GPU1:-"softplus:0.5 softplus:2.0"}
cd "$(dirname "$0")"
mkdir -p results
launch() {  # gpu tp ti
  local gpu=$1 tp=$2 ti=$3 tag="${2}_t${3}"
  OMP_NUM_THREADS=36 MKL_NUM_THREADS=36 OPENBLAS_NUM_THREADS=36 CUDA_VISIBLE_DEVICES=$gpu nohup $PY -u experiments/exp_scale.py --device cuda --workers 1 \
     --hidden $HID --n-layers $NL --epochs $EPOCHS --shells "$SHELLS" --t-param "$tp" --t-init "$ti" --out "results/scale_${PFX}${tag}.csv" > "/tmp/leo_${PFX}${tag}.log" 2>&1
}
# GPU0: relu 0.5 -> relu 2.0 ; GPU1: softplus 0.5 -> softplus 2.0  (tuan tu trong moi GPU)
( for a in $ARMS_GPU0; do launch 0 ${a%:*} ${a#*:}; done ) &
( for a in $ARMS_GPU1; do launch 1 ${a%:*} ${a#*:}; done ) &
sleep 3
echo "da khoi dong; theo doi: tail -2 /tmp/leo_*.log"
