#!/usr/bin/env bash
# Full-context probe of the Q6_K preset through :8080 (check.py: 3 decode prompts + fill to ctx-1024).
cd "$(dirname "$0")"
M=qwen3.8-27b-q6-mtp
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a driver.log; }
WATCH_ALIAS=$M ./watchdog.sh & wd=$!
trap 'kill $wd 2>/dev/null' EXIT
systemctl --user restart llama-router; sleep 5
until curl -sf localhost:8080/health >/dev/null; do sleep 1; done
log "probe $M ctx 131072 start, RAM avail $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) MiB"
./check.py $M 131072 > last-probe.json; rc=$?
log "probe rc=$rc $(python3 -c "import json;r=json.load(open('last-probe.json'));print('load_s',r.get('load_s'),'peak',r.get('peak_mib'),'free',r.get('free_mib'),'decode',r.get('decode_mean'),r.get('decode'),'deep',r.get('deep_decode_tps'),'prefill',r.get('prefill_tps'),'fill_s',r.get('fill_wall_s'),'http',r.get('fill_http'),r.get('error',''))" 2>&1)"
log "probe RAM $(tail -1 watchdog.log)"
log "probe DONE"
