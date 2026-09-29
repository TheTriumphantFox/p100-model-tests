#!/usr/bin/env bash
# Round 2b, 2026-09-20. Replaces run-queue-6c.sh.
#
# What 6c got wrong, and why this file exists:
#   stop_router killed the ROUTER but not the per-model llama-server it had spawned. That
#   child holds the whole model in VRAM and takes ~20s more to die. 6c waited 5s, saw
#   24.5 GB still resident, WARNED, and started the next router anyway -- so ornith's model
#   server computed its offload plan against a nearly-full GPU, put ~16 GB of itself in
#   system RAM (RSS 21.7 GB, only 5.9 GB on the cards) and ran on CPU. This is the same
#   contamination that voided the first speculative-decoding pass, one level down.
#
#   Fixes: stop_router now kills the child model servers too and POLLS until the GPU is
#   actually free; fresh_router treats a dirty GPU as FATAL for that model, not a warning.
#   A wrong number is worse than a missing one.
#
# PHASE B: thinking ON, router ctx 16384, num_predict 12288. 4096 was too small -- 3 of
#   ornith's 14 batches burned the whole budget reasoning and emitted no answer (0/5 each),
#   reporting 70.00% for a run that was 89.09% among questions it actually answered.
#   Evidence kept in mmlu-ornith-think4096-TRUNCATED/.
# PHASE A: the three new Qwen3.8-27B quants at ctx 8192 -- they are scored against the
#   thinking-OFF shelf baselines, every one of which ran at 8192. Do not "improve" it.
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
  # The router's spawned per-model servers are what actually hold VRAM. Bracket the first
  # letter so this pattern can never match the shell that is running it.
  for c in $(ps -eo pid,args | grep '[l]lama-server --host 127.0.0.1 --jinja' | awk '{print $1}'); do
    kill "$c" 2>/dev/null
  done
  # Poll until the VRAM is genuinely released; a dying server can hold 24 GB for ~20s.
  for i in $(seq 1 60); do
    u=$(gpu_mib); [ "${u:-9999}" -lt 1000 ] && break
    sleep 2
  done
  log "router stopped (was pid ${p:-none}); GPU now $(gpu_mib) MiB after ${i}x2s"
}
start_router() {   # $1 = runtime dir, $2 = ctx size
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
# Verify the model actually landed on the GPU rather than silently spilling to system RAM.
assert_on_gpu() {   # $1 = minimum MiB we expect resident
  sleep 5
  u=$(gpu_mib)
  if [ "${u:-0}" -lt "$1" ]; then
    log "!!! RIG-FAIL: only ${u} MiB on the GPU, expected >= $1 -- model spilled to CPU."
    return 1
  fi
  log "model resident: ${u} MiB on GPU"; return 0
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

log "================ QUEUE-6D START ================"
log "shims: $(ss -ltnH 'sport = :11500 or sport = :11501' | awk '{print $4}' | paste -sd' ')"

# ============ PHASE B: thinking ON, ctx 16384 / num_predict 12288 ======================
log "--- PHASE B: thinking-on MMLU-Pro (ctx 16384, num_predict 12288) ---"
if fresh_router ~/llama-cuda12 ornith-1.5-35b-a3b_q4_k_m 16384; then
  assert_shim_tag 'ornith-1.5-35b-a3b:q4_k_m' 11501 \
    && "$RUN/bench_think.sh" 'ornith-1.5-35b-a3b:q4_k_m' ornith 12288 16384
fi
if fresh_router ~/llama-cuda12 nemotron-cascade-2-30b-a3b_q4_k_m 16384; then
  "$RUN/bench_think.sh" 'nemotron-cascade-2-30b-a3b:q4_k_m' nemotron 12288 16384
fi
if fresh_router ~/llama-cuda12-xing xing4.0-29b-a4b_iq4_nl 16384; then
  "$RUN/bench_think.sh" 'xing4.0-29b-a4b:iq4_nl' xing 12288 16384
fi
if fresh_router ~/llama-cuda12-g9v3 g9v3-39a5b_q4_k_m 16384; then
  "$RUN/bench_think.sh" 'g9v3-39a5b:q4_k_m' g9v3 12288 16384
fi
log "--- PHASE B COMPLETE ---"

# ============ PHASE A: the three new Qwen3.8-27B quants, ctx 8192 ======================
# All dense: 20.0 / 24.9 / 27.7 GB active per token -> ~11 tok/s, 60-110 min per HumanEval.
runA() { # $1 router-id  $2 tag  $3 slug  $4 min-MiB-expected-on-gpu
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
log "================ QUEUE-6D DONE ================"
