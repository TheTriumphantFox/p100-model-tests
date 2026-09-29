#!/usr/bin/env bash
set -uo pipefail
ROOT=/home/hm/llama-cuda12
export LD_LIBRARY_PATH="$ROOT/lib"
MODEL=/var/lib/ollama/custom/devstral-q6_k.gguf
SP=/tmp/claude-1000/-home-hm/7fab0db3-e628-42a7-832f-2c8826781c04/scratchpad
printf '%-10s %-10s %-10s %s\n' CTX GEN_TPS PREFILL VRAM_MiB
for CTX in 65536 49152; do
  pkill -x llama-server 2>/dev/null; sleep 4
  "$ROOT/bin/llama-server" --model "$MODEL" --host 127.0.0.1 --port 8080 \
     --ctx-size $CTX --split-mode layer \
     --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn on \
     --jinja --parallel 1 --batch-size 512 --ubatch-size 512 \
     --alias m > "$SP/q6-$CTX.log" 2>&1 &
  for i in $(seq 1 120); do
    [ "$(curl -s -o /dev/null -w '%{http_code}' -m 2 http://127.0.0.1:8080/health 2>/dev/null)" = "200" ] && break
    sleep 5
  done
  if [ "$(curl -s -o /dev/null -w '%{http_code}' -m 2 http://127.0.0.1:8080/health 2>/dev/null)" != "200" ]; then
     printf '%-10s %s\n' "$CTX" "FAILED"; continue; fi
  R=$(curl -s -m 300 http://127.0.0.1:8080/v1/chat/completions -H 'Content-Type: application/json' -d @"$SP/pp.json")
  GEN=$(echo "$R" | python3 -c "import sys,json;print(round(json.load(sys.stdin).get('timings',{}).get('predicted_per_second',0),2))" 2>/dev/null)
  PRE=$(echo "$R" | python3 -c "import sys,json;print(round(json.load(sys.stdin).get('timings',{}).get('prompt_per_second',0),1))" 2>/dev/null)
  VR=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | paste -sd' ' -)
  printf '%-10s %-10s %-10s %s\n' "$CTX" "$GEN" "$PRE" "$VR"
done
pkill -x llama-server 2>/dev/null
echo "q6 sweep done"
