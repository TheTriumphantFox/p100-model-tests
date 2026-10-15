#!/usr/bin/env bash
# Requires a maintained Gitleaks binary. No silent skip if the scanner is missing.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
command -v gitleaks >/dev/null || { echo 'Gitleaks is required; see SECURITY.md for the pinned verified release' >&2; exit 2; }
case "${1:-all}" in
  staged) exec gitleaks git --pre-commit --staged --redact --ignore-gitleaks-allow --config .gitleaks.toml . ;;
  all)
    gitleaks git --log-opts=--all --redact --ignore-gitleaks-allow --max-decode-depth=2 --config .gitleaks.toml .
    exec gitleaks dir --redact --ignore-gitleaks-allow --max-decode-depth=2 --config .gitleaks.toml . ;;
  *) echo 'Usage: check_secrets.sh [all|staged]' >&2; exit 2 ;;
esac
