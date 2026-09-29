#!/usr/bin/env bash
# Verification of the 2026-09-26 23:40 fixes: typed reporter values, careful tool-loop persona.
set -uo pipefail
OUT=~/Projects/Tests/2026-09-26/rig/fixes-check
cd ~/Projects/Tests/rig
echo "[$(date +'%F %T')] part 1 starting" >> "$OUT/schedule.log"
./drive.sh --config qwen36moe-loop-careful.json --config qwen36moe-loop.json --config qwen36moe-careful.json \
           --config qwen36moe-full-self.json --suite flows --suite bench40 --out "$OUT" --name fixes-check
echo "[$(date +'%F %T')] part 1 rc=$?; part 2 starting" >> "$OUT/schedule.log"
./drive.sh --config qwen36-27b-full-self.json --suite flows --out "$OUT" --name fixes-check
echo "[$(date +'%F %T')] part 2 rc=$?; done" >> "$OUT/schedule.log"
