#!/usr/bin/env bash
# Best dense config on the largest rewrites.
cd "$(dirname "$0")"
D=/var/lib/ollama/candidates-r2
export GGML_ENV=NCCL_P2P_DISABLE=1
./serve_bench.sh q38q8-tensor-mtp4-ub256-big $D/Qwen3.8-27B-Q8_0.gguf \
  "size-10000-port size-13000-port size-15500-port escaping-timeout-7500" \
  -fa on -sm tensor -ub 256 -md $D/mtp-Qwen3.8-27B-Q8_0.gguf --spec-type draft-mtp --spec-draft-n-max 4
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader
./summ.py serve/q38q8-tensor-mtp4-ub256-big.json
echo PHASE_DONE
