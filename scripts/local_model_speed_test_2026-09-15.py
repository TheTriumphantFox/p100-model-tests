#!/usr/bin/env python3
"""Small sequential Ollama generation-speed benchmark for all installed tags."""
import csv
import datetime as dt
import json
import statistics
import subprocess
import time
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:11434"
OUT_DIR = Path.home() / "Projects" / "Tests" / "2026-09-15" / "local-model-benchmark"
OUT_DIR.mkdir(parents=True, exist_ok=True)
NUM_CTX = 4096
NUM_PREDICT = 160
TRIALS = 2
PROMPT = (
    "Continue this numbered list with distinct common English words, one item per line. "
    "Do not explain and do not stop early.\n1. apple\n2. river\n3."
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


def gpu_snapshot():
    try:
        raw = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,memory.used,memory.total,utilization.gpu,power.draw,power.limit", "--format=csv,noheader,nounits"],
            text=True,
            timeout=10,
        ).strip()
        return raw.splitlines()
    except Exception as exc:
        return [f"unavailable: {exc}"]


def save_results(started, results, finished=False):
    payload = {
        "started": started,
        "finished": dt.datetime.now().astimezone().isoformat() if finished else None,
        "settings": {
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
            "trials": TRIALS,
            "temperature": 0,
            "seed": 42,
            "think": False,
            "warmup_tokens": 16,
        },
        "gpu_at_start": gpu_snapshot(),
        "results": results,
    }
    (OUT_DIR / "results.json").write_text(json.dumps(payload, indent=2) + "\n")


def write_reports(started, results):
    successful = sorted(
        (r for r in results if "error" not in r),
        key=lambda r: r["generation_tps_mean"],
        reverse=True,
    )
    with (OUT_DIR / "results.csv").open("w", newline="") as f:
        fields = ["rank", "model", "parameter_size", "quantization", "size_gb", "generation_tps_mean", "generation_tps_min", "generation_tps_max", "prompt_tps_mean", "load_seconds", "tokens_per_trial"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for rank, r in enumerate(successful, 1):
            writer.writerow({
                "rank": rank,
                "model": r["model"],
                "parameter_size": r.get("parameter_size", ""),
                "quantization": r.get("quantization", ""),
                "size_gb": f'{r.get("size_gb", 0):.2f}',
                "generation_tps_mean": f'{r["generation_tps_mean"]:.2f}',
                "generation_tps_min": f'{r["generation_tps_min"]:.2f}',
                "generation_tps_max": f'{r["generation_tps_max"]:.2f}',
                "prompt_tps_mean": f'{r["prompt_tps_mean"]:.2f}',
                "load_seconds": f'{r["load_seconds"]:.2f}',
                "tokens_per_trial": r["eval_counts"],
            })

    lines = [
        "# Local Ollama model speed test",
        "",
        f"Run started: `{started}`",
        "",
        f"- Context: {NUM_CTX} tokens",
        f"- Output cap: {NUM_PREDICT} tokens per trial",
        f"- Trials: {TRIALS} per model after a 16-token warm-up",
        "- Temperature: 0, seed: 42, thinking disabled",
        "- Models tested sequentially through Ollama and unloaded between models",
        "- Generation speed is Ollama `eval_count / eval_duration`",
        "",
        "| Rank | Model | Quant | Size | Generation tok/s | Range | Load |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for rank, r in enumerate(successful, 1):
        lines.append(
            f'| {rank} | `{r["model"]}` | {r.get("quantization", "")} | {r.get("size_gb", 0):.1f} GB '
            f'| **{r["generation_tps_mean"]:.2f}** | {r["generation_tps_min"]:.2f}-{r["generation_tps_max"]:.2f} '
            f'| {r["load_seconds"]:.1f}s |'
        )
    failures = [r for r in results if "error" in r]
    if failures:
        lines += ["", "## Failures", ""]
        lines += [f'- `{r["model"]}`: {r["error"]}' for r in failures]
    (OUT_DIR / "REPORT.md").write_text("\n".join(lines) + "\n")


def main():
    started = dt.datetime.now().astimezone().isoformat()
    tags = request_json("/api/tags")["models"]
    results = []
    print(f"Benchmarking {len(tags)} installed Ollama model entries", flush=True)
    print("GPU at start:", " | ".join(gpu_snapshot()), flush=True)

    for index, tag in enumerate(tags, 1):
        model = tag["name"]
        details = tag.get("details", {})
        print(f"[{index}/{len(tags)}] {model}: loading", flush=True)
        base_payload = {
            "model": model,
            "prompt": PROMPT,
            "raw": True,
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "options": {
                "num_ctx": NUM_CTX,
                "num_predict": NUM_PREDICT,
                "temperature": 0,
                "seed": 42,
            },
        }
        try:
            warm = dict(base_payload)
            warm["options"] = dict(base_payload["options"])
            warm["options"]["num_predict"] = 16
            warm_result = request_json("/api/generate", warm)
            load_seconds = warm_result.get("load_duration", 0) / 1e9
            print(f"  loaded in {load_seconds:.2f}s; GPU: {' | '.join(gpu_snapshot())}", flush=True)

            generation_tps = []
            prompt_tps = []
            eval_counts = []
            trial_details = []
            for trial in range(1, TRIALS + 1):
                measured = dict(base_payload)
                measured["options"] = dict(base_payload["options"])
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

            results.append({
                "model": model,
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
            })
        except Exception as exc:
            print(f"  ERROR: {exc}", flush=True)
            results.append({"model": model, "error": str(exc)})
        finally:
            try:
                request_json("/api/generate", {"model": model, "keep_alive": 0}, timeout=120)
            except Exception:
                pass
            save_results(started, results)
            time.sleep(2)

    save_results(started, results, finished=True)
    write_reports(started, results)
    print("\nRanked results:", flush=True)
    for rank, r in enumerate(sorted((x for x in results if "error" not in x), key=lambda x: x["generation_tps_mean"], reverse=True), 1):
        print(f"{rank:2}. {r['model']}: {r['generation_tps_mean']:.2f} tok/s (load {r['load_seconds']:.1f}s)", flush=True)
    print(f"\nSaved {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
