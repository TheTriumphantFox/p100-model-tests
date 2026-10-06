#!/usr/bin/env bash
# MMLU-Pro thinking-ON, through the --force-think shim on :11501.
# Settings match candidates-round2/bench_think.sh exactly (per_category 5, seed 42,
# ctx 16384, num_predict 12288, api_timeout 2400) so every number produced here is
# pairable against the round-2 thinking-on column via mcnemar.py.
#
#   bench_think.sh <ollama-tag> <slug> [num_predict] [num_ctx] [api_timeout]
#
# Reads the thinking-OFF run at mmlu-<slug>-pc5-np2048 as the engagement control. A
# thinking-on run that did not generate far more tokens than its own thinking-off run
# is a rig failure (the template ignored enable_thinking, or the model has no thinking
# mode at all), not a model result -- gemma4 and gpt-oss are the likely cases here.
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-10-02/flash-next-full
TAG=$1; SLUG=$2; NP=${3:-12288}; CTX=${4:-16384}; TMO=${5:-2400}
SHIM=http://127.0.0.1:11501
log() { echo "[$(date '+%m-%d %T')] $*" | tee -a "$RUN/driver.log"; }
py() { "$T/.venv/bin/python" "$@"; }
cd "$T"

OUT=$RUN/mmlu-$SLUG-pc5-think$NP
if [ -f "$OUT/results.json" ]; then log "$SLUG: MMLU-think@$NP already present, skipping"; exit 0; fi
log "$SLUG: MMLU-Pro THINKING-ON num_predict=$NP ctx=$CTX timeout=$TMO"
py 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run --base-url $SHIM \
  --model "$TAG" --num-ctx "$CTX" --num-predict "$NP" --per-category 5 --api-timeout "$TMO" \
  --output "$OUT" > "$OUT.log" 2>&1

py - "$OUT" "$RUN/mmlu-$SLUG-pc5-np2048" "$SLUG" "$NP" <<'PY' | tee -a "$RUN/driver.log"
import json, sys, time
from pathlib import Path
out, base, slug, np_ = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], int(sys.argv[4])
stamp = time.strftime("%m-%d %T")

def load(p):
    d = json.load(open(p / "results.json"))
    s = d["model_summaries"][0]
    return d, s, sum(int(b.get("eval_count") or 0) for b in d["batches"])

try:
    d, s, tok = load(out)
except Exception as exc:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: thinking-on results unreadable ({exc})"); sys.exit(0)
try:
    _, _, btok = load(base)
except Exception:
    btok = None

capped = [b["category"] for b in d["batches"] if int(b.get("eval_count") or 0) >= np_ - 8]
tmo    = [b["category"] for b in d["batches"] if "Timeout" in str(b.get("error") or "")]
answered = [r for r in d["results"] if r["predicted_answer"]]
among = 100 * sum(bool(r["correct"]) for r in answered) / len(answered) if answered else 0

line = (f"[{stamp}] {slug}: MMLU-think@{np_} -> {s['accuracy']:.2f}% "
        f"parsed={s['parsed']}/{s['total']} among-answered={among:.2f}% tok={tok} "
        f"tps={s.get('generation_tps') or 0:.1f} wall={(s.get('wall_seconds') or 0)/60:.1f}min")
if btok:
    line += f" (off tok={btok}, ratio={tok/btok:.1f}x)"
print(line)

if tok == 0:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: 0 generated tokens -- every request errored, not a result.")
if btok and tok < 2 * btok:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: {tok} tokens vs {btok} thinking-off ({tok/btok:.2f}x). "
          f"Thinking did NOT engage -- the template ignored enable_thinking, or this model has "
          f"no thinking mode. Do not report this as a thinking-on result.")
if s["total"] < 70:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: only {s['total']}/70 questions ran -- partial, not a result.")
if tmo:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: {len(tmo)} batch(es) hit the CLIENT TIMEOUT "
          f"({', '.join(tmo)}). eval_count=0 is the tell; raise --api-timeout. Rig failure, not truncation.")
if capped:
    print(f"[{stamp}] !!! WARN {slug}: {len(capped)} batch(es) hit the {np_}-token cap "
          f"({', '.join(capped)}). Those score 0/5, so {s['accuracy']:.2f}% is a FLOOR, not a score.")
PY
log "$SLUG: think DONE"
