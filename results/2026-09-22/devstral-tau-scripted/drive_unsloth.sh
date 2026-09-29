#!/usr/bin/env bash
# tau-bench retail, 115 tasks, qwen3.8-27b-unsloth_q8_0 (stock Qwen3.8-27B, Q8_0).
#
# Pulled out of the 2026-09-22 overnight run to be scheduled on its own. Writes
# into the same folder and is picked up by summarise.py alongside the rest.
#
# The 27.7 GB weight size is the thing to watch. The Q6_K_P it replaced is
# 24.7 GB and sat at 27 GB of 32 GB resident with ctx 32768 f16 KV, so the extra
# 3 GB may not fit -- and llama.cpp does not fail when it doesn't, it silently
# offloads layers to CPU and runs roughly an order of magnitude slower (see
# run-queue-6c.sh.SUPERSEDED-cpu-spill). The model is therefore loaded, measured
# against its own weight size, and dropped to ctx 16384 if it is not fully
# resident. Peak observed tau-bench transcript is ~7.2k tokens, so 16384 still
# leaves better than 2x headroom; a fallback is logged as a config difference.
#
# Re-runnable: skips the model if its JSON already holds 115 results.
set -uo pipefail

T=~/Projects/Tests
RUN=$T/2026-09-22/devstral-tau-scripted
BM=~/llama-bench-models
PY=$T/.venv/bin/python
URL=http://127.0.0.1:8081/v1/chat/completions
TASKS=115
MODEL=qwen3.8-27b-unsloth_q8_0
SLUG=qwen38unsloth
NOTHINK='{"chat_template_kwargs":{"enable_thinking":false}}'

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

start_router() {  # $1=ctx
  local i p
  nohup env LD_LIBRARY_PATH=~/llama-cuda12/lib ~/llama-cuda12/bin/llama-server \
    --models-dir "$BM" --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size "$1" --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 \
    >> "$RUN/router-8081.log" 2>&1 &
  for i in $(seq 1 90); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null 2>&1 && break; done
  p=$(router_pid); log "router started ctx=$1 (pid ${p:-FAILED})"
  [ -n "$p" ]
}

warm() {
  curl -s -o /dev/null -w '%{http_code}' --max-time 1200 -X POST "$URL" \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":1,\"temperature\":0}"
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

# ---------------------------------------------------------------- main
OUT=$RUN/retail_$SLUG.json
if complete "$OUT"; then log "$SLUG: already complete, nothing to do"; exit 0; fi

log "=== unsloth q8_0 standalone run starting ==="
systemctl --user stop llama-devstral.service 2>/dev/null
stop_router

SZ=$(du -Lm "$BM/$MODEL.gguf" | cut -f1)
CTX=32768
start_router $CTX || { log "FATAL: router would not start"; exit 1; }
code=$(warm); used=$(gpu_mib)
log "$MODEL: weights ${SZ} MiB, HTTP $code, GPU ${used} MiB at ctx $CTX"

if [ "$code" != "200" ] || [ "$used" -lt "$SZ" ]; then
  log "$MODEL: NOT fully resident at ctx $CTX (need >= ${SZ} MiB, got ${used}) -- dropping to 16384"
  CTX=16384
  stop_router
  start_router $CTX || { log "FATAL: router would not start at ctx $CTX"; exit 1; }
  code=$(warm); used=$(gpu_mib)
  log "$MODEL: HTTP $code, GPU ${used} MiB at ctx $CTX"
fi

if [ "$code" = "200" ]; then
  log "$SLUG: starting $TASKS tasks (model=$MODEL, ctx=$CTX)"
  t0=$SECONDS
  $PY "$RUN/run.py" --url "$URL" --model "$MODEL" --tasks $TASKS --start 0 \
      --out "$OUT" --extra-body "$NOTHINK" >> "$RUN/$SLUG.log" 2>&1
  log "$SLUG: finished rc=$? in $(( (SECONDS-t0)/60 ))m -- $(tail -2 "$RUN/$SLUG.log" | head -1)"
else
  log "FATAL: $MODEL will not serve at any tested ctx"
fi

stop_router
systemctl --user start llama-devstral.service 2>/dev/null
log "=== unsloth run done; :8080 devstral service restored ==="

$PY "$RUN/summarise.py" 2>&1 | tee -a "$RUN/driver.log"
