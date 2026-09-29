#!/usr/bin/env bash
# GPU driver for the rig: frees the GPUs, serves ~/llama-bench-models on :8081, runs
# rig.py with the given arguments, and restores the :8080 devstral service on exit.
#
#   ./drive.sh --config v8-qwen36moe.json --config qwen36moe-full-self.json --suite flows --name evening
#
# Router settings match the planner benchmark: ctx 32768 (the R58 planner target), f16 KV,
# layer split, --models-max 1. A config that mixes models therefore pays a real unload and
# load whenever the role changes model; the report counts those switches.
# g9v3 needs its fork build (~/llama-cuda12-g9v3) and is not served by this router.
set -uo pipefail

T=~/Projects/Tests
RIG=$T/rig
BM=~/llama-bench-models
PY=$T/.venv/bin/python
BUILD=${BUILD:-~/llama-cuda12}
LOG=$RIG/logs
mkdir -p "$LOG"
log() { echo "[$(date +'%F %T')] $*" | tee -a "$LOG/drive.log"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }

stop_router() {
  local p i
  p=$(router_pid)
  [ -n "$p" ] && { kill "$p" 2>/dev/null; for i in $(seq 1 30); do sleep 2; [ -z "$(router_pid)" ] && break; done; }
  for i in $(seq 1 60); do [ "$(gpu_mib)" -lt 1000 ] && break; sleep 2; done
  log "router stopped (was ${p:-none}); GPU $(gpu_mib) MiB"
}

restore() {
  stop_router
  systemctl --user start llama-devstral.service 2>/dev/null
  log "=== exit: bench router stopped, :8080 devstral service restarted ==="
}

# A fixed run name, so the resume after a router restart continues the same run folder.
case " $* " in *" --name "*) ;; *) set -- "$@" --name "drive-$(date +%H-%M)";; esac

$PY "$RIG/selftest.py" >> "$LOG/drive.log" 2>&1 || { log "FATAL: selftest failed, nothing run"; exit 1; }

trap restore EXIT
trap 'log "received signal, stopping"; exit 130' INT TERM
systemctl --user stop llama-devstral.service 2>/dev/null
stop_router
if [ "$(gpu_mib)" -ge 1000 ]; then
  log "FATAL: $(gpu_mib) MiB still held on the GPUs by something else:"
  nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv | tee -a "$LOG/drive.log"
  exit 1
fi

nohup env LD_LIBRARY_PATH="$BUILD/lib" "$BUILD/bin/llama-server" \
  --models-dir "$BM" --models-autoload --models-max 1 \
  --host 127.0.0.1 --port 8081 --ctx-size 32768 --split-mode layer \
  --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
  --parallel 1 --batch-size 512 --ubatch-size 512 \
  >> "$LOG/router-8081.log" 2>&1 &
for i in $(seq 1 90); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null 2>&1 && break; done
[ -n "$(router_pid)" ] || { log "FATAL: router did not start (see $LOG/router-8081.log)"; exit 1; }
log "router up (pid $(router_pid)); running: rig.py run $*"

for attempt in 1 2; do
  $PY "$RIG/rig.py" run "$@" 2>&1 | tee -a "$LOG/drive.log"
  rc=${PIPESTATUS[0]}
  log "rig.py rc=$rc"
  [ "$rc" -ne 2 ] && break
  log "router unreachable; restarting it once and resuming"
  stop_router
  nohup env LD_LIBRARY_PATH="$BUILD/lib" "$BUILD/bin/llama-server" \
    --models-dir "$BM" --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size 32768 --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 \
    >> "$LOG/router-8081.log" 2>&1 &
  for i in $(seq 1 90); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null 2>&1 && break; done
done
