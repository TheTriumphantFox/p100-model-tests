#!/usr/bin/env bash
# SECURITY: historical driver; may stop services, kill processes, or edit live presets.
if [ "${P100_ALLOW_ARCHIVED_DRIVER:-}" != "1" ]; then
  printf '%s\n' 'Refusing archived driver. Review SECURITY.md; explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 only in a disposable test environment.' >&2
  exit 2
fi
# Restart of Strata + Flash-Next IQ3_S on :8090 with layer_split 36, STRATA_STAGE_TRIM=1 and
# expert_profile_save (2026-10-25), under the RAM watchdog. Unlike the 2026-10-12 launcher the
# server and watchdog are detached (setsid), so the server stays up for the pi pricing runs.
# Stop: kill $(cat watchdog.pid) and SIGTERM the server.py process.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
STRATA=/home/hm/AI/Strata

busy=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 > 1024')
if [ -n "$busy" ]; then
  echo "GPUs in use (index, MiB):"; echo "$busy"; exit 1
fi
echo "MemAvailable: $(awk '/^MemAvailable:/ {printf "%.1f", $2 / 1048576}' /proc/meminfo) GiB"

setsid nohup "$D/ram_watchdog.sh" 3 "$D/memory-samples.csv" >/dev/null 2>&1 </dev/null &
echo $! > "$D/watchdog.pid"
cd "$STRATA"
setsid nohup .venv/bin/python serve/server.py --engine strata --config "$STRATA/strata-iq3_s.json" --port 8090 \
  >"$D/server-$(date +%Y%m%d-%H%M%S).log" 2>&1 </dev/null &
echo "server pid $!"
