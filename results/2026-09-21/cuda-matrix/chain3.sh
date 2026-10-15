#!/usr/bin/env bash
# SECURITY: historical driver; may stop services, kill processes, or edit live presets.
if [ "${P100_ALLOW_ARCHIVED_DRIVER:-}" != "1" ]; then
  printf '%s\n' 'Refusing archived driver. Review SECURITY.md; explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 only in a disposable test environment.' >&2
  exit 2
fi
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
