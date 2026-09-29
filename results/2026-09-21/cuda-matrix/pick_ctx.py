#!/usr/bin/env python3
"""Largest context from a ladder that actually served tokens, and its decode rate.

    pick_ctx.py <ladder.jsonl> <preferred-ctx>   ->  "<ctx> <tok_per_s>"  (or "0 0")

Prefers the requested context; falls back to the largest rung that served anything.
A SPILLED rung still counts as serving -- it answers correctly, just slowly, and that
slowness is the measurement. A rung that served nothing does not count.
"""
import json
import sys
from pathlib import Path

f, target = Path(sys.argv[1]), int(sys.argv[2])
rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.is_file() else []
ran = [r for r in rows if (r.get("tok_per_s") or 0) > 0]
hit = [r for r in ran if r["ctx"] == target]
pick = hit[0] if hit else (max(ran, key=lambda r: r["ctx"]) if ran else None)
print(f"{pick['ctx']} {pick['tok_per_s']:.2f}" if pick else "0 0")
