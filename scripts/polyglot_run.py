#!/usr/bin/env python3
"""Run Aider Polyglot exercises in a fixed order against a local llama.cpp router.

Runs INSIDE the aider-benchmark container (podman), because both modes execute code:

  validate  -- put each exercise's own reference solution in place and run the unit tests.
               Proves the test runner passes known-good code before any model is blamed for
               a failure. An exercise whose reference fails is broken infrastructure, not a
               hard problem, and is reported as such.
  run       -- one model, exercises [start, end) of the order file, stopping early when the
               next exercise would not finish before --deadline.

The scoring itself is aider's own benchmark.run_test(), imported and called UNMODIFIED, so
results are the same .aider.results.json files `benchmark.py --stats` reads. This file only
decides which exercises run, in what order, and when to stop.

Container paths: /aider (aider repo), /polyglot (exercises), /run (output), /scripts.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "/aider/benchmark")
import benchmark  # noqa: E402  (aider's harness)
from aider import models, sendchat  # noqa: E402
from aider.coders import base_coder  # noqa: E402

POLYGLOT = Path("/polyglot")


def log(fh, msg):
    line = f"[{time.strftime('%F %T')}] {msg}"
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def read_order(path, start, end):
    names = [ln.strip() for ln in Path(path).read_text().splitlines() if ln.strip()]
    return list(enumerate(names))[start:end]


def copy_exercise(rel, dest_root):
    dest = dest_root / rel
    if not dest.exists():
        shutil.copytree(POLYGLOT / rel, dest)
    return dest


# --------------------------------------------------------------------------- validate
def install_reference(ex_dir):
    """Copy .meta example files over the solution stubs. Returns the files replaced."""
    files = json.loads((ex_dir / ".meta/config.json").read_text())["files"]
    examples = files.get("example", [])
    placed = []
    for sol in files["solution"]:
        if sol.endswith(("CMakeLists.txt", "Cargo.toml")):
            continue
        suffix = Path(sol).suffix
        cands = [e for e in examples if e.endswith(suffix)]
        if len(cands) > 1:
            cands = [e for e in cands if Path(e).name == Path(sol).name]
        if len(cands) == 1:
            shutil.copy(ex_dir / cands[0], ex_dir / sol)
            placed.append(sol)
        # else: header-only reference (3 cpp exercises) -- the stub .cpp stays as shipped.
    # References may ship helper files with no stub of their own (java/bowling's Frame.java).
    # They go beside the first solution file with the same suffix.
    used = {e for e in examples if any(Path(e).name == Path(s).name or
            (Path(e).suffix == Path(s).suffix and len([x for x in examples if x.endswith(Path(s).suffix)]) == 1)
            for s in files["solution"])}
    for extra in sorted(set(examples) - used):
        home = next((s for s in files["solution"] if Path(s).suffix == Path(extra).suffix), None)
        if home:
            dest = ex_dir / Path(home).parent / Path(extra).name
            shutil.copy(ex_dir / extra, dest)
            placed.append(str(dest.relative_to(ex_dir)))
    return placed


def validate(args):
    out = Path(args.out)
    with open(out.with_suffix(".log"), "a") as fh, open(out, "a") as res:
        for idx, rel in read_order(args.order, args.start, args.end):
            with tempfile.TemporaryDirectory() as tmp:
                ex = copy_exercise(rel, Path(tmp))
                placed = install_reference(ex)
                cfg = json.loads((ex / ".meta/config.json").read_text())["files"]
                t0 = time.time()
                try:
                    err = benchmark.run_unit_tests(POLYGLOT, ex, ex / ".hist.md", cfg["test"])
                    ok = not err
                    detail = (err or "")[-400:]
                except Exception as exc:  # noqa: BLE001 -- timeouts included
                    ok, detail = False, f"{type(exc).__name__}: {exc}"[-400:]
                rec = {"idx": idx, "exercise": rel, "ref_passes": ok, "placed": placed,
                       "secs": round(time.time() - t0, 1), "detail": "" if ok else detail}
                res.write(json.dumps(rec) + "\n")
                res.flush()
                log(fh, f"{idx:3d} {'PASS' if ok else 'FAIL'} {rel} ({rec['secs']}s)")


# --------------------------------------------------------------------------- run
def run(args):
    out_root = Path(args.outdir)
    out_root.mkdir(parents=True, exist_ok=True)
    model_name = f"openai/{args.model_id}"

    models.register_litellm_models([args.metadata])
    models.register_models([args.settings])
    # benchmark.main() sets these to 24h so a run "never gives up". A dead router would
    # then hang the whole time budget; 10 minutes of retries is plenty for a local server.
    sendchat.RETRY_TIMEOUT = base_coder.RETRY_TIMEOUT = models.RETRY_TIMEOUT = 600

    progress = out_root / "progress.jsonl"
    est = args.est_secs
    dead_streak = 0
    with open(out_root / "driver.log", "a") as fh:
        log(fh, f"model={model_name} range=[{args.start},{args.end}) deadline="
                f"{time.strftime('%T', time.localtime(args.deadline))} est={est:.0f}s/exercise")
        for idx, rel in read_order(args.order, args.start, args.end):
            ex = out_root / rel
            if (ex / ".aider.results.json").exists():
                continue  # resumable: already scored
            left = args.deadline - time.time()
            if left < est:
                log(fh, f"STOP before #{idx}: {left:.0f}s left < {est:.0f}s estimate")
                break
            copy_exercise(rel, out_root)
            t0 = time.time()
            res = benchmark.run_test(
                POLYGLOT, ex, model_name, args.edit_format, args.tries,
                False, False, False, args.commit_hash, None, None, None,
            ) or {}
            wall = time.time() - t0
            outcomes = res.get("tests_outcomes", [])
            rec = {
                "idx": idx, "exercise": rel, "wall_s": round(wall, 1),
                "outcomes": outcomes, "pass": bool(outcomes and outcomes[-1]),
                "exception": "exception" in res,
                "completion_tokens": res.get("completion_tokens"),
                "prompt_tokens": res.get("prompt_tokens"),
                "malformed": res.get("num_malformed_responses"),
                "error_outputs": res.get("num_error_outputs"),
                "test_timeouts": res.get("test_timeouts"),
            }
            with open(progress, "a") as pf:
                pf.write(json.dumps(rec) + "\n")
            log(fh, f"#{idx:3d} {'PASS' if rec['pass'] else 'fail'} {outcomes} {rel} "
                    f"{wall:.0f}s tok={rec['completion_tokens']}")
            # Rolling estimate for the stop rule: never trust a single fast exercise.
            est = max(est * 0.7 + wall * 0.3, args.est_floor)

            # A model that has stopped serving produces exceptions or zero-token replies.
            # Four in a row is not a hard model -- it is a dead backend. Stop and say so.
            if rec["exception"] or not rec["completion_tokens"]:
                dead_streak += 1
                if dead_streak >= 4:
                    log(fh, "!!! ABORT: 4 consecutive exercises with no model output -- "
                            "backend not serving. This is NOT a score.")
                    sys.exit(3)
            else:
                dead_streak = 0
        log(fh, "done")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--order", required=True)
    v.add_argument("--start", type=int, default=0)
    v.add_argument("--end", type=int, default=None)
    v.add_argument("--out", required=True)
    r = sub.add_parser("run")
    r.add_argument("--order", required=True)
    r.add_argument("--model-id", required=True)
    r.add_argument("--outdir", required=True)
    r.add_argument("--settings", required=True)
    r.add_argument("--metadata", required=True)
    r.add_argument("--start", type=int, default=0)
    r.add_argument("--end", type=int, default=None)
    r.add_argument("--deadline", type=float, required=True, help="epoch seconds")
    r.add_argument("--est-secs", type=float, default=180.0)
    r.add_argument("--est-floor", type=float, default=30.0)
    r.add_argument("--edit-format", default="whole")
    r.add_argument("--tries", type=int, default=2)
    r.add_argument("--commit-hash", default="unknown")
    args = ap.parse_args()
    os.chdir("/run")
    validate(args) if args.mode == "validate" else run(args)


if __name__ == "__main__":
    main()
