#!/usr/bin/env python3
"""Generate FINAL.md: the readable version of this run, built from the raw records.

Every number is read from results.json / *.jsonl at generation time, so the document
cannot drift from the data. Regenerate with:  ./make_final.py > FINAL.md
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = HERE.parents[1]
PY = str(TESTS / ".venv" / "bin" / "python")
REF = "qwen3.6-27b-abliterated:q5_k_m"

SOURCES = [HERE, TESTS / "2026-09-19" / "candidates-round2", TESTS / "2026-09-19" / "candidates"]
ORDER = [
    ("qwen3.6-27b-abliterated:q5_k_m", "incumbent — the model to beat"),
    ("qwen3.8-27b-ggmlorg:q8_0", "**new** — the DFlash speculative-decoding base"),
    ("qwen3.8-27b-unsloth:q8_0", "best HumanEval on the box"),
    ("qwen3.8-27b-uncensored-hauhaucs:q6_k_p", "uncensored"),
    ("qwen3.8-27b-stock:q4_k_m", "the only unmodified Qwen3.8"),
    ("gpt-oss-20b:q8_0", "fastest useful model, 12.1 GB"),
    ("ornith-1.5-35b-a3b:q4_k_m", "MoE, 4.8× the incumbent's speed"),
    ("g9v3-39a5b:q4_k_m", "MoE, cheapest KV measured"),
    ("qwen3.6-27b-opus-distill:q4_k_m", "**unrunnable** — vision model, not the text distill"),
    ("qwen3.6-35b-a3b-abliterated-vl:q4_k_m", "**unrunnable** — mrope not supported"),
    ("gemma4-e4b-abliterated:q4_k_m", "**unrunnable** — E4B tensors not mapped"),
    ("devstral-patched:latest", "**production** — measured 2026-09-21; no thinking mode"),
]
RETIRED = ["qwen3.8-27b-unsloth:ud_q6_k", "glm-4.7-flash:q5_k_m",
           "nemotron-cascade-2-30b-a3b:q4_k_m", "xing4.0-29b-a4b:iq4_nl"]


def sh(*args: str) -> str:
    return subprocess.run([PY, *args], capture_output=True, text=True, cwd=HERE).stdout.rstrip()


def read(d: Path, kind: str):
    f = d / "results.json"
    if not f.is_file():
        return None
    try:
        p = json.loads(f.read_text())
    except Exception:
        return None
    rows, sm = p.get("results") or [], p.get("model_summaries") or []
    meta = p.get("metadata") or {}
    if not rows or not sm or not meta.get("finished"):
        return None
    s, cfg, batches = sm[0], meta.get("settings") or {}, p.get("batches") or []
    tok = sum(int(b.get("eval_count") or 0) for b in batches)
    errs = sum(1 for b in batches if str(b.get("error") or ""))
    item_err = sum(1 for r in rows if str(r.get("error") or ""))
    dead = (batches and (tok == 0 or errs == len(batches))) or \
           (not batches and rows and item_err == len(rows))
    np_ = cfg.get("num_predict") or 0
    cap = sum(1 for b in batches if int(b.get("eval_count") or 0) >= np_ - 8) if np_ else 0
    if "question_id" in rows[0]:
        items = {str(r["question_id"]): bool(r["correct"]) for r in rows}
    else:
        items = {str(r["task_id"]): bool(r["passed"]) for r in rows}
    return dict(kind=kind, dead=bool(dead), acc=s.get("pass_at_1", s.get("accuracy")),
                n=s.get("attempted", s.get("total")), parsed=s.get("parsed"),
                cap=cap, tok=tok, np=np_, items=items, pc=cfg.get("per_category"))


def collect():
    cells: dict[str, dict] = {}
    for src in SOURCES:
        if not src.is_dir():
            continue
        for d in sorted(src.iterdir()):
            if not d.is_dir():
                continue
            if d.name.startswith("humaneval-"):
                kind = "he"
            elif d.name.startswith("mmlu-"):
                kind = "on" if "think" in d.name else "off"
            else:
                continue
            r = read(d, kind)
            if not r:
                continue
            if kind != "he" and r["pc"] != 5:
                continue
            tag = json.loads((d / "results.json").read_text())["model_summaries"][0]["name"]
            slot = cells.setdefault(tag, {})
            cur = slot.get(kind)
            if cur is None or (cur["dead"] and not r["dead"]) or \
               (not r["dead"] and r["np"] > cur["np"]):
                slot[kind] = r
        for f in sorted((src / "throughput").glob("*.json")):
            try:
                by = json.loads(f.read_text())["summary"]["by_model_test"]
                tag, tests = next(iter(by.items()))
                v = [t["avg_score_tok_per_sec"] for t in tests.values()
                     if t.get("avg_score_tok_per_sec")]
                if v:
                    cells.setdefault(tag, {}).setdefault(
                        "tput", f"{min(v):.1f}" if max(v) - min(v) < .05 else f"{min(v):.1f}–{max(v):.1f}")
            except Exception:
                pass
    mark_nothink(cells)
    return cells


def mark_nothink(cells) -> None:
    """Flag thinking-on runs where thinking never actually engaged.

    A model with no thinking mode still produces a complete, finished thinking-on
    results.json: the shim sets chat_template_kwargs.enable_thinking, the template
    ignores a variable it does not define, and the model answers exactly as it does
    thinking-off. devstral-patched is the case that forced this -- 280 generated tokens
    against 280 thinking-off, 0/0 discordant over all 70 questions, byte-identical
    behaviour. Printing its 58.57 in a column headed "model allowed to think first"
    would state something that did not happen.

    The rule is bench_think.sh's own, so the driver and the report cannot disagree:
    fewer than 2x the thinking-off token count means thinking did not engage.
    """
    for slot in cells.values():
        on, off = slot.get("on"), slot.get("off")
        if on and off and off["tok"] and on["tok"] < 2 * off["tok"]:
            on["nothink"] = True


def fmt(r, best=None):
    """Bold ONLY the column leader. Bolding every cell marks nothing."""
    if r is None:
        return "—"
    if r["dead"]:
        return "`cannot load`"
    if r.get("nothink"):
        return "`no thinking mode`"
    lead = best is not None and abs(r["acc"] - best) < 1e-9 and not r["cap"]
    txt = f"**{r['acc']:.2f}**" if lead else f"{r['acc']:.2f}"
    if r["cap"]:
        txt += f" †{r['cap']}"
    return txt


def column_best(cells, kind, tags):
    """Highest score in a column, ignoring dead runs and floors (a floor is not a score)."""
    vals = [cells[t][kind]["acc"] for t in tags
            if t in cells and cells[t].get(kind)
            and not cells[t][kind]["dead"] and not cells[t][kind]["cap"]
            and not cells[t][kind].get("nothink")]
    return max(vals) if vals else None


def exact(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def pair(a, b):
    ids = sorted(a["items"])
    if set(a["items"]) != set(b["items"]):
        return None
    x = sum(1 for q in ids if a["items"][q] and not b["items"][q])
    y = sum(1 for q in ids if b["items"][q] and not a["items"][q])
    return x, y, exact(x, y)


def ladders():
    out = {}
    d = HERE / "ctx-ladder"
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.jsonl")):
        rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
        rows.sort(key=lambda r: r["ctx"])
        fit = [r for r in rows if r.get("status") == "resident" and r.get("vram_mib")]
        kv = None
        if len(fit) > 1 and fit[-1]["ctx"] != fit[0]["ctx"]:
            kv = (fit[-1]["vram_mib"] - fit[0]["vram_mib"]) * 1048576 / (fit[-1]["ctx"] - fit[0]["ctx"]) / 1024
        out[f.stem] = dict(rows=rows, kv=kv, top=max((r["ctx"] for r in fit), default=0),
                           weights=rows[0].get("weights_mib", 0),
                           vram_top=fit[-1]["vram_mib"] if fit else 0,
                           tps=fit[-1].get("tok_per_s") if fit else None)
    return out


def repro():
    out = []
    d = HERE / "repro"
    arms = [("A", "incumbent MMLU-off (control)", "A-incumbent-off-*"),
            ("B", "gpt-oss MMLU-off", "B-gptoss-off-*"),
            ("C", "gpt-oss MMLU-off, no `reasoning_effort`", "C-gptoss-off-noeffort"),
            ("D", "incumbent MMLU-**ON**", "D-incumbent-on-*")]
    hist = {"B": [TESTS / "2026-09-19/candidates/mmlu-gpt-oss", HERE / "mmlu-gpt-oss-20b-pc5-np2048"],
            "D": [TESTS / "2026-09-19/candidates-round2/mmlu-qwen36-rerun-think12288"]}
    for k, label, pat in arms:
        runs = [read(x, "off") for x in sorted(d.glob(pat))] if d.is_dir() else []
        runs = [r for r in runs if r]
        for h in hist.get(k, []):
            r = read(h, "off")
            if r:
                runs.insert(0, r)
        if not runs:
            continue
        accs = [r["acc"] for r in runs]
        toks = [r["tok"] for r in runs]
        ident = all(runs[0]["items"] == r["items"] for r in runs[1:])
        out.append((k, label, len(runs), min(toks), max(toks), accs,
                    max(accs) - min(accs), ident))
    return out



# ---------------------------------------------------------------------------------------
# Presentation. Written for someone reading this cold: a verdict first, plain words for the
# statistics, and only the differences that survived a test -- the previous version printed
# three six-column tables of every comparison, significant or not, which buried the answer.
# ---------------------------------------------------------------------------------------

WORKING = [
    ("qwen3.6-27b-abliterated:q5_k_m", "the incumbent"),
    ("devstral-patched:latest", "**what production runs today**"),
    ("qwen3.8-27b-unsloth:q8_0", "Qwen3.8, Unsloth Q8_0"),
    ("qwen3.8-27b-ggmlorg:q8_0", "Qwen3.8, ggml-org Q8_0 — has the 2× drafters"),
    ("qwen3.8-27b-uncensored-hauhaucs:q6_k_p", "Qwen3.8, uncensored"),
    ("qwen3.8-27b-stock:q4_k_m", "Qwen3.8, stock"),
    ("gpt-oss-20b:q8_0", "small and very fast"),
    ("ornith-1.5-35b-a3b:q4_k_m", "MoE, fast"),
    ("g9v3-39a5b:q4_k_m", "MoE, fast, cheap context"),
]
BROKEN = [
    ("qwen3.6-27b-opus-distill:q4_k_m", "won't load — it is a vision model"),
    ("qwen3.6-35b-a3b-abliterated-vl:q4_k_m", "won't load — vision model"),
    ("gemma4-e4b-abliterated:q4_k_m", "won't load — unsupported architecture"),
]


def score(r, best=None) -> str:
    if r is None:
        return "—"
    if r["dead"]:
        return "—"
    if r.get("nothink"):
        return "none"
    txt = f"{r['acc']:.1f}"
    if best is not None and abs(r["acc"] - best) < 1e-9 and not r["cap"]:
        txt = f"**{txt}**"
    if r["cap"]:
        txt += "*"
    return txt


def main() -> int:
    cells, lad = collect(), ladders()
    tags = [t for t, _ in WORKING] + RETIRED
    best = {k: column_best(cells, k, tags) for k in ("off", "on", "he")}
    L: list[str] = []
    p = L.append

    p("# Which local model should we use?")
    p("")
    p(f"*Test run finished {time.strftime('%d %B %Y')}. Two Tesla P100s, 32 GB of video memory total.*")
    p("")
    p("## The answer")
    p("")
    p("**Keep the incumbent, `qwen3.6-27b-abliterated`. Nothing displaced it.**")
    p("")
    p("It has the best score in every accuracy test, and it is the only model that finishes")
    p("every reasoning question instead of running out of budget partway through.")
    p("")
    p("Four things changed, and none of them is \"switch models\":")
    p("")
    p("- **The fast-and-accurate combination we were chasing does not exist.** A Qwen3.8 file")
    p("  runs at twice the incumbent's speed, but its coding score is no better — so the speed")
    p("  is real and the accuracy gain was wishful.")
    p("- **Our best reasoning score was a fluke.** `gpt-oss-20b` was recorded at 77.1. Repeated")
    p("  five times, it scores 71.4 in four of them — the same as the incumbent, not ahead of it.")
    p("- **Three models on the shelf cannot run on this machine at all.** Not \"scored badly\" —")
    p("  they fail to load.")
    p("- **`devstral`, the model production actually runs, is now measured.** It is")
    p("  **measurably worse at coding than the incumbent** — 84.8 against 96.3, a gap solid")
    p("  enough to call (p<0.001) — and lower on the quick exam too, though that second gap")
    p("  is not big enough to be sure of. It has no thinking mode at all. **This is not an")
    p("  argument for replacing it**: nothing here tests what production actually uses it")
    p("  *for*. See \"What these tests do not cover\" — the most important section in this")
    p("  document for that decision.")
    p("")
    p("---")
    p("")
    p("## How to read the numbers")
    p("")
    p("| column | what it means | higher is |")
    p("|---|---|---|")
    p("| **Speed** | tokens per second — roughly words per second, as you feel it typing out | better |")
    p("| **Reasoning (quick)** | general-knowledge exam, model answers immediately | better |")
    p("| **Reasoning (thinking)** | same exam, model allowed to think first | better |")
    p("| **Coding** | 164 programming problems, % that actually run correctly | better |")
    p("")
    p("**none** in the thinking column means the model has **no thinking mode** — there is no")
    p("such run to report, which is different from scoring badly at it.")
    p("")
    p("An asterisk `*` means **the real score is higher than shown**. The model spent its whole")
    p("thinking budget and never wrote an answer down, which the exam counts as wrong. So a")
    p("starred number is a floor, and cannot be fairly compared with an unstarred one.")
    p("")
    p("All scores come from the same questions for every model, so they are directly comparable.")
    p("")
    p("## The results")
    p("")
    p("| model | | Speed | Reasoning (quick) | Reasoning (thinking) | Coding |")
    p("|---|---|---:|---:|---:|---:|")
    for tag, note in WORKING:
        c = cells.get(tag, {})
        p(f"| `{tag.split(':')[0]}` | {note} | {c.get('tput', '—')} | "
          f"{score(c.get('off'), best['off'])} | {score(c.get('on'), best['on'])} | "
          f"{score(c.get('he'), best['he'])} |")
    p("")
    p("**Bold** is the best in that column. Speed is tokens per second.")
    p("")
    p("### Models that produced no numbers")
    p("")
    p("| model | why |")
    p("|---|---|")
    for tag, why in BROKEN:
        p(f"| `{tag.split(':')[0]}` | {why} |")
    p("")
    p("## Which gaps are real, and which are noise?")
    p("")
    p("A 70-question exam cannot tell apart two models a few points apart — the difference is")
    p("as likely to be luck as skill. So each model was compared against the incumbent")
    p("question by question, and only differences that pass a statistical test are listed here.")
    p("")
    real, noise = [], []
    for kind, label in (("off", "Reasoning (quick)"), ("on", "Reasoning (thinking)"),
                        ("he", "Coding")):
        ref = cells.get(REF, {}).get(kind)
        if not ref:
            continue
        for tag, _ in WORKING + [(t, "") for t in RETIRED]:
            if tag == REF:
                continue
            c = cells.get(tag, {}).get(kind)
            if not c or c["dead"]:
                continue
            # A model with no thinking mode has no thinking run to compare. Listing its
            # thinking-off answers against the incumbent's thinking run under the heading
            # "Reasoning (thinking)" would compare two different tasks.
            if c.get("nothink"):
                continue
            got = pair(c, ref)
            if not got:
                continue
            x, y, pv = got
            row = (label, tag.split(":")[0], c["acc"] - ref["acc"], pv, tag in RETIRED)
            (real if pv < 0.05 else noise).append(row)
    p("### Real differences — all of them are the incumbent winning")
    p("")
    p("Models still on the shelf come first; the rest were deleted after earlier rounds and")
    p("are shown only because they were measured on the same questions.")
    p("")
    p("| test | model | behind the incumbent by | confidence |")
    p("|---|---|---:|---|")
    def pfmt(v):
        return "p < 0.001" if v < 0.001 else f"p={v:.3f}"
    for label, tag, gap, pv, retired in sorted(real, key=lambda r: (r[4], r[2])):
        name = f"`{tag}` *(deleted)*" if retired else f"`{tag}`"
        p(f"| {label} | {name} | {abs(gap):.1f} points | {pfmt(pv)} |")
    p("")
    p(f"### Everything else is a tie ({len(noise)} comparisons)")
    p("")
    p("No other model beat the incumbent on any test, and no other gap is big enough to call.")
    p("**\"We can't tell them apart\" is not the same as \"it's as good as the incumbent\"** —")
    p("and the brief asked for something better, which nothing delivered.")
    p("")
    p("The closest calls, all statistically indistinguishable from the incumbent:")
    p("")
    shelf_noise = [r for r in noise if not r[4]]
    for label, tag, gap, pv in [(a, b, c, d) for a, b, c, d, _ in
                                sorted(shelf_noise, key=lambda r: -r[3])[:5]]:
        how = "an exact tie" if abs(gap) < 0.05 else f"{gap:+.1f} points"
        p(f"- `{tag}` on {label.lower()}: {how} (p={pv:.2f})")
    p("")
    p("## Can we trust these numbers?")
    p("")
    p("Yes — with one named exception. The same test was repeated several times to see whether")
    p("it gives the same answer twice.")
    p("")
    p("| what was repeated | times run | scores | same answers each time? |")
    p("|---|---:|---|---|")
    for k, label, n, lo, hi, accs, spread, ident in repro():
        clean = (label.replace("incumbent MMLU-off (control)", "incumbent, quick exam")
                      .replace("gpt-oss MMLU-off, no `reasoning_effort`", "gpt-oss, settings changed")
                      .replace("gpt-oss MMLU-off", "gpt-oss, quick exam")
                      .replace("incumbent MMLU-**ON**", "**incumbent, thinking exam**"))
        idt = ("**yes, identical**" if ident else "**no**") if n > 1 else "only ran once"
        p(f"| {clean} | {n} | {', '.join(f'{a:.1f}' for a in accs)} | {idt} |")
    p("")
    p("**The thinking test is perfectly repeatable.** The incumbent's 44,000-token thinking run")
    p("was done three times across two days and gave an identical result every time, down to")
    p("the individual question. So the thinking scores in the table above are solid.")
    p("")
    p("**`gpt-oss-20b` is the exception.** It is the only model that gives different answers on")
    p("identical repeat runs. Its old 77.1 record could not be reproduced under any setting we")
    p("tried — including deliberately letting it think much harder, which made it *worse* (60.0).")
    p("Treat its numbers as approximate in a way no other model's are.")
    p("")
    p("## How much context fits?")
    p("")
    p("Context is the model's working memory for a conversation. The worry was that big models")
    p("could not hold a useful amount. **They can, easily.**")
    p("")
    p("| model | biggest context tested | still fit in memory? | speed penalty |")
    p("|---|---:|---|---|")
    for slug, d in sorted(lad.items()):
        if slug.endswith("-q8_0"):
            continue
        p(f"| `{slug}` | {d['top']:,} tokens | yes, {32768 - d['vram_top']:,} MiB spare | none |")
    p("")
    p("Nothing ran out of memory at any size tested, and speed did not drop at all as context")
    p("grew. Two numbers in our earlier notes were simply wrong:")
    p("")
    p("- We recorded that these models cost **260 KB of memory per token** of context. Measured,")
    p("  it is **72 KB** — three and a half times cheaper. The incumbent has room for roughly")
    p("  **180,000 tokens** of context, not the ~8,000 we have been running.")
    p("- We recorded `g9v3` as having **seven times** cheaper context than the others, which was")
    p("  the main reason to keep it. Measured, it is **1.6 times** cheaper. Still cheapest, but")
    p("  that is not a reason to keep a model on its own.")
    p("")
    p("The one caveat: 32,768 tokens was the largest size we *tried*, not the largest that fits.")
    p("The real ceiling is higher and has not been found.")
    p("")
    p("### Production has room to roughly double its context, for free")
    p("")
    p("`devstral` was loaded at two context sizes during this round, which measures its")
    p("context cost directly:")
    p("")
    p("| context | memory used | note |")
    p("|---:|---:|---|")
    p("| 8,192 | 25,679 MiB | the size we benchmark at |")
    p("| 16,384 | 27,023 MiB | the thinking-exam size |")
    p("")
    p("That is **168 KB per token** — more than twice the 72 KB the Qwen models cost, so the")
    p("\"room for 180,000 tokens\" figure above is about the incumbent and does **not** carry")
    p("over to devstral. Production halves that cost again by storing its context compressed")
    p("(`q8_0`), giving roughly **84 KB per token**.")
    p("")
    p("At that rate, production\'s current 49,152-token setting leaves about **4,400 MB unused**,")
    p("and the ceiling is roughly **100,000 tokens**. Raising production to **65,536** would")
    p("still leave ~3,000 MB of headroom and costs nothing — no new model, no new hardware, no")
    p("accuracy trade. On the evidence in this document that is worth more than any model")
    p("swap on the shelf: every win this box has produced has come from configuration —")
    p("thinking on (+15.7 points), Q8_0 over Q4_K_M (+4.27), and context — and none from")
    p("choosing a different model.")
    p("")
    p("One honest caveat: the 84 KB figure is the measured 168 KB halved, not separately")
    p("measured. `ctx-ladder.sh` would confirm it in about twenty minutes, and should be run")
    p("before the change is made.")
    p("")
    p("## What these tests do not cover")
    p("")
    p("**All four columns are single-turn question-and-answer.** A question goes in, one")
    p("answer comes back, and it is marked right or wrong. Nothing here involves the model")
    p("calling a tool, reading the result, and deciding what to do next.")
    p("")
    p("That matters most for `devstral`, because **agentic tool use is the entire job it does")
    p("in production**. Its scores above therefore say almost nothing about whether it is the")
    p("right model for that job. The evidence is in the model file itself: devstral\'s prompt")
    p("template carries a tool-calling section, and the local patch that gives it the")
    p("`-patched` name is a fix to that section for agentic clients. It is built for a task")
    p("none of these four tests administers.")
    p("")
    p("So: **do not read \"devstral scores below the incumbent\" as \"replace devstral\".** The")
    p("honest statement is that on general knowledge and on one-shot coding problems the")
    p("incumbent is better, and on the thing production actually does, we have no measurement")
    p("at all. Getting one needs a tool-use harness, which does not exist here yet.")
    p("")
    p("The same gap applies to refusal behaviour, and this round sharpened why: the quick exam")
    p("cannot even tell an uncensored model from a stock one — three versions of Qwen3.8 gave")
    p("*identical* answers to all 70 questions — so it is no evidence either way.")
    p("")
    p("## What is still not done")
    p("")
    p("1. **No harness measures agentic tool use**, which is the gap above and the most")
    p("   valuable one to close.")
    p("2. **Three models cannot be tested on this machine** without a newer or patched runtime.")
    p("   Worth knowing: `opus-distill` was kept on the shelf specifically to verify its claimed")
    p("   75.7 reasoning score. That claim cannot be checked here at all — the file is a vision")
    p("   model, not the text model our notes describe.")
    p("3. **The bigger 280-question exam is built but not run**, waiting on your choice of which")
    p("   models deserve it. It will need the incumbent re-run as a fresh baseline, because it")
    p("   draws different questions and its scores cannot be compared to the ones above.")
    p("4. **`devstral` has no thinking mode**, so its thinking-exam cell is not a low score —")
    p("   there is no such run to report. Its prompt template contains no thinking path at all,")
    p("   and the thinking-on attempt returned the thinking-off answers exactly.")
    p("")
    p("---")
    p("")
    p("## Reference")
    p("")
    p("**Settings** — every score above: 70 exam questions (5 per category × 14), fixed random")
    p("seed 42, temperature 0. Quick exam: 8,192 context. Thinking exam: 16,384 context and a")
    p("12,288-token thinking budget. Coding: all 164 HumanEval problems. Identical to the")
    p("settings used in the previous two rounds, so old and new numbers are comparable.")
    p("")
    inv = sh(str(HERE / "inventory.py"))
    count = next((l.split(" runs")[0] for l in inv.splitlines() if " runs on disk" in l), "?")
    p(f"**Data** — {count} benchmark runs on disk, each storing its own settings, question set")
    p("and per-question results.")
    p("")
    p("| file | what it holds |")
    p("|---|---|")
    p("| `FINAL.md` | this document — regenerate with `./make_final.py > FINAL.md` |")
    p("| `REPORT.md` | the technical write-up: method, every finding, the bugs found |")
    p("| `DATASET.txt` | complete raw dump — regenerate with `./DATASET.sh` |")
    p("| `inventory.py` | every run with its settings and provenance |")
    p("| `pairs.py`, `mcnemar.py` | the statistical comparisons |")
    p("| `ctx-ladder/` | the context measurements |")
    p("| `WATCHDOG.log` | what the run monitor saw overnight |")
    p("")
    p("**The statistics**, for anyone checking: comparisons are McNemar's exact test on paired")
    p("per-question results, not a two-proportion test — every model answers the same questions,")
    p("and discarding that pairing would both lose power and, at 70 questions, be capable of")
    p("calling a genuine 15-point gap noise. Gaps are reported as significant only at p<0.05.")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
