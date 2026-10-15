#!/usr/bin/env bash
# Build llama.cpp against CUDA 12.6 with sm_60 (Pascal / Tesla P100).
# Host has CUDA 13.x, which dropped Pascal; the container supplies both a
# CUDA 12 toolkit and a gcc nvcc accepts. No GPU needed to compile.
set -euo pipefail

# Defaults pin the locally validated Pascal build and its CUDA image.
# Override only with another reviewed full commit and registry digest, never a branch/tag.
REPO=${REPO:-https://github.com/ggml-org/llama.cpp}
LLAMA_COMMIT=${LLAMA_COMMIT:-50631b3d2c569ad8e5c112090cd28570b1268ee0}
IMG=${CUDA_IMAGE:-docker.io/nvidia/cuda@sha256:392c0df7b577ecae17a17f6ba7f2009c217bb4422f8431c053ae9af61a8c148a}
[[ "$REPO" == https://github.com/* && "$REPO" != *'@'* && "$REPO" != *'?'* && "$REPO" != *'#'* ]] || { echo 'REPO must be a credential-free GitHub HTTPS URL' >&2; exit 2; }
[[ "$LLAMA_COMMIT" =~ ^[0-9a-f]{40}$ && "$IMG" =~ ^docker.io/nvidia/cuda@sha256:[0-9a-f]{64}$ ]] || { echo 'Immutable source and image pins required' >&2; exit 2; }
[[ -z "${REF:-}" ]] || { echo 'REF is no longer supported; use a reviewed LLAMA_COMMIT' >&2; exit 2; }
OUT=${OUT:-$HOME/Projects/Tests/tools/llama-cuda12-$LLAMA_COMMIT}
mkdir -p "$OUT"
[[ -z "$(find "$OUT" -mindepth 1 -maxdepth 1 -print -quit)" ]] || { echo 'OUT must be a new empty build directory; existing builds are never overwritten' >&2; exit 2; }

podman run --rm --http-proxy=false --security-opt=no-new-privileges -v "$OUT":/out:Z -e REPO="$REPO" -e LLAMA_COMMIT="$LLAMA_COMMIT" "$IMG" bash -euxc '
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq git cmake ninja-build build-essential

  git init /src
  git -C /src remote add origin "$REPO"
  git -C /src fetch --depth 1 origin "$LLAMA_COMMIT"
  git -C /src checkout --detach FETCH_HEAD
  test "$(git -C /src rev-parse HEAD)" = "$LLAMA_COMMIT"
  git -C /src rev-parse HEAD > /out/LLAMA_COMMIT
  echo "$REPO $LLAMA_COMMIT" > /out/LLAMA_SOURCE
  # Apt repositories still move: preserve the installed package manifest for provenance.
  dpkg-query -W > /out/BUILD_PACKAGES

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
