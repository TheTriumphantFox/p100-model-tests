#!/usr/bin/env python3
"""Summarise a capped Aider Polyglot run.

Scores every model on the COMMON prefix only: the exercises every model finished. A model
that got further is not credited for the extra exercises in the headline table, because
the comparison is paired. Pairwise differences use an exact McNemar test on the
discordant exercises (one model passed, the other did not), which is the only honest
test for paired pass/fail outcomes on a set this small.

    summarise.py [run dir]     (prints markdown; also writes summary.json)
"""
import json
import sys
from math import comb
from pathlib import Path

run = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
order = [ln.strip() for ln in (run / "order.txt").read_text().splitlines() if ln.strip()]
models = [m for m in ["gpt-oss-20b_q8_0", "qwen3.6-35b-a3b_ud-q6_k", "devstral-patched_q8_0",
                      "qwen3.6-27b-abliterated_q5_k_m", "qwen3.8-27b-unsloth_q8_0"]
          if (run / "runs" / m / "progress.jsonl").exists()]
if len(sys.argv) > 2:  # optional comma-separated subset, e.g. the overnight top 3
    models = [m for m in models if m in sys.argv[2].split(",")]


def load(m):
    rows = {}
    for line in open(run / "runs" / m / "progress.jsonl"):
        r = json.loads(line)
        rows[r["exercise"]] = r
    return rows


data = {m: load(m) for m in models}
common = [e for e in order if all(e in data[m] for m in models)]


def mcnemar_p(b, c):
    """Exact two-sided McNemar p from discordant counts b, c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


langs = ["cpp", "go", "java", "javascript", "python", "rust"]
out = [f"Common prefix: **{len(common)} exercises** "
       f"({', '.join(f'{lg} {sum(e.startswith(lg + "/") for e in common)}' for lg in langs)})\n"]
out.append("| Model | pass@1 | pass@2 | malformed replies | exceptions | output tok/exercise | wall s/exercise | scored total |")
out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
summary = {"common": common, "models": {}}
for m in models:
    rows = [data[m][e] for e in common]
    n = len(rows) or 1
    p1 = sum(bool(r["outcomes"] and r["outcomes"][0]) for r in rows)
    p2 = sum(r["pass"] for r in rows)
    mal = sum(r.get("malformed") or 0 for r in rows)
    exc = sum(r.get("exception", False) for r in rows)
    tok = sum(r.get("completion_tokens") or 0 for r in rows) / n
    wall = sum(r["wall_s"] for r in rows) / n
    summary["models"][m] = {"pass1": p1, "pass2": p2, "n": len(rows), "malformed": mal,
                            "exceptions": exc, "tok_per_ex": round(tok), "wall_per_ex": round(wall),
                            "scored_total": len(data[m]),
                            "by_lang": {lg: [sum(r["pass"] for r in rows if r["exercise"].startswith(lg + "/")),
                                             sum(r["exercise"].startswith(lg + "/") for r in rows)] for lg in langs}}
    out.append(f"| {m} | {p1}/{len(rows)} ({100 * p1 / n:.0f}%) | **{p2}/{len(rows)} ({100 * p2 / n:.0f}%)** "
               f"| {mal} | {exc} | {tok:.0f} | {wall:.0f} | {len(data[m])} |")

out.append("\n**pass@2 by language** (passed/attempted on the common prefix)\n")
out.append("| Model | " + " | ".join(langs) + " |")
out.append("|---|" + "---:|" * len(langs))
for m in models:
    bl = summary["models"][m]["by_lang"]
    out.append(f"| {m} | " + " | ".join(f"{bl[lg][0]}/{bl[lg][1]}" for lg in langs) + " |")

out.append("\n**Paired comparison (exact McNemar, pass@2)**: row passed & column failed / reverse, p\n")
out.append("| | " + " | ".join(models) + " |")
out.append("|---|" + "---|" * len(models))
summary["pairs"] = {}
for a in models:
    cells = []
    for b in models:
        if a == b:
            cells.append("—")
            continue
        w = sum(data[a][e]["pass"] and not data[b][e]["pass"] for e in common)
        l_ = sum(data[b][e]["pass"] and not data[a][e]["pass"] for e in common)
        p = mcnemar_p(w, l_)
        summary["pairs"][f"{a}|{b}"] = [w, l_, p]
        cells.append(f"{w}/{l_} p={p:.2f}")
    out.append(f"| {a} | " + " | ".join(cells) + " |")

never = [e for e in common if not any(data[m][e]["pass"] for m in models)]
every = [e for e in common if all(data[m][e]["pass"] for m in models)]
out.append(f"\nPassed by every model: {len(every)}. Passed by none: {len(never)}.")
(run / ("summary.json" if len(sys.argv) <= 2 else "summary-top3.json")).write_text(json.dumps(summary, indent=2))
print("\n".join(out))
