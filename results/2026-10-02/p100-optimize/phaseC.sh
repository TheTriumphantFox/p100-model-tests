#!/usr/bin/env bash
# MTP on every model that has a head (built-in nextn layer), plus the Qwen3.8 MTP file
# on the Qwen3.6-27B incumbent as a long shot. Tensor split, planner tasks.
cd "$(dirname "$0")"
D=/var/lib/ollama/candidates-r2; DL=~/Downloads/Models; M=~/models
STOCK=/var/lib/ollama/blobs/sha256-f5f1dd8920d417aac2718b0bda3403da274301efdd6760b4f0f4b864ff2ad57d
T5="size-2000-port size-5000-port size-7500-port escaping-banner injection-retarget"
export GGML_ENV=NCCL_P2P_DISABLE=1
B=(-fa on -sm tensor)
./serve_bench.sh c-ornith-tensor $D/Ornith-1.5-35B-Q4_K_M.gguf "$T5" "${B[@]}"
./serve_bench.sh c-ornith-tensor-mtp3 $D/Ornith-1.5-35B-Q4_K_M.gguf "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 3
./serve_bench.sh c-q38unsloth-tensor-mtp4 $DL/Qwen3.8-27B-Q8_0.gguf "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 4
./serve_bench.sh c-q38hauhau-tensor-mtp4 $DL/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 4
./serve_bench.sh c-q38stockq4-tensor-mtp4 $STOCK "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 4
./serve_bench.sh c-q36abl-tensor-mtp38file $M/qwen3.6-27b-abliterated_q5_k_m.gguf "$T5" "${B[@]}" -md $D/mtp-Qwen3.8-27B-Q8_0.gguf --spec-type draft-mtp --spec-draft-n-max 3
./summ.py serve/c-*.json
echo PHASE_DONE
