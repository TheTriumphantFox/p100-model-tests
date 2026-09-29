#!/usr/bin/env python3
"""Benchmark every locally installed Ollama model and generate CSV/Markdown/SVG results."""

import csv
import datetime as dt
import html
import json
import statistics
import time
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:11434"
OUT_DIR = Path(__file__).resolve().parent
RESULTS_JSON = OUT_DIR / "results.json"
NUM_CTX = 4096
NUM_PREDICT = 160
TRIALS = 2
PROMPT = (
    "Continue this numbered list with distinct English words, one item per line. "
    "Do not explain and do not stop until at least 500 items have been written.\n"
    "1. apple\n2. river\n3."
)


def request_json(path, payload=None, timeout=900):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def short_label(name):
    labels = {
        "qwen3.6-27b-uncensored-q5-pi:latest": "Qwen3.6 27B Q5 Pi",
        "qwen3.6-35b-a3b-q8-pi:latest": "Qwen3.6 35B-A3B Q8 Pi",
        "qwen3.6-35b-a3b-q6-pi:latest": "Qwen3.6 35B-A3B Q6 Pi",
        "qwen3.6-35b-a3b-q5-pi:latest": "Qwen3.6 35B-A3B Q5 Pi",
        "qwen3.6-35b-a3b:latest": "Qwen3.6 35B-A3B Q4 local",
        "fredrezones55/Qwopus3.6:latest": "Qwopus3.6 27B Q4",
        "fredrezones55/Qwopus3.5:latest": "Qwopus3.5 9B Q4",
        "fredrezones55/Gemma-4-Uncensored-HauhauCS-Aggressive:latest": "Gemma-4 8B Q4",
        "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:Q4": "Hauhau Qwen3.6 A3B Q4 tag",
        "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:latest": "Hauhau Qwen3.6 A3B Q4 latest",
        "qwen3.8:27b-q4_K_M": "Qwen3.8 27B Q4",
        "qwen-pi:latest": "Qwen Pi 35B-A3B Q4",
    }
    return labels.get(name, name)


def save_json(results, started):
    RESULTS_JSON.write_text(
        json.dumps(
            {
                "started": started,
                "finished": dt.datetime.now().astimezone().isoformat(),
                "settings": {
                    "num_ctx": NUM_CTX,
                    "num_predict": NUM_PREDICT,
                    "trials": TRIALS,
                    "temperature": 0,
                    "warmup_tokens": 16,
                },
                "results": results,
            },
            indent=2,
        )
        + "\n"
    )


def generate_outputs(results, started):
    successful = [r for r in results if "error" not in r]
    ranked = sorted(successful, key=lambda r: r["generation_tps_mean"], reverse=True)

    with (OUT_DIR / "results.csv").open("w", newline="") as f:
        fields = [
            "rank", "model", "label", "parameter_size", "quantization", "size_gb",
            "generation_tps_mean", "generation_tps_min", "generation_tps_max",
            "prompt_tps_mean", "load_seconds", "tokens_per_trial", "trials",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for rank, r in enumerate(ranked, 1):
            writer.writerow({
                "rank": rank,
                "model": r["model"],
                "label": r["label"],
                "parameter_size": r["parameter_size"],
                "quantization": r["quantization"],
                "size_gb": f'{r["size_gb"]:.2f}',
                "generation_tps_mean": f'{r["generation_tps_mean"]:.2f}',
                "generation_tps_min": f'{r["generation_tps_min"]:.2f}',
                "generation_tps_max": f'{r["generation_tps_max"]:.2f}',
                "prompt_tps_mean": f'{r["prompt_tps_mean"]:.2f}',
                "load_seconds": f'{r["load_seconds"]:.2f}',
                "tokens_per_trial": r["eval_counts"],
                "trials": TRIALS,
            })

    lines = [
        "# Local Ollama model token-speed benchmark",
        "",
        f"Run started: `{started}`",
        "",
        f"- Hardware: AMD Ryzen 5 7600X, 64 GB RAM, NVIDIA GTX 1660 SUPER 6 GB",
        f"- Context: {NUM_CTX} tokens",
        f"- Measured generation: up to {NUM_PREDICT} tokens per trial",
        f"- Trials: {TRIALS}, after a 16-token warm-up",
        "- Temperature: 0",
        "- Models were tested sequentially through the local Ollama API and unloaded between tests.",
        "- Generation tok/s comes directly from Ollama's `eval_count / eval_duration`.",
        "",
        "![Generation speed graph](generation-tokens-per-second.png)",
        "",
        "| Rank | Model | Quant | Size | Generation tok/s | Range | Prompt tok/s | Load |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for rank, r in enumerate(ranked, 1):
        lines.append(
            f'| {rank} | {r["label"]} | {r["quantization"]} | {r["size_gb"]:.1f} GB '
            f'| **{r["generation_tps_mean"]:.2f}** | {r["generation_tps_min"]:.2f}-{r["generation_tps_max"]:.2f} '
            f'| {r["prompt_tps_mean"]:.1f} | {r["load_seconds"]:.1f}s |'
        )
    failures = [r for r in results if "error" in r]
    if failures:
        lines += ["", "## Failures", ""]
        lines += [f'- `{r["model"]}`: {r["error"]}' for r in failures]
    lines += [
        "",
        "## Notes",
        "",
        "Prompt throughput is based on a short prompt and is less stable than generation throughput.",
        "Two installed Hauhau tags point to the same Ollama model digest; both were still tested as listed.",
    ]
    (OUT_DIR / "REPORT.md").write_text("\n".join(lines) + "\n")

    # Dependency-free horizontal bar chart as SVG.
    width = 1400
    left = 430
    right = 120
    top = 110
    row_h = 52
    bottom = 90
    height = top + row_h * len(ranked) + bottom
    plot_w = width - left - right
    max_value = max((r["generation_tps_mean"] for r in ranked), default=1)
    axis_max = max(5, int((max_value * 1.15 + 4.999) // 5) * 5)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#111718"/>',
        '<style>text{font-family:DejaVu Sans,Arial,sans-serif}.label{fill:#e7eeee;font-size:19px}.small{fill:#9eafb0;font-size:15px}.value{fill:#f7f7f7;font-size:18px;font-weight:bold}.title{fill:#f7f7f7;font-size:30px;font-weight:bold}.subtitle{fill:#9eafb0;font-size:16px}</style>',
        '<text x="40" y="47" class="title">Local model generation speed</text>',
        f'<text x="40" y="76" class="subtitle">Average of {TRIALS} trials, {NUM_PREDICT} output-token cap, {NUM_CTX}-token context | Higher is better</text>',
    ]
    for tick in range(0, axis_max + 1, 5):
        x = left + plot_w * tick / axis_max
        svg.append(f'<line x1="{x:.1f}" y1="{top-20}" x2="{x:.1f}" y2="{height-bottom+8}" stroke="#293536" stroke-width="1"/>')
        svg.append(f'<text x="{x:.1f}" y="{height-bottom+35}" text-anchor="middle" class="small">{tick}</text>')
    svg.append(f'<text x="{left + plot_w/2:.1f}" y="{height-18}" text-anchor="middle" class="small">generated tokens per second</text>')
    colors = ["#48a9b8", "#459dac", "#428f9e", "#3e838f"]
    for i, r in enumerate(ranked):
        y = top + i * row_h
        bar_y = y + 8
        bar_h = 28
        bar_w = plot_w * r["generation_tps_mean"] / axis_max
        svg.append(f'<text x="{left-18}" y="{bar_y+20}" text-anchor="end" class="label">{html.escape(r["label"])}</text>')
        svg.append(f'<rect x="{left}" y="{bar_y}" width="{plot_w}" height="{bar_h}" rx="4" fill="#1c2728"/>')
        svg.append(f'<rect x="{left}" y="{bar_y}" width="{bar_w:.1f}" height="{bar_h}" rx="4" fill="{colors[min(i//3, len(colors)-1)]}"/>')
        svg.append(f'<text x="{left+bar_w+12:.1f}" y="{bar_y+21}" class="value">{r["generation_tps_mean"]:.2f}</text>')
    svg.append('</svg>')
    (OUT_DIR / "generation-tokens-per-second.svg").write_text("\n".join(svg) + "\n")


def main():
    started = dt.datetime.now().astimezone().isoformat()
    tags = request_json("/api/tags")["models"]
    results = []
    print(f"Benchmarking {len(tags)} installed model entries", flush=True)

    for index, tag in enumerate(tags, 1):
        model = tag["name"]
        details = tag.get("details", {})
        print(f"[{index}/{len(tags)}] {model}: loading/warming up", flush=True)
        base_payload = {
            "model": model,
            "prompt": PROMPT,
            "raw": True,
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "num_ctx": NUM_CTX,
                "temperature": 0,
                "seed": 42,
            },
        }
        try:
            warm = json.loads(json.dumps(base_payload))
            warm["options"]["num_predict"] = 16
            warm_result = request_json("/api/generate", warm)
            load_seconds = warm_result.get("load_duration", 0) / 1e9

            generation_tps = []
            prompt_tps = []
            eval_counts = []
            trial_details = []
            for trial in range(1, TRIALS + 1):
                measured = json.loads(json.dumps(base_payload))
                measured["options"]["num_predict"] = NUM_PREDICT
                response = request_json("/api/generate", measured)
                eval_count = response.get("eval_count", 0)
                eval_duration = response.get("eval_duration", 0)
                prompt_count = response.get("prompt_eval_count", 0)
                prompt_duration = response.get("prompt_eval_duration", 0)
                gen_rate = eval_count / (eval_duration / 1e9) if eval_duration else 0
                prompt_rate = prompt_count / (prompt_duration / 1e9) if prompt_duration else 0
                generation_tps.append(gen_rate)
                prompt_tps.append(prompt_rate)
                eval_counts.append(eval_count)
                trial_details.append({
                    "trial": trial,
                    "eval_count": eval_count,
                    "eval_duration_ns": eval_duration,
                    "generation_tps": gen_rate,
                    "prompt_eval_count": prompt_count,
                    "prompt_eval_duration_ns": prompt_duration,
                    "prompt_tps": prompt_rate,
                    "total_duration_ns": response.get("total_duration", 0),
                })
                print(f"  trial {trial}: {gen_rate:.2f} tok/s ({eval_count} tokens)", flush=True)

            result = {
                "model": model,
                "label": short_label(model),
                "digest": tag.get("digest", ""),
                "size_bytes": tag.get("size", 0),
                "size_gb": tag.get("size", 0) / 1_000_000_000,
                "parameter_size": details.get("parameter_size", ""),
                "quantization": details.get("quantization_level", ""),
                "load_seconds": load_seconds,
                "generation_tps_mean": statistics.mean(generation_tps),
                "generation_tps_min": min(generation_tps),
                "generation_tps_max": max(generation_tps),
                "prompt_tps_mean": statistics.mean(prompt_tps),
                "eval_counts": eval_counts,
                "trial_details": trial_details,
            }
            results.append(result)
        except Exception as exc:
            print(f"  ERROR: {exc}", flush=True)
            results.append({
                "model": model,
                "label": short_label(model),
                "error": str(exc),
            })
        finally:
            try:
                request_json("/api/generate", {"model": model, "keep_alive": 0}, timeout=120)
            except Exception:
                pass
            save_json(results, started)
            time.sleep(2)

    generate_outputs(results, started)
    save_json(results, started)
    print(f"Finished. Results: {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
