#!/usr/bin/env python3
"""Score completed ComfyUI image benchmark runs and create charts.

The primary image metric is CLIP prompt-image cosine similarity. This is an
objective prompt-alignment signal, not a complete human-quality score. Speed
charts are also generated from the ComfyUI timing manifest.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import time
from collections import defaultdict
from html import escape
from pathlib import Path
from statistics import mean
from typing import Any

import torch
from PIL import Image


TESTING = Path.home() / "Projects" / "Tests"
CLIP_REPO = "openai/clip-vit-base-patch32"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                value = json.loads(line)
                if isinstance(value, dict):
                    rows.append(value)
            except json.JSONDecodeError:
                pass
    return rows


def load_geneval_tags() -> dict[str, str]:
    path = TESTING / "tools" / "geneval" / "prompts" / "evaluation_metadata.jsonl"
    tags: dict[str, str] = {}
    if path.exists():
        for index, line in enumerate(path.open(encoding="utf-8")):
            try:
                tags[f"{index:04d}"] = str(json.loads(line).get("tag", "unknown"))
            except json.JSONDecodeError:
                tags[f"{index:04d}"] = "unknown"
    return tags


def enrich_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    geneval_tags = load_geneval_tags()
    enriched: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        if item.get("dataset") == "geneval":
            item["test"] = geneval_tags.get(str(item.get("prompt_id")), "unknown")
        else:
            item["test"] = str(item.get("category") or "unknown")
        enriched.append(item)
    return enriched


def score_with_clip(rows: list[dict[str, Any]], score_path: Path, cache_dir: Path, device_name: str, batch_size: int) -> None:
    """Score each successful image, resuming from an existing score JSONL."""
    existing = {str(row.get("key")) for row in read_jsonl(score_path) if row.get("key")}
    pending = [row for row in rows if row.get("status") == "success" and str(row.get("key")) not in existing]
    if not pending:
        print(f"CLIP scores already complete: {score_path}", flush=True)
        return

    from transformers import CLIPModel, CLIPProcessor

    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"Loading {CLIP_REPO} into {cache_dir} on {device_name}...", flush=True)
    processor = CLIPProcessor.from_pretrained(CLIP_REPO, cache_dir=str(cache_dir))
    model = CLIPModel.from_pretrained(CLIP_REPO, cache_dir=str(cache_dir))
    device = torch.device(device_name)
    model.to(device)
    model.eval()
    score_path.parent.mkdir(parents=True, exist_ok=True)

    with score_path.open("a", encoding="utf-8") as output:
        for start in range(0, len(pending), batch_size):
            batch = pending[start:start + batch_size]
            images: list[Image.Image] = []
            valid: list[dict[str, Any]] = []
            for row in batch:
                try:
                    image = Image.open(str(row["image"])).convert("RGB")
                    images.append(image)
                    valid.append(row)
                except Exception as exc:
                    output.write(json.dumps({
                        "key": row.get("key"), "dataset": row.get("dataset"), "test": row.get("test"),
                        "model": row.get("model"), "status": "error", "error": str(exc)[:500],
                    }) + "\n")

            if images:
                prompts = [str(row.get("prompt", "")) for row in valid]
                inputs = processor(
                    text=prompts,
                    images=images,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                )
                inputs = {key: value.to(device) if hasattr(value, "to") else value for key, value in inputs.items()}
                with torch.inference_mode():
                    result = model(**inputs)
                    image_embeds = result.image_embeds
                    text_embeds = result.text_embeds
                    image_embeds = image_embeds / image_embeds.norm(dim=-1, keepdim=True)
                    text_embeds = text_embeds / text_embeds.norm(dim=-1, keepdim=True)
                    scores = (image_embeds * text_embeds).sum(dim=-1).detach().cpu().tolist()
                for row, score in zip(valid, scores):
                    output.write(json.dumps({
                        "key": row.get("key"),
                        "model": row.get("model"),
                        "dataset": row.get("dataset"),
                        "test": row.get("test"),
                        "prompt_id": row.get("prompt_id"),
                        "image": row.get("image"),
                        "clip_score": round(float(score), 6),
                        "status": "success",
                    }, ensure_ascii=False) + "\n")
            output.flush()
            done = start + len(batch)
            print(f"CLIP scoring: {done}/{len(pending)}", flush=True)
            for image in images:
                image.close()


def nice_upper(value: float) -> float:
    if value <= 0:
        return 1.0
    rough = value * 1.15
    magnitude = 10 ** math.floor(math.log10(rough))
    for factor in (1, 2, 5, 10):
        upper = factor * magnitude
        if upper >= rough:
            return upper
    return 10 * magnitude


def label(model: str) -> str:
    return model.replace("_", " ").replace("-", " ")


def text(value: str, x: float, y: float, size: int = 16, fill: str = "#1f2937", anchor: str = "start", weight: str = "normal") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}px" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{escape(str(value))}</text>'


def chart(path: Path, title: str, subtitle: str, entries: list[tuple[str, float, int]], axis: str, color: str, note: str) -> None:
    entries = sorted(entries, key=lambda item: item[1], reverse=True)
    width, left, right, top, bottom = 1800, 530, 170, 125, 105
    row_height = 58
    height = top + bottom + row_height * max(1, len(entries))
    plot_width = width - left - right
    upper = nice_upper(max((value for _, value, _ in entries), default=1.0))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(title, 42, 47, 29, "#111827", weight="bold"),
        text(subtitle, 42, 78, 16, "#4b5563"),
    ]
    for i in range(6):
        value = upper * i / 5
        x = left + plot_width * i / 5
        parts.append(f'<line x1="{x:.1f}" y1="{top - 12}" x2="{x:.1f}" y2="{height - bottom}" stroke="#dbe3ec"/>')
        parts.append(text(f"{value:.3f}" if upper < 2 else f"{value:.0f}", x, height - bottom + 28, 14, "#4b5563", anchor="middle"))
    parts.append(text(axis, left + plot_width / 2, height - 29, 15, "#374151", anchor="middle"))
    for index, (model, value, count) in enumerate(entries):
        y = top + index * row_height + 13
        bar_width = max(0, plot_width * value / upper)
        parts.append(text(f"{index + 1}. {label(model)}", left - 20, y + 23, 16, "#1f2937", anchor="end"))
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="32" rx="4" fill="{color}"><title>{escape(model)}: {value:.6f}</title></rect>')
        parts.append(text(f"{value:.4f}  (n={count})", left + bar_width + 10, y + 23, 15))
    parts.append(text(note, 42, height - 58, 13, "#6b7280"))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def png_for(svg: Path) -> Path | None:
    png = svg.with_suffix(".png")
    try:
        subprocess.run(["rsvg-convert", "-o", str(png), str(svg)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return png


def make_graphs(rows: list[dict[str, Any]], scores: list[dict[str, Any]], output_dir: Path, source_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    models = sorted({str(row.get("model") or "RealVisXL") for row in rows})
    # A single run directory represents one exact ComfyUI model/config.
    for row in rows:
        if not row.get("model"):
            row["model"] = output_dir.parent.name
    models = sorted({str(row.get("model")) for row in rows})

    score_by_key = {str(row.get("key")): row for row in scores if row.get("status") == "success" and row.get("clip_score") is not None}
    grouped_scores: dict[tuple[str, str], list[float]] = defaultdict(list)
    grouped_times: dict[tuple[str, str], list[float]] = defaultdict(list)
    overall_scores: dict[str, list[float]] = defaultdict(list)
    overall_times: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        model = str(row.get("model"))
        test = str(row.get("test", "unknown"))
        if row.get("status") == "success":
            try:
                elapsed = float(row.get("elapsed_sec", 0))
                if elapsed > 0:
                    grouped_times[(model, test)].append(elapsed)
                    overall_times[model].append(elapsed)
            except (TypeError, ValueError):
                pass
        scored = score_by_key.get(str(row.get("key")))
        if scored:
            value = float(scored["clip_score"])
            grouped_scores[(model, test)].append(value)
            overall_scores[model].append(value)

    note = f"Source: {source_name}. CLIP ViT-B/32 prompt-image cosine similarity; higher is better."
    charts: list[dict[str, str]] = []
    tests = sorted({test for _, test in grouped_scores} | {test for _, test in grouped_times})
    for test in tests:
        safe = "".join(char if char.isalnum() or char in "-_" else "_" for char in test.lower())
        score_entries = [(model, mean(grouped_scores[(model, test)]) if grouped_scores[(model, test)] else 0.0, len(grouped_scores[(model, test)])) for model in models]
        time_entries = [(model, 60 / mean(grouped_times[(model, test)]) if grouped_times[(model, test)] else 0.0, len(grouped_times[(model, test)])) for model in models]
        if any(count for _, _, count in score_entries):
            svg = output_dir / f"test_{safe}_clip.svg"
            chart(svg, f"Test: {test} — Prompt Alignment", "All image-generation models", score_entries, "CLIP cosine similarity (higher is better)", "#377eb8", note)
            png = png_for(svg)
            charts.append({"title": f"{test} — CLIP alignment", "svg": svg.name, "png": png.name if png else ""})
        svg = output_dir / f"test_{safe}_speed.svg"
        chart(svg, f"Test: {test} — Generation Speed", "All image-generation models", time_entries, "Images per minute (higher is better)", "#e08214", f"Source: {source_name}. Timing includes ComfyUI queue and generation.")
        png = png_for(svg)
        charts.append({"title": f"{test} — generation speed", "svg": svg.name, "png": png.name if png else ""})

    if any(overall_scores.values()):
        entries = [(model, mean(overall_scores[model]) if overall_scores[model] else 0.0, len(overall_scores[model])) for model in models]
        svg = output_dir / "overall_clip_alignment.svg"
        chart(svg, "Overall Image Generation — Prompt Alignment", "Mean CLIP similarity across all scored prompts", entries, "CLIP cosine similarity (higher is better)", "#4daf4a", note)
        png = png_for(svg)
        charts.append({"title": "Overall — CLIP prompt alignment", "svg": svg.name, "png": png.name if png else ""})
    entries = [(model, 60 / mean(overall_times[model]) if overall_times[model] else 0.0, len(overall_times[model])) for model in models]
    svg = output_dir / "overall_generation_speed.svg"
    chart(svg, "Overall Image Generation — Speed", "Mean generation throughput across all completed prompts", entries, "Images per minute (higher is better)", "#984ea3", f"Source: {source_name}. Timing includes ComfyUI queue and generation.")
    png = png_for(svg)
    charts.append({"title": "Overall — generation speed", "svg": svg.name, "png": png.name if png else ""})

    cards = []
    for item in charts:
        image = item["png"] or item["svg"]
        cards.append(f'<section><h2>{escape(item["title"])}</h2><a href="{escape(item["svg"])}"><img src="{escape(image)}" alt="{escape(item["title"])}"></a><p><a href="{escape(item["svg"])}">SVG</a>' + (f' · <a href="{escape(item["png"])}">PNG</a>' if item["png"] else "") + "</p></section>")
    html = "<!doctype html><html><head><meta charset='utf-8'><title>Image Benchmark Graphs</title><style>body{font-family:Arial;background:#f3f4f6;margin:2rem;color:#1f2937}section{background:#fff;margin:1rem 0;padding:1rem 1.5rem;border-radius:8px}img{max-width:100%;border:1px solid #e5e7eb}a{color:#2563eb}</style></head><body><h1>Image Benchmark Graphs</h1><p>Source: <code>" + escape(source_name) + "</code></p>" + "\n".join(cards) + "</body></html>"
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    (output_dir / "manifest.json").write_text(json.dumps({"source": source_name, "charts": charts, "metric": "CLIP prompt-image cosine similarity plus images/minute"}, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(charts)} charts: {output_dir / 'index.html'}", flush=True)


def process(run_dir: Path, device: str, batch_size: int, skip_clip: bool) -> None:
    manifest = run_dir / "manifest.jsonl"
    rows = enrich_rows(read_jsonl(manifest))
    for row in rows:
        row["model"] = run_dir.name
    scores_path = run_dir / "clip_scores.jsonl"
    if not skip_clip:
        score_with_clip(rows, scores_path, TESTING / "models" / "evaluators" / "clip-vit-base-patch32", device, batch_size)
    scores = read_jsonl(scores_path)
    make_graphs(rows, scores, run_dir / "graphs", manifest.name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Postprocess a completed ComfyUI image benchmark")
    parser.add_argument("run_dir", help="Image benchmark output directory containing manifest.jsonl")
    parser.add_argument("--watch", action="store_true", help="Wait for the manifest to reach --expected records")
    parser.add_argument("--expected", type=int, default=0, help="Expected record count when watching; 0 means do not wait")
    parser.add_argument("--interval", type=float, default=60, help="Watch polling interval in seconds")
    parser.add_argument("--device", default="cpu", help="Scoring device (cpu or cuda:0)")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--skip-clip", action="store_true", help="Only create timing graphs")
    args = parser.parse_args()
    run_dir = Path(args.run_dir).expanduser().resolve()
    manifest = run_dir / "manifest.jsonl"
    if args.watch and args.expected > 0:
        while True:
            count = len(read_jsonl(manifest))
            print(f"Waiting for image run: {count}/{args.expected} records", flush=True)
            if count >= args.expected:
                break
            time.sleep(args.interval)
    if not manifest.exists():
        print(f"ERROR: missing {manifest}")
        return 1
    process(run_dir, args.device, args.batch_size, args.skip_clip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
