#!/usr/bin/env bash
# Sample the :8080 production router for CONTENTION while a bench leg holds the GPU.
#
# watchdog.py guards the production router's PID (did we kill it?). This guards the other
# direction: did PRODUCTION wake up while we were running? The router serves devstral on
# demand, so the tell is a llama-server child appearing under the :8080 pid, and GPU use
# climbing past what our own model accounts for.
#
# It does not kill anything -- a bench run that overlapped production is discarded by a
# human, and an automatic kill on a noisy sample would be worse than the disease. The log
# exists so "was this number taken on a clean box?" is answerable after the fact.
#
#   prodwatch.sh [poll-seconds]
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
LOG=$HERE/PRODWATCH.log
POLL=${1:-30}
PP=$(ss -ltnpH 'sport = :8080' 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
say() { echo "[$(date '+%m-%d %T')] prodwatch: $*" | tee -a "$LOG"; }
say "started; :8080 pid=${PP:-NONE}, polling every ${POLL}s"
prev=""
while true; do
  kids=$(ps -eo pid,ppid,comm | awk -v pp="${PP:-0}" '$2==pp && $3 ~ /llama-server/ {print $1}' | tr '\n' ' ')
  gpu=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}')
  state="${kids:-idle}"
  if [ "$state" != "$prev" ]; then
    if [ -n "$kids" ]; then
      say "!!! PRODUCTION IS SERVING -- :8080 child(ren) $kids appeared, GPU ${gpu} MiB."
      say "!!!   Any bench leg overlapping this window may have spilled to CPU. Discard it."
    else
      say "production idle again (GPU ${gpu} MiB)"
    fi
    prev="$state"
  fi
  sleep "$POLL"
done
