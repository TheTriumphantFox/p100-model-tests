#!/usr/bin/env bash
# Pinned-checks pass: the same 40 tasks, with the check sequence fixed in the grammar
# (bench.response_schema(pin_checks=True)) -- the proposed spec variant. Everything else
# is identical to drive.sh: prompt, router config, sampling, no token or time cap.
#
# Models: the two Qwen MoEs, which both dropped the second check in the unpinned run.
# Results: results/<slug>-pinned.json, next to the unpinned ones.
#
# Waits for any other planner-bench unit to finish first, so it never competes for the
# GPU. A grammar the server refuses aborts the model (run.py rc=3); there is no
# unconstrained fallback in this pass. The EXIT trap restores the :8080 service.
set -uo pipefail

T=~/Projects/Tests
RUN=$T/2026-09-23/planner-bench
BM=~/llama-bench-models
PY=$T/.venv/bin/python
URL=http://127.0.0.1:8081/v1/chat/completions
NTASKS=$($PY -c "import json;print(len(json.load(open('$RUN/tasks.json'))['tasks']))" 2>/dev/null)
NOTHINK='{"chat_template_kwargs":{"enable_thinking":false}}'

log() { echo "[$(date +'%F %T')] pinned: $*" | tee -a "$RUN/logs/driver.log"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }

stop_router() {
  local p i c
  p=$(router_pid)
  [ -n "$p" ] && { kill "$p" 2>/dev/null; for i in $(seq 1 30); do sleep 2; [ -z "$(router_pid)" ] && break; done; }
  for c in $(ps -eo pid,args | grep '[l]lama-server --models-dir' | awk '{print $1}'); do kill "$c" 2>/dev/null; done
  for i in $(seq 1 60); do sleep 2; [ "$(gpu_mib)" -lt 1000 ] && break; done
  log "router stopped; GPU $(gpu_mib) MiB"
}

restore() {
  stop_router
  systemctl --user start llama-devstral.service 2>/dev/null
  log "=== exit: :8080 devstral service restarted ==="
}

for u in planner-bench planner-bench-rerun planner-bench-qwen36moe; do
  while systemctl --user is-active --quiet "$u.service"; do sleep 30; done
done

trap restore EXIT
trap 'log "received signal, stopping"; exit 130' INT TERM
log "=== pinned-checks pass starting ==="
$PY "$RUN/selftest.py" >> "$RUN/logs/driver.log" 2>&1 || { log "FATAL: selftest failed"; exit 1; }

systemctl --user stop llama-devstral.service 2>/dev/null
stop_router
nohup env LD_LIBRARY_PATH=~/llama-cuda12/lib ~/llama-cuda12/bin/llama-server \
  --models-dir "$BM" --models-autoload --models-max 1 \
  --host 127.0.0.1 --port 8081 --ctx-size 32768 --split-mode layer \
  --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
  --parallel 1 --batch-size 512 --ubatch-size 512 >> "$RUN/logs/router-8081.log" 2>&1 &
for i in $(seq 1 90); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null && break; done
[ -n "$(router_pid)" ] || { log "FATAL: router would not start"; exit 1; }

run_pinned() {  # $1 = router model name, $2 = slug
  local out=$RUN/results/$2-pinned.json code used sz rc t0
  sz=$(du -Lm "$BM/$1.gguf" | cut -f1)
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 1800 -X POST "$URL" -H 'Content-Type: application/json' \
    -d "{\"model\":\"$1\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":1}")
  used=$(gpu_mib)
  log "$2: load HTTP $code, weights ${sz} MiB, GPU ${used} MiB"
  if [ "$code" != 200 ] || [ "$used" -lt "$sz" ]; then log "$2: SKIPPED -- not loaded or not fully resident"; return; fi
  log "$2-pinned: running $NTASKS tasks with the check sequence pinned"
  t0=$SECONDS
  $PY "$RUN/run.py" --url "$URL" --model "$1" --out "$out" --extra-body "$NOTHINK" --pin-checks \
      >> "$RUN/logs/$2-pinned.log" 2>&1
  rc=$?
  log "$2-pinned: run.py rc=$rc after $(( (SECONDS-t0)/60 ))m"
}

run_pinned qwen3.6-35b-a3b_ud-q6_k   qwen36moe
run_pinned ornith-1.5-35b-a3b_q4_k_m ornith

$PY "$RUN/summarise.py" > /dev/null 2>> "$RUN/logs/driver.log" && log "RESULTS.md updated" || log "summarise.py failed"
