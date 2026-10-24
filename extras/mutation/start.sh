#!/bin/bash
# start (or restart) any worker that isn't running and isn't finished
for m in 1 2; do
  if [ ! -e /root/mut/DONE$m ] && ! pgrep -f "run.py $m" >/dev/null; then
    cd /root/mut && nohup python3 -I /root/mut/run.py $m >> /root/mut/worker$m.log 2>&1 &
    echo "started worker $m"
  fi
done
