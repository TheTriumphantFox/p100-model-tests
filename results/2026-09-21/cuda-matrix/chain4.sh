#!/usr/bin/env bash
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=${1:-}
[ -n "$W" ] && { echo "[$(date '+%m-%d %T')] chain4: waiting for repro (pid $W)" | tee -a "$HERE/driver.log"
                 while kill -0 "$W" 2>/dev/null; do sleep 30; done; }
"$HERE/finalize.sh"
