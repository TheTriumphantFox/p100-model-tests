#!/usr/bin/env bash
# MMLU-Pro with thinking ENABLED, through a second shim (--force-think) on its own port.
#
# Why a separate script and a separate shim instead of a flag on bench_one2.sh: the
# thinking-OFF numbers are the only ones comparable to the shelf baselines and must stay
# untouched. This writes to mmlu-<slug>-think<N>/ and never to mmlu-<slug>-<N>/.
#
#   bench_think.sh <ollama-tag> <slug> [num_predict] [num_ctx] [api_timeout]
#
# num_predict must be large. At 4096 three of ornith's fourteen batches (engineering,
# history, law) burned the whole budget on reasoning and emitted no answer line at all,
# scoring 0/5 each and dragging a 89.1%-among-parsed run down to a reported 70.0%.
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-09-19/candidates-round2
TAG=$1; SLUG=$2; NP=${3:-12288}; CTX=${4:-16384}; TMO=${5:-2400}
SHIM=http://127.0.0.1:11501          # the --force-think shim; :11500 stays thinking-off
log() { echo "[$(date +%T)] $*" | tee -a "$RUN/driver.log"; }
py() { $T/.venv/bin/python "$@"; }
cd "$T"

OUT=$RUN/mmlu-$SLUG-think$NP
if [ -f "$OUT/results.json" ]; then log "$SLUG: MMLU-think@$NP already present, skipping"; exit 0; fi
log "$SLUG: MMLU-Pro THINKING-ON num_predict=$NP"
py 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run --base-url $SHIM \
  --model "$TAG" --num-ctx $CTX --num-predict $NP --api-timeout $TMO \
  --output "$OUT" > "$OUT.log" 2>&1

# Did thinking actually engage? The wall clock is a poor proxy -- the real signal is
# generated tokens. With thinking off these models answer an entire 5-question batch in
# ~10 tokens; with it on they must generate far more. Compare against this model's own
# thinking-off run at the same 2048 budget. A thinking-on run that did not generate
# meaningfully more tokens is a rig failure, not a model result.
py - "$OUT" "$RUN/mmlu-$SLUG-2048" "$SLUG" "$NP" <<'PY' | tee -a "$RUN/driver.log"
import json, sys
from pathlib import Path
out, base, slug, np_ = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
def load(p):
    d = json.load(open(p / "results.json"))
    s = d["model_summaries"][0]
    return s, sum(int(b.get("eval_count") or 0) for b in d["batches"])
import time
stamp = time.strftime("%T")
try:
    s, tok = load(out)
except Exception as e:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: thinking-on results unreadable ({e})"); sys.exit(0)
try:
    _, btok = load(base)
except Exception:
    btok = None
line = (f"[{stamp}] {slug}: MMLU-think@{np_} -> {s['accuracy']:.2f}% "
        f"parsed/attempt={s['parsed']}/{s['total']} tok={tok} "
        f"tps={s.get('generation_tps',0):.1f} wall={s.get('wall_seconds',0)/60:.1f}min")
if btok is not None:
    line += f" (thinking-off tok={btok}, ratio={tok/btok:.1f}x)"
print(line)
if tok == 0:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: 0 generated tokens -- every request errored. "
          f"Check the batches.csv error column; not a result.")
if btok is not None and btok > 0 and tok < 2 * btok:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: only {tok} tokens vs {btok} thinking-off "
          f"({tok/btok:.2f}x). Thinking did NOT engage -- do not report this as a result.")
if s["total"] < 70:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: only {s['total']} of 70 questions ran. This is a "
          f"partial/interrupted run, not a result -- delete the directory and re-run.")
to = [b["category"] for b in json.load(open(out / "results.json"))["batches"]
      if "Timeout" in str(b.get("error") or "")]
if to:
    print(f"[{stamp}] !!! RIG-FAIL {slug}: {len(to)} batch(es) hit the CLIENT TIMEOUT, not the "
          f"token cap: {', '.join(to)}. Raise --api-timeout; these are rig failures.")
if s["parsed"] < s["total"]:
    print(f"[{stamp}] !!! WARN {slug}: parsed {s['parsed']}/{s['total']} -- "
          f"num_predict={np_} may be truncating the answer after the reasoning.")
PY
log "$SLUG: think DONE"
