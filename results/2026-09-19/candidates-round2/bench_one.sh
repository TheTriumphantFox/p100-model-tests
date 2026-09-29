#!/usr/bin/env bash
# Score one model through the shim: MMLU-Pro at the 96-token baseline, escalated to
# 2048 only if the answer parser came up short (the gpt-oss failure mode documented in
# ../candidates/REPORT.md), then HumanEval 164-task pass@1.
#   bench_one.sh <ollama-tag> <slug> [skip_throughput]
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-09-19/candidates-round2
TAG=$1; SLUG=$2; SKIP_TP=${3:-no}
SHIM=http://127.0.0.1:11500
log() { echo "[$(date +%T)] $*" | tee -a "$RUN/driver.log"; }
py() { $T/.venv/bin/python "$@"; }

parsed_of() { py -c "
import json,sys
try:
    d=json.load(open('$1/results.json')); s=d['model_summaries'][0]
    print(s['parsed'], s['total'], round(s['accuracy'],2))
except Exception as e: print('0 0 0')
"; }

cd "$T"
if [ "$SKIP_TP" != "skip" ]; then
  log "$SLUG: throughput"
  mkdir -p "$RUN/throughput"
  env OLLAMA_HOST=$SHIM py scripts/llm_benchmark.py --models "$TAG" \
    --tests speed_brief,speed_medium,speed_long,python_coding \
    --iterations 5 --context 8192 --timeout 900 \
    --output "$RUN/throughput/$SLUG.json" > "$RUN/throughput/$SLUG.log" 2>&1
  log "$SLUG: throughput rc=$?"
fi

log "$SLUG: MMLU-Pro num_predict=96"
py 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run --base-url $SHIM \
  --model "$TAG" --num-ctx 8192 --num-predict 96 \
  --output "$RUN/mmlu-$SLUG-96" > "$RUN/mmlu-$SLUG-96.log" 2>&1
read p t a <<< "$(parsed_of "$RUN/mmlu-$SLUG-96")"
log "$SLUG: MMLU@96 parsed=$p/$t acc=$a"

if [ "$p" -lt "$t" ] || [ "$t" -eq 0 ]; then
  log "$SLUG: parser short at 96 -> escalating to num_predict=2048"
  py 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run --base-url $SHIM \
    --model "$TAG" --num-ctx 8192 --num-predict 2048 \
    --output "$RUN/mmlu-$SLUG-2048" > "$RUN/mmlu-$SLUG-2048.log" 2>&1
  read p2 t2 a2 <<< "$(parsed_of "$RUN/mmlu-$SLUG-2048")"
  log "$SLUG: MMLU@2048 parsed=$p2/$t2 acc=$a2"
fi

log "$SLUG: HumanEval 164 tasks"
py 2026-09-06/local-llm-humaneval-benchmark/benchmark.py run --base-url $SHIM \
  --model "$TAG" --output "$RUN/humaneval-$SLUG" > "$RUN/humaneval-$SLUG.log" 2>&1
log "$SLUG: HumanEval rc=$? -> $(py -c "
import json
try:
    d=json.load(open('$RUN/humaneval-$SLUG/results.json')); s=d['model_summaries'][0]
    print(f\"pass@1={s.get('pass_at_1', s.get('accuracy'))} n={len(d['results'])} tps={s.get('generation_tps',0):.1f}\")
except Exception as e: print('unreadable', e)
")"
log "$SLUG: DONE"
