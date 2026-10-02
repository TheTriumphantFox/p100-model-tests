#!/usr/bin/env python3
"""Per-run decode/prefill speed and correctness from serve/*.json."""
import json, sys, glob
for f in sorted(sys.argv[1:] or glob.glob("serve/*.json")):
    d = json.load(open(f)); rs = d["results"]
    gen = sum(r.get("completion_tokens") or 0 for r in rs); gms = sum(r.get("predicted_ms") or 0 for r in rs)
    pp = sum(r.get("prompt_tokens") or 0 for r in rs); pms = sum(r.get("prompt_ms") or 0 for r in rs)
    ok = sum(r.get("verdict") == "correct" for r in rs)
    print(f"{f.split('/')[-1][:-5]:34} correct {ok}/{len(rs)}  decode {gen/gms*1000 if gms else 0:6.1f} t/s  "
          f"prefill {pp/pms*1000 if pms else 0:6.1f} t/s  wall {sum(r['wall_s'] for r in rs):6.0f}s")
    for r in rs:
        print(f"   {r['id']:24} {r['wall_s']:6.1f}s tok={r.get('completion_tokens')!s:>5} "
              f"{(r.get('completion_tokens') or 0)/((r.get('predicted_ms') or 1)/1000):5.1f}t/s {r['outcome']} {r.get('verdict')}")
