#!/usr/bin/env bash
# Wait for run-queue-6d's PHASE B to finish, then hand the rig to run-queue-6e, which
# inserts the two thinking-on shelf baselines BEFORE Phase A. 6d would otherwise roll
# straight into Phase A, so this kills it at the boundary. Written as a FILE, launched
# once, never edited while running.
set -uo pipefail
RUN=~/Projects/Tests/2026-09-19/candidates-round2
Q6D=$1
log() { echo "[$(date +%T)] handover: $*" | tee -a "$RUN/driver.log"; }

# Only look at driver.log after 6d's own start marker -- the file still carries lines from
# the abandoned 6b/6c attempts, and a bare grep matches those.
until awk '/QUEUE-6D START/{f=1} f' "$RUN/driver.log" | grep -q 'PHASE B COMPLETE'; do
  kill -0 "$Q6D" 2>/dev/null || { log "6d exited before PHASE B COMPLETE; not handing over"; exit 1; }
  sleep 10
done
log "PHASE B complete; stopping 6d before it starts Phase A"
kill "$Q6D" 2>/dev/null; sleep 3; kill -9 "$Q6D" 2>/dev/null
pkill -9 -f 'mmlu-pro-benchmark/[b]enchmark.py' 2>/dev/null
pkill -9 -f 'humaneval-benchmark/[b]enchmark.py' 2>/dev/null
pkill -9 -f '[l]lm_benchmark.py' 2>/dev/null
for p in $(ps -eo pid,args | grep '[l]lama-server' | grep -v 'llama-models' | awk '{print $1}'); do
  kill -9 "$p" 2>/dev/null
done
for i in $(seq 1 60); do
  u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}')
  [ "${u:-9999}" -lt 1000 ] && break
  sleep 2
done
# 6d may have started Phase A's first model; drop anything partial it left behind.
rm -rf "$RUN/throughput/qwen38-ud-q6k.json" "$RUN/throughput/qwen38-ud-q6k.log" \
       "$RUN"/mmlu-qwen38-ud-q6k-* "$RUN"/humaneval-qwen38-ud-q6k*
log "rig clear (GPU $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}') MiB); launching 6e"
cd "$RUN"
nohup ./run-queue-6e.sh > queue-6e.out 2>&1 &
echo $! > "$RUN/q6e.pid"
log "6e launched, pid $(cat "$RUN/q6e.pid")"
