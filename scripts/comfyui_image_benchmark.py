#!/usr/bin/env python3
"""Generate image-benchmark samples through a local ComfyUI API.

The runner is resumable and writes every generated sample plus JSONL metadata
under ~/Projects/Tests/YYYY-MM-DD/image-generation. It supports the official
GenEval prompts and the validation prompts from T2I-CompBench. Scoring is
deliberately separate: the official GenEval evaluator can consume the
generated directory layout.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TESTING = Path.home() / "Projects" / "Tests"
GENEVAL_METADATA = TESTING / "tools" / "geneval" / "prompts" / "evaluation_metadata.jsonl"
T2I_DATASET = TESTING / "tools" / "t2i_compbench" / "examples" / "dataset"
DEFAULT_CHECKPOINT = "RealVisXL_V5.0_fp16.safetensors"


def current_image_test_root() -> Path:
    return TESTING / datetime.now().astimezone().strftime("%Y-%m-%d") / "image-generation"


DEFAULT_COMFY_OUTPUT = current_image_test_root() / "runtime" / "comfyui_image_output"

T2I_CATEGORIES = [
    "3d_spatial",
    "color",
    "complex",
    "non_spatial",
    "numeracy",
    "shape",
    "spatial",
    "texture",
]


def api_json(base_url: str, endpoint: str, payload: dict[str, Any] | None = None, timeout: float = 30) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if data is None else "POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise RuntimeError(f"ComfyUI request failed: {exc}") from exc
    try:
        result = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from ComfyUI: {body[:500]}") from exc
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected non-object response from ComfyUI")
    return result


def load_prompts(dataset: str) -> list[dict[str, Any]]:
    if dataset == "geneval":
        prompts: list[dict[str, Any]] = []
        with GENEVAL_METADATA.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                item = json.loads(line)
                prompts.append({
                    "dataset": "geneval",
                    "prompt_id": f"{index:04d}",
                    "index": index,
                    "prompt": item["prompt"],
                    "metadata": item,
                })
        return prompts

    if dataset == "t2i":
        prompts = []
        for category in T2I_CATEGORIES:
            path = T2I_DATASET / f"{category}_val.txt"
            with path.open(encoding="utf-8") as handle:
                for index, line in enumerate(handle):
                    text = line.strip()
                    if not text:
                        continue
                    prompts.append({
                        "dataset": "t2i_compbench",
                        "category": category,
                        "prompt_id": f"{category}_{index:04d}",
                        "index": index,
                        "prompt": text,
                    })
        return prompts

    raise ValueError(f"Unknown dataset: {dataset}")


def workflow_for_prompt(
    prompt: str,
    seed: int,
    checkpoint: str,
    width: int,
    height: int,
    steps: int,
    cfg: float,
    filename_prefix: str,
    negative_prompt: str,
) -> dict[str, Any]:
    # Standard ComfyUI API-format SDXL checkpoint workflow. The checkpoint
    # includes its VAE and CLIP, so no external model files are required.
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": checkpoint},
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["1", 1]},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_prompt, "clip": ["1", 1]},
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "denoise": 1.0,
            },
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": filename_prefix,
            },
        },
    }


def wait_for_history(base_url: str, prompt_id: str, timeout: float, poll: float = 0.5) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        history = api_json(base_url, "/history/" + urllib.parse.quote(prompt_id, safe=""), timeout=30)
        item = history.get(prompt_id)
        if item:
            status = item.get("status", {})
            if status.get("status_str") == "error":
                messages = status.get("messages", [])
                raise RuntimeError("ComfyUI execution error: " + json.dumps(messages)[:1000])
            if status.get("completed") or status.get("status_str") == "success":
                return item
        time.sleep(poll)
    raise TimeoutError(f"Timed out after {timeout}s waiting for prompt {prompt_id}")


def first_image_output(history_item: dict[str, Any]) -> dict[str, str]:
    for node_output in history_item.get("outputs", {}).values():
        for image in node_output.get("images", []):
            if image.get("filename"):
                return {
                    "filename": str(image["filename"]),
                    "subfolder": str(image.get("subfolder", "")),
                    "type": str(image.get("type", "output")),
                }
    raise RuntimeError("ComfyUI completed without a SaveImage output")


def get_image(base_url: str, image: dict[str, str], timeout: float = 60) -> bytes:
    query = urllib.parse.urlencode(image)
    req = urllib.request.Request(base_url.rstrip("/") + "/view?" + query)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise RuntimeError(f"Could not retrieve generated image: {exc}") from exc


def cleanup_comfy_output(root: Path, image: dict[str, str]) -> None:
    """Remove the temporary SaveImage copy after retrieving it."""
    try:
        root = root.expanduser().resolve()
        source = (root / image.get("subfolder", "") / image["filename"]).resolve()
        if root in source.parents and source.is_file():
            source.unlink()
    except (KeyError, OSError, RuntimeError):
        # The final benchmark copy is already safe; cleanup is best effort.
        pass


def target_for_prompt(output_root: Path, item: dict[str, Any], sample_index: int) -> tuple[Path, Path]:
    if item["dataset"] == "geneval":
        prompt_dir = output_root / "geneval" / item["prompt_id"]
        return prompt_dir / "samples" / f"{sample_index:04d}.png", prompt_dir / "metadata.jsonl"
    prompt_dir = output_root / "t2i_compbench" / item["category"] / item["prompt_id"]
    return prompt_dir / f"{sample_index:04d}.png", prompt_dir / "metadata.json"


def write_prompt_metadata(item: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    if item["dataset"] == "geneval":
        path.write_text(json.dumps(item["metadata"], ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_completed(manifest_path: Path) -> set[str]:
    completed: set[str] = set()
    if not manifest_path.exists():
        return completed
    with manifest_path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("status") in {"success", "skipped"}:
                completed.add(str(item.get("key")))
    return completed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run GenEval/T2I-CompBench prompts through ComfyUI")
    parser.add_argument("--dataset", choices=["geneval", "t2i", "both"], default="geneval")
    parser.add_argument("--limit", type=int, default=10, help="Prompts per dataset; 0 means all")
    parser.add_argument("--samples-per-prompt", type=int, default=1, help="Images per prompt")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--cfg", type=float, default=6.8)
    parser.add_argument("--negative", default="low quality, blurry, watermark, text, signature, deformed")
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    parser.add_argument("--comfy-output-dir", default=str(DEFAULT_COMFY_OUTPUT))
    parser.add_argument("--output-dir", help="Final image root; default is Tests/YYYY-MM-DD/image-generation/<checkpoint>")
    parser.add_argument("--timeout", type=float, default=900)
    args = parser.parse_args()

    if args.limit < 0 or args.samples_per_prompt < 1:
        parser.error("--limit must be >= 0 and --samples-per-prompt must be >= 1")
    if args.width < 8 or args.height < 8 or args.steps < 1:
        parser.error("width, height, and steps must be positive")

    checkpoint_slug = Path(args.checkpoint).stem.replace(" ", "_")
    output_root = Path(args.output_dir).expanduser() if args.output_dir else current_image_test_root() / checkpoint_slug
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "manifest.jsonl"
    completed = load_completed(manifest_path)

    datasets = ["geneval", "t2i"] if args.dataset == "both" else [args.dataset]
    prompt_items: list[dict[str, Any]] = []
    for dataset in datasets:
        items = load_prompts(dataset)
        if args.limit:
            items = items[: args.limit]
        prompt_items.extend(items)

    total = len(prompt_items) * args.samples_per_prompt
    print(f"ComfyUI: {args.comfy_url}; checkpoint: {args.checkpoint}", flush=True)
    print(f"Prompts: {len(prompt_items)}; samples/prompt: {args.samples_per_prompt}; total images: {total}", flush=True)
    print(f"Output: {output_root}; manifest: {manifest_path}", flush=True)

    client_id = str(uuid.uuid4())
    run_started = datetime.now(timezone.utc).isoformat()
    with manifest_path.open("a", encoding="utf-8") as manifest:
        for item_index, item in enumerate(prompt_items, 1):
            for sample_index in range(args.samples_per_prompt):
                key = f"{item['dataset']}:{item['prompt_id']}:{sample_index}"
                target, metadata_path = target_for_prompt(output_root, item, sample_index)
                write_prompt_metadata(item, metadata_path)
                if key in completed and target.exists() and target.stat().st_size > 0:
                    print(f"[{item_index}/{len(prompt_items)}] sample {sample_index}: skip {key}", flush=True)
                    continue

                started = time.monotonic()
                record: dict[str, Any] = {
                    "key": key,
                    "dataset": item["dataset"],
                    "category": item.get("category", ""),
                    "prompt_id": item["prompt_id"],
                    "sample_index": sample_index,
                    "seed": args.seed + sample_index,
                    "prompt": item["prompt"],
                    "started_at": run_started,
                }
                try:
                    temporary_prefix = f"benchmark_tmp/{item['dataset']}_{item['prompt_id']}_{sample_index}_{uuid.uuid4().hex[:8]}"
                    workflow = workflow_for_prompt(
                        item["prompt"],
                        args.seed + sample_index,
                        args.checkpoint,
                        args.width,
                        args.height,
                        args.steps,
                        args.cfg,
                        temporary_prefix,
                        args.negative,
                    )
                    queued = api_json(args.comfy_url, "/prompt", {"prompt": workflow, "client_id": client_id}, timeout=60)
                    if queued.get("node_errors"):
                        raise RuntimeError("Workflow node errors: " + json.dumps(queued["node_errors"])[:1000])
                    prompt_id = str(queued["prompt_id"])
                    history_item = wait_for_history(args.comfy_url, prompt_id, args.timeout)
                    image_info = first_image_output(history_item)
                    image_bytes = get_image(args.comfy_url, image_info)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(image_bytes)
                    cleanup_comfy_output(Path(args.comfy_output_dir), image_info)
                    record.update({
                        "status": "success",
                        "prompt_id_comfy": prompt_id,
                        "image": str(target),
                        "bytes": len(image_bytes),
                        "elapsed_sec": round(time.monotonic() - started, 3),
                    })
                    print(f"[{item_index}/{len(prompt_items)}] sample {sample_index}: OK {record['elapsed_sec']:.1f}s -> {target}", flush=True)
                except Exception as exc:
                    record.update({
                        "status": "error",
                        "error": str(exc)[:2000],
                        "elapsed_sec": round(time.monotonic() - started, 3),
                    })
                    print(f"[{item_index}/{len(prompt_items)}] sample {sample_index}: ERROR {record['error']}", flush=True)
                manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
                manifest.flush()

    print("Generation run finished; use manifest.jsonl for outputs and timings.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
