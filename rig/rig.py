#!/usr/bin/env python3
"""Full-stack test rig: run scenarios through planner -> reviewer -> reporter -> human -> commit.

    rig.py list
    rig.py run --config configs/v8-qwen36moe.json [--config ...] [--suite flows] [--only ID ...]
    rig.py report RUN_DIR

Runs are written to ~/Projects/Tests/<date>/rig/<name>/ and are resumable: a
(config, policy, scenario) already in results.jsonl is skipped.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import controller as C
import flow
import report
from models import RIG, Client, ServerGone, load_models, load_persona

TESTS = RIG.parent


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_suites(names: List[str]) -> List[Dict[str, Any]]:
    out = []
    for n in names:
        doc = load_json(RIG / "scenarios" / f"{n}.json")
        for s in doc["scenarios"]:
            s["suite"] = n
            out.append(s)
    return out


def resolve(cfg_paths: List[str]):
    models = load_models()
    placeholders = {"policy": C.policy_text(), "schema_version": str(C.SCHEMA_VERSION)}
    configs, personas = [], {}
    for p in cfg_paths:
        cfg = load_json(Path(p) if Path(p).exists() else RIG / "configs" / p)
        for role in ("planner", "reviewer", "reporter"):
            spec = cfg.get(role)
            if not spec:
                continue
            if spec["model"] not in models:
                sys.exit(f"{cfg['name']}: unknown model {spec['model']!r} (see models.json)")
            per = personas.get(spec["persona"]) or load_persona(spec["persona"], placeholders)
            if per.role != role:
                sys.exit(f"{cfg['name']}: persona {per.name} is a {per.role}, not a {role}")
            personas[per.name] = per
        configs.append(cfg)
    return configs, models, personas


def cmd_list(_args) -> int:
    print("models (models.json):")
    for k, m in load_models().items():
        print(f"  {k:28} {m.backend:7} {m.model or m.behaviour}")
    print("\npersonas (personas/):")
    for p in sorted((RIG / "personas").glob("*.md")):
        per = load_persona(p.stem, {})
        print(f"  {p.stem:28} {per.role:9} {per.style if per.role == 'planner' else '':8} {per.description}")
    print("\nconfigs (configs/):")
    for p in sorted((RIG / "configs").glob("*.json")):
        c = load_json(p)
        roles = " + ".join(f"{r}={c[r]['model']}/{c[r]['persona']}" for r in ("planner", "reviewer", "reporter") if c.get(r))
        print(f"  {p.name:34} {roles}")
    print("\nsuites (scenarios/):")
    for p in sorted((RIG / "scenarios").glob("*.json")):
        d = load_json(p)
        n = sum(len(s["transactions"]) for s in d["scenarios"])
        print(f"  {p.stem:12} {len(d['scenarios']):3} scenarios, {n:3} transactions  {d.get('description', '')}")
    return 0


def cmd_run(args) -> int:
    configs, models, personas = resolve(args.config)
    scenarios = load_suites(args.suite)
    if args.only:
        scenarios = [s for s in scenarios if s["id"] in set(args.only)]
    if not scenarios:
        sys.exit("no scenarios selected")
    name = args.name or dt.datetime.now().strftime("%H-%M-%S")
    out = Path(args.out) if args.out else TESTS / dt.date.today().isoformat() / "rig" / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "traces").mkdir(exist_ok=True)
    meta = {"started": dt.datetime.now().isoformat(timespec="seconds"), "suites": args.suite,
            "only": args.only, "policies": args.policy, "cache": not args.no_cache,
            "configs": configs,
            "personas": {k: {"role": v.role, "style": v.style, "thinking": v.thinking, "sha256": v.sha256}
                         for k, v in personas.items()},
            "models": {k: vars(m) for k, m in models.items()
                       if any(m.key == (c.get(r) or {}).get("model") for c in configs for r in ("planner", "reviewer", "reporter"))}}
    if (out / "run.json").exists():
        # A second invocation into the same run (e.g. another config on another suite):
        # keep what earlier invocations recorded, so the report covers all of them.
        old = load_json(out / "run.json")
        meta["started"] = old["started"]
        meta["suites"] = sorted(set(old["suites"]) | set(meta["suites"]))
        names = {c["name"] for c in meta["configs"]}
        meta["configs"] = [c for c in old["configs"] if c["name"] not in names] + meta["configs"]
        meta["personas"] = {**old["personas"], **meta["personas"]}
        meta["models"] = {**old.get("models", {}), **meta["models"]}
    (out / "run.json").write_text(json.dumps(meta, indent=1))

    results_path = out / "results.jsonl"
    done = set()
    if results_path.exists():
        for line in results_path.read_text().splitlines():
            r = json.loads(line)
            done.add((r["config"], r["policy"], r["scenario"]))
    client = Client(use_cache=not args.no_cache)
    total = len(configs) * len(args.policy) * len(scenarios)
    n = 0
    for cfg in configs:
        stack = flow.Stack(cfg, models, personas)
        for policy in args.policy:
            for s in scenarios:
                n += 1
                if (stack.name, policy, s["id"]) in done:
                    continue
                try:
                    res = flow.run_scenario(client, stack, s, policy)
                except ServerGone as e:
                    print(f"ABORT: {e}. Resume with the same command.", flush=True)
                    return 2
                traces = {t["index"]: t.pop("trace") for t in res["transactions"] if "trace" in t}
                if any(traces.values()):
                    tdir = out / "traces" / stack.name / policy
                    tdir.mkdir(parents=True, exist_ok=True)
                    (tdir / f"{s['id']}.json").write_text(json.dumps(traces, ensure_ascii=False, indent=1))
                with open(results_path, "a") as f:
                    f.write(json.dumps(res, ensure_ascii=False) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                marks = "".join("." if t["ok"] else report.STATUS_MARK.get(t["status"], "?") for t in res["transactions"])
                print(f"[{n:4}/{total}] {stack.name:28} {policy:12} {s['id']:34} {marks:8} "
                      f"final={res['final_state']:10} {res['model_seconds']:7.1f}s", flush=True)
    (out / "REPORT.md").write_text(report.build(out))
    print(f"\nwrote {out / 'REPORT.md'}")
    return 0


def cmd_report(args) -> int:
    out = Path(args.run_dir)
    (out / "REPORT.md").write_text(report.build(out))
    print(out / "REPORT.md")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    r = sub.add_parser("run")
    r.add_argument("--config", action="append", required=True, help="configs/<name>.json, or a path; repeatable")
    r.add_argument("--suite", action="append", default=None, help="scenarios/<name>.json; repeatable (default: flows)")
    r.add_argument("--only", nargs="*", help="scenario ids")
    r.add_argument("--policy", action="append", choices=flow.POLICIES, default=None,
                   help="approval policy; repeatable (default: both)")
    r.add_argument("--name", help="run folder name (default: the time)")
    r.add_argument("--out", help="run folder (default: ~/Projects/Tests/<date>/rig/<name>)")
    r.add_argument("--no-cache", action="store_true", help="always call the model")
    r.set_defaults(fn=cmd_run)
    rp = sub.add_parser("report")
    rp.add_argument("run_dir")
    rp.set_defaults(fn=cmd_report)
    args = p.parse_args()
    if args.cmd == "run":
        args.suite = args.suite or ["flows"]
        args.policy = args.policy or list(flow.POLICIES)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
