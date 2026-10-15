#!/usr/bin/env bash
# SECURITY: historical driver; may stop services, kill processes, or edit live presets.
if [ "${P100_ALLOW_ARCHIVED_DRIVER:-}" != "1" ]; then
  printf '%s\n' 'Refusing archived driver. Review SECURITY.md; explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 only in a disposable test environment.' >&2
  exit 2
fi
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=${1:-}
[ -n "$W" ] && { echo "[$(date '+%m-%d %T')] chain4: waiting for repro (pid $W)" | tee -a "$HERE/driver.log"
                 while kill -0 "$W" 2>/dev/null; do sleep 30; done; }
"$HERE/finalize.sh"
