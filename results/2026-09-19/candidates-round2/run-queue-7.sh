#!/usr/bin/env bash
# Round 2b, 2026-09-20 — resumed after a manual pause. One driver for everything left.
#
#   B1  thinking-on MMLU-Pro for the 2 candidates that did not finish: xing, g9v3
#   B2  thinking-on MMLU-Pro for the 2 SHELF references, so the thinking-on column has a
#       baseline at all (ornith's 81.43% was being read against the incumbent's 71.43%,
#       which is a thinking-OFF number). Dense, 11-12 tok/s, budget 60-90 min each.
#   A   the 3 new Qwen3.8-27B quants from ~/Downloads/Models, thinking-OFF at ctx 8192 to
#       match the shelf baselines they are scored against. Dense: 20.0/24.9/27.7 GB active
#       per token -> ~11 tok/s, 60-110 min per HumanEval. Two are Q6_K, recorded as the
#       worst quant on GP100; they may land slower than the larger Q8_0.
#
# ornith and nemotron thinking-on are already banked (14/14 batches) and bench_think.sh
# skips any run whose results.json is complete, so re-running this file is safe.
#
# Hard-won rules encoded here:
#   * match processes by PID from $!, or by a bracketed pattern ('[l]lama-server'). A bare
#     pgrep/pkill -f matches the shell running it and any watcher that mentions it.
#   * stop_router must kill the per-model CHILD servers and POLL until VRAM is released;
#     the child holds the whole model ~20s after the parent dies. Loading onto a dirty GPU
#     makes llama.cpp silently leave most layers in system RAM and run on CPU.
#   * `bc` is not installed on this box -> awk.
#   * never edit this file while it is running; bash reads it by offset.
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
start_router() {   # $1 runtime dir, $2 ctx
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
fresh_router() {   # $1 runtime, $2 router-id, $3 ctx
  stop_router
  u=$(gpu_mib)
  if [ "${u:-0}" -gt 1500 ]; then
    log "!!! RIG-FAIL: ${u} MiB still on the GPU; refusing to load '$2' onto a dirty GPU."
    return 1
  fi
  start_router "$1" "$3" || return 1
  assert_listed "$2"
}

log "================ QUEUE-7 START (resumed) ================"
log "shims: $(ss -ltnH 'sport = :11500 or sport = :11501' | awk '{print $4}' | paste -sd' ')"

# ---- B1: finish the candidates -------------------------------------------------------
log "--- B1: thinking-on, remaining candidates (ctx 16384, np 12288) ---"
if fresh_router ~/llama-cuda12-xing xing4.0-29b-a4b_iq4_nl 16384; then
  assert_shim_tag 'xing4.0-29b-a4b:iq4_nl' 11501 \
    && "$RUN/bench_think.sh" 'xing4.0-29b-a4b:iq4_nl' xing 12288 16384
fi
if fresh_router ~/llama-cuda12-g9v3 g9v3-39a5b_q4_k_m 16384; then
  "$RUN/bench_think.sh" 'g9v3-39a5b:q4_k_m' g9v3 12288 16384
fi

# ---- B2: the thinking-on baselines ---------------------------------------------------
log "--- B2: thinking-on, shelf baselines (ctx 16384, np 12288) ---"
if fresh_router ~/llama-cuda12 qwen3.6-27b-abliterated_q5_k_m 16384; then
  assert_shim_tag 'qwen3.6-27b-abliterated:q5_k_m' 11501 \
    && "$RUN/bench_think.sh" 'qwen3.6-27b-abliterated:q5_k_m' qwen36-rerun 12288 16384
fi
if fresh_router ~/llama-cuda12 qwen3.8-27b-stock_q4_k_m 16384; then
  "$RUN/bench_think.sh" 'qwen3.8-27b-stock:q4_k_m' qwen38-27b 12288 16384
fi
log "--- THINKING-ON COLUMN COMPLETE ---"
python3 "$RUN/summarise_think.py" 2>&1 | tee -a "$RUN/driver.log"

# ---- A: the three new quants ---------------------------------------------------------
runA() {   # $1 router-id, $2 tag, $3 slug
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
log "================ QUEUE-7 DONE ================"
