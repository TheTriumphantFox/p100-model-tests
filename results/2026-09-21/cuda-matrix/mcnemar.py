#!/usr/bin/env python3
"""Paired McNemar test over two benchmark runs' per-question records.

Every model answers the SAME seeded questions, so the correct comparison is paired.
An independent-sample test (two proportions) throws away the pairing and is both less
powerful and, on a 70-question sample, capable of calling a real 15-point gap noise.

    mcnemar.py <dir-A> <dir-B> [label-A] [label-B]

Refuses to compare runs whose question sets differ -- which is the whole reason this
matrix re-runs its own baseline. `random.Random(seed).sample(rows, k)` is NOT nested
across k, so a --per-category 20 run shares only 9 of the 70 questions with a
--per-category 5 run at the same seed. Comparing them pairwise would silently score
over the 9-question intersection.

Exact two-sided binomial test on the discordant pairs (not the chi-square
approximation, which is unreliable below ~25 discordant pairs -- and these runs are
almost always below it).
"""
import json
import sys
from math import comb
from pathlib import Path


def load(d: Path) -> tuple[dict[int, bool], str]:
    payload = json.loads((d / "results.json").read_text())
    rows = payload["results"]
    names = {r["model"] for r in rows}
    if len(names) != 1:
        raise SystemExit(f"{d}: expected one model, found {sorted(names)}")
    # MMLU-Pro keys on question_id/correct; HumanEval on task_id/passed.
    if rows and "question_id" in rows[0]:
        by_q = {str(r["question_id"]): bool(r["correct"]) for r in rows}
    elif rows and "task_id" in rows[0]:
        by_q = {str(r["task_id"]): bool(r["passed"]) for r in rows}
    else:
        raise SystemExit(f"{d}: unrecognised result schema {sorted(rows[0]) if rows else '(empty)'}")
    if len(by_q) != len(rows):
        raise SystemExit(f"{d}: duplicate item ids ({len(rows)} rows, {len(by_q)} ids)")
    return by_q, names.pop()


def exact_two_sided(b: int, c: int) -> float:
    """P(|deviation| >= observed) under H0: a discordant pair is 50/50."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    da, db = Path(sys.argv[1]), Path(sys.argv[2])
    qa, na = load(da)
    qb, nb = load(db)
    la = sys.argv[3] if len(sys.argv) > 3 else na
    lb = sys.argv[4] if len(sys.argv) > 4 else nb

    if set(qa) != set(qb):
        shared = set(qa) & set(qb)
        raise SystemExit(
            f"REFUSED: different question sets -- {len(qa)} vs {len(qb)} questions, "
            f"{len(shared)} shared. These runs are not pairable; compare only runs made "
            f"with the same --per-category and --seed."
        )

    ids = sorted(qa)  # item ids: MMLU question_id or HumanEval task_id
    b = sum(1 for q in ids if qa[q] and not qb[q])      # A right, B wrong
    c = sum(1 for q in ids if qb[q] and not qa[q])      # B right, A wrong
    both = sum(1 for q in ids if qa[q] and qb[q])
    neither = len(ids) - both - b - c
    acc_a = 100 * sum(qa[q] for q in ids) / len(ids)
    acc_b = 100 * sum(qb[q] for q in ids) / len(ids)
    p = exact_two_sided(b, c)

    print(f"n = {len(ids)} paired questions")
    print(f"  {la:<44} {acc_a:6.2f}%")
    print(f"  {lb:<44} {acc_b:6.2f}%")
    print(f"  gap {acc_a - acc_b:+.2f} points")
    print(f"  both right {both}, both wrong {neither}, discordant {b}/{c} (A-only/B-only)")
    print(f"  exact McNemar p = {p:.4f}  ->  {'SIGNIFICANT' if p < 0.05 else 'not resolvable at this sample size'}")
    if b + c < 6:
        print(f"  NOTE: only {b + c} discordant pairs; this test cannot reach p<0.05 below 6.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
