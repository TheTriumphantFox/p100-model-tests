"""Compare the 10-02 thinking-on batches with the 10-04 anti-loop reruns (legs A, B)."""
import json, re, sys
from pathlib import Path
OLD = Path.home() / "Projects/Tests/2026-10-02/flash-next-full/mmlu-flashnext-iq2-pc5-think12288"
NEW = Path(__file__).parent
CATS = ["economics", "engineering", "history", "law"]

def batches(d):
    j = json.load(open(d / "results.json"))
    res = {(r["category"], r["question_id"]): r for r in j["results"]}
    return {b["category"]: b for b in j["batches"]}, res

def loopiness(path):
    """Fraction of the text taken by repeated 12-word shingles: a crude loop score."""
    try:
        t = Path(path).read_text(errors="ignore")
    except Exception:
        return None, None
    w = t.split()
    sh = [" ".join(w[i:i+12]) for i in range(0, max(0, len(w)-12))]
    rep = len(sh) - len(set(sh))
    hedges = len(re.findall(r"\b(?:maybe|but maybe|hmm|let's think|let's examine|wait)\b", t, re.I))
    return (rep / len(sh) if sh else 0.0), hedges

legs = {"10-02 (no preset)": OLD}
for leg in ("A", "B"):
    if (NEW / f"mmlu-{leg}" / "results.json").exists():
        legs[f"10-04 {leg}"] = NEW / f"mmlu-{leg}"
data = {k: batches(v) for k, v in legs.items()}
print("| category | " + " | ".join(legs) + " |")
print("|---|" + "---:|" * len(legs))
for c in CATS:
    row = []
    for k in legs:
        b = data[k][0].get(c)
        if not b:
            row.append("—"); continue
        rf = b.get("raw_output_file") or ""
        rp = Path(rf) if Path(rf).is_absolute() else legs[k] / rf
        lp, hed = loopiness(rp)
        cap = " **CAP**" if int(b.get("eval_count") or 0) >= 12280 else ""
        row.append(f"{b['correct']}/{b['total']}, {b.get('eval_count')} tok{cap}, "
                   f"{(b.get('wall_seconds') or 0)/60:.1f} min, rep {lp:.0%}, hedges {hed}" if lp is not None
                   else f"{b['correct']}/{b['total']}, {b.get('eval_count')} tok{cap}")
    print(f"| {c} | " + " | ".join(row) + " |")
tot = {k: sum(data[k][0][c]["correct"] for c in CATS if c in data[k][0]) for k in legs}
print("\ntotal correct (20 Q):", tot)
