#!/usr/bin/env bash
# Xep hang luoi 3 sau khi moi exp_scale hien tai xong. Chay bang: setsid nohup bash queue_grid3.sh &
cd "$(dirname "$0")"
while pgrep -f "experiments/exp_scale.py" >/dev/null; do sleep 120; done
echo "$(date) luoi 2 xong, khoi dong luoi 3" >> /tmp/leo_queue.log
CFG=h32l4 EPOCHS=1000 SHELLS=s264,s1584,s3168 ARMS_GPU0="relu:0.5" ARMS_GPU1="softplus:0.5" bash run_vps.sh >> /tmp/leo_queue.log 2>&1
