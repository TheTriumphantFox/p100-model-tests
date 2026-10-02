#!/usr/bin/env bash
# Speed sweep of every local model that loads on llama.cpp: layer vs tensor split,
# llama-bench pp512 + tg128, f16 KV, flash attention on, 3 reps.
# Stops the :8080 devstral service for the duration and restarts it on exit.
set -u
cd "$(dirname "$0")"
log() { echo "[$(date +'%F %T')] $*" | tee -a sweep.log; }
cleanup() {
  pkill -x llama-bench 2>/dev/null
  systemctl --user start llama-devstral.service && log "cleanup: :8080 devstral restarted"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

systemctl --user stop llama-devstral.service && log ":8080 devstral stopped"
sleep 3

M=~/models; A=/var/lib/ollama/candidates-r2; B=/var/lib/ollama/blobs; DL=~/Downloads/Models
MAIN=~/llama-cuda12; K2H=~/llama-cuda12-k2h
# name | gguf | build
MODELS=(
  "qwen3.6-35b-a3b UD-Q6_K (planner)|$M/qwen3.6-35b-a3b_ud-q6_k.gguf|$MAIN"
  "qwen3.6-27b-abliterated Q5_K_M|$M/qwen3.6-27b-abliterated_q5_k_m.gguf|$MAIN"
  "devstral-patched Q8_0|$M/devstral-patched_q8_0.gguf|$MAIN"
  "gpt-oss-20b Q8_0|$M/gpt-oss-20b_q8_0.gguf|$MAIN"
  "k2-horizon-7b Q8_0|$M/k2-horizon-7b_q8_0.gguf|$K2H"
  "qwen3.8-27b Q8_0 (ggml-org)|$A/Qwen3.8-27B-Q8_0.gguf|$MAIN"
  "qwen3.8-27b Q8_0 (unsloth)|$DL/Qwen3.8-27B-Q8_0.gguf|$MAIN"
  "qwen3.8-27b Q6_K_P (HauhauCS)|$DL/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf|$MAIN"
  "qwen3.8-27b Q4_K_M|$A/Qwen3.8-27B-Q4_K_M.gguf|$MAIN"
  "qwen3.8-27b-stock Q4_K_M|$B/sha256-f5f1dd8920d417aac2718b0bda3403da274301efdd6760b4f0f4b864ff2ad57d|$MAIN"
  "ornith-1.5-35b-a3b Q4_K_M|$A/Ornith-1.5-35B-Q4_K_M.gguf|$MAIN"
  "g9v3-39a5b Q4_K_M|$A/G9v3-39A5B-Q4_K_M.gguf|$HOME/llama-cuda12-g9v3"
)

i=0
for entry in "${MODELS[@]}"; do
  IFS='|' read -r name gguf build <<<"$entry"; i=$((i+1))
  for mode in layer tensor; do
    tag=$(printf "%02d-%s" $i "$mode")
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -1)
    if (( used > 200 )); then log "SKIP $name $mode: GPU busy (${used} MiB)"; continue; fi
    env_extra=(); [[ $mode == tensor ]] && env_extra=(NCCL_P2P_DISABLE=1)
    echo "$name|$gguf|$build|$mode" > raw/$tag.meta
    nvidia-smi --query-gpu=index,temperature.gpu --format=csv,noheader | tr '\n' ' ' >> raw/$tag.meta
    log "START $name $mode"
    timeout 1200 env LD_LIBRARY_PATH=$build/lib:$build/bin "${env_extra[@]}" \
      $build/bin/llama-bench -m "$gguf" -sm $mode -fa on -p 512 -n 128 -r 3 -o jsonl \
      > raw/$tag.jsonl 2> raw/$tag.log
    rc=$?
    log "END   $name $mode rc=$rc $(python3 -c "
import json,sys
r=[json.loads(l) for l in open('raw/$tag.jsonl') if l.strip()]
print(' '.join(('pp' if x['n_prompt'] else 'tg')+f\"={x['avg_ts']:.1f}\" for x in r))" 2>/dev/null)"
    pkill -x llama-bench 2>/dev/null; sleep 2
  done
done
# Flash-Next is bigger than VRAM: server + 48 distinct prompts (see flash-next-iq2/probe.py).
FN=$M/qwen3.8-flash-next_iq2_xxs/Qwen3.8-Flash-Next-IQ2_XXS/Qwen3.8-Flash-Next-IQ2_XXS-00001-of-00002.gguf
log "START qwen3.8-flash-next IQ2_XXS layer (server probe, default --fit)"
LD_LIBRARY_PATH=$MAIN/lib:$MAIN/bin $MAIN/bin/llama-server -m "$FN" --host 127.0.0.1 --port 8090 \
  -c 8192 -fa on --jinja --parallel 1 > raw/13-flashnext.server.log 2>&1 &
spid=$!
for _ in $(seq 1 200); do curl -sf http://127.0.0.1:8090/health >/dev/null && break; kill -0 $spid 2>/dev/null || break; sleep 3; done
timeout 2400 python3 ../flash-next-iq2/probe.py raw/13-flashnext.jsonl > raw/13-flashnext.txt 2>&1
log "END   qwen3.8-flash-next IQ2_XXS $(tail -1 raw/13-flashnext.txt)"
kill $spid 2>/dev/null; wait $spid 2>/dev/null
log "SWEEP_DONE"
