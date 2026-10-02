#!/usr/bin/env bash
# Aider Polyglot, five local models, hard 10-hour cap.
#
# Every model works through the SAME prefix of order.txt (a fixed, language-stratified
# order of all 225 exercises), so scores are paired exercise by exercise. A later full run
# resumes from where this one stops: polyglot_run.py skips any exercise already scored.
#
# Phase A (calibration): each model runs the first K exercises. Its mean wall time per
#   exercise is then MEASURED, not guessed.
# Phase B: the remaining budget is split so every model reaches the same end index E.
#   Each model gets a deadline that leaves exactly the estimated time the models after it
#   need, so slack from an early finisher rolls forward and an overrun is cut instead of
#   eating someone else's slice. polyglot_run.py will not START an exercise it does not
#   expect to finish before its deadline.
# Hard cap: at T0+10h any running container is stopped, whatever it is doing.
#
# Safety: preflight every model (CANNOT LOAD is reported as such, never as a 0), a model
# that stops serving aborts itself after 4 empty exercises, and the :8081 router is
# stopped at the end so no model is left resident on the GPU.
set -uo pipefail

R=${R:-/home/hm/Projects/Tests/2026-10-01/aider-polyglot-10h}
B=/home/hm/llama-cuda12
BUDGET=${BUDGET:-36000}
K=${K:-6}
read -r -a MODELS <<< "${MODELS:-gpt-oss-20b_q8_0 qwen3.6-35b-a3b_ud-q6_k devstral-patched_q8_0 qwen3.6-27b-abliterated_q5_k_m qwen3.8-27b-unsloth_q8_0}"
# First guesses for the phase-A stop rule only, from the smoke tests (s/exercise).
declare -A GUESS=([gpt-oss-20b_q8_0]=90 [qwen3.6-35b-a3b_ud-q6_k]=140
                  [devstral-patched_q8_0]=420 [qwen3.6-27b-abliterated_q5_k_m]=450
                  [qwen3.8-27b-unsloth_q8_0]=460)
AIDER_COMMIT=5dc9490
HERE=$(dirname "$(readlink -f "$0")")   # ctr.sh and probe.py live beside this script

T0=$(date +%s); END=$((T0 + BUDGET))
if [ -n "${RESUME_E:-}" ]; then
  # Resume after a pause: the pause does not count. Budget left = BUDGET - (paused_at - first T0).
  read -r FIRST_T0 _ < "$R/budget.txt"
  PAUSED_AT=$(cat "$R/paused_at.txt")
  END=$((T0 + BUDGET - (PAUSED_AT - FIRST_T0)))
  # An explicit wall-clock stop (the overnight extension) replaces the leftover budget.
  [ -n "${HARD_END:-}" ] && END=$HARD_END
  echo "$FIRST_T0 $END resumed $T0" >> "$R/budget.history"
else
  echo "$T0 $END" > "$R/budget.txt"
fi
cd "$R"

log() { echo "[$(date +'%F %T')] $*" | tee -a "$R/driver.log"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }

start_router() {
  [ -n "$(router_pid)" ] && return 0
  nohup env LD_LIBRARY_PATH="$B/lib" "$B/bin/llama-server" \
    --models-dir /home/hm/llama-bench-models --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size 16384 --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 >> "$R/router-8081.log" 2>&1 &
  for _ in $(seq 1 60); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null && break; done
  log "router started (pid $(router_pid))"
}

stop_router() {
  local p; p=$(router_pid)
  [ -n "$p" ] && kill "$p" 2>/dev/null
  for _ in $(seq 1 30); do sleep 2; [ -z "$(router_pid)" ] && break; done
  # The router exits before its model child has released VRAM; wait for the memory itself.
  for _ in $(seq 1 60); do [ "$(gpu_mib)" -lt 1000 ] && break; sleep 2; done
  log "router stopped (was ${p:-none}); GPU $(gpu_mib) MiB"
}

# Anything on the GPU that is not a child of our router (e.g. pi loading devstral on the
# :8080 production router) would starve the benchmark. Log it loudly; do not kill it.
foreign_gpu() {
  local rp; rp=$(router_pid)
  # Ignore small holders: the compositor (kwin) and the idle :8080 router sit at <50 MiB.
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits 2>/dev/null |
  while IFS=', ' read -r p mib; do
    [ "${mib:-0}" -lt 500 ] && continue
    [ "$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')" = "$rp" ] || echo "$p(${mib}MiB)"
  done | sort -u | tr '\n' ' '
}

# Mean wall seconds per exercise for one model, from its progress.jsonl.
mean_wall() {
  python3 - "$R/runs/$1/progress.jsonl" <<'EOF'
import json, sys
try:
    w = [json.loads(l)["wall_s"] for l in open(sys.argv[1])]
except FileNotFoundError:
    w = []
print(round(sum(w) / len(w)) if w else 0)
EOF
}

count_done() { [ -f "$R/runs/$1/progress.jsonl" ] && wc -l < "$R/runs/$1/progress.jsonl" || echo 0; }

declare -A LOAD MEAN OK
run_model() {  # $1 model  $2 start  $3 end  $4 deadline  $5 est
  local m=$1 name="polyglot-${1//[^a-zA-Z0-9]/-}"
  local f; f=$(foreign_gpu); [ -n "$f" ] && log "!!! foreign process(es) on GPU: $f -- results for $m may be slowed or fail"
  CTR_NAME=$name R="$R" "$HERE/ctr.sh" python3 /scripts/polyglot_run.py run --order /run/order.txt \
    --model-id "$m" --outdir "/run/runs/$m" --settings /run/models.yml \
    --metadata /run/model-metadata.json --start "$2" --end "$3" --deadline "$4" \
    --est-secs "$5" --commit-hash "$AIDER_COMMIT" >> "$R/runs/$m.stdout" 2>&1 &
  local cpid=$!
  while kill -0 "$cpid" 2>/dev/null; do
    sleep 5
    if [ "$(date +%s)" -ge "$END" ]; then
      log "!!! HARD CAP reached -- stopping $m mid-exercise (that exercise is not scored)"
      podman stop -t 10 "$name" >/dev/null 2>&1; break
    fi
    if [ -z "$(router_pid)" ]; then
      log "!!! router died during $m -- stopping its container"; podman stop -t 10 "$name" >/dev/null 2>&1; break
    fi
  done
  wait "$cpid"; local rc=$?
  log "$m: rc=$rc, $(count_done "$m") exercises scored"
}

preflight() {  # loads the model; records load+first-reply wall time
  local m=$1 out
  out=$(python3 "$HERE/probe.py" "$m" 64 2>&1)
  echo "$out" >> "$R/preflight.jsonl"
  if python3 -c 'import json,sys; sys.exit(0 if json.loads(sys.argv[1]).get("ok") else 1)' "$out" 2>/dev/null; then
    LOAD[$m]=$(python3 -c 'import json,sys; print(int(json.loads(sys.argv[1])["wall_s"]))' "$out")
    log "$m: preflight OK (${LOAD[$m]}s incl. load)"
    return 0
  fi
  log "!!! $m: CANNOT LOAD / CANNOT SERVE -- $out. Dropped; this is not a score."
  return 1
}

mkdir -p "$R/runs"
log "=== start: budget ${BUDGET}s, hard end $(date -d @$END +'%F %T'), K=$K"
start_router

# ---------------- resume: every model to the same end index RESUME_E, nothing re-planned
if [ -n "${RESUME_E:-}" ]; then
  log "=== RESUME: target end index $RESUME_E, new hard end $(date -d @$END +'%F %T')"
  todo=()
  for m in "${MODELS[@]}"; do
    [ "$(count_done "$m")" -lt "$RESUME_E" ] || continue
    todo+=("$m"); MEAN[$m]=$(mean_wall "$m")
    # Load time from this model's last preflight record (the HDD-backed file is the slow one).
    LOAD[$m]=$(python3 - "$R/preflight.jsonl" "$m" <<'PY'
import json, sys
w = [json.loads(l)["wall_s"] for l in open(sys.argv[1]) if l.strip().startswith("{") and json.loads(l).get("model") == sys.argv[2]]
print(int(w[-1]) if w else 60)
PY
)
  done
  for i in "${!todo[@]}"; do
    m=${todo[$i]}; later=0
    for j in "${!todo[@]}"; do
      [ "$j" -gt "$i" ] || continue
      n=${todo[$j]}; later=$((later + LOAD[$n] + (RESUME_E - $(count_done "$n")) * MEAN[$n]))
    done
    dl=$((END - later))
    log "$m: resume at $(count_done "$m")/$RESUME_E, mean ${MEAN[$m]}s, deadline $(date -d @$dl +%T)"
    preflight "$m" || continue
    run_model "$m" 0 "$RESUME_E" "$dl" "${MEAN[$m]}"
  done
  stop_router
  log "=== finished at $(date +'%F %T') (resumed run${HARD_END:+, extension to $RESUME_E})"
  for m in "${MODELS[@]}"; do log "  $m: $(count_done "$m") exercises"; done
  exit 0
fi

# ---------------- phase A
for m in "${MODELS[@]}"; do
  [ "$(date +%s)" -ge "$END" ] && break
  preflight "$m" || continue
  OK[$m]=1
  # Calibration may take at most 2x its guess, and never past the hard end.
  dl=$(( $(date +%s) + K * ${GUESS[$m]} * 2 )); [ $dl -gt $END ] && dl=$END
  run_model "$m" 0 "$K" "$dl" "${GUESS[$m]}"
  MEAN[$m]=$(mean_wall "$m")
  log "$m: phase A mean ${MEAN[$m]}s/exercise"
done

# ---------------- plan phase B
live=(); sum=0; loads=0
for m in "${MODELS[@]}"; do
  [ -n "${OK[$m]:-}" ] && [ "${MEAN[$m]:-0}" -gt 0 ] || continue
  live+=("$m"); sum=$((sum + MEAN[$m])); loads=$((loads + LOAD[$m]))
done
now=$(date +%s); remain=$((END - now - loads - 300))
if [ ${#live[@]} -eq 0 ] || [ $remain -le 0 ] || [ $sum -le 0 ]; then
  log "no phase B (live=${#live[@]} remain=${remain}s)"; N2=0
else
  N2=$((remain / sum))
fi
E=$((K + N2)); [ $E -gt 225 ] && E=225
log "=== phase B plan: ${#live[@]} models, ${remain}s usable, sum of means ${sum}s -> +$N2 each, target end index $E"

# ---------------- phase B
if [ $N2 -gt 0 ]; then
  for i in "${!live[@]}"; do
    m=${live[$i]}
    later=0
    for j in "${!live[@]}"; do
      [ "$j" -gt "$i" ] && later=$((later + LOAD[${live[$j]}] + N2 * MEAN[${live[$j]}]))
    done
    dl=$((END - later))
    log "$m: phase B [$K,$E) deadline $(date -d @$dl +%T)"
    preflight "$m" || continue
    run_model "$m" "$K" "$E" "$dl" "${MEAN[$m]}"
  done
fi

stop_router
log "=== finished at $(date +'%F %T'), $(( ($(date +%s) - T0) / 60 )) min of ${BUDGET}s budget"
for m in "${MODELS[@]}"; do log "  $m: $(count_done "$m") exercises"; done
