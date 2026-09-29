#!/usr/bin/env python3
"""Measure devstral generation/prefill against a running llama-server on :8080.

Three points per config: generation at ~zero context, prefill on a fresh prompt,
and generation at depth (where the KV cache read dominates the per-token bytes).
Every prompt is freshly randomized - both ollama and llama-server prefix-cache,
so a repeated prompt gives nonsense prefill numbers.
"""
import json, os, random, string, sys, urllib.request
from datetime import date

URL = "http://127.0.0.1:8080/completion"
TAIL = "\n\nIgnore the noise above. Write the numbers 1 through 300, one per line.\n1\n2\n3"

def post(payload, timeout=1800):
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def rand_words(n):
    return ' '.join(''.join(random.choice(string.ascii_lowercase)
                            for _ in range(random.randint(3, 8))) for _ in range(n))

def run(nwords, npred):
    return post({"prompt": rand_words(nwords) + TAIL, "n_predict": npred,
                 "temperature": 0, "cache_prompt": False})["timings"]

label = sys.argv[1]
deep_words = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 4000
res = {"label": label}

deep_only = "--deep-only" in sys.argv
res["shallow_gen"] = [] if deep_only else [run(8, 200)["predicted_per_second"] for _ in range(3)]
if not deep_only: print("  gen @~0    : " + " ".join(f"{x:6.2f}" for x in res["shallow_gen"]) + " tok/s", flush=True)

pf = [] if deep_only else [run(900, 1) for _ in range(2)]
res["prefill"] = [(t["prompt_per_second"], t["prompt_n"]) for t in pf]
if not deep_only:
    print("  prefill    : " + " ".join(f"{a:7.1f}" for a, _ in res["prefill"]) +
          f" tok/s (n={res['prefill'][0][1]})", flush=True)

deep = [run(deep_words, 120) for _ in range(2)]
res["deep"] = [(t["predicted_per_second"], t["prompt_n"], t["prompt_per_second"]) for t in deep]
print("  gen @depth : " + " ".join(f"{a:6.2f}" for a, _, _ in res["deep"]) +
      f" tok/s (depth {res['deep'][0][1]} tok, prefill {res['deep'][0][2]:.1f})", flush=True)

out = os.environ.get("KV_AB_OUT") or f"/home/hm/Projects/Tests/{date.today()}/devstral-p100-bandwidth"
os.makedirs(out, exist_ok=True)
json.dump(res, open(f"{out}/{label}.json", "w"))
