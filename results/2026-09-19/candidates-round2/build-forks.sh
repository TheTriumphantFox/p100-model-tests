#!/usr/bin/env bash
# Two of the four candidates declare architectures that are not upstream yet:
#   xing4_0 -> open PR ggml-org/llama.cpp#29141 (fairydreaming:xing4_0-port)
#   g9v3    -> linuxid10t/llama.cpp:feature/g9v3-support
# Build each into its own runtime dir so the production ~/llama-cuda12 is untouched.
set -uo pipefail
LOG=/home/hm/Projects/Tests/2026-09-19/candidates-round2/build-forks.log
: > "$LOG"
b() { # repo ref out
  echo "=== $(date +%T) BUILD $1 $2 -> $3" >> "$LOG"
  t0=$(date +%s)
  REPO="$1" REF="$2" OUT="$3" /home/hm/Projects/Tests/scripts/build_llama_cuda12.sh >> "$LOG" 2>&1
  echo "=== $(date +%T) rc=$? wall=$(( $(date +%s)-t0 ))s" >> "$LOG"
}
b https://github.com/fairydreaming/llama.cpp.git xing4_0-port         /home/hm/llama-cuda12-xing
b https://github.com/linuxid10t/llama.cpp.git    feature/g9v3-support /home/hm/llama-cuda12-g9v3
echo "BUILDS DONE $(date +%T)" >> "$LOG"
