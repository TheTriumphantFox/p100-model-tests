#!/usr/bin/env python3
"""Benchmark candidate Vulkan flags through Ollama's real runner setup."""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent / "ollama-runner"
MODEL = "qwen3.8-27b-stock:q4_k_m"
HOST = "127.0.0.1"
PORT = 11435
PARAGRAPH = (
    "Voltage, current, resistance, inductance, capacitance, impedance, power factor, "
    "transformers, motors, grounding, protection, conductors, and control systems are "
    "important electrical engineering concepts. Explain their relationships clearly. "
)
LONG_PROMPT = PARAGRAPH * 24 + "\nProvide the next numbered engineering observation:\n1."
VARIANTS = [
    ("baseline", {}),
    ("disable-mmvq", {"GGML_VK_DISABLE_MMVQ": "1"}),
    ("disable-int-dot", {"GGML_VK_DISABLE_INTEGER_DOT_PRODUCT": "1"}),
    ("disable-both", {"GGML_VK_DISABLE_MMVQ": "1", "GGML_VK_DISABLE_INTEGER_DOT_PRODUCT": "1"}),
]


def api(path: str, payload: dict | None = None, timeout: float = 180) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        f"http://{HOST}:{PORT}{path}", data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def generate(prompt: str, predict: int) -> dict:
    return api(
        "/api/generate",
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "options": {
                "num_ctx": 4096,
                "num_predict": predict,
                "temperature": 0,
                "seed": 42,
            },
        },
    )


def run(name: str, extra_env: dict[str, str]) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "OLLAMA_HOST": f"{HOST}:{PORT}",
            "OLLAMA_MODELS": "/var/lib/ollama",
            "OLLAMA_KEEP_ALIVE": "10m",
            "OLLAMA_LLM_LIBRARY": "vulkan",
            "OLLAMA_VULKAN": "1",
        }
    )
    env.update(extra_env)
    log_path = OUT / f"{name}.log"
    with log_path.open("w") as log:
        proc = subprocess.Popen(["/usr/bin/ollama", "serve"], env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError(f"ollama exited with status {proc.returncode}")
                try:
                    api("/api/tags", timeout=1)
                    break
                except (OSError, urllib.error.URLError, TimeoutError):
                    time.sleep(0.25)
            else:
                raise TimeoutError("ollama did not become ready")

            warmup = generate("Reply with one word: ready", 16)
            measured = generate(LONG_PROMPT, 128)
            prompt_tps = measured["prompt_eval_count"] / (measured["prompt_eval_duration"] / 1e9)
            generation_tps = measured["eval_count"] / (measured["eval_duration"] / 1e9)
            return {
                "name": name,
                "status": "ok",
                "environment": extra_env,
                "prompt_tokens": measured["prompt_eval_count"],
                "prompt_tok_s": prompt_tps,
                "generated_tokens": measured["eval_count"],
                "generation_tok_s": generation_tps,
                "load_seconds": warmup["load_duration"] / 1e9,
            }
        except Exception as exc:
            return {"name": name, "status": "failed", "environment": extra_env, "error": repr(exc)}
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def main() -> None:
    results = []
    for name, env in VARIANTS:
        print(f"Testing {name}...", flush=True)
        result = run(name, env)
        results.append(result)
        print(json.dumps(result, indent=2), flush=True)
        (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")

    good = sorted(
        (result for result in results if result["status"] == "ok"),
        key=lambda result: result["generation_tok_s"],
        reverse=True,
    )
    lines = [
        "# Ollama runner validation",
        "",
        "Qwen3.8 27B Q4_K_M, dual P100 Vulkan, 4096 context, one short warm-up,",
        "then one uncached long-prompt request per server instance.",
        "",
        "| Configuration | Prompt tokens | Prompt tok/s | Generation tok/s |",
        "|---|---:|---:|---:|",
    ]
    for result in good:
        lines.append(
            f"| `{result['name']}` | {result['prompt_tokens']} | "
            f"{result['prompt_tok_s']:.2f} | {result['generation_tok_s']:.2f} |"
        )
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
