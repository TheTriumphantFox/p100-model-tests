#!/usr/bin/env bash
# REPRODUCIBILITY PHASE -- run LAST, after the sweep.
#
# WHY: gpt-oss-20b scored 77.14% on 2026-09-19 and 71.43% on 2026-09-21 at identical
# settings (--per-category 5, seed 42, ctx 8192, num_predict 2048), generating 7,170 vs
# 5,348 tokens. Discordant 0/4 -- the re-run broke four questions and fixed none. The
# incumbent, by contrast, reproduced EXACTLY in round 2 -- but it generates 280 tokens in
# total thinking-off, against gpt-oss's 5-7k.
#
# THE HYPOTHESIS: run-to-run variance scales with generated-token volume. One flipped
# argmax diverges the generation and the divergence compounds. If true, the thinking-on
# column -- 40,000 to 120,000 tokens per run, never once repeated -- carries a variance
# that may exceed most of the gaps the matrix is being used to compare, and McNemar's
# assumption that the only variation is between models does not hold.
#
# THE DESIGN: four arms, ordered cheapest first, spanning three orders of magnitude of
# output length. Each arm repeats ONE measurement; the spread across repeats IS the result.
#
#   A  incumbent   MMLU-off  x3   ~280 tok/run     control: should be identical every time
#   B  gpt-oss     MMLU-off  x3   ~5-7k tok/run    the observed failure; 3 values settle it
#   C  gpt-oss     MMLU-off  x1   through a shim WITHOUT reasoning_effort -- discriminates
#                                 "nondeterminism" from "the shim changed between rounds"
#   D  incumbent   MMLU-ON   x2   ~44k tok/run     the column that matters; the incumbent is
#                                 the only model that ever terminated on all 14 batches
#
# Arms A-C are ~2 minutes each. Arm D is ~70 minutes per repeat and is the expensive half;
# it is last so that A-C are banked even if D is interrupted.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
source "$HERE/lib.sh"
PY=$HOME/Projects/Tests/.venv/bin/python
OUT=$RUN/repro
mkdir -p "$OUT"

INC_RID=qwen3.6-27b-abliterated_q5_k_m
INC_TAG=qwen3.6-27b-abliterated:q5_k_m
OSS_RID=gpt-oss-20b_q8_0
OSS_TAG=gpt-oss-20b:q8_0

mmlu_off() {   # $1 tag, $2 output dir, $3 shim port
  [ -f "$2/results.json" ] && { log "repro: $(basename "$2") already present"; return 0; }
  ( cd "$HOME/Projects/Tests" && "$PY" 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run \
      --base-url "http://127.0.0.1:$3" --model "$1" --num-ctx 8192 --num-predict 2048 \
      --per-category 5 --api-timeout 2400 --output "$2" ) > "$2.log" 2>&1
  log "repro: $(basename "$2") -> $("$PY" -c "
import json
d=json.load(open('$2/results.json')); s=d['model_summaries'][0]
t=sum(int(b.get('eval_count') or 0) for b in d['batches'])
print(f\"{s['accuracy']:.2f}% tok={t} tps={s.get('generation_tps') or 0:.1f}\")" 2>&1)"
}

log "================ REPRO PHASE START ================"

# ---- A: the control, 280 tokens per run ------------------------------------------------
log "--- REPRO A: incumbent MMLU-off x3 (control, ~280 tok/run) ---"
if fresh_router "$HOME/llama-cuda12" "$INC_RID" 8192 && assert_shim_tag "$INC_TAG" 11500; then
  for i in 1 2 3; do mmlu_off "$INC_TAG" "$OUT/A-incumbent-off-$i" 11500; done
else
  log "!!! REPRO A skipped: preflight failed"
fi

# ---- B: the observed failure, 5-7k tokens per run --------------------------------------
log "--- REPRO B: gpt-oss MMLU-off x3 (~5-7k tok/run) ---"
if fresh_router "$HOME/llama-cuda12" "$OSS_RID" 8192 && assert_shim_tag "$OSS_TAG" 11500; then
  for i in 1 2 3; do mmlu_off "$OSS_TAG" "$OUT/B-gptoss-off-$i" 11500; done

  # ---- C: same model, same router, shim without reasoning_effort ----------------------
  log "--- REPRO C: gpt-oss MMLU-off with NO reasoning_effort (shim on :11502) ---"
  nohup "$PY" "$HOME/Projects/Tests/scripts/ollama_shim.py" \
    --router http://127.0.0.1:8081 --port 11502 --omit-effort \
    >> "$RUN/shim-11502.log" 2>&1 &
  SHIM_PID=$!
  for i in $(seq 1 20); do sleep 1; ss -ltnH "sport = :11502" | grep -q . && break; done
  if assert_shim_tag "$OSS_TAG" 11502; then
    mmlu_off "$OSS_TAG" "$OUT/C-gptoss-off-noeffort" 11502
  else
    log "!!! REPRO C skipped: shim on :11502 did not come up"
  fi
  kill "$SHIM_PID" 2>/dev/null
else
  log "!!! REPRO B/C skipped: preflight failed"
fi

# ---- D: the column that matters, ~44k tokens per run -----------------------------------
log "--- REPRO D: incumbent MMLU-ON x2 (~44k tok/run, ~70 min each) ---"
if fresh_router "$HOME/llama-cuda12" "$INC_RID" 16384 && assert_shim_tag "$INC_TAG" 11501; then
  for i in 1 2; do
    D=$OUT/D-incumbent-on-$i
    [ -f "$D/results.json" ] && { log "repro: D-$i already present"; continue; }
    ( cd "$HOME/Projects/Tests" && "$PY" 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run \
        --base-url http://127.0.0.1:11501 --model "$INC_TAG" --num-ctx 16384 \
        --num-predict 12288 --per-category 5 --api-timeout 2400 --output "$D" ) > "$D.log" 2>&1
    log "repro: D-$i -> $("$PY" -c "
import json
d=json.load(open('$D/results.json')); s=d['model_summaries'][0]
t=sum(int(b.get('eval_count') or 0) for b in d['batches'])
print(f\"{s['accuracy']:.2f}% parsed={s['parsed']}/{s['total']} tok={t}\")" 2>&1)"
  done
else
  log "!!! REPRO D skipped: preflight failed"
fi

stop_router
start_router "$HOME/llama-cuda12" 8192
log "================ REPRO PHASE DONE ================"
"$PY" "$HERE/repro_report.py" 2>&1 | tee -a "$RUN/driver.log"
