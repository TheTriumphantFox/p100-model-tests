#!/usr/bin/env python3
"""Compare two Ollama models through the native chat endpoint."""

import json
import statistics
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HOST = "http://127.0.0.1:11434"
MODELS = [
    "qwen3.8-flash-next:ud-iq3_xxs",
    "hf.co/lmstudio-community/Devstral-Small-2-24B-Instruct-2512-GGUF:q8_0",
]
TRIALS = 2
NUM_CTX = 2048
NUM_PREDICT = 160

context = "\n".join(
    f"Record {i:03d}: alpha beta gamma delta epsilon zeta eta theta."
    for i in range(80)
)
PROMPT = (
    "Read the synthetic records below, then write a numbered list of practical "
    "software-testing recommendations. Keep generating until the output limit; "
    "do not include hidden reasoning.\n\n" + context
)


def post(path, body, timeout=3600):
    request = urllib.request.Request(
        HOST + path,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def chat(model, num_predict):
    return post(
        "/api/chat",
        {
            "model": model,
            "messages": [{"role": "user", "content": PROMPT}],
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "options": {
                "num_ctx": NUM_CTX,
                "num_predict": num_predict,
                "temperature": 0,
                "seed": 42,
            },
        },
    )


def rate(count, duration_ns):
    return count / (duration_ns / 1_000_000_000) if duration_ns else 0.0


def unload(model):
    try:
        post("/api/generate", {"model": model, "keep_alive": 0}, timeout=120)
    except Exception as exc:
        print(f"Warning: could not unload {model}: {exc}")


def ps_line(model):
    output = subprocess.run(
        ["ollama", "ps"], capture_output=True, text=True, timeout=30, check=True
    ).stdout
    return next((line for line in output.splitlines() if model in line), output.strip())


def main():
    results = {
        "started": datetime.now().astimezone().isoformat(),
        "settings": {
            "trials": TRIALS,
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
            "temperature": 0,
            "seed": 42,
            "thinking": False,
            "endpoint": "/api/chat",
        },
        "models": [],
    }

    for model in MODELS:
        print(f"\nLoading {model}...", flush=True)
        started = time.monotonic()
        warmup = chat(model, 16)
        load_wall = time.monotonic() - started
        processor = ps_line(model)
        print(processor, flush=True)

        trials = []
        for number in range(1, TRIALS + 1):
            print(f"Trial {number}/{TRIALS}...", flush=True)
            response = chat(model, NUM_PREDICT)
            trial = {
                "prompt_tokens": response.get("prompt_eval_count", 0),
                "prompt_seconds": response.get("prompt_eval_duration", 0) / 1e9,
                "prompt_tps": rate(
                    response.get("prompt_eval_count", 0),
                    response.get("prompt_eval_duration", 0),
                ),
                "generated_tokens": response.get("eval_count", 0),
                "generation_seconds": response.get("eval_duration", 0) / 1e9,
                "generation_tps": rate(
                    response.get("eval_count", 0), response.get("eval_duration", 0)
                ),
                "done_reason": response.get("done_reason"),
                "response_preview": response.get("message", {}).get("content", "")[:300],
            }
            trials.append(trial)
            print(
                f"  prompt {trial['prompt_tps']:.2f} tok/s; "
                f"generation {trial['generation_tps']:.2f} tok/s "
                f"({trial['generated_tokens']} tokens)",
                flush=True,
            )

        model_result = {
            "model": model,
            "warmup_wall_seconds": load_wall,
            "warmup_load_seconds": warmup.get("load_duration", 0) / 1e9,
            "processor": processor,
            "mean_prompt_tps": statistics.mean(t["prompt_tps"] for t in trials),
            "mean_generation_tps": statistics.mean(t["generation_tps"] for t in trials),
            "trials": trials,
        }
        results["models"].append(model_result)
        unload(model)
        time.sleep(3)

    results["finished"] = datetime.now().astimezone().isoformat()
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nSaved {output}")


if __name__ == "__main__":
    main()
