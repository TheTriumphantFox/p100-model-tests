#!/usr/bin/env bash
# Tokenizer-only pass: one CPU-only llama-server per model on :8093, no GPU (CUDA hidden,
# --device none, -ngl 0), no warmup, tiny context. Only /tokenize is called.
set -uo pipefail
D=$(cd "$(dirname "$0")" && pwd)
BM=~/llama-bench-models
PY=~/Projects/Tests/.venv/bin/python
PORT=8093
mkdir -p "$D/logs"

one() {  # $1 = gguf name, $2 = slug, $3 = build dir
  local pid i
  CUDA_VISIBLE_DEVICES= LD_LIBRARY_PATH="$3/lib" "$3/bin/llama-server" \
    -m "$BM/$1.gguf" --host 127.0.0.1 --port $PORT --device none -ngl 0 \
    --no-warmup -c 512 --parallel 1 >"$D/logs/$2.log" 2>&1 &
  pid=$!
  for i in $(seq 1 150); do
    sleep 2
    curl -sf --max-time 2 http://127.0.0.1:$PORT/health >/dev/null && break
    kill -0 $pid 2>/dev/null || { echo "$2: server exited, see logs/$2.log"; return; }
  done
  $PY "$D/measure.py" "$2" $PORT
  kill $pid; wait $pid 2>/dev/null
}

one g9v3-39a5b_q4_k_m              g9v3     ~/llama-cuda12-g9v3
one devstral-patched_q8_0          devstral ~/llama-cuda12
one gpt-oss-20b_q8_0               gptoss   ~/llama-cuda12
one ornith-1.5-35b-a3b_q4_k_m      ornith   ~/llama-cuda12
one qwen3.6-27b-abliterated_q5_k_m qwen36   ~/llama-cuda12
one qwen3.8-27b-unsloth_q8_0       qwen38   ~/llama-cuda12
