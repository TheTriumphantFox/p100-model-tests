#!/usr/bin/env bash
# Fetch Unsloth's Qwen3.6-27B Q8_0 -- the STOCK model (not abliterated), as a plain-Q8_0
# reference beside the incumbent's own abliteration at Q8_K_P. Pinned to revision 82d411ac.
# Differences vs the incumbent are quant AND abliteration together; refusals unmeasured.
#
# /home is NVMe (~245 GB free); /var/lib/ollama is the 181 MB/s HDD that costs ~160s per load.
set -euo pipefail
REPO=unsloth/Qwen3.6-27B-GGUF
REV=82d411acf4a06cfb8d9b073a5211bf410bfc29bf
FILE=Qwen3.6-27B-Q8_0.gguf
SHA=f93f517f38e696d35a1a7df2c0e3155a64f4c4dcd662107a146ae263f7fb14ce
SIZE=28595763424
DEST=$HOME/models/qwen3.6-27b-unsloth_q8_0.gguf
LINK=$HOME/llama-bench-models/qwen3.6-27b-unsloth_q8_0.gguf

if [ ! -f "$DEST" ]; then
  # -C - resumes a partial .part after an interruption
  curl -fL -C - --retry 5 --retry-delay 10 -o "$DEST.part" \
    "https://huggingface.co/$REPO/resolve/$REV/$FILE"
  got=$(stat -c %s "$DEST.part")
  [ "$got" = "$SIZE" ] || { echo "size $got != $SIZE -- rerun to resume"; exit 1; }
  echo "verifying sha256..."
  echo "$SHA  $DEST.part" | sha256sum -c -
  mv "$DEST.part" "$DEST"
fi
ln -sfn "$DEST" "$LINK"
echo "OK: $LINK -> $DEST"
