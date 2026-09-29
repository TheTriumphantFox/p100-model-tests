#!/usr/bin/env bash
# Round 2, part 3: the shelf's Qwen3.8-27B, scored on the CUDA build for the first time.
# It has never been measured on anything but Vulkan, and Artificial Analysis ranks it the
# top small open model - so "does a Qwen3.8 clear 10 tok/s here" deserves a measurement
# rather than the bandwidth estimate. No download: the blob is already on the shelf.
set -uo pipefail
RUN=~/Projects/Tests/2026-09-19/candidates-round2
for i in $(seq 1 3000); do grep -q "QUEUE-2 DONE" "$RUN/driver.log" && break; sleep 20; done
echo "[$(date +%T)] QUEUE-3 START" >> "$RUN/driver.log"
"$RUN/bench_one2.sh" 'qwen3.8-27b-stock:q4_k_m' qwen38-27b
echo "[$(date +%T)] QUEUE-3 DONE" >> "$RUN/driver.log"
