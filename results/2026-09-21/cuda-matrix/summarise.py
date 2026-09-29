#!/usr/bin/env python3
"""Print the CUDA matrix as it stands: one row per model, one column per measurement.

Reads whatever is on disk in this directory, so it is safe to run mid-sweep. A cell is
blank when the run has not happened, and carries a marker when the run happened but is
not a result:

    RIG?   sub-minute wall clock -- treat as a rig failure, not a model result
    0tok   zero generated tokens -- every request errored
    PART   fewer items than the run asked for -- interrupted, not a result
    cap:N  N thinking batches hit the num_predict cap and scored 0; the figure is a FLOOR
    TMO:N  N batches hit the client timeout -- rig failure, raise --api-timeout
"""
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent


def read(d: Path, np_cap: int | None = None) -> dict | None:
    f = d / "results.json"
    if not f.is_file():
        return None
    try:
        payload = json.loads(f.read_text())
    except Exception as exc:
        return {"bad": f"UNREADABLE {exc}"}
    s = payload["model_summaries"][0]
    batches = payload.get("batches") or []
    meta = payload.get("metadata") or {}
    # The harness re-saves results.json after EVERY batch, so a run in progress leaves a
    # perfectly well-formed file holding a partial score. Read mid-sweep, that looks like
    # a finished result and is wrong by however much of the sample is still missing --
    # the first snapshot of this matrix showed 82.86% for a run that was 8 batches in.
    # `finished` is written only in the run's finally block, so its absence is the tell.
    expected = None
    if meta.get("settings", {}).get("per_category") and meta.get("categories"):
        expected = meta["settings"]["per_category"] * len(meta["categories"])
    running = not meta.get("finished")
    out = {
        "acc": s.get("pass_at_1", s.get("accuracy")),
        "n": s.get("attempted", s.get("total")),
        "parsed": s.get("parsed", s.get("passed")),
        "tps": s.get("generation_tps") or 0,
        "wall": (s.get("wall_seconds") or 0) / 60,
        "tok": sum(int(b.get("eval_count") or 0) for b in batches),
        "flags": [],
    }
    if batches:
        if np_cap:
            capped = [b for b in batches if int(b.get("eval_count") or 0) >= np_cap - 8]
            if capped:
                out["flags"].append(f"cap:{len(capped)}")
        tmo = [b for b in batches if "Timeout" in str(b.get("error") or "")]
        if tmo:
            out["flags"].append(f"TMO:{len(tmo)}")
        if out["tok"] == 0 and np_cap:
            out["flags"].append("0tok")
    # A benchmark that finished in under a minute did not run; the usual cause is the
    # router 500ing every request, which still writes a tidy 0.00% results.json.
    if out["wall"] < 1.0:
        out["flags"].append("RIG?")
    if running:
        out["flags"].append(f"PART:{out['n']}/{expected}" if expected else "PART")
    elif expected and out["n"] != expected:
        out["flags"].append(f"PART:{out['n']}/{expected}")
    return out


def cell(r: dict | None, show_tps: bool = False) -> str:
    if r is None:
        return "-"
    if "bad" in r:
        return r["bad"]
    txt = f"{r['acc']:.2f}"
    if r["parsed"] is not None and r["n"] and r["parsed"] < r["n"]:
        txt += f" ({r['parsed']}/{r['n']})"
    if show_tps and r["tps"]:
        txt += f" @{r['tps']:.1f}"
    if r["flags"]:
        txt += " " + ",".join(r["flags"])
    return txt


def throughput(slug: str) -> str:
    """Range across the four speed tests, as the round-2 reports quote it."""
    f = RUN / "throughput" / f"{slug}.json"
    if not f.is_file():
        return "-"
    try:
        by = json.loads(f.read_text())["summary"]["by_model_test"]
        tests = next(iter(by.values()))          # exactly one model per file here
        vals = [t["avg_score_tok_per_sec"] for t in tests.values()
                if t.get("avg_score_tok_per_sec")]
        if not vals:
            return "?"
        return f"{min(vals):.1f}" if max(vals) - min(vals) < 0.05 else f"{min(vals):.1f}-{max(vals):.1f}"
    except Exception as exc:
        return f"ERR {type(exc).__name__}"


def discover() -> list[str]:
    slugs = set()
    for d in RUN.iterdir():
        if not d.is_dir():
            continue
        n = d.name
        for pre in ("mmlu-", "humaneval-"):
            if n.startswith(pre):
                rest = n[len(pre):]
                for suf in ("-pc5-np96", "-pc5-np2048", "-pc20-np96", "-pc20-np2048"):
                    if rest.endswith(suf):
                        rest = rest[: -len(suf)]
                        break
                else:
                    if "-think" in rest:
                        rest = rest.split("-think")[0]
                slugs.add(rest)
    for f in (RUN / "throughput").glob("*.json"):
        slugs.add(f.stem)
    return sorted(slugs)


def main() -> int:
    pc = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    slugs = discover()
    if not slugs:
        print("no runs on disk yet")
        return 0
    hdr = f"{'model (slug)':<20} {'tok/s':>11} {'MMLU-off@' + str(pc):>22} {'MMLU-ON@' + str(pc):>26} {'HumanEval':>20}"
    print(hdr)
    print("-" * len(hdr))
    for slug in slugs:
        off = read(RUN / f"mmlu-{slug}-pc{pc}-np2048") or read(RUN / f"mmlu-{slug}-pc{pc}-np96")
        on = None
        for d in sorted(RUN.glob(f"mmlu-{slug}-pc{pc}-think*")):
            cap = int(d.name.split("think")[-1])
            on = read(d, np_cap=cap)
        he = read(RUN / f"humaneval-{slug}")
        print(f"{slug:<20} {throughput(slug):>11} {cell(off):>22} {cell(on, True):>26} {cell(he):>20}")
    print()
    print("blank = not run. Figures with (p/n) parsed fewer items than were asked;")
    print("an unparsed answer scores as incorrect, so those cells are FLOORS, not scores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
