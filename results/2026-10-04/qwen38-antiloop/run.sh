#!/usr/bin/env bash
# Rerun the 4 MMLU-Pro thinking-on batches that looped/capped on 2026-10-02
# (economics, engineering, history, law; seed 42, per-category 5, np 12288, ctx 16384)
# Qwen3.8-27B (:8080 preset qwen3.8-27b-mtp). Batches that capped on 09-19: engineering, law.
#   0: current preset BEFORE the change (harness temp 0)   LEGS="0:11502" ./run.sh
#   A: harness sampling (temp 0, as in the 10-02 run)  -> isolates effort=medium + budget 6144
#   B: --server-sampling (preset temp 1.0/top-k 20...) -> what pi actually gets
set -uo pipefail
T=~/Projects/Tests; RUN=$T/2026-10-04/qwen38-antiloop
CATS="economics,engineering,history,law"; TAG=qwen3.8-27b:mtp-prod
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a "$RUN/driver.log"; }
PIDS=()
trap 'for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done' EXIT
shim() { port=$1; shift
  "$T/.venv/bin/python" "$T/scripts/ollama_shim.py" --router http://127.0.0.1:8080 \
    --models-dir /home/hm/llama-models --port "$port" --force-think "$@" >> "$RUN/shim-$port.log" 2>&1 &
  PIDS+=($!); sleep 2; }
shim 11502
shim 11503 --server-sampling
LEGS=${LEGS:-A:11502 B:11503}
for leg in $LEGS; do
  name=${leg%%:*}; port=${leg##*:}; OUT=$RUN/mmlu-$name
  log "leg $name via :$port start"
  "$T/.venv/bin/python" "$T/2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py" run \
    --base-url "http://127.0.0.1:$port" --model "$TAG" --num-ctx 16384 --num-predict 12288 \
    --per-category 5 --categories "$CATS" --api-timeout 2400 --output "$OUT" > "$OUT.log" 2>&1
  log "leg $name done rc=$?"
done
log "DONE $LEGS"
