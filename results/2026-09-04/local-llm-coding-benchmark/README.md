# Local LLM coding benchmark

Subject: **local LLM coding benchmark**  
Date: **2026-09-04**

Everything for this test is kept under:

```text
~/Projects/Tests/2026-09-04/local-llm-coding-benchmark/
```

The benchmark uses the local Ollama API. When run, it discovers every model
tag returned by `http://127.0.0.1:11434/api/tags`, so newly installed Ollama
models are included automatically. It currently sees the following ten tags:

- `thinkingcap-qwen3.6-27b-q6_k:latest`
- `qwen3.6-35b-a3b-abliterated:q8_0`
- `qwen3.6-35b-a3b-abliterated-vl:q4_k_m`
- `gemma4-e4b-abliterated:q4_k_m`
- `qwen3.6-27b-opus-distill:q4_k_m`
- `qwen3.6-35b-a3b-abliterated:q6_k`
- `qwen3.6-35b-a3b-abliterated:q5_k_m`
- `qwen3.5-9b-opus-distill:q4_k_m`
- `qwen3.6-27b-abliterated:q5_k_m`
- `qwen3.8-27b-stock:q4_k_m`

A Hugging Face model is not included unless it has also been installed as an
Ollama model. Use `--model` to include a particular tag after installing it.

## Completed run

The full 10-model, 8-task benchmark completed on 2026-09-05. Its report is:

```text
runs/2026-09-05_00-01-44/report.html
```

To run it again:

```fish
cd ~/Projects/Tests/2026-09-04/local-llm-coding-benchmark
python3 benchmark.py run
```

The terminal displays a live progress bar for every model/task/trial. Models
are tested sequentially and unloaded between models. Thinking is explicitly
disabled for this coding benchmark so the output budget is spent on solution
code rather than a separate reasoning trace. Generated solutions are
run with the bubblewrap sandbox when `bwrap` is available.

The default run is one deterministic generation for each model and eight
coding tasks. Optional examples:

```fish
# Repeat every task twice
python3 benchmark.py run --trials 2

# Run selected model tags only
python3 benchmark.py run --model qwen3.5-9b-opus-distill:q4_k_m

# Exclude vision models
python3 benchmark.py run --exclude=-vl:
```

Generated run folders are placed below `runs/` and contain:

- `report.html` - browsable report with the comparison graphs
- `overall-score.svg` - correctness ranking
- `task-heatmap.svg` - model-by-task comparison
- `generation-speed.svg` - generation tokens/second
- `results.csv` and `model-summary.csv` - spreadsheet-friendly data
- `results.json` - complete metadata and results
- `raw/` and `solutions/` - model responses and extracted solutions

Correctness is the primary ranking: each model gets an equally weighted
average of hidden-test scores across tasks. Speed is shown separately and does
not compensate for incorrect code.

## Safety

Model output is executable code. The default `--sandbox required` setting uses
bubblewrap with no network access, a read-only runtime filesystem, and only a
temporary writable work directory. If bubblewrap is unavailable, the runner
stops instead of silently executing model code on the host. Disabling the
sandbox requires both flags below and should only be done for trusted models:

```fish
python3 benchmark.py run --sandbox off --allow-unsafe-code-execution
```

## Rebuild a report

This does not contact Ollama and only regenerates graphs from an existing run:

```fish
python3 benchmark.py report runs/YYYY-MM-DD_HH-MM-SS/results.json
```
