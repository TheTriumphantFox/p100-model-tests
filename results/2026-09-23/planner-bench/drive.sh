#!/usr/bin/env bash
# AIOS planner benchmark, overnight: 40 tasks x 6 models, one model resident at a time.
#
# No time limit on any planning request: each runs to completion and the 120 s /
# 240 s deadlines are applied to measured wall time in summarise.py.
#
# Router setup matches the 2026-09-22 tau-bench run (ctx 32768 -- the R58 planner
# context target -- f16 KV, --models-max 1). g9v3 needs the fork build and runs
# first, on its own router; the rest share the mainline router.
#
# A model that is not fully GPU-resident at ctx 32768 is skipped, not run: a CPU
# spill makes wall times meaningless, and failing the 32k context target is
# itself the R58 answer for that model.
#
# Resumable at task granularity. Whatever happens, the EXIT trap stops the bench
# router and restarts the :8080 devstral service.
set -uo pipefail

T=~/Projects/Tests
RUN=$T/2026-09-23/planner-bench
BM=~/llama-bench-models
PY=$T/.venv/bin/python
CTX=32768
URL=http://127.0.0.1:8081/v1/chat/completions
NTASKS=$($PY -c "import json;print(len(json.load(open('$RUN/tasks.json'))['tasks']))" 2>/dev/null)
NOTHINK='{"chat_template_kwargs":{"enable_thinking":false}}'

mkdir -p "$RUN/results" "$RUN/logs"
log() { echo "[$(date +'%F %T')] $*" | tee -a "$RUN/logs/driver.log"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }

stop_router() {
  local p i c
  p=$(router_pid)
  [ -n "$p" ] && { kill "$p" 2>/dev/null; for i in $(seq 1 30); do sleep 2; [ -z "$(router_pid)" ] && break; done; }
  for c in $(ps -eo pid,args | grep '[l]lama-server --models-dir' | awk '{print $1}'); do kill "$c" 2>/dev/null; done
  for i in $(seq 1 60); do sleep 2; [ "$(gpu_mib)" -lt 1000 ] && break; done
  log "router stopped (was ${p:-none}); GPU $(gpu_mib) MiB"
}

start_router() {  # $1 = llama.cpp build dir
  local i p
  nohup env LD_LIBRARY_PATH="$1/lib" "$1/bin/llama-server" \
    --models-dir "$BM" --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size $CTX --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 \
    >> "$RUN/logs/router-8081.log" 2>&1 &
  for i in $(seq 1 90); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null 2>&1 && break; done
  p=$(router_pid); log "router started from $1 ctx=$CTX (pid ${p:-FAILED})"
  [ -n "$p" ]
}

restore() {
  stop_router
  systemctl --user start llama-devstral.service 2>/dev/null
  log "=== exit: bench router stopped, :8080 devstral service restarted ==="
}
trap restore EXIT
trap 'log "received signal, stopping"; exit 130' INT TERM

warm() {  # load the model; loading is not planning, so a generous bound is fine here
  curl -s -o /dev/null -w '%{http_code}' --max-time 1800 -X POST "$URL" \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$1\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":1,\"temperature\":0}"
}

complete() {
  $PY - "$1" "$NTASKS" <<'EOF' 2>/dev/null
import json,sys
try: d=json.load(open(sys.argv[1]))
except Exception: sys.exit(1)
sys.exit(0 if len(d.get("results",[]))>=int(sys.argv[2]) else 1)
EOF
}

run_model() {  # $1 = router model name, $2 = slug, $3 = build dir (for restart)
  local name=$1 slug=$2 build=$3 out=$RUN/results/$2.json code used sz attempt rc t0
  if complete "$out"; then log "$slug: already complete, skipping"; return 0; fi
  sz=$(du -Lm "$BM/$name.gguf" | cut -f1)
  code=$(warm "$name"); used=$(gpu_mib)
  log "$slug: load HTTP $code, weights ${sz} MiB, GPU ${used} MiB"
  if [ "$code" != "200" ]; then log "$slug: SKIPPED -- would not load at ctx $CTX"; return 0; fi
  if [ "$used" -lt "$sz" ]; then log "$slug: SKIPPED -- not fully GPU-resident at ctx $CTX (R58 target)"; return 0; fi
  for attempt in 1 2; do
    log "$slug: running $NTASKS tasks (attempt $attempt)"
    t0=$SECONDS
    $PY "$RUN/run.py" --url "$URL" --model "$name" --out "$out" --extra-body "$NOTHINK" \
        >> "$RUN/logs/$slug.log" 2>&1
    rc=$?
    log "$slug: run.py rc=$rc after $(( (SECONDS-t0)/60 ))m"
    [ $rc -ne 2 ] && break
    log "$slug: router unreachable, restarting it and resuming"
    stop_router; start_router "$build" || return 0
    warm "$name" >/dev/null
  done
}

# ---------------------------------------------------------------- main
[ -n "$NTASKS" ] || { echo "tasks.json missing"; exit 1; }
log "=== planner benchmark starting: $NTASKS tasks per model ==="
$PY "$RUN/selftest.py" >> "$RUN/logs/driver.log" 2>&1 || { log "FATAL: selftest failed, nothing run"; exit 1; }

systemctl --user stop llama-devstral.service 2>/dev/null
stop_router

if start_router ~/llama-cuda12-g9v3; then
  run_model g9v3-39a5b_q4_k_m g9v3 ~/llama-cuda12-g9v3
else
  log "g9v3: fork router would not start, skipped"
fi
stop_router

start_router ~/llama-cuda12 || { log "FATAL: mainline router would not start"; exit 1; }
run_model devstral-patched_q8_0          devstral ~/llama-cuda12
run_model gpt-oss-20b_q8_0               gptoss   ~/llama-cuda12
run_model ornith-1.5-35b-a3b_q4_k_m      ornith   ~/llama-cuda12
run_model qwen3.6-27b-abliterated_q5_k_m qwen36   ~/llama-cuda12
run_model qwen3.8-27b-unsloth_q8_0       qwen38   ~/llama-cuda12
# Added 2026-09-24: stock Qwen3.6 MoE, highest quant with comfortable VRAM headroom
run_model qwen3.6-35b-a3b_ud-q6_k        qwen36moe ~/llama-cuda12

$PY "$RUN/summarise.py" > /dev/null 2>> "$RUN/logs/driver.log"
log "=== all models done; RESULTS.md written ==="
