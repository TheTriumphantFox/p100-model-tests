#!/usr/bin/env python3
"""set_ctx.py SECTION CTX -- set ctx-size inside one [SECTION] of ~/llama-cuda12/models.ini."""
import re, sys
from pathlib import Path
p = Path.home() / "llama-cuda12/models.ini"
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
