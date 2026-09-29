#!/usr/bin/env bash
# Round 2, part 5 - repairs part 2 and part 4.
#
#  * Xing4.0 and G9v3 never ran: their fork runtimes had NO CUDA runtime libs, because
#    build_llama_cuda12.sh used `find` (not `find -L`) on /usr/local/cuda/lib64, which is a
#    symlink - the exact trap recorded in [[p100-cuda12-llama-build]]. Libs copied in from
#    the production build by hand; the script is fixed for next time.
#  * The speculative A/B ran against a GPU that still held qwen3.8-27b from the previous
#    HumanEval (17 GB). Stop the bench router first so each config gets all 32.5 GB.
set -uo pipefail
T=~/Projects/Tests
RUN=$T/2026-09-19/candidates-round2
DL=/var/lib/ollama/candidates-r2
BM=~/llama-bench-models
S=$T/scripts/spec_ab.sh
export SPEC_AB_OUT=$RUN/spec-decoding
log() { echo "[$(date +%T)] $*" | tee -a "$RUN/driver.log"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
stop_router() {
  p=$(router_pid); [ -n "$p" ] && { kill "$p"; for i in $(seq 1 60); do sleep 2; [ -z "$(router_pid)" ] && break; done; }
  sleep 5
  log "router stopped (was pid ${p:-none}); GPU now $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
}
start_router() {
  nohup env LD_LIBRARY_PATH=$1/lib $1/bin/llama-server \
    --models-dir $BM --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size 8192 --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 >> "$RUN/router-8081.log" 2>&1 &
  for i in $(seq 1 90); do sleep 2; [ -n "$(router_pid)" ] && break; done
  p=$(router_pid)
  log "router started from $1 ($(cut -c1-12 $1/LLAMA_COMMIT), pid ${p:-FAILED-TO-START})"
  [ -n "$p" ]
}

log "QUEUE-5 START"
stop_router
mkdir -p "$SPEC_AB_OUT"

run() { log "spec: $1"; "$S" "$1" "$2" "$3" "${4:-}" >> "$RUN/spec-decoding/$1.run.log" 2>&1
  log "spec: $1 -> $(python3 -c "
import json
try:
    d=json.load(open('$SPEC_AB_OUT/$1.json'))
    r=d['runs'][0]; dr=[f'{k}={r[k]}' for k in r if 'draft' in k or 'accept' in k]
    print(f\"mean {d['mean_gen_tps']:.2f} tok/s (min {d['min_gen_tps']:.2f} max {d['max_gen_tps']:.2f}) {' '.join(dr)}\")
except Exception as e: print('FAILED', e)")"; }

Q4=$DL/Qwen3.8-27B-Q4_K_M.gguf; Q8=$DL/Qwen3.8-27B-Q8_0.gguf
MTP=$DL/mtp-Qwen3.8-27B-Q8_0.gguf; DF=$DL/dflash-Qwen3.8-27B-Q8_0.gguf
run q4-baseline    "$Q4" none
run q4-dflash      "$Q4" draft-dflash "$DF"
run q4-mtp         "$Q4" draft-mtp    "$MTP"
run q4-ngram-cache "$Q4" ngram-cache
run q8-baseline    "$Q8" none
run q8-dflash      "$Q8" draft-dflash "$DF"
run q8-mtp         "$Q8" draft-mtp    "$MTP"

# now the two models that never ran, each on its own runtime
ln -sf "$DL/xing4_0-29b-IQ4_NL.gguf" "$BM/xing4.0-29b-a4b_iq4_nl.gguf"
if start_router ~/llama-cuda12-xing; then "$RUN/bench_one2.sh" 'xing4.0-29b-a4b:iq4_nl' xing; fi
stop_router
ln -sf "$DL/G9v3-39A5B-Q4_K_M.gguf" "$BM/g9v3-39a5b_q4_k_m.gguf"
if start_router ~/llama-cuda12-g9v3; then "$RUN/bench_one2.sh" 'g9v3-39a5b:q4_k_m' g9v3; fi
stop_router
start_router ~/llama-cuda12
log "QUEUE-5 DONE"
