#!/usr/bin/env python3
"""Flash-Next vs the 2026-10-01 Polyglot models on the exercises both attempted.

Same fixed order, same aider commit, whole format, thinking off, 2 tries, so exercise i is
the same task for every model. Pairs by exercise name with an exact McNemar test.
    compare.py            -> markdown to stdout
"""
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = Path("/home/hm/Projects/Tests/2026-10-01/aider-polyglot-10h/runs")
FN = "qwen3.8-flash-next_iq2_xxs"
OTHERS = ["qwen3.6-27b-abliterated_q5_k_m", "qwen3.6-35b-a3b_ud-q6_k", "qwen3.8-27b-unsloth_q8_0",
          "devstral-patched_q8_0", "gpt-oss-20b_q8_0"]


def load(p):
    rows = {}
    if p.exists():
        for l in open(p):
            if l.strip():
                r = json.loads(l)
                rows[r["exercise"]] = r
    return rows


def mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


fn = load(HERE / "runs" / FN / "progress.jsonl")
order = [l.strip() for l in open(HERE / "order.txt") if l.strip()]
done = [e for e in order if e in fn]
print(f"Flash-Next scored {len(done)} exercises.\n")
print("| model | n (common) | pass@2 | pass@1 | mean s/exercise | Flash-Next only / model only | p |")
print("|---|---:|---:|---:|---:|---:|---:|")


def stats(rows, ex):
    p2 = sum(rows[e]["pass"] for e in ex)
    p1 = sum(bool(rows[e]["outcomes"]) and rows[e]["outcomes"][0] for e in ex)
    w = sum(rows[e]["wall_s"] for e in ex) / max(1, len(ex))
    return p2, p1, w


p2, p1, w = stats(fn, done)
print(f"| **qwen3.8-flash-next IQ2_XXS** | {len(done)} | **{p2}/{len(done)} ({100*p2/max(1,len(done)):.0f}%)** | {p1} | {w:.0f} | — | — |")
for m in OTHERS:
    o = load(OLD / m / "progress.jsonl")
    ex = [e for e in done if e in o]
    if not ex:
        continue
    q2, q1, qw = stats(o, ex)
    b = sum(fn[e]["pass"] and not o[e]["pass"] for e in ex)
    c = sum(o[e]["pass"] and not fn[e]["pass"] for e in ex)
    _, _, fw = stats(fn, ex)
    print(f"| {m} | {len(ex)} | {q2}/{len(ex)} ({100*q2/len(ex):.0f}%) | {q1} | {qw:.0f} (FN {fw:.0f}) | {b} / {c} | {mcnemar(b, c):.2f} |")

tok = [fn[e]["prompt_tokens"] for e in done]
print(f"\nFlash-Next prompt tokens per exercise: median {sorted(tok)[len(tok)//2]}, max {max(tok)}; "
      f"exceptions {sum(fn[e]['exception'] for e in done)}, malformed {sum(fn[e]['malformed'] for e in done)}, "
      f"test timeouts {sum(fn[e]['test_timeouts'] for e in done)}")
