#!/usr/bin/env python3
"""Summarize the night's thinking-on legs and pair them (exact McNemar) with the earlier runs."""
import json, subprocess, sys
from pathlib import Path

T = Path.home() / "Projects/Tests"
RUN = T / "2026-10-05/think-fix-full"
MC = T / "2026-09-21/cuda-matrix/mcnemar.py"
PY = str(T / ".venv/bin/python")
BASE = {
    "q38-q4km-0919": T / "2026-09-19/candidates-round2/mmlu-qwen38-27b-think12288",       # Qwen3.8-27B stock Q4_K_M, no fix
    "incumbent-0919": T / "2026-09-19/candidates-round2/mmlu-qwen36-rerun-think12288",    # qwen3.6-27b-abl Q5_K_M
    "flashnext-1002": T / "2026-10-02/flash-next-full/mmlu-flashnext-iq2-pc5-think12288", # Flash-Next, no fix
}
LEGS = {f"{m}-{l}": RUN / f"mmlu-{m}-{l}" for m in ("q6k", "flashnext") for l in "AB"}


def load(d):
    try:
        return json.loads((d / "results.json").read_text())
    except Exception:
        return None


rows = []
cats = None
print("# MMLU-Pro thinking-on, 70 Q (seed 42, 5/category, np 12288)\n")
print("| run | accuracy | correct | parsed | results | gen tokens | batches at cap | wall min |")
print("|---|---:|---:|---:|---:|---:|---:|---:|")
for name, d in {**BASE, **LEGS}.items():
    r = load(d)
    if not r:
        print(f"| {name} | (no run) | | | | | | |"); continue
    s, b = r["model_summaries"][0], r["batches"]
    tok = sum((x.get("eval_count") or 0) for x in b)
    cap = sum(1 for x in b if (x.get("eval_count") or 0) >= 12288)
    wall = sum((x.get("wall_seconds") or 0) for x in b) / 60
    print(f"| {name} | {s['accuracy']:.2f}% | {s['correct']}/{s['total']} | {s['parsed']} | "
          f"{len(r['results'])} | {tok} | {cap} | {wall:.0f} |")
    rows.append((name, r))

print("\n## Per category (correct of 5; tokens)\n")
names = [n for n, _ in rows]
print("| category | " + " | ".join(names) + " |")
print("|---|" + "---:|" * len(names))
by = {n: {x["category"]: x for x in r["batches"]} for n, r in rows}
for c in sorted({c for n in names for c in by[n]}):
    cells = []
    for n in names:
        x = by[n].get(c)
        cells.append(f"{x['correct']} ({x.get('eval_count') or 0})" if x else "-")
    print(f"| {c} | " + " | ".join(cells) + " |")

print("\n## Paired (exact McNemar)\n")
for a, b in [("q38-q4km-0919", "q6k-A"), ("incumbent-0919", "q6k-A"), ("q6k-A", "q6k-B"),
             ("flashnext-1002", "flashnext-A"), ("incumbent-0919", "flashnext-A"),
             ("flashnext-A", "flashnext-B"), ("q6k-B", "flashnext-B")]:
    da, db = {**BASE, **LEGS}[a], {**BASE, **LEGS}[b]
    print(f"### {a} vs {b}\n```")
    if load(da) and load(db):
        out = subprocess.run([PY, str(MC), str(da), str(db), a, b], capture_output=True, text=True)
        print((out.stdout + out.stderr).strip())
    else:
        print("(missing run)")
    print("```")
