#!/usr/bin/env bash
# CONTEXT LADDER -- where each model stops fitting in 32 GB, and what it costs when it
# does not. Run per model; writes one JSON row per rung to ctx-ladder/<slug>.jsonl.
#
#   ctx-ladder.sh <router-id> <ollama-tag> <slug> [kv-type] [ctx...]
#
# WHY THIS EXISTS AND WHY A SPILL IS NOT SKIPPED:
#   llama.cpp does not refuse a model that does not fit. It leaves layers in system RAM
#   and keeps serving -- correct answers, a fraction of the speed. Accuracy cannot detect
#   that; only the decode rate can. So every rung is MEASURED (VRAM resident vs the weight
#   file, plus a real generation) and RECORDED, including the rungs that spill. The spill
#   point of a usable context is the finding, not an error to route around.
#
#   The ladder also prices the KV cache without trusting anyone's KiB/token figure: VRAM at
#   two rungs that both fit differ only by the KV of the extra tokens, so
#   (vram_hi - vram_lo) / (ctx_hi - ctx_lo) is this model's measured bytes per token.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
source "$HERE/lib.sh"

RID=$1; TAG=$2; SLUG=$3; KV=${4:-f16}; shift 4 2>/dev/null || shift 3
RT=${RT:-$HOME/llama-cuda12}   # g9v3 needs its fork runtime, everything else the production build
RUNGS=("$@"); [ ${#RUNGS[@]} -eq 0 ] && RUNGS=(8192 12288 16384 24576 32768)

OUT=$RUN/ctx-ladder
mkdir -p "$OUT"
GGUF=$BM/$RID.gguf
WEIGHTS=$(( $(stat -Lc %s "$GGUF") / 1048576 ))
log "=== CTX LADDER $SLUG (weights ${WEIGHTS} MiB, KV $KV, runtime $RT) rungs: ${RUNGS[*]} ==="

for CTX in "${RUNGS[@]}"; do
  if ! fresh_router "$RT" "$RID" "$CTX" --cache-type-k "$KV" --cache-type-v "$KV"; then
    log "$SLUG ctx=$CTX: router would not start -- recording as a hard failure"
    echo "{\"slug\":\"$SLUG\",\"ctx\":$CTX,\"kv\":\"$KV\",\"weights_mib\":$WEIGHTS,\"status\":\"router-failed\"}" >> "$OUT/$SLUG.jsonl"
    continue
  fi
  # The load itself is indistinguishable from a CPU spill for ~150s, so warm fully first.
  warm_model "$TAG" 11500
  VRAM=$(gpu_mib)
  PROBE=$(py "$HERE/probe.py" "$TAG" 11500 200 1800)
  TPS=$(echo "$PROBE" | py -c 'import json,sys; print(json.load(sys.stdin).get("tok_per_s") or 0)')
  OK=$(echo "$PROBE" | py -c 'import json,sys; print("1" if json.load(sys.stdin).get("ok") else "0")')
  # Resident well below the weight file means layers stayed in system RAM.
  if [ "$VRAM" -lt $(( WEIGHTS * 9 / 10 )) ]; then STATUS=spilled; else STATUS=resident; fi
  [ "$OK" = "0" ] && STATUS=failed
  log "$SLUG ctx=$CTX kv=$KV -> $STATUS, ${VRAM} MiB resident of ${WEIGHTS} MiB weights, ${TPS} tok/s"
  echo "{\"slug\":\"$SLUG\",\"ctx\":$CTX,\"kv\":\"$KV\",\"weights_mib\":$WEIGHTS,\"vram_mib\":$VRAM,\"tok_per_s\":$TPS,\"status\":\"$STATUS\",\"probe\":$PROBE}" >> "$OUT/$SLUG.jsonl"
  # Two spills in a row means every larger rung spills harder; stop burning time on them.
  if [ "$STATUS" = spilled ]; then
    SPILLS=$(( ${SPILLS:-0} + 1 ))
    if [ "$SPILLS" -ge 2 ]; then
      log "$SLUG: two consecutive spills; larger contexts only spill further, stopping the ladder"
      break
    fi
  else
    SPILLS=0
  fi
done
log "=== CTX LADDER $SLUG done -> $OUT/$SLUG.jsonl ==="
