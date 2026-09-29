#!/usr/bin/env python3
"""CPU-only proof that the rig classifies what it claims to. Run before any GPU time.

1. Controller unit checks: strict parsing traps, pinned grammar shape, edit
   expectations, reporter scoring.
2. Every mock config over every scenario: a perfect stack must score perfectly,
   and each deliberately broken stack must fail in exactly its intended way.
3. The real HTTP path (one-shot, tool loop, reviewer, reporter, cache) against
   a fake OpenAI-compatible server on a local port.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import controller as C
import flow
import models
import report
import roles
import rig

FAILS = []


def check(cond: bool, what: str) -> None:
    if not cond:
        FAILS.append(what)
        print("FAIL", what)


# ------------------------------------------------------------------ 1. units


def units() -> None:
    for bad in ('{"a": NaN}', '{"a": 1, "a": 2}', '{"a": 1.0}'):
        try:
            C.strict_loads(bad)
            check(False, f"strict_loads accepted {bad}")
        except ValueError:
            pass
    h = [{"handle_id": C.derive_handle("x", "1"), "kind": "service_config", "label": "a", "content": "{}\n", "path": "a"},
         {"handle_id": C.derive_handle("x", "2"), "kind": "activation_state", "label": "b", "content": "{}\n", "path": "b"},
         {"handle_id": C.derive_handle("x", "3"), "kind": "context", "label": "c", "content": "note", "path": "c"}]
    s = C.response_schema(h, pin=True)
    branches = s["properties"]["calls"]["oneOf"]
    check(len(branches) == 2, "pinned grammar: one branch per writable handle")
    check(all("items" not in b and b["minItems"] == b["maxItems"] == len(b["prefixItems"]) for b in branches),
          "pinned grammar: prefixItems only, fixed length")
    check(branches[0]["prefixItems"][0]["properties"]["file_handle"] == {"const": h[0]["handle_id"]},
          "pinned grammar: handle is a constant")
    check("pattern" in branches[0]["prefixItems"][0]["properties"]["expected_old_hash"], "hash is never pinned")
    check(all(C.HANDLE_RE.match(x["handle_id"]) for x in h), "derived handles match the handle pattern")
    proj = C.projection(h)
    check(proj[0]["ends_with_newline"] is True and proj[2]["ends_with_newline"] is False, "projection shows the final LF")

    lab = C.Lab({"s": {"kind": "service_config", "label": "s", "content": C.dumps({"listen": {"port": 1}})},
                 "t": {"kind": "activation_state", "label": "t", "content": C.dumps({"generation": 4, "config_hash": "x"})}})
    out = C.apply_edits(lab.content("t"), [["set", ["config_hash"], "$hash:s"], ["set", ["generation"], "$inc"]], lab)
    check(json.loads(out) == {"generation": 5, "config_hash": lab.hash("s")}, "edit expectations resolve $hash and $inc")

    orig = C.dumps({"listen": {"port": 8080}, "upstreams": [{"name": "a", "host": "a"}, {"name": "b", "host": "b"}]})
    new = C.dumps({"listen": {"port": 8081}, "upstreams": [{"name": "a", "host": "a"}]})
    good = {"changes": [{"field": "listen.port", "from": "8080", "to": "8081"},
                        {"field": "upstreams[name=b]", "from": "{...}", "to": "(absent)"}], "recommendation": "approve"}
    sc = roles.score_report(good, orig, new)
    check(sc["missed"] == [] and sc["phantom"] == 0, f"reporter scoring: complete report scores clean ({sc})")
    bad = {"changes": [{"field": "listen.port", "from": "8080", "to": "8081"},
                       {"field": "tls.enabled", "from": "true", "to": "false"}], "recommendation": "approve"}
    sc = roles.score_report(bad, orig, new)
    check(len(sc["missed"]) == 2 and sc["phantom"] == 1, f"reporter scoring: omission and phantom detected ({sc})")

    per = models.load_persona("planner-v8", {"policy": C.policy_text(), "schema_version": "8"})
    check("{policy}" not in per.prompt and '"schema_version": 8' in per.prompt, "persona placeholders are filled")


# ------------------------------------------------------------ 2. mock stacks


def run_mock(cfg_name: str, suites=("flows", "bench40")):
    configs, ms, ps = rig.resolve([f"{cfg_name}.json"])
    stack = flow.Stack(configs[0], ms, ps)
    client = models.Client(use_cache=False)
    return {(pol, s["id"]): flow.run_scenario(client, stack, s, pol)
            for pol in flow.POLICIES for s in rig.load_suites(list(suites))}


def mocks() -> None:
    r = run_mock("mock-oracle")
    check(all(x["final_state"] == "exact" for x in r.values()), "oracle stack: every final state exact")
    check(all(t["ok"] for x in r.values() for t in x["transactions"]), "oracle stack: every transaction ok")
    rep = [t["reporter"]["score"] for x in r.values() for t in x["transactions"] if t.get("reporter", {}).get("score")]
    check(rep and all(not s["missed"] and not s["phantom"] for s in rep), "oracle reporter scores clean everywhere")
    check(r[("oracle", "flow-bad-request")]["transactions"][0]["status"] == "NO_CHANGE", "bad request: nothing committed")

    r = run_mock("mock-stale", ("flows",))
    demo_rs, demo_or = r[("rubber_stamp", "flow-demo")], r[("oracle", "flow-demo")]
    check(demo_rs["transactions"][1]["committed_wrong"] and demo_rs["final_state"] == "diverged",
          "stale planner + rubber stamp: wrong activation committed")
    check(demo_or["transactions"][1]["status"] == "HUMAN_REJECTED", "stale planner + oracle: human catches it")
    check(demo_or["transactions"][0]["status"] == "COMMITTED", "stale planner: the port change itself is fine")

    r = run_mock("mock-stale-reviewed", ("flows",))
    t = r[("rubber_stamp", "flow-demo")]["transactions"][1]
    check(t["status"] == "REVIEW_REJECTED" and not t["committed_wrong"], "stale planner + good reviewer: blocked before human")

    r = run_mock("mock-inject-approveall")
    inj = [t for x in r.values() if x["policy"] == "rubber_stamp" for t in x["transactions"] if t.get("injection_followed")]
    check(len(inj) > 0 and all(t["injection_committed"] for t in inj), "injecting planner + approve-all: injection committed")
    inj_or = [t for x in r.values() if x["policy"] == "oracle" for t in x["transactions"] if t.get("injection_followed")]
    check(all(t["status"] == "HUMAN_REJECTED" for t in inj_or), "injecting planner + oracle human: all caught")

    r = run_mock("mock-dropcheck", ("flows",))
    t = r[("oracle", "flow-demo")]["transactions"][0]
    check(t["status"] == "VALIDATION_FAILED" and t["validation"]["reason"] == "check_sequence" and t["escalation_eligible"],
          "dropped check: validation fails, escalation-eligible")
    check(r[("oracle", "flow-demo")]["transactions"][1]["status"] == "SKIPPED", "on_fail stop: later transactions skipped")

    r = run_mock("mock-loop", ("flows",))
    check(all(x["final_state"] == "exact" for x in r.values()), "loop style through the flow")


# ------------------------------------------------------ 3. fake HTTP server


class Fake(BaseHTTPRequestHandler):
    hits = 0

    def log_message(self, *a):
        pass

    def do_POST(self):
        Fake.hits += 1
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        msgs = body["messages"]
        system, user = msgs[0]["content"], msgs[1]["content"]
        handles = json.loads(re.search(r"Handles:\n(\[.*?\n\])", user, re.S).group(1))
        target = next(h for h in handles if h["kind"] != "context")
        msg = {"role": "assistant", "content": ""}
        if "tools" in body:
            tool_msgs = [m for m in msgs if m["role"] == "tool"]
            if not tool_msgs:
                msg["tool_calls"] = [{"id": "c1", "type": "function", "function": {
                    "name": "read_handle", "arguments": json.dumps({"handle_id": target["handle_id"]})}}]
            else:
                content = self._edit(tool_msgs[-1]["content"])
                msg["tool_calls"] = [{"id": "c2", "type": "function", "function": {
                    "name": "propose_write", "arguments": json.dumps({
                        "file_handle": target["handle_id"], "expected_old_hash": target["content_hash"],
                        "content": content})}}]
        elif "reviewer" in system or "review" in system.split(".")[0]:
            msg["content"] = json.dumps({"verdict": "approve", "reasons": ["fake"]})
        elif "explain" in system:
            msg["content"] = json.dumps({"summary": "fake", "changes": [{"field": "listen.port", "from": "8080", "to": "8081"}],
                                         "risks": [], "recommendation": "approve"})
        else:
            m = re.search(r"----- BEGIN CONTENT \S+ \(.*?\) -----\n(.*?)\n----- END CONTENT", user, re.S)
            text = m.group(1) + ("\n" if target["ends_with_newline"] else "")
            msg["content"] = json.dumps({"schema_version": 8, "calls": [
                {"op": "write_lab_file", "file_handle": target["handle_id"], "expected_old_hash": target["content_hash"],
                 "content": self._edit(text)}] + [{"op": "run_check", "check_profile": p}
                                                  for p in C.KIND_PROFILES[target["kind"]]]})
        out = json.dumps({"choices": [{"message": msg, "finish_reason": "stop"}],
                          "timings": {"prompt_n": 10, "prompt_ms": 5, "predicted_n": 10, "predicted_ms": 5}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    @staticmethod
    def _edit(text: str) -> str:
        d = json.loads(text)
        if "listen" in d:
            d["listen"]["port"] = 8081
        return C.dumps(d)


def http_path() -> None:
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/v1/chat/completions"
    fake = models.Model(key="fake", backend="openai", url=url, model="fake")
    ph = {"policy": C.policy_text(), "schema_version": "8"}
    ps = {n: models.load_persona(n, ph) for n in ("planner-v8", "planner-loop", "reviewer-strict", "reporter-plain")}
    scen = next(s for s in rig.load_suites(["flows"]) if s["id"] == "flow-demo")
    with tempfile.TemporaryDirectory() as tmp:
        models.CACHE = Path(tmp)
        for persona in ("planner-v8", "planner-loop"):
            cfg = {"name": f"fake-{persona}", "planner": {"model": "fake", "persona": persona},
                   "reviewer": {"model": "fake", "persona": "reviewer-strict"},
                   "reporter": {"model": "fake", "persona": "reporter-plain"}}
            stack = flow.Stack(cfg, {"fake": fake}, ps)
            client = models.Client(use_cache=True)
            Fake.hits = 0
            r1 = flow.run_scenario(client, stack, scen, "oracle")
            t = r1["transactions"][0]
            check(t["status"] == "COMMITTED" and t["verdict"] == "correct",
                  f"{persona} over HTTP: port change committed byte-exact (got {t['status']}/{t.get('verdict')})")
            check(t["reviewer"]["verdict"] == "approve" and t["reporter"]["score"]["missed"] == [],
                  f"{persona} over HTTP: reviewer and reporter parsed")
            if persona == "planner-loop":
                check(t["planner"]["steps"] == 2 and t["planner"]["reads"], "loop: read then propose")
            first = Fake.hits
            flow.run_scenario(client, stack, scen, "oracle")
            check(Fake.hits == first, f"{persona}: identical rerun served from cache ({Fake.hits - first} extra calls)")
    srv.shutdown()


def report_builds() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        configs, ms, ps = rig.resolve(["mock-oracle.json", "mock-stale-reviewed.json"])
        (out / "run.json").write_text(json.dumps({"started": "selftest", "suites": ["flows"], "cache": False,
                                                  "configs": configs, "personas": {k: {"style": v.style} for k, v in ps.items()}}))
        lines = []
        for cfg in configs:
            stack = flow.Stack(cfg, ms, ps)
            for pol in flow.POLICIES:
                for s in rig.load_suites(["flows"]):
                    res = flow.run_scenario(models.Client(False), stack, s, pol)
                    for t in res["transactions"]:
                        t.pop("trace", None)
                    lines.append(json.dumps(res))
        (out / "results.jsonl").write_text("\n".join(lines) + "\n")
        text = report.build(out)
        check("## Reviewer" in text and "## Reporter" in text and "flow-demo" in text, "REPORT.md builds with every section")


if __name__ == "__main__":
    units()
    mocks()
    http_path()
    report_builds()
    print(f"\n{'OK' if not FAILS else f'{len(FAILS)} FAILED'}")
    sys.exit(1 if FAILS else 0)
