#!/usr/bin/env python3
"""The full CUDA benchmark matrix, assembled from every run on disk across all rounds.

Runs are keyed by the MODEL TAG recorded inside each results.json, not by directory name,
so a model benchmarked in three different rounds lands on one row wherever its files live.

    matrix.py [--pc 5] [--md]

Columns: throughput / MMLU-Pro thinking-off / MMLU-Pro thinking-on / HumanEval.

Cells are marked, not silently averaged, when a run is not a result:
    PART:n/N  fewer items scored than asked -- interrupted or still running
    RIG?      finished in under a minute; a router 500ing every request writes a tidy
              0.00% results.json that looks exactly like a real one
    cap:N     N thinking batches burned the whole num_predict budget and emitted no answer
              line. Those score 0/5, so the figure is a FLOOR, not a score.
    TMO:N     N batches hit the CLIENT timeout (eval_count=0). Rig failure, not truncation.

Only runs sharing --per-category and --seed are shown together: random.Random(seed).sample
is not nested across k, so a 280-question run shares 9 of 70 questions with a 70-question
run at the same seed and the two are not comparable, let alone pairable.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TESTS = Path(__file__).resolve().parents[2]
SOURCES = [
    TESTS / "2026-09-21" / "cuda-matrix",
    TESTS / "2026-09-19" / "candidates-round2",
    TESTS / "2026-09-19" / "candidates",
]
# Rows in the order the brief lists them, then anything else found on disk.
ORDER = [
    "qwen3.6-27b-abliterated:q5_k_m",
    "qwen3.8-27b-stock:q4_k_m",
    "ornith-1.5-35b-a3b:q4_k_m",
    "g9v3-39a5b:q4_k_m",
    "qwen3.8-27b-unsloth:q8_0",
    "qwen3.8-27b-uncensored-hauhaucs:q6_k_p",
    "qwen3.8-27b-ggmlorg:q8_0",
    "gpt-oss-20b:q8_0",
    "qwen3.6-27b-opus-distill:q4_k_m",
    "qwen3.6-35b-a3b-abliterated-vl:q4_k_m",
    "gemma4-e4b-abliterated:q4_k_m",
    "devstral-patched:latest",
]


def classify(name: str) -> str | None:
    if name.startswith("humaneval-"):
        return "he"
    if name.startswith("mmlu-"):
        return "mmlu_on" if "think" in name else "mmlu_off"
    return None


def read_run(d: Path, kind: str) -> dict | None:
    f = d / "results.json"
    if not f.is_file():
        return None
    try:
        payload = json.loads(f.read_text())
    except Exception as exc:
        return {"tag": None, "bad": f"UNREADABLE {type(exc).__name__}"}
    rows = payload.get("results") or []
    summaries = payload.get("model_summaries") or []
    if not rows or not summaries:
        return None
    s = summaries[0]
    meta = payload.get("metadata") or {}
    settings = meta.get("settings") or {}
    batches = payload.get("batches") or []
    flags: list[str] = []

    n = s.get("attempted", s.get("total")) or 0
    expected = None
    if settings.get("per_category") and meta.get("categories"):
        expected = settings["per_category"] * len(meta["categories"])
    # results.json is rewritten after every batch, so a run in progress leaves a
    # well-formed file holding a partial score. `finished` is written only in the
    # run's finally block, so its absence is the tell.
    if not meta.get("finished"):
        flags.append(f"PART:{n}/{expected}" if expected else f"PART:{n}")
    elif expected and n != expected:
        flags.append(f"PART:{n}/{expected}")

    np_ = settings.get("num_predict")
    if batches and np_:
        capped = [b for b in batches if int(b.get("eval_count") or 0) >= np_ - 8]
        if capped:
            flags.append(f"cap:{len(capped)}")
    tmo = [b for b in batches if "Timeout" in str(b.get("error") or "")]
    if tmo:
        flags.append(f"TMO:{len(tmo)}")

    wall = (s.get("wall_seconds") or 0) / 60
    tok = sum(int(b.get("eval_count") or 0) for b in batches)
    errored = sum(1 for b in batches if str(b.get("error") or ""))
    # A benchmark that produced no tokens, or whose every request errored, is a rig
    # failure however tidy its results.json looks -- the router 500ing everything still
    # writes a well-formed 0.00%. Wall-clock alone is NOT the signal: a thinking-off MMLU
    # run generates ~280 tokens in total, so a 70 tok/s model finishes it honestly in
    # under a minute. Flagging on wall time marked four real round-2 results as failures.
    item_err = sum(1 for r_ in rows if str(r_.get("error") or ""))
    if batches and (tok == 0 or errored == len(batches)):
        flags.append("RIG-FAIL")
    elif not batches and rows and item_err == len(rows):
        flags.append("RIG-FAIL")        # HumanEval: every task errored
    elif wall < 1.0 and batches and s.get("accuracy") == 0:
        flags.append("RIG?")

    return {
        "kind": kind,
        "tok": tok,
        "tag": s.get("name") or rows[0].get("model"),
        "acc": s.get("pass_at_1", s.get("accuracy")),
        "n": n,
        "parsed": s.get("parsed", s.get("passed")),
        "tps": s.get("generation_tps") or 0,
        "wall": wall,
        "per_category": settings.get("per_category"),
        "seed": settings.get("seed"),
        "num_predict": np_,
        "flags": flags,
        "dir": d,
    }


def read_throughput(f: Path) -> tuple[str, str] | None:
    try:
        payload = json.loads(f.read_text())
        by = payload["summary"]["by_model_test"]
        tag, tests = next(iter(by.items()))
        vals = [t["avg_score_tok_per_sec"] for t in tests.values()
                if t.get("avg_score_tok_per_sec")]
        if not vals:
            return None
        lo, hi = min(vals), max(vals)
        return tag, (f"{lo:.1f}" if hi - lo < 0.05 else f"{lo:.1f}-{hi:.1f}")
    except Exception:
        return None


def collect(pc: int) -> dict[str, dict]:
    rows: dict[str, dict] = {}

    def slot(tag: str) -> dict:
        return rows.setdefault(tag, {"tput": None, "mmlu_off": None, "mmlu_on": None, "he": None})

    for src in SOURCES:
        if not src.is_dir():
            continue
        for d in sorted(src.iterdir()):
            if not d.is_dir():
                continue
            kind = classify(d.name)
            if kind is None:
                continue
            r = read_run(d, kind)
            if not r or not r.get("tag"):
                continue
            # HumanEval has no --per-category; MMLU runs must match the requested sample.
            if kind != "he" and r.get("per_category") not in (None, pc):
                continue
            cur = slot(r["tag"])[kind]
            # Prefer a finished run over a partial one, then the later/larger budget.
            better = (
                cur is None
                or ("PART" in " ".join(cur["flags"]) and "PART" not in " ".join(r["flags"]))
                or (not any("PART" in f for f in r["flags"])
                    and (r.get("num_predict") or 0) > (cur.get("num_predict") or 0))
            )
            if better:
                slot(r["tag"])[kind] = r
        for f in sorted((src / "throughput").glob("*.json")):
            got = read_throughput(f)
            if got:
                tag, txt = got
                if slot(tag)["tput"] is None:
                    slot(tag)["tput"] = txt
    return rows


def cell(r: dict | None, tps: bool = False) -> str:
    if r is None:
        return "—"
    if r.get("bad"):
        return r["bad"]
    # A model that could not load scored nothing -- it did not score zero. Rendering
    # 0.00 next to real scores invites exactly the wrong reading, and these three rows
    # (gemma4-e4b, opus-distill, qwen36-vl) are unrunnable on this build, not bad models.
    if "RIG-FAIL" in r["flags"]:
        return "CANNOT LOAD"
    txt = f"{r['acc']:.2f}"
    if (r.get("kind") != "he" and r["parsed"] is not None and r["n"]
            and r["parsed"] < r["n"]):
        txt += f" ({r['parsed']}/{r['n']} parsed)"
    if tps and r["tps"]:
        txt += f" @{r['tps']:.0f}"
    if r["flags"]:
        txt += " " + ",".join(r["flags"])
    return txt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pc", type=int, default=5, help="--per-category of the runs to show")
    ap.add_argument("--md", action="store_true", help="emit a markdown table")
    args = ap.parse_args()

    rows = collect(args.pc)
    tags = [t for t in ORDER if t in rows] + sorted(t for t in rows if t not in ORDER)
    if not tags:
        print("no runs on disk")
        return 0

    head = ["model", "tok/s", f"MMLU-off@{args.pc}", f"MMLU-ON@{args.pc}", "HumanEval"]
    table = [[t,
              rows[t]["tput"] or "—",
              cell(rows[t]["mmlu_off"]),
              cell(rows[t]["mmlu_on"], tps=True),
              cell(rows[t]["he"])] for t in tags]

    if args.md:
        print("| " + " | ".join(head) + " |")
        print("|" + "---|" * len(head))
        for r in table:
            print("| " + " | ".join(r) + " |")
    else:
        w = [max(len(str(r[i])) for r in [head] + table) for i in range(len(head))]
        print("  ".join(h.ljust(w[i]) for i, h in enumerate(head)))
        print("  ".join("-" * w[i] for i in range(len(head))))
        for r in table:
            print("  ".join(str(c).ljust(w[i]) for i, c in enumerate(r)))

    missing = sum(1 for t in tags for k in ("tput", "mmlu_off", "mmlu_on", "he")
                  if rows[t][k] is None)
    print(f"\n{len(tags)} models, {len(tags) * 4 - missing}/{len(tags) * 4} cells filled.")
    print("— = never run. (p/n) = fewer answers parsed than asked; an unparsed answer scores")
    print("as incorrect, so those cells are FLOORS. cap:N / TMO:N / PART / RIG? per the header.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
