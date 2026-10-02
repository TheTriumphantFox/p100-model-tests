#!/usr/bin/env python3
"""Negative control for the test runner: the UNSOLVED stubs must fail.

Runs aider's run_unit_tests on the shipped stub of exercises [start, end) of the order and
prints the tail of what the test command actually printed, so a runner that silently passes
everything (wrong cwd, no tests collected, a test command that exits 0) shows up here.
Run inside the aider-benchmark container.
"""
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "/aider/benchmark")
sys.path.insert(0, "/scripts")
import benchmark  # noqa: E402
from polyglot_run import POLYGLOT, copy_exercise, read_order  # noqa: E402

start, end = int(sys.argv[1]), int(sys.argv[2])
for idx, rel in read_order("/run/order.txt", start, end):
    with tempfile.TemporaryDirectory() as tmp:
        ex = copy_exercise(rel, Path(tmp))
        cfg = json.loads((ex / ".meta/config.json").read_text())["files"]
        t0 = time.time()
        try:
            err = benchmark.run_unit_tests(POLYGLOT, ex, ex / ".hist.md", cfg["test"])
        except Exception as exc:  # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
        tail = " | ".join((err or "").strip().splitlines()[-2:])[:160]
        print(f"NEG {idx:3d} {'stub FAILS (good)' if err else 'stub PASSES (BAD)'} "
              f"{time.time() - t0:5.1f}s {rel} :: {tail}", flush=True)
