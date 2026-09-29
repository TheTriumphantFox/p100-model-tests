#!/usr/bin/env python3
"""Verify a shim/model actually reasons before committing hours to a benchmark run.

Why this exists: both accuracy harnesses hard-code `"think": False`, so every model in
round 2 was scored with its chain of thought switched off. `ollama_shim.py --force-think`
overrides that, but "the flag is set" and "the model is reasoning" are different claims,
and the difference is only visible in the token count. A thinking-on run that quietly did
not think looks exactly like a normal run and takes just as long -- 14 batches, plausible
accuracy, nothing in the log. Probe first; it costs one request.

It sends the MMLU-Pro batch shape (several questions, "Do not explain", answer-per-line)
with `think: False` in the body -- exactly what the harness sends -- so a --force-think
shim is exercised on its real input. The two questions have known answers (C and E), and
thinking-off has been observed to get Q1 wrong where thinking-on gets it right, so the
probe shows the mode change in behaviour and not just in token count.

What to look for:
  * eval_count -- thinking-off answers a 2-question batch in ~8 tokens. Anything under
    ~30 means no reasoning happened, whatever the flag says.
  * content    -- must hold ONLY the answer lines. llama.cpp splits a reasoning model's
    analysis into `reasoning_content` and leaves `content` clean; if the CoT leaks into
    `content`, MMLU's line-regex will match stray "1. A" text inside the reasoning and
    the scores are garbage.

    scripts/think_probe.py                      # A/B both shims, the usual case
    scripts/think_probe.py --port 11501 --model ornith-1.5-35b-a3b:q4_k_m
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request

# Known answers: 1=C (v=sqrt(2gh)=9.9 m/s), 2=E (24/8 = 3 half-lives -> 1/8).
PROMPT = """Answer these 2 independent MMLU-Pro multiple-choice questions in the category 'physics'.
Return only one answer per line in exactly this format: `1: A`. Do not explain.
The only valid answer letters are A, B, C, D, E, F, G, H, I, J.

Question 1:
A 2.0 kg block slides down a frictionless incline of height 5.0 m. Its speed at the bottom is closest to:
Options: A) 3.1 m/s  B) 7.0 m/s  C) 9.9 m/s  D) 14.0 m/s  E) 4.5 m/s  F) 10.0 m/s  G) 22.0 m/s  H) 5.0 m/s  I) 6.3 m/s  J) 11.2 m/s

Question 2:
The half-life of a sample is 8.0 days. The fraction remaining after 24 days is:
Options: A) 1/2  B) 1/3  C) 1/4  D) 1/6  E) 1/8  F) 1/9  G) 1/16  H) 1/12  I) 1/24  J) 1/32

Return exactly 2 numbered answer lines and nothing else."""
EXPECTED = {1: "C", 2: "E"}


def probe(port: int, model: str, num_predict: int, timeout: float) -> dict | None:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": False,
        "think": False,  # exactly what the harnesses send; --force-think must override it
        "options": {"temperature": 0, "num_predict": num_predict, "num_ctx": 8192, "seed": 42},
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/chat",
        json.dumps(body).encode(), {"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.load(r)
    except Exception as exc:
        print(f"  port {port}: FAILED {exc!r}")
        return None
    d["_wall"] = time.time() - t0
    return d


def report(port: int, d: dict) -> None:
    content = (d.get("message") or {}).get("content", "") or ""
    n = int(d.get("eval_count") or 0)
    lines = [l.strip() for l in content.strip().splitlines() if l.strip()]
    got = {}
    for l in lines:
        if ":" in l:
            a, _, b = l.partition(":")
            if a.strip().isdigit() and b.strip()[:1].upper() in "ABCDEFGHIJ":
                got[int(a.strip())] = b.strip()[:1].upper()
    score = sum(1 for k, v in EXPECTED.items() if got.get(k) == v)
    verdict = "REASONED" if n >= 30 else "did NOT reason"
    print(f"  port {port}: eval_count={n:<6} {verdict:<15} "
          f"answers={got or '(none parsed)'} correct={score}/2 wall={d['_wall']:.1f}s")
    # The CoT must not be in `content` or MMLU's per-line regex will match inside it.
    if len(lines) > 4:
        print(f"    !! content has {len(lines)} lines -- reasoning may be leaking into the "
              f"answer text, which corrupts MMLU parsing. First line: {lines[0][:70]!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="ornith-1.5-35b-a3b:q4_k_m",
                    help="ollama tag as the shim advertises it (see /api/tags)")
    ap.add_argument("--port", type=int, action="append",
                    help="shim port; repeatable. Default: 11500 and 11501 (A/B)")
    ap.add_argument("--num-predict", type=int, default=4096)
    ap.add_argument("--timeout", type=float, default=1800)
    a = ap.parse_args()
    ports = a.port or [11500, 11501]

    print(f"model: {a.model}   (expected answers 1:C 2:E)")
    print("thinking-off answers this in ~8 tokens; thinking-on in 80+ and is likelier to")
    print("get Q1 right. The model loads on the first call, so that one is slow.\n")
    ok = True
    for p in ports:
        d = probe(p, a.model, a.num_predict, a.timeout)
        if d is None:
            ok = False
            continue
        report(p, d)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
