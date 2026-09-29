#!/usr/bin/env bash
# Run the matrix queues back to back, after the priority ggml-org run finishes.
# Waits on the driver PID rather than a pattern: pgrep -f matches this shell too.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
WAIT_PID=${1:-}
if [ -n "$WAIT_PID" ]; then
  echo "[$(date '+%m-%d %T')] chain: waiting for pid $WAIT_PID" | tee -a "$HERE/driver.log"
  while kill -0 "$WAIT_PID" 2>/dev/null; do sleep 20; done
  echo "[$(date '+%m-%d %T')] chain: pid $WAIT_PID finished" | tee -a "$HERE/driver.log"
fi
"$HERE/queue-1.sh"
"$HERE/queue-2.sh"
echo "[$(date '+%m-%d %T')] chain: ALL QUEUES DONE" | tee -a "$HERE/driver.log"
