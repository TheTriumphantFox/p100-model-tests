#!/usr/bin/env bash
# Round 2, part 4: can Qwen3.8-27B be both the best-scoring and the fastest model here?
#
# Six configs. The two drafters ship in ggml-org's own Qwen3.8 repo, so their vocabulary
# matches by construction - the thing that blocked speculative decoding for devstral.
# ngram-cache needs no draft model at all, which the notes said did not exist; this build
# lists ngram-simple/ngram-cache/ngram-mod under --spec-type, so that is now testable.
set -uo pipefail
RUN=~/Projects/Tests/2026-09-19/candidates-round2
DL=/var/lib/ollama/candidates-r2
S=~/Projects/Tests/scripts/spec_ab.sh
export SPEC_AB_OUT=$RUN/spec-decoding
Q4=$DL/Qwen3.8-27B-Q4_K_M.gguf
Q8=$DL/Qwen3.8-27B-Q8_0.gguf
MTP=$DL/mtp-Qwen3.8-27B-Q8_0.gguf
DF=$DL/dflash-Qwen3.8-27B-Q8_0.gguf
log() { echo "[$(date +%T)] $*" | tee -a "$RUN/driver.log"; }

for i in $(seq 1 3000); do grep -q "QUEUE-3 DONE" "$RUN/driver.log" && break; sleep 20; done
for i in $(seq 1 180); do grep -q "QWEN38 DOWNLOADS DONE" "$RUN/download-qwen38.log" && break; sleep 20; done
log "QUEUE-4 START (speculative decoding A/B)"
mkdir -p "$SPEC_AB_OUT"

run() { # label model spectype [draft]
  log "spec: $1"
  "$S" "$1" "$2" "$3" "${4:-}" >> "$RUN/spec-decoding/$1.run.log" 2>&1
  log "spec: $1 -> $(python3 -c "
import json
try:
    d=json.load(open('$SPEC_AB_OUT/$1.json'))
    print(f\"mean {d['mean_gen_tps']:.2f} tok/s (min {d['min_gen_tps']:.2f} max {d['max_gen_tps']:.2f})\")
except Exception as e: print('FAILED', e)")"
}

run q4-baseline      "$Q4" none
run q4-dflash        "$Q4" draft-dflash "$DF"
run q4-mtp           "$Q4" draft-mtp    "$MTP"
run q4-ngram-cache   "$Q4" ngram-cache
run q8-baseline      "$Q8" none
# Q8_0 is 28.6 GB of a 32.5 GB budget; a 2 GB drafter plus KV may not fit. Try the
# cheaper of the two and let it fail loudly if it does not.
run q8-dflash        "$Q8" draft-dflash "$DF"
log "QUEUE-4 DONE"
