#!/usr/bin/env python3
"""Cross-check pi's llamacpp entries against the :8080 router presets for truncation risks."""
import json, re, urllib.request
from pathlib import Path
models = json.load(open(Path.home() / ".pi/agent/models.json"))["providers"]["llamacpp"]["models"]
sett = json.load(open(Path.home() / ".pi/agent/settings.json"))["compaction"]
router = {m["id"]: m for m in json.load(urllib.request.urlopen("http://127.0.0.1:8080/models"))["data"]}
def arg(a, flag):
    return a[a.index(flag) + 1] if flag in a else None
ids = [m["id"] for m in models]
print("pi entries:", len(ids), "unique:", len(set(ids)), "| router presets:", len(router))
print(f"{'id':30} {'pi ctx':>7} {'router':>7} {'maxTok':>6} {'reserve':>7} {'budget':>6}  verdict")
for m in models:
    a = router[m["id"]]["status"]["args"]
    rctx = int(arg(a, "--ctx-size")); bud = arg(a, "--reasoning-budget")
    ov = sett.get("modelOverrides", {}).get(f"llamacpp/{m['id']}", {})
    res = ov.get("reserveTokens", sett["reserveTokens"]); keep = ov.get("keepRecentTokens", sett["keepRecentTokens"])
    mt = m["maxTokens"]; issues = []
    if m["contextWindow"] != rctx: issues.append(f"pi ctx != router ctx")
    if res < mt: issues.append("reserve < maxTokens (reply can hit n_ctx)")
    if keep + res >= rctx: issues.append("keepRecent+reserve >= ctx")
    if bud and int(bud) >= mt: issues.append("budget >= maxTokens (no room to answer)")
    print(f"{m['id']:30} {m['contextWindow']:>7} {rctx:>7} {mt:>6} {res:>7} {bud or '-':>6}  {'OK' if not issues else '; '.join(issues)}")
