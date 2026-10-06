#!/usr/bin/env bash
# Phase 2 of the Flash-Next full run: Aider Polyglot, first 50 exercises in the fixed
# 2026-10-01 order (comparable with the top-3 table there), whole edit format, thinking off,
# 2 tries, :8081 bench router at ctx 16384 f16 exactly as aider-polyglot-10h/drive.sh ran it,
# except --fit is left on (default) because the 75 GB model must keep experts in RAM.
# Waits for phase 1 (flash-next-full.service) to finish first. Hard deadline 06:15 so the
# report is ready by 07:00; polyglot_run.py does not start an exercise it cannot finish.
set -uo pipefail
R=$(cd "$(dirname "$0")" && pwd)
B=/home/hm/llama-cuda12
M=qwen3.8-flash-next_iq2_xxs
DEADLINE=$(date -d "${DEADLINE_AT:-tomorrow 06:15}" +%s)
EST=${EST:-300}
log() { echo "[$(date +'%F %T')] $*" | tee -a "$R/driver.log"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }

log "=== phase 2 armed; deadline $(date -d @$DEADLINE +'%F %T')"
while systemctl --user is-active --quiet flash-next-full.service; do sleep 30; done
log "phase 1 finished; waiting for its router to release the GPU"
for _ in $(seq 1 60); do [ -z "$(router_pid)" ] && [ "$(gpu_mib)" -lt 1000 ] && break; sleep 5; done
if [ -n "$(router_pid)" ] || [ "$(gpu_mib)" -ge 1000 ]; then
  log "!!! GPU not free (router $(router_pid), $(gpu_mib) MiB) -- not starting"; exit 2
fi

nohup env LD_LIBRARY_PATH="$B/lib" "$B/bin/llama-server" \
  --models-dir /home/hm/llama-bench-models --models-autoload --models-max 1 \
  --host 127.0.0.1 --port 8081 --ctx-size 16384 --split-mode layer \
  --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
  --parallel 1 --batch-size 512 --ubatch-size 512 >> "$R/router-8081.log" 2>&1 &
RP=$!
for _ in $(seq 1 60); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null && break; done
log "router started (pid $RP)"
trap 'kill $RP 2>/dev/null' EXIT

out=$(python3 "$R/probe.py" "$M" 64 2>&1); echo "$out" >> "$R/preflight.jsonl"
if ! python3 -c 'import json,sys; sys.exit(0 if json.loads(sys.argv[1]).get("ok") else 1)' "$out" 2>/dev/null; then
  log "!!! preflight failed: $out"; exit 3
fi
log "preflight OK: $out"

CTR_NAME=polyglot-flashnext R="$R" "$R/ctr.sh" python3 /scripts/polyglot_run.py run --order /run/order.txt \
  --model-id "$M" --outdir "/run/runs/$M" --settings /run/models.yml \
  --metadata /run/model-metadata.json --start 0 --end "${END_IDX:-50}" --deadline "$DEADLINE" \
  --est-secs "$EST" --commit-hash 5dc9490 >> "$R/runs/$M.stdout" 2>&1
log "polyglot rc=$?, $(wc -l < "$R/runs/$M/progress.jsonl" 2>/dev/null || echo 0) exercises scored"
kill $RP 2>/dev/null; wait $RP 2>/dev/null
log "=== phase 2 done"
