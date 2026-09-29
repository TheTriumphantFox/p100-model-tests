#!/usr/bin/env bash
# Continuation of drive_all.sh: g9v3 only.
#
# Written as a SEPARATE file rather than an edit to drive_all.sh: bash re-reads a
# running script by byte offset, and editing one in flight is what produced
# run-queue-6.sh.ABANDONED-corrupted-live-edit on 2026-09-20.
#
# Change from drive_all.sh: qwen3.8 is dropped from this run entirely. The
# uncensored Q6_K_P was swapped for unsloth Q8_0, then unsloth was pulled out to
# be scheduled separately -- see drive_unsloth.sh.
#
# g9v3 needs the fork build at ~/llama-cuda12-g9v3 (mainline reports "unknown
# model architecture: 'g9v3'"), and its graph aborts on a quantized KV cache
# (GGML_ASSERT(obj_new) in build_arch_graph), so f16 KV is mandatory here, not a
# preference.
#
# Models already at 115 results are skipped, so this is safe to re-run.
set -uo pipefail

T=~/Projects/Tests
RUN=$T/2026-09-22/devstral-tau-scripted
BM=~/llama-bench-models
PY=$T/.venv/bin/python
URL=http://127.0.0.1:8081/v1/chat/completions
TASKS=115
CTX=32768

log() { echo "[$(date +'%F %T')] $*" | tee -a "$RUN/driver.log"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }

stop_router() {
  local p i
  p=$(router_pid)
  [ -n "$p" ] && { kill "$p" 2>/dev/null; for i in $(seq 1 30); do sleep 2; [ -z "$(router_pid)" ] && break; done; }
  for c in $(ps -eo pid,args | grep '[l]lama-server --models-dir' | awk '{print $1}'); do kill "$c" 2>/dev/null; done
  for i in $(seq 1 60); do sleep 2; [ "$(gpu_mib)" -lt 1000 ] && break; done
  log "router stopped (was ${p:-none}); GPU $(gpu_mib) MiB"
}

start_router() {  # $1=build
  local i p
  nohup env LD_LIBRARY_PATH="$1/lib" "$1/bin/llama-server" \
    --models-dir "$BM" --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size $CTX --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 \
    >> "$RUN/router-8081.log" 2>&1 &
  for i in $(seq 1 90); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null 2>&1 && break; done
  p=$(router_pid); log "router started from $1 ctx=$CTX (pid ${p:-FAILED})"
  [ -n "$p" ]
}

complete() {
  [ -f "$1" ] || return 1
  $PY - "$1" "$TASKS" <<'EOF'
import json,sys
try: d=json.load(open(sys.argv[1]))
except Exception: sys.exit(1)
sys.exit(0 if len(d.get("results",[]))>=int(sys.argv[2]) else 1)
EOF
}

run_model() {
  local name=$1 slug=$2 extra=${3:-}
  local out=$RUN/retail_$slug.json
  if complete "$out"; then log "$slug: already complete, skipping"; return 0; fi
  log "$slug: starting $TASKS tasks (model=$name)"
  local t0=$SECONDS
  if [ -n "$extra" ]; then
    $PY "$RUN/run.py" --url "$URL" --model "$name" --tasks $TASKS --start 0 \
        --out "$out" --extra-body "$extra" >> "$RUN/$slug.log" 2>&1
  else
    $PY "$RUN/run.py" --url "$URL" --model "$name" --tasks $TASKS --start 0 \
        --out "$out" >> "$RUN/$slug.log" 2>&1
  fi
  log "$slug: finished rc=$? in $(( (SECONDS-t0)/60 ))m -- $(tail -2 "$RUN/$slug.log" | head -1)"
}

# ---------------------------------------------------------------- main
log "=== continuation: qwen3.8 dropped from this run; g9v3 only ==="
stop_router
start_router ~/llama-cuda12-g9v3 && run_model g9v3-39a5b_q4_k_m g9v3 \
  || log "g9v3: fork router would not start, skipped"

stop_router
systemctl --user start llama-devstral.service 2>/dev/null
log "=== continuation done; :8080 devstral service restored ==="

$PY "$RUN/summarise.py" 2>&1 | tee -a "$RUN/driver.log"
