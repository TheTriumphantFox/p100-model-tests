#!/usr/bin/env python3
"""A/B `enable_thinking: false` on llama-server's OpenAI endpoint, over a tool call.

Companion to `think_probe.py`, which probes the SAME question down a different
path. That one goes through `ollama_shim.py` and the Ollama-shaped `"think":
False` body, because the HumanEval / MMLU-Pro / coding harnesses are written
against Ollama. This one talks straight to llama-server's
`/v1/chat/completions` using `chat_template_kwargs.enable_thinking`, which is
what a harness written against the OpenAI API has to send. The flags are not
interchangeable and neither probe tells you about the other's path.

Why it exists at all: the flag being *accepted* and the model actually not
reasoning are different claims, and a thinking-on run that quietly did not think
looks exactly like a normal run. Three signals are checked per request:

  * reasoning_content -- llama.cpp splits a reasoning model's analysis into this
    field. Populated means it reasoned. This is the clearest signal and the one
    `think_probe.py` cannot see, since the Ollama shim does not surface it.
  * completion_tokens -- should drop sharply with thinking off. On
    qwen3.6-27b-abliterated and qwen3.8-27b-uncensored both fell 95-98 -> 52.
  * the tool call itself -- must still be emitted, and still be correct. A flag
    that silences reasoning but breaks tool calling is not usable.

Used on 2026-09-22 to qualify both Qwen models before a 14-hour tau-bench run,
where thinking-on would have roughly tripled per-call latency. See
`2026-09-22/devstral-tau-scripted/REPORT.md`.

    scripts/think_probe_openai.py --model qwen3.6-27b-abliterated_q5_k_m
    scripts/think_probe_openai.py --url http://127.0.0.1:8080/v1/chat/completions \
        --model devstral-cuda        # a non-reasoning model: expect no change
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request

NOTHINK = {"chat_template_kwargs": {"enable_thinking": False}}

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

# A second-turn prompt: the agent already looked the order up, and the tool
# result is in hand. This is the shape that matters for an agent loop, and it
# exercises chaining off a `role: tool` message rather than a cold first call.
MSGS = [
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
        "content": '{"order_id":"#W99911","status":"delivered","total_usd":42.50,'
        '"refundable":true}',
    },
]


def call(url: str, model: str, extra: dict, timeout: int) -> dict:
    body = json.dumps(
        {
            "model": model,
            "messages": MSGS,
            "tools": TOOLS,
            "temperature": 0.0,
            **extra,
        }
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    m = d["choices"][0]["message"]
    reasoning = m.get("reasoning_content") or ""
    calls = m.get("tool_calls") or []
    return {
        "s": round(time.time() - t0, 1),
        "completion_tokens": d.get("usage", {}).get("completion_tokens"),
        "reasoning_len": len(reasoning),
        "tool_call": calls[0]["function"]["name"] if calls else None,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default="http://127.0.0.1:8081/v1/chat/completions")
    p.add_argument("--model", required=True, help="model id as the router reports it")
    p.add_argument("--timeout", type=int, default=900)
    args = p.parse_args()

    print(f"=== {args.model} ===", flush=True)
    seen = {}
    for label, extra in (("think ON (default)", {}), ("think OFF", NOTHINK)):
        try:
            r = call(args.url, args.model, extra, args.timeout)
        except Exception as e:
            print(f"  {label:20} ERROR {type(e).__name__}: {e}", flush=True)
            return 1
        seen[label] = r
        print(
            f"  {label:20} {r['s']:>6}s  completion_tok={r['completion_tokens']}"
            f"  reasoning={r['reasoning_len']}c  call={r['tool_call']}",
            flush=True,
        )

    on, off = seen["think ON (default)"], seen["think OFF"]
    if off["tool_call"] is None:
        print("\n  !! thinking-off broke tool calling -- do not use this flag here")
        return 1
    if on["reasoning_len"] == 0 and off["reasoning_len"] == 0:
        print("\n  no reasoning_content either way: not a reasoning model, or the")
        print("  template ignores enable_thinking. The flag is a no-op here.")
    elif off["reasoning_len"] == 0:
        print("\n  thinking-off ENGAGED: reasoning_content emptied"
              f" ({on['reasoning_len']}c -> 0)"
              f" and completion tokens {on['completion_tokens']}"
              f" -> {off['completion_tokens']}.")
    else:
        print("\n  !! flag accepted but the model STILL reasoned"
              f" ({off['reasoning_len']}c). Treat any 'thinking-off' run as void.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
