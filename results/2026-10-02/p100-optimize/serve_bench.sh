#!/usr/bin/env bash
# serve_bench.sh <tag> <model.gguf> "<task ids>" [extra llama-server args...]
# Starts a single-model llama-server on :8090, runs the given planner-bench tasks
# (pinned checks, thinking off, temp 0 -- same as drive_pinned.sh), then stops it.
set -uo pipefail
tag=$1; model=$2; tasks=$3; shift 3
HERE=$(cd "$(dirname "$0")" && pwd)
PB=~/Projects/Tests/2026-09-23/planner-bench
PY=~/Projects/Tests/.venv/bin/python
mkdir -p "$HERE/serve"
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -1)
if (( used > 200 )); then echo "GPU busy (${used} MiB), not running $tag" >&2; exit 3; fi
log=$HERE/serve/$tag.server.log
echo "# $(date -Is) ${GGML_ENV:-} llama-server -m $model $*" > "$HERE/serve/$tag.cmd"
env LD_LIBRARY_PATH=$HOME/llama-cuda12/lib:$HOME/llama-cuda12/bin ${GGML_ENV:-} \
  $HOME/llama-cuda12/bin/llama-server -m "$model" --host 127.0.0.1 --port 8090 \
  --ctx-size 32768 --jinja --parallel 1 "$@" > "$log" 2>&1 &
pid=$!
trap 'kill $pid 2>/dev/null; wait $pid 2>/dev/null' EXIT
for i in $(seq 1 300); do
  curl -sf http://127.0.0.1:8090/health >/dev/null && break
  kill -0 $pid 2>/dev/null || { echo "server died: $(tail -5 "$log")" >&2; exit 4; }
  sleep 2
done
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader > "$HERE/serve/$tag.vram"
$PY "$PB/run.py" --url http://127.0.0.1:8090/v1/chat/completions --model x \
  --out "$HERE/serve/$tag.json" --pin-checks \
  --extra-body '{"chat_template_kwargs":{"enable_thinking":false}}' --only $tasks
grep -E "draft acceptance|accept" "$log" | tail -3
