#!/usr/bin/env python3
"""check.py MODEL CTX -- through the :8080 router, with the preset exactly as pi gets it:
  1. decode speed on 3 realistic prompts (512 tokens, temp 0);
  2. fill to CTX-1024 tokens + generate 512, recording peak VRAM per card.
Appends one JSON line to results.jsonl."""
import json, os, subprocess, sys, threading, time, urllib.request

model, ctx = sys.argv[1], int(sys.argv[2])
URL = "http://127.0.0.1:8080"
here = os.path.dirname(os.path.abspath(__file__))


def post(path, body, timeout=7200):
    req = urllib.request.Request(URL + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


peak = [0, 0]
stop = threading.Event()


def poll():
    while not stop.is_set():
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True).stdout.split()
        for i, v in enumerate(out[:2]):
            peak[i] = max(peak[i], int(v))
        time.sleep(0.5)


res = {"model": model, "ctx": ctx, "time": time.strftime("%F %T")}
t0 = time.time()
code, r = post("/completion", {"model": model, "prompt": "Hi", "n_predict": 1})
res["load_http"], res["load_s"] = code, round(time.time() - t0, 1)
if code != 200:
    res["error"] = r
    print(json.dumps(res)); open(f"{here}/results.jsonl", "a").write(json.dumps(res) + "\n"); sys.exit(1)
threading.Thread(target=poll, daemon=True).start()

prompts = [
    "Write a Python module that parses an INI file into nested dicts, with type coercion, "
    "comments preserved for round-tripping, and unit tests.",
    "Explain how TCP congestion control works, covering slow start, congestion avoidance, "
    "fast retransmit and BBR, with a worked example.",
    "Here is a bash script:\n#!/bin/bash\nfor f in *.log; do gzip $f; done\n"
    "Rewrite it to be robust (spaces in names, set -euo pipefail, dry-run flag, logging) and explain each change.",
]
dec = []
for p in prompts:
    code, r = post("/completion", {"model": model, "prompt": p, "n_predict": 512, "temperature": 0,
                                   "cache_prompt": False})
    t = r.get("timings", {})
    dec.append({"tps": round(t.get("predicted_per_second", 0), 1), "n": t.get("predicted_n"),
                "draft_n": t.get("draft_n"), "draft_acc": t.get("draft_n_accepted")})
res["decode"] = dec
res["decode_mean"] = round(sum(d["tps"] for d in dec) / len(dec), 1)

words = ("the planner reads a config file then rewrites every section while keeping "
         "keys stable and comments intact before the reviewer checks hashes ").split()
text = " ".join(f"{w}{i % 97}" for i, w in enumerate(words * 4000))
_, tok = post("/tokenize", {"model": model, "content": text})
toks = tok["tokens"]
while len(toks) < ctx:
    toks = toks + toks
fill = ctx - 1024
t1 = time.time()
code, r = post("/completion", {"model": model, "prompt": toks[:fill], "n_predict": 512, "temperature": 0,
                               "cache_prompt": False, "ignore_eos": True})
t = r.get("timings", {})
res.update(fill=fill, fill_http=code, fill_wall_s=round(time.time() - t1, 1),
           prompt_n=t.get("prompt_n"), predicted_n=t.get("predicted_n"),
           prefill_tps=round(t.get("prompt_per_second", 0), 1),
           deep_decode_tps=round(t.get("predicted_per_second", 0), 1))
if code != 200:
    res["error"] = r
stop.set(); time.sleep(0.6)
res["peak_mib"] = peak
res["free_mib"] = [16384 - p for p in peak]
print(json.dumps(res))
open(f"{here}/results.jsonl", "a").write(json.dumps(res) + "\n")
