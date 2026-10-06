#!/usr/bin/env bash
# Flash-Next IQ2_XXS with the MTP head appended as block 48 (append_mtp.py), PR #27836 @1d8de7c.
cd "$(dirname "$0")"
export ROOT=$HOME/llama-cuda12-mtp SPEC_AB_OUT=$PWD NPRED=400
M=$HOME/models/qwen3.8-flash-next_iq2_xxs-mtp/Qwen3.8-Flash-Next-IQ2_XXS-MTP-00001-of-00002.gguf
S=~/Projects/Tests/scripts/spec_ab.sh
$S mtpfile-base $M none
for n in 1 2 3; do EXTRA="--spec-draft-n-max $n" $S mtpfile-n$n $M draft-mtp; done
EXTRA="--spec-draft-n-max 2 --spec-draft-p-min 0.75" $S mtpfile-n2-pmin75 $M draft-mtp
echo AB_DONE
