#!/usr/bin/env bash
# QUEUE-DEVSTRAL -- the one row the matrix has never had: devstral-patched:latest, the
# model actually in production on :8080.
#
# Settings are queue-1.sh's, unchanged, because the whole point is pairability:
# --per-category 5, seed 42, ctx 8192 thinking-off / 16384 thinking-on, num_predict 12288,
# --api-timeout 2400. Nothing here may be "improved" or the numbers stop being comparable.
#
# THE CONSTRAINT: devstral is served ON DEMAND by the :8080 production router. The weights
# are 23.9 GiB; two copies do not fit in 32 GB. If pi calls :8080 while this holds the GPU,
# production degrades AND this run silently spills layers to system RAM and still writes a
# plausible-looking results.json. So:
#   * a human confirms production is idle before this starts, and again between legs;
#   * prodwatch.sh samples :8080 for a loaded child for the whole run (contention is then
#     visible after the fact, and any overlapping leg is discarded rather than reported);
#   * assert_on_gpu proves the weights are actually resident before the numbers count.
#
# devstral is mistral3 with a SEPARATE mmproj blob -- unlike the three round-3 models that
# failed to load, which pack their vision tower inside the single GGUF. The bench symlink
# points at the model blob only, which is what a text-only load wants. preflight_serves
# settles it in 30s either way; "won't load" is a result, not a thing to work around.
#
#   queue-devstral.sh off     -- MMLU-off (np 96 + 2048), HumanEval, throughput  (~88 min)
#   queue-devstral.sh think   -- MMLU thinking-on                                (~70 min)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
source "$HERE/lib.sh"

LEG=${1:-}
RID=devstral-patched_q8_0
TAG=devstral-patched:latest
SLUG=devstral
GGUF=$BM/$RID.gguf

log "================ QUEUE-DEVSTRAL: leg '$LEG' ================"
log "prod router :$PROD_PORT pid=$PROD_PID -- asserted unchanged after every stop_router"

case "$LEG" in
off)
  log "--- devstral thinking-off (mmlu96, mmlu2048, humaneval, throughput) ---"
  if fresh_router "$HOME/llama-cuda12" "$RID" 8192 && assert_shim_tag "$TAG" 11500; then
    warm_model "$TAG" 11500
    assert_on_gpu "$GGUF" "$SLUG ctx8192" || log "!!! continuing anyway is NOT ok -- see above"
    "$HERE/bench_off.sh" "$TAG" "$SLUG" 5 mmlu96,mmlu2048,humaneval,throughput
    log "devstral: bench_off rc=$?"
  else
    log "!!! SKIPPED devstral thinking-off: router or shim refused the model"
  fi
  ;;
think)
  log "--- devstral thinking-on (ctx 16384, num_predict 12288) ---"
  if fresh_router "$HOME/llama-cuda12" "$RID" 16384 && assert_shim_tag "$TAG" 11501; then
    warm_model "$TAG" 11501
    u=$(gpu_mib); log "devstral: GPU $u MiB with ctx 16384 loaded"
    assert_on_gpu "$GGUF" "$SLUG ctx16384" || log "!!! continuing anyway is NOT ok -- see above"
    "$HERE/bench_think.sh" "$TAG" "$SLUG" 12288 16384 2400
    log "devstral: bench_think rc=$?"
  else
    log "!!! SKIPPED devstral thinking-on: router or shim refused the model"
  fi
  ;;
*)
  log "usage: queue-devstral.sh off|think"; exit 2 ;;
esac

# Hand the GPU back: stop the bench router entirely so production can load devstral on
# demand without contending with anything of ours.
stop_router
log "================ QUEUE-DEVSTRAL '$LEG' DONE; bench router down, GPU released ================"
