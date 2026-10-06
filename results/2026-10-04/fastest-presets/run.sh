#!/usr/bin/env bash
# Waits until the router has been quiet for 120 s, restarts it so it rereads models.ini,
# then checks each changed preset.
cd "$(dirname "$0")"
last() { journalctl --user -u llama-router -n 1 --no-pager -o short-unix | awk '{print int($1)}'; }
while :; do
  now=$(date +%s); l=$(last)
  util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | sort -n | tail -1)
  [ $((now - l)) -ge 120 ] && [ "$util" -lt 10 ] && break
  sleep 15
done
echo "idle at $(date +%T), restarting router"
systemctl --user restart llama-router; sleep 5
until curl -sf localhost:8080/health >/dev/null; do sleep 1; done
./check.py qwen3.6-27b-abliterated 131072
./check.py qwen3.6-35b-a3b-planner 81920
./check.py qwen3.6-35b-a3b-planner-mtp 49152
echo ALL_DONE
