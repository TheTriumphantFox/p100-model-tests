#!/usr/bin/env bash
# Round 2b tail 2: re-run qwen3.8-27b-stock thinking-on with a client timeout that fits.
#
# Its first clean attempt scored 80.00% but lost `engineering` and `law` to
# "TimeoutError: timed out" with eval_count=0 -- the MMLU harness defaults to
# --api-timeout 900s and a 12288-token budget at this model's 12.0 tok/s needs ~1024s. The
# model was still generating when the client hung up. That is a rig failure, and it matters
# here: 93.33% among the 60 questions it did answer is the highest of any model in the
# column, so the two lost batches may be hiding a result above the incumbent's 87.14%.
# bench_think.sh now takes an api_timeout argument (default 2400).
#
# Only the slow dense models are exposed: at 53 tok/s a full budget takes 232s. The
# incumbent (11.0 tok/s) escaped only because its longest batch was 7014 tokens.
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-09-19/candidates-round2
BM=~/llama-bench-models
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

log "================ QUEUE-9 START ================"
stop_router
start_router ~/llama-cuda12 16384 || { log "!!! RIG-FAIL: router would not start"; exit 1; }
"$RUN/bench_think.sh" 'qwen3.8-27b-stock:q4_k_m' qwen38-27b 12288 16384 2400
log "--- THINKING-ON COLUMN COMPLETE (retimed) ---"
python3 "$RUN/summarise_think.py" 2>&1 | tee -a "$RUN/driver.log"
stop_router
start_router ~/llama-cuda12 8192
log "================ QUEUE-9 DONE ================"
