#!/usr/bin/env bash
# Qwen3.8-27B from ggml-org's own repo: Q8_0 (fast kernel path on Pascal), Q4_K_M from the
# same conversion, and the two matched draft modules - MTP and DFlash. A drafter published
# with the model has the model's vocabulary by construction, which is what made
# speculative decoding a dead end for devstral.
set -uo pipefail
DL=/var/lib/ollama/candidates-r2
LOG=/home/hm/Projects/Tests/2026-09-19/candidates-round2/download-qwen38.log
: > "$LOG"
for f in mtp-Qwen3.8-27B-Q8_0.gguf dflash-Qwen3.8-27B-Q8_0.gguf Qwen3.8-27B-Q4_K_M.gguf Qwen3.8-27B-Q8_0.gguf; do
  echo "=== $(date +%T) START $f" >> "$LOG"; t0=$(date +%s)
  /home/hm/.local/bin/hf download ggml-org/Qwen3.8-27B-GGUF "$f" --local-dir "$DL" >> "$LOG" 2>&1
  echo "=== $(date +%T) rc=$? wall=$(( $(date +%s)-t0 ))s size=$(stat -c %s "$DL/$f" 2>/dev/null)" >> "$LOG"
done
echo "QWEN38 DOWNLOADS DONE $(date +%T)" >> "$LOG"
