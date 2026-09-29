#!/usr/bin/env bash
# Same as bench_one.sh but runs MMLU-Pro at BOTH token budgets unconditionally.
# Why: every model in round 2 is a reasoning model. At the 96-token baseline they parse
# fine (unlike gpt-oss) but answer with no chain of thought, so 96 measures a different
# thing than their published numbers. Report both.
#   bench_one2.sh <ollama-tag> <slug> [skip_throughput] [skip_humaneval] [only_2048]
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-09-19/candidates-round2
TAG=$1; SLUG=$2; SKIP_TP=${3:-no}; SKIP_HE=${4:-no}; ONLY_2048=${5:-no}
SHIM=http://127.0.0.1:11500
log() { echo "[$(date +%T)] $*" | tee -a "$RUN/driver.log"; }
py() { $T/.venv/bin/python "$@"; }
summ() { py -c "
import json
try:
    d=json.load(open('$1/results.json')); s=d['model_summaries'][0]
    k='pass_at_1' if 'pass_at_1' in s else 'accuracy'
    print(f\"{s[k]:.2f}% parsed/attempt={s.get('parsed', s.get('attempted'))}/{s.get('total', s.get('attempted'))} n={len(d['results'])} tps={s.get('generation_tps',0):.1f} wall={s.get('wall_seconds',0)/60:.1f}min\")
except Exception as e: print('unreadable', e)
"; }
cd "$T"

if [ "$SKIP_TP" != "skip" ]; then
  log "$SLUG: throughput"; mkdir -p "$RUN/throughput"
  env OLLAMA_HOST=$SHIM $T/.venv/bin/python scripts/llm_benchmark.py --models "$TAG" \
    --tests speed_brief,speed_medium,speed_long,python_coding --iterations 5 \
    --context 8192 --timeout 900 --output "$RUN/throughput/$SLUG.json" \
    > "$RUN/throughput/$SLUG.log" 2>&1
  log "$SLUG: throughput rc=$? $(py -c "
import json
d=json.load(open('$RUN/throughput/$SLUG.json'))
b=d['summary']['by_model_test']['$TAG']
print(' '.join(f\"{k}={v['avg_score_tok_per_sec']:.1f}\" for k,v in b.items()))
" 2>/dev/null)"
fi

for NP in 96 2048; do
  [ "$ONLY_2048" = "only2048" ] && [ "$NP" = "96" ] && continue
  [ -f "$RUN/mmlu-$SLUG-$NP/results.json" ] && { log "$SLUG: MMLU@$NP already present, skipping"; continue; }
  log "$SLUG: MMLU-Pro num_predict=$NP"
  py 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run --base-url $SHIM \
    --model "$TAG" --num-ctx 8192 --num-predict $NP \
    --output "$RUN/mmlu-$SLUG-$NP" > "$RUN/mmlu-$SLUG-$NP.log" 2>&1
  log "$SLUG: MMLU@$NP -> $(summ "$RUN/mmlu-$SLUG-$NP")"
done

if [ "$SKIP_HE" != "skip" ]; then
  if [ -f "$RUN/humaneval-$SLUG/results.json" ]; then log "$SLUG: HumanEval already present, skipping"; else
  log "$SLUG: HumanEval 164 tasks"
  py 2026-09-06/local-llm-humaneval-benchmark/benchmark.py run --base-url $SHIM \
    --model "$TAG" --output "$RUN/humaneval-$SLUG" > "$RUN/humaneval-$SLUG.log" 2>&1
  log "$SLUG: HumanEval -> $(summ "$RUN/humaneval-$SLUG")"
  fi
fi
log "$SLUG: DONE"
