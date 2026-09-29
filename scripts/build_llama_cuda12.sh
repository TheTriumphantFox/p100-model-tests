#!/usr/bin/env bash
# Build llama.cpp against CUDA 12.6 with sm_60 (Pascal / Tesla P100).
# Host has CUDA 13.x, which dropped Pascal; the container supplies both a
# CUDA 12 toolkit and a gcc nvcc accepts. No GPU needed to compile.
set -euo pipefail

OUT=${OUT:-/home/hm/llama-cuda12}
# REPO/REF let one script build an out-of-tree architecture branch (e.g. an open
# PR adding a model arch) into its own OUT without touching the production build.
REPO=${REPO:-https://github.com/ggml-org/llama.cpp}
REF=${REF:-}
IMG=docker.io/nvidia/cuda:12.6.3-devel-ubuntu24.04
mkdir -p "$OUT"

podman run --rm -v "$OUT":/out:Z -e REPO="$REPO" -e REF="$REF" "$IMG" bash -euxc '
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq git cmake ninja-build build-essential

  if [ -n "$REF" ]; then git clone --depth 1 -b "$REF" "$REPO" /src
  else git clone --depth 1 "$REPO" /src; fi
  git -C /src rev-parse HEAD > /out/LLAMA_COMMIT
  echo "$REPO ${REF:-default}" > /out/LLAMA_SOURCE

  # libcuda.so.1 is the DRIVER lib, absent without --gpus. Link against the
  # toolkit stub; the host supplies the real one at runtime.
  ln -sf /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1
  STUBS=-L/usr/local/cuda/lib64/stubs\ -Wl,-rpath-link,/usr/local/cuda/lib64/stubs

  cmake -S /src -B /b -G Ninja \
      -DCMAKE_BUILD_TYPE=Release \
      -DGGML_CUDA=ON \
      -DCMAKE_CUDA_ARCHITECTURES=60 \
      -DLLAMA_CURL=OFF \
      -DLLAMA_BUILD_TESTS=OFF \
      -DCMAKE_EXE_LINKER_FLAGS="$STUBS" \
      -DCMAKE_SHARED_LINKER_FLAGS="$STUBS"
  cmake --build /b -j"$(nproc)" --target llama-server llama-bench llama-cli

  mkdir -p /out/bin /out/lib
  find /b/bin -maxdepth 1 -type f -executable -exec cp -a {} /out/bin/ \;
  find /b -name "*.so*" -exec cp -a {} /out/lib/ \;

  # /usr/local/cuda/lib64 is a SYMLINK, so plain `find` descends nothing and copies
  # nothing - the runtime then dies with "libcudart.so.12: cannot open shared object
  # file". -L is load-bearing. libnccl is needed for the multi-GPU split, and the
  # image installs it from the libnccl2 apt package into /usr/lib/x86_64-linux-gnu,
  # NOT the CUDA tree - searching only lib64 fails the assert below.
  for l in libcudart libcublas libcublasLt libnccl; do
    find -L /usr/local/cuda/lib64 /usr/lib/x86_64-linux-gnu -maxdepth 1 -name "${l}.so*" -exec cp -a {} /out/lib/ \;
  done
  for l in libcudart libcublas libcublasLt libnccl; do
    ls /out/lib/${l}.so* >/dev/null 2>&1 || { echo "FATAL: ${l} not copied into /out/lib"; exit 1; }
  done
  chmod -R a+rX /out
'
echo "BUILD OK: $(cat "$OUT"/LLAMA_COMMIT) from $(cat "$OUT"/LLAMA_SOURCE 2>/dev/null) -> $OUT"
