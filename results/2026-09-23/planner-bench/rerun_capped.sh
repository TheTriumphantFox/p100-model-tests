#!/usr/bin/env bash
# Re-run every task that stopped at the old 16384-token cap, with no cap.
#
# The first overnight run (2026-09-23 21:00) passed max_tokens 16384. For
# gpt-oss that budget includes reasoning tokens, so long reasoning on large
# files ran out before any content was written -- a cut-off answer, not a model
# failure. run.py no longer sends a cap; this finds the capped results, moves
# them to "superseded" (kept, not deleted), and re-runs drive.sh, which skips
# complete models and resumes the rest at task granularity.
#
# Waits for planner-bench.service to finish first, so it never competes for the GPU.
set -uo pipefail

RUN=~/Projects/Tests/2026-09-23/planner-bench
PY=~/Projects/Tests/.venv/bin/python
log() { echo "[$(date +'%F %T')] rerun: $*" | tee -a "$RUN/logs/driver.log"; }

while systemctl --user is-active --quiet planner-bench.service; do sleep 60; done
log "main run finished; looking for results cut off by the old token cap"

n=$($PY - "$RUN/results" <<'EOF'
import json, os, sys, glob
total = 0
for f in glob.glob(os.path.join(sys.argv[1], "*.json")):
    d = json.load(open(f))
    keep, capped = [], []
    for r in d["results"]:
        # Old records have no max_tokens field and ran under the 16384 cap.
        if r.get("finish_reason") == "length" and r.get("max_tokens", 16384):
            capped.append(r)
        else:
            keep.append(r)
    if capped:
        d.setdefault("superseded", []).extend(dict(r, superseded_because="16384-token cap") for r in capped)
        d["results"] = keep
        json.dump(d, open(f + ".tmp", "w"), ensure_ascii=False, indent=1)
        os.replace(f + ".tmp", f)
        print(f"{os.path.basename(f)}: {[r['id'] for r in capped]}", file=sys.stderr)
        total += len(capped)
print(total)
EOF
)
if [ "${n:-0}" -eq 0 ]; then log "nothing was capped; done"; exit 0; fi
log "$n capped result(s) moved to 'superseded'; re-running them with no token cap"
exec "$RUN/drive.sh"
