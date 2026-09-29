#!/usr/bin/env bash
set -uo pipefail
SP=/tmp/claude-1000/-home-hm/7fab0db3-e628-42a7-832f-2c8826781c04/scratchpad
BLOB=$(cat "$SP/qwen_blob.txt"); MODEL=qwen3.6-27b-abliterated:q5_k_m; CTX=32768
ROOT=/home/hm/llama-cuda12

mkprompt() { python3 -c "
import random,sys
random.seed(int(sys.argv[1]))
toks=[f'def fn_{random.randint(100000,999999)}(a{random.randint(0,999)}, b):\n    return a{random.randint(0,999)} + {random.randint(0,9999)}\n' for _ in range(70)]
print(''.join(toks))" $1; }

pkill -x llama-server 2>/dev/null; sleep 5
# --- Vulkan, unique prompt ---
P1=$(mkprompt 11)
python3 -c "
import json;print(json.dumps({'model':'$MODEL','prompt':'''$P1'''+'\nSummarize.','stream':False,
'options':{'num_ctx':$CTX,'num_predict':8,'temperature':0}}))" > "$SP/olp.json"
curl -s -m 900 http://127.0.0.1:11434/api/generate -d @"$SP/olp.json" > "$SP/olp.out"
VP=$(python3 -c "
import json;d=json.load(open('$SP/olp.out'))
pe,pd=d.get('prompt_eval_count',0),d.get('prompt_eval_duration',1)
print(f'{pe} {pe/(pd/1e9):.1f}')")
ollama stop $MODEL 2>/dev/null; sleep 5

# --- CUDA, DIFFERENT unique prompt ---
export LD_LIBRARY_PATH="$ROOT/lib"
"$ROOT/bin/llama-server" --model "$BLOB" --host 127.0.0.1 --port 8081 --ctx-size $CTX \
  --split-mode layer --cache-type-k q8_0 --cache-type-v q8_0 --flash-attn on \
  --jinja --parallel 1 --batch-size 512 --ubatch-size 512 --alias q > "$SP/qc.log" 2>&1 &
for i in $(seq 1 150); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' -m 2 http://127.0.0.1:8081/health 2>/dev/null)" = "200" ] && break; sleep 5; done
P2=$(mkprompt 22)
python3 -c "
import json;print(json.dumps({'model':'q','messages':[{'role':'user','content':'''$P2'''+'\nSummarize.'}],
'max_tokens':8,'temperature':0}))" > "$SP/cup.json"
CP=$(curl -s -m 900 http://127.0.0.1:8081/v1/chat/completions -H 'Content-Type: application/json' -d @"$SP/cup.json" \
  | python3 -c "import sys,json;t=json.load(sys.stdin).get('timings',{});print(f\"{t.get('prompt_n',0)} {t.get('prompt_per_second',0):.1f}\")")
pkill -x llama-server 2>/dev/null
echo
echo "===== PREFILL, cold cache, unique prompts ====="
printf '%-20s %-10s %s\n' BACKEND TOKENS TOK/S
printf '%-20s %-10s %s\n' "Vulkan (ollama)" $VP
printf '%-20s %-10s %s\n' "CUDA (llama.cpp)" $CP
