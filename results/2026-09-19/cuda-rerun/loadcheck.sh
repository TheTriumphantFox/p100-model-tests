#!/usr/bin/env bash
# Which shelf models does the CUDA sm_60 llama.cpp build actually load?
# One tiny request per model through the shim; records load time or the error.
set -uo pipefail
SHIM=${SHIM:-http://127.0.0.1:11500}
OUT=${1:-/home/hm/Projects/Tests/2026-09-19/cuda-rerun/loadcheck.txt}
: > "$OUT"

TAGS=(
  "gemma4-e4b-abliterated:q4_k_m"
  "qwen3.8-27b-stock:q4_k_m"
  "qwen3.6-27b-opus-distill:q4_k_m"
  "qwen3.6-27b-abliterated:q5_k_m"
  "qwen3.6-35b-a3b-abliterated-vl:q4_k_m"
  "devstral-patched:latest"
)

for tag in "${TAGS[@]}"; do
  printf '%-42s ' "$tag" | tee -a "$OUT"
  t0=$(date +%s)
  body=$(curl -s --max-time 900 "$SHIM/api/chat" -H 'Content-Type: application/json' \
    -d "{\"model\":\"$tag\",\"stream\":false,\"think\":false,
         \"messages\":[{\"role\":\"user\",\"content\":\"Reply with exactly: ok\"}],
         \"options\":{\"num_ctx\":8192,\"num_predict\":16,\"temperature\":0,\"seed\":42}}")
  t1=$(date +%s)
  echo "$body" | python3 -c "
import json,sys
try: d=json.load(sys.stdin)
except Exception as e: print('BAD JSON', e); raise SystemExit
if 'error' in d:
    msg=str(d['error'])
    import re
    m=re.search(r'wrong number of tensors[^\"]*|failed to load|out of memory|[A-Za-z ]*error[^\"]{0,60}', msg)
    print('FAIL  ', (m.group(0) if m else msg)[:90])
else:
    ec=d.get('eval_count',0); ed=d.get('eval_duration',1)/1e9
    print(f\"ok    {ec:3d} tok  {ec/ed if ed else 0:6.2f} tok/s  reply={d['message']['content'][:20]!r}\")
" | tee -a "$OUT"
  echo "    (wall $((t1-t0))s)" | tee -a "$OUT"
  # unload so the next model gets the whole card
  curl -s --max-time 120 "$SHIM/api/generate" -H 'Content-Type: application/json' \
    -d "{\"model\":\"$tag\",\"keep_alive\":0}" >/dev/null 2>&1
  sleep 5
done
echo "--- done ---" | tee -a "$OUT"
