#!/usr/bin/env python3
"""Devstral on tau-bench retail, with deterministic scripted user turns.

tau-bench normally drives the customer side with a frontier LLM. No metered API
key is configured on this box and the only ready provider is a ChatGPT consumer
OAuth credential, which is not a legitimate batch-inference backend. So the user
side is scripted instead: the task instruction is handed over in full on turn 1
and every later user turn is a fixed, information-free nudge.

That makes this EASIER than published tau-bench: the agent never has to extract
requirements through dialogue. Scores here are NOT comparable to the
leaderboard. What it does isolate -- and what actually matters for judging
Devstral as a planner -- is tool selection, argument correctness, policy
compliance and multi-step recovery.

Scoring is tau-bench's own: replay the task's ground-truth actions against a
fresh database, hash it, and compare against the hash of the database the agent
actually produced. Partial credit does not exist.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request

TAU = Path(__file__).resolve().parents[2] / "tools" / "tau_bench"
sys.path.insert(0, str(TAU))

from tau_bench.envs.retail import MockRetailDomainEnv  # noqa: E402
from tau_bench.envs.user import BaseUserSimulationEnv  # noqa: E402
from tau_bench.types import Action, RESPOND_ACTION_NAME  # noqa: E402


# A model that pauses to ask "Option A or B? confirm the card?" gets no answer
# from the `nudge` policy, never mutates, and scores zero however good its tool
# use was. That penalty is uneven -- on the 2026-09-22 run it accounted for 9.3%
# of devstral's failures but 22.2% of gpt-oss's -- so the ranking partly measured
# willingness to act rather than competence. (Stalls where the model never found
# the order are not counted here; see stall_kind() in summarise.py.)
ASKING = re.compile(
    r"\?\s*$|confirm|would you like|shall i|which option|before i (can )?(proceed|complete)"
    r"|need your|let me know|please provide|can you (confirm|tell me)|may i",
    re.I,
)


class ScriptedUser(BaseUserSimulationEnv):
    """Deterministic customer, in one of two policies.

    `nudge`   -- says everything up front, then adds nothing. Cannot answer a
                 question, so it scores cautious models as failures.
    `confirm` -- additionally answers a confirmation request affirmatively and
                 re-states the instruction, so a model that asks permission can
                 proceed.

    MEASURED RESULT, devstral tasks 40-63 (2026-09-23): `confirm` eliminates the
    stall confound completely (5 stalls -> 0) and does NOT improve fidelity. It
    trades one bias for another. Extra user turns push models to act more, so
    mutation counts rise across the board, and spurious mutations cost about as
    many tasks as the recovered stalls gain:

        nudge    14/24 pass, 5 stalled,  98s/task
        confirm  15/24 pass, 0 stalled, 147s/task  (+40,45,55,58  -56,60,62)

    On 51-63 alone confirm is a net LOSS (7/13 -> 6/13). Task 62, whose correct
    behaviour is to change nothing, goes from passing to issuing a spurious
    cancel_pending_order. Narrowing the wording to explicitly refuse a wider
    mandate made task 62 worse, not better (two spurious mutations instead of
    one) -- the driver is the extra turn itself, not the words in it.

    So `nudge` remains the default and the published numbers stand. Report pass
    rate and stall rate as two metrics rather than trusting either policy alone.

    The structural fix is a real user simulator: a canned reply cannot tell "yes,
    do the thing you asked about" from "no, that is outside my request". That
    needs an LLM in the user role.

    Neither policy leaks ground truth. The only thing restated is the task
    instruction the agent already received on turn 1.
    """

    def __init__(self, max_turns: int = 2, policy: str = "nudge") -> None:
        self.max_turns = max_turns
        self.policy = policy
        self.instruction = ""
        self.turns = 0

    def reset(self, instruction: Optional[str] = None) -> str:
        self.instruction = instruction or ""
        self.turns = 0
        return self.instruction

    def step(self, content: str) -> str:
        self.turns += 1
        if self.turns > self.max_turns:
            return "###STOP###"
        if self.turns == 1:
            return (
                "To restate what I need: "
                f"{self.instruction}\n\n"
                "Please go ahead and complete it."
            )
        if self.policy == "confirm" and ASKING.search(content or ""):
            # Deliberately NOT a blanket authorization. An earlier version said
            # "you have my confirmation for the whole request", which on task 62
            # -- whose correct behaviour is to change nothing -- talked the agent
            # into a cancel_pending_order it should never have made. Answering
            # the question must not widen the mandate.
            return (
                "Decide that yourself, based on exactly what I asked for - I'm not "
                "adding anything to my original request, and I don't want anything "
                "done beyond it. If what I asked for doesn't require a change, don't "
                "make one. Otherwise go ahead without checking back.\n\n"
                f"What I asked for was: {self.instruction}"
            )
        return "I have nothing further to add. Please complete the request."

    def get_total_cost(self) -> float:
        return 0.0


class DevstralAgent:
    """tau-bench ToolCallingAgent, pointed at the local llama.cpp router."""

    def __init__(
        self,
        url: str,
        model: str,
        temperature: float = 0.0,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.url = url
        self.model = model
        self.temperature = temperature
        self.extra_body = extra_body or {}

    def complete(
        self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]
    ) -> tuple[Dict[str, Any], float, Dict[str, Any]]:
        body = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "temperature": self.temperature,
                **self.extra_body,
            }
        ).encode()
        req = urllib.request.Request(
            self.url, data=body, headers={"Content-Type": "application/json"}
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=900) as r:
            payload = json.load(r)
        return (
            payload["choices"][0]["message"],
            time.time() - t0,
            payload.get("usage", {}),
        )


def message_to_action(message: Dict[str, Any]) -> tuple[Action, Optional[str]]:
    """Mirror tau-bench's mapping. Second value is a parse-failure reason."""
    calls = message.get("tool_calls")
    if calls and calls[0].get("function"):
        fn = calls[0]["function"]
        raw = fn.get("arguments") or "{}"
        try:
            kwargs = json.loads(raw)
        except json.JSONDecodeError as e:
            return (
                Action(name=RESPOND_ACTION_NAME, kwargs={"content": ""}),
                f"bad_json_arguments: {e}: {raw[:200]!r}",
            )
        if not isinstance(kwargs, dict):
            return (
                Action(name=RESPOND_ACTION_NAME, kwargs={"content": ""}),
                f"arguments_not_object: {raw[:200]!r}",
            )
        return Action(name=fn["name"], kwargs=kwargs), None
    return Action(
        name=RESPOND_ACTION_NAME, kwargs={"content": message.get("content") or ""}
    ), None


def run_task(env, agent: DevstralAgent, index: int, max_steps: int) -> Dict[str, Any]:
    reset = env.reset(task_index=index)
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": env.wiki},
        {"role": "user", "content": reset.observation},
    ]
    latencies: List[float] = []
    parse_failures: List[str] = []
    tool_calls: List[str] = []
    reward = 0.0
    done = False
    t0 = time.time()
    err = None

    for _ in range(max_steps):
        try:
            msg, dt, usage = agent.complete(messages, env.tools_info)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            err = f"{type(e).__name__}: {e}"
            break
        latencies.append(dt)
        action, failure = message_to_action(msg)
        if failure:
            parse_failures.append(failure)
        if action.name != RESPOND_ACTION_NAME:
            tool_calls.append(action.name)

        resp = env.step(action)
        reward = resp.reward
        done = resp.done

        if action.name != RESPOND_ACTION_NAME:
            call = msg["tool_calls"][0]
            messages.append({**msg, "tool_calls": [call]})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id", "call_0"),
                    "name": call["function"]["name"],
                    "content": resp.observation,
                }
            )
        else:
            messages.append({"role": "assistant", "content": msg.get("content") or ""})
            messages.append({"role": "user", "content": resp.observation})

        if done:
            break

    wall = time.time() - t0
    # tau-bench only scores a terminated conversation. Score an unterminated one
    # too, so "ran out of steps" is distinguishable from "wrong final state".
    diagnostic = reward
    if not done and err is None:
        try:
            diagnostic = env.calculate_reward().reward
        except Exception:
            diagnostic = 0.0

    return {
        "task_index": index,
        "reward": reward,
        "diagnostic_reward": diagnostic,
        "done": done,
        "error": err,
        "steps": len(latencies),
        "wall_s": round(wall, 1),
        "mean_latency_s": round(sum(latencies) / len(latencies), 2) if latencies else None,
        "tool_calls": tool_calls,
        "parse_failures": parse_failures,
        "gt_actions": [a.name for a in env.task.actions],
        "messages": messages,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8080/v1/chat/completions")
    p.add_argument("--model", default="devstral-cuda")
    p.add_argument("--tasks", type=int, default=5, help="how many tasks to run")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--max-steps", type=int, default=30)
    p.add_argument(
        "--user-policy",
        choices=["nudge", "confirm"],
        default="nudge",
        help="nudge: customer adds nothing after turn 1 (the 2026-09-22 runs). "
        "confirm: also answers a confirmation request affirmatively, so a model "
        "that asks permission is not scored as a failure for asking.",
    )
    p.add_argument(
        "--max-user-turns",
        type=int,
        default=None,
        help="default 2 for --user-policy nudge, 6 for confirm (which needs "
        "more back-and-forth).",
    )
    p.add_argument("--out", default=None)
    p.add_argument(
        "--extra-body",
        default=None,
        help='JSON merged into each request, e.g. \'{"chat_template_kwargs":'
        ' {"enable_thinking": false}}\'',
    )
    args = p.parse_args()

    extra = json.loads(args.extra_body) if args.extra_body else {}
    env = MockRetailDomainEnv(user_strategy="human", task_split="test")
    turns = args.max_user_turns
    if turns is None:
        turns = 6 if args.user_policy == "confirm" else 2
    env.user = ScriptedUser(max_turns=turns, policy=args.user_policy)
    agent = DevstralAgent(args.url, args.model, extra_body=extra)

    out = Path(args.out) if args.out else Path(__file__).parent / (
        f"run_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    )
    results: List[Dict[str, Any]] = []
    t0 = time.time()

    for i in range(args.start, args.start + args.tasks):
        if i >= len(env.tasks):
            break
        r = run_task(env, agent, i, args.max_steps)
        results.append(r)
        flag = "PASS" if r["reward"] == 1.0 else "fail"
        extra = ""
        if r["error"]:
            extra = f" ERROR {r['error']}"
        elif not r["done"]:
            extra = " (unterminated)"
        elif r["parse_failures"]:
            extra = f" ({len(r['parse_failures'])} parse fail)"
        print(
            f"[{i:>3}] {flag}  steps={r['steps']:>2}  {r['wall_s']:>6.1f}s"
            f"  tools={len(r['tool_calls'])}{extra}",
            flush=True,
        )
        out.write_text(
            json.dumps(
                {
                    "config": vars(args),
                    "elapsed_s": round(time.time() - t0, 1),
                    "results": results,
                },
                indent=1,
            )
        )

    n = len(results)
    if n:
        passed = sum(1 for r in results if r["reward"] == 1.0)
        diag = sum(1 for r in results if r["diagnostic_reward"] == 1.0)
        unterm = sum(1 for r in results if not r["done"])
        pf = sum(len(r["parse_failures"]) for r in results)
        print(
            f"\npass {passed}/{n} ({100*passed/n:.1f}%)   "
            f"correct-state incl. unterminated {diag}/{n}   "
            f"unterminated {unterm}   parse failures {pf}"
        )
        print(f"total {time.time()-t0:.0f}s   ->  {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
