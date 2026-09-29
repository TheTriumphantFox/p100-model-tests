#!/usr/bin/env python3
"""Load qwen3.8-flash-next, record placement, measure generation at a short prompt."""
import json, time, urllib.request, subprocess, threading, sys

MODEL = "qwen3.8-flash-next:ud-iq3_xxs"
API = "http://127.0.0.1:11434/api"

def post(path, payload, timeout=3600):
    req = urllib.request.Request(API + path, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def sample():
    g = subprocess.run(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],
                       capture_output=True, text=True).stdout.split()
    m = {}
    for line in open("/proc/meminfo"):
        k, v = line.split(":", 1)
        m[k] = int(v.strip().split()[0]) // 1024
    return {"gpu_mib": [int(x) for x in g if x.isdigit()],
            "ram_used_mib": m["MemTotal"] - m["MemAvailable"],
            "cached_mib": m["Cached"], "swap_used_mib": m["SwapTotal"] - m["SwapFree"]}

peak = {"gpu": [0,0], "ram": 0, "swap": 0}
stop = threading.Event()
def monitor():
    while not stop.wait(2):
        s = sample()
        for i, v in enumerate(s["gpu_mib"][:2]):
            peak["gpu"][i] = max(peak["gpu"][i], v)
        peak["ram"] = max(peak["ram"], s["ram_used_mib"])
        peak["swap"] = max(peak["swap"], s["swap_used_mib"])

print("baseline:", json.dumps(sample()))
t = threading.Thread(target=monitor, daemon=True); t.start()

prompt = sys.argv[1] if len(sys.argv) > 1 else "Write a Python function that returns the nth Fibonacci number. Code only."
npred = int(sys.argv[2]) if len(sys.argv) > 2 else 128

t0 = time.time()
try:
    r = post("/generate", {"model": MODEL, "prompt": prompt, "stream": False,
                           "options": {"num_predict": npred, "temperature": 0, "num_ctx": 4096}})
except Exception as e:
    stop.set(); print("FAILED after %.0fs: %r" % (time.time()-t0, e)); print("peak:", peak); raise
wall = time.time() - t0
stop.set(); time.sleep(0.1)

ld = r.get("load_duration",0)/1e9
pe, pd = r.get("prompt_eval_count",0), r.get("prompt_eval_duration",1)/1e9
ec, ed = r.get("eval_count",0), r.get("eval_duration",1)/1e9
print(f"\nwall            {wall:8.1f} s")
print(f"load            {ld:8.1f} s")
print(f"prompt eval     {pe:5d} tok in {pd:6.1f} s = {pe/pd if pd else 0:6.2f} tok/s")
print(f"generation      {ec:5d} tok in {ed:6.1f} s = {ec/ed if ed else 0:6.2f} tok/s")
print(f"\npeak gpu {peak['gpu']} MiB  ram {peak['ram']} MiB  swap {peak['swap']} MiB")
print("after:", json.dumps(sample()))
print("\n--- response ---")
print(r.get("response","")[:1200])
