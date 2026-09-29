#!/usr/bin/env python3
"""Run-to-run variance as a function of generated-token volume.

Each arm repeats ONE measurement at fixed settings. The spread across repeats is the
result: it is the variance that every between-model p-value in the matrix silently
assumes to be zero.
"""
from __future__ import annotations

import json
from itertools import combinations
from math import comb
from pathlib import Path

RUN = Path(__file__).resolve().parent
OUT = RUN / "repro"
ARMS = [
    ("A", "incumbent MMLU-off (control)", "A-incumbent-off-*", "~280"),
    ("B", "gpt-oss MMLU-off", "B-gptoss-off-*", "~5-7k"),
    ("C", "gpt-oss MMLU-off, no reasoning_effort", "C-gptoss-off-noeffort", "?"),
    ("D", "incumbent MMLU-ON", "D-incumbent-on-*", "~44k"),
]
HISTORIC = {
    "B": [("round 1, 2026-09-19", RUN.parents[1] / "2026-09-19/candidates/mmlu-gpt-oss"),
          ("matrix, 2026-09-21", RUN / "mmlu-gpt-oss-20b-pc5-np2048")],
    "D": [("round 2, 2026-09-20", RUN.parents[1]
           / "2026-09-19/candidates-round2/mmlu-qwen36-rerun-think12288")],
}


def load(d: Path):
    f = d / "results.json"
    if not f.is_file():
        return None
    p = json.loads(f.read_text())
    if not (p.get("metadata") or {}).get("finished"):
        return None
    s = p["model_summaries"][0]
    items = {str(r["question_id"]): bool(r["correct"]) for r in p["results"]}
    return dict(name=d.name, acc=s["accuracy"], parsed=s["parsed"], total=s["total"],
                tok=sum(int(b.get("eval_count") or 0) for b in p["batches"]), items=items)


def exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def main() -> int:
    print(f"{'arm':<4} {'run':<28} {'score':>7} {'parsed':>8} {'gen tok':>9}")
    print("-" * 60)
    got: dict[str, list] = {}
    for key, label, pat, _ in ARMS:
        runs = [load(d) for d in sorted(OUT.glob(pat))] if OUT.is_dir() else []
        runs = [r for r in runs if r]
        for lbl, d in HISTORIC.get(key, []):
            h = load(d)
            if h:
                h["name"] = lbl
                runs.insert(0, h)
        got[key] = runs
        if not runs:
            print(f"{key:<4} {label:<28} not run yet")
            continue
        for r in runs:
            print(f"{key:<4} {r['name']:<28} {r['acc']:>6.2f}% "
                  f"{r['parsed']:>4}/{r['total']:<3} {r['tok']:>9}")
        print()

    print("\n=== SPREAD ACROSS REPEATS (the result) ===\n")
    for key, label, _, vol in ARMS:
        runs = got.get(key) or []
        if len(runs) < 2:
            print(f"{key}  {label:<40} needs 2+ runs (have {len(runs)})")
            continue
        accs = [r["acc"] for r in runs]
        toks = [r["tok"] for r in runs]
        spread = max(accs) - min(accs)
        # Identical item-level records, or merely an identical score?
        ident = all(runs[0]["items"] == r["items"] for r in runs[1:])
        print(f"{key}  {label}")
        print(f"     output volume   {vol} tok/run (measured {min(toks)}-{max(toks)})")
        print(f"     scores          {', '.join(f'{a:.2f}%' for a in accs)}")
        print(f"     SPREAD          {spread:.2f} points")
        print(f"     item-identical  {'YES -- fully deterministic' if ident else 'NO'}")
        if not ident:
            for a, b in combinations(range(len(runs)), 2):
                x = sum(1 for q in runs[a]["items"]
                        if runs[a]["items"][q] and not runs[b]["items"][q])
                y = sum(1 for q in runs[a]["items"]
                        if runs[b]["items"][q] and not runs[a]["items"][q])
                if x or y:
                    print(f"       {runs[a]['name']} vs {runs[b]['name']}: "
                          f"discordant {x}/{y}, p={exact(x, y):.4f}")
        print()

    d_spread = None
    if len(got.get("D") or []) >= 2:
        accs = [r["acc"] for r in got["D"]]
        d_spread = max(accs) - min(accs)
    print("HOW TO READ THIS:")
    print("  Arm A is the control. If it is item-identical, the harness and rig are")
    print("  deterministic and any spread in B/D is caused by output length, not by setup.")
    print("  Arm C separates the two explanations for gpt-oss: if it reproduces round 1's")
    print("  ~7,170 tokens and ~77%, the shim's reasoning_effort was the cause and there is")
    print("  no nondeterminism to worry about. If it lands with arm B, it is nondeterminism.")
    if d_spread is not None:
        print(f"  Arm D measured a {d_spread:.2f}-point spread on the thinking-on column.")
        print("  Any thinking-on gap smaller than that is not resolvable by this harness,")
        print("  whatever its p-value -- McNemar assumes the only variation is between models.")
    else:
        print("  Arm D is the one that matters: it prices the thinking-on column's own")
        print("  variance, which every MMLU-ON p-value in the matrix assumes to be zero.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
