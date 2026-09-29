#!/usr/bin/env bash
# tau-bench retail (scripted user), five models, 115 tasks each.
#
# Sequential by necessity: the router runs --models-max 1 because 32 GB of VRAM
# does not hold two of these at once. Each model is loaded, scored, and unloaded
# before the next starts.
#
# g9v3 is the awkward one, in two ways. Its architecture is not in mainline
# llama.cpp ("unknown model architecture: 'g9v3'"), so it needs the fork build at
# ~/llama-cuda12-g9v3 and runs last, as run-queue-forks.sh did on 2026-09-20.
# Second, the fork's g9v3 graph aborts on a QUANTIZED KV cache
# (GGML_ASSERT(obj_new) in build_arch_graph) -- ctx size is not the problem,
# q8_0 is. Everything therefore runs f16 KV, which also keeps all five models on
# one identical config instead of special-casing one of them.
#
# Resumable: a model whose output JSON already holds 115 results is skipped, so
# re-running after an interruption picks up where it stopped.
set -uo pipefail

T=~/Projects/Tests
RUN=$T/2026-09-22/devstral-tau-scripted
BM=~/llama-bench-models
PY=$T/.venv/bin/python
CTX=32768
URL=http://127.0.0.1:8081/v1/chat/completions
TASKS=115

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

start_router() {
  local build=$1 i p
  nohup env LD_LIBRARY_PATH="$build/lib" "$build/bin/llama-server" \
    --models-dir "$BM" --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size $CTX --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 \
    >> "$RUN/router-8081.log" 2>&1 &
  for i in $(seq 1 90); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null 2>&1 && break; done
  p=$(router_pid); log "router started from $build ctx=$CTX (pid ${p:-FAILED})"
  [ -n "$p" ]
}

complete() {  # $1=json path -- already has all TASKS results?
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
  local rc=$? mins=$(( (SECONDS-t0)/60 ))
  log "$slug: finished rc=$rc in ${mins}m -- $(tail -2 "$RUN/$slug.log" | head -1)"
}

# ---------------------------------------------------------------- main
log "=== multi-model tau-bench retail run starting ==="
systemctl --user stop llama-devstral.service 2>/dev/null
stop_router

NOTHINK='{"chat_template_kwargs":{"enable_thinking":false}}'

start_router ~/llama-cuda12 || { log "FATAL: mainline router would not start"; exit 1; }
run_model devstral-patched_q8_0                   devstral
run_model gpt-oss-20b_q8_0                        gptoss
run_model qwen3.6-27b-abliterated_q5_k_m          qwen36      "$NOTHINK"
run_model qwen3.8-27b-uncensored-hauhaucs_q6_k_p  qwen38unc   "$NOTHINK"

stop_router
start_router ~/llama-cuda12-g9v3 && run_model g9v3-39a5b_q4_k_m g9v3 \
  || log "g9v3: fork router would not start, skipped"

stop_router
systemctl --user start llama-devstral.service 2>/dev/null
log "=== all models done; :8080 devstral service restored ==="

$PY "$RUN/summarise.py" 2>&1 | tee -a "$RUN/driver.log"
