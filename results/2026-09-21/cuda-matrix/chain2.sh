#!/usr/bin/env bash
# SECURITY: historical driver; may stop services, kill processes, or edit live presets.
if [ "${P100_ALLOW_ARCHIVED_DRIVER:-}" != "1" ]; then
  printf '%s\n' 'Refusing archived driver. Review SECURITY.md; explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 only in a disposable test environment.' >&2
  exit 2
fi
# Run order after the priority ggml-org accuracy run:
#   1. process-test.sh  -- thinking-on at a context worth using, 10 questions, paths not scores
#   2. queue-1.sh       -- complete matrix rows for the four models with no CUDA numbers
#   3. queue-2.sh       -- context ladders, then the thinking-on cells that depend on them
# Waits on a PID, not a pattern: pgrep -f would match this shell too.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
WAIT_PID=${1:-}
say() { echo "[$(date '+%m-%d %T')] chain: $*" | tee -a "$HERE/driver.log"; }
if [ -n "$WAIT_PID" ]; then
  say "waiting for pid $WAIT_PID (priority run)"
  while kill -0 "$WAIT_PID" 2>/dev/null; do sleep 20; done
  say "pid $WAIT_PID finished"
fi
"$HERE/process-test.sh"; say "process-test rc=$?"
"$HERE/queue-1.sh";     say "queue-1 rc=$?"
"$HERE/queue-2.sh";     say "queue-2 rc=$?"
say "ALL QUEUES DONE"
