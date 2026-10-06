#!/usr/bin/env python3
"""verify.py NAME BUILD CTX -- llama-server args...

Starts llama-server on :8090 with the exact config pi will use, then:
  1. fills the context to CTX-1024 tokens and generates 512 (the worst case pi
     can produce before compaction), recording peak VRAM per card;
  2. sends CTX+256 tokens and checks the server refuses with the overflow error
     pi recognizes, rather than truncating silently.
Appends one JSON line to results.jsonl.
"""
import json, os, signal, subprocess, sys, threading, time, urllib.request

name, build, ctx = sys.argv[1], sys.argv[2], int(sys.argv[3])
args = sys.argv[sys.argv.index("--") + 1:]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f"{here}/raw", exist_ok=True)
log = open(f"{here}/raw/verify-{name}.log", "w")
env = dict(os.environ, LD_LIBRARY_PATH=f"{build}/lib")
srv = subprocess.Popen([f"{build}/bin/llama-server", "--host", "127.0.0.1", "--port", "8090",
                        "-c", str(ctx), *args], stdout=log, stderr=subprocess.STDOUT, env=env)
URL = "http://127.0.0.1:8090"


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


res = {"name": name, "ctx": ctx, "args": " ".join(args)}
t0 = time.time()
try:
    for _ in range(600):
        if srv.poll() is not None:
            raise RuntimeError(f"server exited rc={srv.returncode}")
        try:
            urllib.request.urlopen(URL + "/health", timeout=2)
            break
        except Exception:
            time.sleep(1)
    res["load_s"] = round(time.time() - t0, 1)
    threading.Thread(target=poll, daemon=True).start()

    # Varied filler so prompt caching / repetition doesn't distort anything.
    words = ("the planner reads a config file then rewrites every section while keeping "
             "keys stable and comments intact before the reviewer checks hashes ").split()
    text = " ".join(f"{w}{i % 97}" for i, w in enumerate(words * 4000))
    _, tok = post("/tokenize", {"content": text})
    toks = tok["tokens"]
    while len(toks) < ctx + 256:
        toks = toks + toks
    fill = int(os.environ.get("FILL", ctx - 1024))  # FILL: for models too slow to fill fully
    t1 = time.time()
    code, r = post("/completion", {"prompt": toks[:fill], "n_predict": 512, "temperature": 0,
                                   "cache_prompt": False, "ignore_eos": True})
    res["fill"] = fill
    res["fill_http"] = code
    res["fill_wall_s"] = round(time.time() - t1, 1)
    if code == 200:
        t = r.get("timings", {})
        res.update(prompt_n=t.get("prompt_n"), predicted_n=t.get("predicted_n"),
                   prefill_tps=round(t.get("prompt_per_second", 0), 1),
                   decode_tps=round(t.get("predicted_per_second", 0), 1),
                   stop_type=r.get("stop_type"), truncated=r.get("truncated"))
    else:
        res["fill_error"] = str(r)[:300]
    code, r = post("/completion", {"prompt": toks[:ctx + 256], "n_predict": 8, "cache_prompt": False})
    res["over_http"] = code
    res["over_msg"] = (r.get("error") or {}).get("message", str(r))[:160] if code != 200 else "ACCEPTED (silent truncation?)"
except Exception as e:
    res["error"] = repr(e)[:300]
finally:
    stop.set()
    res["peak_mib"] = peak
    srv.send_signal(signal.SIGINT)
    try:
        srv.wait(30)
    except subprocess.TimeoutExpired:
        srv.kill()
    log.close()
    res["server_errors"] = sum(1 for l in open(f"{here}/raw/verify-{name}.log", errors="ignore")
                               if "out of memory" in l or "failed to allocate" in l)
    print(json.dumps(res), flush=True)
    with open(f"{here}/results.jsonl", "a") as f:
        f.write(json.dumps(res) + "\n")
    # let VRAM drain before the next model
    for _ in range(30):
        used = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                              capture_output=True, text=True).stdout.split()
        if max(map(int, used)) < 500:
            break
        time.sleep(1)
