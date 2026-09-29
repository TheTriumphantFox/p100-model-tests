#!/usr/bin/env bash
# QUEUE 2 -- context limits as a measured result, then the thinking-ON cells that depend
# on them.
#
# The two empty thinking-on cells in the brief's table are on the two largest quants, and
# that is very likely not a coincidence. Thinking-on needs ctx 16384 to hold a 12288-token
# budget; at f16 that is ~4.3 GB of KV on top of 29 GB of weights, in a 32 GB box.
#
# A spill is DATA, not an error to route around. llama.cpp does not refuse an over-large
# load -- it leaves layers in system RAM and keeps answering correctly at a fraction of the
# speed. Accuracy cannot detect that, and re-running an accuracy benchmark while spilled
# would mostly just re-measure the same answers slowly: partial offload changes the decode
# RATE, not what the model says. So the spill is priced where it actually shows up --
# tok/s against context size -- and the accuracy runs then use the largest context that is
# genuinely resident.
#
# PART 1  ctx ladder: 8k -> 32k per model, recording VRAM resident vs weight size and a
#         real decode rate at every rung, spilled rungs included. Also yields each model's
#         measured KV bytes/token from the VRAM difference between two resident rungs, so
#         nobody's published KiB/token figure has to be trusted.
#         Includes g9v3, whose 38 KiB/token KV is the one structural long-context claim on
#         the shelf that no benchmark here has ever tested, and the incumbent as reference.
#
# PART 2  thinking-on MMLU-Pro for the three big quants, at the largest RESIDENT context
#         the ladder found. Where that is below 16384 the token budget shrinks with it, so
#         more batches truncate and the score is a FLOOR -- flagged, not smoothed over.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
source "$HERE/lib.sh"
PY=$HOME/Projects/Tests/.venv/bin/python

# ---- PART 1: the ladder ---------------------------------------------------------------
# router-id | tag | slug | runtime
LADDER=(
  "qwen3.8-27b-ggmlorg_q8_0|qwen3.8-27b-ggmlorg:q8_0|ggmlorg-q8|$HOME/llama-cuda12"
  "qwen3.8-27b-unsloth_q8_0|qwen3.8-27b-unsloth:q8_0|unsloth-q8|$HOME/llama-cuda12"
  "qwen3.8-27b-uncensored-hauhaucs_q6_k_p|qwen3.8-27b-uncensored-hauhaucs:q6_k_p|uncensored-q6kp|$HOME/llama-cuda12"
  "qwen3.6-27b-abliterated_q5_k_m|qwen3.6-27b-abliterated:q5_k_m|incumbent|$HOME/llama-cuda12"
  "g9v3-39a5b_q4_k_m|g9v3-39a5b:q4_k_m|g9v3|$HOME/llama-cuda12-g9v3"
)

log "================ QUEUE-2 PART 1: context ladders ================"
for row in "${LADDER[@]}"; do
  IFS='|' read -r RID TAG SLUG RT <<<"$row"
  if [ ! -x "$RT/bin/llama-server" ]; then
    log "!!! SKIPPED ladder $SLUG: no runtime at $RT"; continue
  fi
  if [ -s "$RUN/ctx-ladder/$SLUG.jsonl" ]; then
    log "ladder $SLUG already present, skipping"; continue
  fi
  RT="$RT" "$HERE/ctx-ladder.sh" "$RID" "$TAG" "$SLUG" f16 8192 12288 16384 24576 32768
done
"$PY" "$HERE/ladder_report.py" 2>&1 | tee -a "$RUN/driver.log"

# ---- PART 2: thinking-on at the largest resident context ------------------------------
log "================ QUEUE-2 PART 2: thinking-on, big quants ================"
THINK=(
  "qwen3.8-27b-ggmlorg_q8_0|qwen3.8-27b-ggmlorg:q8_0|ggmlorg-q8"
  "qwen3.8-27b-uncensored-hauhaucs_q6_k_p|qwen3.8-27b-uncensored-hauhaucs:q6_k_p|uncensored-q6kp"
  "qwen3.8-27b-unsloth_q8_0|qwen3.8-27b-unsloth:q8_0|unsloth-q8"
)
for row in "${THINK[@]}"; do
  IFS='|' read -r RID TAG SLUG <<<"$row"
  CTX=$("$PY" "$HERE/ladder_report.py" --best "$SLUG" 2>/dev/null)
  if [ -z "$CTX" ] || [ "$CTX" -lt 4096 ]; then
    log "!!! $SLUG: the ladder found no resident context at all; cannot score thinking-on."
    log "!!!   That is a hardware limit on this box, not a model result. Cell stays empty."
    continue
  fi
  # Leave room for the prompt: an MMLU batch prompt is 1-2k tokens.
  NP=$(( CTX - 4096 )); [ "$NP" -gt 12288 ] && NP=12288
  if [ "$CTX" -lt 16384 ]; then
    log "$SLUG: !!! DEVIATION -- largest resident ctx is $CTX, below the 16384 the round-2"
    log "$SLUG:     thinking-on column used. num_predict drops to $NP, so more batches will"
    log "$SLUG:     truncate and the score will be a FLOOR. Read it with its cap count."
  fi
  log "--- QUEUE-2: $SLUG thinking-on at ctx=$CTX np=$NP ---"
  if fresh_router "$HOME/llama-cuda12" "$RID" "$CTX" && assert_shim_tag "$TAG" 11501; then
    warm_model "$TAG" 11501
    assert_on_gpu "$BM/$RID.gguf" "$SLUG" || log "$SLUG: WARN proceeding on a spilled load -- speed is not this model's real speed"
    "$HERE/bench_think.sh" "$TAG" "$SLUG" "$NP" "$CTX" 3600
  else
    log "!!! SKIPPED $SLUG thinking-on: preflight failed"
  fi
done

stop_router
start_router "$HOME/llama-cuda12" 8192
log "================ QUEUE-2 DONE ================"
"$PY" "$HERE/matrix.py" --pc 5 2>&1 | tee -a "$RUN/driver.log"
