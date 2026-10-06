#!/usr/bin/env bash
# loadtest.sh NAME BUILD CTX KV -- extra llama-server args
# Loads one model on :8090 with --fit off and every layer on GPU, so a context
# that doesn't fit fails instead of spilling layers to CPU. Records peak VRAM.
set -u
name=$1 build=$2 ctx=$3 kv=$4; shift 5
out=$(dirname "$0")/raw; mkdir -p "$out"
log=$out/$name-$ctx-$kv.log
export LD_LIBRARY_PATH=$build/lib
"$build/bin/llama-server" --host 127.0.0.1 --port 8090 -c "$ctx" -ctk "$kv" -ctv "$kv" \
  -fa on --jinja --parallel 1 -b 512 -ub 512 -sm layer --fit off -ngl 999 "$@" > "$log" 2>&1 &
pid=$!
st=FAIL
for i in $(seq 1 300); do
  if ! kill -0 $pid 2>/dev/null; then st=EXITED; break; fi
  if curl -sf localhost:8090/health >/dev/null 2>&1; then st=OK; break; fi
  sleep 1
done
mem=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | paste -sd/)
kill $pid 2>/dev/null; wait $pid 2>/dev/null
for i in $(seq 1 30); do [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -1)" -lt 500 ] && break; sleep 1; done
oom=$(grep -ciE 'out of memory|failed to allocate|cudaMalloc failed' "$log")
off=$(grep -oE 'offloaded [0-9]+/[0-9]+ layers' "$log" | head -1)
echo "$name ctx=$ctx kv=$kv -> $st vram=${mem}MiB oom_lines=$oom $off"
