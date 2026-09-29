#!/usr/bin/env bash
# Round 2, part 2. Waits for the production-build queue, fills in the MMLU-Pro 2048
# passes it skipped, then swaps the router binary for each out-of-tree architecture.
# Router pid is found via the listening socket - `pkill -f llama-server` would match
# this script's own shell (see [[pkill-self-match-pitfall]]).
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-09-19/candidates-round2
DL=/var/lib/ollama/candidates-r2
BM=~/llama-bench-models
log() { echo "[$(date +%T)] $*" | tee -a "$RUN/driver.log"; }

router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
stop_router() {
  p=$(router_pid); [ -n "$p" ] && { kill "$p"; for i in $(seq 1 60); do sleep 2; [ -z "$(router_pid)" ] && break; done; }
  log "router stopped (was pid ${p:-none})"
}
start_router() { # $1 = runtime dir
  nohup env LD_LIBRARY_PATH=$1/lib $1/bin/llama-server \
    --models-dir $BM --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size 8192 --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 >> "$RUN/router-8081.log" 2>&1 &
  for i in $(seq 1 60); do sleep 2; [ -n "$(router_pid)" ] && break; done
  log "router started from $1 (commit $(cat $1/LLAMA_COMMIT | cut -c1-12), pid $(router_pid))"
}

# 0. wait for the production-build queue
for i in $(seq 1 2000); do grep -q "QUEUE DONE" "$RUN/driver.log" && break; sleep 20; done
log "FORK QUEUE START"

# 1. the MMLU-Pro 2048 passes bench_one.sh skipped (reasoning models parsed fine at 96,
#    so its escalation never triggered - but 96 gives them no room to think)
for pair in "ornith-1.5-35b-a3b:q4_k_m ornith" \
            "nemotron-cascade-2-30b-a3b:q4_k_m nemotron" \
            "qwen3.6-27b-abliterated:q5_k_m qwen36-rerun"; do
  set -- $pair
  [ -f "$BM/${1%%:*}"* ] 2>/dev/null || true
  "$RUN/bench_one2.sh" "$1" "$2" skip skip only2048
done

# 2. Xing4.0 - arch xing4_0, open PR ggml-org/llama.cpp#29141
F="$DL/xing4_0-29b-IQ4_NL.gguf"
for i in $(seq 1 180); do [ -f "$F" ] && break; sleep 20; done
if [ -f "$F" ]; then
  ln -sf "$F" "$BM/xing4.0-29b-a4b_iq4_nl.gguf"
  stop_router; start_router ~/llama-cuda12-xing
  "$RUN/bench_one2.sh" 'xing4.0-29b-a4b:iq4_nl' xing
else log "xing download never arrived"; fi

# 3. G9v3 - arch g9v3, linuxid10t/llama.cpp:feature/g9v3-support
F="$DL/G9v3-39A5B-Q4_K_M.gguf"
for i in $(seq 1 360); do [ -f "$F" ] && break; sleep 20; done
if [ -f "$F" ]; then
  ln -sf "$F" "$BM/g9v3-39a5b_q4_k_m.gguf"
  stop_router; start_router ~/llama-cuda12-g9v3
  "$RUN/bench_one2.sh" 'g9v3-39a5b:q4_k_m' g9v3
else log "g9v3 download never arrived"; fi

# 4. leave the rig on the production build
stop_router; start_router ~/llama-cuda12
log "FORK QUEUE DONE"
