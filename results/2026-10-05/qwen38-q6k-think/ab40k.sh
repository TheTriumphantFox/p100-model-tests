#!/usr/bin/env bash
# Decode A/B at 40k, same check.py prompts, temp 0, no anti-loop sampling: Q8_0 vs UD-Q6_K.
cd "$(dirname "$0")"
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a driver.log; }
systemctl --user restart llama-router; sleep 5
until curl -sf localhost:8080/health >/dev/null; do sleep 1; done
for m in tmp-q8-40k tmp-q6-40k; do
  WATCH_ALIAS=$m ./watchdog.sh & wd=$!
  ./check.py $m 40960 > last-$m.json; rc=$?
  kill $wd
  log "$m rc=$rc $(python3 -c "import json;r=json.load(open('last-$m.json'));print('peak',r.get('peak_mib'),'decode',r.get('decode_mean'),[d['tps'] for d in r['decode']],'acc',[round(d['draft_acc']/d['draft_n'],2) for d in r['decode']],'deep',r.get('deep_decode_tps'),'prefill',r.get('prefill_tps'))" 2>&1)"
done
log "ab40k DONE"
