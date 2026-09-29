#!/usr/bin/env python3
"""Measure generation speed of a running llama-server with and without speculative decoding.

Six DISTINCT realistic prompts per config (code, refactor, prose, reasoning) - not the
"write 1..300" filler kv_ab.py uses, because that output is almost perfectly predictable
and would flatter a drafter. Prompts are sent with cache_prompt=false, and each config
runs the same six, in the same order, at temperature 0.

    spec_ab.py <label> [port] [n_predict]

Writes <label>.json to $SPEC_AB_OUT (default: a dated run folder).
"""
import json, os, sys, urllib.request
from datetime import date

label = sys.argv[1]
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8082
npred = int(sys.argv[3]) if len(sys.argv) > 3 else 200
URL = f"http://127.0.0.1:{port}/completion"

PROMPTS = [
    "Write a Python function `merge_intervals(intervals)` that merges overlapping closed "
    "intervals and returns them sorted. Include a docstring and handle the empty case.\n\n",
    "Refactor this into idiomatic Python and explain each change:\n\n"
    "def f(l):\n  r=[]\n  for i in range(len(l)):\n    if l[i]%2==0: r.append(l[i]*l[i])\n  return r\n\n",
    "Write a bash function that finds every file over 100 MB under a directory, newest "
    "first, and prints size in GiB with two decimals. Explain the sort key.\n\n",
    "A CUDA kernel reads 24 GB of weights per token and the card sustains 300 GB/s. "
    "Derive the ceiling on tokens per second, then explain which term changes if the "
    "model is a sparse mixture of experts.\n\n",
    "Explain, in one paragraph each, the difference between a write-through and a "
    "write-back cache, and which one a battery-backed RAID controller prefers.\n\n",
    "Write a SQL query against tables orders(id, customer_id, placed_at, total_cents) and "
    "customers(id, name, country) that returns the top 5 countries by revenue in the last "
    "90 days, with order counts. Explain the join and the date filter.\n\n",
]

def post(prompt):
    req = urllib.request.Request(URL, data=json.dumps({
        "prompt": prompt, "n_predict": npred, "temperature": 0, "cache_prompt": False,
    }).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        return json.loads(r.read())

rows, res = [], {"label": label, "n_predict": npred, "runs": []}
for i, p in enumerate(PROMPTS):
    d = post(p)
    t = d["timings"]
    row = {
        "i": i,
        "gen_tps": t.get("predicted_per_second", 0.0),
        "predicted_n": t.get("predicted_n", 0),
        "prompt_n": t.get("prompt_n", 0),
        "prompt_tps": t.get("prompt_per_second", 0.0),
        # present only when a speculative path is active; names vary by build
        **{k: t[k] for k in t if "draft" in k or "accept" in k},
    }
    res["runs"].append(row)
    rows.append(row["gen_tps"])
    print(f"  prompt {i}: {row['gen_tps']:6.2f} tok/s  ({row['predicted_n']} tok"
          + (f", draft {row.get('draft_n','-')}/{row.get('draft_n_accepted','-')} accepted" if any('draft' in k for k in row) else "")
          + ")", flush=True)

res["mean_gen_tps"] = sum(rows) / len(rows)
res["min_gen_tps"], res["max_gen_tps"] = min(rows), max(rows)
print(f"  MEAN {res['mean_gen_tps']:6.2f} tok/s  (min {res['min_gen_tps']:.2f}, max {res['max_gen_tps']:.2f})")

out = os.environ.get("SPEC_AB_OUT") or f"/home/hm/Projects/Tests/{date.today()}/spec-decoding"
os.makedirs(out, exist_ok=True)
json.dump(res, open(f"{out}/{label}.json", "w"), indent=1)
