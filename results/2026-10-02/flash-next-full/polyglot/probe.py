#!/usr/bin/env python3
"""Preflight one model on the :8081 router: does it load, serve, and obey thinking-off?

Sends one short coding request with the exact extra body the polyglot run will use
(models.yml), and reports load time, decode rate, and whether any reasoning leaked.
Exit 0 only if the model produced content.

    probe.py <router-model-id> [max_tokens]
"""
import json
import sys
import time
import urllib.request

URL = "http://127.0.0.1:8081/v1/chat/completions"
model = sys.argv[1]
max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 300

body = {
    "model": model,
    "temperature": 0,
    "max_tokens": max_tokens,
    "messages": [{"role": "user", "content":
                  f"Write a Python function `run_length({model.split('_')[0].replace('-', '_').replace('.', '_')}: str) -> str` "
                  "that run-length encodes a string. Reply with only the code."}],
    "chat_template_kwargs": {"enable_thinking": False},
}
if model.startswith("gpt-oss"):
    body["reasoning_effort"] = "low"

t0 = time.time()
try:
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    resp = json.load(urllib.request.urlopen(req, timeout=900))
except Exception as exc:  # noqa: BLE001
    print(json.dumps({"model": model, "ok": False, "error": str(exc)[:300], "secs": round(time.time() - t0, 1)}))
    sys.exit(1)

msg = resp["choices"][0]["message"]
tim = resp.get("timings", {})
out = {
    "model": model,
    "ok": bool((msg.get("content") or "").strip()),
    "wall_s": round(time.time() - t0, 1),
    "completion_tokens": resp.get("usage", {}).get("completion_tokens"),
    "reasoning_chars": len(msg.get("reasoning_content") or ""),
    "content_chars": len(msg.get("content") or ""),
    "gen_tok_s": round(tim.get("predicted_per_second", 0), 2),
    "prefill_tok_s": round(tim.get("prompt_per_second", 0), 2),
    "finish": resp["choices"][0].get("finish_reason"),
}
print(json.dumps(out))
sys.exit(0 if out["ok"] else 1)
