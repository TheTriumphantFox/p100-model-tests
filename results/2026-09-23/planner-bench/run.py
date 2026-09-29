#!/usr/bin/env python3
"""Run the planner tasks against one model on a llama.cpp router. Resumable.

No time limit and, by default, no output-token limit. Each request runs until
the model stops or the context window is full; the 120 s and 240 s section 3
deadlines are applied afterwards, in summarise.py, to the measured wall time.
(The first overnight run used a 16384-token cap. It cut off gpt-oss, whose
reasoning tokens count against it, so it was removed; capped results are
re-run by rerun_capped.sh.)

Sampling follows R57: temperature 0, top_k 1, fixed seed, grammar-constrained
output. Prompt caching is off, so every request pays full prefill as a cold
AIOS request would.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import bench

HERE = Path(__file__).resolve().parent


def post(url: str, body: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=None) as r:  # deliberately unbounded
        return json.loads(r.read())


class GrammarRejected(Exception):
    """The server refused a pinned-checks grammar. That arm has no fallback."""


def request_body(model: str, task: dict, max_tokens: int, extra: dict, constrained: bool,
                 pin_checks: bool = False) -> dict:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": bench.SYSTEM_PROMPT},
            {"role": "user", "content": bench.user_message(task)},
        ],
        "temperature": 0,
        "top_k": 1,
        "seed": 42,
        "cache_prompt": False,
    }
    if max_tokens:  # 0 = omit: generate until the model stops or the context is full
        body["max_tokens"] = max_tokens
    if constrained:
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "aios_plan", "strict": True,
                            "schema": bench.response_schema(task, pin_checks=pin_checks)},
        }
    body.update(extra)
    return body


def run_one(url: str, model: str, task: dict, max_tokens: int, extra: dict, pin_checks: bool = False) -> dict:
    rec = {"id": task["id"], "family": task["family"], "target_bytes": task["target_bytes"],
           "constrained": True, "http_error": None, "max_tokens": max_tokens or None,
           "pinned_checks": pin_checks}
    for constrained in (True, False):
        rec["constrained"] = constrained
        t0 = time.monotonic()
        try:
            resp = post(url, request_body(model, task, max_tokens, extra, constrained, pin_checks))
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:600]
            rec["http_error"] = f"{e.code}: {msg}"
            rec["wall_s"] = round(time.monotonic() - t0, 2)
            if pin_checks and constrained and "context" not in msg.lower() and "exceed" not in msg.lower():
                raise GrammarRejected(rec["http_error"])
            # A server that refuses the grammar gets one unconstrained attempt,
            # flagged, so the run still yields data. Context overflow is not a
            # grammar problem and is recorded as it is.
            if constrained and "context" not in msg.lower() and "exceed" not in msg.lower():
                continue
            rec.update({"raw": None, "finish_reason": None})
            break
        rec["wall_s"] = round(time.monotonic() - t0, 2)
        msg = resp["choices"][0]["message"]
        timings = resp.get("timings") or {}
        usage = resp.get("usage") or {}
        rec.update({
            "raw": msg.get("content"),
            "reasoning_chars": len(msg.get("reasoning_content") or ""),
            "finish_reason": resp["choices"][0].get("finish_reason"),
            "prompt_tokens": timings.get("prompt_n", usage.get("prompt_tokens")),
            "completion_tokens": timings.get("predicted_n", usage.get("completion_tokens")),
            "prompt_ms": timings.get("prompt_ms"),
            "predicted_ms": timings.get("predicted_ms"),
        })
        break
    rec.update(bench.score(rec.get("raw"), task))
    return rec


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--url", default="http://127.0.0.1:8081/v1/chat/completions")
    p.add_argument("--model", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--extra-body", default="{}", help="JSON merged into every request")
    p.add_argument("--max-tokens", type=int, default=0, help="0 (default) = no limit")
    p.add_argument("--only", nargs="*", help="task ids (for smoke tests)")
    p.add_argument("--pin-checks", action="store_true",
                   help="fix the check sequence in the grammar (proposed spec variant)")
    args = p.parse_args()

    tasks = json.load(open(HERE / "tasks.json"))["tasks"]
    if args.only:
        tasks = [t for t in tasks if t["id"] in set(args.only)]
    out = Path(args.out)
    doc = json.load(open(out)) if out.exists() else {
        "config": {"url": args.url, "model": args.model, "extra_body": json.loads(args.extra_body),
                   "max_tokens": args.max_tokens, "pin_checks": args.pin_checks, "temperature": 0, "top_k": 1, "seed": 42,
                   "cache_prompt": False, "started": dt.datetime.now().isoformat(timespec="seconds")},
        "results": [],
    }
    done = {r["id"] for r in doc["results"]}
    extra = json.loads(args.extra_body)

    for t in tasks:
        if t["id"] in done:
            continue
        try:
            rec = run_one(args.url, args.model, t, args.max_tokens, extra, args.pin_checks)
        except GrammarRejected as e:
            print(f"ABORT {t['id']}: server rejected the pinned-checks grammar: {e}", flush=True)
            return 3
        except (urllib.error.URLError, ConnectionError, OSError) as e:
            # The router is gone. Record nothing for this task so a resume retries it.
            print(f"ABORT {t['id']}: router unreachable ({e})", flush=True)
            return 2
        doc["results"].append(rec)
        tmp = out.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
        os.replace(tmp, out)
        tok = rec.get("completion_tokens")
        print(f"{t['id']:28} {rec['wall_s']:7.1f}s  tok={tok!s:>5}  {rec['outcome']:17} "
              f"{rec['reason'] or rec['verdict'] or ''}"
              f"{'  INJECTED' if rec['injection_followed'] else ''}"
              f"{'  UNCONSTRAINED' if not rec['constrained'] else ''}", flush=True)
    doc["config"]["finished"] = dt.datetime.now().isoformat(timespec="seconds")
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
