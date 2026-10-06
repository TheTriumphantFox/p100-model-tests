#!/usr/bin/env bash
# Kill the probed model's llama-server if host MemAvailable drops below FLOOR_MIB.
# Logs the lowest MemAvailable seen to watchdog.log. (Script file, so pgrep -f can't match this shell.)
cd "$(dirname "$0")"
FLOOR_MIB=${FLOOR_MIB:-6144}
min=999999
while :; do
  avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  [ "$avail" -lt "$min" ] && { min=$avail; echo "[$(date '+%T')] min MemAvailable $min MiB" >> watchdog.log; }
  if [ "$avail" -lt "$FLOOR_MIB" ]; then
    echo "[$(date '+%T')] MemAvailable $avail < $FLOOR_MIB MiB -- killing qwen3.8-27b-mtp" >> watchdog.log
    pkill -KILL -f -- '--alias qwen3.8-27b-mtp'
  fi
  sleep 1
done
