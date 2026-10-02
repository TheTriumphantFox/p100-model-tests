#!/usr/bin/env bash
# bench.sh <tag> [env assignments...] -- <llama-bench args>
# Refuses to run if anything other than the desktop holds GPU memory.
set -euo pipefail
tag=$1; shift
envs=()
while [[ $# -gt 0 && $1 != -- ]]; do envs+=("$1"); shift; done
shift
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -1)
if (( used > 200 )); then echo "GPU busy (${used} MiB used), not running $tag" >&2; exit 3; fi
out=raw/$tag.jsonl
echo "# $(date -Is) ${envs[*]:-} llama-bench $*" > raw/$tag.cmd
nvidia-smi --query-gpu=index,temperature.gpu,clocks.sm --format=csv,noheader > raw/$tag.temps-before
timeout ${BENCH_TIMEOUT:-1500} env LD_LIBRARY_PATH=$HOME/llama-cuda12/lib:$HOME/llama-cuda12/bin "${envs[@]}" \
  $HOME/llama-cuda12/bin/llama-bench -o jsonl "$@" > "$out" 2> raw/$tag.log
rc=${PIPESTATUS[0]:-0}; python3 - "$out" <<'PY'
import json,sys
for l in open(sys.argv[1]):
    r=json.loads(l)
    t=f"pp{r['n_prompt']}" if r['n_prompt'] else f"tg{r['n_gen']}"
    if r.get('n_depth'): t+=f"@d{r['n_depth']}"
    print(f"{r['model_type'][:28]:28} sm={r['split_mode']:6} fa={r['flash_attn']} kv={r['type_k']}/{r['type_v']} ub={r['n_ubatch']} {t:14} {r['avg_ts']:8.2f} ± {r['stddev_ts']:.2f}")
PY
