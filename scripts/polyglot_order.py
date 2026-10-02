#!/usr/bin/env python3
"""Write a fixed, language-stratified order for all 225 Aider Polyglot exercises.

Why a fixed order: aider's benchmark.py shuffles with an unseeded RNG, so two runs never
see the same subset. A time-capped run is only comparable across models if every model
works through the SAME prefix of the SAME list, and a later full run can then resume from
where the capped one stopped instead of starting again.

Why stratified: each language list is shuffled with a fixed seed, then the lists are
interleaved by largest remainder -- at every step the next exercise comes from whichever
language is furthest behind its share of the full 225. Any prefix of the order therefore
holds the languages in close to their full-suite proportions (cpp 26, go 39, java 47,
javascript 49, python 34, rust 30), so a 60-exercise prefix is a miniature of the suite,
not 60 random draws that happen to skip Rust.

    polyglot_order.py <polyglot-benchmark dir> <out file> [seed]
"""
import random
import sys
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20261001

pools = {}
for lang_dir in sorted(p for p in root.iterdir() if (p / "exercises" / "practice").is_dir()):
    names = sorted(d.name for d in (lang_dir / "exercises" / "practice").iterdir() if d.is_dir())
    random.Random(f"{seed}-{lang_dir.name}").shuffle(names)
    pools[lang_dir.name] = names

total = sum(len(v) for v in pools.values())
taken = {lang: 0 for lang in pools}
order = []
for step in range(1, total + 1):
    # Deficit = how far each language is behind its proportional share at this step.
    lang = max(
        (lang for lang in pools if taken[lang] < len(pools[lang])),
        key=lambda lang: (step * len(pools[lang]) / total - taken[lang], lang),
    )
    order.append(f"{lang}/exercises/practice/{pools[lang][taken[lang]]}")
    taken[lang] += 1

out.write_text("\n".join(order) + "\n")
print(f"{len(order)} exercises -> {out} (seed {seed})")
for n in (30, 60, 90):
    head = [o.split("/")[0] for o in order[:n]]
    print(f"  first {n}: " + ", ".join(f"{lang} {head.count(lang)}" for lang in pools))
