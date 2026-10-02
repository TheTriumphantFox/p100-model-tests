#!/usr/bin/env python3
"""Markdown table of the sweep: decode and prefill tok/s, layer vs tensor."""
import glob, json, os, re, statistics
rows = {}
for meta in sorted(glob.glob("raw/[0-9][0-9]-*.meta")):
    tag = os.path.basename(meta)[:-5]; idx, mode = tag.split("-", 1)
    name = open(meta).read().split("|")[0]
    res = {}
    try:
        for l in open(f"raw/{tag}.jsonl"):
            if l.strip():
                r = json.loads(l); res["pp" if r["n_prompt"] else "tg"] = r["avg_ts"]
    except FileNotFoundError:
        pass
    rows.setdefault(idx, {"name": name})[mode] = res
fmt = lambda v: f"{v:.1f}" if v else "fail"
print("| model | decode layer | decode tensor | gain | prefill layer | prefill tensor |")
print("|---|---:|---:|---:|---:|---:|")
for idx in sorted(rows):
    r = rows[idx]; L, T = r.get("layer", {}), r.get("tensor", {})
    gain = f"{(T['tg']/L['tg']-1)*100:+.0f}%" if L.get("tg") and T.get("tg") else "—"
    print(f"| {r['name']} | {fmt(L.get('tg'))} | {fmt(T.get('tg'))} | {gain} | {fmt(L.get('pp'))} | {fmt(T.get('pp'))} |")
fn = "raw/13-flashnext.jsonl"
if os.path.exists(fn):
    m = [json.loads(l) for l in open(fn) if '"measure"' in l]
    if m:
        print(f"| qwen3.8-flash-next IQ2_XXS (server, 24 distinct prompts) | {statistics.median(x['gen_tps'] for x in m):.1f} | not supported | — | {statistics.median(x['pp_tps'] for x in m):.1f} | — |")
