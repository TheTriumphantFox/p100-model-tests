#!/usr/bin/env python3
"""Run standard HumanEval pass@1 against local Ollama models."""
from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import hashlib
import html
import json
import math
import os
import re
import shutil
import signal
import statistics
import subprocess
import sys
import tempfile
import textwrap
import time
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pyarrow.parquet as pq

SCRIPT_DIR = Path(__file__).resolve().parent
TESTS_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_DATASET = TESTS_ROOT / "datasets/humaneval/openai_humaneval/test-00000-of-00001.parquet"
DEFAULT_OUTPUT_ROOT = SCRIPT_DIR / "runs"
DEFAULT_BASE_URL = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MARKER = "__HUMANEVAL_RESULT__"


def now() -> str:
    return dt.datetime.now().astimezone().isoformat()


def normalize_url(value: str) -> str:
    value = value.strip() or "http://127.0.0.1:11434"
    return (value if "://" in value else "http://" + value).rstrip("/")


def request_json(base: str, path: str, payload: dict[str, Any] | None = None, timeout: float = 30) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode()
    request = Request(normalize_url(base) + path, data=body, headers={"Content-Type": "application/json"}, method="GET" if body is None else "POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise RuntimeError(f"Ollama HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach Ollama at {base}: {exc.reason}") from exc
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ollama returned invalid JSON for {path}") from exc
    if not isinstance(result, dict):
        raise RuntimeError(f"Ollama returned a non-object for {path}")
    return result


def discover_models(base: str, timeout: float) -> list[dict[str, Any]]:
    models = request_json(base, "/api/tags", timeout=timeout).get("models")
    if not isinstance(models, list):
        raise RuntimeError("Ollama /api/tags did not return a model list")
    return [model for model in models if isinstance(model, dict) and model.get("name")]


def unload_model(base: str, model: str) -> None:
    try:
        request_json(base, "/api/generate", {"model": model, "prompt": "", "keep_alive": 0}, timeout=120)
    except Exception as exc:
        print(f"warning: could not unload {model}: {exc}", file=sys.stderr)


def model_metadata(model: dict[str, Any]) -> dict[str, Any]:
    details = model.get("details") or {}
    return {"name": model.get("name", ""), "digest": model.get("digest", ""), "size_bytes": model.get("size", 0), "parameter_size": details.get("parameter_size", ""), "quantization": details.get("quantization_level", ""), "family": details.get("family", "")}


def load_tasks(dataset: Path) -> list[dict[str, Any]]:
    if not dataset.is_file():
        raise RuntimeError(f"HumanEval dataset not found: {dataset}")
    rows = pq.read_table(dataset).to_pylist()
    required = {"task_id", "prompt", "test", "entry_point"}
    if not rows or not required.issubset(rows[0]):
        raise RuntimeError("HumanEval dataset has an unexpected schema")
    return sorted(rows, key=lambda row: int(str(row["task_id"]).split("/")[-1]))


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")[:100] or "item"


def strip_thinking(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.I | re.S)
    if re.search(r"<think>", text, re.I):
        text = re.split(r"<think>", text, flags=re.I, maxsplit=1)[0]
    return text.strip("\r\n")


def valid_module(source: str, entrypoint: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == entrypoint for node in tree.body)


def source_candidates(text: str) -> list[str]:
    cleaned = strip_thinking(text)
    fenced = re.findall(r"```[ \t]*(?:python|py)?[^\n]*\n(.*?)```", cleaned, flags=re.I | re.S)
    candidates = [candidate.strip("\n") for candidate in fenced] + [cleaned]
    expanded: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in expanded:
            expanded.append(candidate)
        lines = candidate.splitlines()
        for index, line in enumerate(lines):
            if line.strip().startswith(("from ", "import ", "def ", "async def ", "@", "    ", "\t")):
                suffix = "\n".join(lines[index:]).strip("\n")
                if suffix and suffix not in expanded:
                    expanded.append(suffix)
                break
    return expanded


def extract_solution(text: str, prompt: str, entrypoint: str) -> tuple[str, str]:
    candidates = source_candidates(text)
    for candidate in candidates:
        if valid_module(candidate, entrypoint):
            return candidate.rstrip() + "\n", ""
    prefix = prompt.rstrip() + "\n"
    for candidate in candidates:
        variants = [candidate]
        if candidate and not candidate.startswith((" ", "\t")):
            variants.append(textwrap.indent(candidate, "    "))
        for body in variants:
            combined = prefix + body.rstrip() + "\n"
            if valid_module(combined, entrypoint):
                return combined, ""
    return "", f"Could not extract a valid module defining {entrypoint}"


def sandbox_command(work: Path) -> list[str]:
    bwrap = shutil.which("bwrap")
    if not bwrap:
        raise RuntimeError("bubblewrap (bwrap) is required")
    command = [bwrap, "--die-with-parent", "--new-session", "--unshare-all"]
    for root in ("/usr", "/usr/local", "/bin", "/lib", "/lib64", "/etc"):
        if Path(root).exists():
            command += ["--ro-bind", root, root]
    command += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--dir", "/benchmark", "--bind", str(work), "/benchmark", "--chdir", "/benchmark", "--setenv", "HOME", "/tmp", "--setenv", "PATH", "/usr/local/bin:/usr/bin:/bin", "--setenv", "PYTHONDONTWRITEBYTECODE", "1", "/usr/bin/python3", "-B", "runner.py"]
    return command


def kill_process(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            process.kill()
        except ProcessLookupError:
            pass


def check_solution(source: str, task: dict[str, Any], work_root: Path, timeout: float) -> tuple[bool, str]:
    work = Path(tempfile.mkdtemp(prefix=safe_name(task["task_id"]) + "-", dir=work_root))
    try:
        (work / "solution.py").write_text(source, encoding="utf-8")
        runner = (
            "import json, resource\n"
            "resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))\n"
            "resource.setrlimit(resource.RLIMIT_CORE, (0, 0))\n"
            "resource.setrlimit(resource.RLIMIT_AS, (1500000000, 1500000000))\n"
            "resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))\n"
            "try:\n"
            "    namespace = {}\n"
            "    source = open('solution.py', encoding='utf-8').read()\n"
            "    exec(compile(source, 'solution.py', 'exec'), namespace)\n"
            f"    tests = {task['test']!r}\n"
            "    exec(compile(tests, 'tests.py', 'exec'), namespace)\n"
            f"    namespace['check'](namespace[{task['entry_point']!r}])\n"
            "    result = {'passed': True, 'error': ''}\n"
            "except BaseException as exc:\n"
            "    result = {'passed': False, 'error': f'{type(exc).__name__}: {exc}'}\n"
            f"print({MARKER!r} + json.dumps(result))\n"
        )
        (work / "runner.py").write_text(runner, encoding="utf-8")
        process = subprocess.Popen(sandbox_command(work), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_process(process)
            process.communicate()
            return False, f"test timeout after {timeout:g}s"
        lines = [line[len(MARKER):] for line in stdout.splitlines() if line.startswith(MARKER)]
        if lines:
            try:
                result = json.loads(lines[-1])
                return bool(result.get("passed")), str(result.get("error") or "")
            except json.JSONDecodeError:
                pass
        detail = stderr.strip() or stdout.strip() or f"checker exited {process.returncode}"
        return False, detail[-2000:]
    finally:
        shutil.rmtree(work, ignore_errors=True)


def ns_seconds(value: Any) -> float | None:
    try:
        return float(value) / 1_000_000_000
    except (TypeError, ValueError):
        return None


def chat(base: str, model: str, task: dict[str, Any], args: argparse.Namespace) -> tuple[dict[str, Any], str, float]:
    system = (
        "Complete the supplied Python HumanEval task. Return only one complete, import-safe Python module, preferably in a single python code block. "
        "Include the requested function and all required imports. Do not explain, read files, use the network, spawn processes, or use third-party packages."
    )
    user = "Complete this Python program:\n\n```python\n" + str(task["prompt"]) + "\n```"
    payload = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "stream": False, "think": False, "keep_alive": args.keep_alive, "options": {"num_ctx": args.num_ctx, "num_predict": args.num_predict, "temperature": 0, "seed": args.seed}}
    last_error: Exception | None = None
    for attempt in range(args.retries + 1):
        started = time.monotonic()
        try:
            response = request_json(base, "/api/chat", payload, timeout=args.api_timeout)
            elapsed = time.monotonic() - started
            message = response.get("message") or {}
            return response, str(message.get("content") or response.get("response") or ""), elapsed
        except Exception as exc:
            last_error = exc
            if attempt < args.retries:
                print(f"\n  request failed; retrying in 10s: {exc}", file=sys.stderr, flush=True)
                time.sleep(10)
    raise RuntimeError(str(last_error))


class Progress:
    def __init__(self, total: int, done: int = 0, started: float | None = None) -> None:
        self.total, self.done = total, done
        self.started = started if started is not None else time.monotonic()
        self.tty = sys.stdout.isatty()

    @staticmethod
    def duration(seconds: float) -> str:
        if seconds >= 86400:
            return f"{int(seconds // 86400)}d {int(seconds % 86400 // 3600):02d}h"
        if seconds >= 3600:
            return f"{int(seconds // 3600)}h {int(seconds % 3600 // 60):02d}m"
        if seconds >= 60:
            return f"{int(seconds // 60)}m {int(seconds % 60):02d}s"
        return f"{seconds:.0f}s"

    def update(self, label: str) -> None:
        self.done += 1
        elapsed = time.monotonic() - self.started
        rate_done = max(1, self.done)
        eta = elapsed / rate_done * (self.total - self.done)
        width = 30
        filled = int(width * self.done / self.total)
        line = f"[{'#'*filled}{'-'*(width-filled)}] {self.done}/{self.total} ({100*self.done/self.total:5.1f}%) {label[:55]:55} ETA {self.duration(eta)}"
        print(("\r" if self.tty else "") + line, end="" if self.tty else "\n", flush=True)
        if self.tty and self.done == self.total:
            print()


def aggregate(models: list[dict[str, Any]], results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for model in models:
        rows = [row for row in results if row["model"] == model["name"]]
        speeds = [float(row["generation_tps"]) for row in rows if row.get("generation_tps") is not None]
        summaries.append({**model, "pass_at_1": 100 * sum(bool(row["passed"]) for row in rows) / len(rows) if rows else 0, "passed": sum(bool(row["passed"]) for row in rows), "attempted": len(rows), "errors": sum(row["status"] == "error" for row in rows), "generation_tps": statistics.mean(speeds) if speeds else None, "wall_seconds": sum(float(row.get("wall_seconds") or 0) for row in rows)})
    return sorted(summaries, key=lambda row: (row["pass_at_1"], row.get("generation_tps") or 0), reverse=True)


def write_csv(output: Path, results: list[dict[str, Any]], summaries: list[dict[str, Any]]) -> None:
    fields = ["model", "task_id", "entry_point", "passed", "status", "generation_tps", "prompt_tps", "wall_seconds", "load_seconds", "eval_count", "solution_file", "raw_output_file", "error"]
    with (output / "results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(results)
    fields = ["rank", "model", "pass_at_1", "passed", "attempted", "errors", "generation_tps", "wall_seconds"]
    with (output / "model-summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore"); writer.writeheader()
        for rank, summary in enumerate(summaries, 1): writer.writerow({"rank": rank, **summary})


def svg_start(width: int, height: int, title: str, subtitle: str) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#111718"/>', '<style>text{font-family:DejaVu Sans,Arial,sans-serif}.title{fill:#fff;font-size:28px;font-weight:bold}.sub{fill:#9eafb0;font-size:14px}.label{fill:#e7eeee;font-size:16px}.value{fill:#fff;font-size:15px;font-weight:bold}</style>', f'<text x="36" y="42" class="title">{html.escape(title)}</text>', f'<text x="36" y="68" class="sub">{html.escape(subtitle)}</text>']


def write_bar(path: Path, summaries: list[dict[str, Any]], key: str, title: str, subtitle: str, suffix: str, color: str) -> None:
    ordered = sorted(summaries, key=lambda row: row.get(key) or 0, reverse=True)
    values = [float(row.get(key) or 0) for row in ordered]
    axis_max = 100.0 if key == "pass_at_1" else max(1.0, max(values, default=1) * 1.15)
    width, left, top, row_h, bottom = 1500, 450, 95, 46, 65
    height, plot = top + max(1, len(ordered))*row_h + bottom, width-left-80
    svg = svg_start(width, height, title, subtitle)
    for index in range(6):
        tick = axis_max * index / 5; x = left + plot * index / 5
        svg += [f'<line x1="{x}" y1="80" x2="{x}" y2="{height-bottom}" stroke="#293536"/>', f'<text x="{x}" y="{height-23}" text-anchor="middle" class="sub">{tick:.0f}{suffix}</text>']
    for index, row in enumerate(ordered):
        value = float(row.get(key) or 0); y = top + index*row_h; bar = plot*value/axis_max
        svg += [f'<text x="{left-14}" y="{y+21}" text-anchor="end" class="label">{html.escape(row["name"][:48])}</text>', f'<rect x="{left}" y="{y+3}" width="{plot}" height="26" rx="4" fill="#1c2728"/>', f'<rect x="{left}" y="{y+3}" width="{bar}" height="26" rx="4" fill="{color}"/>', f'<text x="{left+bar+10}" y="{y+22}" class="value">{value:.1f}{suffix}</text>']
    svg.append("</svg>"); path.write_text("\n".join(svg)+"\n")


def write_report(output: Path, metadata: dict[str, Any], results: list[dict[str, Any]], summaries: list[dict[str, Any]]) -> None:
    total_tasks = int(metadata["task_count"])
    state = "interrupted" if metadata.get("interrupted") else ("complete" if metadata.get("finished") and len(results) == len(metadata["models"])*total_tasks else "in progress")
    rows = []
    for rank, row in enumerate(summaries, 1):
        speed = "--" if row["generation_tps"] is None else f'{row["generation_tps"]:.2f}'
        rows.append(f'<tr><td>{rank}</td><td><code>{html.escape(row["name"])}</code></td><td><strong>{row["pass_at_1"]:.1f}%</strong></td><td>{row["passed"]}/{row["attempted"]}</td><td>{row["errors"]}</td><td>{speed}</td></tr>')
    body = f'''<!doctype html><html><head><meta charset="utf-8"><title>HumanEval benchmark</title><style>body{{background:#111718;color:#e7eeee;font:16px system-ui,sans-serif;max-width:1550px;margin:2rem auto;padding:0 1rem}}h1,h2{{color:#fff}}.card{{background:#182122;border:1px solid #293536;border-radius:8px;padding:1rem;margin:1rem 0;overflow:auto}}img{{max-width:100%}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #293536;padding:.55rem;text-align:left}}th,.note{{color:#9eafb0}}code{{color:#b9e5dc}}</style></head><body><h1>Local LLM HumanEval benchmark</h1><p class="note">Started: <code>{html.escape(str(metadata.get("started")))}</code> | State: <code>{state}</code> | Completed: <code>{len(results)}/{len(metadata["models"])*total_tasks}</code></p><div class="card"><h2>Pass@1</h2><img src="pass-at-1.svg"></div><div class="card"><h2>Generation speed</h2><img src="generation-speed.svg"></div><div class="card"><h2>Ranking</h2><table><thead><tr><th>Rank</th><th>Model</th><th>Pass@1</th><th>Passed</th><th>Errors</th><th>tok/s</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><div class="card"><h2>Method</h2><p>All {total_tasks} OpenAI HumanEval test tasks, one deterministic generation per model, temperature 0, seed {metadata["settings"]["seed"]}, thinking disabled. Generated code is executed with the dataset tests inside a network-isolated bubblewrap sandbox. This is pass@1; no retries are used to improve incorrect solutions.</p></div></body></html>'''
    (output / "report.html").write_text(body, encoding="utf-8")


def save(output: Path, metadata: dict[str, Any], results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = aggregate(metadata["models"], results)
    metadata["updated"] = now(); payload = {"metadata": metadata, "results": results, "model_summaries": summaries}
    temporary = output / "results.json.tmp"; temporary.write_text(json.dumps(payload, indent=2)+"\n"); temporary.replace(output/"results.json")
    write_csv(output, results, summaries)
    write_bar(output/"pass-at-1.svg", summaries, "pass_at_1", "HumanEval pass@1 by model", "All 164 standard test tasks | Higher is better", "%", "#52c1a2")
    write_bar(output/"generation-speed.svg", summaries, "generation_tps", "HumanEval generation speed", "Ollama output throughput | Correctness is ranked separately", "", "#c88a55")
    write_report(output, metadata, results, summaries)
    return summaries


def run(args: argparse.Namespace) -> int:
    if not shutil.which("bwrap"):
        raise RuntimeError("bwrap is required to execute generated code safely")
    base = normalize_url(args.base_url); dataset = Path(args.dataset).expanduser().resolve(); tasks = load_tasks(dataset)
    if args.limit: tasks = tasks[:args.limit]
    discovered = discover_models(base, args.api_timeout)
    if args.model:
        lookup = {model["name"]: model for model in discovered}; missing = [name for name in args.model if name not in lookup]
        if missing: raise RuntimeError("Requested model(s) not installed: " + ", ".join(missing))
        discovered = [lookup[name] for name in args.model]
    if args.exclude: discovered = [model for model in discovered if not any(re.search(pattern, model["name"]) for pattern in args.exclude)]
    if not discovered: raise RuntimeError("No models selected")

    if args.resume:
        results_path = Path(args.resume).expanduser().resolve(); payload = json.loads(results_path.read_text()); output = results_path.parent
        metadata, results = payload["metadata"], payload["results"]
        wanted_models = [model["name"] for model in metadata["models"]]
        lookup = {model["name"]: model for model in discovered}; missing = [name for name in wanted_models if name not in lookup]
        if missing: raise RuntimeError("Resume model(s) no longer installed: " + ", ".join(missing))
        discovered = [lookup[name] for name in wanted_models]
        task_ids = set(metadata["task_ids"]); tasks = [task for task in tasks if task["task_id"] in task_ids]
        metadata["interrupted"] = False; metadata.pop("finished", None); metadata["resumed"] = now()
    else:
        output = Path(args.output).expanduser().resolve() if args.output else DEFAULT_OUTPUT_ROOT/dt.datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
        if output.exists() and any(output.iterdir()): raise RuntimeError(f"Output directory is not empty: {output}")
        output.mkdir(parents=True); results = []
        metadata = {"started": now(), "interrupted": False, "backend": "Ollama /api/chat", "dataset": str(dataset), "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(), "task_count": len(tasks), "task_ids": [task["task_id"] for task in tasks], "settings": {"num_ctx": args.num_ctx, "num_predict": args.num_predict, "temperature": 0, "seed": args.seed, "thinking": False, "checker_timeout": args.checker_timeout, "sandbox": "bubblewrap", "request_retries": args.retries}, "models": [model_metadata(model) for model in discovered]}
    raw_dir, solutions_dir, work_root = output/"raw", output/"solutions", output/"work"
    raw_dir.mkdir(exist_ok=True); solutions_dir.mkdir(exist_ok=True); work_root.mkdir(exist_ok=True)
    completed = {(row["model"], row["task_id"]) for row in results}
    total = len(discovered)*len(tasks); progress = Progress(total, len(completed))
    print(f"HumanEval: {len(discovered)} model(s) × {len(tasks)} tasks = {total} generations.")
    print(f"Already completed: {len(completed)}. Results: {output}")
    try:
        for model_index, model in enumerate(discovered, 1):
            name = model["name"]; print(f"\nModel {model_index}/{len(discovered)}: {name}")
            try:
                for task in tasks:
                    task_id = str(task["task_id"])
                    if (name, task_id) in completed: continue
                    number = int(task_id.split("/")[-1]); stem = f"{model_index:02d}-{safe_name(name)}-{number:03d}"
                    raw_path, solution_path = raw_dir/(stem+".txt"), solutions_dir/(stem+".py")
                    response: dict[str, Any] = {}; text = ""; elapsed: float | None = None; error = ""; status = "failed"; passed = False
                    try:
                        response, text, elapsed = chat(base, name, task, args); raw_path.write_text(text, encoding="utf-8")
                        solution, extraction_error = extract_solution(text, str(task["prompt"]), str(task["entry_point"]))
                        if extraction_error:
                            error = extraction_error
                        else:
                            solution_path.write_text(solution, encoding="utf-8")
                            passed, error = check_solution(solution, task, work_root, args.checker_timeout)
                            status = "passed" if passed else "failed"
                    except Exception as exc:
                        error = f"{type(exc).__name__}: {exc}"; status = "error"; raw_path.write_text("BENCHMARK ERROR\n"+error+"\n", encoding="utf-8")
                    eval_seconds, prompt_seconds = ns_seconds(response.get("eval_duration")), ns_seconds(response.get("prompt_eval_duration")); eval_count, prompt_count = response.get("eval_count"), response.get("prompt_eval_count")
                    results.append({"model": name, "model_digest": model.get("digest", ""), "task_id": task_id, "entry_point": task["entry_point"], "passed": passed, "status": status, "generation_tps": float(eval_count)/eval_seconds if eval_count is not None and eval_seconds else None, "prompt_tps": float(prompt_count)/prompt_seconds if prompt_count is not None and prompt_seconds else None, "wall_seconds": elapsed, "load_seconds": ns_seconds(response.get("load_duration")), "eval_count": eval_count, "solution_file": str(solution_path.relative_to(output)) if solution_path.exists() else "", "raw_output_file": str(raw_path.relative_to(output)), "error": error})
                    completed.add((name, task_id)); progress.update(f"{name} / {task_id}"); save(output, metadata, results)
            finally:
                unload_model(base, name)
    except KeyboardInterrupt:
        metadata["interrupted"] = True; print("\nInterrupted; partial results saved.", file=sys.stderr)
    finally:
        metadata["finished"] = now(); summaries = save(output, metadata, results); shutil.rmtree(work_root, ignore_errors=True)
    print(f"\nFinished {len(results)}/{total} generations. Report: {output/'report.html'}")
    if summaries: print(f"Leader: {summaries[0]['name']} ({summaries[0]['pass_at_1']:.1f}%)")
    return 0


def report(args: argparse.Namespace) -> int:
    path = Path(args.results_json).expanduser().resolve(); payload = json.loads(path.read_text()); output = Path(args.output).expanduser().resolve() if args.output else path.parent
    summaries = save(output, payload["metadata"], payload["results"]); print(f"Report: {output/'report.html'} ({len(summaries)} models)"); return 0


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__); sub = root.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run"); run_parser.add_argument("--base-url", default=DEFAULT_BASE_URL); run_parser.add_argument("--dataset", default=str(DEFAULT_DATASET)); run_parser.add_argument("--model", action="append"); run_parser.add_argument("--exclude", action="append"); run_parser.add_argument("--limit", type=int); run_parser.add_argument("--num-ctx", type=int, default=8192); run_parser.add_argument("--num-predict", type=int, default=1024); run_parser.add_argument("--seed", type=int, default=42); run_parser.add_argument("--keep-alive", default="10m"); run_parser.add_argument("--api-timeout", type=float, default=900); run_parser.add_argument("--checker-timeout", type=float, default=10); run_parser.add_argument("--retries", type=int, default=1); run_parser.add_argument("--output"); run_parser.add_argument("--resume")
    report_parser = sub.add_parser("report"); report_parser.add_argument("results_json"); report_parser.add_argument("--output")
    return root


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "run":
        if args.limit is not None and args.limit < 1: raise RuntimeError("--limit must be positive")
        if min(args.num_ctx, args.num_predict) < 1 or min(args.api_timeout, args.checker_timeout) <= 0 or args.retries < 0: raise RuntimeError("numeric options are invalid")
        return run(args)
    return report(args)


if __name__ == "__main__":
    try: raise SystemExit(main())
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr); raise SystemExit(1)
