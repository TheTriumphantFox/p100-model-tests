#!/usr/bin/env python3
"""Run and report an objective coding benchmark against local Ollama models.

The run command discovers every model tag returned by Ollama, asks each model
to solve the same tasks, executes the returned code in a bubblewrap sandbox,
and writes CSV/JSON/SVG/HTML results.  Importing this module never contacts
Ollama and the report command never contacts Ollama.
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
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
import time
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tasks import TASKS


MARKER = "__LOCAL_CODING_BENCHMARK_RESULT__"
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = SCRIPT_DIR / "runs"
DEFAULT_BASE_URL = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")


# ---------------------------------------------------------------------------
# General helpers


def iso_now() -> str:
    return dt.datetime.now().astimezone().isoformat()


def normalize_base_url(value: str) -> str:
    value = value.strip()
    if not value:
        value = "http://127.0.0.1:11434"
    if "://" not in value:
        value = "http://" + value
    return value.rstrip("/")


def format_seconds(seconds: float | None) -> str:
    if seconds is None or not math.isfinite(seconds):
        return "--"
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes, remainder = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {remainder:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m"


def truncate(value: str, length: int) -> str:
    value = str(value)
    if len(value) <= length:
        return value
    return value[: max(1, length - 3)] + "..."


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return cleaned[:100] or "unnamed"


def ns_to_seconds(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number / 1_000_000_000 if number else 0.0


def mean_or_none(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


# ---------------------------------------------------------------------------
# Ollama API


def request_json(
    base_url: str,
    path: str,
    payload: dict[str, Any] | None = None,
    timeout: float = 30,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        normalize_base_url(base_url) + path,
        data=body,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Ollama HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach Ollama at {base_url}: {exc.reason}") from exc
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama returned invalid JSON for {path}") from exc


def discover_models(base_url: str, timeout: float) -> list[dict[str, Any]]:
    response = request_json(base_url, "/api/tags", timeout=timeout)
    models = response.get("models")
    if not isinstance(models, list):
        raise RuntimeError("Ollama /api/tags response did not contain a model list")
    return [model for model in models if isinstance(model, dict) and model.get("name")]


def unload_model(base_url: str, model: str) -> None:
    """Ask Ollama to release a model without generating a response."""
    try:
        request_json(
            base_url,
            "/api/generate",
            {"model": model, "prompt": "", "keep_alive": 0},
            timeout=120,
        )
    except Exception as exc:  # unloading is best effort
        print(f"  warning: could not unload {model}: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Progress display


class Progress:
    def __init__(self, total: int) -> None:
        self.total = max(1, total)
        self.done = 0
        self.started = time.monotonic()
        self.is_tty = sys.stdout.isatty()

    def update(self, label: str) -> None:
        self.done += 1
        elapsed = time.monotonic() - self.started
        rate = self.done / elapsed if elapsed > 0 else 0
        eta = (self.total - self.done) / rate if rate > 0 else None
        fraction = min(1.0, self.done / self.total)
        width = 30
        filled = int(width * fraction)
        bar = "#" * filled + "-" * (width - filled)
        line = (
            f"[{bar}] {self.done}/{self.total} ({fraction * 100:5.1f}%) "
            f"{truncate(label, 58):58} ETA {format_seconds(eta)}"
        )
        if self.is_tty:
            print("\r" + line, end="", flush=True)
            if self.done >= self.total:
                print()
        else:
            print(line, flush=True)


# ---------------------------------------------------------------------------
# Model response extraction and isolated test execution


def has_entrypoint(source: str, entrypoint: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.name == entrypoint
        for node in tree.body
    )


def strip_thinking(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)
    # Some clients expose an unfinished thinking block when a response is cut off.
    if "<think>" in cleaned.lower():
        cleaned = re.split(r"<think>", cleaned, flags=re.IGNORECASE, maxsplit=1)[0]
    return cleaned.strip()


def extract_code(text: str, entrypoint: str) -> tuple[str, str | None]:
    """Extract a Python module from a model response."""
    cleaned = strip_thinking(text)
    fenced = re.findall(
        r"```[ \t]*(?:python|py)?[^\n]*\n(.*?)```",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )
    candidates = fenced + [cleaned]

    # A model occasionally adds a short sentence before an unfenced solution.
    # Try each plausible source line before reporting an extraction failure.
    expanded: list[str] = []
    for candidate in candidates:
        expanded.append(candidate.strip())
        lines = candidate.splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ", "class ", "def ", "async def ", "@", "#", '"""', "'''")):
                expanded.append("\n".join(lines[index:]).strip())

    for candidate in expanded:
        if candidate and has_entrypoint(candidate, entrypoint):
            return candidate + "\n", None

    candidate = next((item for item in expanded if item), "")
    if not candidate:
        return "", "The model returned no code"
    try:
        ast.parse(candidate)
        syntax_note = ""
    except SyntaxError as exc:
        syntax_note = f"; syntax error: {exc.msg}"
    return candidate + "\n", f"Could not find top-level `{entrypoint}`{syntax_note}"


def sandbox_command(work_dir: Path) -> list[str]:
    """Build a minimal read-only bubblewrap environment for generated code."""
    bwrap = shutil.which("bwrap")
    if not bwrap:
        raise RuntimeError("bubblewrap (bwrap) is required for the default sandbox")

    command = [bwrap, "--die-with-parent", "--new-session", "--unshare-all"]
    # Python and its standard library are under /usr on this machine.  Keep
    # common runtime directories read-only and expose only the work directory
    # as writable.  Network access is disabled by --unshare-all.
    for root in ("/usr", "/usr/local", "/bin", "/lib", "/lib64", "/etc"):
        if Path(root).exists():
            command.extend(["--ro-bind", root, root])
    command.extend(
        [
            "--proc",
            "/proc",
            "--dev",
            "/dev",
            "--tmpfs",
            "/tmp",
            "--dir",
            "/benchmark",
            "--bind",
            str(work_dir),
            "/benchmark",
            "--chdir",
            "/benchmark",
            "--setenv",
            "HOME",
            "/tmp",
            "--setenv",
            "PATH",
            "/usr/local/bin:/usr/bin:/bin",
            "--setenv",
            "PYTHONDONTWRITEBYTECODE",
            "1",
        ]
    )
    python = sys.executable
    if not (python.startswith("/usr/") or python.startswith("/bin/")):
        python = "/usr/bin/python3"
    command.extend([python, "-B", "test_runner.py"])
    return command


def terminate_process(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            process.kill()
        except ProcessLookupError:
            pass


def run_checker(
    solution: str,
    task: Any,
    work_root: Path,
    timeout: float,
    sandbox_mode: str,
    allow_unsafe: bool,
) -> dict[str, Any]:
    """Run one generated solution and return the trusted checker result."""
    work_dir = Path(tempfile.mkdtemp(prefix=f"{task.slug}-", dir=work_root))
    solution_path = work_dir / "solution.py"
    runner_path = work_dir / "test_runner.py"
    solution_path.write_text(solution, encoding="utf-8")
    runner_path.write_text(
        "import json\n"
        f"{task.checker_source}\n"
        "try:\n"
        "    import solution\n"
        "    result = check(solution)\n"
        "except BaseException as exc:\n"
        "    result = {'passed': 0, 'total': "
        f"{task.test_count!s}"
        ", 'failures': [{'case': 'import', 'error': f'{type(exc).__name__}: {exc}'}]}\n"
        f"print({MARKER!r} + json.dumps(result, sort_keys=True, default=repr))\n",
        encoding="utf-8",
    )

    try:
        if sandbox_mode == "required":
            command = sandbox_command(work_dir)
            cwd = None
        elif sandbox_mode == "auto" and shutil.which("bwrap"):
            command = sandbox_command(work_dir)
            cwd = None
        else:
            command = None
            cwd = None
    except Exception:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise

    if command is None:
        if not allow_unsafe:
            shutil.rmtree(work_dir, ignore_errors=True)
            return {
                "passed": 0,
                "total": task.test_count,
                "failures": [],
                "error": "No sandbox available; rerun with --allow-unsafe-code-execution",
            }
        command = [sys.executable, "-B", "test_runner.py"]
        cwd = str(work_dir)

    process: subprocess.Popen[str] | None = None
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            terminate_process(process)
            stdout, stderr = process.communicate()
            return {
                "passed": 0,
                "total": task.test_count,
                "failures": [],
                "error": f"test timeout after {timeout:g}s",
                "stderr": stderr[-2000:],
            }
    except OSError as exc:
        return {
            "passed": 0,
            "total": task.test_count,
            "failures": [],
            "error": f"could not execute checker: {exc}",
        }
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    marker_lines = [line[len(MARKER) :] for line in stdout.splitlines() if line.startswith(MARKER)]
    if marker_lines:
        try:
            result = json.loads(marker_lines[-1])
            if isinstance(result, dict):
                result.setdefault("passed", 0)
                result.setdefault("total", task.test_count)
                result.setdefault("failures", [])
                if process.returncode != 0 and stderr.strip():
                    result.setdefault("stderr", stderr[-2000:])
                return result
        except json.JSONDecodeError:
            pass

    detail = stderr.strip() or stdout.strip() or f"checker exited with code {process.returncode}"
    return {
        "passed": 0,
        "total": task.test_count,
        "failures": [],
        "error": truncate(detail, 2000),
    }


# ---------------------------------------------------------------------------
# Scoring and report data


def model_metadata(model: dict[str, Any]) -> dict[str, Any]:
    details = model.get("details") or {}
    return {
        "name": model.get("name", ""),
        "digest": model.get("digest", ""),
        "size_bytes": model.get("size", 0),
        "parameter_size": details.get("parameter_size", ""),
        "quantization": details.get("quantization_level", ""),
        "family": details.get("family", ""),
    }


def task_metadata(task: Any) -> dict[str, Any]:
    return {"slug": task.slug, "title": task.title, "test_count": task.test_count}


def task_definitions(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    definitions = metadata.get("tasks")
    if isinstance(definitions, list) and definitions:
        return [item for item in definitions if isinstance(item, dict) and item.get("slug")]
    return [task_metadata(task) for task in TASKS]


def model_definitions(metadata: dict[str, Any], results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    definitions = metadata.get("models")
    if isinstance(definitions, list) and definitions:
        return [item for item in definitions if isinstance(item, dict) and item.get("name")]
    names = []
    for result in results:
        if result.get("model") and result["model"] not in names:
            names.append(result["model"])
    return [{"name": name} for name in names]


def aggregate(
    results: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    tasks = task_definitions(metadata)
    models = model_definitions(metadata, results)
    by_model_task: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        by_model_task[(result.get("model", ""), result.get("task", ""))].append(result)

    summaries: list[dict[str, Any]] = []
    for model in models:
        name = model["name"]
        task_scores: dict[str, float] = {}
        task_records: list[dict[str, Any]] = []
        for task in tasks:
            records = by_model_task.get((name, task["slug"]), [])
            scores = [float(record.get("score", 0) or 0) for record in records]
            task_scores[task["slug"]] = mean_or_none(scores) or 0.0
            task_records.extend(records)

        generation = [float(r["generation_tps"]) for r in task_records if r.get("generation_tps") is not None]
        prompt = [float(r["prompt_tps"]) for r in task_records if r.get("prompt_tps") is not None]
        wall = [float(r["wall_seconds"]) for r in task_records if r.get("wall_seconds") is not None]
        load = [float(r["load_seconds"]) for r in task_records if r.get("load_seconds") is not None and r.get("load_seconds")]
        scores = list(task_scores.values())
        summaries.append(
            {
                **model,
                "overall_score": mean_or_none(scores) or 0.0,
                "task_scores": task_scores,
                "tasks_solved": sum(score >= 99.999 for score in task_scores.values()),
                "tasks_total": len(tasks),
                "passed_tests": sum(int(r.get("passed_tests", 0) or 0) for r in task_records),
                "total_tests": sum(int(r.get("total_tests", 0) or 0) for r in task_records),
                "generation_tps": mean_or_none(generation),
                "prompt_tps": mean_or_none(prompt),
                "wall_seconds": mean_or_none(wall),
                "load_seconds": mean_or_none(load),
                "records": len(task_records),
            }
        )

    return sorted(
        summaries,
        key=lambda item: (item["overall_score"], item.get("generation_tps") or 0),
        reverse=True,
    )


def write_csv_files(
    output_dir: Path,
    results: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
) -> None:
    result_fields = [
        "model",
        "task",
        "task_title",
        "trial",
        "status",
        "passed_tests",
        "total_tests",
        "score",
        "generation_tps",
        "prompt_tps",
        "wall_seconds",
        "load_seconds",
        "eval_count",
        "solution_file",
        "raw_output_file",
        "error",
    ]
    with (output_dir / "results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=result_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    summary_fields = [
        "rank",
        "model",
        "overall_score",
        "tasks_solved",
        "tasks_total",
        "passed_tests",
        "total_tests",
        "generation_tps",
        "prompt_tps",
        "wall_seconds",
        "load_seconds",
        "records",
    ]
    with (output_dir / "model-summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields, extrasaction="ignore")
        writer.writeheader()
        for rank, summary in enumerate(summaries, 1):
            writer.writerow({"rank": rank, **summary})


def svg_header(width: int, height: int, title: str, subtitle: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#111718"/>',
        '<style>text{font-family:DejaVu Sans,Arial,sans-serif}.label{fill:#e7eeee;font-size:17px}.small{fill:#9eafb0;font-size:14px}.value{fill:#f7f7f7;font-size:16px;font-weight:bold}.title{fill:#f7f7f7;font-size:28px;font-weight:bold}.subtitle{fill:#9eafb0;font-size:15px}</style>',
        f'<text x="36" y="42" class="title">{html.escape(title)}</text>',
        f'<text x="36" y="68" class="subtitle">{html.escape(subtitle)}</text>',
    ]


def write_overall_svg(path: Path, summaries: list[dict[str, Any]]) -> None:
    ordered = sorted(summaries, key=lambda item: item["overall_score"], reverse=True)
    width, left, right, top, row_h, bottom = 1500, 430, 80, 100, 48, 75
    height = top + row_h * max(1, len(ordered)) + bottom
    plot_width = width - left - right
    svg = svg_header(width, height, "Coding correctness by model", "Average hidden-test score across tasks | Higher is better")
    for tick in (0, 25, 50, 75, 100):
        x = left + plot_width * tick / 100
        svg.append(f'<line x1="{x:.1f}" y1="{top-16}" x2="{x:.1f}" y2="{height-bottom+4}" stroke="#293536"/>')
        svg.append(f'<text x="{x:.1f}" y="{height-bottom+30}" text-anchor="middle" class="small">{tick}</text>')
    if not ordered:
        svg.append(f'<text x="{left}" y="{top+25}" class="label">No completed benchmark results yet.</text>')
    colors = ["#52c1a2", "#4aabb1", "#548fbd", "#756fba"]
    for index, summary in enumerate(ordered):
        y = top + index * row_h
        score = max(0.0, min(100.0, float(summary["overall_score"])))
        bar_width = plot_width * score / 100
        svg.append(f'<text x="{left-16}" y="{y+22}" text-anchor="end" class="label">{html.escape(truncate(summary["name"], 45))}</text>')
        svg.append(f'<rect x="{left}" y="{y+5}" width="{plot_width}" height="26" rx="4" fill="#1c2728"/>')
        svg.append(f'<rect x="{left}" y="{y+5}" width="{bar_width:.1f}" height="26" rx="4" fill="{colors[min(index // 3, len(colors)-1)]}"/>')
        svg.append(f'<text x="{left+bar_width+12:.1f}" y="{y+24}" class="value">{score:.1f}%</text>')
    svg.append(f'<text x="{left + plot_width / 2:.1f}" y="{height-18}" text-anchor="middle" class="small">average correctness score (%)</text>')
    svg.append("</svg>")
    path.write_text("\n".join(svg) + "\n", encoding="utf-8")


def write_speed_svg(path: Path, summaries: list[dict[str, Any]]) -> None:
    ordered = sorted(summaries, key=lambda item: item.get("generation_tps") or 0, reverse=True)
    values = [float(item.get("generation_tps") or 0) for item in ordered]
    maximum = max(values, default=0.0)
    step = 5 if maximum <= 100 else 10 if maximum <= 200 else 25
    axis_max = max(step, math.ceil(maximum * 1.15 / step) * step)
    width, left, right, top, row_h, bottom = 1500, 430, 80, 100, 48, 75
    height = top + row_h * max(1, len(ordered)) + bottom
    plot_width = width - left - right
    svg = svg_header(width, height, "Generation speed by model", "Ollama eval throughput | Informational; correctness is the primary score")
    for tick in range(0, axis_max + 1, step):
        x = left + plot_width * tick / axis_max
        svg.append(f'<line x1="{x:.1f}" y1="{top-16}" x2="{x:.1f}" y2="{height-bottom+4}" stroke="#293536"/>')
        svg.append(f'<text x="{x:.1f}" y="{height-bottom+30}" text-anchor="middle" class="small">{tick}</text>')
    for index, summary in enumerate(ordered):
        y = top + index * row_h
        value = float(summary.get("generation_tps") or 0)
        bar_width = plot_width * value / axis_max if axis_max else 0
        svg.append(f'<text x="{left-16}" y="{y+22}" text-anchor="end" class="label">{html.escape(truncate(summary["name"], 45))}</text>')
        svg.append(f'<rect x="{left}" y="{y+5}" width="{plot_width}" height="26" rx="4" fill="#1c2728"/>')
        svg.append(f'<rect x="{left}" y="{y+5}" width="{bar_width:.1f}" height="26" rx="4" fill="#c88a55"/>')
        svg.append(f'<text x="{left+bar_width+12:.1f}" y="{y+24}" class="value">{value:.2f}</text>')
    svg.append(f'<text x="{left + plot_width / 2:.1f}" y="{height-18}" text-anchor="middle" class="small">generated tokens per second</text>')
    svg.append("</svg>")
    path.write_text("\n".join(svg) + "\n", encoding="utf-8")


def heat_color(score: float) -> str:
    score = max(0.0, min(100.0, score)) / 100.0
    # Red -> amber -> green, with enough contrast for the white score label.
    if score < 0.5:
        ratio = score * 2
        red, green, blue = 177, int(63 + 75 * ratio), 73
    else:
        ratio = (score - 0.5) * 2
        red, green, blue = int(177 - 110 * ratio), int(138 + 45 * ratio), int(73 + 45 * ratio)
    return f"#{red:02x}{green:02x}{blue:02x}"


def write_heatmap_svg(path: Path, summaries: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    tasks = task_definitions(metadata)
    width = 360 + 125 * max(1, len(tasks))
    left, top, cell_w, row_h, bottom = 340, 145, 120, 44, 70
    height = top + row_h * max(1, len(summaries)) + bottom
    svg = svg_header(width, height, "Task-by-task correctness heatmap", "Each cell is the average hidden-test score for one model and task")
    for index, task in enumerate(tasks):
        x = left + index * cell_w + cell_w / 2
        label = truncate(task["title"], 17)
        svg.append(f'<text x="{x:.1f}" y="{top-22}" text-anchor="middle" class="small" transform="rotate(-35 {x:.1f} {top-22})">{html.escape(label)}</text>')
    for row, summary in enumerate(summaries):
        y = top + row * row_h
        svg.append(f'<text x="{left-14}" y="{y+27}" text-anchor="end" class="label">{html.escape(truncate(summary["name"], 35))}</text>')
        scores = summary.get("task_scores", {})
        for column, task in enumerate(tasks):
            score = float(scores.get(task["slug"], 0) or 0)
            x = left + column * cell_w
            svg.append(f'<rect x="{x}" y="{y+3}" width="{cell_w-5}" height="{row_h-6}" rx="3" fill="{heat_color(score)}"/>')
            svg.append(f'<text x="{x+(cell_w-5)/2:.1f}" y="{y+27}" text-anchor="middle" class="value">{score:.0f}%</text>')
    legend_y = height - 38
    for index, score in enumerate((0, 25, 50, 75, 100)):
        x = left + index * 90
        svg.append(f'<rect x="{x}" y="{legend_y-14}" width="28" height="18" fill="{heat_color(score)}"/>')
        svg.append(f'<text x="{x+35}" y="{legend_y}" class="small">{score}%</text>')
    svg.append("</svg>")
    path.write_text("\n".join(svg) + "\n", encoding="utf-8")


def write_report_html(
    output_dir: Path,
    metadata: dict[str, Any],
    results: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
) -> None:
    settings = metadata.get("settings", {})
    tasks = task_definitions(metadata)
    run_state = "interrupted" if metadata.get("interrupted") else "complete/partial"
    rows: list[str] = []
    for rank, summary in enumerate(summaries, 1):
        speed = "--" if summary.get("generation_tps") is None else f"{summary['generation_tps']:.2f}"
        rows.append(
            "<tr>"
            f"<td>{rank}</td><td><code>{html.escape(summary['name'])}</code></td>"
            f"<td><strong>{summary['overall_score']:.1f}%</strong></td>"
            f"<td>{summary['tasks_solved']}/{summary['tasks_total']}</td>"
            f"<td>{summary['passed_tests']}/{summary['total_tests']}</td>"
            f"<td>{speed}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="6">No benchmark results yet.</td></tr>')

    task_list = "".join(f"<li>{html.escape(task['title'])} ({task['test_count']} hidden cases)</li>" for task in tasks)
    generated = html.escape(str(metadata.get("started", "unknown")))
    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Local coding benchmark</title>
<style>
body {{ background:#111718; color:#e7eeee; font:16px system-ui,sans-serif; max-width:1500px; margin:2rem auto; padding:0 1rem; }}
h1,h2 {{ color:#f7f7f7; }}
.card {{ background:#182122; border:1px solid #293536; border-radius:8px; padding:1rem; margin:1rem 0; overflow-x:auto; }}
img {{ max-width:100%; height:auto; background:#111718; }}
table {{ border-collapse:collapse; width:100%; }}
th,td {{ border-bottom:1px solid #293536; padding:.55rem; text-align:left; }}
th {{ color:#9eafb0; }}
code {{ color:#b9e5dc; }}
.note {{ color:#b8c4c4; }}
</style>
</head>
<body>
<h1>Local LLM coding benchmark</h1>
<p class="note">Run started: <code>{generated}</code> | State: <code>{run_state}</code> | Completed records: <code>{len(results)}</code></p>
<div class="card"><h2>Overall correctness</h2><img src="overall-score.svg" alt="Overall correctness bar chart"></div>
<div class="card"><h2>Task comparison</h2><img src="task-heatmap.svg" alt="Task correctness heatmap"></div>
<div class="card"><h2>Generation speed</h2><img src="generation-speed.svg" alt="Generation speed bar chart"></div>
<div class="card">
<h2>Model ranking</h2>
<table><thead><tr><th>Rank</th><th>Model</th><th>Score</th><th>Tasks solved</th><th>Hidden tests</th><th>Generation tok/s</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
</div>
<div class="card"><h2>Benchmark details</h2>
<ul>{task_list}</ul>
<p class="note">Context: {html.escape(str(settings.get('num_ctx', '--')))} tokens; output cap: {html.escape(str(settings.get('num_predict', '--')))} tokens; trials: {html.escape(str(settings.get('trials', '--')))}; temperature: 0.</p>
<p class="note">Correctness is the primary ranking metric. Speed is reported separately so a fast model cannot compensate for incorrect code.</p>
</div>
</body></html>
"""
    (output_dir / "report.html").write_text(body, encoding="utf-8")


def save_artifacts(
    output_dir: Path,
    metadata: dict[str, Any],
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = aggregate(results, metadata)
    metadata["updated"] = iso_now()
    metadata["result_count"] = len(results)
    payload = {"metadata": metadata, "results": results, "model_summaries": summaries}
    (output_dir / "results.json").write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    write_csv_files(output_dir, results, summaries)
    write_overall_svg(output_dir / "overall-score.svg", summaries)
    write_heatmap_svg(output_dir / "task-heatmap.svg", summaries, metadata)
    write_speed_svg(output_dir / "generation-speed.svg", summaries)
    write_report_html(output_dir, metadata, results, summaries)
    return summaries


# ---------------------------------------------------------------------------
# Benchmark run


def choose_models(
    discovered: list[dict[str, Any]],
    requested: list[str] | None,
    excluded: list[str] | None,
) -> list[dict[str, Any]]:
    excluded = excluded or []
    if requested:
        by_name = {model["name"]: model for model in discovered}
        missing = [name for name in requested if name not in by_name]
        if missing:
            raise RuntimeError("Requested model tag(s) not found in Ollama: " + ", ".join(missing))
        models = [by_name[name] for name in requested]
    else:
        models = discovered
    if excluded:
        models = [model for model in models if not any(re.search(pattern, model["name"]) for pattern in excluded)]
    return models


def chat_model(
    base_url: str,
    model: str,
    task: Any,
    num_ctx: int,
    num_predict: int,
    keep_alive: str,
    api_timeout: float,
) -> tuple[dict[str, Any], str, float]:
    system = (
        "You are completing one isolated Python coding benchmark task. "
        "Return only one complete Python module, preferably in a single ```python code block. "
        "Do not explain the solution, do not use third-party packages, do not read files, "
        "use the network, spawn processes, or perform work at import time. "
        f"The required top-level entrypoint is `{task.entrypoint}`."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": task.prompt},
        ],
        "stream": False,
        # Disable Ollama's default thinking mode so the output budget is spent
        # on the requested code module rather than a separate reasoning trace.
        "think": False,
        "keep_alive": keep_alive,
        "options": {
            "num_ctx": num_ctx,
            "num_predict": num_predict,
            "temperature": 0,
            "seed": 42,
        },
    }
    started = time.monotonic()
    response = request_json(base_url, "/api/chat", payload, timeout=api_timeout)
    wall_seconds = time.monotonic() - started
    message = response.get("message") or {}
    text = message.get("content") or response.get("response") or ""
    return response, str(text), wall_seconds


def result_from_response(
    response: dict[str, Any],
    text: str,
    wall_seconds: float,
    task: Any,
    model: dict[str, Any],
    trial: int,
    solution_file: str,
    raw_output_file: str,
    checker: dict[str, Any],
) -> dict[str, Any]:
    eval_count = response.get("eval_count")
    eval_duration = ns_to_seconds(response.get("eval_duration"))
    prompt_count = response.get("prompt_eval_count")
    prompt_duration = ns_to_seconds(response.get("prompt_eval_duration"))
    generation_tps = None
    prompt_tps = None
    if eval_count is not None and eval_duration:
        generation_tps = float(eval_count) / eval_duration
    if prompt_count is not None and prompt_duration:
        prompt_tps = float(prompt_count) / prompt_duration
    passed = int(checker.get("passed", 0) or 0)
    total = int(checker.get("total", task.test_count) or task.test_count)
    total = max(total, 1)
    score = max(0.0, min(100.0, 100.0 * passed / total))
    error = checker.get("error")
    return {
        "model": model.get("name", ""),
        "model_digest": model.get("digest", ""),
        "task": task.slug,
        "task_title": task.title,
        "trial": trial,
        "status": "passed" if not error and passed == total else "failed",
        "passed_tests": passed,
        "total_tests": total,
        "score": score,
        "generation_tps": generation_tps,
        "prompt_tps": prompt_tps,
        "wall_seconds": wall_seconds,
        "load_seconds": ns_to_seconds(response.get("load_duration")),
        "eval_count": eval_count,
        "solution_file": solution_file,
        "raw_output_file": raw_output_file,
        "failures": checker.get("failures", []),
        "error": error,
    }


def failed_result(
    model: dict[str, Any],
    task: Any,
    trial: int,
    error: str,
    raw_output_file: str = "",
) -> dict[str, Any]:
    return {
        "model": model.get("name", ""),
        "model_digest": model.get("digest", ""),
        "task": task.slug,
        "task_title": task.title,
        "trial": trial,
        "status": "error",
        "passed_tests": 0,
        "total_tests": task.test_count,
        "score": 0.0,
        "generation_tps": None,
        "prompt_tps": None,
        "wall_seconds": None,
        "load_seconds": None,
        "eval_count": None,
        "solution_file": "",
        "raw_output_file": raw_output_file,
        "failures": [],
        "error": error,
    }


def run_benchmark(args: argparse.Namespace) -> int:
    base_url = normalize_base_url(args.base_url)
    if args.sandbox == "required" and not shutil.which("bwrap"):
        raise RuntimeError("bwrap is not installed; use --sandbox off --allow-unsafe-code-execution only if you accept the risk")
    if args.sandbox == "off" and not args.allow_unsafe_code_execution:
        raise RuntimeError("--sandbox off requires --allow-unsafe-code-execution")

    discovered = discover_models(base_url, args.api_timeout)
    models = choose_models(discovered, args.model, args.exclude)
    if not models:
        raise RuntimeError("No Ollama models matched the requested selection")

    selected_tasks = TASKS
    if args.task:
        wanted = set(args.task)
        unknown = sorted(wanted - {task.slug for task in TASKS})
        if unknown:
            raise RuntimeError("Unknown task slug(s): " + ", ".join(unknown))
        selected_tasks = [task for task in TASKS if task.slug in wanted]

    if args.output:
        output_dir = Path(args.output).expanduser().resolve()
    else:
        output_dir = DEFAULT_OUTPUT_ROOT / dt.datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    solutions_dir = output_dir / "solutions"
    work_root = output_dir / "work"
    raw_dir.mkdir()
    solutions_dir.mkdir()
    work_root.mkdir()

    metadata: dict[str, Any] = {
        "started": iso_now(),
        "interrupted": False,
        "backend": "Ollama /api/chat",
        "base_url": base_url,
        "settings": {
            "num_ctx": args.num_ctx,
            "num_predict": args.num_predict,
            "trials": args.trials,
            "temperature": 0,
            "seed": 42,
            "thinking": False,
            "checker_timeout": args.checker_timeout,
            "sandbox": args.sandbox,
        },
        "hardware_note": "Use the machine's current hardware; this is recorded for the run, not assumed by the scorer.",
        "models": [model_metadata(model) for model in models],
        "tasks": [task_metadata(task) for task in selected_tasks],
    }
    results: list[dict[str, Any]] = []
    total_jobs = len(models) * len(selected_tasks) * args.trials
    progress = Progress(total_jobs)
    print(f"Discovered {len(models)} Ollama model tag(s) and {len(selected_tasks)} coding task(s).")
    print(f"Planned jobs: {total_jobs}. Correctness is scored from hidden tests.")
    print(f"Results will be written to: {output_dir}")

    try:
        for model_index, model in enumerate(models, 1):
            model_name = model["name"]
            print(f"\nModel {model_index}/{len(models)}: {model_name}")
            try:
                for task in selected_tasks:
                    for trial in range(1, args.trials + 1):
                        raw_name = f"{model_index:02d}-{safe_filename(model_name)}-{task.slug}-trial-{trial}.txt"
                        solution_name = f"{model_index:02d}-{safe_filename(model_name)}-{task.slug}-trial-{trial}.py"
                        raw_path = raw_dir / raw_name
                        solution_path = solutions_dir / solution_name
                        try:
                            response, text, wall_seconds = chat_model(
                                base_url,
                                model_name,
                                task,
                                args.num_ctx,
                                args.num_predict,
                                args.keep_alive,
                                args.api_timeout,
                            )
                            raw_path.write_text(text, encoding="utf-8")
                            solution, extraction_error = extract_code(text, task.entrypoint)
                            if solution:
                                solution_path.write_text(solution, encoding="utf-8")
                            if extraction_error:
                                checker = {"passed": 0, "total": task.test_count, "failures": [], "error": extraction_error}
                            else:
                                checker = run_checker(
                                    solution,
                                    task,
                                    work_root,
                                    args.checker_timeout,
                                    args.sandbox,
                                    args.allow_unsafe_code_execution,
                                )
                            result = result_from_response(
                                response,
                                text,
                                wall_seconds,
                                task,
                                model,
                                trial,
                                str(solution_path.relative_to(output_dir)) if solution else "",
                                str(raw_path.relative_to(output_dir)),
                                checker,
                            )
                        except Exception as exc:
                            raw_path.write_text(f"BENCHMARK ERROR\n{type(exc).__name__}: {exc}\n", encoding="utf-8")
                            result = failed_result(model, task, trial, f"{type(exc).__name__}: {exc}", str(raw_path.relative_to(output_dir)))
                        results.append(result)
                        progress.update(f"{model_name} / {task.slug} / trial {trial}")
                        save_artifacts(output_dir, metadata, results)
            finally:
                unload_model(base_url, model_name)
    except KeyboardInterrupt:
        metadata["interrupted"] = True
        print("\nBenchmark interrupted. Partial results and graphs were saved.", file=sys.stderr)
    finally:
        metadata["finished"] = iso_now()
        save_artifacts(output_dir, metadata, results)
        shutil.rmtree(work_root, ignore_errors=True)

    summaries = aggregate(results, metadata)
    print(f"\nFinished {len(results)}/{total_jobs} job(s).")
    print(f"HTML report: {output_dir / 'report.html'}")
    if summaries:
        print(f"Current leader: {summaries[0]['name']} ({summaries[0]['overall_score']:.1f}%)")
    return 0


# ---------------------------------------------------------------------------
# CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark local Ollama models on coding tasks without third-party Python dependencies.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="discover local models and run the coding benchmark")
    run.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Ollama base URL (default: OLLAMA_HOST or localhost:11434)")
    run.add_argument("--model", action="append", help="run only this exact Ollama tag; repeat for multiple tags")
    run.add_argument("--exclude", action="append", help="regular expression for model tags to skip; repeat as needed")
    run.add_argument("--task", action="append", help="run only this task slug; repeat as needed")
    run.add_argument("--trials", type=int, default=1, help="independent generations per task (default: 1)")
    run.add_argument("--num-ctx", type=int, default=8192, help="Ollama context size (default: 8192)")
    run.add_argument("--num-predict", type=int, default=1200, help="maximum output tokens (default: 1200)")
    run.add_argument("--keep-alive", default="10m", help="keep each model loaded between its tasks (default: 10m)")
    run.add_argument("--api-timeout", type=float, default=900, help="seconds allowed for each Ollama request")
    run.add_argument("--checker-timeout", type=float, default=10, help="seconds allowed for each generated solution's tests")
    run.add_argument("--output", help="result directory; default is ./runs/YYYY-MM-DD_HH-MM-SS")
    run.add_argument("--sandbox", choices=("required", "auto", "off"), default="required", help="how to execute generated code (default: required bubblewrap sandbox)")
    run.add_argument("--allow-unsafe-code-execution", action="store_true", help="required when running without bubblewrap; generated code is untrusted")

    report = subparsers.add_parser("report", help="rebuild graphs and HTML from an existing results.json")
    report.add_argument("results_json", type=Path, help="path to a benchmark results.json")
    report.add_argument("--output", help="directory for regenerated report files; defaults beside results.json")
    return parser


def report_from_file(args: argparse.Namespace) -> int:
    results_path = args.results_json.expanduser().resolve()
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("results.json must contain an object")
    results = payload.get("results", [])
    metadata = payload.get("metadata", {})
    if not isinstance(results, list) or not isinstance(metadata, dict):
        raise RuntimeError("results.json has an invalid metadata/results shape")
    output_dir = Path(args.output).expanduser().resolve() if args.output else results_path.parent
    summaries = save_artifacts(output_dir, metadata, results)
    print(f"Report written to: {output_dir / 'report.html'}")
    print(f"Models represented: {len(summaries)}")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "run":
        if args.trials < 1 or args.num_ctx < 1 or args.num_predict < 1 or args.api_timeout <= 0 or args.checker_timeout <= 0:
            raise SystemExit("numeric run options must be positive")
        return run_benchmark(args)
    if args.command == "report":
        return report_from_file(args)
    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
