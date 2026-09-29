#!/usr/bin/env bash
# Dump every measurement this matrix has, from the raw records. Reproducible: it reads
# results.json / *.jsonl only, computes nothing it cannot show the provenance of.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY=$HOME/Projects/Tests/.venv/bin/python
R2=$HOME/Projects/Tests/2026-09-19/candidates-round2
R1=$HOME/Projects/Tests/2026-09-19/candidates

echo "###############  CUDA BENCHMARK MATRIX  --  $(date '+%F %T')  ###############"
echo
echo "=== 1. THE MATRIX (--per-category 5, seed 42) ==="
echo
"$PY" "$HERE/matrix.py" --pc 5
echo
echo "=== 2. EVERY RUN, WITH ITS SETTINGS AND PROVENANCE ==="
echo
"$PY" "$HERE/inventory.py"
echo
echo "=== 3. CONTEXT LADDERS ==="
echo
"$PY" "$HERE/ladder_report.py"
echo
echo "=== 4. PAIRED TESTS (McNemar, exact, same questions) ==="
echo
"$PY" "$HERE/pairs.py"
echo
echo "=== 5. RIG STATE ==="
echo
nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv
echo
ss -ltnp 2>/dev/null | grep -E ':(8080|8081|8082|11500|11501)' | awk '{print $4, $6}'
echo
echo "queue tail:"; tail -8 "$HERE/driver.log"
