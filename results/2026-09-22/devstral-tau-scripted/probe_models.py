#!/usr/bin/env python3
"""Pre-flight: does each model emit tool calls llama.cpp can actually parse?

Run before committing hours to a multi-model tau-bench run. A model whose calls
come back as prose in `content` instead of a structured `tool_calls` array will
score 0% for reasons that have nothing to do with its reasoning.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request

URL = "http://127.0.0.1:8081/v1/chat/completions"

MODELS = [
    "devstral-patched_q8_0",
    "gpt-oss-20b_q8_0",
    "g9v3-39a5b_q4_k_m",
    "qwen3.6-27b-abliterated_q5_k_m",
    "qwen3.8-27b-uncensored-hauhaucs_q6_k_p",
]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up the current status of a customer order.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": "Issue a refund for an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "amount_usd": {"type": "number"},
                },
                "required": ["order_id", "amount_usd"],
            },
        },
    },
]


def call(model, messages, timeout=900):
    body = json.dumps(
        {"model": model, "messages": messages, "tools": TOOLS, "temperature": 0.0}
    ).encode()
    req = urllib.request.Request(
        URL, data=body, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r), time.time() - t0


def probe(model):
    out = {"model": model}
    # 1. simple call
    try:
        r, dt = call(model, [{"role": "user", "content": "Status of order #W12345?"}])
        m = r["choices"][0]["message"]
        tc = m.get("tool_calls")
        out["simple_parsed"] = bool(tc)
        out["simple_name"] = tc[0]["function"]["name"] if tc else None
        out["simple_s"] = round(dt, 1)
        out["simple_content"] = (m.get("content") or "")[:160]
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
        return out

    # 2. irrelevance
    try:
        r, dt = call(model, [{"role": "user", "content": "What's the capital of France?"}])
        m = r["choices"][0]["message"]
        out["irrelevance_declined"] = not m.get("tool_calls")
        out["irrelevance_s"] = round(dt, 1)
    except Exception as e:
        out["irrelevance_declined"] = f"ERR {e}"

    # 3. multi-turn chain off a tool result
    try:
        msgs = [
            {"role": "user", "content": "Refund order #W99911 for $42.50."},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {
                            "name": "get_order_status",
                            "arguments": '{"order_id": "#W99911"}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "c1",
                "content": '{"order_id":"#W99911","status":"delivered",'
                '"total_usd":42.50,"refundable":true}',
            },
        ]
        r, dt = call(model, msgs)
        m = r["choices"][0]["message"]
        tc = m.get("tool_calls")
        out["chain_parsed"] = bool(tc)
        out["chain_name"] = tc[0]["function"]["name"] if tc else None
        out["chain_s"] = round(dt, 1)
    except Exception as e:
        out["chain_parsed"] = f"ERR {e}"
    return out


def main():
    results = []
    for model in MODELS:
        print(f"\n=== {model} ===", flush=True)
        r = probe(model)
        results.append(r)
        if "error" in r:
            print(f"  FAILED: {r['error']}", flush=True)
            continue
        verdict = (
            "USABLE"
            if r.get("simple_parsed") and r.get("chain_parsed") is True
            else "NOT USABLE"
        )
        print(
            f"  simple      : parsed={r['simple_parsed']} "
            f"name={r['simple_name']} ({r['simple_s']}s)",
            flush=True,
        )
        if not r["simple_parsed"]:
            print(f"    content -> {r['simple_content']!r}", flush=True)
        print(f"  irrelevance : declined={r.get('irrelevance_declined')}", flush=True)
        print(
            f"  chain       : parsed={r.get('chain_parsed')} "
            f"name={r.get('chain_name')} ({r.get('chain_s')}s)",
            flush=True,
        )
        print(f"  --> {verdict}", flush=True)

    out = "/home/hm/Projects/Tests/2026-09-22/devstral-tau-scripted/probe_models.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    sys.exit(main())
