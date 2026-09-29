#!/usr/bin/env bash
# First full rig run, scheduled for 2026-09-26 21:00 (systemd user timer rig-first-stack).
# Part 1: five qwen3.6-35b-a3b configs on flows + bench40. Part 2: the dense 27B in all three
# roles, flows only (it is ~5x slower). Both write to this folder; drive.sh stops the :8080
# devstral service for each part and restores it afterwards.
set -uo pipefail
OUT=~/Projects/Tests/2026-09-26/rig/first-stack
RIG=~/Projects/Tests/rig
cd "$RIG"
echo "[$(date +'%F %T')] part 1 starting" >> "$OUT/schedule.log"
./drive.sh --config v8-qwen36moe.json --config qwen36moe-careful.json --config qwen36moe-full-self.json \
           --config qwen36moe-loop.json --config qwen36moe-gptoss-review.json \
           --suite flows --suite bench40 --out "$OUT" --name first-stack
echo "[$(date +'%F %T')] part 1 rc=$?; part 2 starting" >> "$OUT/schedule.log"
./drive.sh --config qwen36-27b-full-self.json --suite flows --out "$OUT" --name first-stack
echo "[$(date +'%F %T')] part 2 rc=$?; done" >> "$OUT/schedule.log"
