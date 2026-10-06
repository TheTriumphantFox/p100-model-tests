#!/usr/bin/env bash
# Raise each pi model's ctx to the largest value that fills to ctx-1024 and keeps >=600 MiB
# free per card (the rule from the devstral warmup OOM). Reverts on failure.
cd "$(dirname "$0")"
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a driver.log; }
idle_restart() {
  last() { journalctl --user -u llama-router -n 1 --no-pager -o short-unix | awk '{print int($1)}'; }
  while :; do
    now=$(date +%s); l=$(last)
    util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | sort -n | tail -1)
    [ $((now - l)) -ge 120 ] && [ "$util" -lt 10 ] && break
    sleep 15
  done
  systemctl --user restart llama-router; sleep 5
  until curl -sf localhost:8080/health >/dev/null; do sleep 1; done
}
try() {  # model new old minfree
  m=$1 new=$2 old=$3 minfree=$4
  ./set_ctx.py "$m" "$new" | tee -a driver.log; idle_restart
  free -m | awk 'NR==2{print "RAM used "$3" MiB, avail "$7}' | tee -a driver.log
  ./check.py "$m" "$new" > "last-$m.json"; rc=$?
  ok=$(python3 -c "import json;r=json.load(open('last-$m.json'));print(int(r.get('fill_http')==200 and min(r.get('free_mib',[0]))>=$minfree))" 2>/dev/null || echo 0)
  log "$m ctx=$new rc=$rc ok=$ok $(python3 -c "import json;r=json.load(open('last-$m.json'));print('peak',r.get('peak_mib'),'free',r.get('free_mib'),'decode',r.get('decode_mean'),'deep',r.get('deep_decode_tps'),'prefill',r.get('prefill_tps'),'fill_s',r.get('fill_wall_s'))" 2>/dev/null)"
  if [ "$ok" != 1 ]; then ./set_ctx.py "$m" "$old" | tee -a driver.log; log "$m REVERTED to $old"; fi
}
try qwen3.6-35b-a3b-planner-mtp 55296 49152 600
try qwen3.6-27b-abliterated 120832 114688 600
# Flash-Next runs under --fit (keeps ~1 GiB free per card by itself), so the VRAM floor is moot;
# the question is whether 256k loads, fills and still decodes at a usable speed.
try qwen3.8-flash-next-iq2 262144 131072 0
idle_restart
log ALL_DONE
