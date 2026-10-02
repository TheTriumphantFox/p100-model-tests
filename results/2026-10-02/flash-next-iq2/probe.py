#!/usr/bin/env python3
"""Steady-state speed of a sparse MoE bigger than VRAM, on a llama-server.

Every prompt is DISTINCT (see 2026-09-19/qwen3.8-flash-next: repeating a prompt
re-routes to experts already resident and gives a bogus warm figure). The first
--warm prompts warm the page cache; the rest are the measurement.

  probe.py <out.jsonl> [--url URL] [--warm 24] [--npred 128]
"""
import argparse, json, statistics, sys, time, urllib.request

import ast
# The 24 prompts used on 2026-09-19, read without running that script.
_src = ast.parse(open("/home/hm/Projects/Tests/2026-09-19/qwen3.8-flash-next/warmup.py").read())
P1 = next(ast.literal_eval(n.value) for n in _src.body
          if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PROMPTS")

P2 = [
    "Explain how a hash map handles collisions with open addressing.",
    "Write a Python generator that yields Fibonacci numbers below n.",
    "Summarise the main arguments for and against nuclear power in four bullets.",
    "What does a GFCI breaker detect, and why does it trip?",
    "Translate 'the meeting has been moved to Thursday' into Spanish and French.",
    "Integrate x * e^x dx and show the steps.",
    "Describe the role of the cambium in tree growth.",
    "Write a SQL query that finds customers with no orders in the last 90 days.",
    "What is the difference between a patent and a trademark? Two sentences.",
    "Explain why bread dough needs kneading.",
    "Why is the sky red at sunset? Explain the physics briefly.",
    "Write a bash loop that renames every .jpeg file to .jpg in a directory.",
    "Summarise Kant's categorical imperative in plain language.",
    "How does a heat pump move heat from a cold place to a warm one?",
    "Write a regex that matches US phone numbers in three common formats.",
    "Explain how mRNA vaccines instruct cells to make an antigen.",
    "What causes inflation, according to the quantity theory of money?",
    "Explain why quicksort is O(n^2) in the worst case.",
    "Why do ships float even though steel is denser than water?",
    "Write a TypeScript interface for a paginated API response.",
    "What were the main causes of the fall of the Western Roman Empire?",
    "Explain what a voltage drop calculation is used for in wiring.",
    "Give three ways to reduce lock contention in a multithreaded program.",
    "Explain the difference between precision and recall.",
]
PROMPTS = P1 + P2


def cache_gb():
    for line in open("/proc/meminfo"):
        if line.startswith("Cached:"):
            return int(line.split()[1]) / 1048576
    return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--url", default="http://127.0.0.1:8090/v1/chat/completions")
    ap.add_argument("--warm", type=int, default=24); ap.add_argument("--npred", type=int, default=128)
    a = ap.parse_args()
    rows = []
    with open(a.out, "w") as f:
        for i, p in enumerate(PROMPTS):
            body = {"model": "x", "messages": [{"role": "user", "content": p}], "max_tokens": a.npred,
                    "temperature": 0, "seed": 42, "cache_prompt": False,
                    "chat_template_kwargs": {"enable_thinking": False}}
            t0 = time.time()
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                a.url, json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=1800).read())
            t = r.get("timings", {})
            row = {"i": i, "phase": "warm" if i < a.warm else "measure", "wall_s": round(time.time() - t0, 1),
                   "gen_tps": t.get("predicted_per_second"), "pp_tps": t.get("prompt_per_second"),
                   "gen_n": t.get("predicted_n"), "pp_n": t.get("prompt_n"), "cache_gb": round(cache_gb(), 1),
                   "answer": r["choices"][0]["message"].get("content", "")[:200]}
            rows.append(row); f.write(json.dumps(row) + "\n"); f.flush()
            print(f"{i:3} {row['phase']:7} {row['cache_gb']:5.1f}G {row['wall_s']:6.1f}s  gen {row['gen_tps'] or 0:6.2f}  pp {row['pp_tps'] or 0:6.2f}", flush=True)
    m = [r for r in rows if r["phase"] == "measure"]
    if m:
        print(f"MEASURE n={len(m)}  gen median {statistics.median(r['gen_tps'] for r in m):.2f}  "
              f"pp median {statistics.median(r['pp_tps'] for r in m):.2f} tok/s")


if __name__ == "__main__":
    main()
