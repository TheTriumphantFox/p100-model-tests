#!/usr/bin/env bash
# Hand drive_all.sh off to drive_rest.sh at the qwen3.6 -> qwen3.8 boundary.
#
# drive_all.sh has the uncensored Q6_K_P hard-coded and cannot be edited while it
# runs (bash re-reads a running script by byte offset). So instead: wait for
# qwen3.6 to reach a full 115 results, stop the original driver before or just
# after it moves on, and start the continuation that runs unsloth Q8_0 instead.
#
# Stopping earlier was not an option -- the resume check only skips a model at a
# full 115, so killing mid-qwen3.6 would have restarted it from task 0.
set -uo pipefail

RUN=~/Projects/Tests/2026-09-22/devstral-tau-scripted
PY=~/Projects/Tests/.venv/bin/python
log() { echo "[$(date +'%F %T')] swap: $*" | tee -a "$RUN/driver.log"; }

count() {
  $PY - "$RUN/retail_qwen36.json" <<'EOF' 2>/dev/null || echo 0
import json,sys
try: print(len(json.load(open(sys.argv[1]))["results"]))
except Exception: print(0)
EOF
}

log "watching for qwen3.6 to reach 115 results"
while [ "$(count)" -lt 115 ]; do
  systemctl --user is-active --quiet taubench-multimodel.service || {
    log "original driver is no longer active; proceeding to continuation"
    break
  }
  sleep 60
done
log "qwen3.6 at $(count)/115 -- stopping original driver"

systemctl --user stop taubench-multimodel.service 2>/dev/null
sleep 5
for c in $(ps -eo pid,args | grep '[d]rive_all.sh' | awk '{print $1}'); do kill "$c" 2>/dev/null; done
for c in $(ps -eo pid,args | grep '[r]un.py --url' | awk '{print $1}'); do kill "$c" 2>/dev/null; done
sleep 3

# Park any partial uncensored output rather than deleting it -- it is real data
# about a model that was dropped from the queue, and summarise.py would otherwise
# report a truncated run as if it were a result.
for f in "$RUN/retail_qwen38unc.json" "$RUN/qwen38unc.log"; do
  [ -f "$f" ] && { mv "$f" "$f.PARTIAL-superseded-by-unsloth"; log "parked $(basename "$f")"; }
done

log "launching drive_rest.sh (unsloth q8_0 + g9v3)"
exec "$RUN/drive_rest.sh"
