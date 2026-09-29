#!/usr/bin/env python3
"""Comprehensive, repeatable benchmark suite for every model installed in Ollama.

Each model/test pair is run ``--iterations`` times (five by default).  The
slowest/failed run is removed independently for every model and test before
summary statistics are calculated.  Ollama's API timings are used instead of
counting words as tokens.

This is a performance benchmark with content-oriented prompts.  It does not
pretend to assign a subjective quality grade to generated text; the responses
are retained in the JSON report for qualitative review.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TESTS: list[dict[str, Any]] = [
    {
        "id": "speed_brief",
        "name": "Brief Response Speed (50 tokens)",
        "type": "speed",
        "prompt": "Write a one-sentence summary of photosynthesis.",
        "max_tokens": 60,
    },
    {
        "id": "speed_medium",
        "name": "Medium Response Speed (200 tokens)",
        "type": "speed",
        "prompt": "Explain the causes and effects of the Industrial Revolution in about 150 words, covering economic, social, and technological factors.",
        "max_tokens": 250,
    },
    {
        "id": "speed_long",
        "name": "Long Response Speed (350+ tokens)",
        "type": "speed",
        "prompt": "Write a comprehensive essay comparing centralized and decentralized systems in terms of security, scalability, fault tolerance, and user experience. Include at least three real-world examples for each architecture type. Aim for around 400 words.",
        "max_tokens": 420,
    },
    {
        "id": "logic_reasoning",
        "name": "Logic & Reasoning",
        "type": "quality",
        "prompt": """Here is the puzzle:
- All bloops are bleeps.
- Some bleeps are blips.
- No blips are blops.
- All blops are bloinks.

Question: If something is a bloop, which of the following must be true?
A) It is a blip.
B) It is not a blop.
C) It is a bloink.
D) It is a bleep.
E) Both B and D.

Explain your reasoning step by step, then give your final answer as: ANSWER: X""",
        "max_tokens": 300,
    },
    {
        "id": "math_reasoning",
        "name": "Mathematical Reasoning",
        "type": "quality",
        "prompt": """A restaurant has tables for 2, 4, and 6 people. There are 15 tables total, with 8 of them being 2-seaters. The number of 4-seaters is one-third the number of 6-seaters. Each table is fully occupied on a busy night.

How many guests can be seated when all tables are full?

Show your working step by step, then answer: ANSWER: X""",
        "max_tokens": 300,
    },
    {
        "id": "factual_knowledge",
        "name": "Factual Knowledge Recall",
        "type": "quality",
        "prompt": """For each statement, say TRUE or FALSE and give a one-sentence explanation:
1. The Great Wall of China is visible from space with the naked eye.
2. Water expands when it freezes, which is why ice floats.
3. Shakespeare wrote 37 plays.
4. The human body contains approximately 206 bones in an adult.
5. Mercury (the planet) is closest to the Sun on average (even though Venus has the highest surface temp).""",
        "max_tokens": 400,
    },
    {
        "id": "python_coding",
        "name": "Python Coding",
        "type": "quality",
        "prompt": """Write a Python function called `merge_sorted_arrays` that takes two sorted lists of integers and returns a new sorted list containing all elements from both. Use an efficient algorithm (not just sort()). Include type hints, a docstring with examples, and error handling for invalid inputs. Return valid Python code only.""",
        "max_tokens": 400,
    },
    {
        "id": "html_coding",
        "name": "HTML/CSS/JS Coding",
        "type": "quality",
        "prompt": """Write a single HTML file that creates a responsive card component showing:
- A title field
- A description paragraph
- A styled button with hover effects
Use only inline CSS (no external dependencies). The design should be modern and clean. Return valid HTML code.""",
        "max_tokens": 400,
    },
    {
        "id": "creative_writing",
        "name": "Creative Writing & Style",
        "type": "quality",
        "prompt": """Write a short creative piece (about 200 words) in the style of magical realism. The premise: An elderly clockmaker discovers that his clocks don't just measure time — they can briefly show glimpses of alternate timelines. Focus on sensory detail and atmosphere.""",
        "max_tokens": 280,
    },
    {
        "id": "summarization",
        "name": "Information Extraction & Summarization",
        "type": "quality",
        "prompt": """Read the following excerpt and extract all key entities and their attributes into a structured format:

\"The European Space Agency's Euclid mission successfully launched on July 1, 2023 from Cape Canaveral in Florida aboard a SpaceX Falcon 9 rocket. The $1.5 billion telescope will spend six years mapping dark matter and dark energy across 10,000 square degrees of sky — roughly a third of the observable universe. Project scientist Paolo Cavallotti noted that Euclid will study how structure in the universe has evolved over the past 10 billion years.\"

Return: Launch Date, Location, Launcher, Cost, Mission Duration, Target Area, Primary Goals, Key Person.""",
        "max_tokens": 250,
    },
    {
        "id": "instruction_following",
        "name": "Complex Instruction Following",
        "type": "quality",
        "prompt": """Create a table comparing 4 types of renewable energy (solar, wind, hydro, geothermal) across these dimensions: efficiency (%), cost per kWh ($), carbon footprint (gCO2/kWh), land use impact, and availability reliability. Format as Markdown. After the table, add a one-paragraph recommendation for a coastal region with high winds, abundant sunshine, but limited freshwater supply.""",
        "max_tokens": 350,
    },
    {
        "id": "context_understanding",
        "name": "Context Understanding (with long prompt)",
        "type": "quality",
        "prompt": """Consider: A company has the following employees distributed across departments and shifts:

- Engineering (14 people): Alice(B, 3yr), Bob(A, 5yr), Carol(C, 2yr), Dave(D, 7yr), Eve(A, 1yr), Frank(B, 4yr), Grace(C, 6yr), Hank(A, 2yr), Iris(D, 3yr), Jack(B, 8yr), Kate(C, 5yr), Leo(A, 1yr), Mia(D, 4yr), Noah(B, 3yr)
- Marketing (9 people): Oscar(A, 2yr), Penny(C, 6yr), Quinn(D, 1yr), Rita(B, 7yr), Sam(A, 3yr), Tina(C, 5yr), Uma(B, 2yr), Victor(D, 4yr), Wendy(A, 8yr)
- Sales (7 people): Xander(C, 4yr), Yuki(A, 1yr), Zane(C, 6yr), Alice(B, 3yr), Bob(D, 5yr), Carol(A, 2yr), Dave(B, 7yr)

Where shift letters A-D are Morning/Afternoon/Evening/Overnight. Numbers in brackets indicate years at company.

Questions:
1. How many total employees are there?
2. Which department has the median average tenure?
3. Who is in Engineering with 5+ years and on a non-Morning shift? List them.""",
        "max_tokens": 300,
    },
]


class BenchmarkError(RuntimeError):
    """An API or local benchmark error."""


def normalize_host(value: str) -> str:
    value = value.strip()
    if not value:
        return "http://127.0.0.1:11434"
    if "://" not in value:
        value = "http://" + value
    return value.rstrip("/")


def api_json(host: str, endpoint: str, payload: dict[str, Any] | None = None, timeout: float = 30) -> dict[str, Any]:
    url = host + endpoint
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if data is None else "POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise BenchmarkError(f"HTTP {exc.code} from {endpoint}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise BenchmarkError(f"Could not reach Ollama at {url}: {exc}") from exc
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        raise BenchmarkError(f"Invalid JSON from {endpoint}: {body[:300]}") from exc
    if not isinstance(value, dict):
        raise BenchmarkError(f"Unexpected response from {endpoint}")
    if value.get("error"):
        raise BenchmarkError(str(value["error"]))
    return value


def ns_seconds(value: Any) -> float:
    try:
        return float(value or 0) / 1_000_000_000
    except (TypeError, ValueError):
        return 0.0


def loaded_model_names(host: str) -> list[str]:
    try:
        data = api_json(host, "/api/ps", timeout=10)
    except BenchmarkError:
        return []
    return [str(item.get("name")) for item in data.get("models", []) if item.get("name")]


def stop_loaded_models(host: str) -> None:
    """Unload models so that every iteration starts cold."""
    for model in loaded_model_names(host):
        try:
            subprocess.run(
                ["ollama", "stop", model],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass


def installed_models(host: str) -> list[dict[str, Any]]:
    data = api_json(host, "/api/tags", timeout=30)
    models = data.get("models", [])
    if not isinstance(models, list):
        raise BenchmarkError("Ollama returned no model list")
    return [m for m in models if isinstance(m, dict) and m.get("name")]


def select_tests(test_filter: str | None) -> list[dict[str, Any]]:
    if not test_filter:
        return TESTS
    wanted = {part.strip() for part in test_filter.split(",") if part.strip()}
    selected = [test for test in TESTS if test["id"] in wanted]
    unknown = wanted - {test["id"] for test in TESTS}
    if unknown:
        raise BenchmarkError("Unknown test ID(s): " + ", ".join(sorted(unknown)))
    if not selected:
        raise BenchmarkError("No tests selected")
    return selected


def select_models(models: list[dict[str, Any]], model_filter: str | None) -> list[dict[str, Any]]:
    if not model_filter:
        return models
    wanted = [part.strip() for part in model_filter.split(",") if part.strip()]
    by_name = {str(model["name"]): model for model in models}
    missing = [name for name in wanted if name not in by_name]
    if missing:
        raise BenchmarkError("Model(s) not found in Ollama: " + ", ".join(missing))
    return [by_name[name] for name in wanted]


def result_failure(model: str, test: dict[str, Any], iteration: int, run_id: int, started: float, error: str) -> dict[str, Any]:
    wall = time.monotonic() - started
    return {
        "run_id": run_id,
        "model": model,
        "iteration": iteration,
        "test_id": test["id"],
        "success": False,
        "error": error[:1000],
        "score": 0.0,
        "generation_tok_per_sec": 0.0,
        "prompt_tok_per_sec": 0.0,
        "tokens_generated": 0,
        "prompt_tokens": 0,
        "generation_time_sec": 0.0,
        "prompt_eval_time_sec": 0.0,
        "load_time_sec": 0.0,
        "total_time_sec": round(wall, 3),
        "wall_time_sec": round(wall, 3),
        "response": "",
    }


def run_model(
    host: str,
    model: str,
    test: dict[str, Any],
    iteration: int,
    run_id: int,
    timeout: float,
    keep_alive: str,
    think: bool,
    context: int,
) -> dict[str, Any]:
    started = time.monotonic()
    payload: dict[str, Any] = {
        "model": model,
        "prompt": test["prompt"],
        "stream": False,
        "think": think,
        "keep_alive": keep_alive,
        "options": {
            "seed": 42,
            "temperature": 0,
            "num_ctx": context,
            "num_predict": test["max_tokens"],
        },
    }
    try:
        data = api_json(host, "/api/generate", payload, timeout=timeout)
    except BenchmarkError as exc:
        return result_failure(model, test, iteration, run_id, started, str(exc))

    wall = time.monotonic() - started
    eval_count = int(data.get("eval_count") or 0)
    prompt_count = int(data.get("prompt_eval_count") or 0)
    eval_time = ns_seconds(data.get("eval_duration"))
    prompt_time = ns_seconds(data.get("prompt_eval_duration"))
    load_time = ns_seconds(data.get("load_duration"))
    total_time = ns_seconds(data.get("total_duration")) or wall
    generation_tps = eval_count / eval_time if eval_time > 0 else 0.0
    prompt_tps = prompt_count / prompt_time if prompt_time > 0 else 0.0
    response = str(data.get("response") or "")
    success = bool(data.get("done", False)) and (eval_count > 0 or bool(response))

    result: dict[str, Any] = {
        "run_id": run_id,
        "model": model,
        "iteration": iteration,
        "test_id": test["id"],
        "success": success,
        "error": "" if success else "Empty or incomplete response",
        # Higher is better.  This is the outlier-removal metric for every test.
        "score": round(generation_tps, 3),
        "generation_tok_per_sec": round(generation_tps, 3),
        "prompt_tok_per_sec": round(prompt_tps, 3),
        "tokens_generated": eval_count,
        "prompt_tokens": prompt_count,
        "generation_time_sec": round(eval_time, 3),
        "prompt_eval_time_sec": round(prompt_time, 3),
        "load_time_sec": round(load_time, 3),
        "total_time_sec": round(total_time, 3),
        "wall_time_sec": round(wall, 3),
        "response": response,
    }
    if data.get("thinking"):
        result["thinking"] = str(data["thinking"])
    return result


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def remove_worst(raw_results: list[dict[str, Any]], models: list[str], tests: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Remove exactly one worst run from every model/test group."""
    removed: list[dict[str, Any]] = []
    removed_ids: set[int] = set()
    for model in models:
        for test in tests:
            group = [
                result for result in raw_results
                if result["model"] == model and result["test_id"] == test["id"]
            ]
            if not group:
                continue
            # Failed runs are worse than successful runs.  Among failures,
            # discard the longest one; among successes, discard lowest speed.
            worst = min(
                group,
                key=lambda result: (
                    1 if result["success"] else 0,
                    result["score"] if result["success"] else 0.0,
                    -result["wall_time_sec"],
                ),
            )
            removed_ids.add(int(worst["run_id"]))
            removed.append({
                "model": model,
                "test_id": test["id"],
                "run_id": worst["run_id"],
                "score": worst["score"],
                "success": worst["success"],
                "tokens_generated": worst["tokens_generated"],
                "total_time_sec": worst["total_time_sec"],
                "error": worst.get("error", ""),
            })
    retained = [result for result in raw_results if int(result["run_id"]) not in removed_ids]
    return retained, removed


def average(values: list[float]) -> float:
    return round(statistics.mean(values), 3) if values else 0.0


def summarize(retained: list[dict[str, Any]], raw: list[dict[str, Any]], models: list[str], tests: list[dict[str, Any]]) -> dict[str, Any]:
    by_model_test: dict[str, dict[str, Any]] = {}
    for model in models:
        by_model_test[model] = {}
        for test in tests:
            group = [r for r in retained if r["model"] == model and r["test_id"] == test["id"]]
            raw_group = [r for r in raw if r["model"] == model and r["test_id"] == test["id"]]
            by_model_test[model][test["id"]] = {
                "name": test["name"],
                "type": test["type"],
                "raw_runs": len(raw_group),
                "retained_runs": len(group),
                "successful_retained_runs": sum(1 for r in group if r["success"]),
                "avg_score_tok_per_sec": average([r["score"] for r in group if r["success"]]),
                "avg_tokens_generated": average([float(r["tokens_generated"]) for r in group if r["success"]]),
                "avg_generation_time_sec": average([r["generation_time_sec"] for r in group if r["success"]]),
                "avg_total_time_sec": average([r["total_time_sec"] for r in group if r["success"]]),
            }

    speed_ids = {test["id"] for test in tests if test["type"] == "speed"}
    overall: dict[str, Any] = {}
    for model in models:
        speed_runs = [r for r in retained if r["model"] == model and r["test_id"] in speed_ids and r["success"]]
        all_runs = [r for r in retained if r["model"] == model]
        overall[model] = {
            "raw_runs": len([r for r in raw if r["model"] == model]),
            "retained_runs": len(all_runs),
            "successful_retained_runs": sum(1 for r in all_runs if r["success"]),
            "average_speed_tok_per_sec": average([r["score"] for r in speed_runs]),
            "average_total_time_sec": average([r["total_time_sec"] for r in all_runs if r["success"]]),
        }
    return {"by_model_test": by_model_test, "overall": overall}


def short_model_name(name: str) -> str:
    return name if len(name) <= 62 else name[:59] + "..."


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark every local Ollama model")
    parser.add_argument("--iterations", type=int, default=5, help="Runs per model/test (default: 5)")
    parser.add_argument("--models", help="Comma-separated exact model names; default is every installed model")
    parser.add_argument("--tests", help="Comma-separated test IDs; default is the full suite")
    parser.add_argument("--output", help="JSON report path; default is Tests/YYYY-MM-DD/local-llm-benchmark/")
    parser.add_argument("--timeout", type=float, default=900, help="Per-request timeout in seconds")
    parser.add_argument("--context", type=int, default=65536, help="Context size used for every request")
    parser.add_argument("--keep-alive", default="10m", help="Keep model loaded between tests in an iteration")
    parser.add_argument("--think", action="store_true", help="Enable model thinking; default is disabled for comparability")
    args = parser.parse_args()

    if args.iterations < 1:
        parser.error("--iterations must be at least 1")
    if args.context < 1:
        parser.error("--context must be positive")

    host = normalize_host(os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"))
    try:
        version = api_json(host, "/api/version", timeout=10).get("version", "unknown")
        all_model_records = installed_models(host)
        selected_records = select_models(all_model_records, args.models)
        tests = select_tests(args.tests)
    except BenchmarkError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    models = [str(record["name"]) for record in selected_records]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_output_dir = Path.home() / "Projects" / "Tests" / datetime.now().strftime("%Y-%m-%d") / "local-llm-benchmark"
    output_path = Path(args.output).expanduser() if args.output else default_output_dir / f"benchmark_results_{timestamp}.json"
    started_at = datetime.now(timezone.utc).isoformat()
    total_runs = len(models) * len(tests) * args.iterations
    raw_results: list[dict[str, Any]] = []
    run_id = 0

    report_base: dict[str, Any] = {
        "complete": False,
        "started_at": started_at,
        "ollama_host": host,
        "ollama_version": version,
        "iterations_requested": args.iterations,
        "context_size": args.context,
        "thinking_enabled": args.think,
        "score_metric": "generation_tok_per_sec (higher is better); failed runs score 0",
        "outlier_policy": "remove one worst run independently from every model/test group",
        "quality_note": "Quality prompts are included and responses are retained, but no subjective quality grade is assigned.",
        "models": selected_records,
        "tests": tests,
        "raw_results": raw_results,
    }
    atomic_write_json(output_path, report_base)

    print("=" * 88, flush=True)
    print("  LOCAL OLLAMA LLM BENCHMARK", flush=True)
    print(f"  Ollama: {version} | API: {host}", flush=True)
    print(f"  Models: {len(models)} | Tests: {len(tests)} | Iterations: {args.iterations} | Requests: {total_runs}", flush=True)
    print(f"  Context: {args.context} | Thinking: {'on' if args.think else 'off'} | Score: generation tok/s", flush=True)
    print(f"  Report: {output_path}", flush=True)
    print("=" * 88, flush=True)
    for index, record in enumerate(selected_records, 1):
        print(f"  {index:2d}. {record['name']} ({record.get('details', {}).get('quantization_level', '?')}, {record.get('size', 0) / 1e9:.1f} GB)", flush=True)
    print("\nEvery iteration unloads the previous model before starting, then keeps the current model warm across its tests.\n", flush=True)

    try:
        for model_index, model in enumerate(models, 1):
            print(f"\n{'=' * 72}\nMODEL {model_index}/{len(models)}: {model}\n{'=' * 72}", flush=True)
            for iteration in range(1, args.iterations + 1):
                stop_loaded_models(host)
                print(f"  Iteration {iteration}/{args.iterations} (cold model load)", flush=True)
                for test_index, test in enumerate(tests, 1):
                    run_id += 1
                    result = run_model(
                        host,
                        model,
                        test,
                        iteration,
                        run_id,
                        args.timeout,
                        args.keep_alive,
                        args.think,
                        args.context,
                    )
                    raw_results.append(result)
                    if result["success"]:
                        print(
                            f"    {test_index:2d}/{len(tests)} {test['id']:<24} "
                            f"{result['score']:7.2f} tok/s | "
                            f"{result['tokens_generated']:4d} tok | "
                            f"{result['total_time_sec']:7.2f}s"
                            f"{' (load ' + format(result['load_time_sec'], '.1f') + 's)' if result['load_time_sec'] else ''}",
                            flush=True,
                        )
                    else:
                        print(f"    {test_index:2d}/{len(tests)} {test['id']:<24} FAILED: {result['error'][:120]}", flush=True)
                    # A valid partial report is useful if a long benchmark is interrupted.
                    report_base["raw_results"] = raw_results
                    report_base["requests_completed"] = len(raw_results)
                    atomic_write_json(output_path, report_base)
    except KeyboardInterrupt:
        print("\nInterrupted; partial results were saved.", file=sys.stderr, flush=True)
        return 130
    finally:
        stop_loaded_models(host)

    retained, removed = remove_worst(raw_results, models, tests)
    report_base.update({
        "complete": True,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "requests_completed": len(raw_results),
        "removed_worst": removed,
        "retained_results": retained,
        "summary": summarize(retained, raw_results, models, tests),
    })
    atomic_write_json(output_path, report_base)

    print("\n" + "=" * 88, flush=True)
    print("  COMPLETE — ONE WORST RUN REMOVED PER MODEL/TEST", flush=True)
    print("=" * 88, flush=True)
    ranking = sorted(
        report_base["summary"]["overall"].items(),
        key=lambda item: item[1]["average_speed_tok_per_sec"],
        reverse=True,
    )
    print("\n  Overall ranking (retained speed-test generation throughput):", flush=True)
    for position, (model, summary) in enumerate(ranking, 1):
        print(
            f"  #{position:2d} {short_model_name(model):<62} "
            f"{summary['average_speed_tok_per_sec']:8.2f} tok/s | "
            f"{summary['successful_retained_runs']}/{summary['retained_runs']} retained successful",
            flush=True,
        )
    print(f"\n  Raw runs: {len(raw_results)} | Retained: {len(retained)} | Removed: {len(removed)}", flush=True)
    print(f"  JSON report: {output_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
