#!/usr/bin/env bash
# Rebuild bench-sheet.html from whatever runs are currently on disk.
#
# The page carries its data inline, so it is a BUILD product: edit
# bench-sheet.template.html for design changes, never bench-sheet.html, or the next
# build overwrites you. Run this after any new model is benchmarked.
#
# To update the published artifact at the SAME url rather than creating a second one,
# republish bench-sheet.html passing that url explicitly:
#   https://claude.ai/artifact/5sv44WSnA1yPSmRjaSr4wQ
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY=$HOME/Projects/Tests/.venv/bin/python
"$PY" "$HERE/export_all.py" > "$HERE/all.json"
"$PY" -c "
import json,sys
d=json.load(open('$HERE/all.json'))
open('$HERE/all.min.json','w').write(json.dumps(d,separators=(',',':')))
print(len(d['models']),'models exported')
"
"$PY" - <<'PYEOF'
from pathlib import Path
d = Path("/home/hm/Projects/Tests/2026-09-21/cuda-matrix")
tpl = (d / "bench-sheet.template.html").read_text()
data = (d / "all.min.json").read_text().strip()
assert "__DATA__" in tpl, "template lost its __DATA__ placeholder"
(d / "bench-sheet.html").write_text(tpl.replace("__DATA__", data, 1))
print("bench-sheet.html rebuilt:", len((d / "bench-sheet.html").read_text()), "bytes")
PYEOF
