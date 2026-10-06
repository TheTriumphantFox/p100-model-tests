#!/usr/bin/env bash
# kv-ab.sh <label> <cache-type> <ctx> -- serve devstral with one KV type, measure, stop.
# Stop llama-router.service first; both cannot hold the model at once.
set -uo pipefail
ROOT=/home/hm/llama-cuda12
# Results default to a dated run folder; override with KV_AB_OUT.
BENCH=${KV_AB_OUT:-/home/hm/Projects/Tests/$(date +%F)/devstral-p100-bandwidth}
mkdir -p "$BENCH"
MODEL=/var/lib/ollama/blobs/sha256-52018a575c1f167dcb3948be64afefde325934536a15b9f7913dfb3f450caac3
LABEL=$1; KV=$2; CTX=$3
# KV may be "ktype,vtype" for a mixed cache
KT=${KV%%,*}; VT=${KV##*,}
export LD_LIBRARY_PATH="$ROOT/lib:${LD_LIBRARY_PATH:-}"
"$ROOT/bin/llama-server" --model "$MODEL" --host 127.0.0.1 --port 8080 \
  --ctx-size "$CTX" --split-mode layer --cache-type-k "$KT" --cache-type-v "$VT" \
  --flash-attn on --jinja --parallel 1 --batch-size 512 --ubatch-size 512 ${EXTRA:-} \
  > "$BENCH/$LABEL.log" 2>&1 &
PID=$!
for i in $(seq 1 300); do
  curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1 && break
  kill -0 $PID 2>/dev/null || { echo "$LABEL: server died"; tail -12 "$BENCH/$LABEL.log"; exit 1; }
  sleep 1
done
echo "=== $LABEL  (KV=$KV, ctx=$CTX)  ready in ${i}s"
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' '; echo
python3 "$(dirname "$0")/kv_ab.py" "$LABEL" ${4:-4000} ${5:-}
RC=$?
kill $PID 2>/dev/null; wait $PID 2>/dev/null; sleep 4
exit $RC
