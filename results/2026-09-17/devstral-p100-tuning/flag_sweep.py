#!/usr/bin/env python3
"""Benchmark Vulkan kernel flags for Devstral on an isolated Ollama server."""

import json
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HOST = "http://127.0.0.1:11435"
MODEL = "hf.co/lmstudio-community/Devstral-Small-2-24B-Instruct-2512-GGUF:q8_0"
CONFIGS = [
    ("baseline", {}),
    ("disable-int-dot", {"GGML_VK_DISABLE_INTEGER_DOT_PRODUCT": "1"}),
    ("disable-mmvq", {"GGML_VK_DISABLE_MMVQ": "1"}),
    (
        "disable-both",
        {
            "GGML_VK_DISABLE_INTEGER_DOT_PRODUCT": "1",
            "GGML_VK_DISABLE_MMVQ": "1",
        },
    ),
]
TRIALS = 2
NUM_CTX = 2048
NUM_PREDICT = 128
CONTEXT = "\n".join(
    f"Function {i:03d}: validate input, transform state, record result, return status."
    for i in range(64)
)


def request(path, body=None, timeout=1800):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        HOST + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def wait_ready(process, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"ollama serve exited with {process.returncode}")
        try:
            request("/api/tags", timeout=2)
            return
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    raise TimeoutError("isolated Ollama server did not become ready")


def chat(nonce, num_predict):
    prompt = (
        f"Unique benchmark nonce {nonce}. Read the code inventory, then give a "
        "numbered list of concrete testing recommendations. Continue until the "
        "output limit and do not mention the nonce.\n\n" + CONTEXT
    )
    return request(
        "/api/chat",
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "num_ctx": NUM_CTX,
                "num_predict": num_predict,
                "temperature": 0,
                "seed": 42,
            },
        },
    )


def rate(count, duration):
    return count / (duration / 1e9) if duration else 0


def stop(process):
    if process.poll() is None:
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def main():
    output_dir = Path(__file__).parent
    results = {
        "started": datetime.now().astimezone().isoformat(),
        "model": MODEL,
        "settings": {
            "trials": TRIALS,
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
            "temperature": 0,
            "seed": 42,
        },
        "configurations": [],
    }

    for name, flags in CONFIGS:
        print(f"\n=== {name} ===", flush=True)
        env = os.environ.copy()
        for variable in ("GGML_VK_DISABLE_INTEGER_DOT_PRODUCT", "GGML_VK_DISABLE_MMVQ"):
            env.pop(variable, None)
        env.update(
            {
                "OLLAMA_HOST": "127.0.0.1:11435",
                "OLLAMA_MODELS": "/var/lib/ollama",
                "OLLAMA_LLM_LIBRARY": "vulkan",
                "OLLAMA_KEEP_ALIVE": "10m",
            }
        )
        env.update(flags)
        log_path = output_dir / f"{name}.log"
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                ["ollama", "serve"], stdout=log, stderr=subprocess.STDOUT, env=env
            )
            try:
                wait_ready(process)
                started = time.monotonic()
                warmup = chat(f"{name}-warmup", 16)
                warmup_wall = time.monotonic() - started
                ps = subprocess.run(
                    ["ollama", "ps"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=True,
                    env={**os.environ, "OLLAMA_HOST": "127.0.0.1:11435"},
                ).stdout.strip()
                trials = []
                for trial_number in range(1, TRIALS + 1):
                    response = chat(f"{name}-trial-{trial_number}", NUM_PREDICT)
                    trial = {
                        "prompt_tokens": response.get("prompt_eval_count", 0),
                        "prompt_tps": rate(
                            response.get("prompt_eval_count", 0),
                            response.get("prompt_eval_duration", 0),
                        ),
                        "generated_tokens": response.get("eval_count", 0),
                        "generation_tps": rate(
                            response.get("eval_count", 0), response.get("eval_duration", 0)
                        ),
                        "done_reason": response.get("done_reason"),
                    }
                    trials.append(trial)
                    print(
                        f"trial {trial_number}: prompt {trial['prompt_tps']:.2f}, "
                        f"generation {trial['generation_tps']:.2f} tok/s",
                        flush=True,
                    )
                results["configurations"].append(
                    {
                        "name": name,
                        "environment": flags,
                        "warmup_wall_seconds": warmup_wall,
                        "warmup_load_seconds": warmup.get("load_duration", 0) / 1e9,
                        "processor": ps,
                        "mean_prompt_tps": sum(t["prompt_tps"] for t in trials) / len(trials),
                        "mean_generation_tps": sum(t["generation_tps"] for t in trials) / len(trials),
                        "trials": trials,
                    }
                )
            finally:
                stop(process)
                time.sleep(3)

    results["finished"] = datetime.now().astimezone().isoformat()
    path = output_dir / "flag-results.json"
    path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
