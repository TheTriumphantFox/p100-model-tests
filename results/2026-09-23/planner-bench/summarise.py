#!/usr/bin/env python3
"""Summarise planner-bench results into RESULTS.md (and stdout). CPU-only.

The headline metric is **correct within deadline**: exact bytes, validated, and
finished inside the section 3 planner deadline (120 s initial, 240 s maximum).
**Escalation-eligible** follows v7.2 R76: VALIDATION_FAILED, or PLANNER_DEADLINE
(wall time over the deadline). NO_CHANGE, CHECK_FAILED and a wrong-but-valid
plan are not eligible -- the last one reaches the human reviewer, which makes it
the most dangerous outcome, and it is counted separately.
"""
from __future__ import annotations

import glob
import json
import statistics
from collections import Counter
from pathlib import Path

import bench

HERE = Path(__file__).resolve().parent
ORDER = ["g9v3", "devstral", "gptoss", "ornith", "qwen36", "qwen38", "qwen36moe", "ornith-pinned", "qwen36moe-pinned"]
NAMES = {"g9v3": "g9v3-39a5b q4_k_m", "devstral": "devstral q8_0", "gptoss": "gpt-oss-20b q8_0",
         "ornith": "ornith-1.5-35b-a3b q4_k_m", "qwen36": "qwen3.6-27b q5_k_m", "qwen38": "qwen3.8-27b q8_0",
         "qwen36moe": "qwen3.6-35b-a3b UD-Q6_K",
         "ornith-pinned": "ornith, checks pinned", "qwen36moe-pinned": "qwen3.6-35b-a3b, checks pinned"}


def load():
    runs = {}
    for f in glob.glob(str(HERE / "results" / "*.json")):
        slug = Path(f).stem
        try:
            runs[slug] = json.load(open(f))
        except (ValueError, OSError):
            pass
    return runs


def _content(raw):
    """The write's content from a raw response, whether or not the plan validated."""
    try:
        w = bench.strict_loads(raw.strip())["calls"][0]
        return w["content"] if isinstance(w.get("content"), str) else None
    except Exception:
        return None


def rescore(runs, tasks):
    """Re-score every result from its raw response with the current scorer, so all
    models are judged identically, and add two views:

    ok          correct, ignoring a missing trailing newline. The prompt renders each
                file with its trailing newline stripped (bench.user_message), so a
                model cannot see it; holding that against it would score the harness.
    content_ok  the content alone is ok, whatever happened to the envelope (handle,
                hash, checks) -- what a grammar pinning the envelope would yield.
    """
    by_id = {t["id"]: t for t in tasks}
    for doc in runs.values():
        for r in doc["results"]:
            t = by_id[r["id"]]
            r.update(bench.score(r.get("raw"), t))
            exp = t["expected_content"]
            c = _content(r.get("raw"))
            near = c is not None and (c == exp or c == exp.rstrip("\n"))
            r["ok"] = r["verdict"] == "correct" or (r["outcome"] == "reviewable" and near)
            r["content_ok"] = near


def eligible(r, deadline):
    return r["outcome"] == "validation_failed" or r["wall_s"] > deadline


def correct_within(r, deadline):
    return r["ok"] and r["wall_s"] <= deadline


def pct(a, n):
    return f"{a}/{n} ({100 * a / n:.0f}%)" if n else "–"


def main():
    tasks = json.load(open(HERE / "tasks.json"))["tasks"]
    total = len(tasks)
    runs = load()
    slugs = [s for s in ORDER if s in runs] + sorted(s for s in runs if s not in ORDER)
    if not slugs:
        print("no results yet")
        return
    rescore(runs, tasks)
    L = []
    L.append("# Planner benchmark results\n")
    L.append(f"{total} tasks per model. Every request ran to completion with no time limit; "
             "deadlines are applied to the measured wall time afterwards.\n")

    # ---------------------------------------------------------- headline
    L.append("## Headline\n")
    L.append("| Model | Done | Correct (any time) | Correct ≤120 s | Correct ≤240 s | Content correct, envelope ignored | "
             "Wrong but valid | Escalation-eligible @120 | @240 | Injection followed | Median wall | Max wall |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for s in slugs:
        rs = runs[s]["results"]
        n = len(rs)
        walls = [r["wall_s"] for r in rs]
        inj = [r for r in rs if r["family"] == "injection"]
        L.append(
            f"| {NAMES.get(s, s)} | {n}/{total} "
            f"| {pct(sum(r['ok'] for r in rs), n)} "
            f"| {pct(sum(correct_within(r, 120) for r in rs), n)} "
            f"| {pct(sum(correct_within(r, 240) for r in rs), n)} "
            f"| {pct(sum(r['content_ok'] for r in rs), n)} "
            f"| {sum(r['outcome'] == 'reviewable' and r['verdict'] == 'wrong' for r in rs)} "
            f"| {pct(sum(eligible(r, 120) for r in rs), n)} "
            f"| {pct(sum(eligible(r, 240) for r in rs), n)} "
            f"| {sum(bool(r['injection_followed']) for r in inj)}/{len(inj)} "
            f"| {statistics.median(walls):.0f} s | {max(walls):.0f} s |"
        )
    L.append("")
    L.append("*Correct* = validated, and the content is the exact expected bytes, allowing only a missing "
             "trailing newline (the prompt renders files without it, so models cannot see it). On a "
             "no-change task it also covers the unchanged file, which the controller rejects as `NO_CHANGE`. "
             "The strict byte-exact count is in the next table. *Content correct, envelope ignored* = the same test "
             "applied to the content alone, even when the handle, hash or check list failed validation: what a "
             "grammar that pinned those fields would yield. *Wrong but valid* = passed every controller check with "
             "the wrong content, so only the human reviewer stands between it and a commit.\n")

    # ---------------------------------------------------------- outcomes
    L.append("## Where the answers went\n")
    L.append("Strict scoring: *Correct* here means byte-exact, so a missing trailing newline counts as *Equivalent*.\n")
    L.append("| Model | Correct | Equivalent (reformatted) | Wrong but valid | Check failed | No-change on a change task | Validation failed | Server error |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for s in slugs:
        rs = runs[s]["results"]
        c = Counter()
        for r in rs:
            if r.get("http_error") and r.get("raw") is None:
                c["server"] += 1
            elif r["verdict"] == "correct":
                c["correct"] += 1
            elif r["outcome"] == "reviewable":
                c["equivalent" if r["verdict"] == "equivalent" else "wrong"] += 1
            elif r["outcome"] == "check_failed":
                c["check"] += 1
            elif r["outcome"] == "no_change":
                c["nochange"] += 1
            else:
                c["validation"] += 1
        L.append(f"| {NAMES.get(s, s)} | {c['correct']} | {c['equivalent']} | {c['wrong']} | {c['check']} "
                 f"| {c['nochange']} | {c['validation']} | {c['server']} |")
    L.append("")

    L.append("### Validation failures by reason\n")
    reasons = sorted({r["reason"] for s in slugs for r in runs[s]["results"] if r["outcome"] == "validation_failed"})
    if reasons:
        L.append("| Model | " + " | ".join(f"`{x}`" for x in reasons) + " |")
        L.append("|---|" + "---:|" * len(reasons))
        for s in slugs:
            c = Counter(r["reason"] for r in runs[s]["results"] if r["outcome"] == "validation_failed")
            L.append(f"| {NAMES.get(s, s)} | " + " | ".join(str(c[x]) for x in reasons) + " |")
        L.append("")
        L.append("Details (identical failures grouped):\n")
        for s in slugs:
            groups = {}
            for r in runs[s]["results"]:
                if r["outcome"] == "validation_failed":
                    groups.setdefault((r["reason"], r["detail"]), []).append(r["id"])
            for (reason, detail), ids in sorted(groups.items(), key=lambda kv: -len(kv[1])):
                shown = ", ".join(f"`{i}`" for i in ids[:4]) + (f" and {len(ids) - 4} more" if len(ids) > 4 else "")
                L.append(f"- {NAMES.get(s, s)} · `{reason}` {detail} · {len(ids)} task{'s' * (len(ids) != 1)}: {shown}")
        L.append("")
    else:
        L.append("None.\n")

    # ---------------------------------------------------------- size ladder
    sizes = sorted({t["target_bytes"] for t in tasks if t["family"] == "size"})
    L.append("## Size ladder: wall time and verdict\n")
    L.append("Same two edits (listen port, one route's timeout) at each file size. "
             "✓ correct · ≈ same data, different bytes · ✗ wrong · V validation failed · C check failed. "
             "Bold = over 240 s.\n")
    L.append("| Model | " + " | ".join(f"{b / 1024:.1f} KiB" for b in sizes) + " |")
    L.append("|---|" + "---:|" * len(sizes))
    mark = {"correct": "✓", "equivalent": "≈", "wrong": "✗"}
    for s in slugs:
        by = {}
        for r in runs[s]["results"]:
            if r["family"] == "size":
                sym = "✓" if r["ok"] else mark.get(r["verdict"]) or \
                    {"validation_failed": "V", "check_failed": "C"}.get(r["outcome"], "?")
                w = f"{r['wall_s']:.0f}"
                by.setdefault(r["target_bytes"], []).append(f"{'**' + w + '**' if r['wall_s'] > 240 else w}{sym}")
        L.append(f"| {NAMES.get(s, s)} | " + " | ".join(" ".join(by.get(b, ["–"])) for b in sizes) + " |")
    L.append("")

    # ---------------------------------------------------------- speed
    L.append("## Speed\n")
    L.append("| Model | Prefill tok/s | Generation tok/s | Output bytes per token | Largest correct file ≤120 s | ≤240 s | Truncated | Unconstrained fallback | Mean reasoning chars |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for s in slugs:
        rs = [r for r in runs[s]["results"] if r.get("predicted_ms")]
        pre = [r["prompt_tokens"] / (r["prompt_ms"] / 1000) for r in rs if r.get("prompt_ms")]
        gen = [r["completion_tokens"] / (r["predicted_ms"] / 1000) for r in rs if r["predicted_ms"] > 0]
        bpt = [r["target_bytes"] / r["completion_tokens"] for r in rs
               if r["family"] == "size" and r.get("completion_tokens") and not r.get("reasoning_chars")]
        allr = runs[s]["results"]

        def largest(d):
            ok = [r["target_bytes"] for r in allr if correct_within(r, d)]
            return f"{max(ok) / 1024:.1f} KiB" if ok else "none"

        if not (pre and gen):
            L.append(f"| {NAMES.get(s, s)} | – | – | – | – | – | – | – | – |")
            continue
        # gpt-oss always reasons, so its completion tokens do not measure output bytes
        bpt_cell = f"{statistics.median(bpt):.2f}" if bpt else "– (reasons)"
        L.append(
            f"| {NAMES.get(s, s)} | {statistics.median(pre):.0f} | {statistics.median(gen):.1f} "
            f"| {bpt_cell} | {largest(120)} | {largest(240)} "
            f"| {sum(r.get('finish_reason') == 'length' for r in allr)} "
            f"| {sum(not r['constrained'] for r in allr)} "
            f"| {statistics.mean(r.get('reasoning_chars') or 0 for r in allr):.0f} |")
    L.append("")
    L.append("Output bytes per token is measured on the size ladder (file bytes ÷ completion tokens, "
             "including the JSON envelope), models without reasoning output only.\n")

    # ---------------------------------------------------------- families
    fams = ["size", "variety", "context", "activation", "injection", "nochange", "escaping"]
    L.append("## Correct by task family (any time)\n")
    L.append("| Model | " + " | ".join(fams) + " |")
    L.append("|---|" + "---:|" * len(fams))
    for s in slugs:
        rs = runs[s]["results"]
        cells = []
        for f in fams:
            fr = [r for r in rs if r["family"] == f]
            cells.append(f"{sum(r['ok'] for r in fr)}/{len(fr)}" if fr else "–")
        L.append(f"| {NAMES.get(s, s)} | " + " | ".join(cells) + " |")
    L.append("")

    text = "\n".join(L)
    (HERE / "RESULTS.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
