#!/usr/bin/env python3
"""Every paired comparison the data supports, run against the incumbent as reference.

Paired (McNemar, exact binomial on the discordant pairs) because every model answers the
SAME seeded questions. An independent-sample test discards that pairing, and on 70
questions it will call a real 15-point gap noise.

Pairs are only formed between runs with IDENTICAL item sets. random.Random(seed).sample is
not nested across k, so a 280-question run shares 9 of 70 items with a 70-question run at
the same seed; comparing them would silently score over the intersection.
"""
from __future__ import annotations

import json
import subprocess
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = HERE.parents[1]
SOURCES = [HERE, TESTS / "2026-09-19" / "candidates-round2", TESTS / "2026-09-19" / "candidates"]
REFERENCE = "qwen3.6-27b-abliterated:q5_k_m"


def load(d: Path):
    try:
        p = json.loads((d / "results.json").read_text())
    except Exception:
        return None
    res, sm = p.get("results") or [], p.get("model_summaries") or []
    meta = p.get("metadata") or {}
    if not res or not sm or not meta.get("finished"):
        return None
    if "question_id" in res[0]:
        items = {str(r["question_id"]): bool(r["correct"]) for r in res}
    elif "task_id" in res[0]:
        items = {str(r["task_id"]): bool(r["passed"]) for r in res}
    else:
        return None
    batches = p.get("batches") or []
    if batches and sum(int(b.get("eval_count") or 0) for b in batches) == 0:
        return None          # rig failure, not a result
    kind = "HumanEval" if "pass_at_1" in sm[0] else ("MMLU-ON" if "think" in d.name else "MMLU-off")
    cfg = meta.get("settings") or {}
    return dict(tag=sm[0].get("name") or res[0]["model"], kind=kind, items=items,
                np=cfg.get("num_predict") or 0, pc=cfg.get("per_category"), run=d.name)


def exact_two_sided(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def main() -> int:
    runs = []
    for src in SOURCES:
        if src.is_dir():
            for d in sorted(src.iterdir()):
                if d.is_dir() and (d.name.startswith("mmlu-") or d.name.startswith("humaneval-")):
                    r = load(d)
                    if r:
                        runs.append(r)
    # one run per (tag, kind): the largest budget that finished
    best: dict[tuple[str, str], dict] = {}
    for r in runs:
        k = (r["tag"], r["kind"])
        if k not in best or r["np"] > best[k]["np"]:
            best[k] = r

    for kind in ("MMLU-off", "MMLU-ON", "HumanEval"):
        ref = best.get((REFERENCE, kind))
        print(f"--- {kind}: everything vs {REFERENCE} ---")
        if not ref:
            print("  reference run missing\n"); continue
        out = []
        for (tag, k), r in best.items():
            if k != kind or tag == REFERENCE:
                continue
            if set(r["items"]) != set(ref["items"]):
                print(f"  {tag:<40} NOT PAIRABLE ({len(r['items'])} vs {len(ref['items'])} items, "
                      f"{len(set(r['items']) & set(ref['items']))} shared)")
                continue
            ids = sorted(ref["items"])
            b = sum(1 for q in ids if ref["items"][q] and not r["items"][q])
            c = sum(1 for q in ids if r["items"][q] and not ref["items"][q])
            ra = 100 * sum(ref["items"][q] for q in ids) / len(ids)
            rb = 100 * sum(r["items"][q] for q in ids) / len(ids)
            out.append((rb - ra, tag, rb, ra, b, c, exact_two_sided(b, c), len(ids)))
        for gap, tag, rb, ra, b, c, p, n in sorted(out):
            verdict = "SIGNIFICANT" if p < 0.05 else ("noise" if b + c >= 6 else "underpowered")
            print(f"  {tag:<40} {rb:6.2f} vs {ra:6.2f}  {gap:+6.2f}  "
                  f"discordant {b}/{c}  p={p:.4f}  {verdict}  n={n}")
        print()

    print("--- the three Qwen3.8 Q8_0-class files against each other ---")
    trio = ["qwen3.8-27b-unsloth:q8_0", "qwen3.8-27b-ggmlorg:q8_0", "qwen3.8-27b-uncensored-hauhaucs:q6_k_p"]
    for kind in ("MMLU-off", "HumanEval"):
        for i, a in enumerate(trio):
            for bb in trio[i + 1:]:
                ra, rb = best.get((a, kind)), best.get((bb, kind))
                if not ra or not rb or set(ra["items"]) != set(rb["items"]):
                    continue
                ids = sorted(ra["items"])
                x = sum(1 for q in ids if ra["items"][q] and not rb["items"][q])
                y = sum(1 for q in ids if rb["items"][q] and not ra["items"][q])
                pa = 100 * sum(ra["items"][q] for q in ids) / len(ids)
                pb = 100 * sum(rb["items"][q] for q in ids) / len(ids)
                p = exact_two_sided(x, y)
                print(f"  {kind:<10} {a.split(':')[0][-12:]:>12} vs {bb.split(':')[0][-12:]:<12} "
                      f"{pa:6.2f} vs {pb:6.2f}  discordant {x}/{y}  p={p:.4f}")
    print("\n'underpowered' = fewer than 6 discordant pairs, below which an exact test")
    print("cannot reach p<0.05 no matter which way they fall.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
