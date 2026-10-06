#!/usr/bin/env bash
# run.sh LABEL CTX [KEY=VALUE ...] -- probe qwen3.8-27b-mtp at CTX with extra preset keys
# (VALUE "-" removes a key),
# through the :8080 router exactly as pi gets it, under the host-RAM watchdog.
cd "$(dirname "$0")"
M=qwen3.8-27b-mtp label=$1 ctx=$2; shift 2
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a driver.log; }
./watchdog.sh & wd=$!
trap 'kill $wd 2>/dev/null' EXIT
./set_preset.py $M ctx-size=$ctx "$@" | tee -a driver.log
systemctl --user restart llama-router; sleep 5
until curl -sf localhost:8080/health >/dev/null; do sleep 1; done
curl -s localhost:8080/models | python3 -c "import json,sys;a=[m for m in json.load(sys.stdin)['data'] if m['id']=='$M'][0]['status']['args'];print('router args:',' '.join(a[a.index('--alias')+2:]))" | tee -a driver.log
log "$label start, RAM avail $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) MiB"
./check.py $M $ctx > "last-$label.json"; rc=$?
log "$label ctx=$ctx rc=$rc $(python3 -c "import json;r=json.load(open('last-$label.json'));print('load_s',r.get('load_s'),'peak',r.get('peak_mib'),'free',r.get('free_mib'),'decode',r.get('decode_mean'),'deep',r.get('deep_decode_tps'),'prefill',r.get('prefill_tps'),'fill_s',r.get('fill_wall_s'),'http',r.get('fill_http'),r.get('error',''))" 2>&1)"
log "$label RAM min $(tail -1 watchdog.log)"
log "$label DONE"
