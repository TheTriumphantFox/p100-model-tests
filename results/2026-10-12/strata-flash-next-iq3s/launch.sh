#!/usr/bin/env bash
# SECURITY: historical driver; may stop services, kill processes, or edit live presets.
if [ "${P100_ALLOW_ARCHIVED_DRIVER:-}" != "1" ]; then
  printf '%s\n' 'Refusing archived driver. Review SECURITY.md; explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 only in a disposable test environment.' >&2
  exit 2
fi
# First launch of Strata + Qwen3.8-Flash-Next IQ3_S on :8090, under the RAM watchdog.
# Refuses to start while anything holds the GPUs (the llama routers' loaded models).
# Ctrl-C stops the server and the watchdog together.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
STRATA=/home/hm/AI/Strata

busy=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 > 1024')
if [ -n "$busy" ]; then
  echo "GPUs in use (index, MiB):"; echo "$busy"
  nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
  echo "Unload the model from the llama router(s) first."; exit 1
fi
avail=$(awk '/^MemAvailable:/ {printf "%.1f", $2 / 1048576}' /proc/meminfo)
echo "MemAvailable: ${avail} GiB (IQ3_S needs ~50 GiB for its expert arena plus headroom)"

"$D/ram_watchdog.sh" 3 "$D/memory-samples.csv" &
WD=$!
trap 'kill $WD 2>/dev/null; pkill -P $$ 2>/dev/null || true' EXIT

cd "$STRATA"
# run-iq3_s.sh without --open (no browser tab)
.venv/bin/python serve/server.py --engine strata --config "$STRATA/strata-iq3_s.json" --port 8090 \
  2>&1 | tee "$D/server-$(date +%Y%m%d-%H%M%S).log"
