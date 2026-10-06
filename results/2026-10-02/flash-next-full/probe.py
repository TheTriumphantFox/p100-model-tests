#!/usr/bin/env python3
"""One short generation through the shim; print its decode rate as JSON.

    probe.py <ollama-tag> <shim-port> [num_predict] [timeout]

Used to price a context size. The point is to catch a partial CPU offload, which
llama.cpp performs silently -- the model loads, answers correctly, and runs at a
fraction of the speed. Accuracy does not reveal it; only tok/s does.

Reports the decode rate from the server's own eval_count / eval_duration rather than
wall clock, so prompt processing and queueing are excluded.
"""
import json
import sys
import time
import urllib.error
import urllib.request

PROMPT = ("Write a short paragraph explaining what a B-tree is and why databases "
          "use one instead of a binary search tree.")


def main() -> int:
    tag, port = sys.argv[1], sys.argv[2]
    npred = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 900

    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/chat",
        data=json.dumps({
            "model": tag,
            "messages": [{"role": "user", "content": PROMPT}],
            "stream": False,
            "options": {"num_predict": npred, "temperature": 0},
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            body = json.load(fh)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}",
                          "wall_s": round(time.monotonic() - t0, 1)}))
        return 1
    wall = time.monotonic() - t0
    n = body.get("eval_count") or 0
    ns = body.get("eval_duration") or 0
    print(json.dumps({
        "ok": n > 0,
        "eval_count": n,
        "tok_per_s": round(n / (ns / 1e9), 2) if n and ns else None,
        "prompt_eval_count": body.get("prompt_eval_count"),
        "wall_s": round(wall, 1),
    }))
    return 0 if n > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
