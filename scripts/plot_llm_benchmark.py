#!/usr/bin/env python3
"""Create per-test and overall charts from an Ollama benchmark report.

Uses only the Python standard library plus the locally installed rsvg-convert
when PNG copies are requested. The charts plot retained generation throughput
(score = generation tokens/second), not subjective answer quality.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from html import escape
from pathlib import Path
from statistics import mean
from typing import Any


def compact_label(name: str) -> str:
    """Make a readable, unique-ish label while retaining important tags."""
    if name == "fredrezones55/Gemma-4-Uncensored-HauhauCS-Aggressive:latest":
        return "Gemma-4 Uncensored"
    if name == "fredrezones55/Qwopus3.5:latest":
        return "Qwopus 3.5"
    if name == "fredrezones55/Qwopus3.6:latest":
        return "Qwopus 3.6"
    if "Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive" in name:
        tag = name.rsplit(":", 1)[-1]
        return f"HauhauCS Qwen3.6-35B-A3B [{tag}]"
    if name == "qwen-pi:latest":
        return "qwen-pi"
    if name == "qwen3.8:27b-q4_K_M":
        return "qwen3.8 27B Q4"
    if name == "qwen3.6-27b-uncensored-q5-pi:latest":
        return "qwen3.6 27B Q5 pi"
    if name.startswith("qwen3.6-35b-a3b-"):
        quant = name.split("-")[-2].upper()
        return f"qwen3.6 35B-A3B {quant} pi"
    if name == "qwen3.6-35b-a3b:latest":
        return "qwen3.6 35B-A3B Q4"
    return name.removesuffix(":latest")


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


def svg_text(text: str, x: float, y: float, size: int = 16, fill: str = "#1f2937", anchor: str = "start", weight: str = "normal") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}px" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{escape(str(text))}</text>'


def make_chart(
    path: Path,
    title: str,
    subtitle: str,
    entries: list[tuple[str, float, int, int]],
    color: str,
    note: str,
) -> None:
    # Entries are (full model name, average score, successful retained runs, retained runs).
    entries = sorted(entries, key=lambda item: item[1], reverse=True)
    width = 1800
    row_height = 54
    top = 125
    bottom = 92
    left = 515
    right = 155
    height = top + bottom + row_height * len(entries)
    plot_width = width - left - right
    x_max = nice_upper(max((value for _, value, _, _ in entries), default=1.0))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        svg_text(title, 42, 47, 29, "#111827", weight="bold"),
        svg_text(subtitle, 42, 78, 16, "#4b5563"),
    ]

    # Five intervals give readable grid lines and labels.
    intervals = 5
    for tick_index in range(intervals + 1):
        value = x_max * tick_index / intervals
        x = left + plot_width * tick_index / intervals
        parts.append(f'<line x1="{x:.1f}" y1="{top - 12}" x2="{x:.1f}" y2="{height - bottom}" stroke="#dbe3ec" stroke-width="1"/>')
        parts.append(svg_text(f"{value:.0f}", x, height - bottom + 27, 14, "#4b5563", anchor="middle"))
    parts.append(svg_text("Generation throughput (tokens/second; higher is better)", left + plot_width / 2, height - 25, 15, "#374151", anchor="middle"))

    for index, (model, value, successful, retained) in enumerate(entries):
        y = top + index * row_height + 12
        bar_height = 30
        bar_width = max(0.0, plot_width * value / x_max)
        label = compact_label(model)
        parts.append(svg_text(f"{index + 1}. {label}", left - 20, y + 21, 16, "#1f2937", anchor="end"))
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" rx="4" fill="{color}"><title>{escape(model)}: {value:.2f} tok/s</title></rect>')
        parts.append(svg_text(f"{value:.2f}  ({successful}/{retained})", left + bar_width + 10, y + 21, 15, "#1f2937"))

    parts.append(svg_text(note, 42, height - 54, 13, "#6b7280"))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def convert_png(svg_path: Path) -> Path | None:
    png_path = svg_path.with_suffix(".png")
    try:
        subprocess.run(
            ["rsvg-convert", "-o", str(png_path), str(svg_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return png_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Graph an Ollama benchmark JSON report")
    parser.add_argument("report", help="Benchmark JSON report")
    parser.add_argument("--output-dir", help="Directory for charts; default is <report stem>_graphs")
    args = parser.parse_args()

    report_path = Path(args.report).expanduser().resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir).expanduser() if args.output_dir else report_path.with_name(report_path.stem + "_graphs")
    output_dir.mkdir(parents=True, exist_ok=True)

    models = [str(record["name"]) for record in report["models"]]
    tests = report["tests"]
    retained = [result for result in report["retained_results"] if result.get("success")]
    by_model_test: dict[tuple[str, str], list[float]] = {}
    for result in retained:
        key = (str(result["model"]), str(result["test_id"]))
        by_model_test.setdefault(key, []).append(float(result.get("score", result.get("generation_tok_per_sec", 0))))

    note = (
        "Based on retained runs in " + report_path.name + "; one worst run removed independently per model/test. "
        f"Thinking={'on' if report.get('thinking_enabled') else 'off'}, context={report.get('context_size', '?')}."
    )
    charts: list[dict[str, str]] = []
    mapping_lines = ["label\tfull_model_name"]
    for model in models:
        mapping_lines.append(f"{compact_label(model)}\t{model}")
    (output_dir / "model_labels.tsv").write_text("\n".join(mapping_lines) + "\n", encoding="utf-8")

    for test in tests:
        test_id = str(test["id"])
        entries: list[tuple[str, float, int, int]] = []
        for model in models:
            values = by_model_test.get((model, test_id), [])
            entries.append((model, mean(values) if values else 0.0, len(values), 4))
        filename = f"test_{test_id}.svg"
        svg_path = output_dir / filename
        kind = "speed" if test.get("type") == "speed" else "content-task performance"
        make_chart(
            svg_path,
            str(test["name"]),
            f"All local models — retained average generation throughput ({kind})",
            entries,
            "#377eb8" if test.get("type") == "speed" else "#e08214",
            note,
        )
        png = convert_png(svg_path)
        charts.append({"title": str(test["name"]), "svg": svg_path.name, "png": png.name if png else ""})

    speed_ids = {str(test["id"]) for test in tests if test.get("type") == "speed"}
    overall_speed_entries: list[tuple[str, float, int, int]] = []
    overall_all_entries: list[tuple[str, float, int, int]] = []
    for model in models:
        speed_values = [value for (candidate, test_id), values in by_model_test.items() if candidate == model and test_id in speed_ids for value in values]
        all_values = [value for (candidate, _), values in by_model_test.items() if candidate == model for value in values]
        overall_speed_entries.append((model, mean(speed_values) if speed_values else 0.0, len(speed_values), len(speed_values)))
        overall_all_entries.append((model, mean(all_values) if all_values else 0.0, len(all_values), len(all_values)))

    overall_note = note + " Overall speed is the mean of the three speed tests; values are not subjective quality grades."
    for filename, title, subtitle, entries, chart_key in [
        (
            "overall_speed.svg",
            "Overall Model Ranking — Speed Tests",
            "Mean retained generation throughput across the three speed tests",
            overall_speed_entries,
            "overall_speed",
        ),
        (
            "overall_all_tests.svg",
            "Overall Model Ranking — All Tests",
            "Informational mean retained generation throughput across all 12 prompts",
            overall_all_entries,
            "overall_all_tests",
        ),
    ]:
        svg_path = output_dir / filename
        make_chart(svg_path, title, subtitle, entries, "#4daf4a" if chart_key == "overall_speed" else "#984ea3", overall_note)
        png = convert_png(svg_path)
        charts.insert(0, {"title": title, "svg": svg_path.name, "png": png.name if png else ""})

    # A small, self-contained index makes all 14 charts easy to browse.
    cards = []
    for chart in charts:
        image = chart["png"] or chart["svg"]
        cards.append(
            f'<section><h2>{escape(chart["title"])}</h2>'
            f'<a href="{escape(chart["svg"])}"><img src="{escape(image)}" alt="{escape(chart["title"])}"></a>'
            f'<p><a href="{escape(chart["svg"])}">Open SVG</a>'
            + (f' · <a href="{escape(chart["png"])}">Open PNG</a>' if chart["png"] else "")
            + "</p></section>"
        )
    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Local LLM Benchmark Graphs</title>
<style>body{font-family:Arial,sans-serif;color:#1f2937;background:#f3f4f6;margin:2rem}h1{margin-bottom:.3rem}header{background:#fff;padding:1rem 1.5rem;margin-bottom:1rem;border-radius:8px}section{background:#fff;padding:1rem 1.5rem;margin:1rem 0;border-radius:8px;box-shadow:0 1px 3px #0001}img{max-width:100%;height:auto;border:1px solid #e5e7eb}a{color:#2563eb}</style></head>
<body><header><h1>Local LLM Benchmark Graphs</h1><p>Source: <code>""" + escape(report_path.name) + """</code>. Charts use retained generation throughput; one worst run was removed per model/test.</p></header>
""" + "\n".join(cards) + "\n</body></html>"
    (output_dir / "index.html").write_text(html, encoding="utf-8")

    manifest = {
        "source_report": str(report_path),
        "output_dir": str(output_dir),
        "metric": "mean retained generation_tok_per_sec",
        "charts": charts,
        "retained_successful_results": len(retained),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Created {len(charts)} charts in {output_dir}")
    print(f"Index: {output_dir / 'index.html'}")
    print(f"Model label map: {output_dir / 'model_labels.tsv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
