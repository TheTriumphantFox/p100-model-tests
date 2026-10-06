#!/usr/bin/env bash
# 2026-10-02: qwen3.8-flash-next IQ2_XXS on the 2026-09-30 harness (copied from qwen36-q8kp),
# paired against the incumbent q5_k_p. Original header follows.
# Q8_K_P vs the incumbent Q5_K_P: same HauhauCS Aggressive abliteration, two quant levels.
# Every leg uses the exact settings of the incumbent's 2026-09-19 baselines (per-category 5,
# seed 42, router ctx 8192 thinking-off / 16384 thinking-on, num_predict 12288, timeout
# 2400), so each result pairs question-by-question against them with mcnemar.py.
#
#   run.sh [router-id ollama-tag slug]     default: the Q8_K_P
#   queue.sh runs every model in turn; use that rather than this directly.
#
# Expected wall time ~3.5 h at ~10 tok/s: HumanEval ~75 min, MMLU think ~80 min,
# throughput ~15 min, MMLU off and the ladder a few minutes.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
T=~/Projects/Tests
# shellcheck source=../../2026-09-21/cuda-matrix/lib.sh
source "$T/2026-09-21/cuda-matrix/lib.sh"
RUN=$HERE                                  # lib.sh points RUN at the matrix; log here instead

RID=${1:-qwen3.8-flash-next_iq2_xxs}
TAG=${2:-qwen3.8-flash-next:iq2_xxs}
SLUG=${3:-flashnext-iq2}
RT=$HOME/llama-cuda12
BASE=$T/2026-09-19/candidates-round2      # incumbent runs, same blob sha256 9200d792...
# The 31.96 GB weights leave ~2.2 GB of the 32 GB, so a PARTIAL spill is the likely
# failure. lib.sh's assert_on_gpu passes anything above 90% of the weights, which here
# would let ~3 GB of layers sit in system RAM unnoticed. Decode rate is the real tell:
# the incumbent runs 11.14 tok/s and the 27.7 GB Qwen3.8 Q8_0 10.91, while a spill
# measured 5.00 where the truth was 12.32.
# 2026-10-02 FLASH-NEXT: 75 GB on 32 GB of VRAM, so --fit (left on) puts experts in RAM BY DESIGN
# and the VRAM-resident check below is disabled. Its healthy decode is ~17 tok/s (pi-context);
# a page-cache thrash collapses it toward 1 tok/s, so the floor is what guards this run.
TPS_FLOOR=${TPS_FLOOR:-10.0}
# ...and the floor alone is not enough. ~/llama-cuda12 defaults to `-ngl auto --fit on`
# with a 1024 MiB per-device margin, so a file that nearly fills the cards gets a FEW layers
# quietly left in RAM: the first Q8_K_P attempt lost ~2 layers and only ~15% speed, well
# above the floor (see q8kp-VOID-fit-partial-offload/). So VRAM is checked too, against
# what a fully-offloaded qwen35 27B measures here: non-embedding weights + 1082 MiB +
# 72 KiB/token of f16 KV (fits the incumbent at 8192 and the Unsloth Q8_0 at 8192, 16384
# and 32768 to the MiB). One layer is ~450 MiB, so a 300 MiB shortfall means a spill.
# ROUTER_EXTRA passes flags to the router, e.g. "--fit off -ngl 999" to forbid CPU layers.
read -r -a ROUTER_EXTRA <<<"${ROUTER_EXTRA:-}"
NONEMBED_MIB=0   # unused for flash-next (see TPS_FLOOR note)

[ -d "$BM/$RID" ] || { log "!!! $BM/$RID/ missing (split GGUF subdir)"; exit 1; }

# The GPU must be empty. Whatever holds it is the owner's (ollama, or :8080 with a model
# loaded) -- report it and stop; never kill it from here.
u=$(gpu_mib)
if [ "$u" -ge "$VRAM_FLOOR" ] && [ -z "$(router_pid)" ]; then
  log "!!! GPU holds $u MiB and it is not the bench router. Holders:"
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader \
    | while IFS=, read -r p m; do echo "    $m  $(ps -o args= -p "$p" | cut -c1-140)"; done \
    | tee -a "$RUN/driver.log"
  log "!!! Unload it (ollama stop <model>, or let :8080 idle out) and rerun. Not touching it."
  exit 2
fi

PIDS=()
cleanup() { for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done; stop_router; }
trap cleanup EXIT

start_shim() {   # $1 port [flags...]
  local port=$1 i; shift
  if [ -n "$(port_pid "$port")" ]; then log "shim :$port already up (pid $(port_pid "$port")) -- reusing"; return 0; fi
  nohup "$T/.venv/bin/python" "$T/scripts/ollama_shim.py" \
    --router "http://127.0.0.1:$BENCH_PORT" --port "$port" "$@" >> "$RUN/shim-$port.log" 2>&1 &
  PIDS+=($!)
  for i in $(seq 1 20); do sleep 1; [ -n "$(port_pid "$port")" ] && break; done
  log "shim :$port started $* (pid $(port_pid "$port"))"
}
start_shim 11500
start_shim 11501 --force-think
"$T/.venv/bin/python" "$HERE/watchdog.py" "$PROD_PID" 45 >> "$RUN/watchdog.out" 2>&1 &
PIDS+=($!)

# One ladder rung: (re)start the router at this ctx/KV, load, measure. Leaves it loaded.
STATUS=
rung() {   # $1 ctx, $2 kv
  local ctx=$1 kv=$2 vram probe tps ok w
  w=$(( $(stat -Lc %s "$BM/$RID"/*.gguf | awk '{s+=$1} END{print s}') / 1048576 ))
  if ! fresh_router "$RT" "$RID" "$ctx" --cache-type-k "$kv" --cache-type-v "$kv" "${ROUTER_EXTRA[@]}"; then
    STATUS=router-failed
  else
    warm_model "$TAG" 11500
    vram=$(gpu_mib)
    probe=$(py "$HERE/probe.py" "$TAG" 11500 200 1800)
    tps=$(echo "$probe" | py -c 'import json,sys; print(json.load(sys.stdin).get("tok_per_s") or 0)' 2>/dev/null || echo 0)
    ok=$(echo "$probe" | py -c 'import json,sys; print("1" if json.load(sys.stdin).get("ok") else "0")' 2>/dev/null || echo 0)
    if [ "$ok" != 1 ]; then STATUS=failed
    elif awk -v t="$tps" -v f="$TPS_FLOOR" 'BEGIN{exit !(t < f)}'; then STATUS=spilled
    elif false && [ "$kv" = f16 ] && [ "$vram" -lt $(( NONEMBED_MIB + 1082 + ctx * 72 / 1024 - 300 )) ]; then
      STATUS=spilled
      log "!!! $SLUG ctx=$ctx: $vram MiB on GPU, expected ~$(( NONEMBED_MIB + 1082 + ctx * 72 / 1024 )) fully offloaded -- layers are in RAM"
    else STATUS=resident; fi
  fi
  log "$SLUG ctx=$ctx kv=$kv -> $STATUS, ${vram:-?} MiB on GPU, weights $w MiB, ${tps:-0} tok/s (floor $TPS_FLOOR)"
  echo "{\"slug\":\"$SLUG\",\"ctx\":$ctx,\"kv\":\"$kv\",\"weights_mib\":$w,\"vram_mib\":${vram:-0},\"tok_per_s\":${tps:-0},\"status\":\"$STATUS\",\"probe\":${probe:-null}}" >> "$RUN/ctx-ladder.jsonl"
  [ "$STATUS" = resident ]
}

log "================ $SLUG RUN START (prod :$PROD_PORT pid=${PROD_PID:-none}) router extra: ${ROUTER_EXTRA[*]:-none} ================"

# ---- thinking-off: MMLU 96/2048, HumanEval, throughput at ctx 8192 -----------------------
if rung 8192 f16; then
  "$HERE/bench_off.sh" "$TAG" "$SLUG" 5 mmlu96,mmlu2048,humaneval,throughput
else
  log "!!! $SLUG does not run cleanly at ctx 8192 ($STATUS). Nothing is comparable."
  exit 3
fi

# ---- thinking-on at ctx 16384; fall back to q8_0 KV only if f16 does not fit -------------
THINK_KV=f16
if ! rung 16384 f16; then
  THINK_KV=q8_0
  rung 16384 q8_0 || THINK_KV=
fi
if [ -n "$THINK_KV" ]; then
  [ "$THINK_KV" != f16 ] && log "!!! NOTE: think leg uses KV q8_0; the incumbent baseline used f16."
  "$HERE/bench_think.sh" "$TAG" "$SLUG" 12288 16384 2400
else
  log "!!! $SLUG: no thinking-on leg -- ctx 16384 does not fit with either KV type"
fi

# ---- how much context is left (informational, ~1 min) ---------------------------------------
rung 32768 f16 || true

# ---- pair against the incumbent -------------------------------------------------------------
{
  echo "# paired McNemar, incumbent q5_k_p (A) vs $SLUG (B) -- $(date '+%F %T')"
  for p in "humaneval-qwen36-rerun humaneval-$SLUG" \
           "mmlu-qwen36-rerun-96 mmlu-$SLUG-pc5-np96" \
           "mmlu-qwen36-rerun-2048 mmlu-$SLUG-pc5-np2048" \
           "mmlu-qwen36-rerun-think12288 mmlu-$SLUG-pc5-think12288"; do
    set -- $p
    echo; echo "## $2"
    if [ -f "$RUN/$2/results.json" ]; then
      py "$T/2026-09-21/cuda-matrix/mcnemar.py" "$BASE/$1" "$RUN/$2" incumbent-q5kp "$SLUG"
    else echo "(no run)"; fi
  done
} 2>&1 | tee "$RUN/pairs-$SLUG.txt" | tee -a "$RUN/driver.log"

log "================ $SLUG RUN DONE -- see pairs-$SLUG.txt, ctx-ladder.jsonl ================"
