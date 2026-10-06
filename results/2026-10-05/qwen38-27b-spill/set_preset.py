#!/usr/bin/env python3
"""set_preset.py SECTION KEY=VALUE ... -- set keys inside one [SECTION] of ~/llama-cuda12/models.ini.
A key that is missing is added at the end of the section; VALUE "-" deletes the key."""
import re, sys
from pathlib import Path
p = Path.home() / "llama-cuda12/models.ini"
sec, pairs = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
lines = p.read_text().splitlines(keepends=True)
start = next(i for i, l in enumerate(lines) if l.strip() == f"[{sec}]")
end = next((i for i in range(start + 1, len(lines)) if re.match(r"\[.+\]\s*$", lines[i])), len(lines))
while end > start + 1 and (not lines[end - 1].strip() or lines[end - 1].lstrip().startswith(";")):
    end -= 1  # keep trailing comments/blank lines that belong to the next section
body = lines[start + 1:end]
for k, v in pairs.items():
    idx = [i for i, l in enumerate(body) if re.match(rf"{re.escape(k)}\s*=", l)]
    if v == "-":
        body = [l for i, l in enumerate(body) if i not in idx]
    elif idx:
        body[idx[0]] = f"{k} = {v}\n"
    else:
        body.append(f"{k} = {v}\n")
lines[start + 1:end] = body
p.write_text("".join(lines))
print(f"[{sec}] " + ", ".join(f"{k} = {v}" for k, v in pairs.items()))
