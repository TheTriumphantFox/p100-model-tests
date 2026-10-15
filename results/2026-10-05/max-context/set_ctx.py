#!/usr/bin/env python3
"""set_ctx.py SECTION CTX -- set ctx-size inside one [SECTION] of ~/llama-cuda12/models.ini."""
import os, re, sys
from pathlib import Path
if os.environ.get("P100_ALLOW_ARCHIVED_DRIVER") != "1" or not os.environ.get("P100_PRESET_FILE"):
    sys.exit("Refusing archived preset edit: explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 and P100_PRESET_FILE to a disposable preset copy. See SECURITY.md.")
p = Path(os.environ["P100_PRESET_FILE"]).resolve()
sec, ctx = sys.argv[1], sys.argv[2]
out, cur, done = [], None, False
for line in p.read_text().splitlines(keepends=True):
    m = re.match(r"\[(.+)\]\s*$", line)
    if m:
        cur = m.group(1)
    if cur == sec and re.match(r"ctx-size\s*=", line):
        line = f"ctx-size = {ctx}\n"; done = True
    out.append(line)
if not done:
    sys.exit(f"no ctx-size in [{sec}]")
p.write_text("".join(out)); print(f"[{sec}] ctx-size = {ctx}")
