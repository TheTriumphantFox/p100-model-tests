#!/usr/bin/env bash
# MTP draft depth and DFlash, with footprints that fit 2x16 GB.
cd "$(dirname "$0")"
M8=/var/lib/ollama/candidates-r2/Qwen3.8-27B-Q8_0.gguf
M4=/var/lib/ollama/candidates-r2/Qwen3.8-27B-Q4_K_M.gguf
D=/var/lib/ollama/candidates-r2
MTP=(-md $D/mtp-Qwen3.8-27B-Q8_0.gguf --spec-type draft-mtp)
T5="size-2000-port size-5000-port size-7500-port escaping-banner injection-retarget"
export GGML_ENV=NCCL_P2P_DISABLE=1
./serve_bench.sh q38q8-tensor-mtp4-ub256 $M8 "$T5" -fa on -sm tensor -ub 256 "${MTP[@]}" --spec-draft-n-max 4
./serve_bench.sh q38q4-tensor $M4 "$T5" -fa on -sm tensor
./serve_bench.sh q38q4-tensor-mtp3 $M4 "$T5" -fa on -sm tensor "${MTP[@]}" --spec-draft-n-max 3
./serve_bench.sh q38q4-tensor-mtp5 $M4 "$T5" -fa on -sm tensor "${MTP[@]}" --spec-draft-n-max 5
GGML_ENV= ./serve_bench.sh q38q4-layer-dflash $M4 "$T5" -fa on -sm layer -md $D/dflash-Qwen3.8-27B-Q8_0.gguf --spec-type draft-dflash --spec-draft-n-max 8
./summ.py serve/q38*.json
echo PHASE_DONE
