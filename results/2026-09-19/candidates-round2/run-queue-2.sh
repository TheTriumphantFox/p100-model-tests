#!/usr/bin/env bash
# Round 2, part 2 (replaces run-queue-forks.sh, which was killed).
#
# Two bugs in part 1 are corrected here:
#   1. `env VAR=x py ...` -> rc=127. `env` cannot run a shell function; call the
#      interpreter path. (Cost: the nemotron/qwen36 throughput runs.)
#   2. The llama.cpp router enumerates --models-dir ONCE AT STARTUP. A GGUF symlinked
#      in afterwards is invisible ("Requested model(s) not installed"), which is why
#      nemotron scored 0/0 in 2 seconds. Restart the router after adding a model.
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
start_router() {
  nohup env LD_LIBRARY_PATH=$1/lib $1/bin/llama-server \
    --models-dir $BM --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size 8192 --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 >> "$RUN/router-8081.log" 2>&1 &
  for i in $(seq 1 60); do sleep 2; [ -n "$(router_pid)" ] && break; done
  log "router started from $1 ($(cut -c1-12 $1/LLAMA_COMMIT), pid $(router_pid))"
}

for i in $(seq 1 3000); do grep -q "QUEUE DONE" "$RUN/driver.log" && break; sleep 20; done
log "QUEUE-2 START"

# Nemotron-Cascade-2: symlink already in place, router just needs to see it
stop_router; start_router ~/llama-cuda12
"$RUN/bench_one2.sh" 'nemotron-cascade-2-30b-a3b:q4_k_m' nemotron

# the 2048-budget MMLU passes part 1 skipped, plus the throughput runs it lost to rc=127
"$RUN/bench_one2.sh" 'ornith-1.5-35b-a3b:q4_k_m'       ornith       skip skip only2048
"$RUN/bench_one2.sh" 'qwen3.6-27b-abliterated:q5_k_m'  qwen36-rerun no   skip only2048

# Xing4.0 - arch xing4_0, open PR ggml-org/llama.cpp#29141
ln -sf "$DL/xing4_0-29b-IQ4_NL.gguf" "$BM/xing4.0-29b-a4b_iq4_nl.gguf"
stop_router; start_router ~/llama-cuda12-xing
"$RUN/bench_one2.sh" 'xing4.0-29b-a4b:iq4_nl' xing

# G9v3 - arch g9v3, linuxid10t/llama.cpp:feature/g9v3-support
ln -sf "$DL/G9v3-39A5B-Q4_K_M.gguf" "$BM/g9v3-39a5b_q4_k_m.gguf"
stop_router; start_router ~/llama-cuda12-g9v3
"$RUN/bench_one2.sh" 'g9v3-39a5b:q4_k_m' g9v3

stop_router; start_router ~/llama-cuda12
log "QUEUE-2 DONE"
