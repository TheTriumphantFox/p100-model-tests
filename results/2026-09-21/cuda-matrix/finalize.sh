#!/usr/bin/env bash
# Runs after everything. Regenerates the dataset, writes FINAL.md, and stops the watchdog.
# Exists so the evening's first look is a finished document, not a log tail.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY=$HOME/Projects/Tests/.venv/bin/python
say() { echo "[$(date '+%m-%d %T')] finalize: $*" | tee -a "$HERE/driver.log"; }

say "regenerating the dataset"
"$HERE/DATASET.sh" > "$HERE/DATASET.txt" 2>&1

"$PY" "$HERE/make_final.py" > "$HERE/FINAL.md" 2>"$HERE/FINAL.err"
say "wrote FINAL.md"

# Stop the watchdog: it polls forever by design. Matched on the exact script path via ps,
# never pkill -f, which would also match this script's own command line.
for p in $(ps -eo pid,args | awk -v me=$$ '$1!=me && /[w]atchdog\.py/ {print $1}'); do
  kill "$p" 2>/dev/null && say "stopped watchdog pid $p"
done
say "================ ALL WORK COMPLETE ================"
