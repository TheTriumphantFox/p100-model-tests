#!/usr/bin/env bash
# SECURITY: historical driver; may stop services, kill processes, or edit live presets.
if [ "${P100_ALLOW_ARCHIVED_DRIVER:-}" != "1" ]; then
  printf '%s\n' 'Refusing archived driver. Review SECURITY.md; explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 only in a disposable test environment.' >&2
  exit 2
fi
# Host-RAM watchdog for the Strata IQ3_S run. On 2026-10-05 Flash-Next froze this box
# by exhausting host RAM into zram; IQ3_S keeps a ~47 GiB expert arena in RAM on a
# 61 GiB machine. Kills the engine before that can happen, and samples RAM/VRAM.
#   ram_watchdog.sh [floor_gib=3] [samples.csv]
# Matches the engine by process NAME (pidof), never pkill -f, which can match itself.
FLOOR_KIB=$(( ${1:-3} * 1024 * 1024 ))
OUT=${2:-$(dirname "$0")/memory-samples.csv}
echo "epoch,mem_avail_gib,swap_used_gib,gpu0_mib,gpu1_mib" > "$OUT"
n=0
while true; do
  avail=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
  if [ "$avail" -lt "$FLOOR_KIB" ]; then
    echo "$(date -Is) MemAvailable $((avail / 1024)) MiB < floor: killing strata" | tee -a "$OUT.kills"
    pids=$(pidof strata; pgrep -f "Strata/serve/server.py")
    [ -n "$pids" ] && kill -9 $pids
    sleep 5
  fi
  if [ $(( n % 5 )) -eq 0 ]; then
    swap=$(awk '/^SwapTotal:/ {t=$2} /^SwapFree:/ {f=$2} END {print t-f}' /proc/meminfo)
    gpu=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | paste -sd,)
    awk -v t="$(date +%s)" -v a="$avail" -v s="$swap" -v g="$gpu" \
      'BEGIN {printf "%s,%.2f,%.2f,%s\n", t, a / 1048576, s / 1048576, g}' >> "$OUT"
  fi
  n=$(( n + 1 ))
  sleep 1
done
