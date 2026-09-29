#!/usr/bin/env python3
"""Aggregate the per-model tau-bench retail runs into one comparison table."""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter

RUN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RUN, "..", "..", "tools", "tau_bench"))
sys.path.insert(0, RUN)  # tau_bench ships its own run.py; ours must win

from run import ASKING  # noqa: E402  -- same classifier the `confirm` policy uses

ORDER = ["devstral", "gptoss", "qwen36", "qwen38unsloth", "qwen38unc", "g9v3"]

# The retail tools that change the database. The policy requires an explicit
# "yes" from the user before any of them.
WRITE_TOOLS = frozenset({
    "cancel_pending_order",
    "exchange_delivered_order_items",
    "modify_pending_order_address",
    "modify_pending_order_items",
    "modify_pending_order_payment",
    "modify_user_address",
    "return_delivered_order_items",
})
YES = re.compile(r"\byes\b", re.I)


def tool_calls(r):
    """(name, args) for every tool call in the transcript, in order."""
    for m in r["messages"]:
        for c in m.get("tool_calls") or []:
            try:
                args = json.loads(c["function"]["arguments"] or "{}")
            except (ValueError, TypeError):
                args = {}
            yield c["function"]["name"], args if isinstance(args, dict) else {}


def unconfirmed_writes(r):
    """Write calls issued before any user turn said "yes".

    The task instruction is removed from each user turn before matching, so a
    "yes" inside the restated instruction does not count as a confirmation.
    """
    users = [m for m in r["messages"] if m["role"] == "user"]
    instruction = users[0]["content"] if users else ""
    confirmed, n = False, 0
    for m in r["messages"]:
        if m["role"] == "user" and m is not users[0]:
            if YES.search((m["content"] or "").replace(instruction, "")):
                confirmed = True
        for c in m.get("tool_calls") or []:
            if c["function"]["name"] in WRITE_TOOLS and not confirmed:
                n += 1
    return n


def duplicate_writes(r):
    """Write calls that repeat an earlier write with identical arguments."""
    seen, n = set(), 0
    for name, args in tool_calls(r):
        if name in WRITE_TOOLS:
            key = (name, json.dumps(args, sort_keys=True))
            n += key in seen
            seen.add(key)
    return n


def excess_writes(r, task):
    """Writes beyond the number the ground truth makes for this task."""
    gt = sum(a.name in WRITE_TOOLS for a in task.actions)
    return max(0, sum(n in WRITE_TOOLS for n, _ in tool_calls(r)) - gt)


def stall_kind(r, task):
    """Why a failed task made no write when it needed one, or None.

    `lookup` -- never opened any order the ground truth acts on (or, for a task
                with no order, never called get_user_details). It could not have
                acted correctly whatever the user said: a model failure.
    `asking` -- found the right order, then ended on a question. The only kind
                the scripted user can be blamed for.
    `silent` -- found the right order and simply stopped.
    """
    if r["reward"] == 1.0 or r["error"] or not r["done"]:
        return None
    gt_writes = [a for a in task.actions if a.name in WRITE_TOOLS]
    calls = list(tool_calls(r))
    if not gt_writes or any(n in WRITE_TOOLS for n, _ in calls):
        return None
    targets = {a.kwargs["order_id"] for a in gt_writes if "order_id" in a.kwargs}
    if targets:
        opened = {a.get("order_id") for n, a in calls if n == "get_order_details"}
        found = bool(targets & opened)
    else:
        found = any(n == "get_user_details" for n, _ in calls)
    if not found:
        return "lookup"
    last = [m for m in r["messages"] if m["role"] == "assistant" and m.get("content")]
    return "asking" if last and ASKING.search(last[-1]["content"]) else "silent"


def load():
    out = {}
    for f in glob.glob(os.path.join(RUN, "retail_*.json")):
        slug = os.path.basename(f)[len("retail_") : -len(".json")]
        try:
            out[slug] = json.load(open(f))
        except Exception as e:
            print(f"  !! {slug}: unreadable ({e})")
    return out


def main():
    runs = load()
    if not runs:
        print("no retail_*.json found")
        return 0

    try:
        from tau_bench.envs.retail.tasks_test import TASKS_TEST
    except Exception:
        TASKS_TEST = None

    rows = []
    for slug in ORDER + [s for s in runs if s not in ORDER]:
        if slug not in runs:
            continue
        rs = runs[slug]["results"]
        n = len(rs)
        if not n:
            continue
        passed = sum(1 for r in rs if r["reward"] == 1.0)
        unterm = sum(1 for r in rs if not r["done"])
        errs = sum(1 for r in rs if r["error"])
        pf = sum(len(r["parse_failures"]) for r in rs)
        steps = sum(r["steps"] for r in rs) / n
        lat = [r["mean_latency_s"] for r in rs if r["mean_latency_s"]]
        wall = sum(r["wall_s"] for r in rs)
        stalls = Counter(stall_kind(r, TASKS_TEST[r["task_index"]]) for r in rs) if TASKS_TEST else Counter()
        uw = [unconfirmed_writes(r) for r in rs]
        rows.append(
            {
                "model": slug,
                "n": n,
                "pass": passed,
                "pct": 100 * passed / n,
                "parse_fail": pf,
                "unterm": unterm,
                "errors": errs,
                "mean_steps": steps,
                "mean_lat": sum(lat) / len(lat) if lat else 0,
                "hours": wall / 3600,
                "lookup": stalls["lookup"],
                "asking": stalls["asking"],
                "silent": stalls["silent"],
                "ceiling": 100 * (passed + stalls["asking"]) / n,
                "writes": sum(1 for r in rs for c, _ in tool_calls(r) if c in WRITE_TOOLS),
                "unconf": sum(uw),
                "pass_unconf": sum(1 for r, u in zip(rs, uw) if r["reward"] == 1.0 and u),
                "excess": sum(excess_writes(r, TASKS_TEST[r["task_index"]]) for r in rs) if TASKS_TEST else 0,
                "dups": sum(duplicate_writes(r) for r in rs),
                "dup_tasks": sum(1 for r in rs if duplicate_writes(r)),
            }
        )

    w = max(len(r["model"]) for r in rows) + 1
    print(f"\n{'model':<{w}} {'n':>4} {'pass':>6} {'%':>7} {'parsefail':>10}"
          f" {'unterm':>7} {'err':>4} {'steps':>6} {'lat s':>7} {'hours':>6}")
    print("-" * (w + 62))
    for r in rows:
        print(
            f"{r['model']:<{w}} {r['n']:>4} {r['pass']:>6} {r['pct']:>6.1f}%"
            f" {r['parse_fail']:>10} {r['unterm']:>7} {r['errors']:>4}"
            f" {r['mean_steps']:>6.1f} {r['mean_lat']:>7.1f} {r['hours']:>6.2f}"
        )

    if TASKS_TEST:
        # A scripted user cannot answer a question, so a model that stops to ask
        # scores zero. Only `asking` stalls are the harness's fault; `lookup`
        # stalls never found the order and would have failed anyway.
        print(f"\n{'model':<{w}} {'stall:lookup':>13} {'asking':>7} {'silent':>7}"
              f" {'ceiling':>8}   {'writes':>7} {'no yes':>7} {'passes w/o yes':>15}")
        print("-" * (w + 72))
        for r in rows:
            print(
                f"{r['model']:<{w}} {r['lookup']:>13} {r['asking']:>7} {r['silent']:>7}"
                f" {r['ceiling']:>7.1f}%   {r['writes']:>7} {r['unconf']:>7}"
                f" {r['pass_unconf']:>11}/{r['pass']:<3}"
            )
        print("ceiling = (pass + asking stalls) / n, an upper bound."
              " 'no yes' = writes issued before any user turn said yes.")
        print(f"\n{'model':<{w}} {'writes':>7} {'beyond gt':>10} {'dup writes':>11} {'in tasks':>9}")
        print("-" * (w + 40))
        for r in rows:
            print(f"{r['model']:<{w}} {r['writes']:>7} {r['excess']:>10} {r['dups']:>11} {r['dup_tasks']:>9}")
        print("beyond gt = per-task writes over the ground-truth count, summed."
              " dup = identical name+args repeated.")

    # Which tasks did everyone miss? Those are benchmark-hard, not model-specific.
    if len(rows) > 1:
        full = {s: {r["task_index"] for r in runs[s]["results"] if r["reward"] == 1.0}
                for s in runs}
        allidx = {r["task_index"] for s in runs for r in runs[s]["results"]}
        never = sorted(i for i in allidx if not any(i in v for v in full.values()))
        always = sorted(i for i in allidx if all(i in v for v in full.values()))
        print(f"\nsolved by every model : {len(always)}")
        print(f"solved by no model    : {len(never)}")
        if never and TASKS_TEST:
            req = Counter()
            for i in never:
                if i < len(TASKS_TEST):
                    for o in TASKS_TEST[i].outputs:
                        req[o] += 1
            if req:
                print(f"  required outputs among universally-failed tasks: {dict(req.most_common(8))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
