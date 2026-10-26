#!/usr/bin/env bash
# Build Strata's experimental CUDA 12 engine with sm_60 (Pascal / Tesla P100).
# Host has CUDA 13.x (dropped Pascal) and GCC 16 (too new for nvcc 12); the
# container supplies a CUDA 12.9 toolkit and a gcc nvcc accepts. No GPU needed.
# setup.py's own toolkit install is apt/Ubuntu-only, so it cannot do this here.
#
# Output: $STRATA/engine-cuda12/{strata,lib/} plus a BUILD.json stamped with
# setup.py's own source hash, so `setup.sh` treats the engine as already built.
set -euo pipefail

STRATA=${STRATA:-/home/hm/AI/Strata}
ARCHS=${ARCHS:-60}
IMG=docker.io/nvidia/cuda:12.9.1-devel-ubuntu24.04
ENG="$STRATA/engine-cuda12"

# ggml at the commit setup.py pins (third_party/llama.cpp); fetch it the same way setup does
[ -f "$STRATA/third_party/llama.cpp/ggml/CMakeLists.txt" ] ||
  (cd "$STRATA" && python3 -c "import setup; setup.get_llama_cpp()")

mkdir -p "$ENG/lib"
# ROOTFS=<dir from fetch_image_rootfs.py>: run on a flattened image instead of podman's
# store, for when the storage driver cannot start (kernel upgraded, modules gone until
# reboot: no overlay). An empty throwaway vfs store gets podman past its storage init.
if [ -n "${ROOTFS:-}" ]; then
  PODROOT=$(mktemp -d)
  PODMAN=(podman --storage-driver vfs --root "$PODROOT/root" --runroot "$PODROOT/run")
  # options first: the rootfs path takes the image's positional slot
  SRC=(--network host
       -e PATH=/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
       --rootfs "$ROOTFS")
else
  PODMAN=(podman)
  SRC=("$IMG")
fi
"${PODMAN[@]}" run --rm -v "$STRATA":/src:Z -e ARCHS="$ARCHS" "${SRC[@]}" bash -euxc '
  export DEBIAN_FRONTEND=noninteractive
  APT="-o APT::Sandbox::User=root"
  apt-get $APT update -qq
  apt-get $APT install -y -qq cmake ninja-build build-essential

  # libcuda.so.1 is the DRIVER lib (Strata uses the driver VMM API), absent
  # without --gpus. Link against the toolkit stub; the host supplies the real one.
  ln -sf /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1
  STUBS=-L/usr/local/cuda/lib64/stubs\ -Wl,-rpath-link,/usr/local/cuda/lib64/stubs

  # The same definitions setup.py build_engine() passes for a CUDA 12 engine
  cmake -G Ninja -S /src -B /src/build-cuda12 \
      -DCMAKE_BUILD_TYPE=Release \
      -DSTRATA_ENABLE_CUDA=ON -DSTRATA_BUILD_TESTS=OFF \
      -DCMAKE_CUDA_ARCHITECTURES="$ARCHS" \
      -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc -DCUDAToolkit_ROOT=/usr/local/cuda \
      -DSTRATA_GGML_DIR=/src/third_party/llama.cpp \
      -DSTRATA_EXPERIMENTAL_SM60=ON \
      -DCMAKE_EXE_LINKER_FLAGS="$STUBS" -DCMAKE_SHARED_LINKER_FLAGS="$STUBS"
  nice -n 19 cmake --build /src/build-cuda12 --target strata -j"$(( $(nproc) / 2 ))"
  cp -a /src/build-cuda12/strata /src/engine-cuda12/strata

  # /usr/local/cuda/lib64 is a SYMLINK: without -L, find copies nothing and the
  # engine later dies on a missing libcublas. The ldd check below catches it.
  for l in libcudart libcublas libcublasLt libnccl; do
    find -L /usr/local/cuda/lib64 /usr/lib/x86_64-linux-gnu -maxdepth 1 -name "${l}.so*" \
      -exec cp -a {} /src/engine-cuda12/lib/ \;
  done
  chmod -R a+rX /src/engine-cuda12
'
[ -z "${PODROOT:-}" ] || rm -rf "$PODROOT"

# Every shared lib the engine needs must resolve on the HOST, with only lib/ added
missing=$(LD_LIBRARY_PATH="$ENG/lib" ldd "$ENG/strata" | grep "not found" || true)
[ -z "$missing" ] || { echo "FATAL: unresolved libs:"; echo "$missing"; exit 1; }

# Stamp BUILD.json exactly as setup.py build_engine() would after its own compile
(cd "$STRATA" && ENG="$ENG" ARCHS="$ARCHS" python3 - <<'PY'
import json, os, setup
from pathlib import Path
eng = Path(os.environ["ENG"])
floor = setup.cpu_floor(setup.cpu_info()[1])
meta = {"source": "local", "version": setup.source_version(),
        "archs": sorted(int(a) for a in os.environ["ARCHS"].split(";")),
        "vision": "none", "toolkit": 12, "cuda_dirs": [str(eng / "lib")],
        "src": setup.source_hash(setup.ENGINE_SOURCES), "vision_src": None,
        **({"isa_floor": floor} if floor else {})}
assert not setup.stale_binary(eng / setup.EXE), "binary version != source version"
(eng / "BUILD.json").write_text(json.dumps(meta, indent=1))
print("stamped", eng / "BUILD.json", meta["version"], meta["archs"])
PY
)
echo "BUILD OK: $("$ENG/strata" --version 2>/dev/null | head -1 || echo strata) -> $ENG"
