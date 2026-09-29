# Local LLM MMLU-Pro benchmark

This benchmark compares every locally installed Ollama model on a compact,
balanced subset of the downloaded MMLU-Pro test split.

## Default method

- 14 subject categories
- 5 deterministically selected test questions per category
- 70 scored answers per model (700 answers for the current 10 models)
- 14 category-batched Ollama requests per model
- zero-shot, direct-answer prompting
- temperature 0, seed 42, thinking disabled
- missing or malformed answers count as incorrect

This design keeps the local run practical while representing every category.
It is not directly comparable to the official full 12,032-question, normally
5-shot chain-of-thought MMLU-Pro leaderboard.

## Completed run

The 10-model run completed all 140 batches and 700 scored answers in 1:04:22.
The report is:

```text
runs/2026-09-05_22-56-18/report.html
```

The top result was `qwen3.6-27b-opus-distill:q4_k_m` at 75.7% (53/70).

## Run again

```fish
cd ~/Projects/Tests/2026-09-05/local-llm-mmlu-pro-benchmark
../../.venv/bin/python benchmark.py run
```

The runner discovers all current Ollama model tags automatically, runs models
sequentially, unloads each model afterward, displays a terminal progress bar,
and saves partial reports after every category batch.

Each run folder contains:

- `report.html`
- `overall-accuracy.svg`
- `category-heatmap.svg`
- `model-summary.csv`
- `results.csv`
- `batches.csv`
- `results.json`
- `raw/`

Rebuild a report without contacting Ollama:

```fish
../../.venv/bin/python benchmark.py report runs/YYYY-MM-DD_HH-MM-SS/results.json
```
