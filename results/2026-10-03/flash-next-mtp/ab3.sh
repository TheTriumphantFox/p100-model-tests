#!/usr/bin/env bash
# Warm-cache rerun, interleaved to expose drift: base, n2/p-min .75, n3, base.
cd "$(dirname "$0")"
export ROOT=$HOME/llama-cuda12-mtp SPEC_AB_OUT=$PWD NPRED=400
M=$HOME/models/qwen3.8-flash-next_iq2_xxs-mtp/Qwen3.8-Flash-Next-IQ2_XXS-MTP-00001-of-00002.gguf
S=~/Projects/Tests/scripts/spec_ab.sh
$S warm-base-a $M none
EXTRA="--spec-draft-n-max 2 --spec-draft-p-min 0.75" $S warm-n2-pmin75 $M draft-mtp
EXTRA="--spec-draft-n-max 3 --spec-draft-p-min 0.75" $S warm-n3-pmin75 $M draft-mtp
$S warm-base-b $M none
echo AB_DONE
