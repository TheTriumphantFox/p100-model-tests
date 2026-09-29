#!/usr/bin/env bash
# Quick speed and fit check for one model, before committing an overnight slot to it.
#
#   ./speedtest.sh qwen3.6-35b-a3b_ud-q6_k
#
# Same router config as drive.sh (ctx 32768, f16 KV). Measures residency at load, then
# runs three planner tasks -- 1.4, 7.2 and 15 KiB targets -- which give prefill and
# generation speed and the wall time of the largest write. Results go to smoke/, not
# results/, so the full run later starts clean. The :8080 devstral service is stopped
# for the few minutes this takes and restarted on exit, whatever happens.
set -uo pipefail

MODEL=${1:?usage: speedtest.sh <router model name>}
RUN=~/Projects/Tests/2026-09-23/planner-bench
BM=~/llama-bench-models
PY=~/Projects/Tests/.venv/bin/python
URL=http://127.0.0.1:8081/v1/chat/completions
OUT=$RUN/smoke/speed-$MODEL.json
LOG=$RUN/smoke/speed-$MODEL.log

log() { echo "[$(date +'%F %T')] $*" | tee -a "$LOG"; }
router_pid() { ss -ltnpH "sport = :8081" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1; }
gpu() { nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits; }
gpu_mib() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '{s+=$1} END{print s+0}'; }

cleanup() {
  local p i c
  p=$(router_pid); [ -n "$p" ] && kill "$p" 2>/dev/null
  for i in $(seq 1 30); do sleep 2; [ -z "$(router_pid)" ] && break; done
  for c in $(ps -eo pid,args | grep '[l]lama-server --models-dir' | awk '{print $1}'); do kill "$c" 2>/dev/null; done
  sleep 3
  systemctl --user start llama-devstral.service 2>/dev/null
  log "cleanup: router stopped, :8080 devstral restarted"
}
trap cleanup EXIT

[ -e "$BM/$MODEL.gguf" ] || { echo "no $BM/$MODEL.gguf"; exit 1; }
mkdir -p "$RUN/smoke"
rm -f "$OUT"
systemctl --user stop llama-devstral.service 2>/dev/null
for c in $(ps -eo pid,args | grep '[l]lama-server --models-dir' | awk '{print $1}'); do kill "$c" 2>/dev/null; done
for i in $(seq 1 60); do sleep 2; [ "$(gpu_mib)" -lt 1000 ] && break; done

nohup env LD_LIBRARY_PATH=~/llama-cuda12/lib ~/llama-cuda12/bin/llama-server \
  --models-dir "$BM" --models-autoload --models-max 1 \
  --host 127.0.0.1 --port 8081 --ctx-size 32768 --split-mode layer \
  --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
  --parallel 1 --batch-size 512 --ubatch-size 512 >> "$RUN/smoke/speed-router.log" 2>&1 &
for i in $(seq 1 90); do sleep 2; curl -s --max-time 2 http://127.0.0.1:8081/v1/models >/dev/null && break; done

t0=$SECONDS
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 1800 -X POST "$URL" -H 'Content-Type: application/json' \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":1}")
sz=$(du -Lm "$BM/$MODEL.gguf" | cut -f1)
log "$MODEL: load HTTP $code in $((SECONDS-t0)) s; weights ${sz} MiB; GPU total $(gpu_mib) MiB"
gpu | while IFS=, read -r idx used total; do log "  GPU$idx: ${used# } / ${total# } MiB (free $(( ${total# } - ${used# } )) MiB)"; done
if [ "$code" != 200 ] || [ "$(gpu_mib)" -lt "$sz" ]; then log "NOT fully resident -- stopping here"; exit 1; fi

$PY "$RUN/run.py" --url "$URL" --model "$MODEL" --out "$OUT" \
    --extra-body '{"chat_template_kwargs":{"enable_thinking":false}}' \
    --only size-1000-port size-7500-port size-15500-port 2>&1 | grep -v RuntimeWarning | tee -a "$LOG"
gpu | while IFS=, read -r idx used total; do log "  after run GPU$idx: ${used# } / ${total# } MiB"; done

$PY - "$OUT" <<'EOF' | tee -a "$LOG"
import json, sys
for r in json.load(open(sys.argv[1]))["results"]:
    pre = r["prompt_tokens"] / (r["prompt_ms"] / 1000)
    gen = r["completion_tokens"] / (r["predicted_ms"] / 1000)
    print(f"{r['id']:18} {r['target_bytes']/1024:5.1f} KiB  prefill {pre:6.0f} tok/s  gen {gen:5.1f} tok/s  "
          f"wall {r['wall_s']:6.1f} s  {r['verdict'] or r['outcome']}")
EOF
