#!/usr/bin/env python3
"""Warm qwen3.8-flash-next's expert pool into page cache before scoring it.

Cold, this model runs at 0.55 tok/s prompt / 0.66 tok/s generation because a
10-of-512 expert draw never lets a cold cache converge. A benchmark harness with
a 900 s request timeout cannot survive that on a 3k-token prompt. Several varied
passes pull a broad slice of the 44 GB expert pool into cache first; the run is
only meaningful once the rate stops climbing.
"""
import json, time, urllib.request, sys

MODEL = "qwen3.8-flash-next:ud-iq3_xxs"
API = "http://127.0.0.1:11434/api/chat"

# Every prompt must be DISTINCT. Repeating one re-routes to the same 10-of-512
# experts, which are already resident, and measures best-case expert reuse
# rather than steady-state throughput -- the trap that produced a bogus
# "12.53 tok/s warm" figure on 2026-09-19.
PROMPTS = [
    "Explain in three sentences why merge sort is O(n log n).",
    "Write a Python function that validates an IPv4 address. Code only.",
    "Summarise the causes of the 1929 stock market crash in four bullet points.",
    "A patient presents with hyponatremia. List three differential diagnoses.",
    "Translate to formal English: 'gotta bounce, catch ya later'.",
    "What is the derivative of x^3 * ln(x)? Show the steps.",
    "Describe how a three-phase induction motor produces torque.",
    "Write a SQL query returning the second-highest salary per department.",
    "What distinguishes a tort from a breach of contract? Two sentences.",
    "Explain the Maillard reaction and why it needs low moisture.",
    "Give the electron configuration of iron(III) and explain the order.",
    "Write a bash one-liner that finds files over 100MB modified this week.",
    "Summarise Rawls' veil of ignorance in plain language.",
    "Why does a fibre-optic cable have a cladding layer? Be specific.",
    "Write a regex matching ISO-8601 datetimes with an optional timezone.",
    "Explain how CRISPR-Cas9 achieves sequence specificity.",
    "What is the difference between monetary and fiscal policy?",
    "Derive the time complexity of binary search on a sorted array.",
    "Explain why aircraft wings generate lift, without using Bernoulli alone.",
    "Write a Python dataclass modelling a library loan with validation.",
    "What were the main provisions of the Treaty of Westphalia?",
    "Explain thermal runaway in lithium-ion cells and how BMS prevents it.",
    "Give three reasons a database index can make a query slower.",
    "Explain the difference between Type I and Type II statistical errors.",
]


def cache_gb():
    for line in open("/proc/meminfo"):
        if line.startswith("Cached:"):
            return int(line.split()[1]) / 1048576
    return 0.0


def one(prompt, npred):
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
               "stream": False, "think": False,
               "options": {"num_ctx": 8192, "num_predict": npred, "temperature": 0, "seed": 42}}
    req = urllib.request.Request(API, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    t0 = time.time()
    r = json.load(urllib.request.urlopen(req, timeout=7200))
    wall = time.time() - t0
    ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1) / 1e9
    pc, pd = r.get("prompt_eval_count", 0), r.get("prompt_eval_duration", 1) / 1e9
    return wall, pc, (pc / pd if pd else 0), ec, (ec / ed if ed else 0)


npred = int(sys.argv[1]) if len(sys.argv) > 1 else 200
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0   # skip prompts already used
print(f"{'pass':>4} {'cache':>7} {'wall':>8} {'prompt tok/s':>13} {'gen tok/s':>10}", flush=True)
for i, p in enumerate(PROMPTS[start:], start + 1):
    wall, pc, pps, ec, gps = one(p, npred)
    print(f"{i:>4} {cache_gb():6.1f}G {wall:7.1f}s {pps:13.2f} {gps:10.2f}", flush=True)
print("\nwarm when the rate stops climbing; scoring is only valid from there on.")
