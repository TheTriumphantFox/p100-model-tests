#!/usr/bin/env bash
# Historical entry point now delegates to the hardened launcher; no host-network fallback.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
exec bash "$ROOT/scripts/secure_polyglot.sh" "$@"
