#!/usr/bin/env bash
# 2026-10-05 21:00: MMLU-Pro thinking-on, full 70 questions (seed 42, per-category 5, np 12288,
# ctx 16384, timeout 2400 -- the 10-02 settings), for both models WITH the anti-loop preset
# (temp 1.0/top-p 0.95/top-k 20, reasoning-effort medium, reasoning-budget 6144), served by
# the :8080 production router exactly as pi gets them.
#   A: harness sampling (temp 0)        -> pairs with the 09-19 / 10-02 thinking-on runs
#   B: --server-sampling (preset temps) -> the whole fix, as pi gets it
# Thinking-off legs are left out on purpose: the fix can't change them.
set -uo pipefail
T=~/Projects/Tests; RUN=$T/2026-10-05/think-fix-full
PY=$T/.venv/bin/python
MODELS=${MODELS:-"qwen3.8-27b-q6-mtp:qwen3.8-27b:ud-q6k-prod:q6k qwen3.8-flash-next-iq2:qwen3.8-flash-next:iq2-prod:flashnext"}
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a "$RUN/driver.log"; }
PIDS=()
trap 'for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done' EXIT
cd "$RUN"

# Don't evict a model pi is using: wait until :8080 has logged nothing for 5 min (max 2 h).
wait_idle() {
  local t0 last
  t0=$(date +%s)
  while :; do
    last=$(journalctl --user -u llama-router -n 1 --no-pager -o short-unix | awk '{print int($1)}')
    [ $(( $(date +%s) - last )) -ge 300 ] && return 0
    [ $(( $(date +%s) - t0 )) -ge 7200 ] && { log "!!! :8080 still busy after 2 h -- going ahead anyway"; return 0; }
    sleep 30
  done
}

shim() { local port=$1; shift
  "$PY" "$T/scripts/ollama_shim.py" --router http://127.0.0.1:8080 \
    --models-dir /home/hm/llama-models --port "$port" --force-think "$@" >> "$RUN/shim-$port.log" 2>&1 &
  PIDS+=($!); sleep 2; }

log "================ NIGHT START: models $MODELS"
wait_idle
log ":8080 idle; starting shims 11504 (temp 0) / 11505 (server sampling)"
shim 11504
shim 11505 --server-sampling

for spec in $MODELS; do
  IFS=: read -r rid tag1 tag2 slug <<<"$spec"; tag="$tag1:$tag2"
  WATCH_ALIAS=$rid FLOOR_MIB=6144 ./watchdog.sh & wd=$!
  log "---- $slug ($rid as $tag): preflight, RAM avail $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) MiB"
  pf=$("$PY" "$T/scripts/think_probe.py" --model "$tag" --port 11504 --port 11505 --num-predict 12288 --timeout 2400 2>&1)
  echo "$pf" | tee -a "$RUN/preflight-$slug.txt" >> "$RUN/driver.log"
  if [ "$(echo "$pf" | grep -c 'REASONED')" -ne 2 ]; then
    log "!!! $slug preflight: both shims must REASON -- skipping this model"; kill $wd; continue
  fi
  for leg in A:11504 B:11505; do
    name=${leg%%:*}; port=${leg##*:}; OUT=$RUN/mmlu-$slug-$name
    log "$slug leg $name via :$port start"
    t0=$(date +%s)
    "$PY" "$T/2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py" run \
      --base-url "http://127.0.0.1:$port" --model "$tag" --num-ctx 16384 --num-predict 12288 \
      --per-category 5 --api-timeout 2400 --output "$OUT" > "$OUT.log" 2>&1
    rc=$?
    log "$slug leg $name rc=$rc $(( ($(date +%s) - t0) / 60 )) min: $("$PY" - "$OUT" <<'EOF'
import json, sys
try:
    r = json.load(open(sys.argv[1] + "/results.json"))
except Exception as e:
    print(f"RIG-FAIL no results.json ({e})"); sys.exit()
s = r["model_summaries"][0]; b = r["batches"]
n = len(r["results"]); capped = sum(1 for x in b if (x.get("eval_count") or 0) >= 12288)
tok = sum((x.get("eval_count") or 0) for x in b)
flag = "" if n == 70 else f" RIG-FAIL only {n}/70 results"
print(f"{s['accuracy']:.2f}% ({s['correct']}/{s['total']}), parsed {s['parsed']}, "
      f"{tok} gen tokens, {capped} batches at the 12288 cap{flag}")
EOF
)"
  done
  kill $wd 2>/dev/null
  log "$slug RAM $(tail -1 watchdog.log)"
done

"$PY" "$RUN/summarize.py" > "$RUN/summary.md" 2>&1
log "================ NIGHT DONE -- summary.md"
