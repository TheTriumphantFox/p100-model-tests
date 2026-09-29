#!/usr/bin/env python3
"""Compare Ollama num_batch values with the winning P100 Vulkan flags."""

import benchmark_ollama as bench

bench.OUT = bench.OUT.parent / "ollama-batches-fine"
bench.VARIANTS = [(f"batch-{size}", {"GGML_VK_DISABLE_MMVQ": "1", "GGML_VK_DISABLE_INTEGER_DOT_PRODUCT": "1"}) for size in (128, 192, 256, 320, 384)]
current_batch = 512
original_run = bench.run


def generate(prompt: str, predict: int) -> dict:
    return bench.api(
        "/api/generate",
        {
            "model": bench.MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "options": {
                "num_ctx": 4096,
                "num_batch": current_batch,
                "num_predict": predict,
                "temperature": 0,
                "seed": 42,
            },
        },
    )


def run(name: str, env: dict[str, str]) -> dict:
    global current_batch
    current_batch = int(name.removeprefix("batch-"))
    return original_run(name, env)


bench.generate = generate
bench.run = run
bench.main()
