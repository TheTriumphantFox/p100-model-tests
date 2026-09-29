#!/usr/bin/env bash
# Thinking-OFF leg of the matrix: MMLU-Pro (any --per-category) + HumanEval + throughput.
# The router must already be up and serving this model; use fresh_router from lib.sh.
#
#   bench_off.sh <ollama-tag> <slug> <per-category> <what>
#     what: comma list from mmlu96,mmlu2048,humaneval,throughput  (default: all four)
#
# Order matters: MMLU first (minutes), HumanEval second (~70 min on a dense 11 tok/s
# model), throughput last (~13 min), so the accuracy answer lands as early as possible.
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-09-21/cuda-matrix
TAG=$1; SLUG=$2; PC=${3:-5}; WHAT=${4:-mmlu96,mmlu2048,humaneval,throughput}
SHIM=http://127.0.0.1:11500          # thinking-off shim; :11501 is --force-think
BATCH=${BATCH:-$PC}                  # questions per request; see bench_think.sh header
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a "$RUN/driver.log"; }
py() { "$T/.venv/bin/python" "$@"; }
want() { case ",$WHAT," in *",$1,"*) return 0;; esac; return 1; }
summ() { py -c "
import json
try:
    d=json.load(open('$1/results.json')); s=d['model_summaries'][0]
    k='pass_at_1' if 'pass_at_1' in s else 'accuracy'
    print(f\"{s[k]:.2f}% parsed={s.get('parsed', s.get('attempted'))}/{s.get('total', s.get('attempted'))} tps={s.get('generation_tps',0):.1f} wall={s.get('wall_seconds',0)/60:.1f}min\")
except Exception as e: print('UNREADABLE', e)
"; }
cd "$T"

# Nothing below is worth running if the model cannot answer at all. See preflight_serves
# in lib.sh for what this cost before it existed.
if [ "${SKIP_PREFLIGHT:-no}" != "yes" ]; then
  # shellcheck source=lib.sh
  source "$RUN/lib.sh"
  preflight_serves "$TAG" "${SHIM##*:}" "$SLUG" || {
    log "$SLUG: ABORTED before any leg ran (preflight)"; exit 3; }
fi

BATCH_ARG=()
[ "$BATCH" != "$PC" ] && BATCH_ARG=(--batch-size "$BATCH")

for NP in 96 2048; do
  want "mmlu$NP" || continue
  OUT=$RUN/mmlu-$SLUG-pc$PC-np$NP
  [ -f "$OUT/results.json" ] && { log "$SLUG: MMLU pc=$PC np=$NP already present, skipping"; continue; }
  log "$SLUG: MMLU-Pro per-category=$PC (batch $BATCH) num_predict=$NP"
  py 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run --base-url $SHIM \
    --model "$TAG" --num-ctx 8192 --num-predict $NP --per-category "$PC" \
    "${BATCH_ARG[@]}" --api-timeout 2400 \
    --output "$OUT" > "$OUT.log" 2>&1
  log "$SLUG: MMLU pc=$PC np=$NP -> $(summ "$OUT")"
done

if want humaneval; then
  OUT=$RUN/humaneval-$SLUG
  if [ -f "$OUT/results.json" ]; then log "$SLUG: HumanEval already present, skipping"; else
    log "$SLUG: HumanEval 164 tasks"
    py 2026-09-06/local-llm-humaneval-benchmark/benchmark.py run --base-url $SHIM \
      --model "$TAG" --output "$OUT" > "$OUT.log" 2>&1
    log "$SLUG: HumanEval -> $(summ "$OUT")"
  fi
fi

if want throughput; then
  mkdir -p "$RUN/throughput"
  if [ -f "$RUN/throughput/$SLUG.json" ]; then log "$SLUG: throughput already present, skipping"; else
    log "$SLUG: throughput"
    # NOT `env VAR=x py ...`: py() is a shell function and env cannot run one, so that
    # form exits 127 in zero seconds and writes no JSON. This is bug 3 in
    # candidates-round2/REPORT.md, which cost two throughput runs there and one here.
    env OLLAMA_HOST=$SHIM "$T/.venv/bin/python" scripts/llm_benchmark.py --models "$TAG" \
      --tests speed_brief,speed_medium,speed_long,python_coding --iterations 5 \
      --context 8192 --timeout 900 --output "$RUN/throughput/$SLUG.json" \
      > "$RUN/throughput/$SLUG.log" 2>&1
    log "$SLUG: throughput -> $(py -c "
import json
d=json.load(open('$RUN/throughput/$SLUG.json'))
b=d['summary']['by_model_test']['$TAG']
print(' '.join(f\"{k}={v['avg_score_tok_per_sec']:.1f}\" for k,v in b.items()))
" 2>/dev/null)"
  fi
fi
log "$SLUG: bench_off DONE (pc=$PC what=$WHAT)"
