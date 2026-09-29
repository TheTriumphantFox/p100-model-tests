#!/usr/bin/env bash
# A/B Vulkan(ollama) vs CUDA(llama-server) on a K-quant model, matched ctx 32768.
set -uo pipefail
SP=/tmp/claude-1000/-home-hm/7fab0db3-e628-42a7-832f-2c8826781c04/scratchpad
BLOB=$(cat "$SP/qwen_blob.txt")
MODEL=qwen3.6-27b-abliterated:q5_k_m
CTX=32768
ROOT=/home/hm/llama-cuda12

PROMPT=$(python3 -c "print('def process_record(item, config, registry):\n    validate(item)\n    normalize(item, config)\n'*60)")

# ---------- 1. VULKAN via ollama ----------
pkill -x llama-server 2>/dev/null; sleep 5
python3 -c "
import json
p=open('$SP/prompt.txt').read() if False else '''$PROMPT'''
print(json.dumps({'model':'$MODEL','prompt':p+'\nSummarize the above code in one sentence.','stream':False,
 'options':{'num_ctx':$CTX,'num_predict':128,'temperature':0}}))" > "$SP/olreq.json"
echo '--- vulkan (ollama) warming up ---'
curl -s -m 900 http://127.0.0.1:11434/api/generate -d @"$SP/olreq.json" > "$SP/ol1.json"
curl -s -m 900 http://127.0.0.1:11434/api/generate -d @"$SP/olreq.json" > "$SP/ol2.json"
VULK=$(python3 -c "
import json
d=json.load(open('$SP/ol2.json'))
pe,pd=d.get('prompt_eval_count',0),d.get('prompt_eval_duration',1)
ec,ed=d.get('eval_count',0),d.get('eval_duration',1)
print(f'{pe/(pd/1e9):.1f} {ec/(ed/1e9):.2f}')")
ollama stop $MODEL 2>/dev/null; sleep 5

# ---------- 2. CUDA via llama-server ----------
export LD_LIBRARY_PATH="$ROOT/lib"
"$ROOT/bin/llama-server" --model "$BLOB" --host 127.0.0.1 --port 8081 \
   --ctx-size $CTX --split-mode layer \
   --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn on \
   --jinja --parallel 1 --batch-size 512 --ubatch-size 512 --alias q > "$SP/qwen-cuda.log" 2>&1 &
for i in $(seq 1 150); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' -m 2 http://127.0.0.1:8081/health 2>/dev/null)" = "200" ] && break
  sleep 5
done
if [ "$(curl -s -o /dev/null -w '%{http_code}' -m 2 http://127.0.0.1:8081/health 2>/dev/null)" != "200" ]; then
  echo "CUDA server FAILED to start"; grep -iE "error|assert|cudaMalloc" "$SP/qwen-cuda.log" | head -5; exit 1
fi
python3 -c "
import json
print(json.dumps({'model':'q','messages':[{'role':'user','content':'''$PROMPT'''+'\nSummarize the above code in one sentence.'}],
 'max_tokens':128,'temperature':0}))" > "$SP/cureq.json"
curl -s -m 900 http://127.0.0.1:8081/v1/chat/completions -H 'Content-Type: application/json' -d @"$SP/cureq.json" > /dev/null
CUDAR=$(curl -s -m 900 http://127.0.0.1:8081/v1/chat/completions -H 'Content-Type: application/json' -d @"$SP/cureq.json" | python3 -c "
import sys,json;t=json.load(sys.stdin).get('timings',{})
print(f\"{t.get('prompt_per_second',0):.1f} {t.get('predicted_per_second',0):.2f}\")")
VR=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | paste -sd' ' -)
pkill -x llama-server 2>/dev/null

echo
echo "===== $MODEL (Q5_K_M, 20G) @ ctx $CTX ====="
printf '%-22s %-12s %s\n' BACKEND PREFILL GENERATION
printf '%-22s %-12s %s\n' "Vulkan (ollama)" $VULK
printf '%-22s %-12s %s\n' "CUDA (llama.cpp)" $CUDAR
echo "CUDA VRAM: $VR MiB"
