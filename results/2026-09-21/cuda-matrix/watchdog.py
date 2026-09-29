#!/usr/bin/env python3
"""Kill benchmark runs that are provably going nowhere, and guard the production router.

WHY: a benchmark whose every request errors still runs to completion. On 2026-09-21
qwen3.6-35b-a3b-abliterated-vl spent 30 minutes failing all 164 HumanEval tasks on a
10-second retry loop, because the model could not load and nothing was watching. The
result was a tidy results.json holding 0.00%.

preflight_serves in lib.sh now stops that class at the door. This is the second line: it
catches a model that loads and then stops serving -- an OOM mid-run, a crashed child, a
router that lost its model -- which a preflight cannot see.

RULES, deliberately conservative. Killing a good run is worse than letting a bad one
continue, so a run is killed only when it has produced a meaningful number of failures and
ZERO successes:

    >= FAIL_FLOOR items attempted, all errored, none succeeded  ->  kill the harness

It also asserts the :8080 production router is the pid it was at startup, and stops itself
if that ever changes rather than risk acting during something it does not understand.

    watchdog.py <prod-pid> [poll-seconds]
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
LOG = RUN / "WATCHDOG.log"
FAIL_FLOOR = 12


def say(msg: str) -> None:
    line = f"[{time.strftime('%m-%d %T')}] watchdog: {msg}"
    print(line, flush=True)
    with LOG.open("a") as fh:
        fh.write(line + "\n")
    # Loud failures also go to the driver log, which is what a human actually reads.
    if "!!!" in msg:
        with (RUN / "driver.log").open("a") as fh:
            fh.write(line + "\n")


def port_pid(port: int) -> str:
    """Pid listening on a port, or "" if it could not be read.

    ss prints the pid INSIDE a users:((...)) blob -- users:(("llama-server",pid=123,fd=19))
    -- so it has to be searched for, not matched at the start of a token. Getting that
    wrong made the first version of this watchdog announce that the production router had
    vanished, 0.1s after starting, while it was serving normally.
    """
    try:
        out = subprocess.run(["ss", "-ltnpH", f"sport = :{port}"],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return ""
    m = re.search(r"pid=(\d+)", out)
    return m.group(1) if m else ""


def harness_pid_for(out_dir: Path) -> int | None:
    """The python process writing this output directory, found by exact cmdline match.

    Reads /proc directly instead of pgrep -f: a bare pattern match also matches this
    watchdog's own command line and anything else mentioning the path.
    """
    me = os.getpid()
    target = str(out_dir)
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if pid == me:
            continue
        try:
            argv = (entry / "cmdline").read_bytes().decode("utf-8", "replace").split("\0")
        except Exception:
            continue
        if any(a == target for a in argv) and any("benchmark.py" in a for a in argv):
            return pid
    return None


def inspect(d: Path) -> tuple[int, int] | None:
    """(errored, succeeded) for an in-progress run, or None if not in progress."""
    f = d / "results.json"
    if not f.is_file():
        return None
    try:
        p = json.loads(f.read_text())
    except Exception:
        return None                     # mid-write; try again next poll
    if (p.get("metadata") or {}).get("finished"):
        return None
    rows = p.get("results") or []
    batches = p.get("batches") or []
    if batches:                          # MMLU-Pro: one record per batch
        err = sum(1 for b in batches if str(b.get("error") or ""))
        ok = sum(1 for b in batches if not str(b.get("error") or "")
                 and int(b.get("eval_count") or 0) > 0)
        return err, ok
    err = sum(1 for r in rows if str(r.get("error") or ""))
    ok = sum(1 for r in rows if not str(r.get("error") or ""))
    return err, ok


def main() -> int:
    prod_pid = sys.argv[1] if len(sys.argv) > 1 else ""
    poll = int(sys.argv[2]) if len(sys.argv) > 2 else 45
    # Self-test before trusting the guard: prove the pid can actually be read, and that it
    # matches what the caller passed. A monitor that is wrong about its own baseline will
    # either fire constantly or never fire, and both look like "monitoring is on".
    seen = port_pid(8080)
    if not seen:
        say("!!! cannot read the :8080 pid at all -- production guard DISABLED. "
            "Run-failure detection continues.")
        prod_pid = ""
    elif prod_pid and seen != prod_pid:
        say(f"!!! :8080 pid is {seen}, not the {prod_pid} passed in. Refusing to start "
            f"with a baseline I cannot verify.")
        return 1
    elif not prod_pid:
        prod_pid = seen
        say(f"no pid passed; adopting the running :8080 pid {seen} as the baseline")
    say(f"started; guarding :8080 pid={prod_pid or 'DISABLED'}, polling every {poll}s, "
        f"kill rule = {FAIL_FLOOR}+ attempts with zero successes")
    killed: set[str] = set()
    while True:
        now = port_pid(8080)
        # "" means the read failed; only a DIFFERENT pid means production actually moved.
        if prod_pid and now and now != prod_pid:
            say(f"!!! PRODUCTION ROUTER CHANGED on :8080 ({prod_pid} -> {now or 'GONE'}). "
                f"Stopping rather than acting blind.")
            return 1
        for d in sorted(RUN.iterdir()):
            if not d.is_dir() or str(d) in killed:
                continue
            got = inspect(d)
            if not got:
                continue
            err, ok = got
            if err >= FAIL_FLOOR and ok == 0:
                pid = harness_pid_for(d)
                say(f"!!! {d.name}: {err} attempts, ZERO successes -- this run cannot "
                    f"produce a result. Killing harness pid={pid}.")
                say(f"!!!   Check router-8081.log; a load error here means the model is "
                    f"UNRUNNABLE on this build, not that it scored zero.")
                if pid:
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                killed.add(str(d))
        time.sleep(poll)


if __name__ == "__main__":
    raise SystemExit(main())
