#!/usr/bin/env bash
# Fetch HauhauCS Qwen3.6-27B-Uncensored-Aggressive Q8_K_P onto the NVMe and verify it.
#
# Pinned to revision f2db94d0 (2026-04-24, "Upgraded coherence") -- the v2 upload.
# The incumbent q5_k_m is 20,812,953,056 bytes and reports general.version v2, which is
# exactly the v2 Q5_K_P size (v1 was 32 bytes shorter). Its sha256 (9200d792...) matches
# NEITHER published revision, though, so "same revision" is inferred from size + metadata,
# not proven by hash. See REPORT.md.
#
# /home is NVMe (~245 GB free); /var/lib/ollama is the 181 MB/s HDD that costs ~160s per load.
set -euo pipefail
REPO=HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Aggressive
REV=f2db94d03eccf3b133aeea3dea62388acf98e864
FILE=Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-Q8_K_P.gguf
SHA=77672ff20cf3c6b99fe875df1e7f53fec4ded86e767fbfaef40b5def61b112ca
SIZE=31963749856
DEST=$HOME/models/qwen3.6-27b-abliterated_q8_k_p.gguf
LINK=$HOME/llama-bench-models/qwen3.6-27b-abliterated_q8_k_p.gguf

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
