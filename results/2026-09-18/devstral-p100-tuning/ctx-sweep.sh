#!/usr/bin/env bash
# Sweep n_ctx and measure generation + prefill, to find where the model stops
# spilling to CPU. Uses pkill -x (comm name) to avoid self-match.
set -uo pipefail
ROOT=/home/hm/llama-cuda12
export LD_LIBRARY_PATH="$ROOT/lib"
MODEL=/var/lib/ollama/blobs/sha256-52018a575c1f167dcb3948be64afefde325934536a15b9f7913dfb3f450caac3
SP=/tmp/claude-1000/-home-hm/7fab0db3-e628-42a7-832f-2c8826781c04/scratchpad

python3 -c "
import json
p='def process_record(item, config, registry):\n    validate(item)\n    normalize(item, config)\n'*60
print(json.dumps({'model':'m','messages':[{'role':'user','content':p+'\nSummarize in one sentence.'}],'max_tokens':64,'temperature':0}))
" > "$SP/pp.json"

printf '%-8s %-10s %-10s %-12s %s\n' CTX GEN_TPS PREFILL CPU_SPILL VRAM_USED
for CTX in 65536 49152 32768 24576; do
  pkill -x llama-server 2>/dev/null; sleep 4
  "$ROOT/bin/llama-server" --model "$MODEL" --host 127.0.0.1 --port 8080 \
     --ctx-size $CTX --split-mode layer \
     --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn on \
     --jinja --parallel 1 --batch-size 512 --ubatch-size 512 \
     --alias m > "$SP/sweep-$CTX.log" 2>&1 &
  for i in $(seq 1 120); do
    [ "$(curl -s -o /dev/null -w '%{http_code}' -m 2 http://127.0.0.1:8080/health 2>/dev/null)" = "200" ] && break
    sleep 5
  done
  if [ "$(curl -s -o /dev/null -w '%{http_code}' -m 2 http://127.0.0.1:8080/health 2>/dev/null)" != "200" ]; then
    printf '%-8s %s\n' "$CTX" "FAILED TO START"; continue
  fi
  R=$(curl -s -m 300 http://127.0.0.1:8080/v1/chat/completions -H 'Content-Type: application/json' -d @"$SP/pp.json")
  GEN=$(echo "$R" | python3 -c "import sys,json;print(round(json.load(sys.stdin).get('timings',{}).get('predicted_per_second',0),2))" 2>/dev/null)
  PRE=$(echo "$R" | python3 -c "import sys,json;print(round(json.load(sys.stdin).get('timings',{}).get('prompt_per_second',0),1))" 2>/dev/null)
  SPILL=$(grep -oiE "CPU model buffer size *= *[0-9.]+" "$SP/sweep-$CTX.log" | head -1 | grep -oE "[0-9.]+$")
  [ -z "$SPILL" ] && SPILL=$(grep -oiE "CPU_Mapped model buffer size *= *[0-9.]+" "$SP/sweep-$CTX.log" | head -1 | grep -oE "[0-9.]+$")
  [ -z "$SPILL" ] && SPILL="?"
  VR=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | paste -sd+ | bc)
  printf '%-8s %-10s %-10s %-12s %s MiB\n' "$CTX" "$GEN" "$PRE" "$SPILL" "$VR"
done
pkill -x llama-server 2>/dev/null
echo "sweep done"
