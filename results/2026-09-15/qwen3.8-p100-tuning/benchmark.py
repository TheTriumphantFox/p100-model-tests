#!/usr/bin/env python3
"""Benchmark Qwen3.8 27B Q4_K_M Vulkan tuning variants on two P100s."""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent
MODEL = Path("/var/lib/ollama/blobs/sha256-f5f1dd8920d417aac2718b0bda3403da274301efdd6760b4f0f4b864ff2ad57d")
SERVER = "/usr/lib/ollama/llama-server"
PORT = 18080
BASE_ENV = {
    "GGML_BACKEND_PATH": "/usr/lib/ollama/vulkan/libggml-vulkan.so",
    # Hide the Ryzen iGPU and retain the x16 P100 before the x4 P100.
    "GGML_VK_VISIBLE_DEVICES": "1,2",
}
BASE_ARGS = [
    SERVER,
    "--model", str(MODEL),
    "--host", "127.0.0.1",
    "--port", str(PORT),
    "-c", "4096",
    "-np", "1",
    "-b", "512",
    "-ub", "512",
    "--device", "Vulkan0,Vulkan1",
    "-ngl", "all",
    "--flash-attn", "on",
    "--no-jinja",
    "--no-webui",
    "--offline",
]
VARIANTS = [
    {"name": "baseline-layer-50-50", "env": {}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "force-mmvq", "env": {"GGML_VK_FORCE_MMVQ": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "disable-mmvq", "env": {"GGML_VK_DISABLE_MMVQ": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "disable-fusion", "env": {"GGML_VK_DISABLE_FUSION": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "disable-async", "env": {"GGML_VK_DISABLE_ASYNC": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "layer-55-45", "env": {}, "args": ["--split-mode", "layer", "--tensor-split", "55,45"]},
    {"name": "layer-60-40", "env": {}, "args": ["--split-mode", "layer", "--tensor-split", "60,40"]},
    {"name": "row-50-50", "env": {}, "args": ["--split-mode", "row", "--tensor-split", "1,1", "--main-gpu", "0"]},
]


def request(path: str, payload: dict | None = None, timeout: float = 30) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def wait_ready(proc: subprocess.Popen, timeout: float = 90) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited with status {proc.returncode}")
        try:
            request("/health", timeout=1)
            return
        except (OSError, urllib.error.URLError, TimeoutError):
            time.sleep(0.5)
    raise TimeoutError("server did not become ready")


def completion(tokens: int, seed: int) -> dict:
    return request(
        "/completion",
        {
            "prompt": "Continue this numbered list with detailed one-sentence facts about electrical engineering:\n1.",
            "n_predict": tokens,
            "temperature": 0,
            "seed": seed,
            "ignore_eos": True,
            "cache_prompt": False,
        },
        timeout=120,
    )


def run_variant(variant: dict) -> dict:
    log_path = OUT / f"{variant['name']}.log"
    env = os.environ.copy()
    env.update(BASE_ENV)
    env.update(variant["env"])
    started = time.monotonic()
    with log_path.open("w") as log:
        proc = subprocess.Popen(BASE_ARGS + variant["args"], env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            wait_ready(proc)
            ready_seconds = time.monotonic() - started
            completion(32, 40)
            trials = []
            for seed in (41, 42):
                result = completion(128, seed)
                trials.append(result["timings"])
            speeds = [trial["predicted_per_second"] for trial in trials]
            prompt_speeds = [trial["prompt_per_second"] for trial in trials]
            return {
                "name": variant["name"],
                "status": "ok",
                "environment": variant["env"],
                "arguments": variant["args"],
                "ready_seconds": ready_seconds,
                "generation_tok_s": sum(speeds) / len(speeds),
                "generation_trials_tok_s": speeds,
                "prompt_tok_s": sum(prompt_speeds) / len(prompt_speeds),
                "prompt_trials_tok_s": prompt_speeds,
            }
        except Exception as exc:
            return {
                "name": variant["name"],
                "status": "failed",
                "environment": variant["env"],
                "arguments": variant["args"],
                "error": repr(exc),
            }
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for variant in VARIANTS:
        print(f"Testing {variant['name']}...", flush=True)
        result = run_variant(variant)
        results.append(result)
        if result["status"] == "ok":
            print(
                f"  generation {result['generation_tok_s']:.3f} tok/s; "
                f"prompt {result['prompt_tok_s']:.3f} tok/s",
                flush=True,
            )
        else:
            print(f"  FAILED: {result['error']}", flush=True)
        (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")

    ranked = sorted(
        (result for result in results if result["status"] == "ok"),
        key=lambda result: result["generation_tok_s"],
        reverse=True,
    )
    lines = [
        "# Qwen3.8 27B Q4_K_M P100 Vulkan tuning",
        "",
        "Direct llama-server test, 4096 context, flash attention enabled, 32-token warm-up,",
        "then two deterministic 128-token generation trials per configuration.",
        "The x16 P100 is Vulkan0 and the x4 P100 is Vulkan1.",
        "",
        "| Rank | Configuration | Generation tok/s | Prompt tok/s | Load to ready (s) |",
        "|---:|---|---:|---:|---:|",
    ]
    for rank, result in enumerate(ranked, 1):
        lines.append(
            f"| {rank} | `{result['name']}` | {result['generation_tok_s']:.3f} | "
            f"{result['prompt_tok_s']:.3f} | {result['ready_seconds']:.1f} |"
        )
    failures = [result for result in results if result["status"] != "ok"]
    if failures:
        lines += ["", "## Failures", ""]
        lines += [f"- `{result['name']}`: {result['error']}" for result in failures]
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
