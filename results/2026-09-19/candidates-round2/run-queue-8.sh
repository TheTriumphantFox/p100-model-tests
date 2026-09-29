#!/usr/bin/env bash
# Round 2b tail: re-run the ONE thinking-on baseline that failed.
#
# qwen3.8-27b-stock's first attempt returned 0.0% in 94s: the shim's --force-think path set
# reasoning_effort="high", and the Qwen3.8 chat template VALIDATES that field against
# ('xhigh','medium','low') and raises a Jinja exception -> router 500 on every request. The
# five models already measured do not reference reasoning_effort in their templates at all,
# so the field was a no-op for them; the shim now omits it entirely, which leaves those five
# unchanged and lets Qwen3.8 use its own default depth (xhigh). Void run deleted.
#
# Waits for run-queue-7.sh (Phase A) by PID so it never competes for the GPU.
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-09-19/candidates-round2
BM=~/llama-bench-models
Q7=$1
log() { echo "[$(date +%T)] $*" | tee -a "$RUN/driver.log"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }
stop_router() {
  p=$(router_pid)
  [ -n "$p" ] && { kill "$p" 2>/dev/null; for i in $(seq 1 30); do sleep 2; [ -z "$(router_pid)" ] && break; done; }
  for c in $(ps -eo pid,args | grep '[l]lama-server --host 127.0.0.1 --jinja' | awk '{print $1}'); do kill "$c" 2>/dev/null; done
  for i in $(seq 1 60); do u=$(gpu_mib); [ "${u:-9999}" -lt 1000 ] && break; sleep 2; done
  log "router stopped (was pid ${p:-none}); GPU now $(gpu_mib) MiB after ${i}x2s"
}
start_router() {
  nohup env LD_LIBRARY_PATH=$1/lib $1/bin/llama-server \
    --models-dir $BM --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size $2 --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 >> "$RUN/router-8081.log" 2>&1 &
  for i in $(seq 1 90); do sleep 2; [ -n "$(router_pid)" ] && break; done
  p=$(router_pid); log "router started from $1 ctx=$2 (pid ${p:-FAILED-TO-START})"; [ -n "$p" ]
}

while kill -0 "$Q7" 2>/dev/null; do sleep 60; done
log "================ QUEUE-8 START (queue-7 finished) ================"

# Prove the fix before spending an hour on it: one request through :11501 must come back 200.
probe=$(curl -sf --max-time 60 -X POST http://127.0.0.1:11501/api/tags -o /dev/null -w '%{http_code}' 2>/dev/null || echo fail)
log "shim :11501 reachable: $probe"

stop_router
start_router ~/llama-cuda12 16384 || { log "!!! RIG-FAIL: router would not start"; exit 1; }
"$RUN/bench_think.sh" 'qwen3.8-27b-stock:q4_k_m' qwen38-27b 12288 16384
log "--- THINKING-ON COLUMN COMPLETE ---"
python3 "$RUN/summarise_think.py" 2>&1 | tee -a "$RUN/driver.log"
stop_router
start_router ~/llama-cuda12 8192
log "================ QUEUE-8 DONE ================"
