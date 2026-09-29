#!/usr/bin/env bash
# QUEUE 1 -- complete the matrix rows for the four models that have no CUDA numbers in it,
# at the EXISTING settings (--per-category 5, seed 42), not the extended 280-question ones.
# Every cell produced here is therefore pairable via mcnemar.py against the round-2 records
# in ../../2026-09-19/candidates-round2/ and the round-1 records in ../../2026-09-19/candidates/.
#
# Fast models first, so complete rows land early:
#   gemma4-e4b    6.3 GB  -- tiny; also the only audio-in model on the shelf
#   gpt-oss-20b  12.1 GB  -- 66 tok/s; round-1 CUDA numbers exist at IDENTICAL settings, so
#                            this doubles as a reproducibility check on them
#   qwen36-vl    22.1 GB  -- MoE a3b, the vision model + qwen worker
#   opus-distill 17.5 GB  -- dense; the point of this one is the 75.7 MMLU claim, which is a
#                            Vulkan-era number that has never been re-run on CUDA
#
# Per model: thinking-off legs at ctx 8192, then a router restart to ctx 16384 for the
# thinking-on leg (12288 num_predict needs the bigger window).
#
# NOT here: devstral-patched. It is the production model on :8080 and the two routers would
# contend for VRAM if pi sent a request mid-run -- degrading production AND silently spilling
# the benchmark to CPU. Waiting on a confirmed idle window.
#
# NOT here: thinking-on for the three big Qwen3.8 quants (ggmlorg-q8 28.6, unsloth-q8 29.0,
# uncensored-q6kp 25.9 GB). At ctx 16384 with f16 KV those may not fit in 32 GB, which is the
# likely reason those two cells were empty in the first place. queue-2.sh measures the fit
# before running them rather than assuming it.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
source "$HERE/lib.sh"

# router-id | ollama tag | slug | thinking-off legs | think? (yes/no)
QUEUE=(
  # Re-run of the ggml-org throughput leg only: the first attempt exited 127 in zero
  # seconds because bench_off.sh used `env OLLAMA_HOST=... py ...` and env cannot run a
  # shell function -- the exact bug recorded as #3 in candidates-round2/REPORT.md. Its
  # thinking-on cell is queue-2's job, so no think leg here.
  "qwen3.8-27b-ggmlorg_q8_0|qwen3.8-27b-ggmlorg:q8_0|ggmlorg-q8|throughput|no"
  "gemma4-e4b-abliterated_q4_k_m|gemma4-e4b-abliterated:q4_k_m|gemma4-e4b|mmlu96,mmlu2048,humaneval,throughput|yes"
  # gpt-oss reasons unconditionally (harmony format); at num_predict 96 it never reaches an
  # answer line, which is why round 1 ran only the 2048 budget. Same choice here.
  "gpt-oss-20b_q8_0|gpt-oss-20b:q8_0|gpt-oss-20b|mmlu2048,humaneval,throughput|yes"
  "qwen3.6-35b-a3b-abliterated-vl_q4_k_m|qwen3.6-35b-a3b-abliterated-vl:q4_k_m|qwen36-vl|mmlu96,mmlu2048,humaneval,throughput|yes"
  "qwen3.6-27b-opus-distill_q4_k_m|qwen3.6-27b-opus-distill:q4_k_m|opus-distill|mmlu96,mmlu2048,humaneval,throughput|yes"
)

log "================ QUEUE-1 START (per-category 5, matching round 2) ================"
log "prod router :$PROD_PORT pid=$PROD_PID -- asserted unchanged after every stop_router"

for row in "${QUEUE[@]}"; do
  IFS='|' read -r RID TAG SLUG WHAT THINK <<<"$row"

  log "--- QUEUE-1: $SLUG thinking-off ($WHAT) ---"
  if fresh_router "$HOME/llama-cuda12" "$RID" 8192 && assert_shim_tag "$TAG" 11500; then
    "$HERE/bench_off.sh" "$TAG" "$SLUG" 5 "$WHAT"
  else
    log "!!! SKIPPED $SLUG thinking-off: preflight failed"
  fi

  if [ "$THINK" != "yes" ]; then
    log "--- QUEUE-1: $SLUG has no think leg here ---"; continue
  fi
  log "--- QUEUE-1: $SLUG thinking-on ---"
  if fresh_router "$HOME/llama-cuda12" "$RID" 16384 && assert_shim_tag "$TAG" 11501; then
    u=$(gpu_mib); log "$SLUG: GPU $u MiB with ctx 16384 loaded"
    "$HERE/bench_think.sh" "$TAG" "$SLUG" 12288 16384 2400
  else
    log "!!! SKIPPED $SLUG thinking-on: preflight failed"
  fi
done

stop_router
start_router "$HOME/llama-cuda12" 8192
log "================ QUEUE-1 DONE ================"
"$HOME/Projects/Tests/.venv/bin/python" "$HERE/summarise.py" 5 2>&1 | tee -a "$RUN/driver.log"
