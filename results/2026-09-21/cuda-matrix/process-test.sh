#!/usr/bin/env bash
# PROCESS TEST -- thinking-on MMLU-Pro at a context size anyone would actually want to
# use, over 10 questions. The point is the PROCESS, not the score: 10 questions resolves
# nothing statistically and no number from this run belongs in the matrix.
#
# WHICH CONTEXT COUNTS AS "ACTUALLY WANT TO USE", and why it is not 16384:
#   16384 is a benchmark minimum -- the smallest window that holds a 12288-token thinking
#   budget. The context this box actually runs in production is the devstral router on
#   :8080: ctx 49152 with q8_0 KV. That is the standing answer to "what would you want",
#   so this test targets 49152 with q8_0 KV, the production configuration, and ladders up
#   to it to find out what it costs on a 28.6 GB Q8_0.
#
# WHICH 10 QUESTIONS, and why not just the first 10:
#   --per-category 1 over 10 chosen categories. One question per request means ten
#   independent passes through the whole path -- prompt build, thinking, parse, timeout,
#   truncation detection -- rather than two batches of five. The ten are picked to include
#   the categories that actually broke round 2: `law` truncated for all four candidates,
#   chemistry and history for most. A process test aimed at the easy categories proves
#   only that the easy path works.
#
# WHAT THIS TEST IS ALLOWED TO CONCLUDE:
#   whether the pipeline runs end to end at a usable context; what that context costs in
#   tok/s; whether truncation, timeout and parse handling fire correctly. Nothing about
#   which model is better.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
source "$HERE/lib.sh"
PY=$HOME/Projects/Tests/.venv/bin/python

RID=${RID:-qwen3.8-27b-ggmlorg_q8_0}
TAG=${TAG:-qwen3.8-27b-ggmlorg:q8_0}
SLUG=${SLUG:-ggmlorg-q8}
KV=${KV:-q8_0}                     # production's KV quant, not the benchmark's f16
TARGET_CTX=${TARGET_CTX:-49152}    # production's context on :8080
CATS='biology,chemistry,computer science,economics,engineering,health,history,law,math,physics'

log "================ PROCESS TEST: $SLUG, thinking-on at a usable context ================"
log "target ctx=$TARGET_CTX kv=$KV (the :8080 production configuration), 10 questions"

# ---- 1. what does this context actually cost? -----------------------------------------
# Ladder first, so the token budget below is sized from a measured decode rate instead of
# a guess. A spilled rung is recorded, not skipped -- that is the result, not an error.
if [ ! -s "$RUN/ctx-ladder/$SLUG-$KV.jsonl" ]; then
  SLUG="$SLUG-$KV" "$HERE/ctx-ladder.sh" "$RID" "$TAG" "$SLUG-$KV" "$KV" 16384 32768 "$TARGET_CTX"
fi
"$PY" "$HERE/ladder_report.py" 2>&1 | tee -a "$RUN/driver.log"

# 49152 may not load at all: llama.cpp can fail the KV allocation outright rather than
# spill. That is still an answer to "can I use this context", so fall back to the largest
# rung that actually served a token, and say which one is being used.
read -r ACTUAL_CTX TPS <<<"$("$PY" "$HERE/pick_ctx.py" "$RUN/ctx-ladder/$SLUG-$KV.jsonl" "$TARGET_CTX")"
ACTUAL_CTX=${ACTUAL_CTX:-0}; TPS=${TPS:-0}
if [ "$ACTUAL_CTX" = "0" ]; then
  log "!!! $SLUG: no context on the ladder served a single token, so the process test"
  log "!!!   cannot run. That is itself the finding: no usable thinking context here."
  exit 1
fi
if [ "$ACTUAL_CTX" != "$TARGET_CTX" ]; then
  log "$SLUG: !!! ctx=$TARGET_CTX would not serve; falling back to $ACTUAL_CTX, the largest that did"
  TARGET_CTX=$ACTUAL_CTX
fi
log "$SLUG: measured $TPS tok/s at ctx=$TARGET_CTX with $KV KV"

# Size the budget so ten batches cannot outrun ~75 minutes even if every one runs to the
# cap. A thinking batch that never terminates is the documented failure mode here, so the
# cap is what bounds the test -- not optimism about termination.
NP=$("$PY" -c "
tps = max(float('$TPS'), 0.5)
budget = int(75 * 60 * tps / 10)          # seconds of wall clock, ten batches
print(max(2048, min(12288, budget // 256 * 256)))
")
TMO=$("$PY" -c "print(int(max(1800, min(7200, $NP / max(float('$TPS'), 0.5) * 1.5))))")
log "$SLUG: num_predict=$NP api_timeout=${TMO}s (sized from the measured rate, ten batches)"

# ---- 2. the run ------------------------------------------------------------------------
OUT=$RUN/PROCESS-mmlu-$SLUG-ctx$TARGET_CTX-$KV-think$NP
if [ -f "$OUT/results.json" ]; then
  log "process test already present at $OUT -- not re-running"
else
  if fresh_router "$HOME/llama-cuda12" "$RID" "$TARGET_CTX" --cache-type-k "$KV" --cache-type-v "$KV" \
     && assert_shim_tag "$TAG" 11501; then
    warm_model "$TAG" 11501
    assert_on_gpu "$BM/$RID.gguf" "$SLUG" \
      || log "$SLUG: SPILLED at ctx=$TARGET_CTX -- proceeding deliberately; the cost is the result"
    log "$SLUG: 10 questions, one per category, thinking ON"
    ( cd "$HOME/Projects/Tests" && "$PY" 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run \
        --base-url http://127.0.0.1:11501 --model "$TAG" \
        --num-ctx "$TARGET_CTX" --num-predict "$NP" \
        --per-category 1 --categories "$CATS" --api-timeout "$TMO" \
        --output "$OUT" ) > "$OUT.log" 2>&1
  else
    log "!!! process test: preflight failed"; exit 1
  fi
fi

# ---- 3. what happened, path by path ----------------------------------------------------
"$PY" - "$OUT" "$TARGET_CTX" "$KV" "$NP" <<'PY' 2>&1 | tee -a "$RUN/driver.log"
import json, sys
from pathlib import Path
out, ctx, kv, np_ = Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4])
try:
    d = json.load(open(out / "results.json"))
except Exception as exc:
    print(f"PROCESS TEST UNREADABLE: {exc}"); raise SystemExit(0)
s = d["model_summaries"][0]
b = d["batches"]
tok = sum(int(x.get("eval_count") or 0) for x in b)
capped = [x["category"] for x in b if int(x.get("eval_count") or 0) >= np_ - 8]
tmo = [x["category"] for x in b if "Timeout" in str(x.get("error") or "")]
err = [x["category"] for x in b if str(x.get("error") or "") and x["category"] not in tmo]
unparsed = [r["category"] for r in d["results"] if not r["predicted_answer"]]
print(f"\n=== PROCESS TEST: ctx {ctx}, {kv} KV, num_predict {np_} ===")
print(f"batches completed     {len(b)}/10")
print(f"questions parsed      {s['parsed']}/{s['total']}")
print(f"generated tokens      {tok}  (mean {tok // max(len(b), 1)}/batch)")
print(f"decode rate           {s.get('generation_tps') or 0:.2f} tok/s")
print(f"wall clock            {(s.get('wall_seconds') or 0) / 60:.1f} min")
print(f"score (NOT a result)  {s['accuracy']:.1f}% over 10 questions")
print("\npath coverage:")
print(f"  thinking engaged    {'YES' if tok > 40 * len(b) else 'NO -- a thinking-off run generates ~2 tok/question'}")
print(f"  cap-truncation      {len(capped)} batch(es){': ' + ', '.join(capped) if capped else ' -- path not exercised'}")
print(f"  client timeout      {len(tmo)} batch(es){': ' + ', '.join(tmo) if tmo else ' -- path not exercised'}")
print(f"  other errors        {len(err)} batch(es){': ' + ', '.join(err) if err else ''}")
print(f"  unparsed answers    {len(unparsed)}{': ' + ', '.join(unparsed) if unparsed else ''}")
print("\n10 questions cannot resolve any difference between models. Read the paths, not the score.")
PY
log "================ PROCESS TEST DONE ================"
