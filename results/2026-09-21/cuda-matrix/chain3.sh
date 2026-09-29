#!/usr/bin/env bash
# Runs the reproducibility phase after the sweep finishes, per the owner's instruction to
# do it last. Waits on a PID, not a pattern.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=${1:-}
say() { echo "[$(date '+%m-%d %T')] chain3: $*" | tee -a "$HERE/driver.log"; }
if [ -n "$W" ]; then
  say "waiting for the sweep (pid $W) before the repro phase"
  while kill -0 "$W" 2>/dev/null; do sleep 30; done
  say "sweep finished"
fi
"$HERE/repro.sh"; say "repro rc=$?"
say "EVERYTHING DONE"
