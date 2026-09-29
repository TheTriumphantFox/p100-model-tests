#!/usr/bin/env bash
# Download the four 2026-09-19 round-2 candidates. Sequential: clean per-file timing,
# and the first model can start benchmarking while the rest land.
set -uo pipefail
DL=/var/lib/ollama/candidates-r2
LOG=/home/hm/Projects/Tests/2026-09-19/candidates-round2/download.log
: > "$LOG"
dl() { # repo file
  echo "=== $(date +%T) START $1 :: $2" >> "$LOG"
  t0=$(date +%s)
  /home/hm/.local/bin/hf download "$1" "$2" --local-dir "$DL" >> "$LOG" 2>&1
  rc=$?
  t1=$(date +%s)
  sz=$(stat -c %s "$DL/$2" 2>/dev/null || echo 0)
  echo "=== $(date +%T) DONE rc=$rc wall=$((t1-t0))s bytes=$sz ($(echo "scale=1;$sz/1000000000"|bc) GB) rate=$(echo "scale=1;$sz/1000000/($t1-t0+1)"|bc) MB/s" >> "$LOG"
}
dl ornith-ai/Ornith-1.5-35B-A3B-GGUF            Ornith-1.5-35B-Q4_K_M.gguf
dl bartowski/nvidia_Nemotron-Cascade-2-30B-A3B-GGUF nvidia_Nemotron-Cascade-2-30B-A3B-Q4_K_M.gguf
dl XingChen-AGI/Xing4.0-29B-A4B-GGUF            xing4_0-29b-IQ4_NL.gguf
dl linuxid10t/G9v3-39A5B-GGUF                   G9v3-39A5B-Q4_K_M.gguf
echo "ALL DONE $(date +%T)" >> "$LOG"
