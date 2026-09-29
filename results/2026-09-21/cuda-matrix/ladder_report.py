#!/usr/bin/env python3
"""Read the context ladders and report where each model stops fitting, and what it costs.

    ladder_report.py              table of every rung
    ladder_report.py --best SLUG  largest fully-resident context, for scripts

Derives each model's KV cost per token from the data rather than a published figure:
between two RESIDENT rungs the only thing that grows is the KV cache, so

    bytes/token = (vram_hi - vram_lo) / (ctx_hi - ctx_lo)

A rung is 'spilled' when the resident VRAM is materially below the weight file itself --
llama.cpp keeps serving in that state at a fraction of the decode rate, which is exactly
what the tok/s column prices.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
LAD = RUN / "ctx-ladder"


def load() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    if not LAD.is_dir():
        return out
    for f in sorted(LAD.glob("*.jsonl")):
        rows = []
        for line in f.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        if rows:
            out[f.stem] = sorted(rows, key=lambda r: r["ctx"])
    return out


def best_resident(rows: list[dict]) -> int:
    fit = [r["ctx"] for r in rows if r.get("status") == "resident"]
    return max(fit) if fit else 0


def kv_bytes_per_token(rows: list[dict]) -> float | None:
    fit = [r for r in rows if r.get("status") == "resident" and r.get("vram_mib")]
    if len(fit) < 2:
        return None
    lo, hi = fit[0], fit[-1]
    if hi["ctx"] == lo["ctx"]:
        return None
    return (hi["vram_mib"] - lo["vram_mib"]) * 1048576 / (hi["ctx"] - lo["ctx"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--best", metavar="SLUG")
    args = ap.parse_args()
    data = load()

    if args.best:
        rows = data.get(args.best)
        if not rows:
            return 1
        print(best_resident(rows))
        return 0

    if not data:
        print("no ladders on disk yet")
        return 0

    print(f"{'model':<18} {'ctx':>7} {'VRAM MiB':>9} {'weights':>8} {'tok/s':>7}  status")
    print("-" * 66)
    for slug, rows in data.items():
        for r in rows:
            print(f"{slug:<18} {r['ctx']:>7} {r.get('vram_mib', 0):>9} "
                  f"{r.get('weights_mib', 0):>8} {r.get('tok_per_s') or 0:>7.2f}  {r.get('status')}")
        b = best_resident(rows)
        kv = kv_bytes_per_token(rows)
        note = f"  largest fully-resident context: {b}" if b else "  never fully resident"
        if kv:
            note += f"; measured KV {kv / 1024:.1f} KiB/token"
        # The cost of a spill, stated as the ratio the owner actually feels.
        res = [r for r in rows if r.get("status") == "resident" and (r.get("tok_per_s") or 0) > 0]
        spl = [r for r in rows if r.get("status") == "spilled" and (r.get("tok_per_s") or 0) > 0]
        if res and spl:
            note += (f"; spilling at {spl[0]['ctx']} costs "
                     f"{res[-1]['tok_per_s'] / spl[0]['tok_per_s']:.1f}x speed "
                     f"({res[-1]['tok_per_s']:.1f} -> {spl[0]['tok_per_s']:.1f} tok/s)")
        print(note)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
