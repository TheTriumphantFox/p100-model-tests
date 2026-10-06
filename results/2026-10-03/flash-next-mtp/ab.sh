#!/usr/bin/env bash
# Flash-Next IQ2_XXS + detached MTP head (PR ggml-org/llama.cpp#27836 @1d8de7c), stock --fit.
cd "$(dirname "$0")"
export ROOT=$HOME/llama-cuda12-mtp SPEC_AB_OUT=$PWD NPRED=400
M=$HOME/models/qwen3.8-flash-next_iq2_xxs/Qwen3.8-Flash-Next-IQ2_XXS/Qwen3.8-Flash-Next-IQ2_XXS-00001-of-00002.gguf
H=$HOME/models/flash-next-mtp-heads
S=~/Projects/Tests/scripts/spec_ab.sh
$S base-warmup $M none
$S base $M none
for n in 2 3 4; do EXTRA="--spec-draft-n-max $n" $S ggml-q4_0-n$n $M draft-mtp $H/mtp-Qwen3.8-Flash-Next-Q4_0.gguf; done
EXTRA="--spec-draft-n-max 3" $S unsloth-shared-q4km-n3 $M draft-mtp $H/MTP/mtp-Qwen3.8-Flash-Next-shared-Q4_K_M.gguf
echo AB_DONE
