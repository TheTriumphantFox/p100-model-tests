#!/usr/bin/env bash
# Run Aider with no host networking, no shared writable caches, and a narrow Unix inference bridge.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
T=${P100_TEST_WORKSPACE:-$HOME/Projects/Tests}
[[ $# -gt 0 ]] || { echo 'Supply the command to run inside the container' >&2; exit 2; }
: "${P100_RUN_DIR:?Set P100_RUN_DIR to a NEW empty absolute output directory; archived results must not be reused}"
[[ "$P100_RUN_DIR" = /* && "$P100_RUN_DIR" != *:* && "$P100_RUN_DIR" != *,* ]] || { echo 'Invalid output path' >&2; exit 2; }
mkdir -p -- "$P100_RUN_DIR"
[[ -z "$(find "$P100_RUN_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]] || { echo 'Output directory must be empty' >&2; exit 2; }
[[ -d "$T/tools/aider" && -d "$T/tools/polyglot-benchmark" ]] || { echo 'Trusted Aider and exercise sources are missing' >&2; exit 2; }
[[ "$(podman info --format '{{.Host.Security.Rootless}}')" = true ]] || { echo 'Rootless Podman is required' >&2; exit 2; }
# Never pull a mutable remote image implicitly. Resolve the locally installed image to its immutable ID.
IMAGE=$(podman image inspect --format '{{.Id}}' "${P100_AIDER_IMAGE:-localhost/aider-benchmark}")
[[ "$IMAGE" =~ ^(sha256:)?[0-9a-f]{64}$ ]] || { echo 'Invalid local image ID' >&2; exit 2; }
BRIDGE=$(mktemp -d /tmp/p100-inference.XXXXXXXX)
bridge_pid=''
cleanup() {
  if [[ -n "$bridge_pid" ]]; then kill "$bridge_pid" 2>/dev/null || true; wait "$bridge_pid" 2>/dev/null || true; fi
  rm -rf -- "$BRIDGE"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
env -i PATH=/usr/bin:/bin python3 "$ROOT/scripts/inference_bridge.py" host \
  --socket "$BRIDGE/router.sock" --upstream "${P100_INFERENCE_URL:-http://127.0.0.1:8081}" &
bridge_pid=$!
for _ in {1..50}; do
  [[ -S "$BRIDGE/router.sock" ]] && break
  kill -0 "$bridge_pid" 2>/dev/null || { echo 'Inference bridge failed' >&2; exit 2; }
  sleep .1
done
[[ -S "$BRIDGE/router.sock" ]] || { echo 'Inference bridge timed out' >&2; exit 2; }
# Cache seeds are optional, read-only public dependency artifacts. Copies are disposable tmpfs data.
cache_mounts=()
for cache in gradle cargo-registry; do
  if [[ -d "$T/tools/polyglot-cache/$cache" ]]; then cache_mounts+=(-v "$T/tools/polyglot-cache/$cache:/seed/$cache:ro"); fi
done
podman run --rm --pull=never --http-proxy=false --network none --read-only --cap-drop=ALL \
  --security-opt=no-new-privileges --pids-limit=256 --cpus=4 --memory=12g --memory-swap=12g \
  --ulimit nofile=1024:1024 --ulimit core=0:0 \
  --tmpfs /tmp:rw,nosuid,nodev,size=1g --tmpfs /root:rw,nosuid,nodev,size=3g \
  -e AIDER_DOCKER=1 -e OPENAI_API_BASE=http://127.0.0.1:8081/v1 -e OPENAI_API_KEY=sk-local \
  -v "$T/tools/aider:/aider:ro" -v "$T/tools/polyglot-benchmark:/polyglot:ro" \
  -v "$P100_RUN_DIR:/run:rw" -v "$ROOT/scripts:/scripts:ro" -v "$BRIDGE:/inference:ro" \
  "${cache_mounts[@]}" "$IMAGE" bash -euc '
    mkdir -p /root/.gradle /root/.cargo/registry
    if [ -d /seed/gradle ]; then cp -a /seed/gradle/. /root/.gradle/; fi
    if [ -d /seed/cargo-registry ]; then cp -a /seed/cargo-registry/. /root/.cargo/registry/; fi
    python3 /scripts/inference_bridge.py container --socket /inference/router.sock &
    adapter=$!
    trap '\''kill "$adapter" 2>/dev/null || true'\'' EXIT
    for i in $(seq 1 50); do
      python3 -c "import socket;s=socket.create_connection((\"127.0.0.1\",8081),.1);s.close()" 2>/dev/null && break
      kill -0 "$adapter"; sleep .1
    done
    cd /run
    # Apply file limits after OCI setup; combined crun setup rejected an OCI fsize limit here.
    ulimit -f 131072
    "$@"
  ' p100-container "$@"
