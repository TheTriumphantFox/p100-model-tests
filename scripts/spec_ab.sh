#!/usr/bin/env bash
# spec_ab.sh <label> <model-gguf> <spec-type|none> [draft-gguf]
# Serve one model on :8082 with one speculative-decoding config, measure, stop.
# Deliberately NOT :8080 (production devstral router) or :8081 (bench router).
set -uo pipefail
ROOT=${ROOT:-/home/hm/llama-cuda12}
OUT=${SPEC_AB_OUT:-/home/hm/Projects/Tests/$(date +%F)/spec-decoding}
mkdir -p "$OUT"
LABEL=$1; MODEL=$2; STYPE=$3; DRAFT=${4:-}
PORT=${PORT:-8082}
ARGS=(--model "$MODEL" --host 127.0.0.1 --port "$PORT" --ctx-size "${CTX:-8192}"
      --split-mode layer --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja
      --parallel 1 --batch-size 512 --ubatch-size 512)
[ "$STYPE" != "none" ] && ARGS+=(--spec-type "$STYPE")
[ -n "$DRAFT" ] && ARGS+=(--spec-draft-model "$DRAFT")
# EXTRA: further llama-server flags, e.g. EXTRA="--spec-draft-n-max 3" (word-split).
read -r -a EXTRA_ARGS <<< "${EXTRA:-}"; ARGS+=("${EXTRA_ARGS[@]}")
export LD_LIBRARY_PATH="$ROOT/lib:${LD_LIBRARY_PATH:-}"
"$ROOT/bin/llama-server" "${ARGS[@]}" > "$OUT/$LABEL.log" 2>&1 &
PID=$!
for i in $(seq 1 600); do
  curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break
  kill -0 $PID 2>/dev/null || { echo "$LABEL: SERVER DIED"; tail -15 "$OUT/$LABEL.log"; exit 1; }
  sleep 1
done
echo "=== $LABEL  (spec=$STYPE draft=${DRAFT##*/})  ready in ${i}s"
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' '; echo
SPEC_AB_OUT="$OUT" python3 "$(dirname "$0")/spec_ab.py" "$LABEL" "$PORT" "${NPRED:-200}"
RC=$?
kill $PID 2>/dev/null; wait $PID 2>/dev/null; sleep 5
exit $RC
