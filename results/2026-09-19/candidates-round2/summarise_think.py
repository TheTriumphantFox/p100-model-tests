#!/usr/bin/env python3
"""Summarise the thinking-ON MMLU-Pro runs against their thinking-OFF counterparts.

Scoring rule is the harness's own: an unparsed answer counts as incorrect. With thinking
enabled a batch can spend its whole num_predict budget reasoning and emit no answer line,
so a thinking-on score is a FLOOR wherever a batch hit the cap. Both numbers are printed:
`scored` (the harness's, directly comparable in rule to the thinking-off column) and
`answered` (accuracy over questions that produced a parseable answer).
"""
import json, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
NP = 12288
MODELS = [("qwen36-rerun", "qwen3.6-27b-abliterated:q5_k_m  (incumbent)"),
          ("qwen38-27b", "qwen3.8-27b-stock:q4_k_m  (shelf)"),
          ("ornith", "ornith-1.5-35b-a3b:q4_k_m"),
          ("nemotron", "nemotron-cascade-2-30b-a3b:q4_k_m"),
          ("xing", "xing4.0-29b-a4b:iq4_nl"),
          ("g9v3", "g9v3-39a5b:q4_k_m")]

def load(p):
    if not (p / "results.json").is_file():
        return None
    d = json.load(open(p / "results.json"))
    s = d["model_summaries"][0]
    return {"acc": s["accuracy"], "correct": s["correct"], "total": s["total"],
            "parsed": s["parsed"], "tps": s.get("generation_tps") or 0,
            "wall": (s.get("wall_seconds") or 0) / 60,
            "tok": sum(int(b.get("eval_count") or 0) for b in d["batches"]),
            "capped": [b["category"] for b in d["batches"]
                       if int(b.get("eval_count") or 0) >= NP - 8],
            "timeout": [b["category"] for b in d["batches"]
                        if "Timeout" in str(b.get("error") or "")],
            "nbatch": len(d["batches"])}

rows = []
for slug, tag in MODELS:
    on = load(RUN / f"mmlu-{slug}-think{NP}")
    off = load(RUN / f"mmlu-{slug}-2048")
    if on is None:
        print(f"{tag:<38} thinking-on run not present yet"); continue
    if on["tok"] == 0:
        print(f"{tag:<38} VOID -- 0 generated tokens, every request errored"); continue
    if on["nbatch"] < 14 or on["total"] < 70:
        print(f"{tag:<38} PARTIAL ({on['nbatch']}/14 batches) -- not a result"); continue
    rows.append((tag, off, on))

print(f"{'model':<38} {'off':>7} {'on(scored)':>11} {'delta':>7} {'on(answered)':>13} {'parsed':>8} {'tok':>8} {'tps':>6}")
for tag, off, on in rows:
    ans = on["correct"] / on["parsed"] * 100 if on["parsed"] else 0.0
    offacc = f"{off['acc']:.2f}" if off else "  ?  "
    delta = f"{on['acc'] - off['acc']:+.2f}" if off else "  ?  "
    print(f"{tag:<38} {offacc:>7} {on['acc']:>10.2f}% {delta:>7} {ans:>12.2f}% "
          f"{on['parsed']:>4}/{on['total']:<3} {on['tok']:>8} {on['tps']:>6.1f}")
    if on["timeout"]:
        print(f"{'':<38} CLIENT TIMEOUT (rig failure, not the model): {', '.join(on['timeout'])}")
    if on["capped"]:
        print(f"{'':<38} truncated at {NP}: {', '.join(on['capped'])} "
              f"(these score 0 and make the scored figure a floor)")
