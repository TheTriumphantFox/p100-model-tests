#!/usr/bin/env bash
# Everything that runs on the PRODUCTION ~/llama-cuda12 build (router :8081 already up):
# the two candidates whose architectures are already upstream, plus a reproducibility
# re-run of the incumbent. xing4_0 and g9v3 need their own fork builds - separate queue.
set -uo pipefail
RUN=~/Projects/Tests/2026-09-19/candidates-round2
DL=/var/lib/ollama/candidates-r2
BM=~/llama-bench-models
echo "[$(date +%T)] QUEUE START" >> "$RUN/driver.log"

# 1. Ornith - throughput already run separately
"$RUN/bench_one.sh" 'ornith-1.5-35b-a3b:q4_k_m' ornith skip

# 2. Nemotron-Cascade-2 - wait for the download to land, then wire it in
F="$DL/nvidia_Nemotron-Cascade-2-30B-A3B-Q4_K_M.gguf"
for i in $(seq 1 180); do [ -f "$F" ] && break; sleep 20; done
if [ -f "$F" ]; then
  ln -sf "$F" "$BM/nemotron-cascade-2-30b-a3b_q4_k_m.gguf"
  echo "[$(date +%T)] nemotron symlinked" >> "$RUN/driver.log"
  "$RUN/bench_one.sh" 'nemotron-cascade-2-30b-a3b:q4_k_m' nemotron
else
  echo "[$(date +%T)] nemotron download never arrived" >> "$RUN/driver.log"
fi

# 3. Incumbent re-run: same tag, same harnesses, same rig as 2026-09-19/candidates
"$RUN/bench_one.sh" 'qwen3.6-27b-abliterated:q5_k_m' qwen36-rerun
echo "[$(date +%T)] QUEUE DONE" >> "$RUN/driver.log"
