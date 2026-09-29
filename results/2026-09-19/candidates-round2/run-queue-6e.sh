#!/usr/bin/env bash
# Round 2b, 2026-09-20, part 3. Takes over from run-queue-6d.sh after its PHASE B.
#
# PHASE B2 (new): thinking-ON MMLU-Pro for the two SHELF references -- the incumbent and
#   qwen3.8-27b-stock. Without these the thinking-on column has no baseline: ornith's
#   81.43% was being read against the incumbent's 71.43%, which is a thinking-OFF number.
#   Both are dense (~11-12 tok/s) and thinking-on generates 40-60k tokens, so budget 60-90
#   min each. Same budget as the candidates -- ctx 16384, num_predict 12288 -- or the
#   column is not internally comparable.
# PHASE A: the three new Qwen3.8-27B quants at ctx 8192 (thinking-off, to match the shelf
#   baselines they are scored against). Unchanged from 6d.
#
# Inherits 6d's guards: child-server kill + VRAM poll in stop_router, FATAL dirty-GPU
# check in fresh_router, router/shim listing assertions.
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
  for c in $(ps -eo pid,args | grep '[l]lama-server --host 127.0.0.1 --jinja' | awk '{print $1}'); do
    kill "$c" 2>/dev/null
  done
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
  p=$(router_pid)
  log "router started from $1 ctx=$2 ($(cut -c1-12 $1/LLAMA_COMMIT 2>/dev/null), pid ${p:-FAILED-TO-START})"
  [ -n "$p" ]
}
assert_listed() {
  ids=$(curl -sf --max-time 30 http://127.0.0.1:8081/models | python3 -c 'import json,sys; print(" ".join(m["id"] for m in json.load(sys.stdin)["data"]))' 2>/dev/null)
  case " $ids " in *" $1 "*) return 0;; esac
  log "!!! RIG-FAIL: router does not list '$1'. Listed: $ids"; return 1
}
assert_shim_tag() {
  curl -sf --max-time 30 "http://127.0.0.1:$2/api/tags" | grep -q "\"$1\"" && return 0
  log "!!! RIG-FAIL: shim on :$2 does not advertise tag '$1'"; return 1
}
fresh_router() {
  stop_router
  u=$(gpu_mib)
  if [ "${u:-0}" -gt 1500 ]; then
    log "!!! RIG-FAIL: ${u} MiB still on the GPU; refusing to load '$2' onto a dirty GPU."
    return 1
  fi
  start_router "$1" "$3" || return 1
  assert_listed "$2"
}

log "================ QUEUE-6E START ================"

# ===== PHASE B2: thinking-on baselines, the two shelf references ======================
log "--- PHASE B2: thinking-on MMLU-Pro, shelf baselines (ctx 16384, np 12288) ---"
if fresh_router ~/llama-cuda12 qwen3.6-27b-abliterated_q5_k_m 16384; then
  assert_shim_tag 'qwen3.6-27b-abliterated:q5_k_m' 11501 \
    && "$RUN/bench_think.sh" 'qwen3.6-27b-abliterated:q5_k_m' qwen36-rerun 12288 16384
fi
if fresh_router ~/llama-cuda12 qwen3.8-27b-stock_q4_k_m 16384; then
  "$RUN/bench_think.sh" 'qwen3.8-27b-stock:q4_k_m' qwen38-27b 12288 16384
fi
log "--- PHASE B2 COMPLETE ---"
python3 "$RUN/summarise_think.py" 2>&1 | tee -a "$RUN/driver.log"

# ===== PHASE A: the three new Qwen3.8-27B quants, ctx 8192 ============================
runA() {
  log "--- PHASE A: $3 ---"
  if fresh_router ~/llama-cuda12 "$1" 8192 && assert_shim_tag "$2" 11500; then
    "$RUN/bench_one2.sh" "$2" "$3"
  else
    log "!!! SKIPPED $3: preflight failed"
  fi
}
runA qwen3.8-27b-unsloth_ud_q6_k               'qwen3.8-27b-unsloth:ud_q6_k'            qwen38-ud-q6k
runA qwen3.8-27b-uncensored-hauhaucs_q6_k_p    'qwen3.8-27b-uncensored-hauhaucs:q6_k_p' qwen38-uncensored-q6kp
runA qwen3.8-27b-unsloth_q8_0                  'qwen3.8-27b-unsloth:q8_0'               qwen38-unsloth-q8

stop_router
start_router ~/llama-cuda12 8192
log "================ QUEUE-6E DONE ================"
