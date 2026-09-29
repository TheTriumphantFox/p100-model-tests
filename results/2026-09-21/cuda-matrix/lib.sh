#!/usr/bin/env bash
# Shared rig control for the 2026-09-21 CUDA matrix. Source this; do not run it.
#
# WHAT IS DIFFERENT FROM candidates-round2/run-queue-7.sh, and why:
#
# 1. stop_router kills the bench router's children BY PPID, never by command-line
#    pattern. The old pattern was '[l]lama-server --host 127.0.0.1 --jinja', which is
#    the EXACT prefix the PRODUCTION router on :8080 uses for its own child when
#    devstral is loaded on demand. Nothing in round 2 hit this only because devstral
#    happened to be cold every time. The brief says never touch :8080, so the pattern
#    kill is gone: children are enumerated from the router pid BEFORE the parent is
#    killed (after that they reparent to init and the link is lost), and PROD_PID is
#    asserted alive after every stop.
#
# 2. If VRAM does not drop below the floor, we STOP. The old code fell through and let
#    the next model load onto a dirty GPU, which llama.cpp does silently by leaving
#    layers in system RAM -- a quarter-speed run that looks like a model result.
#
# Everything else that was learned the hard way is kept:
#   * the router enumerates --models-dir ONLY at startup -> restart after adding a GGUF
#   * a model load and a CPU spill look identical for ~150s; judge no earlier than 300s
#   * `bc` is not installed -> awk
#   * never edit a running bash script; bash reads it by file offset
#   * track PIDs from $!; pgrep/pkill -f matches the shell that runs it
set -uo pipefail

T=~/Projects/Tests
RUN=$T/2026-09-21/cuda-matrix
BM=~/llama-bench-models
BENCH_PORT=8081
PROD_PORT=8080
VRAM_FLOOR=1500          # MiB; above this the GPU is dirty and we refuse to load

mkdir -p "$RUN"
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a "$RUN/driver.log"; }
py() { "$T/.venv/bin/python" "$@"; }

port_pid() { ss -ltnpH "sport = :$1" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
router_pid() { port_pid $BENCH_PORT; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }

# Recorded once, at source time, so every stop can prove it did not touch production.
PROD_PID=$(port_pid $PROD_PORT)
assert_prod_alive() {
  local now; now=$(port_pid $PROD_PORT)
  if [ -n "$PROD_PID" ] && [ "$now" != "$PROD_PID" ]; then
    log "!!! ABORT: production router on :$PROD_PORT changed pid ($PROD_PID -> ${now:-GONE}). Stopping."
    return 1
  fi
  return 0
}

stop_router() {
  local p kids i u
  p=$(router_pid)
  if [ -n "$p" ]; then
    # Enumerate children FIRST: once the parent dies they reparent to init.
    kids=$(ps -eo pid,ppid,comm | awk -v pp="$p" '$2==pp && $3 ~ /llama-server/ {print $1}')
    kill "$p" 2>/dev/null
    for i in $(seq 1 30); do sleep 2; [ -z "$(router_pid)" ] && break; done
    for k in $kids; do kill "$k" 2>/dev/null; done
  fi
  for i in $(seq 1 90); do u=$(gpu_mib); [ "${u:-99999}" -lt "$VRAM_FLOOR" ] && break; sleep 2; done
  u=$(gpu_mib)
  log "router stopped (was pid ${p:-none}, children: ${kids:-none}); GPU $u MiB after ${i}x2s"
  assert_prod_alive || return 1
  if [ "${u:-99999}" -ge "$VRAM_FLOOR" ]; then
    log "!!! RIG-FAIL: $u MiB still held after stop_router. Refusing to continue; a load onto a"
    log "!!!           dirty GPU spills to CPU silently and yields a plausible wrong number."
    return 1
  fi
  return 0
}

start_router() {   # $1 runtime dir, $2 ctx  [$3.. extra args]
  local rt=$1 ctx=$2 p i; shift 2
  nohup env LD_LIBRARY_PATH="$rt/lib" "$rt/bin/llama-server" \
    --models-dir "$BM" --models-autoload --models-max 1 \
    --host 127.0.0.1 --port $BENCH_PORT --ctx-size "$ctx" --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 "$@" \
    >> "$RUN/router-$BENCH_PORT.log" 2>&1 &
  for i in $(seq 1 90); do sleep 2; [ -n "$(router_pid)" ] && break; done
  p=$(router_pid)
  log "router started from $rt ctx=$ctx $* (pid ${p:-FAILED-TO-START})"
  [ -n "$p" ]
}

assert_listed() {
  local ids
  ids=$(curl -sf --max-time 30 "http://127.0.0.1:$BENCH_PORT/models" \
        | py -c 'import json,sys; print(" ".join(m["id"] for m in json.load(sys.stdin)["data"]))' 2>/dev/null)
  case " $ids " in *" $1 "*) return 0;; esac
  log "!!! RIG-FAIL: router does not list '$1'. Listed: $ids"
  log "!!!           The router enumerates --models-dir once, at startup. Restart it."
  return 1
}

assert_shim_tag() {   # $1 ollama tag, $2 shim port
  curl -sf --max-time 30 "http://127.0.0.1:$2/api/tags" | grep -q "\"$1\"" && return 0
  log "!!! RIG-FAIL: shim on :$2 does not advertise tag '$1' (is it in ollama_shim.py TAGS?)"
  return 1
}

fresh_router() {   # $1 runtime, $2 router-id, $3 ctx  [$4.. extra args]
  local rt=$1 rid=$2 ctx=$3; shift 3
  stop_router || return 1
  start_router "$rt" "$ctx" "$@" || return 1
  assert_listed "$rid"
}

# A model that does not fit is not refused by llama.cpp -- it silently leaves layers in
# system RAM and runs at a quarter speed, which reads as a model result. After a load,
# VRAM should be at least the weight file itself; well below that means layers stayed in
# RAM. Call only once the model is actually loaded (issue one request first).
assert_on_gpu() {   # $1 gguf path (follows symlinks), $2 label
  local want used
  want=$(( $(stat -Lc %s "$1") / 1048576 ))
  used=$(gpu_mib)
  if [ "$used" -lt $(( want * 9 / 10 )) ]; then
    log "!!! RIG-FAIL $2: $used MiB on the GPU but the weights alone are $want MiB."
    log "!!!           Layers stayed in system RAM -- this will run at a fraction of the"
    log "!!!           real speed and must not be reported. Lower the context or the KV quant."
    return 1
  fi
  log "$2: $used MiB resident, weights $want MiB -- fully offloaded"
  return 0
}

# Force the currently-selected model to load, so VRAM can be judged. The router loads
# on first request; a load and a CPU spill look identical for ~150s, so allow 300s+.
warm_model() {   # $1 ollama tag, $2 shim port
  curl -sf --max-time 600 "http://127.0.0.1:$2/api/chat" \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$1\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"stream\":false,\"options\":{\"num_predict\":1}}" \
    >/dev/null 2>&1
}

# Refuse to start a benchmark on a model that cannot serve a single token.
#
# WHY THIS EXISTS: on 2026-09-21 three models (gemma4-e4b, qwen3.6-27b-opus-distill,
# qwen3.6-35b-a3b-abliterated-vl) could not load on this build at all. Nothing checked, so
# the queue ran the full suite against each: qwen36-vl spent THIRTY MINUTES failing all 164
# HumanEval tasks on a 10-second retry loop, and opus-distill had started doing the same
# before a human happened to look. A 30-second check in front of each row would have caught
# all three. warm_model and probe.py already existed; they simply were not wired in.
#
# The check is deliberately cheap and deliberately BLOCKING: no result is worth more than
# proving the model answers at all.
preflight_serves() {   # $1 ollama tag, $2 shim port, $3 label
  local out ok
  log "$3: preflight -- can this model serve one token?"
  warm_model "$1" "$2"
  out=$(py "$RUN/probe.py" "$1" "$2" 16 900 2>/dev/null)
  ok=$(printf '%s' "$out" | py -c 'import json,sys; print("1" if json.load(sys.stdin).get("ok") else "0")' 2>/dev/null)
  if [ "${ok:-0}" = "1" ]; then
    log "$3: preflight OK -- $out"
    return 0
  fi
  log "!!! $3: PREFLIGHT FAILED -- the model does not serve. $out"
  log "!!!   Skipping every leg for this model. Check router-8081.log for the load error;"
  log "!!!   'wrong number of tensors' or 'tensor ... not found' means this build cannot"
  log "!!!   load this file, which is UNRUNNABLE, not a score of zero."
  return 1
}
