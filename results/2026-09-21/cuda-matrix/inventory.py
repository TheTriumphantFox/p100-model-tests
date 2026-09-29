#!/usr/bin/env python3
"""Every benchmark run on disk across all three rounds, with its settings and provenance.

The matrix collapses each model to four cells; this is the layer under it. Use it to see
exactly which file produced a number, at what settings, and whether it finished.
"""
from __future__ import annotations

import json
from pathlib import Path

TESTS = Path(__file__).resolve().parents[2]
SOURCES = [
    ("2026-09-21/cuda-matrix", TESTS / "2026-09-21" / "cuda-matrix"),
    ("2026-09-19/candidates-round2", TESTS / "2026-09-19" / "candidates-round2"),
    ("2026-09-19/candidates", TESTS / "2026-09-19" / "candidates"),
]


def rows():
    for label, src in SOURCES:
        if not src.is_dir():
            continue
        for d in sorted(src.iterdir()):
            if not d.is_dir() or not (d / "results.json").is_file():
                continue
            try:
                p = json.loads((d / "results.json").read_text())
            except Exception as exc:
                yield dict(where=label, run=d.name, tag="?", note=f"UNREADABLE {exc}")
                continue
            res = p.get("results") or []
            sm = p.get("model_summaries") or []
            if not res or not sm:
                continue
            s, meta = sm[0], p.get("metadata") or {}
            cfg = meta.get("settings") or {}
            batches = p.get("batches") or []
            tok = sum(int(b.get("eval_count") or 0) for b in batches)
            errs = sum(1 for b in batches if str(b.get("error") or ""))
            kind = "HumanEval" if "pass_at_1" in s else ("MMLU-ON" if "think" in d.name else "MMLU-off")
            note = []
            if not meta.get("finished"):
                note.append("UNFINISHED")
            if batches and (tok == 0 or errs == len(batches)):
                note.append(f"RIG-FAIL({errs}/{len(batches)} batches errored)")
            elif errs:
                note.append(f"{errs} batch errors")
            np_ = cfg.get("num_predict")
            if np_ and batches:
                cap = sum(1 for b in batches if int(b.get("eval_count") or 0) >= np_ - 8)
                if cap:
                    note.append(f"cap:{cap}")
            yield dict(
                where=label, run=d.name, tag=s.get("name") or res[0].get("model"), kind=kind,
                score=s.get("pass_at_1", s.get("accuracy")),
                n=s.get("attempted", s.get("total")),
                pc=cfg.get("per_category"), bs=cfg.get("batch_size"), seed=cfg.get("seed"),
                ctx=cfg.get("num_ctx"), np=np_, cats=cfg.get("categories_arg", "all"),
                tps=s.get("generation_tps") or 0, wall=(s.get("wall_seconds") or 0) / 60,
                tok=tok, started=(meta.get("started") or "")[:16],
                note=", ".join(note),
            )


def main() -> int:
    data = sorted(rows(), key=lambda r: (r.get("tag") or "", r.get("kind") or "", r.get("run") or ""))
    hdr = f"{'model tag':<40} {'kind':<10} {'score':>7} {'n':>4} {'pc':>3} {'bs':>3} {'ctx':>6} {'npred':>6} {'tok':>7} {'tok/s':>6} {'min':>6}  run"
    print(hdr); print("-" * len(hdr))
    for r in data:
        if r.get("note", "").startswith("UNREADABLE"):
            print(f"{r['run']:<40} {r['note']}")
            continue
        print(f"{r['tag']:<40} {r['kind']:<10} {r['score']:>7.2f} {r['n']:>4} "
              f"{str(r['pc'] or '-'):>3} {str(r['bs'] or r['pc'] or '-'):>3} {str(r['ctx'] or '-'):>6} "
              f"{str(r['np'] or '-'):>6} {r['tok']:>7} {r['tps']:>6.1f} {r['wall']:>6.1f}  "
              f"{r['where']}/{r['run']}")
        extra = []
        if r["note"]:
            extra.append(r["note"])
        if r["cats"] not in ("all", None):
            extra.append(f"categories={r['cats']}")
        if extra:
            print(f"{'':<40} -> {'; '.join(extra)}")
    print(f"\n{len(data)} runs on disk. pc = --per-category, bs = questions per request,")
    print("npred = num_predict, tok = total generated tokens across all batches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
